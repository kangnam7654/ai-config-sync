"""mtime, unlink_if_file, prune_empty_dirs 테스트 — 9개."""

from __future__ import annotations

import os
from pathlib import Path

import sync_timestamps as st


# ── mtime (2개) ──

def test_mtime_existing(tmp_path: Path):
    f = tmp_path / "file.txt"
    f.write_text("data")
    assert st.mtime(f) > 0

def test_mtime_nonexistent(tmp_path: Path):
    assert st.mtime(tmp_path / "no_such_file") == 0.0


# ── unlink_if_file (4개) ──

def test_unlink_file(tmp_path: Path):
    f = tmp_path / "file.txt"
    f.write_text("data")
    st.unlink_if_file(f)
    assert not f.exists()

def test_unlink_symlink(tmp_path: Path):
    target = tmp_path / "target.txt"
    target.write_text("data")
    link = tmp_path / "link.txt"
    link.symlink_to(target)
    st.unlink_if_file(link)
    assert not link.exists()
    assert target.exists()  # 원본 유지

def test_unlink_directory(tmp_path: Path):
    d = tmp_path / "mydir"
    d.mkdir()
    st.unlink_if_file(d)
    assert d.exists()  # 디렉토리는 삭제하지 않음

def test_unlink_nonexistent(tmp_path: Path):
    """존재하지 않는 파일은 에러 없이 무시."""
    st.unlink_if_file(tmp_path / "nope")  # 예외 없음


# ── prune_empty_dirs (3개) ──

def test_prune_empty(tmp_path: Path):
    d = tmp_path / "a" / "b" / "c"
    d.mkdir(parents=True)
    st.prune_empty_dirs(tmp_path)
    assert not (tmp_path / "a").exists()

def test_prune_nonempty(tmp_path: Path):
    d = tmp_path / "a" / "b"
    d.mkdir(parents=True)
    (d / "file.txt").write_text("keep")
    st.prune_empty_dirs(tmp_path)
    assert d.exists()
    assert (d / "file.txt").exists()

def test_prune_nested_mixed(tmp_path: Path):
    """빈 디렉토리만 제거, 파일 있는 디렉토리는 유지."""
    (tmp_path / "a" / "b" / "c").mkdir(parents=True)
    (tmp_path / "a" / "d").mkdir(parents=True)
    (tmp_path / "a" / "d" / "file.txt").write_text("keep")
    st.prune_empty_dirs(tmp_path)
    assert not (tmp_path / "a" / "b").exists()
    assert (tmp_path / "a" / "d" / "file.txt").exists()
