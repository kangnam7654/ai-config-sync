# Audit Report: ai-config-sync

> 진단 일시: 2026-03-24
> 진단 대상: /Users/kangnam/projects/ai-config-sync

---

## 대상 개요

| 항목 | 값 |
|------|-----|
| 프로젝트 경로 | `/Users/kangnam/projects/ai-config-sync` |
| 언어 | Python 3 (sync-timestamps.py), Bash (sync.sh, setup-mac.sh, setup-windows.sh) |
| 프레임워크 | 없음 (stdlib only) |
| DB | 없음 |
| UI | 없음 (CLI 도구) |
| 핵심 파일 수 | 5개 (sync-timestamps.py, sync.sh, setup-mac.sh, setup-windows.sh, .gitignore) |
| 총 커밋 수 | 729 (대부분 30분 간격 자동 sync 커밋) |
| 동기화 대상 | `~/.openclaw/workspace` (OpenClaw), `~/.claude` (Claude Code) |
| 동기화 방식 | newest-wins (파일별 mtime 비교), cron 30분 간격 |
| 진단 범위 | 코드 품질, 보안, 아키텍처, 테스트 (DB: 해당 없음, UX/UI: 해당 없음) |

---

## 베이스라인 점수

| 영역 | 점수 (0-10) | 가중치 | 가중 점수 |
|------|------------|--------|----------|
| 코드 품질 | 5.5 | 0.25 | 1.375 |
| 보안 | 6.0 | 0.25 | 1.500 |
| 아키텍처 | 6.5 | 0.20 | 1.300 |
| DB | N/A | 0.00 | - |
| 테스트 | 1.0 | 0.20 | 0.200 |
| UX/UI | N/A | 0.00 | - |
| **가중 평균 총점** | | | **4.86 / 10** |

> 가중치 합계를 DB/UX 제외 후 0.90으로 정규화하면 총점 = 4.375 / 0.90 = **4.86**

---

## 우선순위 매트릭스

### P0 Critical

| ID | 제목 | 영역 | 심각도 | 난이도 |
|----|------|------|--------|--------|
| TEST-001 | 테스트 전무: sync-timestamps.py에 대한 테스트가 하나도 없음 | test | Critical | M |

### P1 High

| ID | 제목 | 영역 | 심각도 | 난이도 |
|----|------|------|--------|--------|
| CODE-001 | bare except (line 73): `except:` 는 KeyboardInterrupt, SystemExit까지 삼킴 | code_quality | High | S |
| CODE-002 | sys.argv 검증 미흡: 인자 누락 시 IndexError로 크래시 (사용자 메시지 없음) | code_quality | High | S |
| SEC-001 | 동기화 대상에 민감 파일 유입 가능성: CLAUDE_INCLUDES에 `settings.json`, `memory`, `todos` 포함 — 이 경로들이 git push되므로 민감값 유출 경로 존재 | security | High | M |
| ARCH-001 | 동시 실행 보호 없음: cron이 30분마다 sync.sh를 실행하지만 lock 메커니즘이 없어 이전 실행이 늦게 끝나면 동시 실행으로 race condition 발생 가능 | architecture | High | S |

### P2 Medium

| ID | 제목 | 영역 | 심각도 | 난이도 |
|----|------|------|--------|--------|
| CODE-003 | main() 함수가 138줄 단일 블록: 세부 기능(피어 TS 로드, 섹션 처리, TS 저장)이 분리되지 않음 | code_quality | Medium | M |
| CODE-004 | 에러 로깅 부재: git 명령 실패 시 stderr를 무시하고 빈 결과만 반환 | code_quality | Medium | S |
| CODE-005 | 타입 힌트 미적용: 함수 파라미터/반환 타입이 대부분 미지정 (mtime, should_include 등 일부만 있음) | code_quality | Medium | M |
| SEC-002 | git 이력에 민감값 노출 가능성: README에 "이미 토큰이 레포 이력에 노출된 적이 있다면 즉시 재발급" 경고 존재 — git filter-repo 흔적 있음 (.git/filter-repo/), 과거 유출 이력 있었음을 시사 | security | Medium | S |
| SEC-003 | setup-mac.sh에서 생성된 token이 openclaw.json에 평문 저장됨: .gitignore로 추적 제외되어 있으나, sync-timestamps.py가 `~/.openclaw` 하위를 읽을 때 경로 실수로 유입 가능 | security | Medium | S |
| ARCH-002 | sync.sh에서 python3 직접 호출: CLAUDE.md의 NEVER 규칙 #3("시스템 python을 직접 호출하지 마라")과 모순. 단, sync.sh는 cron에서 자동 실행되므로 uv 의존성 추가가 적절한지 검토 필요 | architecture | Medium | S |
| ARCH-003 | Windows `git reset --hard origin/main`: 로컬 변경이 있을 경우 무조건 소실. 경고/백업 없음 | architecture | Medium | S |

### P3 Low

| ID | 제목 | 영역 | 심각도 | 난이도 |
|----|------|------|--------|--------|
| CODE-006 | import 문 스타일: `import os, json, sys, subprocess, shutil, fnmatch` 한 줄에 6개 모듈 나열 (PEP 8 권장은 개별 줄) | code_quality | Low | S |
| CODE-007 | 매직 넘버: `applied_from_peer[:3]`의 3이 상수로 추출되지 않음 (출력 제한) | code_quality | Low | S |
| CODE-008 | sync.sh의 generate_state()에 `find` 명령이 `~/.openclaw/workspace` 없을 때 에러 출력 (2>/dev/null으로 억제되지만 비효율) | code_quality | Low | S |
| ARCH-004 | 타임스탬프 JSON 파일 크기 증가: Kangnamui-MacBookPro.json이 220KB. 동기화 대상 파일이 늘어나면 지속 증가 | architecture | Low | M |
| SEC-004 | .gitignore에 `claude-code/plugins/marketplaces/` 패턴이 있지만 해당 디렉토리가 이미 tracked 상태 (git rm --cached 필요 가능) | security | Low | S |

---

## 영역별 상세 진단

### 1. 코드 품질 (5.5/10)

**안티패턴 및 코드 스멜**:
- `sync-timestamps.py` line 73: `except:` (bare except). `except Exception:` 또는 구체적 예외로 변경 필요.
- `main()` 함수가 126~264줄 (138줄)로 단일 블록. 피어 TS 로딩, 섹션별 처리, TS 저장 등 최소 3개 함수로 분리 권장.
- `sys.argv[1]`, `sys.argv[2]` 접근 시 인자 검증 없음. `len(sys.argv) < 3`이면 IndexError.

**코드 복잡도**:
- `main()` 내부에 3중 for 루프 + 조건 분기가 중첩. 인지 복잡도(Cognitive Complexity) 추정 15+.
- `should_include()` 함수는 2단계 필터(제외 패턴 + 화이트리스트)를 한 함수에서 처리. 단, 짧아서 분리 불필요.

**네이밍 일관성**:
- 함수명은 snake_case로 일관됨 (양호).
- 변수 `r`, `fp`, `p`, `f` 등 축약어 사용. 로컬 스코프 내이므로 수용 가능하나, `r` 대신 `result`가 명확.

**에러 처리 패턴**:
- `git_cmd()`, `git_bytes()`: returncode를 반환하지만 호출부에서 일관되게 검사하지 않음. line 157 `content, _`에서 returncode 무시.
- 피어 TS JSON 파싱 실패 시 `except Exception: pass` (line 160). 어떤 피어가 파싱 실패했는지 로그 없음.

**의존성 관리**:
- stdlib만 사용 (외부 의존성 없음). 양호.
- `pyproject.toml`, `requirements.txt` 없음. Python 프로젝트 메타데이터 미정의.

### 2. 보안 (6.0/10)

**민감 데이터 처리**:
- `.gitignore`로 `openclaw/openclaw.json`, `credentials/`, `auth-profiles.json`, `.env` 등 적절히 제외. 양호.
- `CLAUDE_INCLUDES` 화이트리스트로 claude-code 동기화 범위를 제한. 양호.
- 그러나 `settings.json`, `memory/`, `todos/`, `agent-memory/` 등이 동기화 대상에 포함되어 git에 push됨. 이 파일들에 민감 컨텍스트(프로젝트 경로, 사용자 정보 등)가 포함될 수 있음.
- `.git/filter-repo/` 디렉토리 존재 -- 과거에 git-filter-repo를 실행한 이력이 있음. README에도 "토큰이 레포 이력에 노출된 적이 있다면 즉시 재발급" 경고가 있어, 과거 민감값 유출 사고가 있었음을 시사.

**subprocess 사용**:
- `sync-timestamps.py`에서 `subprocess.run()` 사용 시 `shell=False` (리스트 인자). 양호.
- 사용자 입력이 직접 subprocess에 전달되지 않음 (git 명령만 실행). 인젝션 위험 낮음.

**인증/인가**:
- 해당 없음 (서버 아닌 로컬 도구).

**CORS/CSP**:
- 해당 없음.

### 3. 아키텍처 (6.5/10)

**모듈 간 결합도**:
- 핵심 코드가 2개 파일(`sync-timestamps.py`, `sync.sh`)에 집중. 결합도 낮음 (양호).
- `sync.sh`가 `sync-timestamps.py`를 호출하는 단방향 의존. 명확.

**계층 분리**:
- 단일 계층 스크립트. 계층화가 필요한 규모가 아님.
- 그러나 `sync-timestamps.py`의 `main()` 함수가 I/O, 비즈니스 로직, 출력을 모두 처리. 테스트 가능성을 위해 분리 권장.

**확장성 병목**:
- 타임스탬프 JSON이 파일 1개당 1 엔트리. 동기화 대상 수천 개 시 JSON 크기 증가 (현재 220KB).
- 매 실행마다 `os.walk()` + `git show`로 전체 파일 스캔. 파일 수 증가 시 선형 성능 저하.

**기술 부채**:
- 동시 실행 보호 부재 (lock file 미사용).
- Windows 경로에서 `git reset --hard`로 로컬 변경 무조건 폐기.
- `sync.sh`에서 `python3` 직접 호출 (프로젝트 CLAUDE.md에서는 `uv run python` 사용 규칙이 있으나, cron 환경에서 uv 가용성이 보장되지 않으므로 현재 방식이 합리적일 수 있음. CLAUDE.md에서도 "테스트 프레임워크 없음. 변경 시 python3로 직접 실행해서 확인"이라고 명시).

**설정/환경 관리**:
- 플랫폼 감지(`detect_platform`)가 `sync.sh`에 구현. 양호.
- 환경 변수(`PYTHONUTF8`, `PYTHONIOENCODING`)가 Windows에서 적절히 설정됨.

### 4. DB 진단

해당 없음 (DB 미사용).

### 5. 테스트 (1.0/10)

**테스트 커버리지**: 0%.

**테스트 인프라**:
- `tests/` 디렉토리 없음.
- `pyproject.toml` 없음.
- pytest 미설정.
- 프로젝트 CLAUDE.md에 명시적으로 "테스트 프레임워크 없음"이라고 기록되어 있음.

**누락된 테스트 영역** (우선순위순):
1. `should_include()`: 제외 패턴 + 화이트리스트 로직. 경계 케이스가 많음.
2. `migrate_ts_keys()`: 키 마이그레이션 로직.
3. `walk_files()` / `walk_all_files()`: .git 제외, 상대경로 변환.
4. `main()` 내 newest-wins 병합 로직: 피어 TS > 로컬 TS, 로컬 > 피어, 동일, 파일 삭제 전파 시나리오.
5. `sync.sh` 통합 테스트: 플랫폼별 분기, push/pull-only 동작.

**1점 부여 근거**: 코드가 프로덕션에서 cron으로 30분마다 실행 중이고 실제로 동작하고 있으므로 암묵적 검증은 되고 있음. 그러나 자동화된 테스트는 0.

### 6. UX/UI 진단

해당 없음 (CLI 도구, UI 없음).

---

## 개선 범위

### design-loop에 전달할 개선 대상 영역

| 영역 | 개선 필요 | 예상 난이도 |
|------|----------|------------|
| 아키텍처 | 예 (main 분리, lock file, 에러 처리) | M |
| DB | 아니오 | - |
| UX/UI | 아니오 | - |
| 코드 품질 | 예 (bare except, arg 검증, 타입 힌트) | S |
| 보안 | 예 (민감파일 검토, 동기화 범위 재확인) | S |
| 테스트 | 예 (테스트 인프라 구축 + 핵심 함수 테스트) | M |

### 우선순위 기반 개선 순서

1. **TEST-001 (P0)**: 테스트 인프라 구축 + `should_include`, `migrate_ts_keys`, newest-wins 로직 테스트 작성
2. **CODE-001 (P1)**: bare except 수정
3. **CODE-002 (P1)**: sys.argv 검증 + usage 메시지
4. **SEC-001 (P1)**: 동기화 대상 파일 중 민감값 포함 가능성 재검토 (settings.json 내용 확인, memory/ 내 민감 컨텍스트 여부)
5. **ARCH-001 (P1)**: sync.sh에 lock file 메커니즘 추가
6. **CODE-003 (P2)**: main() 함수 분리 리팩터링
7. **CODE-004 (P2)**: git 명령 실패 시 에러 로깅
8. **CODE-005 (P2)**: 타입 힌트 추가
9. **나머지 P2~P3**: 위 항목 완료 후 진행

---

## 제약 조건

| 제약 | 설명 |
|------|------|
| 하위호환 | sync.sh, sync-timestamps.py는 macOS, Ubuntu, Windows(Git Bash) 3개 플랫폼에서 동작해야 함. pathlib + `as_posix()` 경로 통일 패턴 유지 필수. |
| cron 환경 | sync.sh는 cron/Task Scheduler에서 30분마다 실행됨. 스크립트 오류 시 전체 동기화 중단. 변경 시 안정성 최우선. |
| encoding | Windows CP949 문제로 모든 파일 I/O에 `encoding="utf-8"` 필수. |
| push 방식 | sync.sh는 `git add -A openclaw/workspace claude-code timestamps state` 경로만 add. 의도치 않은 파일 커밋 방지를 위해 이 패턴 유지. |
| 기존 테스트 | 없음 (보존할 테스트 없음). 신규 테스트 작성 시 기존 동작을 보존하는 방향으로. |
| Python 직접 호출 | sync.sh에서 `python3` 직접 호출 중. cron 환경에서 `uv` 설치가 보장되지 않으므로, 글로벌 CLAUDE.md NEVER 규칙 #3의 예외로 간주할 수 있음. CLAUDE.md(프로젝트)에서도 `python3`으로 직접 실행하라고 명시. |
| 민감 파일 | `openclaw/openclaw.json`은 절대 추적하지 않음. `openclaw.template.json`만 관리. |

---

## CTO 종합 판정

### gate-decision

```yaml
gate: audit-cto
decision: PROCEED
baseline_scores:
  code_quality: 5.5
  security: 6.0
  architecture: 6.5
  db: N/A
  test_coverage: 1.0
  ux_ui: N/A
priority_items:
  p0:
    - {id: "TEST-001", title: "테스트 전무 - sync-timestamps.py에 대한 테스트 0개", area: "test"}
  p1:
    - {id: "CODE-001", title: "bare except (line 73)", area: "code_quality"}
    - {id: "CODE-002", title: "sys.argv 검증 미흡", area: "code_quality"}
    - {id: "SEC-001", title: "민감 파일 유입 가능성 (settings.json, memory 등 push)", area: "security"}
    - {id: "ARCH-001", title: "동시 실행 보호 없음 (lock file 미사용)", area: "architecture"}
  p2:
    - {id: "CODE-003", title: "main() 138줄 단일 블록", area: "code_quality"}
    - {id: "CODE-004", title: "에러 로깅 부재", area: "code_quality"}
    - {id: "CODE-005", title: "타입 힌트 미적용", area: "code_quality"}
    - {id: "SEC-002", title: "git 이력 민감값 유출 이력", area: "security"}
    - {id: "SEC-003", title: "openclaw.json 평문 토큰", area: "security"}
    - {id: "ARCH-002", title: "python3 직접 호출 vs CLAUDE.md NEVER 규칙", area: "architecture"}
    - {id: "ARCH-003", title: "Windows git reset --hard 위험", area: "architecture"}
  p3:
    - {id: "CODE-006", title: "import 문 스타일 비준수", area: "code_quality"}
    - {id: "CODE-007", title: "매직 넘버 3", area: "code_quality"}
    - {id: "CODE-008", title: "generate_state() find 비효율", area: "code_quality"}
    - {id: "ARCH-004", title: "타임스탬프 JSON 크기 증가", area: "architecture"}
    - {id: "SEC-004", title: ".gitignore vs tracked marketplaces 디렉토리", area: "security"}
improvement_scope:
  architecture: true
  db: false
  ux_ui: false
  estimated_effort: M
```

### 판정 근거

P0 (TEST-001: 테스트 전무)과 P1 4건이 존재하므로 **PROCEED**. 30분마다 cron으로 실행되는 프로덕션 스크립트에 테스트가 0개이며, bare except, race condition 등 안정성 리스크가 있어 개선이 필요하다.
