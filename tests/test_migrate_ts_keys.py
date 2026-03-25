"""migrate_ts_keys() 단위 테스트 — 4개."""

from __future__ import annotations

import sync_timestamps as st


def test_normal_migration():
    ts = {"claude-config": {"file.md": 100.0}}
    result = st.migrate_ts_keys(ts)
    assert "claude-code" in result
    assert "claude-config" not in result
    assert result["claude-code"]["file.md"] == 100.0


def test_already_migrated():
    ts = {"claude-code": {"file.md": 200.0}}
    result = st.migrate_ts_keys(ts)
    assert result["claude-code"]["file.md"] == 200.0


def test_empty_dict():
    result = st.migrate_ts_keys({})
    assert result == {}


def test_both_keys_no_overwrite():
    """신 키가 이미 있으면 구 키를 마이그레이션하지 않는다."""
    ts = {
        "claude-config": {"old.md": 100.0},
        "claude-code": {"new.md": 200.0},
    }
    result = st.migrate_ts_keys(ts)
    assert "claude-config" in result  # 마이그레이션 안 됨
    assert result["claude-code"]["new.md"] == 200.0
