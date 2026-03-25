"""load_timestamps, load_peer_timestamps 테스트 — 7개."""

from __future__ import annotations

import json
import time
from pathlib import Path

import sync_timestamps as st


# ── load_timestamps (3개) ──

def test_load_normal(sync_env: dict):
    ts_data = {"workspace": {"file.md": 100.0}}
    ts_file = sync_env["ts_dir"] / "test-host.json"
    ts_file.write_text(json.dumps(ts_data), encoding="utf-8")
    result = st.load_timestamps(sync_env["ts_dir"], "test-host")
    assert result["workspace"]["file.md"] == 100.0


def test_load_missing(sync_env: dict):
    result = st.load_timestamps(sync_env["ts_dir"], "test-host")
    assert result == {}


def test_load_with_migration(sync_env: dict):
    ts_data = {"claude-config": {"file.md": 100.0}}
    ts_file = sync_env["ts_dir"] / "test-host.json"
    ts_file.write_text(json.dumps(ts_data), encoding="utf-8")
    result = st.load_timestamps(sync_env["ts_dir"], "test-host")
    assert "claude-code" in result
    assert "claude-config" not in result


# ── load_peer_timestamps (4개) ──

def test_peer_normal(sync_env: dict, mock_git):
    peer_ts = {"workspace": {"file.md": time.time() - 100}}
    mock_git.set_cmd(
        "ls-tree",
        "100644 blob abc123\ttimestamps/peer1.json",
    )
    mock_git.set_cmd("show", json.dumps(peer_ts))
    result = st.load_peer_timestamps(sync_env["sync_dir"], "test-host")
    assert "peer1" in result
    assert "file.md" in result["peer1"]["workspace"]


def test_peer_empty_output(sync_env: dict, mock_git):
    mock_git.set_cmd("ls-tree", "")
    result = st.load_peer_timestamps(sync_env["sync_dir"], "test-host")
    assert result == {}


def test_peer_parse_failure(sync_env: dict, mock_git):
    mock_git.set_cmd("ls-tree", "100644 blob abc\ttimestamps/peer1.json")
    mock_git.set_cmd("show", "not-json")
    result = st.load_peer_timestamps(sync_env["sync_dir"], "test-host")
    assert "peer1" not in result


def test_peer_excludes_self(sync_env: dict, mock_git):
    peer_ts = {"workspace": {"file.md": time.time()}}
    mock_git.set_cmd(
        "ls-tree",
        "100644 blob abc\ttimestamps/test-host.json",
    )
    mock_git.set_cmd("show", json.dumps(peer_ts))
    result = st.load_peer_timestamps(sync_env["sync_dir"], "test-host")
    assert "test-host" not in result
