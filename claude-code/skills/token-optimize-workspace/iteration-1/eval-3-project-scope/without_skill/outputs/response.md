# 프로젝트 CLAUDE.md 토큰 최적화 분석

## 현황

- 파일: `/Users/kangnam/projects/ai-config-sync/CLAUDE.md`
- 크기: 3,204 bytes / 67줄 / 404단어
- 추정 토큰: 약 1,500-1,800 토큰 (한국어+영어+코드 혼합 기준)

## 최적화 전략

이 문서는 이미 비교적 간결하지만, 아래 변경으로 약 30-40% 토큰 절감이 가능하다.

---

### 1. 제거 대상: 불필요한 보일러플레이트 (약 50토큰 절감)

**현재:**
```
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
```

**변경:** 첫 줄 설명 문장을 삭제한다. Claude Code는 CLAUDE.md의 용도를 이미 알고 있으므로 이 설명은 토큰 낭비다.

**변경 후:**
```
# ai-config-sync
```

---

### 2. Commands 섹션 압축 (약 100토큰 절감)

**현재 (12줄):**
````
## Commands

```bash
# 동기화 실행 (전 플랫폼)
bash sync.sh

# 동기화 핵심 로직만 실행 (디버깅용)
python3 sync-timestamps.py <sync_dir> <hostname>

# 초기 설정 (최초 1회)
bash setup-mac.sh       # macOS/Ubuntu
bash setup-windows.sh   # Windows (Git Bash)
```

테스트 프레임워크 없음. 변경 시 `python3 sync-timestamps.py . $(hostname -s)` 로 직접 실행해서 확인.
````

**변경 후 (5줄):** 코드 블록을 제거하고 인라인으로 압축한다. 주석은 LLM이 코드 자체에서 추론 가능하므로 제거한다.

```
## Commands

- 동기화: `bash sync.sh`
- 디버깅: `python3 sync-timestamps.py <sync_dir> <hostname>`
- 초기 설정: `bash setup-mac.sh` (macOS/Ubuntu), `bash setup-windows.sh` (Windows)
- 테스트: 프레임워크 없음. `python3 sync-timestamps.py . $(hostname -s)`로 직접 확인
```

---

### 3. Architecture 섹션 압축 (약 250토큰 절감)

이 섹션이 가장 토큰을 많이 소비한다. 코드에서 직접 읽을 수 있는 정보(변수명, 함수명)와 설명이 중복된다.

**현재 "동기화 흐름" (8줄):**
```
`sync.sh`가 30분마다 크론/Task Scheduler로 실행됨:

1. `git fetch origin main` — remote 변경 가져오기
2. `sync-timestamps.py` — FETCH_HEAD의 피어 타임스탬프와 로컬 mtime 비교, **newest-wins** 방식으로 파일별 병합
3. `generate_state` — `state/{hostname}.md`에 기기 환경 정보 기록
4. `git add` (동기화 산출물 경로만) → `git commit` → `git push` (Windows는 pull-only로 skip)
5. `git pull --rebase` — 코드 변경 자동 반영 (Windows는 `git reset --hard origin/main`으로 대체)
```

**변경 후 (3줄):** `sync.sh`를 읽으면 파악 가능한 상세 단계를 제거하고, 핵심 동작 원리만 남긴다.

```
`sync.sh`가 크론/Task Scheduler로 30분 주기 실행: fetch → `sync-timestamps.py`(newest-wins 병합) → `generate_state` → commit/push (Windows는 pull-only).
코드 변경은 마지막 `git pull --rebase`로 다음 실행 시 자동 반영 (Windows는 `git reset --hard origin/main`).
```

**현재 "핵심 구조" (7줄):**
```
- `sections` dict: section key → `(로컬 경로, repo 하위 경로)` 튜플로 매핑
  - `workspace` → `(~/.openclaw/workspace, openclaw/workspace)`
  - `claude-code` → `(~/.claude, claude-code)`
- 피어 타임스탬프는 `FETCH_HEAD`의 `timestamps/` 디렉토리에서 `git show`로 읽음 (working tree가 아닌 fetch된 상태 기준)
- 파일별로 `our_file_ts` vs `peer_file_ts` 비교 → 피어가 최신이면 `git show`로 내용 가져와 로컬+repo 동시 갱신
- `CLAUDE_INCLUDES` 화이트리스트로 claude-code 동기화 대상 제한
- `EXCLUDES` 딕셔너리로 섹션별 제외 패턴 관리
- `TS_KEY_MIGRATIONS`로 과거 키 이름 자동 마이그레이션
```

**변경 후 (4줄):** `sections` dict의 구체적 매핑 값은 코드에서 직접 확인 가능하므로 제거. 타임스탬프 비교 메커니즘도 한 줄로 압축.

```
- `sections` dict: section key → `(로컬 경로, repo 하위 경로)` 매핑
- 피어 타임스탬프는 `FETCH_HEAD`의 `timestamps/`에서 `git show`로 읽어 로컬 mtime과 비교, 피어가 최신이면 `git show`로 가져와 로컬+repo 동시 갱신
- `CLAUDE_INCLUDES`(화이트리스트), `EXCLUDES`(섹션별 제외), `TS_KEY_MIGRATIONS`(키 이름 마이그레이션) 참고
```

---

### 4. 플랫폼별 동기화 범위 테이블 압축 (약 80토큰 절감)

**현재 (9줄):**
```
| 플랫폼 | OpenClaw | Claude Code |
|---|---|---|
| macOS (개인) | O | O |
| Ubuntu (개인) | O | O |
| Windows (회사) | X (보안) | O (pull-only) |

- `~/.openclaw/workspace`이 없으면 OpenClaw 섹션은 자동 스킵됨
- Windows는 pull-only: 피어 설정을 수신만 하고 push하지 않음
```

**변경 후 (3줄):** 마크다운 테이블은 토큰 비용이 높다. 산문으로 같은 정보를 전달한다.

```
- macOS/Ubuntu: OpenClaw + Claude Code 양방향 동기화
- Windows: Claude Code만 pull-only (OpenClaw은 보안상 제외)
- `~/.openclaw/workspace` 부재 시 OpenClaw 섹션 자동 스킵
```

---

### 5. 코드 수정 시 주의사항 압축 (약 120토큰 절감)

**현재 (7줄):**
```
- `sync-timestamps.py` 수정 시: 모든 플랫폼에서 동작 확인 (pathlib 사용, `as_posix()`로 경로 통일)
- Windows CP949 주의: `read_text()`/`write_text()`/`subprocess(text=True)` 에 `encoding="utf-8"` 필수
- 새 동기화 대상 추가 시: `CLAUDE_INCLUDES` 또는 `sections` dict 수정. `setup-windows.sh`의 복사 항목 리스트도 함께 갱신 필요
- 크론/Task Scheduler가 30분마다 `sync.sh`를 실행 중 — 스크립트 오류 시 동기화 중단됨
- `sync.sh` 마지막에 `git pull`이 있어 코드 변경이 다음 실행 시 자동 반영됨
- `sync.sh`는 `git add .`를 쓰지 않고 `openclaw/workspace claude-code timestamps state` 경로만 add함
- 민감값이 포함된 `openclaw/openclaw.json`은 추적 금지 (`openclaw.template.json`만 관리)
```

**변경 후 (5줄):** Architecture에서 이미 언급된 내용(pull, 30분 주기)을 중복 제거하고, 핵심 제약만 남긴다.

```
- 크로스 플랫폼: pathlib + `as_posix()` 사용. Windows는 모든 파일 I/O와 subprocess에 `encoding="utf-8"` 필수
- 동기화 대상 추가: `CLAUDE_INCLUDES`/`sections` dict + `setup-windows.sh` 복사 리스트 함께 수정
- git add 범위: `openclaw/workspace claude-code timestamps state` 경로만 (`git add .` 금지)
- `openclaw/openclaw.json` 추적 금지 (민감값). `openclaw.template.json`만 관리
```

---

## 최적화 결과 요약

| 섹션 | 현재 줄 수 | 변경 후 줄 수 | 절감 |
|------|-----------|-------------|------|
| 헤더/보일러플레이트 | 3 | 1 | -2 |
| Commands | 12 | 5 | -7 |
| Architecture - 흐름 | 8 | 2 | -6 |
| Architecture - 구조 | 7 | 3 | -4 |
| 플랫폼별 범위 | 9 | 3 | -6 |
| 주의사항 | 7 | 4 | -3 |
| **합계** | **67** | **약 38** | **약 43% 줄 수 감소** |

추정 토큰 절감: 약 500-600 토큰 (전체의 30-40%)

## 최적화된 전체 문서 (제안)

```markdown
# ai-config-sync

Ubuntu/MacBook/Windows 간 OpenClaw + Claude Code 설정을 양방향 동기화하는 프로젝트.

## Commands

- 동기화: `bash sync.sh`
- 디버깅: `python3 sync-timestamps.py <sync_dir> <hostname>`
- 초기 설정: `bash setup-mac.sh` (macOS/Ubuntu), `bash setup-windows.sh` (Windows)
- 테스트: 프레임워크 없음. `python3 sync-timestamps.py . $(hostname -s)`로 직접 확인

## Architecture

`sync.sh`가 크론/Task Scheduler로 30분 주기 실행: fetch → `sync-timestamps.py`(newest-wins 병합) → `generate_state` → commit/push (Windows는 pull-only).
코드 변경은 마지막 `git pull --rebase`로 다음 실행 시 자동 반영 (Windows는 `git reset --hard origin/main`).

### `sync-timestamps.py` 핵심 구조

- `sections` dict: section key → `(로컬 경로, repo 하위 경로)` 매핑
- 피어 타임스탬프는 `FETCH_HEAD`의 `timestamps/`에서 `git show`로 읽어 로컬 mtime과 비교, 피어가 최신이면 `git show`로 가져와 로컬+repo 동시 갱신
- `CLAUDE_INCLUDES`(화이트리스트), `EXCLUDES`(섹션별 제외), `TS_KEY_MIGRATIONS`(키 이름 마이그레이션) 참고

### 플랫폼별 동기화 범위

- macOS/Ubuntu: OpenClaw + Claude Code 양방향 동기화
- Windows: Claude Code만 pull-only (OpenClaw은 보안상 제외)
- `~/.openclaw/workspace` 부재 시 OpenClaw 섹션 자동 스킵

## 코드 수정 시 주의사항

- 크로스 플랫폼: pathlib + `as_posix()` 사용. Windows는 모든 파일 I/O와 subprocess에 `encoding="utf-8"` 필수
- 동기화 대상 추가: `CLAUDE_INCLUDES`/`sections` dict + `setup-windows.sh` 복사 리스트 함께 수정
- git add 범위: `openclaw/workspace claude-code timestamps state` 경로만 (`git add .` 금지)
- `openclaw/openclaw.json` 추적 금지 (민감값). `openclaw.template.json`만 관리
```

## 적용 방법

위 변경을 `/Users/kangnam/projects/ai-config-sync/CLAUDE.md`에 적용하면 된다. 정보 손실 없이 토큰만 줄이는 방향이며, 코드에서 직접 확인 가능한 중복 정보(변수명, 단계별 git 명령 등)를 제거하고, 마크다운 테이블을 산문 리스트로 대체하는 것이 핵심이다.
