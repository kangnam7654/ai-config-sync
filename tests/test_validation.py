"""validate_hostname, validate_filepath, validate_timestamp 단위 테스트 — 15개."""

from __future__ import annotations

import time

import pytest
import sync_timestamps as st


# ── validate_hostname (5개) ──

def test_hostname_valid_simple():
    assert st.validate_hostname("my-host") == "my-host"

def test_hostname_valid_alphanumeric():
    assert st.validate_hostname("MacBookPro2024") == "MacBookPro2024"

def test_hostname_invalid_slash():
    with pytest.raises(SystemExit) as exc:
        st.validate_hostname("host/name")
    assert exc.value.code == 2

def test_hostname_invalid_special():
    with pytest.raises(SystemExit) as exc:
        st.validate_hostname("host@name")
    assert exc.value.code == 2

def test_hostname_empty():
    with pytest.raises(SystemExit) as exc:
        st.validate_hostname("")
    assert exc.value.code == 2


# ── validate_filepath (5개) ──

def test_filepath_valid():
    assert st.validate_filepath("agents/my-agent.md", "claude-code") is True

def test_filepath_traversal():
    assert st.validate_filepath("../etc/passwd", "workspace") is False

def test_filepath_absolute():
    assert st.validate_filepath("/etc/passwd", "workspace") is False

def test_filepath_null_byte():
    assert st.validate_filepath("file\x00.txt", "workspace") is False

def test_filepath_empty():
    assert st.validate_filepath("", "workspace") is False


# ── validate_timestamp (5개) ──

def test_timestamp_valid():
    ts = time.time() - 3600
    assert st.validate_timestamp(ts, "file.md") == ts

def test_timestamp_non_numeric():
    assert st.validate_timestamp("not-a-number", "file.md") is None

def test_timestamp_negative():
    assert st.validate_timestamp(-1.0, "file.md") is None

def test_timestamp_future_exceeded():
    future = time.time() + 200000  # > 24시간
    assert st.validate_timestamp(future, "file.md") is None

def test_timestamp_boundary():
    """24시간 이내 미래값은 허용."""
    near_future = time.time() + 3600  # 1시간 뒤
    result = st.validate_timestamp(near_future, "file.md")
    assert result == near_future
