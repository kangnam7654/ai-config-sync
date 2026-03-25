#!/usr/bin/env python3
"""
sync-timestamps.py - 파일별 최신 버전 우선(newest-wins) 동기화
사용법: python3 sync-timestamps.py <sync_dir> <hostname>
        python3 sync-timestamps.py --list-includes
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

# ── 섹션별 포함/제외 규칙 ────────────────────────────────────────
EXCLUDES: dict[str, list[str]] = {
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
TS_KEY_MIGRATIONS: dict[str, str] = {"claude-config": "claude-code"}

# claude-code는 화이트리스트 방식 (이 항목만 동기화)
CLAUDE_INCLUDES: set[str] = {
    "settings.json", "CLAUDE.md", "stop-hook-git-check.sh",
    "agents", "plugins", "skills", "agent-memory", "memory", "todos", "teams",
}

# ── 검증 함수 ────────────────────────────────────────────────────

_HOSTNAME_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$")
_MAX_FUTURE_DRIFT_SECONDS = 86400  # 24시간


def validate_hostname(hostname: str) -> str:
    """hostname 검증. RFC 952/1123 준수.

    Returns: 검증된 hostname
    Raises: SystemExit(2) 비유효 시
    """
    if not _HOSTNAME_RE.match(hostname):
        print(f"  [ERROR] 유효하지 않은 hostname: {hostname!r}", file=sys.stderr)
        sys.exit(2)
    return hostname


def validate_filepath(filepath: str, section: str) -> bool:
    """피어 파일 경로가 섹션 경계를 벗어나지 않는지 검증.

    차단 조건: ".." 포함, 절대 경로, null byte 포함
    Returns: True(안전) / False(차단)
    """
    if not filepath:
        return False
    if "\x00" in filepath:
        return False
    if filepath.startswith("/") or filepath.startswith("\\"):
        return False
    try:
        normalized = Path(filepath).as_posix()
    except ValueError:
        return False
    if ".." in normalized.split("/"):
        return False
    return True


def validate_timestamp(value: object, filepath: str) -> float | None:
    """타임스탬프 값 검증.

    Returns: 유효한 float timestamp, 또는 None (무시)
    """
    if not isinstance(value, (int, float)):
        return None
    ts = float(value)
    if ts < 0:
        return None
    if ts > time.time() + _MAX_FUTURE_DRIFT_SECONDS:
        return None
    return ts


def print_includes() -> None:
    """CLAUDE_INCLUDES 목록을 공백 구분으로 stdout 출력."""
    print(" ".join(sorted(CLAUDE_INCLUDES)))


def parse_args() -> tuple[Path, str]:
    """sys.argv 파싱 + 검증.

    Returns: (sync_dir, hostname)
    Raises: SystemExit(0) --list-includes, SystemExit(2) 인수 부족/유효하지 않은 값
    """
    if len(sys.argv) >= 2 and sys.argv[1] == "--list-includes":
        print_includes()
        sys.exit(0)
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <sync_dir> <hostname>", file=sys.stderr)
        sys.exit(2)
    sync_dir = Path(sys.argv[1]).expanduser().resolve()
    hostname = validate_hostname(sys.argv[2])
    if not sync_dir.is_dir():
        print(f"  [ERROR] sync_dir이 존재하지 않음: {sync_dir}", file=sys.stderr)
        sys.exit(2)
    return sync_dir, hostname


# ── 순수 함수 ────────────────────────────────────────────────────

def migrate_ts_keys(ts: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
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


def git_cmd(args: list[str], cwd: Path | str) -> tuple[str, int]:
    import subprocess
    r = subprocess.run(["git"] + args, cwd=str(cwd),
                       capture_output=True, text=True, encoding="utf-8")
    return r.stdout.strip(), r.returncode


def git_bytes(args: list[str], cwd: Path | str) -> tuple[bytes, int]:
    import subprocess
    r = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True)
    return r.stdout, r.returncode


def mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except OSError:
        return 0.0


def walk_files(base: Path, section: str) -> dict[str, float]:
    """includable 파일의 {상대경로: mtime} 반환"""
    result: dict[str, float] = {}
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
    except OSError as e:
        print(f"  [WARN] 삭제 실패: {path} ({e})", file=sys.stderr)


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


# ── 핵심 로직 (분리된 함수) ───────────────────────────────────────

def load_timestamps(ts_dir: Path, hostname: str) -> dict[str, dict[str, float]]:
    """로컬 타임스탬프 파일 로드 + 키 마이그레이션.

    Args:
        ts_dir: timestamps/ 디렉토리 경로
        hostname: 현재 호스트명
    Returns:
        섹션별 타임스탬프 dict. 예: {"workspace": {"file.md": 1711234567.0}, ...}
    """
    ts_file = ts_dir / f"{hostname}.json"
    if ts_file.exists():
        our_ts = json.loads(ts_file.read_text(encoding="utf-8"))
    else:
        our_ts = {}
    return migrate_ts_keys(our_ts)


def load_peer_timestamps(
    sync_dir: Path, hostname: str
) -> dict[str, dict[str, dict[str, float]]]:
    """FETCH_HEAD에서 피어 타임스탬프 로드.

    Args:
        sync_dir: 동기화 루트 디렉토리
        hostname: 현재 호스트명 (자기 자신 제외용)
    Returns:
        {peer_name: {section: {filepath: timestamp}}} 3중 dict
    """
    peer_ts_all: dict[str, dict[str, dict[str, float]]] = {}
    ls_out, rc = git_cmd(["ls-tree", "FETCH_HEAD", "timestamps/"], sync_dir)
    if rc != 0 or not ls_out:
        return peer_ts_all

    for line in ls_out.split("\n"):
        if not line:
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        fname = parts[3]  # e.g. timestamps/Kangnamui-MacBookPro.json
        if not re.match(r"^timestamps/[a-zA-Z0-9._-]+\.json$", fname):
            continue
        peer = Path(fname).stem
        if peer == hostname:
            continue
        content, _ = git_cmd(["show", f"FETCH_HEAD:{fname}"], sync_dir)
        try:
            raw = migrate_ts_keys(json.loads(content))
            # 타임스탬프 값 검증
            _KNOWN_SECTIONS = {"workspace", "claude-code"}
            validated: dict[str, dict[str, float]] = {}
            for section_key, files in raw.items():
                if not isinstance(section_key, str) or section_key not in _KNOWN_SECTIONS or not isinstance(files, dict):
                    continue
                validated_files: dict[str, float] = {}
                for fp, ts in files.items():
                    if not isinstance(fp, str):
                        continue
                    valid_ts = validate_timestamp(ts, fp)
                    if valid_ts is not None:
                        validated_files[fp] = valid_ts
                validated[section_key] = validated_files
            peer_ts_all[peer] = validated
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  [WARN] 피어 {peer} 파싱 실패: {e}", file=sys.stderr)

    return peer_ts_all


def sync_section(
    section: str,
    local_dir: Path,
    repo_subdir: str,
    sync_dir: Path,
    our_section_ts: dict[str, float],
    peer_ts_all: dict[str, dict[str, dict[str, float]]],
) -> dict[str, float]:
    """단일 섹션의 newest-wins 병합 수행.

    Args:
        section: 섹션 키 ("workspace" | "claude-code")
        local_dir: 로컬 디렉토리 경로 (~/.openclaw/workspace 등)
        repo_subdir: repo 내 하위 경로 ("openclaw/workspace" 등)
        sync_dir: 동기화 루트 디렉토리
        our_section_ts: 이 섹션의 기존 타임스탬프
        peer_ts_all: 전체 피어 타임스탬프 (load_peer_timestamps 반환값)
    Returns:
        병합 후 이 섹션의 새 타임스탬프 dict {filepath: mtime}
    """
    repo_section = sync_dir / repo_subdir
    repo_section.mkdir(parents=True, exist_ok=True)

    local_files = walk_files(local_dir, section)
    repo_files = walk_all_files(repo_section)

    # 피어 중 파일별 최신 타임스탬프 추출
    peer_best: dict[str, tuple[float, str]] = {}
    for peer, peer_data in peer_ts_all.items():
        for fp, ts in peer_data.get(section, {}).items():
            if fp not in peer_best or ts > peer_best[fp][0]:
                peer_best[fp] = (ts, peer)

    # 삭제 전파/잔존 파일 정리를 위해 전체 파일 합산
    all_files = (
        set(local_files.keys())
        | set(peer_best.keys())
        | set(our_section_ts.keys())
        | repo_files
    )
    applied_from_peer: list[str] = []
    kept_local: list[str] = []
    removed_from_repo = 0

    for filepath in sorted(all_files):
        # 경로 검증
        if not validate_filepath(filepath, section):
            continue

        local_path = local_dir / filepath
        repo_path = repo_section / filepath
        included = should_include(filepath, section)

        # 현재 규칙에서 제외된 파일은 repo에서 제거해 stale 누적 방지
        if not included:
            if repo_path.exists() or repo_path.is_symlink():
                unlink_if_file(repo_path)
                removed_from_repo += 1
            continue

        # 우리 타임스탬프: 저장된 값 우선, 없으면 현재 mtime
        our_file_ts = our_section_ts.get(filepath, local_files.get(filepath, 0.0))
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

    return walk_files(local_dir, section)


def save_timestamps(
    ts_dir: Path, hostname: str, new_ts: dict[str, dict[str, float]]
) -> None:
    """타임스탬프 JSON 저장.

    Args:
        ts_dir: timestamps/ 디렉토리 경로
        hostname: 현재 호스트명
        new_ts: 저장할 타임스탬프 dict
    """
    ts_file = ts_dir / f"{hostname}.json"
    ts_file.write_text(json.dumps(new_ts, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  ✓ 타임스탬프 저장: timestamps/{hostname}.json")


# ── main ──────────────────────────────────────────────────────────

def main() -> None:
    sync_dir, hostname = parse_args()

    sections = {
        "workspace": (Path("~/.openclaw/workspace").expanduser(), "openclaw/workspace"),
        "claude-code": (Path("~/.claude").expanduser(), "claude-code"),
    }

    ts_dir = sync_dir / "timestamps"
    ts_dir.mkdir(exist_ok=True)

    our_ts = load_timestamps(ts_dir, hostname)
    peer_ts_all = load_peer_timestamps(sync_dir, hostname)

    if peer_ts_all:
        print(f"  피어 감지: {', '.join(peer_ts_all.keys())}")
    else:
        print("  피어 타임스탬프 없음 (첫 실행이거나 피어 미등록)")

    new_ts: dict[str, dict[str, float]] = {}
    for section, (local_dir, repo_subdir) in sections.items():
        if not local_dir.exists():
            continue
        new_ts[section] = sync_section(
            section, local_dir, repo_subdir, sync_dir,
            our_ts.get(section, {}), peer_ts_all,
        )

    save_timestamps(ts_dir, hostname, new_ts)


if __name__ == "__main__":
    main()
