"""save_timestamps, print_includes, parse_args 추가 테스트."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import sync_timestamps as st


# ── save_timestamps (2개) ──

def test_save_normal(sync_env: dict):
    new_ts = {"workspace": {"file.md": 100.0}}
    st.save_timestamps(sync_env["ts_dir"], "test-host", new_ts)
    saved = json.loads(
        (sync_env["ts_dir"] / "test-host.json").read_text(encoding="utf-8")
    )
    assert saved["workspace"]["file.md"] == 100.0


def test_save_overwrites(sync_env: dict):
    old_ts = {"workspace": {"old.md": 50.0}}
    st.save_timestamps(sync_env["ts_dir"], "test-host", old_ts)
    new_ts = {"workspace": {"new.md": 200.0}}
    st.save_timestamps(sync_env["ts_dir"], "test-host", new_ts)
    saved = json.loads(
        (sync_env["ts_dir"] / "test-host.json").read_text(encoding="utf-8")
    )
    assert "new.md" in saved["workspace"]
    assert "old.md" not in saved["workspace"]


# ── print_includes (1개) ──

def test_print_includes(capsys):
    st.print_includes()
    out = capsys.readouterr().out.strip()
    items = out.split()
    assert "CLAUDE.md" in items
    assert "agents" in items
    assert "settings.json" in items


# ── parse_args edge cases (3개) ──

def test_parse_args_list_includes():
    """--list-includes는 SystemExit(0)."""
    result = subprocess.run(
        [sys.executable, "sync-timestamps.py", "--list-includes"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "CLAUDE.md" in result.stdout


def test_parse_args_no_args():
    """인수 없으면 exit 2."""
    result = subprocess.run(
        [sys.executable, "sync-timestamps.py"],
        capture_output=True, text=True,
    )
    assert result.returncode == 2
    assert "Usage:" in result.stderr


def test_parse_args_invalid_hostname():
    """유효하지 않은 hostname이면 exit 2."""
    result = subprocess.run(
        [sys.executable, "sync-timestamps.py", ".", "host/bad"],
        capture_output=True, text=True,
    )
    assert result.returncode == 2
    assert "ERROR" in result.stderr


# ── walk_all_files (1개) ──

def test_walk_all_files(tmp_path: Path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("b")
    result = st.walk_all_files(tmp_path)
    assert "a.txt" in result
    assert "sub/b.txt" in result


# ── git_cmd, git_bytes 실제 호출 (2개) ──

def test_git_cmd_real(tmp_path: Path):
    """실제 git 명령 실행."""
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True)
    out, rc = st.git_cmd(["status"], tmp_path)
    assert rc == 0


def test_git_bytes_real(tmp_path: Path):
    """실제 git bytes 명령."""
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True)
    out, rc = st.git_bytes(["status"], tmp_path)
    assert rc == 0
    assert isinstance(out, bytes)
