"""
TDD 유닛 테스트: sync-timestamps.py의 should_include 함수

대상 함수 시그니처:
    should_include(filepath: str, section: str) -> bool

의존성:
    - EXCLUDES: 섹션별 제외 패턴 딕셔너리
    - CLAUDE_INCLUDES: claude-code 섹션 화이트리스트 집합

테스트 전략:
    1. workspace 섹션: EXCLUDES 패턴 기반 제외 + 기본 허용
    2. claude-code 섹션: EXCLUDES + CLAUDE_INCLUDES 화이트리스트 이중 필터
    3. 알 수 없는 섹션: EXCLUDES 없으면 모두 허용
    4. 경계 케이스: 빈 문자열, 중첩 경로, 특수 패턴
"""
import sys
import os
import pytest

# sync-timestamps.py를 모듈로 임포트하기 위한 경로 설정
# 실제 실행 시에는 프로젝트 루트를 sys.path에 추가해야 함
PROJECT_ROOT = "/Users/kangnam/projects/ai-config-sync"
sys.path.insert(0, PROJECT_ROOT)

# sync-timestamps.py는 하이픈이 포함된 파일명이므로 importlib 사용
import importlib.util

spec = importlib.util.spec_from_file_location(
    "sync_timestamps",
    os.path.join(PROJECT_ROOT, "sync-timestamps.py"),
)
sync_timestamps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_timestamps)

should_include = sync_timestamps.should_include


# ============================================================
# 1. workspace 섹션 - 기본 허용 (EXCLUDES만 적용)
# ============================================================
class TestWorkspaceSection:
    """workspace 섹션: EXCLUDES 패턴에 매칭되지 않으면 허용"""

    def test_normal_file_included(self):
        """일반 파일은 포함되어야 한다"""
        assert should_include("config.json", "workspace") is True

    def test_nested_normal_file_included(self):
        """중첩 경로의 일반 파일도 포함되어야 한다"""
        assert should_include("subdir/myfile.txt", "workspace") is True

    def test_exclude_notion_data_json(self):
        """notion_data_*.json 패턴은 제외되어야 한다"""
        assert should_include("notion_data_20260101.json", "workspace") is False

    def test_exclude_notion_data_json_nested(self):
        """중첩 경로에서도 notion_data_*.json 패턴은 파일명 파트 매칭으로 제외"""
        assert should_include("subdir/notion_data_abc.json", "workspace") is False

    def test_exclude_tmp_json(self):
        """tmp_*.json 패턴은 제외되어야 한다"""
        assert should_include("tmp_export.json", "workspace") is False

    def test_exclude_jsonl_files(self):
        """*.jsonl 패턴은 제외되어야 한다"""
        assert should_include("data.jsonl", "workspace") is False

    def test_exclude_jsonl_nested(self):
        """중첩 경로의 *.jsonl도 파일명 파트 매칭으로 제외"""
        assert should_include("logs/events.jsonl", "workspace") is False

    def test_exclude_dot_git(self):
        """.git 디렉토리 하위 파일은 제외되어야 한다"""
        assert should_include(".git/config", "workspace") is False

    def test_exclude_tools_flutter_dir(self):
        """tools/flutter 경로는 제외되어야 한다 (전체 경로 fnmatch)"""
        assert should_include("tools/flutter", "workspace") is False

    def test_exclude_tools_flutter_subpath(self):
        """tools/flutter/** 하위 파일은 제외되어야 한다"""
        assert should_include("tools/flutter/bin/flutter", "workspace") is False

    def test_exclude_tools_flutter_nested_deep(self):
        """tools/flutter 깊은 하위 경로도 제외되어야 한다"""
        assert should_include("tools/flutter/packages/flutter/lib/main.dart", "workspace") is False

    def test_tools_non_flutter_included(self):
        """tools/ 하위지만 flutter가 아닌 경로는 포함되어야 한다"""
        assert should_include("tools/scripts/build.sh", "workspace") is True

    def test_similar_but_not_matching_pattern(self):
        """notion_data로 시작하지만 패턴에 맞지 않으면 포함"""
        # notion_data.json은 notion_data_*.json 패턴에 매칭되지 않음
        assert should_include("notion_data.json", "workspace") is True

    def test_tmp_without_underscore_included(self):
        """tmp로 시작하지만 tmp_*.json 패턴이 아닌 파일은 포함"""
        assert should_include("tmpfile.json", "workspace") is True


# ============================================================
# 2. claude-code 섹션 - EXCLUDES + 화이트리스트 이중 필터
# ============================================================
class TestClaudeCodeSection:
    """claude-code 섹션: EXCLUDES 제외 후 CLAUDE_INCLUDES 화이트리스트 체크"""

    # --- 화이트리스트에 포함된 파일/디렉토리 ---

    def test_settings_json_included(self):
        """settings.json은 화이트리스트에 있으므로 포함"""
        assert should_include("settings.json", "claude-code") is True

    def test_claude_md_included(self):
        """CLAUDE.md는 화이트리스트에 있으므로 포함"""
        assert should_include("CLAUDE.md", "claude-code") is True

    def test_stop_hook_script_included(self):
        """stop-hook-git-check.sh는 화이트리스트에 있으므로 포함"""
        assert should_include("stop-hook-git-check.sh", "claude-code") is True

    def test_agents_dir_included(self):
        """agents/ 하위 파일은 화이트리스트에 있으므로 포함"""
        assert should_include("agents/my-agent.md", "claude-code") is True

    def test_plugins_dir_included(self):
        """plugins/ 하위 파일은 화이트리스트에 있으므로 포함"""
        assert should_include("plugins/some-plugin/init.py", "claude-code") is True

    def test_skills_dir_included(self):
        """skills/ 하위 파일은 화이트리스트에 있으므로 포함"""
        assert should_include("skills/my-skill/prompt.md", "claude-code") is True

    def test_agent_memory_dir_included(self):
        """agent-memory/ 하위 파일은 화이트리스트에 있으므로 포함"""
        assert should_include("agent-memory/data.json", "claude-code") is True

    def test_memory_dir_included(self):
        """memory/ 하위 파일은 화이트리스트에 있으므로 포함"""
        assert should_include("memory/notes.md", "claude-code") is True

    def test_todos_dir_included(self):
        """todos/ 하위 파일은 화이트리스트에 있으므로 포함"""
        assert should_include("todos/task.json", "claude-code") is True

    def test_teams_dir_included(self):
        """teams/ 하위 파일은 화이트리스트에 있으므로 포함"""
        assert should_include("teams/config.json", "claude-code") is True

    # --- 화이트리스트에 없는 파일/디렉토리 ---

    def test_random_file_excluded(self):
        """화이트리스트에 없는 파일은 제외"""
        assert should_include("random.txt", "claude-code") is False

    def test_projects_dir_excluded(self):
        """projects/ 디렉토리는 화이트리스트에 없으므로 제외"""
        assert should_include("projects/my-project/CLAUDE.md", "claude-code") is False

    def test_credentials_excluded(self):
        """credentials.json은 화이트리스트에 없으므로 제외"""
        assert should_include("credentials.json", "claude-code") is False

    # --- EXCLUDES에 의한 제외 (화이트리스트보다 우선) ---

    def test_history_jsonl_excluded_by_excludes(self):
        """history.jsonl은 EXCLUDES에 있으므로 화이트리스트 무관하게 제외"""
        assert should_include("history.jsonl", "claude-code") is False

    def test_usage_log_jsonl_excluded(self):
        """usage-log.jsonl은 EXCLUDES에 있으므로 제외"""
        assert should_include("usage-log.jsonl", "claude-code") is False

    def test_cache_dir_excluded(self):
        """cache 디렉토리 하위 파일은 EXCLUDES에 의해 제외"""
        assert should_include("cache/data.bin", "claude-code") is False

    def test_debug_dir_excluded(self):
        """debug 디렉토리 하위 파일은 EXCLUDES에 의해 제외"""
        assert should_include("debug/log.txt", "claude-code") is False

    def test_backups_dir_excluded(self):
        """backups 디렉토리 하위 파일은 EXCLUDES에 의해 제외"""
        assert should_include("backups/old.json", "claude-code") is False

    def test_file_history_dir_excluded(self):
        """file-history 디렉토리 하위 파일은 EXCLUDES에 의해 제외"""
        assert should_include("file-history/v1.json", "claude-code") is False

    def test_telemetry_dir_excluded(self):
        """telemetry 디렉토리 하위 파일은 EXCLUDES에 의해 제외"""
        assert should_include("telemetry/metrics.json", "claude-code") is False

    def test_session_env_dir_excluded(self):
        """session-env 디렉토리 하위 파일은 EXCLUDES에 의해 제외"""
        assert should_include("session-env/env.json", "claude-code") is False

    def test_shell_snapshots_dir_excluded(self):
        """shell-snapshots 디렉토리 하위 파일은 EXCLUDES에 의해 제외"""
        assert should_include("shell-snapshots/snapshot.json", "claude-code") is False

    def test_ide_dir_excluded(self):
        """ide 디렉토리 하위 파일은 EXCLUDES에 의해 제외"""
        assert should_include("ide/config.json", "claude-code") is False

    def test_downloads_dir_excluded(self):
        """downloads 디렉토리 하위 파일은 EXCLUDES에 의해 제외"""
        assert should_include("downloads/file.zip", "claude-code") is False

    def test_dot_git_excluded(self):
        """.git 디렉토리는 EXCLUDES에 의해 제외"""
        assert should_include(".git/HEAD", "claude-code") is False

    # --- 화이트리스트 경계 케이스 ---

    def test_skills_deep_nested_included(self):
        """skills 하위 깊은 경로도 최상위가 화이트리스트면 포함"""
        assert should_include("skills/agent-create/qa-engineer/prompt.md", "claude-code") is True

    def test_agents_single_file_included(self):
        """agents 디렉토리 바로 아래 파일도 포함"""
        assert should_include("agents/reviewer.md", "claude-code") is True


# ============================================================
# 3. 알 수 없는/커스텀 섹션
# ============================================================
class TestUnknownSection:
    """EXCLUDES에 정의되지 않은 섹션은 모든 파일을 허용해야 한다"""

    def test_any_file_included_for_unknown_section(self):
        """알 수 없는 섹션은 EXCLUDES가 없으므로 모두 포함"""
        assert should_include("anything/goes/here.txt", "unknown-section") is True

    def test_dot_git_not_excluded_for_unknown_section(self):
        """알 수 없는 섹션에서는 .git도 EXCLUDES가 없으므로 포함"""
        assert should_include(".git/config", "unknown-section") is True

    def test_empty_section_name(self):
        """빈 문자열 섹션도 EXCLUDES가 없으므로 모두 포함"""
        assert should_include("file.txt", "") is True


# ============================================================
# 4. 경계 케이스
# ============================================================
class TestEdgeCases:
    """경계 조건 및 특수 케이스"""

    def test_empty_filepath_workspace(self):
        """빈 filepath에 대한 workspace 섹션 처리"""
        # 빈 경로는 parts가 비어있으므로 EXCLUDES 매칭 안 됨 → True
        assert should_include("", "workspace") is True

    def test_empty_filepath_claude_code(self):
        """빈 filepath에 대한 claude-code 섹션: top이 빈 문자열이므로 화이트리스트 밖"""
        assert should_include("", "claude-code") is False

    def test_filepath_with_only_filename_workspace(self):
        """파일명만 있는 경로 (디렉토리 없음) - workspace"""
        assert should_include("README.md", "workspace") is True

    def test_filepath_with_only_filename_claude_code_in_whitelist(self):
        """파일명만 있는 경로 - claude-code 화이트리스트에 있는 파일"""
        assert should_include("CLAUDE.md", "claude-code") is True

    def test_filepath_with_only_filename_claude_code_not_in_whitelist(self):
        """파일명만 있는 경로 - claude-code 화이트리스트에 없는 파일"""
        assert should_include("README.md", "claude-code") is False

    def test_exclude_pattern_matches_any_part(self):
        """EXCLUDES 패턴이 경로의 중간 파트에도 매칭되는지 확인"""
        # workspace의 .git 패턴이 중간 파트에 있는 경우
        assert should_include("subdir/.git/config", "workspace") is False

    def test_claude_code_whitelist_checks_first_part_only(self):
        """claude-code 화이트리스트는 첫 번째 경로 파트만 확인한다"""
        # "other/skills/file.md"의 첫 파트는 "other"이므로 화이트리스트 밖
        assert should_include("other/skills/file.md", "claude-code") is False

    def test_workspace_non_excluded_extension(self):
        """workspace에서 제외 대상이 아닌 확장자는 포함"""
        assert should_include("config.yaml", "workspace") is True
        assert should_include("script.py", "workspace") is True
        assert should_include("data.json", "workspace") is True

    def test_workspace_jsonl_anywhere_in_path(self):
        """workspace에서 .jsonl 파일은 어떤 위치에 있든 제외"""
        assert should_include("deep/nested/path/file.jsonl", "workspace") is False

    def test_claude_code_excludes_take_priority_over_whitelist(self):
        """EXCLUDES가 화이트리스트보다 먼저 평가된다 (cache는 제외 대상)"""
        # "cache"라는 이름이 EXCLUDES에 있고, parts에 "cache"가 있으면 제외
        # 화이트리스트 체크까지 가지 않음
        assert should_include("cache", "claude-code") is False
