---
title: Design Spec — ai-config-sync P0+P1+P2 개선
date: 2026-03-25
status: APPROVED (CTO Design Gate 8.70/10, Plan-critic 9.00/10)
scope: 16건 (P0: 4, P1: 5, P2: 7)
source: audit-report.md + arch-spec.md 흡수
---

# Design Spec

## 목적

audit-report에서 식별된 16건의 개선 사항을 구현하여 합성 점수를 5.045에서 8.0 이상으로 끌어올린다.
완료 조건: `uv run python -m pytest tests/ -q --cov --cov-fail-under=80` 전체 통과 (55개 이상 테스트, 커버리지 80%+).

---

## 베이스라인 점수 (audit-report 기준)

| 영역 | 점수 |
|------|------|
| 코드 품질 | 5.4 |
| 보안 | 7.0 |
| 아키텍처 | 6.85 |
| 테스트 | 1.3 |
| Repo Health | 6.0 |
| **가중 총점** | **5.045** |

---

## 파일 변경 목록

| 파일 | 작업 | 관련 ID |
|------|------|---------|
| sync-timestamps.py | 대규모 수정: main() 분리 4개 함수, 검증 함수 4개 추가, bare except 수정, 타입 어노테이션, --list-includes | CODE-001~002,005,007, SEC-001~002,004, ARCH-001 |
| sync.sh | 수정: push 에러 핸들링 | CODE-003 |
| setup.sh | 수정: CLAUDE_INCLUDES 동적 참조, 로그 경로, 토큰 umask | ARCH-001, SEC-003, SEC-005 |
| setup-windows.sh | 수정: CLAUDE_INCLUDES 동적 참조, 로그 경로 | ARCH-001, SEC-003 |
| setup-mac.sh | 수정: deprecated 리다이렉트, 토큰 umask | CODE-006, SEC-005 |
| pyproject.toml | 신규 | TEST-001 |
| tests/conftest.py | 신규 | TEST-001 |
| tests/test_should_include.py | 신규 (12 tests) | TEST-001 |
| tests/test_migrate_ts_keys.py | 신규 (4 tests) | TEST-001 |
| tests/test_validation.py | 신규 (15 tests) | TEST-001, SEC-001~004 |
| tests/test_walk_files.py | 신규 (3 tests) | TEST-001 |
| tests/test_helpers.py | 신규 (6 tests: mtime 2, unlink 4) | TEST-001, CODE-004 |
| tests/test_sync_section.py | 신규 (8 tests) | TEST-001 |
| tests/test_load_timestamps.py | 신규 (4+3 tests) | TEST-001 |
| .github/workflows/test.yml | 신규 | REPO-002 |

---

## 구현 순서

### Phase 1: 인프라 + 무파괴 변경 (1-1, 1-2, 1-3 병렬 가능)

**1-1. TEST-001a: pyproject.toml + conftest.py**

파일: `pyproject.toml` (신규)
```toml
[project]
name = "ai-config-sync"
version = "0.1.0"
requires-python = ">=3.10"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]

[dependency-groups]
dev = ["pytest>=8.0", "pytest-cov>=5.0"]
```

파일: `tests/conftest.py` (신규) — sync_env fixture (tmp_path 기반), mock_git fixture (monkeypatch git_cmd/git_bytes)

done-when: `uv sync --group dev && uv run python -m pytest --co -q` 에러 없이 실행

**1-2. REPO-001: __pycache__ 추적 제거**
```bash
git rm -r --cached claude-code/skills/agent-create/scripts/__pycache__/
git rm -r --cached claude-code/skills/skill-create/scripts/__pycache__/
git rm -r --cached claude-code/skills/pptx/scripts/office/__pycache__/
git rm -r --cached openclaw/workspace/skills/skill-create/scripts/__pycache__/
git rm -r --cached openclaw/workspace/skills/agent-create/scripts/__pycache__/
```
done-when: `git ls-files '*.pyc'` 빈 출력

**1-3. CODE-007: 타입 어노테이션**

sync-timestamps.py 1행에 `from __future__ import annotations` 추가. 17개 함수에 타입 어노테이션 추가:
```python
def git_cmd(args: list[str], cwd: Path | str) -> tuple[str, int]: ...
def git_bytes(args: list[str], cwd: Path | str) -> tuple[bytes, int]: ...
def walk_files(base: Path, section: str) -> dict[str, float]: ...
def walk_all_files(base: Path) -> set[str]: ...
# (나머지는 arch-spec CODE-007 참조)
```
done-when: `uv run python -c "import sync_timestamps"` 성공

---

### Phase 2: 검증 함수 + 단위 테스트 (2-1~2-6 병렬, 2-7은 후속)

**2-1. SEC-001: validate_hostname()**
```python
import re
_HOSTNAME_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$")

def validate_hostname(hostname: str) -> str:
    if not _HOSTNAME_RE.match(hostname):
        print(f"  [ERROR] 유효하지 않은 hostname: {hostname!r}", file=sys.stderr)
        sys.exit(2)
    return hostname
```

**2-2. SEC-002: validate_filepath()**
```python
def validate_filepath(filepath: str, section: str) -> bool:
    if "\x00" in filepath:
        return False
    if filepath.startswith("/") or filepath.startswith("\\"):
        return False
    try:
        normalized = Path(filepath).as_posix()
    except ValueError:
        return False
    if ".." in normalized.split("/"):
        return False
    return True
```

**2-3. SEC-004: validate_timestamp()**
```python
import time
_MAX_FUTURE_DRIFT_SECONDS = 86400

def validate_timestamp(value: object, filepath: str) -> float | None:
    if not isinstance(value, (int, float)):
        return None
    ts = float(value)
    if ts < 0 or ts > time.time() + _MAX_FUTURE_DRIFT_SECONDS:
        return None
    return ts
```

**2-4. CODE-002: parse_args()**
```python
def parse_args() -> tuple[Path, str]:
    if len(sys.argv) >= 2 and sys.argv[1] == "--list-includes":
        print_includes()
        sys.exit(0)
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <sync_dir> <hostname>", file=sys.stderr)
        sys.exit(2)
    sync_dir = Path(sys.argv[1]).expanduser().resolve()
    hostname = validate_hostname(sys.argv[2])
    if not sync_dir.is_dir():
        print(f"  [ERROR] sync_dir이 존재하지 않음: {sync_dir}", file=sys.stderr)
        sys.exit(2)
    return sync_dir, hostname
```
main() L127-128을 `sync_dir, hostname = parse_args()`로 교체.

**2-5. CODE-001: bare except 제거**
- mtime() L73: `except:` → `except OSError:`
- peer JSON L160: `except Exception:` → `except (json.JSONDecodeError, KeyError) as e:` + `print(f"  [WARN] 피어 {peer} 파싱 실패: {e}", file=sys.stderr)`

**2-6. CODE-004: unlink_if_file 로깅**
```python
except OSError as e:
    print(f"  [WARN] 삭제 실패: {path} ({e})", file=sys.stderr)
```

**2-7. TEST-001b: 단위 테스트 36개**

| 대상 | 파일 | 테스트 수 |
|------|------|----------|
| should_include | test_should_include.py | 12 |
| migrate_ts_keys | test_migrate_ts_keys.py | 4 |
| validate_hostname | test_validation.py | 5 |
| validate_filepath | test_validation.py | 5 |
| validate_timestamp | test_validation.py | 5 |
| walk_files | test_walk_files.py | 3 |
| mtime | test_helpers.py | 2 |

done-when: `uv run python -m pytest tests/ -q` 36개 이상 통과

---

### Phase 3: main() 분리 — 전제: Phase 2 테스트 36개 전체 통과

**3-1. CODE-005: 4개 함수 추출**

```python
def load_timestamps(ts_dir: Path, hostname: str) -> dict[str, dict[str, float]]:
    """로컬 타임스탬프 파일 로드 + 키 마이그레이션."""
    # 현재 L136-141 이동

def load_peer_timestamps(sync_dir: Path, hostname: str) -> dict[str, dict[str, dict[str, float]]]:
    """FETCH_HEAD에서 피어 타임스탬프 로드."""
    # 현재 L143-166 이동. validate_timestamp 적용 (3-3).

def sync_section(
    section: str, local_dir: Path, repo_subdir: str, sync_dir: Path,
    our_section_ts: dict[str, float],
    peer_ts_all: dict[str, dict[str, dict[str, float]]],
) -> dict[str, float]:
    """단일 섹션 newest-wins 병합."""
    # 현재 L168-251 이동. validate_filepath 적용 (3-2).
    # Returns: 병합 후 타임스탬프 dict

def save_timestamps(ts_dir: Path, hostname: str, new_ts: dict[str, dict[str, float]]) -> None:
    """타임스탬프 JSON 저장."""
    # 현재 L253-260 이동
```

분리 후 main() (~25행):
```python
def main() -> None:
    sync_dir, hostname = parse_args()
    sections = {
        "workspace": (Path("~/.openclaw/workspace").expanduser(), "openclaw/workspace"),
        "claude-code": (Path("~/.claude").expanduser(), "claude-code"),
    }
    ts_dir = sync_dir / "timestamps"
    ts_dir.mkdir(exist_ok=True)
    our_ts = load_timestamps(ts_dir, hostname)
    peer_ts_all = load_peer_timestamps(sync_dir, hostname)
    new_ts: dict[str, dict[str, float]] = {}
    for section, (local_dir, repo_subdir) in sections.items():
        if not local_dir.exists():
            continue
        new_ts[section] = sync_section(
            section, local_dir, repo_subdir, sync_dir,
            our_ts.get(section, {}), peer_ts_all,
        )
    save_timestamps(ts_dir, hostname, new_ts)
```

done-when: Phase 2 테스트 36개 통과 + `python3 sync-timestamps.py . $(hostname -s)` 정상

**3-2. SEC-002 적용**: sync_section() 내 `for filepath` 루프 진입 시 `if not validate_filepath(filepath, section): continue`

**3-3. SEC-004 적용**: load_peer_timestamps() 내 피어 JSON 파싱 후 `validate_timestamp()` 호출, None이면 엔트리 무시

**3-4. TEST-001c: 통합 테스트 19개**

| 대상 | 파일 | 테스트 수 |
|------|------|----------|
| sync_section | test_sync_section.py | 8 (peer>local, local>peer, 동일, 삭제전파, 신규, 제외파일, 트래버설차단, 미래TS) |
| load_peer_timestamps | test_load_timestamps.py | 4 (정상, 빈 출력, 파싱 실패, 자기 제외) |
| prune_empty_dirs | test_helpers.py | 3 (빈, 비어있지않음, 중첩) |
| unlink_if_file | test_helpers.py | 4 (파일, 심링크, 디렉토리, 미존재) |

done-when: `uv run python -m pytest tests/ -q` 55개 이상 통과

---

### Phase 4: Bash 스크립트 수정 (4-1→4-2 순차, 4-3~4-6 병렬)

**4-1. ARCH-001a: --list-includes 서브커맨드**
```python
def print_includes() -> None:
    print(" ".join(sorted(CLAUDE_INCLUDES)))
```
parse_args()에 이미 분기 포함 (2-4에서 추가).

**4-2. ARCH-001b: setup.sh, setup-windows.sh 동적 참조**
```bash
CLAUDE_ITEMS=$($PYTHON_CMD "$SCRIPT_DIR/sync-timestamps.py" --list-includes 2>/dev/null)
if [ -z "$CLAUDE_ITEMS" ]; then
    CLAUDE_ITEMS="CLAUDE.md agents agent-memory memory plugins settings.json skills stop-hook-git-check.sh teams todos"
fi
for item in $CLAUDE_ITEMS; do
```

**4-3. CODE-003: sync.sh push 에러 핸들링**
```bash
if ! git push origin main; then
    echo "  -> Push conflict, rebasing..."
    if ! git pull --rebase origin main; then
        echo "  [WARN] Rebase conflict. Aborting rebase."
        git rebase --abort
        echo "  [WARN] 수동 해결 필요. 다음 실행에서 재시도합니다."
    else
        if ! git push origin main; then
            echo "  [WARN] Push 재시도 실패. 다음 실행에서 재시도합니다."
        else
            echo "  Push OK (after rebase)"
        fi
    fi
fi
```

**4-4. SEC-003: 로그 경로**
setup.sh, setup-windows.sh: `/tmp/ai-config-sync.log` → `$HOME/.local/share/ai-config-sync/sync.log` + `chmod 700`

**4-5. SEC-005: 토큰 umask**
setup.sh, setup-mac.sh: `(umask 077 && sed ...)` 서브셸

**4-6. CODE-006: setup-mac.sh deprecated**
```bash
echo "DEPRECATED: 'bash setup.sh'를 사용하세요."
exec bash "$(dirname "$0")/setup.sh"
```

---

### Phase 5: CI + 최종 검증

**5-1. REPO-002: GitHub Actions**
```yaml
name: test
on:
  push:
    branches: [main]
    paths: ["sync-timestamps.py", "tests/**", "pyproject.toml"]
  pull_request:
    branches: [main]
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --group dev
      - run: uv run python -m pytest tests/ -q --cov --cov-report=term-missing --cov-fail-under=80
```

**5-2. 최종 검증**
done-when: `uv run python -m pytest tests/ -q --cov --cov-fail-under=80` exit code 0, 55개+ 테스트, 80%+ 커버리지

---

## 롤백 계획

| Phase | 트리거 | 방법 |
|-------|--------|------|
| Phase 2 (parse_args) | 인수 처리 오류 | git revert 단일 커밋 |
| Phase 3 (main 분리) | 테스트 실패 | Phase 3 커밋 전체 git revert |
| Phase 3 (push 후 타 기기) | 타 기기 sync 에러 | git revert push. pull-only 기기 자동 적용 |
| Phase 4 (push 핸들링) | rebase --abort 오작동 | git revert 단일 커밋 |

---

## 제약 조건

1. 3개 플랫폼 크론 30분 실행 중 — 스크립트 오류 시 동기화 중단
2. 외부 의존성 금지 (표준 라이브러리만, dev dependency 허용)
3. timestamps/*.json 구조 변경 없음
4. sync.sh git pull로 코드 변경 자동 반영 — 오류 코드 push 시 전 기기 전파
5. Python 3.10+ 필수
6. git add 경로 제한: `openclaw/workspace claude-code timestamps state`만. 신규 파일(tests/, .github/) 별도 커밋

---

## 의사결정

| 결정 | 채택 | 기각 (사유) |
|------|------|-----------|
| CLAUDE_INCLUDES 단일소스화 | --list-includes 서브커맨드 (4.45) | sync-config.json (Bash에서 jq 필요, 외부 의존성 위반), Python eval (보안/유지보수 리스크) |
| main() 분리 | 4개 함수 추출 (동일 파일 내) | 클래스 (메서드 2개 이하 금지), 별도 모듈 (1곳 호출 금지) |
| 테스트 Mock 전략 | git_cmd/git_bytes monkeypatch | subprocess.run 직접 Mock (래퍼 존재 시 불안정) |
| CI 트리거 | paths 필터 (sync 데이터 변경 시 미트리거) | 전체 트리거 (30분 sync 커밋이 CI 과부하) |
