"""
should_include() 함수 유닛 테스트

테스트 대상: sync-timestamps.py의 should_include(filepath, section)
동작 요약:
  1. EXCLUDES 패턴에 매칭되면 False 반환
  2. section이 "claude-code"이면 CLAUDE_INCLUDES 화이트리스트에 top-level이 포함될 때만 True
  3. 그 외 섹션은 EXCLUDES에 걸리지 않으면 True

실행: uv run python -m pytest test_should_include.py -v
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# sync-timestamps.py를 모듈로 임포트하기 위한 경로 설정
SYNC_SCRIPT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent.parent / "projects" / "ai-config-sync"
sys.path.insert(0, str(SYNC_SCRIPT))

# 모듈명에 하이픈이 있으므로 importlib으로 임포트
import importlib.util

spec = importlib.util.spec_from_file_location(
    "sync_timestamps", SYNC_SCRIPT / "sync-timestamps.py"
)
sync_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_mod)

should_include = sync_mod.should_include
EXCLUDES = sync_mod.EXCLUDES
CLAUDE_INCLUDES = sync_mod.CLAUDE_INCLUDES


# ============================================================
# workspace 섹션 테스트
# ============================================================
class TestWorkspaceSection:
    """workspace 섹션의 EXCLUDES 패턴 기반 필터링 테스트"""

    # -- 포함되어야 하는 파일 --

    def test_normal_file_included(self):
        """일반 파일은 포함"""
        assert should_include("config.json", "workspace") is True

    def test_nested_normal_file_included(self):
        """하위 디렉토리의 일반 파일도 포함"""
        assert should_include("subdir/config.yaml", "workspace") is True

    def test_deeply_nested_file_included(self):
        """깊은 중첩 경로의 일반 파일도 포함"""
        assert should_include("a/b/c/d/file.txt", "workspace") is True

    def test_json_file_not_matching_exclude_pattern(self):
        """notion_data_ 접두사가 아닌 json 파일은 포함"""
        assert should_include("data.json", "workspace") is True

    def test_non_matching_tmp_prefix(self):
        """tmp_ 접두사가 아닌 json 파일은 포함"""
        assert should_include("my_tmp_data.json", "workspace") is True

    # -- 제외되어야 하는 파일 --

    def test_exclude_notion_data_json(self):
        """notion_data_*.json 패턴 제외"""
        assert should_include("notion_data_2026.json", "workspace") is False

    def test_exclude_notion_data_json_nested(self):
        """하위 디렉토리의 notion_data_*.json도 제외 (parts 매칭)"""
        assert should_include("subdir/notion_data_abc.json", "workspace") is False

    def test_exclude_tmp_json(self):
        """tmp_*.json 패턴 제외"""
        assert should_include("tmp_export.json", "workspace") is False

    def test_exclude_tmp_json_nested(self):
        """하위 디렉토리의 tmp_*.json도 제외"""
        assert should_include("data/tmp_cache.json", "workspace") is False

    def test_exclude_jsonl_files(self):
        """*.jsonl 파일 제외"""
        assert should_include("logs.jsonl", "workspace") is False

    def test_exclude_jsonl_nested(self):
        """하위 디렉토리의 *.jsonl 파일도 제외"""
        assert should_include("logs/output.jsonl", "workspace") is False

    def test_exclude_dot_git(self):
        """.git 디렉토리 경로 제외"""
        assert should_include(".git/config", "workspace") is False

    def test_exclude_flutter_tools(self):
        """tools/flutter 경로 제외"""
        assert should_include("tools/flutter", "workspace") is False

    def test_exclude_flutter_tools_nested(self):
        """tools/flutter/** 하위 파일 제외"""
        assert should_include("tools/flutter/bin/flutter", "workspace") is False

    def test_exclude_flutter_tools_deep_nested(self):
        """tools/flutter 깊은 하위 경로도 제외"""
        assert should_include("tools/flutter/packages/flutter/lib/main.dart", "workspace") is False


# ============================================================
# claude-code 섹션 테스트
# ============================================================
class TestClaudeCodeSection:
    """claude-code 섹션의 EXCLUDES + CLAUDE_INCLUDES 화이트리스트 테스트"""

    # -- CLAUDE_INCLUDES 화이트리스트에 포함되는 항목 --

    def test_include_settings_json(self):
        """settings.json은 화이트리스트에 포함"""
        assert should_include("settings.json", "claude-code") is True

    def test_include_claude_md(self):
        """CLAUDE.md는 화이트리스트에 포함"""
        assert should_include("CLAUDE.md", "claude-code") is True

    def test_include_stop_hook(self):
        """stop-hook-git-check.sh는 화이트리스트에 포함"""
        assert should_include("stop-hook-git-check.sh", "claude-code") is True

    def test_include_agents_dir(self):
        """agents/ 디렉토리의 파일은 화이트리스트에 포함"""
        assert should_include("agents/my-agent.md", "claude-code") is True

    def test_include_plugins_dir(self):
        """plugins/ 디렉토리의 파일은 화이트리스트에 포함"""
        assert should_include("plugins/plugin.json", "claude-code") is True

    def test_include_skills_dir(self):
        """skills/ 디렉토리의 파일은 화이트리스트에 포함"""
        assert should_include("skills/my-skill/skill.md", "claude-code") is True

    def test_include_skills_deeply_nested(self):
        """skills/ 깊은 하위 파일도 화이트리스트에 포함"""
        assert should_include("skills/a/b/c/d.json", "claude-code") is True

    def test_include_agent_memory_dir(self):
        """agent-memory/ 디렉토리의 파일은 화이트리스트에 포함"""
        assert should_include("agent-memory/data.json", "claude-code") is True

    def test_include_memory_dir(self):
        """memory/ 디렉토리의 파일은 화이트리스트에 포함"""
        assert should_include("memory/MEMORY.md", "claude-code") is True

    def test_include_todos_dir(self):
        """todos/ 디렉토리의 파일은 화이트리스트에 포함"""
        assert should_include("todos/todo.md", "claude-code") is True

    def test_include_teams_dir(self):
        """teams/ 디렉토리의 파일은 화이트리스트에 포함"""
        assert should_include("teams/team-config.json", "claude-code") is True

    # -- CLAUDE_INCLUDES 화이트리스트에 포함되지 않는 항목 --

    def test_exclude_unknown_top_level_file(self):
        """화이트리스트에 없는 최상위 파일은 제외"""
        assert should_include("random-file.txt", "claude-code") is False

    def test_exclude_unknown_directory(self):
        """화이트리스트에 없는 디렉토리의 파일은 제외"""
        assert should_include("unknown-dir/file.txt", "claude-code") is False

    def test_exclude_projects_dir(self):
        """projects/ 디렉토리는 화이트리스트에 없으므로 제외"""
        assert should_include("projects/my-project/CLAUDE.md", "claude-code") is False

    def test_exclude_worktrees_dir(self):
        """worktrees/ 디렉토리는 화이트리스트에 없으므로 제외"""
        assert should_include("worktrees/agent-123/file.py", "claude-code") is False

    # -- EXCLUDES가 CLAUDE_INCLUDES보다 우선하는 케이스 --

    def test_excludes_override_history_jsonl(self):
        """history.jsonl은 EXCLUDES에 의해 제외 (화이트리스트 체크 전 필터링)"""
        assert should_include("history.jsonl", "claude-code") is False

    def test_excludes_override_usage_log(self):
        """usage-log.jsonl은 EXCLUDES에 의해 제외"""
        assert should_include("usage-log.jsonl", "claude-code") is False

    def test_excludes_override_cache(self):
        """cache 디렉토리 경로는 EXCLUDES에 의해 제외"""
        assert should_include("cache/data.bin", "claude-code") is False

    def test_excludes_override_debug(self):
        """debug 디렉토리 경로는 EXCLUDES에 의해 제외"""
        assert should_include("debug/log.txt", "claude-code") is False

    def test_excludes_override_backups(self):
        """backups 디렉토리 경로는 EXCLUDES에 의해 제외"""
        assert should_include("backups/old-config.json", "claude-code") is False

    def test_excludes_override_file_history(self):
        """file-history 디렉토리 경로는 EXCLUDES에 의해 제외"""
        assert should_include("file-history/v1.json", "claude-code") is False

    def test_excludes_override_telemetry(self):
        """telemetry 디렉토리 경로는 EXCLUDES에 의해 제외"""
        assert should_include("telemetry/events.json", "claude-code") is False

    def test_excludes_override_session_env(self):
        """session-env 디렉토리 경로는 EXCLUDES에 의해 제외"""
        assert should_include("session-env/env.json", "claude-code") is False

    def test_excludes_override_shell_snapshots(self):
        """shell-snapshots 디렉토리 경로는 EXCLUDES에 의해 제외"""
        assert should_include("shell-snapshots/snap.txt", "claude-code") is False

    def test_excludes_override_ide(self):
        """ide 디렉토리 경로는 EXCLUDES에 의해 제외"""
        assert should_include("ide/vscode.json", "claude-code") is False

    def test_excludes_override_downloads(self):
        """downloads 디렉토리 경로는 EXCLUDES에 의해 제외"""
        assert should_include("downloads/file.zip", "claude-code") is False

    def test_excludes_override_dot_git(self):
        """.git 디렉토리는 EXCLUDES에 의해 제외"""
        assert should_include(".git/HEAD", "claude-code") is False


# ============================================================
# 존재하지 않는 섹션 테스트
# ============================================================
class TestUnknownSection:
    """EXCLUDES에 정의되지 않은 섹션은 모든 파일을 포함"""

    def test_unknown_section_includes_all(self):
        """알 수 없는 섹션은 제외 규칙이 없으므로 모두 포함"""
        assert should_include("any/file.txt", "unknown-section") is True

    def test_unknown_section_includes_json(self):
        """알 수 없는 섹션에서 json 파일도 포함"""
        assert should_include("data.json", "other") is True

    def test_unknown_section_includes_jsonl(self):
        """알 수 없는 섹션에서는 *.jsonl도 제외 안 됨"""
        assert should_include("log.jsonl", "custom") is True


# ============================================================
# 엣지 케이스
# ============================================================
class TestEdgeCases:
    """경계 조건 및 엣지 케이스"""

    def test_empty_filepath(self):
        """빈 filepath 처리 (에러 없이 동작)"""
        # Path("").parts == () → EXCLUDES에 매칭 안 됨
        # claude-code의 경우 parts가 비므로 top이 "" → CLAUDE_INCLUDES에 없으므로 False
        result = should_include("", "claude-code")
        assert result is False

    def test_empty_filepath_workspace(self):
        """빈 filepath, workspace 섹션 (에러 없이 동작)"""
        result = should_include("", "workspace")
        assert result is True

    def test_single_filename_workspace(self):
        """파일명만 있는 경로 (디렉토리 없음)"""
        assert should_include("config.yaml", "workspace") is True

    def test_exclude_pattern_exact_match_as_part(self):
        """EXCLUDES 패턴이 경로의 한 part와 정확히 일치하는 경우"""
        # "cache"는 claude-code EXCLUDES에 있음
        # filepath "cache" → parts == ("cache",) → fnmatch("cache", "cache") → True → 제외
        assert should_include("cache", "claude-code") is False

    def test_exclude_pattern_in_middle_of_path(self):
        """EXCLUDES 패턴이 경로 중간에 있는 경우"""
        # "backups" 패턴이 parts 중 하나와 매칭
        assert should_include("skills/backups/file.txt", "claude-code") is False

    def test_claude_includes_top_level_file_only(self):
        """화이트리스트의 파일명이 최상위에 있을 때만 매칭"""
        # "settings.json"은 CLAUDE_INCLUDES에 있지만 top-level part로 매칭
        assert should_include("settings.json", "claude-code") is True

    def test_claude_includes_does_not_match_nested(self):
        """화이트리스트 항목이 하위 경로에 있으면 매칭 안 됨"""
        # "subdir/settings.json"의 top part는 "subdir" → 화이트리스트에 없음
        assert should_include("subdir/settings.json", "claude-code") is False

    def test_workspace_no_whitelist(self):
        """workspace 섹션은 화이트리스트 없이 EXCLUDES만 적용"""
        # EXCLUDES에 없는 아무 파일이나 포함됨
        assert should_include("anything/goes/here.txt", "workspace") is True

    def test_notion_data_without_json_extension(self):
        """notion_data_ 접두사지만 .json이 아닌 파일은 포함 (패턴이 *.json이므로)"""
        assert should_include("notion_data_2026.txt", "workspace") is True

    def test_tools_without_flutter(self):
        """tools/ 하위지만 flutter가 아닌 경로는 포함"""
        assert should_include("tools/nodejs/bin/node", "workspace") is True

    def test_git_directory_at_any_depth(self):
        """.git이 경로 어디에든 있으면 제외"""
        assert should_include("some/path/.git/objects/pack", "workspace") is False

    def test_dotgit_as_part_workspace(self):
        """.git 자체가 filepath인 경우 workspace에서 제외"""
        assert should_include(".git", "workspace") is False
