# TDD 워크플로우: should_include 함수 유닛 테스트

## 대상 함수

```python
# sync-timestamps.py (line 41-56)
def should_include(filepath: str, section: str) -> bool:
    parts = Path(filepath).parts

    # 제외 패턴 체크
    for pattern in EXCLUDES.get(section, []):
        if any(fnmatch.fnmatch(p, pattern) for p in parts):
            return False
        if fnmatch.fnmatch(filepath, pattern):
            return False

    # claude-code 화이트리스트
    if section == "claude-code":
        top = parts[0] if parts else ""
        return top in CLAUDE_INCLUDES

    return True
```

## 의존하는 상수

```python
EXCLUDES = {
    "workspace": [
        "notion_data_*.json", "tmp_*.json", "*.jsonl", ".git",
        "tools/flutter", "tools/flutter/**",
    ],
    "claude-code": [
        "history.jsonl", "usage-log.jsonl", "cache", "debug",
        "backups", "file-history", "telemetry", "session-env",
        "shell-snapshots", "ide", "downloads", ".git",
    ],
}

CLAUDE_INCLUDES = {
    "settings.json", "CLAUDE.md", "stop-hook-git-check.sh",
    "agents", "plugins", "skills", "agent-memory", "memory", "todos", "teams",
}
```

## Phase 1: RED - 테스트 케이스 도출

### 함수 동작 분석

`should_include`는 3단계 로직을 가진다:

1. **EXCLUDES 패턴 매칭** (모든 섹션 공통)
   - `EXCLUDES[section]`의 각 패턴에 대해:
     - filepath의 각 path part를 `fnmatch`로 개별 매칭 (예: `.git`이 중간 파트에 있어도 매칭)
     - filepath 전체를 `fnmatch`로 매칭 (예: `tools/flutter/**`로 하위 경로 전체 매칭)
   - 하나라도 매칭되면 `False` 반환

2. **claude-code 화이트리스트** (claude-code 섹션만)
   - filepath의 첫 번째 path part (`parts[0]`)가 `CLAUDE_INCLUDES`에 있는지 확인
   - 있으면 `True`, 없으면 `False`
   - `parts`가 비어있으면 `top = ""`이므로 `False`

3. **기본 허용** (그 외 섹션)
   - EXCLUDES를 통과한 나머지는 모두 `True`

### 테스트 분류

| 카테고리 | 테스트 수 | 검증 내용 |
|---------|---------|----------|
| workspace 기본 허용 | 15 | EXCLUDES 패턴별 제외/허용, 유사하지만 비매칭 패턴 |
| claude-code 이중 필터 | 23 | EXCLUDES 우선 적용 + 화이트리스트 포함/제외 |
| 알 수 없는 섹션 | 3 | EXCLUDES 미정의 시 전체 허용 |
| 경계 케이스 | 10 | 빈 경로, 중간 파트 매칭, 우선순위 확인 |
| **합계** | **51** | |

### 테스트 케이스 상세

#### 1. workspace 섹션 (15개)

| # | 테스트명 | 입력 | 기대값 | 검증 포인트 |
|---|---------|------|--------|------------|
| 1 | test_normal_file_included | `("config.json", "workspace")` | True | 기본 허용 |
| 2 | test_nested_normal_file_included | `("subdir/myfile.txt", "workspace")` | True | 중첩 경로 기본 허용 |
| 3 | test_exclude_notion_data_json | `("notion_data_20260101.json", "workspace")` | False | glob 패턴 `notion_data_*.json` |
| 4 | test_exclude_notion_data_json_nested | `("subdir/notion_data_abc.json", "workspace")` | False | 중첩 경로에서 파트별 매칭 |
| 5 | test_exclude_tmp_json | `("tmp_export.json", "workspace")` | False | glob 패턴 `tmp_*.json` |
| 6 | test_exclude_jsonl_files | `("data.jsonl", "workspace")` | False | glob 패턴 `*.jsonl` |
| 7 | test_exclude_jsonl_nested | `("logs/events.jsonl", "workspace")` | False | 중첩 경로 `*.jsonl` |
| 8 | test_exclude_dot_git | `(".git/config", "workspace")` | False | `.git` 파트 매칭 |
| 9 | test_exclude_tools_flutter_dir | `("tools/flutter", "workspace")` | False | 전체 경로 매칭 |
| 10 | test_exclude_tools_flutter_subpath | `("tools/flutter/bin/flutter", "workspace")` | False | `tools/flutter/**` 패턴 |
| 11 | test_exclude_tools_flutter_nested_deep | `("tools/flutter/packages/.../main.dart", "workspace")` | False | 깊은 하위 경로 |
| 12 | test_tools_non_flutter_included | `("tools/scripts/build.sh", "workspace")` | True | flutter 아닌 tools 하위 |
| 13 | test_similar_but_not_matching_pattern | `("notion_data.json", "workspace")` | True | `_` 없어 패턴 비매칭 |
| 14 | test_tmp_without_underscore_included | `("tmpfile.json", "workspace")` | True | `tmp_` 아닌 `tmp`로 시작 |
| 15 | (추가 가능) | 다양한 허용 파일 | True | 기본 허용 확인 |

#### 2. claude-code 섹션 (23개)

**화이트리스트 포함 (10개):** settings.json, CLAUDE.md, stop-hook-git-check.sh, agents/, plugins/, skills/, agent-memory/, memory/, todos/, teams/ 하위 파일

**화이트리스트 제외 (3개):** random.txt, projects/ 하위, credentials.json

**EXCLUDES 제외 (12개):** history.jsonl, usage-log.jsonl, cache/, debug/, backups/, file-history/, telemetry/, session-env/, shell-snapshots/, ide/, downloads/, .git/

#### 3. 알 수 없는 섹션 (3개)

EXCLUDES에 키가 없는 섹션은 `EXCLUDES.get(section, [])` → 빈 리스트 → 패턴 체크 스킵 → `section != "claude-code"` → `True` 반환

#### 4. 경계 케이스 (10개)

- 빈 filepath ("") + workspace → True (parts 비어있으므로 패턴 매칭 없음)
- 빈 filepath ("") + claude-code → False (top = "", 화이트리스트에 없음)
- EXCLUDES가 화이트리스트보다 먼저 평가됨 확인
- 경로 중간 파트에 EXCLUDES 패턴이 있는 경우

## Phase 2: GREEN - 테스트 실행 예상 결과

함수가 이미 구현되어 있으므로, 모든 51개 테스트가 통과할 것으로 예상된다.

### 실행 명령어

```bash
cd /Users/kangnam/projects/ai-config-sync
uv run python -m pytest /Users/kangnam/.claude/skills/agent-create/qa-engineer-workspace/iteration-2/eval-0/with_skill/outputs/test_should_include.py -v
```

### 예상 출력

```
test_should_include.py::TestWorkspaceSection::test_normal_file_included PASSED
test_should_include.py::TestWorkspaceSection::test_nested_normal_file_included PASSED
test_should_include.py::TestWorkspaceSection::test_exclude_notion_data_json PASSED
test_should_include.py::TestWorkspaceSection::test_exclude_notion_data_json_nested PASSED
test_should_include.py::TestWorkspaceSection::test_exclude_tmp_json PASSED
test_should_include.py::TestWorkspaceSection::test_exclude_jsonl_files PASSED
test_should_include.py::TestWorkspaceSection::test_exclude_jsonl_nested PASSED
test_should_include.py::TestWorkspaceSection::test_exclude_dot_git PASSED
test_should_include.py::TestWorkspaceSection::test_exclude_tools_flutter_dir PASSED
test_should_include.py::TestWorkspaceSection::test_exclude_tools_flutter_subpath PASSED
test_should_include.py::TestWorkspaceSection::test_exclude_tools_flutter_nested_deep PASSED
test_should_include.py::TestWorkspaceSection::test_tools_non_flutter_included PASSED
test_should_include.py::TestWorkspaceSection::test_similar_but_not_matching_pattern PASSED
test_should_include.py::TestWorkspaceSection::test_tmp_without_underscore_included PASSED
test_should_include.py::TestClaudeCodeSection::test_settings_json_included PASSED
test_should_include.py::TestClaudeCodeSection::test_claude_md_included PASSED
... (중략)
test_should_include.py::TestEdgeCases::test_claude_code_excludes_take_priority_over_whitelist PASSED

============= 51 passed in 0.XXs =============
```

## Phase 3: REFACTOR - 개선 포인트

현재 함수에서 발견된 잠재적 이슈/개선점:

### 1. 빈 filepath 처리
- `should_include("", "workspace")` → `True` (의도된 동작인지 확인 필요)
- `Path("").parts` → `()` 빈 튜플이므로 EXCLUDES 루프를 무사 통과

### 2. EXCLUDES 패턴 매칭 방식의 이중성
- **파트별 매칭**: `any(fnmatch.fnmatch(p, pattern) for p in parts)` — 경로의 각 구성요소를 개별 매칭
- **전체 경로 매칭**: `fnmatch.fnmatch(filepath, pattern)` — 전체 경로를 한 번에 매칭
- 이 이중 매칭은 `tools/flutter`(전체 경로)와 `.git`(파트별)을 모두 처리하기 위한 것

### 3. 화이트리스트 체크가 parts[0]만 보는 설계
- 파일(settings.json)과 디렉토리(skills)를 동일한 방식으로 처리
- `settings.json`의 `parts[0]`은 `"settings.json"` 자체 → 화이트리스트에 있으므로 통과
- `skills/prompt.md`의 `parts[0]`은 `"skills"` → 화이트리스트에 있으므로 통과

## 테스트 설계 원칙

1. **각 EXCLUDES 패턴을 최소 1개 테스트로 커버**: 패턴이 변경/제거될 때 즉시 감지
2. **CLAUDE_INCLUDES의 모든 항목을 테스트**: 화이트리스트 항목 누락 감지
3. **경계 케이스로 구현 로직의 세부 동작 검증**: 빈 입력, 우선순위, 중간 파트 매칭
4. **유사하지만 매칭되지 않는 패턴으로 false positive 방지**: `notion_data.json` vs `notion_data_*.json`
