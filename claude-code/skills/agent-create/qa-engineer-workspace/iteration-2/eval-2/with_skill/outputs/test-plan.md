# Test Plan: Sync Engine

**Source**: `/Users/kangnam/.claude/skills/agent-create/qa-engineer-workspace/iteration-1/eval-2/test-design-doc.md`
**Generated**: 2026-03-23
**Implementation Status**: 9 of 11 requirements implemented

## Summary

| Type | Count | P0 | P1 | P2 |
|------|-------|----|----|----|
| Unit | 52 | 24 | 16 | 12 |
| Integration | 17 | 8 | 6 | 3 |
| E2E | 10 | 0 | 7 | 3 |
| **Total** | **79** | **32** | **29** | **18** |

## Test Cases

### Purpose

설계문서 성공 기준: "어느 기기에서 설정을 변경하든 30분 이내에 모든 기기에 반영된다."

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 1 | peer_newer_file_applied_to_local_and_repo | integration | P0 | 로컬 mtime=100.0, 피어 ts=200.0, FETCH_HEAD에 새 내용 존재 | 로컬 파일과 repo 파일 모두 피어 내용으로 갱신됨 | Implemented |
| 2 | local_newer_file_copied_to_repo | integration | P0 | 로컬 mtime=200.0, 피어 ts=100.0 | 로컬 파일 내용이 repo에 shutil.copy2로 복사됨 | Implemented |
| 3 | equal_timestamp_keeps_local | integration | P0 | 로컬 mtime=100.0, 피어 ts=100.0 | peer_file_ts > our_file_ts가 False이므로 로컬 유지 (동점 시 로컬 우선) | Implemented |
| 4 | multiple_peers_selects_newest | integration | P1 | peer_A ts=100.0, peer_B ts=200.0, peer_C ts=150.0 | peer_B(ts=200.0)의 내용이 적용됨 | Implemented |
| 5 | timestamp_json_persisted_after_sync | integration | P0 | 동기화 정상 완료 | `timestamps/{hostname}.json` 파일 생성, JSON 파싱 가능, 섹션별 파일 mtime 포함 | Implemented |

### Architecture

설계문서에서 식별된 컴포넌트: `sync.sh`, `sync-timestamps.py`, `timestamps/`, 로컬 파일시스템, Git repo.

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 6 | sync_sh_calls_python_with_correct_args | e2e | P1 | `bash sync.sh` 실행 | `sync-timestamps.py`가 `$SYNC_DIR`과 `$HOSTNAME` 인수로 호출됨 | Implemented |
| 7 | sync_sh_detects_macos_platform | e2e | P1 | `OSTYPE=darwin*` 환경 | `PLATFORM="macos"`, `PYTHON_CMD="python3"` | Implemented |
| 8 | sync_sh_detects_windows_platform | e2e | P1 | `OSTYPE=msys` 환경 | `PLATFORM="windows"`, `PYTHON_CMD="python"`, `PYTHONUTF8=1` 설정 | Implemented |
| 9 | sync_sh_detects_linux_platform | e2e | P1 | `OSTYPE=linux-gnu` 환경 | `PLATFORM="linux"`, `PYTHON_CMD="python3"` | Implemented |
| 10 | cron_30min_interval_configured | e2e | P2 | 크론 설정 확인 | 30분 간격 실행 등록 | Implemented |

### Data Flow

설계문서 5단계 데이터 흐름: fetch -> timestamp 비교 -> 피어 적용 -> state 기록 -> push.

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 11 | fetch_head_peer_timestamps_read | integration | P1 | FETCH_HEAD에 `timestamps/peer.json` 존재 | `git ls-tree` + `git show`로 피어 ts dict 파싱됨 | Implemented |
| 12 | fetch_head_missing_graceful_handling | integration | P1 | `git ls-tree FETCH_HEAD` returncode=128 | `peer_ts_all` 빈 dict, 에러 없이 진행 | Implemented |
| 13 | peer_content_fetched_via_git_show | integration | P0 | 피어가 최신, `git show FETCH_HEAD:{repo_subdir}/{filepath}` 호출 | returncode=0이면 바이트 내용 반환, 로컬+repo에 write_bytes | Implemented |
| 14 | git_show_failure_skips_file | integration | P1 | `git show` returncode!=0 | 해당 파일 갱신 스킵, 에러 없이 다음 파일 처리 | Implemented |
| 15 | state_file_generated_after_sync | e2e | P1 | 동기화 완료 | `state/{hostname}.md` 파일 생성, Environment/OpenClaw/Claude Code 섹션 포함 | Implemented |
| 16 | git_add_limited_to_sync_paths_only | e2e | P1 | `sync.sh` 실행 | `git add -A openclaw/workspace claude-code timestamps state`만 실행 (다른 경로 포함 안 됨) | Implemented |
| 17 | windows_skips_push | e2e | P1 | `PLATFORM=windows` | `git push` 호출 없음, "pull-only mode" 메시지 출력 | Implemented |
| 18 | push_conflict_triggers_rebase_retry | e2e | P2 | 첫 `git push` 실패 | `git pull --rebase origin main` 후 재push | Implemented |
| 19 | windows_resets_to_origin_main | e2e | P2 | `PLATFORM=windows`, 동기화 완료 | `git reset --hard origin/main` 실행 | Implemented |

### API Design

설계문서에 명시된 3개 API와 코드에서 추가 식별된 6개 헬퍼 함수.

#### `should_include(filepath, section)` -- 화이트리스트/블랙리스트 필터

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 20 | include_normal_workspace_file | unit | P0 | `("MEMORY.md", "workspace")` | `True` | Implemented |
| 21 | include_nested_workspace_file | unit | P0 | `("agents/reviewer.md", "workspace")` | `True` | Implemented |
| 22 | exclude_notion_data_glob | unit | P0 | `("notion_data_2026.json", "workspace")` | `False` | Implemented |
| 23 | exclude_tmp_glob | unit | P0 | `("tmp_backup.json", "workspace")` | `False` | Implemented |
| 24 | exclude_jsonl_glob | unit | P0 | `("data.jsonl", "workspace")` | `False` | Implemented |
| 25 | exclude_git_directory | unit | P0 | `(".git", "workspace")` | `False` | Implemented |
| 26 | exclude_flutter_directory | unit | P0 | `("tools/flutter", "workspace")` | `False` | Implemented |
| 27 | exclude_flutter_deep_nested | unit | P0 | `("tools/flutter/bin/dart", "workspace")` | `False` | Implemented |
| 28 | include_claude_code_whitelist_settings | unit | P0 | `("settings.json", "claude-code")` | `True` | Implemented |
| 29 | include_claude_code_whitelist_claude_md | unit | P0 | `("CLAUDE.md", "claude-code")` | `True` | Implemented |
| 30 | include_claude_code_whitelist_skills_subdir | unit | P0 | `("skills/doc-loop/prompt.md", "claude-code")` | `True` | Implemented |
| 31 | include_claude_code_whitelist_agents | unit | P0 | `("agents/reviewer.md", "claude-code")` | `True` | Implemented |
| 32 | include_claude_code_whitelist_plugins | unit | P1 | `("plugins/my-plugin/config.json", "claude-code")` | `True` | Implemented |
| 33 | include_claude_code_whitelist_memory | unit | P1 | `("memory/MEMORY.md", "claude-code")` | `True` | Implemented |
| 34 | include_claude_code_whitelist_todos | unit | P1 | `("todos/list.json", "claude-code")` | `True` | Implemented |
| 35 | include_claude_code_whitelist_teams | unit | P1 | `("teams/team-config.json", "claude-code")` | `True` | Implemented |
| 36 | exclude_claude_code_history_jsonl | unit | P0 | `("history.jsonl", "claude-code")` | `False` (EXCLUDES 우선) | Implemented |
| 37 | exclude_claude_code_cache | unit | P0 | `("cache", "claude-code")` | `False` | Implemented |
| 38 | exclude_claude_code_non_whitelist_dir | unit | P0 | `("unknown-dir/file.txt", "claude-code")` | `False` | Implemented |
| 39 | exclude_claude_code_non_whitelist_file | unit | P1 | `("randomfile.txt", "claude-code")` | `False` | Implemented |
| 40 | include_unknown_section_all_files | unit | P1 | `("file.txt", "unknown-section")` | `True` (EXCLUDES에 키 없음, claude-code가 아님) | Implemented |
| 41 | empty_filepath_no_crash | unit | P2 | `("", "workspace")` | 에러 없이 bool 반환 | Implemented |
| 42 | empty_filepath_claude_code | unit | P2 | `("", "claude-code")` | `False` (빈 parts, top이 빈 문자열 -> CLAUDE_INCLUDES에 없음) | Implemented |

#### `walk_files(base, section)` -- 디렉토리 탐색 + 필터링

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 43 | walk_basic_files | unit | P0 | `tmp/a.md`, `tmp/b.txt` 생성, section="workspace" | dict에 `"a.md"`, `"b.txt"` 키, 값은 float mtime > 0 | Implemented |
| 44 | walk_subdirectory_posix_path | unit | P0 | `tmp/sub/deep/file.txt` 생성 | 키가 `"sub/deep/file.txt"` (POSIX 형식) | Implemented |
| 45 | walk_excludes_git_directory | unit | P0 | `tmp/.git/config`, `tmp/a.md` 생성 | dict에 `"a.md"`만 존재 | Implemented |
| 46 | walk_applies_excludes_pattern | unit | P1 | `tmp/notion_data_x.json`, `tmp/a.md`, section="workspace" | `"a.md"`만 포함 | Implemented |
| 47 | walk_claude_code_whitelist | unit | P1 | `tmp/settings.json`, `tmp/cache/data`, section="claude-code" | `"settings.json"`만 포함 | Implemented |
| 48 | walk_empty_directory | unit | P2 | 빈 tmp 디렉토리, section="workspace" | `{}` | Implemented |
| 49 | walk_nonexistent_path | unit | P2 | 존재하지 않는 경로 | `{}` | Implemented |

#### `migrate_ts_keys(ts)` -- 타임스탬프 키 마이그레이션

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 50 | migrate_old_key_to_new | unit | P0 | `{"claude-config": {"f.md": 1.0}}` | `{"claude-code": {"f.md": 1.0}}` | Implemented |
| 51 | migrate_already_new_key_no_change | unit | P0 | `{"claude-code": {"f.md": 1.0}}` | 변경 없음 | Implemented |
| 52 | migrate_empty_dict | unit | P1 | `{}` | `{}` | Implemented |
| 53 | migrate_non_target_key_untouched | unit | P1 | `{"workspace": {"f.md": 1.0}}` | 변경 없음 | Implemented |
| 54 | migrate_both_keys_exist_preserves_new | unit | P0 | `{"claude-config": {"a": 1}, "claude-code": {"b": 2}}` | old key 유지, new key 유지 (마이그레이션 안 함) | Implemented |
| 55 | migrate_returns_same_object | unit | P1 | 임의 dict ref | 반환값 `is` 입력값 (in-place 변경) | Implemented |
| 56 | migrate_old_key_removed | unit | P1 | `{"claude-config": {"a": 1}}` | 마이그레이션 후 `"claude-config" not in result` | Implemented |

#### `mtime(p)` -- 파일 수정 시간 조회 (코드에서 추가 식별)

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 57 | mtime_existing_file | unit | P2 | 존재하는 임시 파일 | float > 0.0 | Implemented |
| 58 | mtime_nonexistent_file | unit | P2 | 존재하지 않는 경로 | `0.0` | Implemented |
| 59 | mtime_permission_error | unit | P2 | `Path.stat` raises `PermissionError` | `0.0` (bare except 처리) | Implemented |

#### `walk_all_files(base)` -- 전체 파일 수집 (코드에서 추가 식별)

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 60 | walk_all_basic | unit | P1 | `tmp/a.md`, `tmp/b/c.txt` 생성 | `{"a.md", "b/c.txt"}` | Implemented |
| 61 | walk_all_excludes_git | unit | P1 | `tmp/.git/HEAD`, `tmp/a.md` 생성 | `{"a.md"}` | Implemented |
| 62 | walk_all_nonexistent_path | unit | P2 | 존재하지 않는 경로 | `set()` | Implemented |

#### `unlink_if_file(path)` -- 파일/심볼릭 링크 삭제 (코드에서 추가 식별)

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 63 | unlink_regular_file | unit | P1 | 존재하는 일반 파일 | 파일 삭제됨 | Implemented |
| 64 | unlink_symlink | unit | P1 | 심볼릭 링크 | 링크 삭제, 대상 파일 유지 | Implemented |
| 65 | unlink_directory_skipped | unit | P1 | 디렉토리 경로 | 삭제 안 됨, 에러 없음 | Implemented |
| 66 | unlink_nonexistent_no_error | unit | P2 | 존재하지 않는 경로 | 에러 없이 반환 | Implemented |

#### `prune_empty_dirs(base)` -- 빈 디렉토리 정리 (코드에서 추가 식별)

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 67 | prune_nested_empty_dirs | unit | P2 | `a/b/c/` 모두 비어있음 | 하위부터 모두 삭제 | Implemented |
| 68 | prune_preserves_dirs_with_files | unit | P2 | `a/file.txt` 존재, `b/` 비어있음 | `b/`만 삭제, `a/` 유지 | Implemented |
| 69 | prune_nonexistent_base_no_error | unit | P2 | 존재하지 않는 경로 | 에러 없이 반환 | Implemented |

#### `git_cmd(args, cwd)` / `git_bytes(args, cwd)` -- Git 래퍼 (코드에서 추가 식별)

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 70 | git_cmd_success_strips_output | unit | P2 | mock: stdout=`"abc\n"`, rc=0 | `("abc", 0)` | Implemented |
| 71 | git_cmd_failure_returns_code | unit | P2 | mock: stdout=`""`, rc=128 | `("", 128)` | Implemented |
| 72 | git_bytes_preserves_binary | unit | P2 | mock: stdout=`b"\xff\xfe"`, rc=0 | `(b"\xff\xfe", 0)` | Implemented |
| 73 | git_bytes_uses_encoding_utf8 | unit | P1 | mock 검사 | `git_cmd`의 subprocess.run 호출에 `encoding="utf-8"` 포함 확인 | Implemented |

### File Structure

설계문서 명시 파일 구조: `sync.sh`, `sync-timestamps.py`, `timestamps/`, `state/`, `openclaw/workspace/`, `claude-code/`.

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 74 | timestamps_dir_created_if_missing | integration | P0 | `timestamps/` 디렉토리 없는 상태에서 main() 실행 | `ts_dir.mkdir(exist_ok=True)`에 의해 자동 생성 | Implemented |
| 75 | repo_section_dir_created_if_missing | integration | P0 | `openclaw/workspace/` 없는 상태 | `repo_section.mkdir(parents=True, exist_ok=True)` 자동 생성 | Implemented |
| 76 | local_parent_dirs_created_for_peer_file | integration | P1 | 피어에만 존재하는 `sub/new/file.md` | `local_path.parent.mkdir(parents=True, exist_ok=True)` 후 write | Implemented |
| 77 | setup_windows_copies_claude_includes_items | e2e | P2 | `setup-windows.sh` 실행 | for 루프 항목(CLAUDE.md, settings.json, agents 등)이 `~/.claude/`로 복사 | Implemented |

### Decision Rationale

설계문서에서 채택/기각된 설계 결정 검증.

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 78 | newest_wins_not_three_way_merge | unit | P0 | 로컬 ts=100, 피어 ts=200, 내용이 다른 두 파일 | 피어 내용으로 단순 덮어쓰기 (3-way merge 없음), 충돌 표시자 없음 | Implemented |
| 79 | windows_pull_only_no_push_executed | integration | P1 | `PLATFORM=windows` 시뮬레이션 | commit/push 로직 실행 안 됨, `git reset --hard origin/main`만 실행 | Implemented |

## Gaps

| # | Gap Description | Recommendation | Suggested Type | Suggested Priority |
|---|----------------|----------------|---------------|-------------------|
| 1 | `sys.argv` 인수 부족 시 예외 처리 없음 -- `main()`에서 `sys.argv[1]`, `sys.argv[2]` 접근 시 IndexError 발생 | `main()`에 argparse 또는 len(sys.argv) 검사 추가, 에러 메시지 출력 후 종료. 테스트: 인수 0개/1개로 호출 시 명확한 에러 메시지 확인 | unit | P1 |
| 2 | `mtime()` 함수의 bare `except:` -- 모든 예외를 삼켜 디버깅 어려움 | `except OSError:`로 범위 제한 권장. 테스트: `OSError` 외 예외(예: `KeyboardInterrupt`)가 전파되는지 확인 | unit | P2 |
| 3 | 설계문서에 삭제 전파 로직 미기술 -- 실제 구현에서 로컬 삭제 시 repo에서도 제거하는 동작이 있으나 설계문서에 없음 | 설계문서 Data Flow에 "로컬에서 삭제된 파일은 repo에서도 삭제" 단계 추가. 해당 동작은 이미 테스트 케이스 INT(#1-5)에 포함 | integration | P0 |
| 4 | 설계문서에 다중 피어 처리 미기술 -- "피어 타임스탬프"로 단수 암시하나 실제로는 여러 피어 중 파일별 최신 선택 | 설계문서 Data Flow에 "여러 피어가 있을 경우 파일별로 가장 최신인 피어의 내용을 선택" 명시 권장 | integration | P1 |
| 5 | 설계문서에 `walk_all_files`, `unlink_if_file`, `prune_empty_dirs`, `git_cmd`, `git_bytes`, `mtime` 미기재 -- 코드에만 존재하는 6개 헬퍼 함수 | 설계문서 API Design 섹션에 헬퍼 함수 목록 추가 권장. 테스트 케이스는 본 플랜에서 이미 생성됨 (#57-73) | unit | P2 |
| 6 | `setup-windows.sh`의 for 루프 항목과 `CLAUDE_INCLUDES`의 동기화 검증 없음 -- 한쪽만 수정 시 불일치 발생 가능 | `setup-windows.sh`의 항목 리스트와 `CLAUDE_INCLUDES` set을 비교하는 테스트 추가 | integration | P1 |
| 7 | 큰 바이너리 파일(100MB+) 처리 시 메모리 사용량 테스트 없음 -- `git_bytes`가 전체 내용을 메모리에 적재 | 대용량 파일 시나리오 테스트 추가 (크래시 없음 확인) | integration | P2 |
| 8 | 피어 타임스탬프 JSON 손상(잘못된 JSON) 시 에러 처리 테스트 없음 -- 코드에 try/except 있으나 설계문서에 미기재 | 잘못된 JSON 입력 시 해당 피어만 무시하고 진행하는지 테스트 추가 | integration | P1 |
| 9 | claude-code 섹션의 심볼릭 링크 제거 동작이 설계문서에 미기재 | 설계문서에 "claude-code repo 내 심볼릭 링크는 동기화 후 삭제" 명시 권장. 테스트 케이스는 본 플랜 #65에서 커버 | unit | P1 |
| 10 | 한글/유니코드 파일명 처리 검증 부재 -- `as_posix()` 사용으로 대부분 안전하나 명시적 테스트 없음 | 한글 파일명(`가나자와-여행플랜.pdf`)으로 walk_files, should_include 호출 테스트 추가 | unit | P2 |
| 11 | `openclaw.json` 등 민감 파일의 동기화 방지 검증 없음 -- `.gitignore`에 의존하나 `should_include` 수준 검증 없음 | `.gitignore` 패턴이 `openclaw/openclaw.json`을 실제로 제외하는지 git 명령 레벨 테스트 추가 | e2e | P0 |

## Cross-Reference

| Design Doc Section | Requirements Found | Test Cases Generated | Coverage |
|-------------------|-------------------|---------------------|----------|
| Purpose | 1 | 5 | 5/5 = 100% |
| Architecture | 3 | 5 | 5/5 = 100% |
| Data Flow | 5 | 9 | 9/9 = 100% |
| API Design | 9 | 54 | 54/54 = 100% |
| File Structure | 4 | 4 | 4/4 = 100% |
| Decision Rationale | 2 | 2 | 2/2 = 100% |

---

## Implementation Notes

### 테스트 인프라 요구사항

현재 프로젝트에 테스트 프레임워크가 설정되어 있지 않다 (`CLAUDE.md`: "테스트 프레임워크 없음"). 테스트 실행을 위해 다음 설정이 필요하다:

```bash
uv add --dev pytest pytest-cov
```

### 모듈 임포트 주의

`sync-timestamps.py`는 파일명에 하이픈이 포함되어 있어 일반 `import`가 불가하다. 테스트에서는 다음 방식을 사용해야 한다:

```python
import importlib.util
spec = importlib.util.spec_from_file_location("sync_timestamps", "sync-timestamps.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
```

### `main()` 통합 테스트 Mock 전략

- `sys.argv`: monkeypatch로 주입
- `sections` dict 내 하드코딩된 홈 디렉토리 경로: `Path.expanduser`를 monkeypatch하거나 `sections` dict 자체를 monkeypatch
- Git 명령: `git_cmd`, `git_bytes` 함수를 monkeypatch
- 파일시스템: `tmp_path` fixture로 격리된 환경 구성

### 테스트 파일 구조

```
ai-config-sync/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # 공통 fixture (sync_env, 모듈 로딩)
│   ├── test_should_include.py     # #20-42
│   ├── test_walk_files.py         # #43-49, #60-62
│   ├── test_migrate_ts_keys.py    # #50-56
│   ├── test_helpers.py            # #57-59, #63-73 (mtime, unlink, prune, git)
│   ├── test_main_integration.py   # #1-5, #11-14, #74-76, #78-79
│   └── test_edge_cases.py         # Gaps 섹션 테스트
└── sync-timestamps.py
```

### 실행 명령

```bash
# 전체 테스트
uv run python -m pytest tests/ -q

# 커버리지 포함
uv run python -m pytest tests/ --cov --cov-fail-under=80

# 특정 모듈만
uv run python -m pytest tests/test_should_include.py -v
```
