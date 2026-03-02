#!/usr/bin/env python3
"""
sync-timestamps.py - 파일별 최신 버전 우선(newest-wins) 동기화
사용법: python3 sync-timestamps.py <sync_dir> <hostname>
"""

import os, json, sys, subprocess, shutil, fnmatch
from pathlib import Path

# ── 섹션별 포함/제외 규칙 ────────────────────────────────────────
EXCLUDES = {
    "workspace": [
        "notion_data_*.json", "tmp_*.json", "*.jsonl", ".git",
    ],
    "claude-config": [
        "history.jsonl", "usage-log.jsonl", "cache", "debug",
        "backups", "file-history", "telemetry", "session-env",
        "shell-snapshots", "ide", "downloads", ".git",
    ],
}

# claude-config는 화이트리스트 방식 (이 항목만 동기화)
CLAUDE_INCLUDES = {
    "settings.json", "CLAUDE.md", "stop-hook-git-check.sh",
    "agents", "plugins", "skills", "agent-memory", "memory", "todos", "teams",
}


def should_include(filepath: str, section: str) -> bool:
    parts = Path(filepath).parts

    # 제외 패턴 체크
    for pattern in EXCLUDES.get(section, []):
        if any(fnmatch.fnmatch(p, pattern) for p in parts):
            return False
        if fnmatch.fnmatch(filepath, pattern):
            return False

    # claude-config 화이트리스트
    if section == "claude-config":
        top = parts[0] if parts else ""
        return top in CLAUDE_INCLUDES

    return True


def git_cmd(args, cwd):
    r = subprocess.run(["git"] + args, cwd=str(cwd),
                       capture_output=True, text=True)
    return r.stdout.strip(), r.returncode


def git_bytes(args, cwd):
    r = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True)
    return r.stdout, r.returncode


def mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except:
        return 0.0


def walk_files(base: Path, section: str) -> dict:
    """includable 파일의 {상대경로: mtime} 반환"""
    result = {}
    if not base.exists():
        return result
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            fp = Path(root) / f
            rel = str(fp.relative_to(base))
            if should_include(rel, section):
                result[rel] = mtime(fp)
    return result


def main():
    sync_dir = Path(sys.argv[1]).expanduser().resolve()
    hostname = sys.argv[2]

    sections = {
        "workspace": Path("~/.openclaw/workspace").expanduser(),
        "claude-config": Path("~/.claude").expanduser(),
    }

    ts_dir = sync_dir / "timestamps"
    ts_dir.mkdir(exist_ok=True)

    our_ts_file = ts_dir / f"{hostname}.json"
    our_ts: dict = json.loads(our_ts_file.read_text()) if our_ts_file.exists() else {}

    # ── FETCH_HEAD에서 피어 타임스탬프 읽기 ──────────────────────
    peer_ts_all: dict[str, dict] = {}
    ls_out, rc = git_cmd(["ls-tree", "FETCH_HEAD", "timestamps/"], sync_dir)
    if rc == 0 and ls_out:
        for line in ls_out.split("\n"):
            if not line:
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            fname = parts[3]          # e.g. timestamps/Kangnamui-MacBookPro.json
            peer = Path(fname).stem
            if peer == hostname:
                continue
            content, _ = git_cmd(["show", f"FETCH_HEAD:{fname}"], sync_dir)
            try:
                peer_ts_all[peer] = json.loads(content)
            except Exception:
                pass

    if peer_ts_all:
        print(f"  피어 감지: {', '.join(peer_ts_all.keys())}")
    else:
        print("  피어 타임스탬프 없음 (첫 실행이거나 피어 미등록)")

    # ── 섹션별 처리 ──────────────────────────────────────────────
    for section, local_dir in sections.items():
        if not local_dir.exists():
            continue

        repo_section = sync_dir / section
        repo_section.mkdir(exist_ok=True)

        local_files = walk_files(local_dir, section)
        our_section_ts = our_ts.get(section, {})

        # 피어 중 파일별 최신 타임스탬프 추출
        peer_best: dict[str, tuple[float, str]] = {}
        for peer, peer_data in peer_ts_all.items():
            for fp, ts in peer_data.get(section, {}).items():
                if fp not in peer_best or ts > peer_best[fp][0]:
                    peer_best[fp] = (ts, peer)

        all_files = set(list(local_files.keys()) + list(peer_best.keys()))
        applied_from_peer = []
        kept_local = []

        for filepath in sorted(all_files):
            if not should_include(filepath, section):
                continue

            local_path = local_dir / filepath
            repo_path  = repo_section / filepath

            # 우리 타임스탬프: 저장된 값 우선, 없으면 현재 mtime
            our_file_ts  = our_section_ts.get(filepath, local_files.get(filepath, 0.0))
            peer_file_ts = peer_best.get(filepath, (0.0, None))[0]

            if peer_file_ts > our_file_ts:
                # 피어가 더 최신 → FETCH_HEAD에서 내용 가져와 로컬 + repo 모두 갱신
                content_bytes, rc2 = git_bytes(
                    ["show", f"FETCH_HEAD:{section}/{filepath}"], sync_dir
                )
                if rc2 == 0:
                    local_path.parent.mkdir(parents=True, exist_ok=True)
                    local_path.write_bytes(content_bytes)
                    repo_path.parent.mkdir(parents=True, exist_ok=True)
                    repo_path.write_bytes(content_bytes)
                    applied_from_peer.append(filepath)
            else:
                # 로컬이 더 최신 (또는 동일) → 로컬 → repo 복사
                if local_path.exists():
                    repo_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(local_path), str(repo_path))
                    kept_local.append(filepath)
                elif repo_path.exists():
                    # 로컬에서 삭제된 파일 → repo에서도 제거
                    repo_path.unlink()

        # 심볼릭 링크 제거 (claude-config)
        if section == "claude-config":
            for link in repo_section.rglob("*"):
                if link.is_symlink():
                    link.unlink()

        if applied_from_peer:
            shown = ", ".join(applied_from_peer[:3])
            extra = f" 외 {len(applied_from_peer)-3}개" if len(applied_from_peer) > 3 else ""
            print(f"  ← [{section}] 피어 최신 적용: {shown}{extra}")
        else:
            print(f"  → [{section}] 로컬이 최신 ({len(kept_local)}개 파일)")

    # ── 현재 타임스탬프 저장 ─────────────────────────────────────
    new_ts = {}
    for section, local_dir in sections.items():
        if local_dir.exists():
            new_ts[section] = walk_files(local_dir, section)

    our_ts_file.write_text(json.dumps(new_ts, indent=2))
    print(f"  ✓ 타임스탬프 저장: timestamps/{hostname}.json")


if __name__ == "__main__":
    main()
