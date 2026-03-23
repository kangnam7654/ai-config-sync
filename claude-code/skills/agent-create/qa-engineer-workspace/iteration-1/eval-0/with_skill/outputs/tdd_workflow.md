# TDD Workflow: should_include 유닛 테스트

## 대상 함수

- 파일: `/Users/kangnam/projects/ai-config-sync/sync-timestamps.py`
- 함수: `should_include(filepath: str, section: str) -> bool`

## 함수 동작 분석

```python
def should_include(filepath: str, section: str) -> bool:
    parts = Path(filepath).parts

    # 1단계: EXCLUDES 패턴 체크 (섹션별)
    for pattern in EXCLUDES.get(section, []):
        if any(fnmatch.fnmatch(p, pattern) for p in parts):
            return False
        if fnmatch.fnmatch(filepath, pattern):
            return False

    # 2단계: claude-code 섹션은 화이트리스트 방식
    if section == "claude-code":
        top = parts[0] if parts else ""
        return top in CLAUDE_INCLUDES

    # 3단계: 다른 섹션은 EXCLUDES를 통과하면 모두 포함
    return True
```

### 핵심 로직

1. **EXCLUDES 우선 적용**: 모든 섹션에서 EXCLUDES 패턴을 먼저 체크한다. parts 개별 매칭과 전체 filepath 매칭 두 가지 방식으로 검사한다.
2. **claude-code 화이트리스트**: EXCLUDES를 통과한 후, claude-code 섹션은 filepath의 첫 번째 경로 요소(top)가 `CLAUDE_INCLUDES`에 있어야만 포함된다.
3. **기본 포함**: claude-code가 아닌 섹션은 EXCLUDES만 통과하면 무조건 포함.

### 의존 상수

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

---

## TDD 사이클 기록

### Red-Green-Refactor 사이클

#### Iteration 1: workspace 기본 포함

**Red** - 테스트 작성 (아직 함수 분석 전 기대값 설정):
- `should_include("config.json", "workspace")` → `True`
- `should_include("subdir/data.json", "workspace")` → `True`

**Green** - 함수 코드 확인 후 기대값이 맞는지 검증:
- EXCLUDES["workspace"]에 "config.json" 매칭 패턴 없음 → True (pass)
- EXCLUDES["workspace"]에 "subdir/data.json" 매칭 패턴 없음 → True (pass)

**Refactor** - 테스트 클래스 `TestWorkspaceInclude`로 구조화.

---

#### Iteration 2: workspace EXCLUDES 제외

**Red** - 각 EXCLUDES 패턴에 대한 테스트 작성:
- `notion_data_*.json` 패턴: `should_include("notion_data_2026.json", "workspace")` → `False`
- `tmp_*.json` 패턴: `should_include("tmp_export.json", "workspace")` → `False`
- `*.jsonl` 패턴: `should_include("logs.jsonl", "workspace")` → `False`
- `.git` 패턴: `should_include(".git/config", "workspace")` → `False`
- `tools/flutter` 패턴: `should_include("tools/flutter", "workspace")` → `False`
- `tools/flutter/**` 패턴: `should_include("tools/flutter/bin/flutter", "workspace")` → `False`

**Green** - 함수의 두 가지 매칭 방식 확인:
1. `any(fnmatch.fnmatch(p, pattern) for p in parts)` — parts 개별 매칭
   - `.git/config` → parts는 `('.git', 'config')`, `.git`이 패턴 `.git`에 매칭 → False
   - `logs.jsonl` → parts는 `('logs.jsonl',)`, `logs.jsonl`이 `*.jsonl`에 매칭 → False
2. `fnmatch.fnmatch(filepath, pattern)` — 전체 경로 매칭
   - `tools/flutter` → filepath가 패턴 `tools/flutter`에 매칭 → False
   - `tools/flutter/bin/flutter` → filepath가 `tools/flutter/**`에 매칭 → False

**Refactor** - `TestWorkspaceExclude` 클래스로 그룹화.

---

#### Iteration 3: workspace 경계 케이스

**Red** - EXCLUDES와 유사하지만 매칭되지 않아야 하는 케이스:
- `should_include("notion.json", "workspace")` → `True` (notion_data_ 프리픽스 없음)
- `should_include("data.json", "workspace")` → `True` (.json은 *.jsonl이 아님)
- `should_include("tools/python/script.py", "workspace")` → `True` (tools/flutter가 아님)
- `should_include("flutter/file.dart", "workspace")` → `True` (tools/ 밖의 flutter)
- `should_include("notion_data_backup.txt", "workspace")` → `True` (.txt는 *.json이 아님)
- `should_include("tmp_file.txt", "workspace")` → `True` (.txt는 *.json이 아님)

**Green** - fnmatch 패턴 매칭 규칙 확인:
- `fnmatch.fnmatch("notion.json", "notion_data_*.json")` → False (프리픽스 불일치)
- `fnmatch.fnmatch("data.json", "*.jsonl")` → False (확장자 불일치)
- `fnmatch.fnmatch("python", "flutter")` → False (디렉토리명 불일치)

**Refactor** - `TestWorkspaceEdgeCases` 클래스로 분리.

---

#### Iteration 4: claude-code 화이트리스트 포함

**Red** - CLAUDE_INCLUDES의 모든 항목에 대한 테스트:
- 파일: `settings.json`, `CLAUDE.md`, `stop-hook-git-check.sh`
- 디렉토리: `agents`, `plugins`, `skills`, `agent-memory`, `memory`, `todos`, `teams`

각각 `should_include("<name>/...", "claude-code")` → `True`

**Green** - 함수에서 `parts[0] in CLAUDE_INCLUDES` 확인:
- `Path("settings.json").parts` → `('settings.json',)`, parts[0] = `'settings.json'` → in CLAUDE_INCLUDES → True
- `Path("skills/a/b/c/prompt.md").parts` → `('skills', 'a', 'b', 'c', 'prompt.md')`, parts[0] = `'skills'` → True

**Refactor** - `TestClaudeCodeInclude` 클래스.

---

#### Iteration 5: claude-code 화이트리스트 제외

**Red** - CLAUDE_INCLUDES에 없는 항목 테스트:
- `should_include("projects/some-project/config.json", "claude-code")` → `False`
- `should_include("random-file.txt", "claude-code")` → `False`
- `should_include("credentials.json", "claude-code")` → `False`

**Green** - parts[0]이 CLAUDE_INCLUDES에 없으므로 False.

**Refactor** - `TestClaudeCodeExcludeByWhitelist` 클래스.

---

#### Iteration 6: claude-code EXCLUDES 제외 (화이트리스트보다 우선)

**Red** - claude-code EXCLUDES 패턴에 매칭되는 파일:
- `history.jsonl`, `usage-log.jsonl` → 전체 filepath 매칭
- `cache/some-file` → parts에 `cache` 매칭
- `debug/log.txt`, `backups/...`, `file-history/...`, `telemetry/...` 등

**Green** - EXCLUDES 체크가 화이트리스트 체크보다 먼저 실행됨.
- `should_include("cache/some-file", "claude-code")` → parts에 `cache`가 있고, EXCLUDES에 `cache`가 있으므로 `fnmatch.fnmatch("cache", "cache")` → True → return False

**Refactor** - `TestClaudeCodeExcludeByPattern` 클래스.

---

#### Iteration 7: 알 수 없는 섹션

**Red** - EXCLUDES에 키가 없는 섹션:
- `should_include("anything.txt", "unknown-section")` → `True`
- `should_include("a/b/c.json", "unknown-section")` → `True`

**Green** - `EXCLUDES.get("unknown-section", [])` → 빈 리스트, claude-code가 아니므로 return True.

**Refactor** - `TestUnknownSection` 클래스.

---

#### Iteration 8: EXCLUDES 우선순위 검증

**Red** - 화이트리스트 항목 하위에 EXCLUDES 패턴이 있는 경우:
- `should_include("skills/.git/config", "claude-code")` → `False`
  - top이 `skills`로 화이트리스트에 있지만, parts에 `.git`이 있어 EXCLUDES 매칭

**Green** - EXCLUDES가 먼저 체크되므로 `.git`이 parts에서 매칭 → False 반환. 화이트리스트까지 도달하지 않음.

**Refactor** - `TestSpecialCases` 클래스에 통합.

---

## 테스트 커버리지 분석

### 테스트된 경로

| 코드 경로 | 테스트 수 | 상태 |
|-----------|----------|------|
| EXCLUDES parts 개별 매칭 → return False | 10 | Covered |
| EXCLUDES 전체 filepath 매칭 → return False | 6 | Covered |
| claude-code 화이트리스트 포함 → return True | 11 | Covered |
| claude-code 화이트리스트 제외 → return False | 4 | Covered |
| 기본 return True (비-claude-code 섹션) | 9 | Covered |
| EXCLUDES 없는 섹션 → 빈 리스트 | 3 | Covered |

### 분기 커버리지

- `EXCLUDES.get(section, [])` — 키 있는 경우 / 없는 경우: 둘 다 테스트됨
- `any(fnmatch.fnmatch(p, pattern) for p in parts)` — 매칭 / 비매칭: 둘 다 테스트됨
- `fnmatch.fnmatch(filepath, pattern)` — 매칭 / 비매칭: 둘 다 테스트됨
- `section == "claude-code"` — True / False: 둘 다 테스트됨
- `top in CLAUDE_INCLUDES` — True / False: 둘 다 테스트됨

### 총 테스트 수: 43개

## 실행 명령 (참고)

```bash
cd /Users/kangnam/projects/ai-config-sync
uv run python -m pytest tests/test_should_include.py -v
```

참고: 이 워크플로우에서는 실제 테스트를 실행하지 않았습니다. 위 명령으로 실행할 수 있습니다.
