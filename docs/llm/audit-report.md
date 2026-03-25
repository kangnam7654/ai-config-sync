---
title: Audit Report — ai-config-sync
date: 2026-03-25
gate: PARTIAL
composite_score: 5.045
---

# Audit Report

## 대상 개요

| 항목 | 값 |
|------|-----|
| 프로젝트 | ai-config-sync |
| 경로 | /Users/kangnam/projects/ai-config-sync |
| 기술 스택 | Python 3 + Bash (표준 라이브러리만 사용) |
| 외부 의존성 | 없음 |
| DB | 없음 |
| UI | 없음 (CLI 전용) |
| 실행 방식 | 크론/Task Scheduler, 30분 주기 |
| 플랫폼 | macOS, Ubuntu, Windows (Git Bash) |
| 주요 파일 | sync-timestamps.py (264L), sync.sh (153L), setup.sh (145L), setup-mac.sh (64L), setup-windows.sh (44L) |

### 진단 범위

| 영역 | 실행 여부 |
|------|----------|
| 코드 품질 | O |
| 보안 | O |
| 아키텍처 | O |
| DB | X (없음) |
| 테스트 | O |
| Repo Health | O |
| UX/UI | X (없음) |

---

## 베이스라인 점수

| 영역 | 점수 | 가중치 | 가중 점수 |
|------|------|--------|----------|
| 코드 품질 | 5.4 | 25% | 1.35 |
| 보안 | 7.0 | 20% | 1.40 |
| 아키텍처 | 6.85 | 20% | 1.37 |
| 테스트 | 1.3 | 25% | 0.325 |
| Repo Health | 6.0 | 10% | 0.60 |
| DB | N/A | — | — |
| UX/UI | N/A | — | — |
| **총점** | — | **100%** | **5.045** |

**판정: FAIL** (기준: 총점 > 8.0 AND 주요 기준 >= 7)
**테스트(1.3)가 PRIMARY 기준이며 7.0 미만으로 FAIL.**

---

## 우선순위 매트릭스

### P0 — Critical (즉시, 1-2일)

| ID | 제목 | 영역 | 난이도 | 파일 |
|----|------|------|--------|------|
| TEST-001 | 테스트 인프라 구축 + 핵심 함수 테스트 | 테스트 | M | 신규: pyproject.toml, tests/test_sync.py |
| CODE-001 | bare except 제거 → 구체적 예외 타입 | 코드 품질 | S | sync-timestamps.py:73, :160 |
| CODE-002 | sys.argv 인덱스 범위 검사 추가 | 코드 품질 | S | sync-timestamps.py:127-128 |
| SEC-001 | hostname 인수 검증 (regex) | 보안 | S | sync-timestamps.py:128 |

### P1 — High (1주)

| ID | 제목 | 영역 | 난이도 | 파일 |
|----|------|------|--------|------|
| SEC-002 | 피어 파일 경로 경계 검증 (디렉토리 트래버설 차단) | 보안 | S | sync-timestamps.py:199-223 |
| SEC-003 | 크론 로그 파일 위치 및 권한 수정 (/tmp → $HOME, chmod 600) | 보안 | S | setup.sh:56, setup-windows.sh:33 |
| CODE-003 | sync.sh push 에러 핸들링 (2>/dev/null 제거, rebase abort 처리) | 코드 품질 | S | sync.sh:131-135 |
| SEC-004 | 피어 타임스탬프 데이터 검증 (타입, 범위, 미래값 거부) | 보안 | S | sync-timestamps.py:159, 183-185 |
| CODE-004 | unlink_if_file 삭제 실패 로깅 추가 | 코드 품질 | S | sync-timestamps.py:107-111 |

### P2 — Medium (2주)

| ID | 제목 | 영역 | 난이도 | 파일 |
|----|------|------|--------|------|
| ARCH-001 | CLAUDE_INCLUDES 단일 소스화 (sync-config.json) | 아키텍처 | M | sync-timestamps.py:27-30, setup.sh:75, setup-windows.sh:17 |
| CODE-005 | main() 함수 3개로 분리 (load_peer, sync_section, save_ts) | 코드 품질 | M | sync-timestamps.py:126-264 |
| REPO-001 | __pycache__ .pyc 파일 Git 추적 제거 | Repo Health | S | claude-code/skills/*/scripts/__pycache__/ |
| REPO-002 | CI/CD 파이프라인 구축 (GitHub Actions) | Repo Health | M | 신규: .github/workflows/test.yml |
| CODE-006 | setup-mac.sh/setup.sh openclaw.json 생성 로직 통합 | 코드 품질 | S | setup-mac.sh:31-36, setup.sh:111-114 |
| CODE-007 | 공개 함수 타입 어노테이션 추가 | 코드 품질 | S | sync-timestamps.py: git_cmd, git_bytes, walk_files |
| SEC-005 | openssl rand 토큰 임시 파일 권한 수정 (umask 077) | 보안 | S | setup.sh:111-114, setup-mac.sh:31-35 |

### P3 — Low (백로그)

| ID | 제목 | 영역 | 난이도 | 파일 |
|----|------|------|--------|------|
| REPO-003 | 대용량 미디어 파일 Git LFS 마이그레이션 | Repo Health | M | openclaw/workspace/video-pipeline/assets/*.mp4 |
| REPO-004 | 중첩 .git 정리 (submodule 또는 .gitignore) | Repo Health | M | claude-code/plugins/marketplaces/claude-plugins-official/ |
| CODE-008 | walk_files/walk_all_files 공통 이터레이터 추출 | 코드 품질 | S | sync-timestamps.py:77-102 |
| REPO-005 | 타임스탬프 JSON 보관 정책 (pruning) | Repo Health | S | timestamps/*.json |
| CODE-009 | generate_state() find 명령 기준 파일 가드 | 코드 품질 | S | sync.sh:68-70 |
| REPO-006 | sync 커밋 히스토리 경량화 전략 | Repo Health | L | Git history |
| CODE-010 | set -e와 || 패턴 혼용 정리 (if/else 구조로) | 코드 품질 | S | setup.sh:49-53, setup-windows.sh:32-40 |
| REPO-007 | pre-commit 훅 설정 | Repo Health | S | 신규: .pre-commit-config.yaml |

---

## 영역별 상세 진단

### 코드 품질 (5.4/10)

**에러 처리 (4/10)**: bare except 2건이 KeyboardInterrupt/SystemExit까지 삼킴. OSError pass로 삭제 실패 무시. sys.argv 미방어로 IndexError. push 실패 시 silent abort.

**코드 복잡도 (5/10)**: main() 140행, 중첩 5단계. 타임스탬프 로드/피어 감지/섹션별 병합/타임스탬프 저장이 단일 함수에 집중.

**코드 중복 (5/10)**: openclaw.json 생성 로직 2중복, schtasks 2중복, CLAUDE_INCLUDES 3곳 하드코딩.

**네이밍 (8/10)**: 전반적 일관성 양호.

**의존성 (9/10)**: 표준 라이브러리만 사용.

### 보안 (7.0/10)

**입력 검증 (5.0/10)**: hostname과 피어 파일 경로에 검증 없음. 경로 트래버설 가능. 피어 타임스탬프 무조건 신뢰.

**subprocess (9.0/10)**: git_cmd/git_bytes 모두 list 형태 + shell=False. 양호.

**민감 데이터 (8.0/10)**: 템플릿 패턴 잘 분리. openclaw.json 추적 금지 정상 동작.

**파일 시스템 (6.5/10)**: 크론 로그가 /tmp(world-readable)에 기록. 토큰 임시 파일 race condition.

### 아키텍처 (6.85/10)

**강점**: Bash(오케스트레이션)/Python(병합 로직) 계층 분리 명확. newest-wins 전략이 도메인에 적합. pathlib으로 크로스 플랫폼 호환.

**약점**: 확장성 5.5/10이 최대 병목. 동기화 대상 목록 4곳 중복. 새 섹션/플랫폼 추가 시 다수 파일 수정 필요. main() 모놀리스.

### 테스트 (1.3/10)

**커버리지 0%**. 테스트 파일, 테스트 프레임워크, CI 모두 부재. CLAUDE.md에 "직접 실행으로 확인" 명시 — 의도적이나 자동화 없음.

**테스트 가능성은 높음**: should_include(), migrate_ts_keys(), prune_empty_dirs() 등 순수 함수가 잘 분리되어 있어 pytest + tmp_path로 빠르게 추가 가능.

**테스트 작성 우선순위**: should_include > migrate_ts_keys > newest-wins 비교 > 삭제 전파 > prune_empty_dirs > mtime.

### Repo Health (6.0/10)

**CI/CD (4/10)**: 완전 부재. 760커밋 중 96%가 auto sync.

**파일 관리 (6/10)**: __pycache__ 27개 추적 위반, 미디어 11.8MB 직접 추적, 중첩 .git 43MB.

**브랜치 (8/10)**: 단일 main 브랜치, 동기화 프로젝트에 적절.

**보안 설정 (7/10)**: .gitignore 정책 양호하나 효과 불일치 있음.

---

## 개선 범위

design-loop에 전달할 개선 대상:

```yaml
improvement_scope:
  architecture: true    # CLAUDE_INCLUDES 단일소스화, main() 분리
  db: false             # DB 없음
  ux_ui: false          # UI 없음
  code_quality: true    # 에러 처리, 중복 제거, 복잡도 해소
  security: true        # 입력 검증, 경로 트래버설, 로그 권한
  test: true            # 테스트 인프라 + 핵심 테스트 작성 (최우선)
  repo_health: true     # __pycache__ 제거, CI/CD 구축
  estimated_effort: M   # P0+P1: 3-5일, P2 포함: 2주
```

---

## 제약 조건

1. **하위호환 필수**: sync.sh/sync-timestamps.py는 3개 플랫폼(macOS, Ubuntu, Windows)에서 크론으로 30분마다 실행 중. 스크립트 오류 시 동기화 즉시 중단됨.
2. **기존 타임스탬프 보존**: timestamps/*.json 구조 변경 시 기존 데이터와의 호환성 유지 필수. migrate_ts_keys() 패턴 활용.
3. **Windows 제약**: setup-windows.sh는 Git Bash에서 실행. Python 3 사용 가능하나 uv 미설치일 수 있음.
4. **테스트 프레임워크 신규 설치 필요**: pyproject.toml 생성 + pytest 의존성 추가 필요.
5. **sync.sh 자동 반영**: sync.sh 마지막에 git pull이 있어 코드 변경이 다음 실행 시 자동 반영됨 — 오류 있는 코드가 push되면 전 기기에 전파.
6. **git add 경로 제한**: sync.sh는 `openclaw/workspace claude-code timestamps state` 경로만 add함. 새 파일(tests/, .github/) 추가 시 별도 커밋 필요.

---

## 게이트 판정

```yaml
gate: audit-cto
decision: PARTIAL
reason: "P0(Critical) 4건 + P1(High) 5건 존재. 테스트 1.3/10이 최대 약점. P0+P1 해소 시 ~6.5-7.0, P2 완료 시 8.0 도달 가능."
baseline_scores:
  code_quality: 5.4
  security: 7.0
  architecture: 6.85
  db: N/A
  test_coverage: 1.3
  repo_health: 6.0
  ux_ui: N/A
priority_items:
  p0:
    - {id: "TEST-001", title: "테스트 인프라 구축 + 핵심 함수 테스트", area: "test", effort: "M"}
    - {id: "CODE-001", title: "bare except 제거", area: "code_quality", effort: "S"}
    - {id: "CODE-002", title: "sys.argv 인덱스 범위 검사", area: "code_quality", effort: "S"}
    - {id: "SEC-001", title: "hostname 인수 검증", area: "security", effort: "S"}
  p1:
    - {id: "SEC-002", title: "피어 파일 경로 경계 검증", area: "security", effort: "S"}
    - {id: "SEC-003", title: "크론 로그 파일 권한", area: "security", effort: "S"}
    - {id: "CODE-003", title: "push 에러 핸들링", area: "code_quality", effort: "S"}
    - {id: "SEC-004", title: "피어 타임스탬프 데이터 검증", area: "security", effort: "S"}
    - {id: "CODE-004", title: "unlink 삭제 실패 로깅", area: "code_quality", effort: "S"}
  p2:
    - {id: "ARCH-001", title: "CLAUDE_INCLUDES 단일소스화", area: "architecture", effort: "M"}
    - {id: "CODE-005", title: "main() 함수 분리", area: "code_quality", effort: "M"}
    - {id: "REPO-001", title: "__pycache__ 추적 제거", area: "repo_health", effort: "S"}
    - {id: "REPO-002", title: "CI/CD 파이프라인 구축", area: "repo_health", effort: "M"}
    - {id: "CODE-006", title: "setup 중복 제거", area: "code_quality", effort: "S"}
    - {id: "CODE-007", title: "타입 어노테이션 추가", area: "code_quality", effort: "S"}
    - {id: "SEC-005", title: "토큰 임시 파일 권한", area: "security", effort: "S"}
  p3:
    - {id: "REPO-003", title: "Git LFS 마이그레이션", area: "repo_health", effort: "M"}
    - {id: "REPO-004", title: "중첩 .git 정리", area: "repo_health", effort: "M"}
    - {id: "CODE-008", title: "walk 함수 통합", area: "code_quality", effort: "S"}
    - {id: "REPO-005", title: "타임스탬프 pruning", area: "repo_health", effort: "S"}
    - {id: "CODE-009", title: "find 명령 가드", area: "code_quality", effort: "S"}
    - {id: "REPO-006", title: "커밋 히스토리 경량화", area: "repo_health", effort: "L"}
    - {id: "CODE-010", title: "set-e 패턴 정리", area: "code_quality", effort: "S"}
    - {id: "REPO-007", title: "pre-commit 훅", area: "repo_health", effort: "S"}
improvement_scope:
  architecture: true
  db: false
  ux_ui: false
  estimated_effort: M
```
