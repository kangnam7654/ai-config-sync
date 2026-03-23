# Sync Engine 테스트 플랜

> 대상 설계문서: `test-design-doc.md` (Sync Engine 설계문서)
> 대상 프로젝트: `/Users/kangnam/projects/ai-config-sync`
> 작성일: 2026-03-23

---

## 1. 분석 요약

### 1.1 테스트 대상 컴포넌트

| 컴포넌트 | 파일 | 유형 | 복잡도 |
|----------|------|------|--------|
| `sync-timestamps.py` | 핵심 동기화 엔진 | Python 스크립트 | 높음 |
| `sync.sh` | 오케스트레이션 셸 스크립트 | Bash | 중간 |
| `setup-mac.sh` | macOS 초기 설정 | Bash | 낮음 |
| `setup-windows.sh` | Windows 초기 설정 | Bash | 낮음 |

### 1.2 테스트 가능한 함수 (설계문서 API 기준)

설계문서에 명시된 3개 함수와 소스 코드에서 추가 식별된 헬퍼 함수들:

| 함수 | 입력 | 출력 | 순수 함수 여부 |
|------|------|------|---------------|
| `should_include(filepath, section)` | 문자열 2개 | bool | Yes |
| `walk_files(base, section)` | Path, 문자열 | dict | No (파일시스템 의존) |
| `migrate_ts_keys(ts)` | dict | dict | Yes |
| `mtime(p)` | Path | float | No (파일시스템 의존) |
| `walk_all_files(base)` | Path | set | No (파일시스템 의존) |
| `unlink_if_file(path)` | Path | None | No (파일시스템 변경) |
| `prune_empty_dirs(base)` | Path | None | No (파일시스템 변경) |
| `git_cmd(args, cwd)` | list, str | tuple | No (외부 프로세스) |
| `git_bytes(args, cwd)` | list, str | tuple | No (외부 프로세스) |
| `main()` | sys.argv | None | No (통합 함수) |

---

## 2. Unit 테스트

### 2.1 `should_include(filepath, section)` -- 20 케이스

이 함수는 순수 함수이며 외부 의존성이 없어 mock 없이 테스트 가능하다.

#### 2.1.1 workspace 섹션 -- 포함 케이스

| ID | 입력 filepath | 입력 section | 기대 결과 | 검증 의도 |
|----|--------------|-------------|----------|----------|
| SI-01 | `"MEMORY.md"` | `"workspace"` | `True` | 일반 파일 포함 확인 |
| SI-02 | `"agents/reviewer.md"` | `"workspace"` | `True` | 하위 디렉토리 파일 포함 |
| SI-03 | `"idea-lab/plan.md"` | `"workspace"` | `True` | 중첩 디렉토리 파일 포함 |

#### 2.1.2 workspace 섹션 -- 제외 케이스

| ID | 입력 filepath | 입력 section | 기대 결과 | 검증 의도 |
|----|--------------|-------------|----------|----------|
| SI-04 | `"notion_data_2026.json"` | `"workspace"` | `False` | `notion_data_*.json` 패턴 제외 |
| SI-05 | `"tmp_backup.json"` | `"workspace"` | `False` | `tmp_*.json` 패턴 제외 |
| SI-06 | `"data.jsonl"` | `"workspace"` | `False` | `*.jsonl` 패턴 제외 |
| SI-07 | `".git"` | `"workspace"` | `False` | `.git` 제외 |
| SI-08 | `"tools/flutter/bin/dart"` | `"workspace"` | `False` | `tools/flutter/**` 패턴 제외 |
| SI-09 | `"tools/flutter"` | `"workspace"` | `False` | `tools/flutter` 정확히 제외 |

#### 2.1.3 claude-code 섹션 -- 포함 케이스 (화이트리스트)

| ID | 입력 filepath | 입력 section | 기대 결과 | 검증 의도 |
|----|--------------|-------------|----------|----------|
| SI-10 | `"settings.json"` | `"claude-code"` | `True` | 화이트리스트 파일 직접 포함 |
| SI-11 | `"CLAUDE.md"` | `"claude-code"` | `True` | CLAUDE.md 포함 |
| SI-12 | `"skills/doc-loop/prompt.md"` | `"claude-code"` | `True` | 화이트리스트 디렉토리 하위 포함 |
| SI-13 | `"agents/reviewer.md"` | `"claude-code"` | `True` | agents 디렉토리 포함 |
| SI-14 | `"plugins/my-plugin/config.json"` | `"claude-code"` | `True` | plugins 디렉토리 포함 |
| SI-15 | `"memory/MEMORY.md"` | `"claude-code"` | `True` | memory 디렉토리 포함 |

#### 2.1.4 claude-code 섹션 -- 제외 케이스

| ID | 입력 filepath | 입력 section | 기대 결과 | 검증 의도 |
|----|--------------|-------------|----------|----------|
| SI-16 | `"history.jsonl"` | `"claude-code"` | `False` | EXCLUDES 패턴 우선 적용 |
| SI-17 | `"cache"` | `"claude-code"` | `False` | 제외 패턴 단일 디렉토리명 |
| SI-18 | `"unknown-dir/file.txt"` | `"claude-code"` | `False` | 화이트리스트에 없는 최상위 디렉토리 |
| SI-19 | `"randomfile.txt"` | `"claude-code"` | `False` | 화이트리스트에 없는 파일 |

#### 2.1.5 엣지 케이스

| ID | 입력 filepath | 입력 section | 기대 결과 | 검증 의도 |
|----|--------------|-------------|----------|----------|
| SI-20 | `""` | `"workspace"` | `True` | 빈 문자열 처리 (크래시 안 남 확인) |

---

### 2.2 `migrate_ts_keys(ts)` -- 8 케이스

순수 함수, mock 불필요.

| ID | 입력 dict | 기대 출력 | 검증 의도 |
|----|----------|----------|----------|
| MK-01 | `{"claude-config": {"f.md": 1.0}}` | `{"claude-code": {"f.md": 1.0}}` | 기본 마이그레이션 동작 |
| MK-02 | `{"claude-code": {"f.md": 1.0}}` | `{"claude-code": {"f.md": 1.0}}` | 이미 새 키면 변경 없음 |
| MK-03 | `{}` | `{}` | 빈 dict 처리 |
| MK-04 | `{"workspace": {"f.md": 1.0}}` | `{"workspace": {"f.md": 1.0}}` | 마이그레이션 대상 아닌 키 |
| MK-05 | `{"claude-config": {"a": 1}, "claude-code": {"b": 2}}` | `{"claude-config": {"a": 1}, "claude-code": {"b": 2}}` | 양쪽 키 모두 존재 시 마이그레이션 안 함 (new_key 이미 있으므로) |
| MK-06 | `{"claude-config": {}, "workspace": {"f.md": 1.0}}` | `{"claude-code": {}, "workspace": {"f.md": 1.0}}` | 빈 값의 old key도 마이그레이션 |
| MK-07 | 원본 dict 참조 | 반환값 is 원본 | in-place 변경 확인 (반환값이 동일 객체) |
| MK-08 | `{"claude-config": {"a": 1}}` 마이그레이션 후 | `"claude-config" not in result` | old key 제거 확인 |

---

### 2.3 `mtime(p)` -- 4 케이스

파일시스템 의존. `tmp_path` fixture 또는 mock 사용.

| ID | 시나리오 | 기대 결과 | Mock 대상 |
|----|---------|----------|----------|
| MT-01 | 존재하는 파일 | 0보다 큰 float | 임시 파일 생성 |
| MT-02 | 존재하지 않는 경로 | `0.0` | 존재하지 않는 Path |
| MT-03 | 권한 없는 파일 | `0.0` | `Path.stat` 에서 PermissionError |
| MT-04 | 디렉토리 경로 | 0보다 큰 float | 임시 디렉토리 |

---

### 2.4 `walk_files(base, section)` -- 7 케이스

파일시스템 의존. `tmp_path` fixture로 디렉토리 구조 생성 후 테스트.

| ID | 디렉토리 구조 | section | 기대 결과 | 검증 의도 |
|----|-------------|---------|----------|----------|
| WF-01 | `a.md`, `b.txt` | `"workspace"` | 2개 항목, 키가 `"a.md"`, `"b.txt"` | 기본 동작 |
| WF-02 | `sub/c.md` | `"workspace"` | 키가 `"sub/c.md"` (POSIX 경로) | 하위 디렉토리 + 경로 형식 |
| WF-03 | `.git/config`, `a.md` | `"workspace"` | 1개 항목 (`a.md`만) | .git 디렉토리 제외 |
| WF-04 | `notion_data_x.json`, `a.md` | `"workspace"` | 1개 항목 (`a.md`만) | EXCLUDES 패턴 적용 |
| WF-05 | `settings.json`, `cache/x` | `"claude-code"` | 1개 항목 (`settings.json`만) | 화이트리스트 + 제외 조합 |
| WF-06 | 빈 디렉토리 | `"workspace"` | 빈 dict `{}` | 빈 디렉토리 처리 |
| WF-07 | 존재하지 않는 경로 | `"workspace"` | 빈 dict `{}` | 미존재 경로 처리 |

---

### 2.5 `walk_all_files(base)` -- 4 케이스

| ID | 디렉토리 구조 | 기대 결과 | 검증 의도 |
|----|-------------|----------|----------|
| WA-01 | `a.md`, `sub/b.txt` | `{"a.md", "sub/b.txt"}` | 기본 동작 + POSIX 경로 |
| WA-02 | `.git/config`, `a.md` | `{"a.md"}` | .git 제외 |
| WA-03 | 빈 디렉토리 | `set()` | 빈 디렉토리 |
| WA-04 | 존재하지 않는 경로 | `set()` | 미존재 경로 |

---

### 2.6 `unlink_if_file(path)` -- 5 케이스

파일시스템 변경 함수. `tmp_path` 사용.

| ID | 시나리오 | 기대 결과 | 검증 의도 |
|----|---------|----------|----------|
| UF-01 | 일반 파일 | 파일 삭제됨 | 기본 삭제 동작 |
| UF-02 | 심볼릭 링크 | 링크 삭제됨 (대상 파일은 유지) | 심볼릭 링크 처리 |
| UF-03 | 디렉토리 | 삭제 안 됨, 에러 안 남 | 디렉토리 보호 |
| UF-04 | 존재하지 않는 경로 | 에러 안 남 | 미존재 파일 안전 처리 |
| UF-05 | 권한 없는 파일 | 에러 안 남 (OSError 무시) | 예외 처리 |

---

### 2.7 `prune_empty_dirs(base)` -- 5 케이스

| ID | 시나리오 | 기대 결과 | 검증 의도 |
|----|---------|----------|----------|
| PD-01 | `a/b/` (둘 다 빈 디렉토리) | 둘 다 삭제 | 재귀 빈 디렉토리 정리 |
| PD-02 | `a/` (파일 있음), `b/` (비어 있음) | `b/`만 삭제 | 비어있지 않은 디렉토리 보존 |
| PD-03 | 존재하지 않는 경로 | 에러 안 남 | 미존재 경로 안전 처리 |
| PD-04 | 파일만 있는 디렉토리 | 변경 없음 | 파일이 있는 디렉토리는 삭제 안 함 |
| PD-05 | 깊이 3이상 중첩 빈 디렉토리 `a/b/c/` | 모두 삭제 | 하위부터 정리 순서 확인 |

---

### 2.8 `git_cmd(args, cwd)` / `git_bytes(args, cwd)` -- 4 케이스

외부 프로세스 호출. `subprocess.run`을 mock한다.

| ID | 함수 | Mock 반환 | 기대 결과 | 검증 의도 |
|----|------|----------|----------|----------|
| GC-01 | `git_cmd` | stdout=`"abc\n"`, rc=0 | `("abc", 0)` | 정상 출력 + strip 처리 |
| GC-02 | `git_cmd` | stdout=`""`, rc=128 | `("", 128)` | 실패 시 returncode 전달 |
| GC-03 | `git_bytes` | stdout=`b"\xff\xfe"`, rc=0 | `(b"\xff\xfe", 0)` | 바이너리 데이터 보존 |
| GC-04 | `git_bytes` | stdout=`b""`, rc=1 | `(b"", 1)` | 실패 시 빈 바이트 |

---

## 3. 통합 테스트

### 3.1 `main()` 함수 -- newest-wins 병합 시나리오

외부 I/O인 `git_cmd`, `git_bytes`와 `sys.argv`를 mock하고, 파일시스템은 `tmp_path`로 실제 구성한다.

| ID | 시나리오 | 초기 상태 | 기대 결과 | Mock 대상 |
|----|---------|----------|----------|----------|
| INT-01 | 피어가 최신 파일 보유 | 로컬 mtime=100, 피어 ts=200 | 로컬+repo에 피어 내용 기록 | `git_cmd`, `git_bytes` |
| INT-02 | 로컬이 최신 | 로컬 mtime=200, 피어 ts=100 | 로컬 내용이 repo에 복사 | `git_cmd` |
| INT-03 | 피어 없음 (첫 실행) | 피어 타임스탬프 없음 | 로컬 파일만 repo에 복사 | `git_cmd` |
| INT-04 | 로컬에서 삭제된 파일 | 로컬 없음, repo에 존재, 피어 ts=0 | repo에서도 삭제 | `git_cmd` |
| INT-05 | 제외 패턴 파일이 repo에 존재 | repo에 `history.jsonl` 존재 | repo에서 삭제됨 | `git_cmd` |
| INT-06 | workspace 미존재 | `~/.openclaw/workspace` 없음 | workspace 섹션 스킵 | `git_cmd` |
| INT-07 | 타임스탬프 키 마이그레이션 | 기존 ts에 `claude-config` 키 | `claude-code`로 변환 후 처리 | `git_cmd` |
| INT-08 | 타임스탬프 JSON 저장 | 동기화 완료 후 | `timestamps/{hostname}.json` 파일 생성, JSON 유효 | `git_cmd` |
| INT-09 | 여러 피어 중 최신 선택 | 피어A ts=100, 피어B ts=200 | 피어B의 내용 적용 | `git_cmd`, `git_bytes` |
| INT-10 | claude-code 심볼릭 링크 제거 | repo에 심볼릭 링크 존재 | 심볼릭 링크 삭제됨 | `git_cmd` |

---

### 3.2 `sync.sh` -- 셸 스크립트 통합 시나리오

셸 스크립트는 단위 테스트가 어려우므로 시나리오 기반 검증 목록으로 관리한다.

| ID | 시나리오 | 검증 항목 | 방법 |
|----|---------|----------|------|
| SH-01 | macOS에서 실행 | `PLATFORM=macos`, `PYTHON_CMD=python3` | 수동/CI |
| SH-02 | Windows에서 실행 | `PLATFORM=windows`, push 스킵, `git reset --hard` 실행 | 수동/CI |
| SH-03 | Linux에서 실행 | `PLATFORM=linux`, `PYTHON_CMD=python3` | 수동/CI |
| SH-04 | push 충돌 시 rebase 재시도 | 첫 push 실패 후 `git pull --rebase` + 재push | 수동 |
| SH-05 | 변경 없을 때 커밋 스킵 | `git diff --cached --quiet` 참이면 커밋 안 함 | 수동 |
| SH-06 | `generate_state` 출력 확인 | `state/{hostname}.md` 생성, 필수 섹션 포함 | 수동/CI |
| SH-07 | `git add` 경로 제한 | `openclaw/workspace claude-code timestamps state`만 add | 코드 리뷰 |

---

## 4. 엣지 케이스 / 경계값 테스트

| ID | 시나리오 | 관련 함수 | 기대 동작 |
|----|---------|----------|----------|
| EC-01 | 타임스탬프 JSON 파일 손상 (유효하지 않은 JSON) | `main()` | `json.loads` 예외 → 피어 무시 |
| EC-02 | FETCH_HEAD 없음 (git fetch 미실행) | `main()` | `ls-tree` 실패 → 피어 없음으로 처리 |
| EC-03 | 매우 큰 파일 (100MB+) | `git_bytes`, `write_bytes` | 메모리 내에서 처리 (성능 저하 가능하나 크래시 안 남) |
| EC-04 | 파일명에 한글/특수문자 포함 | `walk_files`, `should_include` | POSIX 경로로 정상 처리 (실제 데이터에 `가나자와-여행플랜.pdf` 존재) |
| EC-05 | 동일 타임스탬프 (our == peer) | `main()` 비교 로직 | `peer_file_ts > our_file_ts`이므로 로컬 유지 (동점 시 로컬 우선) |
| EC-06 | 타임스탬프 0.0 (mtime 실패한 파일) | `mtime`, `main()` | 0.0으로 비교 → 피어가 양수면 피어 적용 |
| EC-07 | `sys.argv` 인수 부족 | `main()` | `IndexError` 발생 (현재 예외 처리 없음 -- 발견 사항) |
| EC-08 | `git show` 실패 (rc != 0) | `main()` 피어 적용 | 내용 미갱신 (rc2 == 0 체크) |
| EC-09 | 피어 ts에만 있고 로컬/repo 모두 없는 파일 | `main()` | `git show`로 피어 내용 가져와 로컬+repo 생성 |
| EC-10 | sections dict에 없는 섹션명으로 `should_include` 호출 | `should_include` | `True` 반환 (EXCLUDES에 키 없음, claude-code 아님) |

---

## 5. 보안 테스트

| ID | 시나리오 | 관련 파일 | 검증 항목 |
|----|---------|----------|----------|
| SEC-01 | `openclaw.json` 동기화 방지 | `.gitignore` | `openclaw/openclaw.json`이 git 추적에서 제외 확인 |
| SEC-02 | 자격 증명 파일 제외 | `.gitignore` | `credentials/`, `auth-profiles.json`, `*.db` 제외 확인 |
| SEC-03 | `git add` 범위 제한 | `sync.sh` | `git add -A` 뒤에 특정 경로만 지정하여 의도치 않은 파일 커밋 방지 |
| SEC-04 | 화이트리스트 우회 불가 | `should_include` | claude-code 섹션에서 화이트리스트 외 파일은 `False` |

---

## 6. 테스트 환경 및 인프라 요구사항

### 6.1 테스트 프레임워크

```
pytest + tmp_path fixture (파일시스템 테스트)
unittest.mock (subprocess, sys.argv mock)
```

### 6.2 필요 패키지

```
uv add --dev pytest pytest-cov
```

### 6.3 디렉토리 구조

```
ai-config-sync/
├── tests/
│   ├── __init__.py
│   ├── test_should_include.py      # SI-01 ~ SI-20
│   ├── test_migrate_ts_keys.py     # MK-01 ~ MK-08
│   ├── test_mtime.py               # MT-01 ~ MT-04
│   ├── test_walk_files.py          # WF-01 ~ WF-07, WA-01 ~ WA-04
│   ├── test_file_operations.py     # UF-01 ~ UF-05, PD-01 ~ PD-05
│   ├── test_git_helpers.py         # GC-01 ~ GC-04
│   ├── test_main_integration.py    # INT-01 ~ INT-10
│   └── test_edge_cases.py          # EC-01 ~ EC-10
└── sync-timestamps.py
```

### 6.4 실행 명령

```bash
# 전체 테스트
uv run python -m pytest tests/ -q

# 커버리지 포함
uv run python -m pytest tests/ --cov=sync-timestamps --cov-report=term-missing

# 특정 모듈만
uv run python -m pytest tests/test_should_include.py -v
```

---

## 7. 테스트 우선순위

### P0 (필수 -- 핵심 동기화 로직)

- SI-01 ~ SI-20: `should_include` 전체 (동기화 범위 결정 핵심)
- MK-01 ~ MK-08: `migrate_ts_keys` 전체 (데이터 무결성)
- INT-01 ~ INT-05: newest-wins 병합 핵심 시나리오
- INT-08: 타임스탬프 JSON 저장 (상태 지속성)
- EC-05: 동점 처리 (데이터 유실 방지)

### P1 (중요 -- 안정성)

- WF-01 ~ WF-07: `walk_files` (파일 탐색)
- UF-01 ~ UF-05: `unlink_if_file` (파일 삭제 안전성)
- INT-06 ~ INT-07, INT-09 ~ INT-10: 통합 시나리오 나머지
- EC-01, EC-02, EC-08: 예외 상황 대응
- SEC-01 ~ SEC-04: 보안 검증

### P2 (보통 -- 보조 기능)

- MT-01 ~ MT-04: `mtime` (단순 래퍼)
- WA-01 ~ WA-04: `walk_all_files` (보조 함수)
- PD-01 ~ PD-05: `prune_empty_dirs`
- GC-01 ~ GC-04: `git_cmd`/`git_bytes` (래퍼 함수)

### P3 (낮음 -- 셸 스크립트 / 수동)

- SH-01 ~ SH-07: `sync.sh` 시나리오 (자동화 어려움)
- EC-03, EC-04: 대용량/특수문자 (실환경 검증)

---

## 8. 발견 사항 및 리스크

### 8.1 테스트 인프라 부재

프로젝트에 현재 테스트 프레임워크가 설정되어 있지 않다. `CLAUDE.md`에도 "테스트 프레임워크 없음"으로 명시되어 있으며, `pytest` 설정과 `tests/` 디렉토리 생성이 선행되어야 한다.

### 8.2 모듈 임포트 문제

`sync-timestamps.py`는 파일명에 하이픈(`-`)이 포함되어 있어 Python에서 일반적인 `import` 구문으로 임포트할 수 없다. 테스트 시 `importlib.import_module("sync-timestamps")` 또는 `importlib.util.spec_from_file_location`을 사용해야 한다.

### 8.3 `main()` 함수의 테스트 어려움

`main()`은 `sys.argv`로 인수를 받고, `sections` dict 내부에 `~/.openclaw/workspace`와 `~/.claude` 같은 홈 디렉토리 경로가 하드코딩되어 있다. 통합 테스트 시 다음 조치가 필요하다:

- `sys.argv`를 mock
- `Path.expanduser`를 mock하거나 `sections` dict를 monkeypatch
- 또는 `main()` 내부 로직을 매개변수화하는 리팩터링 검토

### 8.4 설계문서와 구현 간 차이

- 설계문서에 명시되지 않은 함수: `walk_all_files`, `unlink_if_file`, `prune_empty_dirs`, `git_cmd`, `git_bytes`, `mtime` -- 이들은 소스 코드 분석을 통해 추가로 식별됨
- 설계문서의 `walk_files` 반환 타입은 `dict`로 정확하나, 값의 타입(`float` -- mtime)은 명시되지 않음

### 8.5 예외 처리 미비

- `main()` 함수에서 `sys.argv[1]`, `sys.argv[2]` 접근 시 인수 부족에 대한 예외 처리 없음 (EC-07)
- `mtime()` 함수의 bare `except:` 사용 -- 모든 예외를 삼킴 (의도적이나 디버깅 어려움)

---

## 9. 커버리지 목표

| 모듈 | 목표 커버리지 | 근거 |
|------|-------------|------|
| `should_include` | 100% | 순수 함수, 분기 완전 테스트 가능 |
| `migrate_ts_keys` | 100% | 순수 함수, 분기 완전 테스트 가능 |
| `walk_files` / `walk_all_files` | 90%+ | 파일시스템 의존이나 `tmp_path`로 제어 가능 |
| `unlink_if_file` / `prune_empty_dirs` | 85%+ | 예외 경로 포함 |
| `main()` | 80%+ | mock 조합으로 주요 분기 커버 |
| **전체** | **80%+** | CLAUDE.md 커버리지 규칙 충족 |

---

## 10. 테스트 케이스 총계

| 카테고리 | 케이스 수 |
|---------|----------|
| Unit 테스트 | 57개 |
| 통합 테스트 | 10개 |
| 셸 스크립트 시나리오 | 7개 |
| 엣지 케이스 | 10개 |
| 보안 테스트 | 4개 |
| **합계** | **88개** |
