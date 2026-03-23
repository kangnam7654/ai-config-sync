"""
TDD 유닛 테스트: should_include(filepath, section)

테스트 대상: sync-timestamps.py의 should_include 함수
프로젝트: /Users/kangnam/projects/ai-config-sync

실행 방법:
  cd /Users/kangnam/projects/ai-config-sync
  uv run python -m pytest tests/test_should_include.py -v
"""

import sys
from pathlib import Path

import pytest

# sync-timestamps.py를 임포트하기 위해 프로젝트 루트를 sys.path에 추가
PROJECT_ROOT = Path("/Users/kangnam/projects/ai-config-sync")
sys.path.insert(0, str(PROJECT_ROOT))

# 테스트 대상 모듈에서 함수와 상수를 임포트
# (모듈명에 하이픈이 있으므로 importlib 사용)
import importlib

sync_mod = importlib.import_module("sync-timestamps")
should_include = sync_mod.should_include
EXCLUDES = sync_mod.EXCLUDES
CLAUDE_INCLUDES = sync_mod.CLAUDE_INCLUDES


# ============================================================
# 1. workspace 섹션 - 기본 포함 케이스
# ============================================================
class TestWorkspaceInclude:
    """workspace 섹션: EXCLUDES에 매칭되지 않는 파일은 포함되어야 한다."""

    def test_normal_json_file(self):
        """일반 JSON 파일은 포함"""
        assert should_include("config.json", "workspace") is True

    def test_nested_file(self):
        """중첩 경로의 일반 파일은 포함"""
        assert should_include("subdir/data.json", "workspace") is True

    def test_text_file(self):
        """텍스트 파일은 포함"""
        assert should_include("notes.txt", "workspace") is True

    def test_deeply_nested_file(self):
        """깊은 중첩 경로의 파일도 포함"""
        assert should_include("a/b/c/d/file.py", "workspace") is True


# ============================================================
# 2. workspace 섹션 - EXCLUDES 패턴 매칭으로 제외되는 케이스
# ============================================================
class TestWorkspaceExclude:
    """workspace 섹션: EXCLUDES 패턴에 매칭되는 파일은 제외되어야 한다."""

    def test_exclude_notion_data_json(self):
        """notion_data_*.json 패턴 매칭 → 제외"""
        assert should_include("notion_data_2026.json", "workspace") is False

    def test_exclude_notion_data_with_suffix(self):
        """notion_data_*.json 다른 변형도 제외"""
        assert should_include("notion_data_backup.json", "workspace") is False

    def test_exclude_tmp_json(self):
        """tmp_*.json 패턴 매칭 → 제외"""
        assert should_include("tmp_export.json", "workspace") is False

    def test_exclude_jsonl_extension(self):
        """*.jsonl 확장자 → 제외"""
        assert should_include("logs.jsonl", "workspace") is False

    def test_exclude_jsonl_in_subdir(self):
        """하위 디렉토리의 *.jsonl도 제외 (parts 매칭)"""
        assert should_include("subdir/data.jsonl", "workspace") is False

    def test_exclude_dot_git(self):
        """.git 디렉토리 자체 → 제외"""
        assert should_include(".git", "workspace") is False

    def test_exclude_dot_git_subpath(self):
        """.git 하위 경로 → 제외 (parts에 .git 포함)"""
        assert should_include(".git/config", "workspace") is False

    def test_exclude_tools_flutter(self):
        """tools/flutter 경로 → 제외"""
        assert should_include("tools/flutter", "workspace") is False

    def test_exclude_tools_flutter_subpath(self):
        """tools/flutter/** 하위 파일 → 제외"""
        assert should_include("tools/flutter/bin/flutter", "workspace") is False

    def test_exclude_tools_flutter_nested_deep(self):
        """tools/flutter 깊은 하위도 제외"""
        assert should_include("tools/flutter/packages/flutter/lib/src/widget.dart", "workspace") is False


# ============================================================
# 3. workspace 섹션 - 제외되지 않아야 하는 경계 케이스
# ============================================================
class TestWorkspaceEdgeCases:
    """workspace 섹션: EXCLUDES 패턴과 유사하지만 매칭되지 않는 케이스."""

    def test_notion_without_data_prefix(self):
        """notion_data_ 프리픽스 없는 notion 파일은 포함"""
        assert should_include("notion.json", "workspace") is True

    def test_tmp_without_underscore(self):
        """tmp_ 프리픽스가 아닌 tmp 파일은 포함"""
        assert should_include("temporary.json", "workspace") is True

    def test_json_not_jsonl(self):
        """.json 확장자는 *.jsonl 패턴에 매칭되지 않아 포함"""
        assert should_include("data.json", "workspace") is True

    def test_tools_not_flutter(self):
        """tools/ 하위지만 flutter가 아닌 경로는 포함"""
        assert should_include("tools/python/script.py", "workspace") is True

    def test_flutter_not_in_tools(self):
        """tools/ 밖의 flutter 디렉토리는 포함 (패턴이 tools/flutter)"""
        # "flutter" 자체가 parts에 있고, EXCLUDES에 "tools/flutter"가 있음
        # fnmatch.fnmatch("flutter", "tools/flutter") → False
        # fnmatch.fnmatch("flutter", "tools/flutter/**") → False
        # parts 개별 매칭: fnmatch.fnmatch("flutter", "tools/flutter") → False
        assert should_include("flutter/file.dart", "workspace") is True


# ============================================================
# 4. claude-code 섹션 - 화이트리스트(CLAUDE_INCLUDES) 포함 케이스
# ============================================================
class TestClaudeCodeInclude:
    """claude-code 섹션: CLAUDE_INCLUDES에 있는 top-level 항목은 포함."""

    def test_settings_json(self):
        """settings.json은 화이트리스트에 포함"""
        assert should_include("settings.json", "claude-code") is True

    def test_claude_md(self):
        """CLAUDE.md는 화이트리스트에 포함"""
        assert should_include("CLAUDE.md", "claude-code") is True

    def test_stop_hook_script(self):
        """stop-hook-git-check.sh는 화이트리스트에 포함"""
        assert should_include("stop-hook-git-check.sh", "claude-code") is True

    def test_agents_directory(self):
        """agents 디렉토리는 화이트리스트에 포함"""
        assert should_include("agents/my-agent.md", "claude-code") is True

    def test_plugins_directory(self):
        """plugins 디렉토리는 화이트리스트에 포함"""
        assert should_include("plugins/plugin.json", "claude-code") is True

    def test_skills_directory(self):
        """skills 디렉토리는 화이트리스트에 포함"""
        assert should_include("skills/my-skill/prompt.md", "claude-code") is True

    def test_agent_memory_directory(self):
        """agent-memory 디렉토리는 화이트리스트에 포함"""
        assert should_include("agent-memory/data.json", "claude-code") is True

    def test_memory_directory(self):
        """memory 디렉토리는 화이트리스트에 포함"""
        assert should_include("memory/MEMORY.md", "claude-code") is True

    def test_todos_directory(self):
        """todos 디렉토리는 화이트리스트에 포함"""
        assert should_include("todos/todo.md", "claude-code") is True

    def test_teams_directory(self):
        """teams 디렉토리는 화이트리스트에 포함"""
        assert should_include("teams/team-config.json", "claude-code") is True

    def test_skills_deeply_nested(self):
        """skills 하위 깊은 경로도 포함 (top이 skills이므로)"""
        assert should_include("skills/a/b/c/prompt.md", "claude-code") is True


# ============================================================
# 5. claude-code 섹션 - 화이트리스트에 없어서 제외되는 케이스
# ============================================================
class TestClaudeCodeExcludeByWhitelist:
    """claude-code 섹션: CLAUDE_INCLUDES에 없는 top-level 항목은 제외."""

    def test_projects_directory(self):
        """projects는 화이트리스트에 없으므로 제외"""
        assert should_include("projects/some-project/config.json", "claude-code") is False

    def test_unknown_file(self):
        """화이트리스트에 없는 파일은 제외"""
        assert should_include("random-file.txt", "claude-code") is False

    def test_credentials(self):
        """credentials.json은 화이트리스트에 없으므로 제외"""
        assert should_include("credentials.json", "claude-code") is False

    def test_statsig_directory(self):
        """statsig 디렉토리는 화이트리스트에 없으므로 제외"""
        assert should_include("statsig/config.json", "claude-code") is False


# ============================================================
# 6. claude-code 섹션 - EXCLUDES 패턴으로 제외되는 케이스
#    (화이트리스트 체크 이전에 EXCLUDES가 먼저 적용됨)
# ============================================================
class TestClaudeCodeExcludeByPattern:
    """claude-code 섹션: EXCLUDES 패턴에 매칭되면 화이트리스트와 무관하게 제외."""

    def test_exclude_history_jsonl(self):
        """history.jsonl → EXCLUDES 매칭으로 제외"""
        assert should_include("history.jsonl", "claude-code") is False

    def test_exclude_usage_log_jsonl(self):
        """usage-log.jsonl → EXCLUDES 매칭으로 제외"""
        assert should_include("usage-log.jsonl", "claude-code") is False

    def test_exclude_cache_directory(self):
        """cache 디렉토리 → EXCLUDES 매칭으로 제외"""
        assert should_include("cache/some-file", "claude-code") is False

    def test_exclude_debug_directory(self):
        """debug 디렉토리 → EXCLUDES 매칭으로 제외"""
        assert should_include("debug/log.txt", "claude-code") is False

    def test_exclude_backups_directory(self):
        """backups 디렉토리 → EXCLUDES 매칭으로 제외"""
        assert should_include("backups/backup-2026.tar", "claude-code") is False

    def test_exclude_file_history(self):
        """file-history 디렉토리 → EXCLUDES 매칭으로 제외"""
        assert should_include("file-history/v1.json", "claude-code") is False

    def test_exclude_telemetry(self):
        """telemetry 디렉토리 → EXCLUDES 매칭으로 제외"""
        assert should_include("telemetry/events.json", "claude-code") is False

    def test_exclude_session_env(self):
        """session-env 디렉토리 → EXCLUDES 매칭으로 제외"""
        assert should_include("session-env/env.json", "claude-code") is False

    def test_exclude_shell_snapshots(self):
        """shell-snapshots 디렉토리 → EXCLUDES 매칭으로 제외"""
        assert should_include("shell-snapshots/snap.json", "claude-code") is False

    def test_exclude_ide(self):
        """ide 디렉토리 → EXCLUDES 매칭으로 제외"""
        assert should_include("ide/settings.json", "claude-code") is False

    def test_exclude_downloads(self):
        """downloads 디렉토리 → EXCLUDES 매칭으로 제외"""
        assert should_include("downloads/file.zip", "claude-code") is False

    def test_exclude_dot_git_claude(self):
        """.git → EXCLUDES 매칭으로 제외"""
        assert should_include(".git/HEAD", "claude-code") is False


# ============================================================
# 7. 알 수 없는 섹션 - EXCLUDES 없음, 화이트리스트 없음
# ============================================================
class TestUnknownSection:
    """존재하지 않는 섹션: EXCLUDES도 없고, claude-code가 아니므로 항상 True."""

    def test_unknown_section_any_file(self):
        """알 수 없는 섹션은 모든 파일을 포함"""
        assert should_include("anything.txt", "unknown-section") is True

    def test_unknown_section_nested_path(self):
        """알 수 없는 섹션은 중첩 경로도 포함"""
        assert should_include("a/b/c.json", "unknown-section") is True

    def test_empty_section(self):
        """빈 문자열 섹션도 EXCLUDES 없으므로 포함"""
        assert should_include("file.txt", "") is True


# ============================================================
# 8. 빈 filepath / 특수 케이스
# ============================================================
class TestSpecialCases:
    """경계 케이스 및 특수 입력."""

    def test_single_filename_workspace(self):
        """파일명만 있는 경우 workspace에서 포함"""
        assert should_include("readme.md", "workspace") is True

    def test_claude_code_top_level_file_in_whitelist(self):
        """claude-code에서 top-level 파일이 화이트리스트에 있으면 포함
        (parts[0]이 파일명 자체)"""
        assert should_include("CLAUDE.md", "claude-code") is True

    def test_claude_code_excludes_take_priority_over_includes(self):
        """EXCLUDES가 CLAUDE_INCLUDES보다 먼저 체크됨.
        만약 화이트리스트 항목 하위에 EXCLUDES 패턴이 매칭되면 제외.
        예: skills/.git/config → .git이 EXCLUDES에 있으므로 제외"""
        assert should_include("skills/.git/config", "claude-code") is False

    def test_workspace_partial_pattern_no_match(self):
        """notion_data 프리픽스지만 .json이 아닌 파일 → *.json 매칭 안됨 → 포함"""
        assert should_include("notion_data_backup.txt", "workspace") is True

    def test_workspace_tmp_non_json(self):
        """tmp_ 프리픽스지만 .json이 아닌 파일 → tmp_*.json 매칭 안됨 → 포함"""
        assert should_include("tmp_file.txt", "workspace") is True
