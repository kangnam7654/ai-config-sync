# Sync Engine 테스트 플랜

> 대상 설계문서: `test-design-doc.md` (Sync Engine 설계문서)
> 대상 프로젝트: `/Users/kangnam/projects/ai-config-sync`
> 작성일: 2026-03-23

---

## 1. 테스트 범위 요약

### 1.1 테스트 대상 컴포넌트

| 컴포넌트 | 파일 | 유형 | 우선순위 |
|---------|------|------|---------|
| `should_include()` | `sync-timestamps.py` | 순수 함수 (Unit) | P0 |
| `walk_files()` | `sync-timestamps.py` | 파일시스템 의존 (Unit) | P0 |
| `migrate_ts_keys()` | `sync-timestamps.py` | 순수 함수 (Unit) | P1 |
| `mtime()` | `sync-timestamps.py` | 파일시스템 의존 (Unit) | P2 |
| `walk_all_files()` | `sync-timestamps.py` | 파일시스템 의존 (Unit) | P1 |
| `unlink_if_file()` | `sync-timestamps.py` | 파일시스템 의존 (Unit) | P2 |
| `prune_empty_dirs()` | `sync-timestamps.py` | 파일시스템 의존 (Unit) | P2 |
| `git_cmd()` / `git_bytes()` | `sync-timestamps.py` | subprocess 래퍼 (Unit) | P2 |
| `main()` | `sync-timestamps.py` | 통합 로직 (Integration) | P0 |
| `sync.sh` | `sync.sh` | E2E 셸 스크립트 | P1 |
| `setup-mac.sh` | `setup-mac.sh` | 셋업 스크립트 (E2E) | P2 |
| `setup-windows.sh` | `setup-windows.sh` | 셋업 스크립트 (E2E) | P2 |

### 1.2 테스트 제외 대상

- 실제 Git remote 연동 (네트워크 의존)
- 실제 크론/Task Scheduler 등록 동작
- 실제 `openclaw`, `claude` CLI 바이너리 호출

---

## 2. Unit 테스트

### 2.1 `should_include(filepath, section)` -- P0

설계문서 명세: EXCLUDES 딕셔너리 패턴과 CLAUDE_INCLUDES 화이트리스트 기반으로 동기화 대상 여부를 판정한다.

#### 테스트 케이스

| ID | 시나리오 | 입력 | 기대 결과 |
|----|---------|------|----------|
| SI-01 | workspace 일반 파일 포함 | `("MEMORY.md", "workspace")` | `True` |
| SI-02 | workspace 제외 패턴 - glob | `("notion_data_20260101.json", "workspace")` | `False` |
| SI-03 | workspace 제외 패턴 - jsonl | `("data.jsonl", "workspace")` | `False` |
| SI-04 | workspace 제외 패턴 - .git | `(".git", "workspace")` 또는 경로에 `.git` 포함 | `False` |
| SI-05 | workspace 제외 - flutter 하위 | `("tools/flutter/config.json", "workspace")` | `False` |
| SI-06 | workspace 제외 - tmp 패턴 | `("tmp_abc.json", "workspace")` | `False` |
| SI-07 | claude-code 화이트리스트 포함 - settings.json | `("settings.json", "claude-code")` | `True` |
| SI-08 | claude-code 화이트리스트 포함 - CLAUDE.md | `("CLAUDE.md", "claude-code")` | `True` |
| SI-09 | claude-code 화이트리스트 포함 - agents 하위 | `("agents/my-agent.md", "claude-code")` | `True` |
| SI-10 | claude-code 화이트리스트 포함 - skills 하위 | `("skills/my-skill/config.json", "claude-code")` | `True` |
| SI-11 | claude-code 화이트리스트 미포함 | `("unknown-dir/file.txt", "claude-code")` | `False` |
| SI-12 | claude-code 제외 패턴 우선 - history.jsonl | `("history.jsonl", "claude-code")` | `False` (EXCLUDES가 먼저 체크됨) |
| SI-13 | claude-code 제외 - cache 디렉토리 | `("cache/data.bin", "claude-code")` | `False` |
| SI-14 | claude-code 제외 - backups 디렉토리 | `("backups/old.json", "claude-code")` | `False` |
| SI-15 | claude-code 제외 - telemetry | `("telemetry/events.log", "claude-code")` | `False` |
| SI-16 | 알 수 없는 section | `("file.txt", "unknown")` | `True` (EXCLUDES에 항목 없으므로) |
| SI-17 | 빈 filepath | `("", "claude-code")` | 동작 확인 (에러 없이 반환) |
| SI-18 | claude-code 화이트리스트 - memory 하위 | `("memory/MEMORY.md", "claude-code")` | `True` |
| SI-19 | claude-code 화이트리스트 - todos | `("todos/list.json", "claude-code")` | `True` |
| SI-20 | claude-code 화이트리스트 - teams | `("teams/team-config.json", "claude-code")` | `True` |

#### 엣지 케이스

| ID | 시나리오 | 입력 | 검증 포인트 |
|----|---------|------|-----------|
| SI-E01 | 경로 구분자 - Windows 스타일 | `("tools\\flutter\\config", "workspace")` | POSIX/Windows 경로 모두 처리 |
| SI-E02 | 중첩 제외 패턴 매칭 | `("tools/flutter/sub/deep/file.txt", "workspace")` | `tools/flutter/**` 패턴으로 제외 |
| SI-E03 | 제외 패턴과 화이트리스트 동시 해당 | `("cache", "claude-code")` | `False` (EXCLUDES 우선) |

### 2.2 `migrate_ts_keys(ts)` -- P1

설계문서 명세: 구 키 이름을 신 키 이름으로 자동 마이그레이션한다.

| ID | 시나리오 | 입력 | 기대 결과 |
|----|---------|------|----------|
| MK-01 | 구 키 마이그레이션 | `{"claude-config": {"file.txt": 123.0}}` | `{"claude-code": {"file.txt": 123.0}}` |
| MK-02 | 신 키 이미 존재 시 구 키 무시 | `{"claude-config": {"a": 1}, "claude-code": {"b": 2}}` | `{"claude-config": {"a": 1}, "claude-code": {"b": 2}}` (구 키 유지) |
| MK-03 | 마이그레이션 대상 없음 | `{"claude-code": {"file.txt": 123.0}}` | 그대로 반환 |
| MK-04 | 빈 딕셔너리 | `{}` | `{}` |
| MK-05 | 여러 섹션 혼합 | `{"workspace": {}, "claude-config": {"a": 1}}` | `{"workspace": {}, "claude-code": {"a": 1}}` |

### 2.3 `walk_files(base, section)` -- P0

설계문서 명세: 디렉토리 경로를 받아 `{상대경로: mtime}` 딕셔너리를 반환한다. `.git` 디렉토리는 항상 제외.

**Mock 전략**: 임시 디렉토리(`tmp_path` fixture)에 테스트 파일 구조를 생성하여 테스트한다.

| ID | 시나리오 | 테스트 셋업 | 기대 결과 |
|----|---------|-----------|----------|
| WF-01 | 일반 파일 수집 | `tmp/a.txt`, `tmp/b.md` 생성 | 두 파일 모두 포함, mtime > 0 |
| WF-02 | .git 디렉토리 제외 | `tmp/.git/config` 생성 | `.git/config` 미포함 |
| WF-03 | 하위 디렉토리 재귀 | `tmp/sub/deep/file.txt` 생성 | `sub/deep/file.txt` 포함 |
| WF-04 | EXCLUDES 패턴 적용 | `tmp/notion_data_123.json` 생성, section="workspace" | 해당 파일 미포함 |
| WF-05 | 존재하지 않는 디렉토리 | `Path("/nonexistent")` 전달 | 빈 딕셔너리 `{}` 반환 |
| WF-06 | 빈 디렉토리 | 빈 `tmp/` 생성 | 빈 딕셔너리 `{}` 반환 |
| WF-07 | claude-code 화이트리스트 적용 | `tmp/settings.json`, `tmp/random/x.txt` 생성, section="claude-code" | `settings.json`만 포함 |
| WF-08 | 상대 경로 형식 검증 | `tmp/sub/file.txt` | 키가 `sub/file.txt` (POSIX 형식, 선행 슬래시 없음) |

### 2.4 `walk_all_files(base)` -- P1

| ID | 시나리오 | 테스트 셋업 | 기대 결과 |
|----|---------|-----------|----------|
| WA-01 | 전체 파일 반환 | `tmp/a.txt`, `tmp/b/c.md` | `{"a.txt", "b/c.md"}` |
| WA-02 | .git 제외 | `tmp/.git/HEAD` 포함 | `.git/HEAD` 미포함 |
| WA-03 | 존재하지 않는 디렉토리 | 없는 경로 | 빈 set |

### 2.5 `mtime(path)` -- P2

| ID | 시나리오 | 입력 | 기대 결과 |
|----|---------|------|----------|
| MT-01 | 존재하는 파일 | 임시 파일 경로 | `> 0.0` |
| MT-02 | 존재하지 않는 파일 | 없는 경로 | `0.0` |
| MT-03 | 권한 없는 파일 | 읽기 권한 제거된 파일 | `0.0` (예외 처리) |

### 2.6 `unlink_if_file(path)` -- P2

| ID | 시나리오 | 입력 | 기대 결과 |
|----|---------|------|----------|
| UF-01 | 일반 파일 삭제 | 존재하는 파일 | 파일 삭제됨 |
| UF-02 | 심볼릭 링크 삭제 | symlink 경로 | 링크 삭제됨 |
| UF-03 | 디렉토리는 건너뜀 | 디렉토리 경로 | 디렉토리 존재 유지 |
| UF-04 | 존재하지 않는 경로 | 없는 경로 | 예외 없이 종료 |

### 2.7 `prune_empty_dirs(base)` -- P2

| ID | 시나리오 | 테스트 셋업 | 기대 결과 |
|----|---------|-----------|----------|
| PD-01 | 빈 디렉토리 제거 | `tmp/empty/` 생성 | `empty/` 삭제됨 |
| PD-02 | 파일 있는 디렉토리 유지 | `tmp/has-file/a.txt` | `has-file/` 유지 |
| PD-03 | 중첩 빈 디렉토리 | `tmp/a/b/c/` (모두 빈) | 모두 삭제 |
| PD-04 | 존재하지 않는 base | 없는 경로 | 예외 없이 종료 |

### 2.8 `git_cmd()` / `git_bytes()` -- P2

**Mock 전략**: `subprocess.run`을 Mock하여 Git 호출 없이 테스트한다.

| ID | 시나리오 | Mock 반환값 | 기대 결과 |
|----|---------|-----------|----------|
| GC-01 | 성공적인 git 명령 | `stdout="output", returncode=0` | `("output", 0)` |
| GC-02 | 실패한 git 명령 | `returncode=128` | `("", 128)` |
| GB-01 | 바이너리 데이터 반환 | `stdout=b"\x00\x01"` | `(b"\x00\x01", 0)` |
| GB-02 | encoding 파라미터 미사용 확인 | - | `git_bytes`가 `text=True` 없이 호출 |

---

## 3. 통합 테스트

### 3.1 `main()` -- newest-wins 병합 로직 -- P0

**Mock 전략**:
- 파일시스템: `tmp_path` 임시 디렉토리로 `sync_dir`, `local_dir` 구성
- Git 명령: `subprocess.run`을 Mock (또는 `git_cmd`/`git_bytes` 함수를 Mock)
- `sys.argv`: 테스트에서 직접 주입

#### 시나리오별 테스트 케이스

| ID | 시나리오 | 셋업 | 기대 결과 |
|----|---------|------|----------|
| M-01 | 피어가 최신 - 파일 갱신 | 피어 ts > 로컬 ts, FETCH_HEAD에 새 내용 존재 | 로컬 + repo 파일 모두 피어 내용으로 갱신 |
| M-02 | 로컬이 최신 - 로컬 유지 | 로컬 ts > 피어 ts | 로컬 파일이 repo로 복사됨 |
| M-03 | 피어 ts 동일 - 로컬 유지 | 로컬 ts == 피어 ts | 로컬 파일이 repo로 복사됨 (동일 시 로컬 우선) |
| M-04 | 피어 없음 - 첫 실행 | `peer_ts_all` 빈 상태 | 로컬 파일만 repo로 복사 |
| M-05 | 여러 피어 중 최신 선택 | peer_A ts=100, peer_B ts=200 | peer_B의 내용 적용 |
| M-06 | 로컬에서 삭제된 파일 | 로컬에 없고 our_ts에만 존재 | repo에서도 삭제됨 |
| M-07 | 제외 파일 repo 정리 | repo에 EXCLUDES 대상 파일 존재 | repo에서 제거됨 |
| M-08 | workspace 섹션 스킵 | `~/.openclaw/workspace` 디렉토리 없음 | workspace 처리 건너뜀, 에러 없음 |
| M-09 | claude-code 심볼릭 링크 정리 | repo claude-code 내 symlink 존재 | symlink 삭제됨 |
| M-10 | 타임스탬프 파일 생성 | 정상 실행 | `timestamps/{hostname}.json` 생성, 올바른 JSON 형식 |

#### 엣지 케이스

| ID | 시나리오 | 조건 | 검증 포인트 |
|----|---------|------|-----------|
| M-E01 | FETCH_HEAD 없음 | `git ls-tree FETCH_HEAD` 실패 (rc!=0) | 에러 없이 로컬 전용 동기화 |
| M-E02 | 피어 타임스탬프 JSON 파싱 실패 | 잘못된 JSON 내용 | 해당 피어 무시, 계속 진행 |
| M-E03 | git show 실패 | 피어가 최신이지만 `git show` rc!=0 | 해당 파일 건너뜀, 에러 없음 |
| M-E04 | 대량 파일 처리 | 100+ 파일 | 성능 저하 없이 정상 완료 |
| M-E05 | 한글/유니코드 파일명 | `가나자와-여행플랜.pdf` 같은 파일 | 정상 처리, 타임스탬프 기록 |

### 3.2 타임스탬프 키 마이그레이션 통합 -- P1

| ID | 시나리오 | 셋업 | 기대 결과 |
|----|---------|------|----------|
| MI-01 | 로컬 ts 파일에 구 키 | `timestamps/host.json`에 `"claude-config"` 키 | `"claude-code"`로 마이그레이션 후 정상 동작 |
| MI-02 | 피어 ts에 구 키 | FETCH_HEAD의 피어 JSON에 구 키 | 마이그레이션 후 비교 가능 |

---

## 4. sync.sh 셸 스크립트 테스트 -- P1

**테스트 방식**: 셸 스크립트의 각 단계를 분리하여 검증한다. 실제 Git remote 연동은 Mock한다.

### 4.1 플랫폼 감지

| ID | 시나리오 | 환경 | 기대 결과 |
|----|---------|------|----------|
| SH-01 | macOS 감지 | `OSTYPE=darwin*` | `PLATFORM="macos"`, `PYTHON_CMD="python3"` |
| SH-02 | Linux 감지 | `OSTYPE=linux-gnu` | `PLATFORM="linux"`, `PYTHON_CMD="python3"` |
| SH-03 | Windows 감지 | `OSTYPE=msys` | `PLATFORM="windows"`, `PYTHON_CMD="python"`, `PYTHONUTF8=1` |

### 4.2 동기화 흐름

| ID | 시나리오 | 조건 | 기대 결과 |
|----|---------|------|----------|
| SH-04 | 변경 없음 | `git diff --cached --quiet` 성공 | "No changes" 출력, commit/push 없음 |
| SH-05 | 변경 있음 - push 성공 | diff 있음, push 성공 | commit + push 실행 |
| SH-06 | push 충돌 - rebase 후 재시도 | 첫 push 실패 | `git pull --rebase` 후 재push |
| SH-07 | Windows pull-only | `PLATFORM=windows` | push 스킵, `git reset --hard origin/main` 실행 |
| SH-08 | git add 경로 제한 | - | `openclaw/workspace claude-code timestamps state`만 add됨 |

### 4.3 state 생성

| ID | 시나리오 | 조건 | 기대 결과 |
|----|---------|------|----------|
| SH-09 | state 파일 생성 | 정상 실행 | `state/{hostname}.md` 생성, 필수 섹션 포함 |
| SH-10 | openclaw 미설치 | `openclaw` 명령 없음 | `Version: N/A` 기록, 에러 없음 |

---

## 5. setup 스크립트 테스트 -- P2

### 5.1 `setup-mac.sh`

| ID | 시나리오 | 조건 | 기대 결과 |
|----|---------|------|----------|
| SM-01 | 워크스페이스 복원 | 정상 실행 | `~/.openclaw/workspace`에 파일 복사됨 |
| SM-02 | openclaw.json 미존재 시 생성 | 파일 없음 | 템플릿에서 생성, 토큰 치환됨 |
| SM-03 | openclaw.json 이미 존재 | 파일 있음 | 건너뜀 (덮어쓰지 않음) |

### 5.2 `setup-windows.sh`

| ID | 시나리오 | 조건 | 기대 결과 |
|----|---------|------|----------|
| SW-01 | Claude Code 설정 복원 | 정상 실행 | 화이트리스트 항목이 `~/.claude/`에 복사됨 |
| SW-02 | 복사 항목 일치 확인 | - | `setup-windows.sh`의 for 루프 항목과 `CLAUDE_INCLUDES`가 일치 |

---

## 6. 설계문서 vs 구현 간 차이 분석

테스트 플랜 작성 과정에서 발견한 설계문서와 실제 구현 간의 불일치/보완 사항이다.

| 항목 | 설계문서 | 실제 구현 | 비고 |
|------|---------|----------|------|
| `walk_files` 반환 타입 | `dict` | `dict[str, float]` | 설계문서에 value 타입 명시 없음 |
| 삭제 전파 로직 | 미언급 | `main()`에서 로컬 삭제 시 repo에서도 제거 | 설계문서에 삭제 시나리오 누락 |
| `walk_all_files()` | 미언급 | 별도 함수로 존재 (필터링 없는 전체 파일 수집) | 설계문서에 없는 함수 |
| `unlink_if_file()` | 미언급 | 파일/심볼릭 링크만 삭제하는 헬퍼 | 설계문서에 없는 함수 |
| `prune_empty_dirs()` | 미언급 | 빈 디렉토리 정리 로직 | 설계문서에 없는 함수 |
| claude-code symlink 정리 | 미언급 | section이 claude-code일 때 repo 내 symlink 삭제 | 설계문서에 없는 동작 |
| 다중 피어 처리 | "피어 타임스탬프" (단수 암시) | 여러 피어 중 파일별 최신 선택 | 설계문서에 다중 피어 로직 미기술 |
| `setup-windows.sh` 화이트리스트 동기화 | 미언급 | `CLAUDE_INCLUDES`와 별도로 하드코딩된 항목 리스트 | 불일치 위험 존재 |

---

## 7. 테스트 인프라 요구사항

### 7.1 프레임워크 및 도구

| 항목 | 권장 도구 |
|------|----------|
| Python 테스트 프레임워크 | `pytest` |
| 임시 파일시스템 | `pytest`의 `tmp_path` fixture |
| Mock | `unittest.mock` (`patch`, `MagicMock`) |
| 셸 스크립트 테스트 | `bats-core` 또는 직접 `bash` 호출 + 출력 검증 |

### 7.2 테스트 파일 구조

```
ai-config-sync/
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # 공통 fixture (tmp 동기화 디렉토리 등)
│   ├── test_should_include.py    # SI-* 테스트 케이스
│   ├── test_walk_files.py        # WF-*, WA-* 테스트 케이스
│   ├── test_migrate_ts_keys.py   # MK-* 테스트 케이스
│   ├── test_helpers.py           # MT-*, UF-*, PD-*, GC-*, GB-* 테스트 케이스
│   ├── test_main_integration.py  # M-*, MI-* 통합 테스트 케이스
│   └── test_sync_shell.py        # SH-* 셸 스크립트 테스트
```

### 7.3 공통 Fixture 설계 (`conftest.py`)

```python
@pytest.fixture
def sync_env(tmp_path):
    """동기화 환경 전체를 tmp_path 내에 구성"""
    sync_dir = tmp_path / "sync"
    sync_dir.mkdir()
    (sync_dir / "timestamps").mkdir()
    (sync_dir / "openclaw" / "workspace").mkdir(parents=True)
    (sync_dir / "claude-code").mkdir()

    local_workspace = tmp_path / "local_workspace"
    local_workspace.mkdir()

    local_claude = tmp_path / "local_claude"
    local_claude.mkdir()

    return {
        "sync_dir": sync_dir,
        "local_workspace": local_workspace,
        "local_claude": local_claude,
        "hostname": "test-host",
    }
```

---

## 8. 테스트 우선순위 및 실행 계획

### Phase 1 (P0 -- 핵심 로직)
1. `test_should_include.py`: 20개 케이스 + 3개 엣지 케이스
2. `test_walk_files.py`: 8개 케이스
3. `test_main_integration.py`: 10개 시나리오 + 5개 엣지 케이스

### Phase 2 (P1 -- 보조 로직 + 셸)
4. `test_migrate_ts_keys.py`: 5개 케이스
5. `test_walk_files.py` (walk_all_files): 3개 케이스
6. `test_sync_shell.py`: 10개 케이스
7. `test_main_integration.py` (마이그레이션 통합): 2개 케이스

### Phase 3 (P2 -- 헬퍼 + 셋업)
8. `test_helpers.py`: 12개 케이스
9. setup 스크립트 검증: 5개 케이스

### 총 테스트 케이스 수

| 우선순위 | Unit | Integration | Shell/E2E | 합계 |
|---------|------|-------------|-----------|------|
| P0 | 28 | 15 | - | 43 |
| P1 | 8 | 2 | 10 | 20 |
| P2 | 12 | - | 5 | 17 |
| **합계** | **48** | **17** | **15** | **80** |

---

## 9. 리스크 및 주의사항

1. **플랫폼 의존성**: `sync-timestamps.py`는 `pathlib`과 `as_posix()`를 사용하여 크로스 플랫폼을 지원하지만, Windows에서의 실제 동작은 CI 환경 없이는 완전 검증 불가하다.
2. **Git 상태 의존성**: `main()` 함수가 `FETCH_HEAD`를 참조하므로, 통합 테스트에서 Git Mock의 정확성이 중요하다.
3. **setup-windows.sh 항목 동기화**: `CLAUDE_INCLUDES` 변경 시 `setup-windows.sh`의 하드코딩된 리스트도 함께 수정해야 한다. 이를 검증하는 테스트(SW-02)를 반드시 포함한다.
4. **타임스탬프 정밀도**: 플랫폼별 `st_mtime` 정밀도 차이(macOS: ns, Linux: ns, Windows: 100ns)로 인한 비교 오류 가능성이 있다.
5. **동시 실행**: 크론이 30분마다 `sync.sh`를 실행하므로, 테스트 실행 중 크론 충돌 가능성을 고려해야 한다. 테스트는 반드시 격리된 `tmp_path`에서 수행한다.
