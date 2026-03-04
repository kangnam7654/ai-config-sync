# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Ubuntu ↔ MacBook ↔ Windows 간 OpenClaw + Claude Code 설정을 양방향 동기화하는 프로젝트.

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

## Architecture

### 동기화 흐름 (`sync.sh` → `sync-timestamps.py`)

`sync.sh`가 30분마다 크론/Task Scheduler로 실행됨:

1. `git fetch origin main` — remote 변경 가져오기
2. `sync-timestamps.py` — FETCH_HEAD의 피어 타임스탬프와 로컬 mtime 비교, **newest-wins** 방식으로 파일별 병합
3. `generate_state` — `state/{hostname}.md`에 기기 환경 정보 기록
4. `git add` (동기화 산출물 경로만) → `git commit` → `git push` (Windows는 pull-only로 skip)
5. `git pull --rebase` — 코드 변경 자동 반영

### `sync-timestamps.py` 핵심 구조

- `sections` dict: section key → `(로컬 경로, repo 하위 경로)` 튜플로 매핑
  - `workspace` → `(~/.openclaw/workspace, openclaw/workspace)`
  - `claude-code` → `(~/.claude, claude-code)`
- 피어 타임스탬프는 `FETCH_HEAD`의 `timestamps/` 디렉토리에서 `git show`로 읽음 (working tree가 아닌 fetch된 상태 기준)
- 파일별로 `our_file_ts` vs `peer_file_ts` 비교 → 피어가 최신이면 `git show`로 내용 가져와 로컬+repo 동시 갱신
- `CLAUDE_INCLUDES` 화이트리스트로 claude-code 동기화 대상 제한
- `EXCLUDES` 딕셔너리로 섹션별 제외 패턴 관리
- `TS_KEY_MIGRATIONS`로 과거 키 이름 자동 마이그레이션

## 플랫폼별 동기화 범위

| 플랫폼 | OpenClaw | Claude Code |
|---|---|---|
| macOS (개인) | O | O |
| Ubuntu (개인) | O | O |
| Windows (회사) | X (보안) | O (pull-only) |

- `~/.openclaw`이 없으면 OpenClaw 섹션은 자동 스킵됨
- Windows는 pull-only: 피어 설정을 수신만 하고 push하지 않음

## 코드 수정 시 주의사항

- `sync-timestamps.py` 수정 시: 모든 플랫폼에서 동작 확인 (pathlib 사용, `as_posix()`로 경로 통일)
- Windows CP949 주의: `read_text()`/`write_text()`/`subprocess(text=True)` 에 `encoding="utf-8"` 필수
- 새 동기화 대상 추가 시: `CLAUDE_INCLUDES` 또는 `sections` dict 수정. `setup-windows.sh`의 복사 항목 리스트도 함께 갱신 필요
- 크론/Task Scheduler가 30분마다 `sync.sh`를 실행 중 — 스크립트 오류 시 동기화 중단됨
- `sync.sh` 마지막에 `git pull`이 있어 코드 변경이 다음 실행 시 자동 반영됨
- `sync.sh`는 `git add .`를 쓰지 않고 `openclaw/workspace claude-code timestamps state` 경로만 add함
- 민감값이 포함된 `openclaw/openclaw.json`은 추적 금지 (`openclaw.template.json`만 관리)
