"""should_include() 단위 테스트 — 12개."""

from __future__ import annotations

import sync_timestamps as st


# ── workspace 섹션: 포함/제외 조합 ──

def test_workspace_normal_file():
    assert st.should_include("MEMORY.md", "workspace") is True

def test_workspace_exclude_jsonl():
    assert st.should_include("data.jsonl", "workspace") is False

def test_workspace_exclude_notion():
    assert st.should_include("notion_data_abc.json", "workspace") is False

def test_workspace_exclude_tmp():
    assert st.should_include("tmp_backup.json", "workspace") is False

def test_workspace_exclude_flutter():
    assert st.should_include("tools/flutter/bin/cache", "workspace") is False

def test_workspace_nested_file():
    assert st.should_include("subdir/file.md", "workspace") is True


# ── claude-code 섹션: 화이트리스트 ──

def test_claude_whitelist_settings():
    assert st.should_include("settings.json", "claude-code") is True

def test_claude_whitelist_agents_subdir():
    assert st.should_include("agents/my-agent/agent.md", "claude-code") is True

def test_claude_reject_history():
    assert st.should_include("history.jsonl", "claude-code") is False

def test_claude_reject_unknown_top():
    assert st.should_include("unknown_dir/file.txt", "claude-code") is False


# ── 엣지 케이스 ──

def test_empty_filepath():
    # 빈 경로는 parts가 빈 tuple → top이 "" → CLAUDE_INCLUDES에 없음
    assert st.should_include("", "claude-code") is False

def test_exclude_git_dir():
    assert st.should_include(".git/config", "claude-code") is False
