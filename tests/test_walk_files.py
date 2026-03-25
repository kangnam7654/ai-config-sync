"""walk_files() 단위 테스트 — 3개."""

from __future__ import annotations

from pathlib import Path

import sync_timestamps as st


def test_walk_normal(tmp_path: Path):
    (tmp_path / "file1.md").write_text("hello")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "file2.md").write_text("world")
    result = st.walk_files(tmp_path, "workspace")
    assert "file1.md" in result
    assert "subdir/file2.md" in result


def test_walk_empty(tmp_path: Path):
    result = st.walk_files(tmp_path, "workspace")
    assert result == {}


def test_walk_nonexistent():
    result = st.walk_files(Path("/nonexistent/path"), "workspace")
    assert result == {}
