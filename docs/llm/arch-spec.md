# Architecture Spec: ai-config-sync P0+P1+P2 개선

date: 2026-03-25
status: DRAFT
scope: audit-report P0(4건) + P1(5건) + P2(7건) = 16건

---

## 목적

audit-report에서 식별된 16건의 개선 사항을 구현하여 합성 점수를 5.045에서 8.0 이상으로 끌어올린다.
완료 조건: `uv run python -m pytest tests/ -q` 전체 통과 + 커버리지 80% 이상 + GitHub Actions CI green.

---

## 결정 1: ARCH-001 CLAUDE_INCLUDES 단일 소스화

### Trade-Off 분석

| Criterion (weight) | Option A: sync-config.json | Option B: Python export + Bash 동적 참조 | Option C: Python으로 includes 목록 출력하는 헬퍼 커맨드 |
|---|---|---|---|
| Complexity (20%) | 3 -- JSON 파싱을 Bash/Python 양쪽에서 수행 필요. Bash에서 jq 또는 python -c 호출 추가 | 2 -- import 시 Python 모듈화 필요, Bash에서 eval $(python ...) 패턴은 취약점 | 4 -- Python에 서브커맨드 1개 추가, Bash에서 $() 캡처만 |
| Performance (25%) | 3 -- 매 실행마다 JSON 파일 읽기 추가 I/O | 3 -- Python 프로세스 기동 필요 | 4 -- 한 번의 Python 호출로 목록 출력, sync.sh에선 이미 Python 호출 중 |
| Maintainability (25%) | 4 -- 설정 파일이 단일 소스. 그러나 JSON 스키마가 없어 오타 시 런타임 실패 | 2 -- Python import 경로 관리, Bash eval 패턴 유지보수 어려움 | 5 -- CLAUDE_INCLUDES가 sync-timestamps.py 한 곳에만 존재. Bash는 출력값만 사용 |
| Time-to-implement (15%) | 3 -- sync-config.json 생성 + Python 파싱 + Bash 파싱 + 3개 setup 스크립트 수정 | 2 -- 모듈 구조 변경 + eval 패턴 + 테스트 | 5 -- 서브커맨드 1개 + Bash 변수 치환 1줄 |
| Durability (15%) | 4 -- JSON 포맷은 안정적이나 스키마 검증이 없으면 런타임 오류 | 2 -- Python 버전/모듈 경로에 의존 | 4 -- Python CLI 인터페이스는 안정적 |
| **Weighted total** | **3.45** | **2.30** | **4.45** |

### 채택: Option C (Python 헬퍼 커맨드)

sync-timestamps.py에 `--list-includes` 서브커맨드를 추가한다. Bash 스크립트(setup.sh, setup-windows.sh)는 하드코딩 목록 대신 `$($PYTHON_CMD sync-timestamps.py --list-includes)` 출력을 사용한다.

기각 사유:
- Option A: Bash에서 JSON 파싱이 jq 의존성 또는 python -c 호출을 강제. 외부 의존성 금지 제약 위반(jq) 또는 이중 Python 호출.
- Option B: eval 패턴은 보안/유지보수 리스크. 모듈 구조 변경 범위가 과대.

### 구현 사양

sync-timestamps.py에 추가:
```python
def print_includes() -> None:
    """CLAUDE_INCLUDES 목록을 공백 구분으로 stdout 출력"""
    print(" ".join(sorted(CLAUDE_INCLUDES)))
```

main() 진입점 분기:
```python
if len(sys.argv) == 2 and sys.argv[1] == "--list-includes":
    print_includes()
    sys.exit(0)
```

setup.sh:75, setup-windows.sh:17 변경:
```bash
# 변경 전
for item in CLAUDE.md settings.json agents plugins skills agent-memory memory todos teams stop-hook-git-check.sh; do
# 변경 후
CLAUDE_ITEMS=$($PYTHON_CMD "$SCRIPT_DIR/sync-timestamps.py" --list-includes)
for item in $CLAUDE_ITEMS; do
```

setup-windows.sh는 `PYTHON_CMD="python"` 변수 추가 필요 (sync.sh의 플랫폼별 분기와 동일 패턴).

---

## 결정 2: CODE-005 main() 분리

### 현재 main() 구조 분석 (L126-264, 139행)

| 행 범위 | 책임 | 분리 대상 함수 |
|---------|------|---------------|
| L127-128 | argv 파싱 + 검증 | main() 유지 (진입점) |
| L130-134 | sections 정의 | main() 유지 (설정) |
| L136-141 | 로컬 타임스탬프 로드 | `load_timestamps()` |
| L143-166 | 피어 타임스탬프 로드 | `load_peer_timestamps()` |
| L168-251 | 섹션별 newest-wins 병합 | `sync_section()` |
| L253-260 | 타임스탬프 저장 | `save_timestamps()` |

### 함수 시그니처

```python
def load_timestamps(ts_dir: Path, hostname: str) -> dict[str, dict[str, float]]:
    """로컬 타임스탬프 파일 로드 + 키 마이그레이션.

    Args:
        ts_dir: timestamps/ 디렉토리 경로
        hostname: 현재 호스트명
    Returns:
        섹션별 타임스탬프 dict. 예: {"workspace": {"file.md": 1711234567.0}, ...}
    """

def load_peer_timestamps(
    sync_dir: Path, hostname: str
) -> dict[str, dict[str, dict[str, float]]]:
    """FETCH_HEAD에서 피어 타임스탬프 로드.

    Args:
        sync_dir: 동기화 루트 디렉토리
        hostname: 현재 호스트명 (자기 자신 제외용)
    Returns:
        {peer_name: {section: {filepath: timestamp}}} 3중 dict
    """

def sync_section(
    section: str,
    local_dir: Path,
    repo_subdir: str,
    sync_dir: Path,
    our_section_ts: dict[str, float],
    peer_ts_all: dict[str, dict[str, dict[str, float]]],
) -> dict[str, float]:
    """단일 섹션의 newest-wins 병합 수행.

    Args:
        section: 섹션 키 ("workspace" | "claude-code")
        local_dir: 로컬 디렉토리 경로 (~/.openclaw/workspace 등)
        repo_subdir: repo 내 하위 경로 ("openclaw/workspace" 등)
        sync_dir: 동기화 루트 디렉토리
        our_section_ts: 이 섹션의 기존 타임스탬프
        peer_ts_all: 전체 피어 타임스탬프 (load_peer_timestamps 반환값)
    Returns:
        병합 후 이 섹션의 새 타임스탬프 dict {filepath: mtime}
    """

def save_timestamps(
    ts_dir: Path, hostname: str, new_ts: dict[str, dict[str, float]]
) -> None:
    """타임스탬프 JSON 저장.

    Args:
        ts_dir: timestamps/ 디렉토리 경로
        hostname: 현재 호스트명
        new_ts: 저장할 타임스탬프 dict
    """
```

### 데이터 흐름

```
main()
  |
  +-- parse_args() --> sync_dir, hostname  [인수 검증 포함]
  |
  +-- load_timestamps(ts_dir, hostname) --> our_ts
  |
  +-- load_peer_timestamps(sync_dir, hostname) --> peer_ts_all
  |
  +-- for section in sections:
  |     sync_section(..., our_ts[section], peer_ts_all) --> new_section_ts
  |     new_ts[section] = new_section_ts
  |
  +-- save_timestamps(ts_dir, hostname, new_ts)
```

### 분리 후 main() (약 25행)

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

---

## 결정 3: 테스트 인프라 설계 (TEST-001 + REPO-002)

### pyproject.toml

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

외부 의존성 금지 제약은 런타임에 적용. 테스트 의존성(dev dependency-group)은 허용.

### 디렉토리 구조

```
tests/
  conftest.py          # 공통 fixtures (tmp_path 기반 sync_dir, mock git)
  test_should_include.py    # should_include() 경계값 테스트
  test_migrate_ts_keys.py   # 키 마이그레이션 테스트
  test_walk_files.py         # walk_files, walk_all_files 테스트
  test_load_timestamps.py    # load_timestamps, load_peer_timestamps 테스트
  test_sync_section.py       # newest-wins 병합 로직 통합 테스트
  test_save_timestamps.py    # 타임스탬프 저장 테스트
  test_validation.py         # SEC-001~004 입력 검증 테스트
  test_helpers.py            # mtime, unlink_if_file, prune_empty_dirs 테스트
```

### Mock 전략

**원칙**: git subprocess는 Mock한다. 파일시스템은 `tmp_path`로 실제 I/O.

```python
# conftest.py 핵심 fixtures

@pytest.fixture
def sync_env(tmp_path: Path) -> dict:
    """동기화 환경을 tmp_path에 구성.
    Returns:
        {"sync_dir": Path, "local_workspace": Path, "local_claude": Path,
         "ts_dir": Path, "hostname": str}
    """
    sync_dir = tmp_path / "repo"
    sync_dir.mkdir()
    (sync_dir / "timestamps").mkdir()
    (sync_dir / "openclaw" / "workspace").mkdir(parents=True)
    (sync_dir / "claude-code").mkdir()
    local_ws = tmp_path / "local_workspace"
    local_ws.mkdir()
    local_claude = tmp_path / "local_claude"
    local_claude.mkdir()
    return {
        "sync_dir": sync_dir,
        "local_workspace": local_ws,
        "local_claude": local_claude,
        "ts_dir": sync_dir / "timestamps",
        "hostname": "test-host",
    }


@pytest.fixture
def mock_git(monkeypatch):
    """git_cmd와 git_bytes를 교체 가능한 Mock으로 제공.
    Usage:
        mock_git.set_ls_tree("timestamps/peer1.json")
        mock_git.set_show("FETCH_HEAD:timestamps/peer1.json", '{"workspace": {}}')
    """
    # unittest.mock.patch로 git_cmd, git_bytes를 모듈 레벨에서 교체
    # 반환값을 테스트별로 설정할 수 있는 헬퍼 객체 반환
```

**git_cmd/git_bytes Mock 상세**:
- `monkeypatch.setattr("sync_timestamps.git_cmd", mock_fn)` 패턴 사용
- subprocess.run을 직접 Mock하지 않는다 (git_cmd/git_bytes가 이미 래퍼 역할)
- 테스트별로 FETCH_HEAD ls-tree 출력과 git show 출력을 미리 정의

**파일시스템은 Mock하지 않는다**:
- `tmp_path`에 실제 파일 생성/삭제하여 walk_files, mtime, shutil.copy2 등을 실물 테스트
- Windows 경로 호환 검증은 CI의 os matrix에서 수행

### 테스트 우선순위 (audit-report 기준)

| 순위 | 테스트 대상 | 테스트 수(최소) | 근거 |
|------|-----------|---------------|------|
| 1 | should_include() | 12 | 화이트리스트+제외 패턴 경계값, 트래버설 차단 검증 |
| 2 | migrate_ts_keys() | 4 | 키 존재/미존재/충돌/빈 dict |
| 3 | newest-wins 비교 (sync_section) | 8 | peer>local, local>peer, 동일, 삭제전파, 신규파일 |
| 4 | 입력 검증 (parse_args, validate_hostname) | 6 | SEC-001, CODE-002 |
| 5 | 경로 경계 검증 | 5 | SEC-002 디렉토리 트래버설 |
| 6 | 타임스탬프 검증 | 4 | SEC-004 타입/범위/미래값 |
| 7 | load_peer_timestamps | 4 | 정상/빈 출력/파싱 실패/자기 자신 제외 |
| 8 | prune_empty_dirs | 3 | 빈 디렉토리/비어있지 않은/중첩 |
| 9 | unlink_if_file | 4 | 파일/심볼릭링크/디렉토리/존재하지 않음 + 로깅 |
| 10 | mtime | 3 | 존재/미존재/권한 없음 |

최소 테스트 수: 53개. 목표 커버리지: 80% 이상.

### CI/CD (GitHub Actions)

```yaml
# .github/workflows/test.yml
name: test
on:
  push:
    branches: [main]
    paths:
      - "sync-timestamps.py"
      - "tests/**"
      - "pyproject.toml"
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

paths 필터로 sync 데이터(openclaw/, claude-code/, timestamps/, state/) 변경 시 CI가 트리거되지 않도록 한다. 30분마다의 자동 sync 커밋이 CI를 발동시키지 않아야 한다.

---

## 결정 4: 보안 강화 (SEC-001~005) 상세 설계

### SEC-001: hostname 검증

```python
import re

_HOSTNAME_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$")

def validate_hostname(hostname: str) -> str:
    """hostname 검증. RFC 952/1123 준수.

    Returns: 검증된 hostname
    Raises: SystemExit(2) 비유효 시
    """
    if not _HOSTNAME_RE.match(hostname):
        print(f"  [ERROR] 유효하지 않은 hostname: {hostname!r}", file=sys.stderr)
        sys.exit(2)
    return hostname
```

### SEC-002: 경로 트래버설 차단

```python
def validate_filepath(filepath: str, section: str) -> bool:
    """피어 파일 경로가 섹션 경계를 벗어나지 않는지 검증.

    차단 조건:
    - ".." 포함
    - 절대 경로 (/ 시작)
    - null byte 포함
    Returns: True(안전) / False(차단)
    """
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

적용 위치: sync_section() 내 `for filepath in sorted(all_files)` 루프 진입 시.
피어 타임스탬프에서 온 filepath와 로컬 walk_files에서 온 filepath 모두 검증.

### SEC-003: 크론 로그 위치/권한

setup.sh:56 변경:
```bash
# 변경 전
CRON_CMD="*/30 * * * * cd $SCRIPT_DIR && bash sync.sh >> /tmp/ai-config-sync.log 2>&1"
# 변경 후
LOG_DIR="$HOME/.local/share/ai-config-sync"
mkdir -p "$LOG_DIR"
chmod 700 "$LOG_DIR"
CRON_CMD="*/30 * * * * cd $SCRIPT_DIR && bash sync.sh >> $LOG_DIR/sync.log 2>&1"
```

setup-windows.sh:33 (Windows는 /tmp가 사용자 전용이므로 경로만 통일):
```bash
LOG_DIR="$HOME/.local/share/ai-config-sync"
mkdir -p "$LOG_DIR"
```

### SEC-004: 타임스탬프 데이터 검증

```python
import time

_MAX_FUTURE_DRIFT_SECONDS = 86400  # 24시간

def validate_timestamp(value: object, filepath: str) -> float | None:
    """타임스탬프 값 검증.

    Returns: 유효한 float timestamp, 또는 None (무시)
    """
    if not isinstance(value, (int, float)):
        return None
    ts = float(value)
    if ts < 0:
        return None
    if ts > time.time() + _MAX_FUTURE_DRIFT_SECONDS:
        return None
    return ts
```

적용 위치: load_peer_timestamps()에서 피어 JSON 파싱 직후, 각 타임스탬프 값에 대해 호출.

### SEC-005: 토큰 임시 파일 권한

setup.sh:111-114, setup-mac.sh:31-35 변경:
```bash
# 변경 전
sed "s|...|...|g" "$TEMPLATE" > "$CONFIG_FILE.tmp"
NEW_TOKEN=$(openssl rand -hex 24)
sed "s|...|...|g" "$CONFIG_FILE.tmp" > "$CONFIG_FILE"
rm "$CONFIG_FILE.tmp"

# 변경 후
(umask 077 && sed "s|...|...|g" "$TEMPLATE" > "$CONFIG_FILE.tmp")
NEW_TOKEN=$(openssl rand -hex 24)
(umask 077 && sed "s|...|...|g" "$CONFIG_FILE.tmp" > "$CONFIG_FILE")
rm -f "$CONFIG_FILE.tmp"
```

서브셸 `(umask 077 && ...)` 으로 임시 파일이 소유자만 읽기/쓰기 가능하도록 보장.

---

## 결정 5: 코드 품질 개선 (CODE-001~004, 006~007) 상세 설계

### CODE-001: bare except 제거

| 위치 | 현재 | 변경 |
|------|------|------|
| L73 (mtime) | `except:` | `except OSError:` |
| L160 (peer JSON 파싱) | `except Exception:` | `except (json.JSONDecodeError, KeyError):` + 로그 |

### CODE-002: sys.argv 인덱스 범위 검사

```python
def parse_args() -> tuple[Path, str]:
    """sys.argv 파싱 + 검증.

    Returns: (sync_dir, hostname)
    Raises: SystemExit(2) 인수 부족 또는 유효하지 않은 값
    """
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

### CODE-003: sync.sh push 에러 핸들링

```bash
# 변경 전 (L131-135)
if ! git push origin main 2>/dev/null; then
    echo "  -> Push conflict, rebasing..."
    git pull --rebase origin main
    git push origin main
fi

# 변경 후
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

핵심 변경:
1. `2>/dev/null` 제거 -- stderr 출력을 로그에 보존
2. rebase 실패 시 `git rebase --abort`로 dirty state 방지
3. 2차 push 실패도 처리 (silent abort 제거)

### CODE-004: unlink 삭제 실패 로깅

```python
def unlink_if_file(path: Path) -> None:
    """파일/심볼릭링크만 삭제 (디렉토리는 건너뜀)"""
    try:
        if path.is_file() or path.is_symlink():
            path.unlink()
    except OSError as e:
        print(f"  [WARN] 삭제 실패: {path} ({e})", file=sys.stderr)
```

### CODE-006: openclaw.json 생성 로직 통합

setup-mac.sh의 openclaw.json 생성 로직(L23-41)을 setup.sh의 패턴과 동일하게 통합.
setup-mac.sh를 deprecated로 표기하고, setup.sh가 모든 플랫폼(macOS/Linux)을 커버.

구체적으로:
- setup-mac.sh 상단에 `echo "DEPRECATED: 'bash setup.sh'를 사용하세요."` 추가 후 `exec bash "$(dirname "$0")/setup.sh"` 로 리다이렉트
- setup.sh에 setup-mac.sh 고유 기능(OpenClaw CLI 설치, gateway 시작) 통합 여부는 별도 결정. 현재 scope에서는 openclaw.json 생성 로직만 단일화.

### CODE-007: 타입 어노테이션 추가

대상 함수와 시그니처:

```python
def migrate_ts_keys(ts: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]: ...
def should_include(filepath: str, section: str) -> bool: ...
def git_cmd(args: list[str], cwd: Path | str) -> tuple[str, int]: ...
def git_bytes(args: list[str], cwd: Path | str) -> tuple[bytes, int]: ...
def mtime(p: Path) -> float: ...
def walk_files(base: Path, section: str) -> dict[str, float]: ...
def walk_all_files(base: Path) -> set[str]: ...
def unlink_if_file(path: Path) -> None: ...
def prune_empty_dirs(base: Path) -> None: ...
def print_includes() -> None: ...
def validate_hostname(hostname: str) -> str: ...
def validate_filepath(filepath: str, section: str) -> bool: ...
def validate_timestamp(value: object, filepath: str) -> float | None: ...
def parse_args() -> tuple[Path, str]: ...
def load_timestamps(ts_dir: Path, hostname: str) -> dict[str, dict[str, float]]: ...
def load_peer_timestamps(sync_dir: Path, hostname: str) -> dict[str, dict[str, dict[str, float]]]: ...
def sync_section(section: str, local_dir: Path, repo_subdir: str, sync_dir: Path, our_section_ts: dict[str, float], peer_ts_all: dict[str, dict[str, dict[str, float]]]) -> dict[str, float]: ...
def save_timestamps(ts_dir: Path, hostname: str, new_ts: dict[str, dict[str, float]]) -> None: ...
```

`from __future__ import annotations` 추가하여 Python 3.10 호환성 확보.

---

## 결정 6: Repo Health (REPO-001, REPO-002)

### REPO-001: __pycache__ 추적 제거

현재 .gitignore에 `__pycache__/`과 `*.pyc`가 이미 있으나, 과거 커밋에서 추적이 시작된 14개 파일이 남아 있음.

```bash
git rm -r --cached claude-code/skills/agent-create/scripts/__pycache__/
git rm -r --cached claude-code/skills/skill-create/scripts/__pycache__/
git rm -r --cached claude-code/skills/pptx/scripts/office/__pycache__/
git rm -r --cached openclaw/workspace/skills/skill-create/scripts/__pycache__/
git rm -r --cached openclaw/workspace/skills/agent-create/scripts/__pycache__/
```

이 파일들은 sync.sh의 `git add -A openclaw/workspace claude-code timestamps state` 경로에 포함되므로, 제거하지 않으면 다음 sync에서 다시 추적됨. `git rm --cached` 후 .gitignore가 방어.

### REPO-002: CI/CD

결정 3에서 상세 기술 완료. `.github/workflows/test.yml`.

---

## 파일 변경 목록

| 파일 | 작업 | 관련 ID |
|------|------|---------|
| sync-timestamps.py | 대규모 수정: main() 분리, 검증 함수 추가, bare except 수정, 타입 어노테이션, --list-includes | CODE-001~002,005,007, SEC-001~002,004, ARCH-001 |
| sync.sh | 수정: push 에러 핸들링 | CODE-003 |
| setup.sh | 수정: CLAUDE_INCLUDES 동적 참조, 로그 경로, 토큰 umask | ARCH-001, SEC-003, SEC-005 |
| setup-windows.sh | 수정: CLAUDE_INCLUDES 동적 참조, 로그 경로 | ARCH-001, SEC-003 |
| setup-mac.sh | 수정: deprecated 리다이렉트, 토큰 umask | CODE-006, SEC-005 |
| pyproject.toml | 신규 | TEST-001 |
| tests/conftest.py | 신규 | TEST-001 |
| tests/test_should_include.py | 신규 | TEST-001 |
| tests/test_migrate_ts_keys.py | 신규 | TEST-001 |
| tests/test_walk_files.py | 신규 | TEST-001 |
| tests/test_load_timestamps.py | 신규 | TEST-001 |
| tests/test_sync_section.py | 신규 | TEST-001 |
| tests/test_save_timestamps.py | 신규 | TEST-001 |
| tests/test_validation.py | 신규 | TEST-001, SEC-001~004 |
| tests/test_helpers.py | 신규 | TEST-001, CODE-004 |
| .github/workflows/test.yml | 신규 | REPO-002 |

---

## 구현 순서

의존관계 기반으로 정렬. 각 단계는 독립 커밋 가능 단위.

### Phase 1: 인프라 + 무파괴 변경 (의존성 없음)

| 순서 | ID | 작업 | 리스크 |
|------|-----|------|--------|
| 1-1 | TEST-001a | pyproject.toml 생성 + tests/conftest.py 작성 | 없음 (기존 코드 미변경) |
| 1-2 | REPO-001 | __pycache__ git rm --cached | 없음 (런타임 무관) |
| 1-3 | CODE-007 | `from __future__ import annotations` + 타입 어노테이션 추가 | 낮음 (런타임 영향 없음, Python 3.10+) |

### Phase 2: 검증 함수 추가 (기존 로직 미변경)

| 순서 | ID | 작업 | 리스크 |
|------|-----|------|--------|
| 2-1 | SEC-001 | validate_hostname() 추가 + parse_args() 추가 | 낮음 (새 함수 추가만, 아직 main()에서 미호출) |
| 2-2 | SEC-002 | validate_filepath() 추가 | 낮음 (새 함수 추가만) |
| 2-3 | SEC-004 | validate_timestamp() 추가 | 낮음 (새 함수 추가만) |
| 2-4 | CODE-002 | main()에서 sys.argv 직접 접근을 parse_args() 호출로 교체 | 중간 (main 진입점 변경) |
| 2-5 | CODE-001 | bare except를 구체적 예외로 교체 | 낮음 (동작 변경 최소) |
| 2-6 | CODE-004 | unlink_if_file에 에러 로깅 추가 | 낮음 |
| 2-7 | TEST-001b | 단위 테스트 작성: should_include 12개, migrate_ts_keys 4개, validate_hostname 5개, validate_filepath 5개, validate_timestamp 5개, walk_files 3개, mtime 2개. 총 36개. done-when: `uv run python -m pytest tests/ -q` 전체 통과 | 없음 |

### Phase 3: 구조 리팩터링 (main 분리)

| 순서 | ID | 작업 | 리스크 |
|------|-----|------|--------|
| 3-1 | CODE-005 | load_timestamps, load_peer_timestamps, sync_section, save_timestamps 추출 | 높음 (핵심 로직 이동) |
| 3-2 | SEC-002 적용 | sync_section 내 validate_filepath 호출 삽입 | 중간 |
| 3-3 | SEC-004 적용 | load_peer_timestamps 내 validate_timestamp 호출 삽입 | 중간 |
| 3-4 | TEST-001c | sync_section, load_peer_timestamps 통합 테스트 작성 | 없음 |

### Phase 4: Bash 스크립트 수정

| 순서 | ID | 작업 | 리스크 |
|------|-----|------|--------|
| 4-1 | ARCH-001 | print_includes() + --list-includes 서브커맨드 추가 | 낮음 |
| 4-2 | ARCH-001 | setup.sh, setup-windows.sh에서 하드코딩 목록을 동적 참조로 교체 | 중간 (setup 스크립트는 초기 1회 실행이므로 실패 시 재실행 가능) |
| 4-3 | CODE-003 | sync.sh push 에러 핸들링 개선 | 중간 (실행 중인 크론에 영향) |
| 4-4 | SEC-003 | 크론 로그 경로 변경 (setup.sh, setup-windows.sh) | 낮음 (신규 설치만 해당, 기존 크론은 기존 경로 유지) |
| 4-5 | SEC-005 | umask 077 적용 (setup.sh, setup-mac.sh) | 낮음 |
| 4-6 | CODE-006 | setup-mac.sh deprecated 리다이렉트 | 낮음 |

### Phase 5: CI + 최종 검증

| 순서 | ID | 작업 | 리스크 |
|------|-----|------|--------|
| 5-1 | REPO-002 | .github/workflows/test.yml 생성 | 없음 |
| 5-2 | -- | 전체 테스트 실행 + 커버리지 확인 | 없음 |

### 롤백 계획

| Phase | 롤백 트리거 | 롤백 방법 |
|-------|-----------|----------|
| Phase 2 (2-4 parse_args) | sync-timestamps.py 인수 처리 오류 | `git revert` 단일 커밋. parse_args를 제거하고 원래 sys.argv 직접 접근으로 복원 |
| Phase 3 (3-1 main 분리) | Phase 2 테스트 36개 중 1개라도 실패 | Phase 3 커밋 전체 `git revert`. Phase 2 상태로 복원 |
| Phase 3 (push 후 타 기기 실패) | 타 기기에서 sync.sh 에러 발생 | `git revert` 커밋 push. pull-only 기기는 자동 적용 |
| Phase 4 (4-3 push 핸들링) | rebase --abort가 의도치 않게 실행 | `git revert` 단일 커밋 |

### 가정

1. 크론은 롤아웃 중에도 30분마다 계속 실행. 각 Phase 커밋+push 후 다음 크론에서 자동 반영.
2. 3개 기기 모두 Git SSH 접근 가능.
3. 동시 sync 실행은 기존 rebase 메커니즘으로 처리.
4. Python 3.10+ 이 3개 기기 모두에 설치.

---

## 영향 범위 분석

### 의존관계 그래프

```
CODE-007 (타입 어노테이션) ── 독립
REPO-001 (__pycache__) ── 독립
TEST-001a (인프라) ── 독립
   |
CODE-001 (bare except) ── 독립
CODE-004 (unlink 로깅) ── 독립
   |
SEC-001 + CODE-002 (parse_args) ── SEC-001은 CODE-002에 포함
SEC-002 (경로 검증) ── 독립
SEC-004 (타임스탬프 검증) ── 독립
   |
   v
CODE-005 (main 분리) ── SEC-001,002,004에 의존 (분리 시 검증 로직 삽입)
   |
   v
ARCH-001 (단일소스화) ── CODE-005에 의존 (--list-includes는 main 분기에 추가)
   |
   v
TEST-001b,c (테스트) ── CODE-005, SEC-* 에 의존
   |
   v
REPO-002 (CI) ── TEST-001에 의존
   |
CODE-003 (push 핸들링) ── 독립 (sync.sh만 수정)
SEC-003 (로그 경로) ── 독립 (setup 스크립트만 수정)
SEC-005 (umask) ── 독립 (setup 스크립트만 수정)
CODE-006 (setup 통합) ── 독립 (setup-mac.sh만 수정)
```

### 하위호환 리스크 분석

| 변경 | 리스크 등급 | 리스크 상세 | 완화 전략 |
|------|-----------|-----------|----------|
| CODE-005 main() 분리 | HIGH | 핵심 동기화 로직 이동. 버그 시 3개 플랫폼 동기화 중단 | Phase 3 전 Phase 2 테스트 완비. 분리 후 즉시 통합 테스트 실행 |
| CODE-002 parse_args | MEDIUM | argv 부족 시 기존에는 IndexError + traceback, 변경 후 깔끔한 exit(2). 동작 변경이나 정상 호출에는 영향 없음 | sync.sh가 항상 2개 인수 전달하므로 정상 경로 영향 없음 |
| SEC-002 경로 검증 | MEDIUM | 피어 타임스탬프에 잘못된 경로가 있었다면 기존에는 처리, 변경 후 무시. False positive 시 파일 미동기화 | validate_filepath 조건을 보수적으로 설정 (.., 절대경로, null byte만 차단) |
| SEC-004 타임스탬프 검증 | MEDIUM | 잘못된 타임스탬프 형식이 있었다면 기존에는 비교 실패/예외, 변경 후 무시 | 실 운영 timestamps/*.json 검사하여 기존 데이터에 문제 없음 확인 |
| ARCH-001 동적 참조 | LOW | setup 스크립트는 초기 1회 실행. Python 미설치 환경에서는 실패할 수 있으나, sync-timestamps.py 실행이 전제이므로 Python은 항상 존재 | --list-includes가 실패하면 fallback으로 하드코딩 목록 유지 (방어 코드) |
| CODE-003 push 핸들링 | LOW | rebase 실패 시 abort 후 다음 실행에서 재시도. 기존보다 안전 | 기존 silent failure보다 명시적 abort가 더 안전 |
| timestamps/*.json 구조 | NONE | 구조 변경 없음. 읽기 시 검증만 추가 | -- |

### ARCH-001 Bash fallback 방어 코드

```bash
CLAUDE_ITEMS=$($PYTHON_CMD "$SCRIPT_DIR/sync-timestamps.py" --list-includes 2>/dev/null)
if [ -z "$CLAUDE_ITEMS" ]; then
    # fallback: Python 실행 실패 시 하드코딩 (최후의 수단)
    CLAUDE_ITEMS="CLAUDE.md agents agent-memory memory plugins settings.json skills stop-hook-git-check.sh teams todos"
fi
```

---

## 제약 조건

1. sync-timestamps.py의 런타임 의존성은 표준 라이브러리만 허용. pytest/pytest-cov는 dev dependency-group에만 추가.
2. timestamps/*.json 구조(섹션별 {filepath: mtime} dict)는 변경하지 않는다.
3. Windows Git Bash에서 `python sync-timestamps.py --list-includes`가 동작해야 한다 (PYTHONUTF8=1 환경).
4. CI는 sync 데이터 경로 변경 시 트리거하지 않는다 (paths 필터 필수).
5. Phase 3(main 분리) 전에 기존 순수 함수 테스트가 통과해야 한다. 테스트 없는 리팩터링 금지.
6. `from __future__ import annotations`는 Python 3.7+에서 동작하나, 프로젝트는 Python 3.10+ 타겟 (pyproject.toml requires-python 기준).

---

## 의사결정 요약

| 결정 | 채택 | 기각 | 기각 사유 |
|------|------|------|----------|
| CLAUDE_INCLUDES 단일소스화 | Python 헬퍼 커맨드 (--list-includes) | sync-config.json | Bash JSON 파싱에 외부 의존성(jq) 필요 또는 이중 Python 호출 |
| CLAUDE_INCLUDES 단일소스화 | Python 헬퍼 커맨드 (--list-includes) | Python export + eval | eval 패턴 보안 리스크, 모듈 구조 변경 과대 |
| main() 분리 방식 | 4개 함수 추출 (load_ts, load_peer, sync_section, save_ts) | 클래스 기반 리팩터링 | 메서드 2개 이하 클래스 금지 규칙. 함수 호출 1곳이므로 클래스 불필요 |
| 테스트 프레임워크 | pytest + pytest-cov (dev dependency-group) | unittest | pytest의 tmp_path fixture, monkeypatch가 이 프로젝트의 Mock 전략에 적합 |
| Mock 대상 | git_cmd/git_bytes 함수 레벨 Mock | subprocess.run 직접 Mock | 래퍼 함수가 이미 존재하므로 상위 레벨 Mock이 더 안정적 |
| CI 트리거 | paths 필터 (sync-timestamps.py, tests/, pyproject.toml) | 모든 push | 30분마다 sync 커밋이 발생하므로 필터 없으면 CI 과부하 |
| setup-mac.sh 처리 | deprecated 리다이렉트 | 삭제 | 기존 사용자가 문서/히스토리에서 참조할 수 있음 |
