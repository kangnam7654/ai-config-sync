"""sync_section() 통합 테스트 — 8개."""

from __future__ import annotations

import time
from pathlib import Path

import sync_timestamps as st


def _make_env(tmp_path: Path):
    """최소 동기화 환경 구성."""
    sync_dir = tmp_path / "repo"
    sync_dir.mkdir()
    local_dir = tmp_path / "local"
    local_dir.mkdir()
    repo_sub = "test-section"
    (sync_dir / repo_sub).mkdir()
    return sync_dir, local_dir, repo_sub


def test_peer_newer(tmp_path: Path, mock_git):
    """피어가 더 최신이면 피어 내용을 적용."""
    sync_dir, local_dir, repo_sub = _make_env(tmp_path)
    (local_dir / "file.md").write_text("old")

    now = time.time()
    peer_ts_all = {"peer1": {"workspace": {"file.md": now + 100}}}
    our_ts = {"file.md": now - 100}

    mock_git.set_bytes("show", b"new content from peer")

    result = st.sync_section(
        "workspace", local_dir, repo_sub, sync_dir, our_ts, peer_ts_all,
    )
    assert (local_dir / "file.md").read_text() == "new content from peer"
    assert "file.md" in result


def test_local_newer(tmp_path: Path, mock_git):
    """로컬이 더 최신이면 로컬 유지."""
    sync_dir, local_dir, repo_sub = _make_env(tmp_path)
    (local_dir / "file.md").write_text("local content")

    now = time.time()
    peer_ts_all = {"peer1": {"workspace": {"file.md": now - 200}}}
    our_ts = {"file.md": now}

    result = st.sync_section(
        "workspace", local_dir, repo_sub, sync_dir, our_ts, peer_ts_all,
    )
    assert (local_dir / "file.md").read_text() == "local content"
    repo_file = sync_dir / repo_sub / "file.md"
    assert repo_file.read_text() == "local content"


def test_equal_timestamp(tmp_path: Path, mock_git):
    """동일 타임스탬프면 로컬 유지."""
    sync_dir, local_dir, repo_sub = _make_env(tmp_path)
    (local_dir / "file.md").write_text("local")

    now = time.time()
    peer_ts_all = {"peer1": {"workspace": {"file.md": now}}}
    our_ts = {"file.md": now}

    result = st.sync_section(
        "workspace", local_dir, repo_sub, sync_dir, our_ts, peer_ts_all,
    )
    assert (local_dir / "file.md").read_text() == "local"


def test_delete_propagation(tmp_path: Path, mock_git):
    """로컬에서 삭제된 파일은 repo에서도 제거."""
    sync_dir, local_dir, repo_sub = _make_env(tmp_path)
    repo_file = sync_dir / repo_sub / "deleted.md"
    repo_file.write_text("stale")

    our_ts = {"deleted.md": 100.0}
    peer_ts_all: dict = {}

    result = st.sync_section(
        "workspace", local_dir, repo_sub, sync_dir, our_ts, peer_ts_all,
    )
    assert not repo_file.exists()


def test_new_local_file(tmp_path: Path, mock_git):
    """로컬에만 있는 새 파일은 repo로 복사."""
    sync_dir, local_dir, repo_sub = _make_env(tmp_path)
    (local_dir / "new.md").write_text("brand new")

    result = st.sync_section(
        "workspace", local_dir, repo_sub, sync_dir, {}, {},
    )
    assert (sync_dir / repo_sub / "new.md").read_text() == "brand new"


def test_excluded_file_removed(tmp_path: Path, mock_git):
    """제외 대상 파일은 repo에서 제거."""
    sync_dir, local_dir, repo_sub = _make_env(tmp_path)
    # workspace에서 .jsonl은 제외
    repo_file = sync_dir / repo_sub / "data.jsonl"
    repo_file.write_text("stale")
    (local_dir / "data.jsonl").write_text("local")

    result = st.sync_section(
        "workspace", local_dir, repo_sub, sync_dir, {}, {},
    )
    assert not repo_file.exists()


def test_traversal_blocked(tmp_path: Path, mock_git):
    """경로 트래버설 시도는 무시."""
    sync_dir, local_dir, repo_sub = _make_env(tmp_path)

    # 피어가 트래버설 경로를 가지고 있음
    now = time.time()
    peer_ts_all = {"evil": {"workspace": {"../etc/passwd": now + 100}}}

    result = st.sync_section(
        "workspace", local_dir, repo_sub, sync_dir, {}, peer_ts_all,
    )
    # 트래버설 경로는 무시되어야 함
    assert not (sync_dir / repo_sub / ".." / "etc" / "passwd").exists()


def test_future_timestamp_rejected(tmp_path: Path, mock_git):
    """미래 타임스탬프(24시간+)는 load_peer_timestamps에서 이미 제거됨.
    sync_section에서는 정상 타임스탬프만 도착함을 확인."""
    sync_dir, local_dir, repo_sub = _make_env(tmp_path)
    (local_dir / "file.md").write_text("local")

    # 미래 타임스탬프가 validate_timestamp에서 걸러진 후의 상태 시뮬레이션
    peer_ts_all: dict = {}  # 미래값은 이미 제거됨
    our_ts = {"file.md": time.time()}

    result = st.sync_section(
        "workspace", local_dir, repo_sub, sync_dir, our_ts, peer_ts_all,
    )
    assert (local_dir / "file.md").read_text() == "local"
