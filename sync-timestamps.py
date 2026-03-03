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
        "tools/flutter", "tools/flutter/**",
    ],
    "claude-code": [
        "history.jsonl", "usage-log.jsonl", "cache", "debug",
        "backups", "file-history", "telemetry", "session-env",
        "shell-snapshots", "ide", "downloads", ".git",
    ],
}

# 타임스탬프 키 마이그레이션 (claude-config → claude-code)
TS_KEY_MIGRATIONS = {"claude-config": "claude-code"}

# claude-code는 화이트리스트 방식 (이 항목만 동기화)
CLAUDE_INCLUDES = {
    "settings.json", "CLAUDE.md", "stop-hook-git-check.sh",
    "agents", "plugins", "skills", "agent-memory", "memory", "todos", "teams",
}


def migrate_ts_keys(ts: dict) -> dict:
    """타임스탬프 키 마이그레이션 (예: claude-config → claude-code)"""
    for old_key, new_key in TS_KEY_MIGRATIONS.items():
        if old_key in ts and new_key not in ts:
            ts[new_key] = ts.pop(old_key)
    return ts


def should_include(filepath: str, section: str) -> bool:
    parts = Path(filepath).parts

    # 제외 패턴 체크
    for pattern in EXCLUDES.get(section, []):
        if any(fnmatch.fnmatch(p, pattern) for p in parts):
            return False
        if fnmatch.fnmatch(filepath, pattern):
            return False

    # claude-code 화이트리스트
    if section == "claude-code":
        top = parts[0] if parts else ""
        return top in CLAUDE_INCLUDES

    return True


def git_cmd(args, cwd):
    r = subprocess.run(["git"] + args, cwd=str(cwd),
                       capture_output=True, text=True, encoding="utf-8")
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
            rel = fp.relative_to(base).as_posix()
            if should_include(rel, section):
                result[rel] = mtime(fp)
    return result


def walk_all_files(base: Path) -> set[str]:
    """base 하위 전체 파일의 상대경로 집합 반환 (.git 제외)"""
    result: set[str] = set()
    if not base.exists():
        return result
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            fp = Path(root) / f
            result.add(fp.relative_to(base).as_posix())
    return result


def unlink_if_file(path: Path) -> None:
    """파일/심볼릭링크만 삭제 (디렉토리는 건너뜀)"""
    try:
        if path.is_file() or path.is_symlink():
            path.unlink()
    except OSError:
        pass


def prune_empty_dirs(base: Path) -> None:
    """비어있는 디렉토리를 하위부터 정리"""
    if not base.exists():
        return
    dirs = [p for p in base.rglob("*") if p.is_dir()]
    for d in sorted(dirs, key=lambda p: len(p.parts), reverse=True):
        try:
            d.rmdir()
        except OSError:
            pass


def main():
    sync_dir = Path(sys.argv[1]).expanduser().resolve()
    hostname = sys.argv[2]

    # section key → (로컬 경로, repo 내 하위 경로)
    sections = {
        "workspace": (Path("~/.openclaw/workspace").expanduser(), "openclaw/workspace"),
        "claude-code": (Path("~/.claude").expanduser(), "claude-code"),
    }

    ts_dir = sync_dir / "timestamps"
    ts_dir.mkdir(exist_ok=True)

    our_ts_file = ts_dir / f"{hostname}.json"
    our_ts: dict = json.loads(our_ts_file.read_text(encoding="utf-8")) if our_ts_file.exists() else {}
    our_ts = migrate_ts_keys(our_ts)

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
                peer_ts_all[peer] = migrate_ts_keys(json.loads(content))
            except Exception:
                pass

    if peer_ts_all:
        print(f"  피어 감지: {', '.join(peer_ts_all.keys())}")
    else:
        print("  피어 타임스탬프 없음 (첫 실행이거나 피어 미등록)")

    # ── 섹션별 처리 ──────────────────────────────────────────────
    for section, (local_dir, repo_subdir) in sections.items():
        if not local_dir.exists():
            continue

        repo_section = sync_dir / repo_subdir
        repo_section.mkdir(parents=True, exist_ok=True)

        local_files = walk_files(local_dir, section)
        repo_files = walk_all_files(repo_section)
        our_section_ts = our_ts.get(section, {})

        # 피어 중 파일별 최신 타임스탬프 추출
        peer_best: dict[str, tuple[float, str]] = {}
        for peer, peer_data in peer_ts_all.items():
            for fp, ts in peer_data.get(section, {}).items():
                if fp not in peer_best or ts > peer_best[fp][0]:
                    peer_best[fp] = (ts, peer)

        # 삭제 전파/잔존 파일 정리를 위해 local, peer, 과거 타임스탬프, repo 현재 파일 전체를 합침
        all_files = (
            set(local_files.keys())
            | set(peer_best.keys())
            | set(our_section_ts.keys())
            | repo_files
        )
        applied_from_peer = []
        kept_local = []
        removed_from_repo = 0

        for filepath in sorted(all_files):
            local_path = local_dir / filepath
            repo_path  = repo_section / filepath
            included = should_include(filepath, section)

            # 현재 규칙에서 제외된 파일은 repo에서 제거해 stale 누적 방지
            if not included:
                if repo_path.exists() or repo_path.is_symlink():
                    unlink_if_file(repo_path)
                    removed_from_repo += 1
                continue

            # 우리 타임스탬프: 저장된 값 우선, 없으면 현재 mtime
            our_file_ts  = our_section_ts.get(filepath, local_files.get(filepath, 0.0))
            peer_file_ts = peer_best.get(filepath, (0.0, None))[0]

            if peer_file_ts > our_file_ts:
                # 피어가 더 최신 → FETCH_HEAD에서 내용 가져와 로컬 + repo 모두 갱신
                content_bytes, rc2 = git_bytes(
                    ["show", f"FETCH_HEAD:{repo_subdir}/{filepath}"], sync_dir
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
                elif repo_path.exists() or repo_path.is_symlink():
                    # 로컬에서 삭제된 파일 → repo에서도 제거
                    unlink_if_file(repo_path)
                    removed_from_repo += 1

        # 심볼릭 링크 제거 (claude-code)
        if section == "claude-code":
            for link in repo_section.rglob("*"):
                if link.is_symlink():
                    link.unlink()

        prune_empty_dirs(repo_section)

        if applied_from_peer:
            shown = ", ".join(applied_from_peer[:3])
            extra = f" 외 {len(applied_from_peer)-3}개" if len(applied_from_peer) > 3 else ""
            removed_msg = f", repo 정리 {removed_from_repo}개" if removed_from_repo else ""
            print(f"  ← [{section}] 피어 최신 적용: {shown}{extra}{removed_msg}")
        else:
            removed_msg = f", repo 정리 {removed_from_repo}개" if removed_from_repo else ""
            print(f"  → [{section}] 로컬이 최신 ({len(kept_local)}개 파일{removed_msg})")

    # ── 현재 타임스탬프 저장 ─────────────────────────────────────
    new_ts = {}
    for section, (local_dir, _) in sections.items():
        if local_dir.exists():
            new_ts[section] = walk_files(local_dir, section)

    our_ts_file.write_text(json.dumps(new_ts, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  ✓ 타임스탬프 저장: timestamps/{hostname}.json")


if __name__ == "__main__":
    main()
