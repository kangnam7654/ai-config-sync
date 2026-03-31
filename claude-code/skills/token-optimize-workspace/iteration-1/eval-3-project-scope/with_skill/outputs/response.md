# Token Optimization: Project CLAUDE.md

## Phase 1: Measurement

| Category | Tokens | Details |
|----------|--------|---------|
| Project CLAUDE.md | 1,105 | 67 lines [KR] |
| Project MEMORY.md | 189 | 0 lines |
| **TOTAL** | **1,294** | |

Optimization opportunity: Korean-to-English conversion on Project CLAUDE.md can save approximately **663 tokens (~60%)**.

---

## Phase 2: Proposed Optimization

**Technique: Korean to English conversion**

The project CLAUDE.md contains substantial Korean text. Converting to concise English preserves all semantic meaning and rules while reducing token consumption by ~60%.

### Diff Preview

```diff
 # CLAUDE.md

 This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

 ## Overview

-Ubuntu ↔ MacBook ↔ Windows 간 OpenClaw + Claude Code 설정을 양방향 동기화하는 프로젝트.
+Bidirectional sync of OpenClaw + Claude Code settings across Ubuntu, MacBook, and Windows.

 ## Commands

 ```bash
-# 동기화 실행 (전 플랫폼)
+# Run sync (all platforms)
 bash sync.sh

-# 동기화 핵심 로직만 실행 (디버깅용)
+# Run core sync logic only (for debugging)
 python3 sync-timestamps.py <sync_dir> <hostname>

-# 초기 설정 (최초 1회)
+# Initial setup (one-time)
 bash setup-mac.sh       # macOS/Ubuntu
 bash setup-windows.sh   # Windows (Git Bash)
 ```

-테스트 프레임워크 없음. 변경 시 `python3 sync-timestamps.py . $(hostname -s)` 로 직접 실행해서 확인.
+No test framework. Verify changes by running `python3 sync-timestamps.py . $(hostname -s)` directly.

 ## Architecture

-### 동기화 흐름 (`sync.sh` → `sync-timestamps.py`)
+### Sync Flow (`sync.sh` -> `sync-timestamps.py`)

-`sync.sh`가 30분마다 크론/Task Scheduler로 실행됨:
+`sync.sh` runs every 30 min via cron/Task Scheduler:

-1. `git fetch origin main` — remote 변경 가져오기
-2. `sync-timestamps.py` — FETCH_HEAD의 피어 타임스탬프와 로컬 mtime 비교, **newest-wins** 방식으로 파일별 병합
-3. `generate_state` — `state/{hostname}.md`에 기기 환경 정보 기록
-4. `git add` (동기화 산출물 경로만) → `git commit` → `git push` (Windows는 pull-only로 skip)
-5. `git pull --rebase` — 코드 변경 자동 반영 (Windows는 `git reset --hard origin/main`으로 대체)
+1. `git fetch origin main` — fetch remote changes
+2. `sync-timestamps.py` — compare peer timestamps from FETCH_HEAD with local mtime, **newest-wins** per-file merge
+3. `generate_state` — write device environment info to `state/{hostname}.md`
+4. `git add` (sync output paths only) -> `git commit` -> `git push` (Windows: pull-only, skip push)
+5. `git pull --rebase` — auto-apply code changes (Windows: `git reset --hard origin/main` instead)

-### `sync-timestamps.py` 핵심 구조
+### `sync-timestamps.py` Core Structure

-- `sections` dict: section key → `(로컬 경로, repo 하위 경로)` 튜플로 매핑
+- `sections` dict: section key -> `(local path, repo subpath)` tuple mapping
   - `workspace` → `(~/.openclaw/workspace, openclaw/workspace)`
   - `claude-code` → `(~/.claude, claude-code)`
-- 피어 타임스탬프는 `FETCH_HEAD`의 `timestamps/` 디렉토리에서 `git show`로 읽음 (working tree가 아닌 fetch된 상태 기준)
-- 파일별로 `our_file_ts` vs `peer_file_ts` 비교 → 피어가 최신이면 `git show`로 내용 가져와 로컬+repo 동시 갱신
-- `CLAUDE_INCLUDES` 화이트리스트로 claude-code 동기화 대상 제한
-- `EXCLUDES` 딕셔너리로 섹션별 제외 패턴 관리
-- `TS_KEY_MIGRATIONS`로 과거 키 이름 자동 마이그레이션
+- Peer timestamps read via `git show` from `FETCH_HEAD`'s `timestamps/` dir (fetched state, not working tree)
+- Per-file `our_file_ts` vs `peer_file_ts` comparison; if peer is newer, fetch content via `git show` and update both local + repo
+- `CLAUDE_INCLUDES` whitelist limits claude-code sync targets
+- `EXCLUDES` dict manages per-section exclusion patterns
+- `TS_KEY_MIGRATIONS` for automatic legacy key name migration

-## 플랫폼별 동기화 범위
+## Platform Sync Scope

-| 플랫폼 | OpenClaw | Claude Code |
+| Platform | OpenClaw | Claude Code |
 |---|---|---|
-| macOS (개인) | O | O |
-| Ubuntu (개인) | O | O |
-| Windows (회사) | X (보안) | O (pull-only) |
+| macOS (personal) | O | O |
+| Ubuntu (personal) | O | O |
+| Windows (work) | X (security) | O (pull-only) |

-- `~/.openclaw/workspace`이 없으면 OpenClaw 섹션은 자동 스킵됨
-- Windows는 pull-only: 피어 설정을 수신만 하고 push하지 않음
+- If `~/.openclaw/workspace` doesn't exist, OpenClaw section is auto-skipped
+- Windows is pull-only: receives peer settings but does not push

-## 코드 수정 시 주의사항
+## Code Modification Notes

-- `sync-timestamps.py` 수정 시: 모든 플랫폼에서 동작 확인 (pathlib 사용, `as_posix()`로 경로 통일)
-- Windows CP949 주의: `read_text()`/`write_text()`/`subprocess(text=True)` 에 `encoding="utf-8"` 필수
-- 새 동기화 대상 추가 시: `CLAUDE_INCLUDES` 또는 `sections` dict 수정. `setup-windows.sh`의 복사 항목 리스트도 함께 갱신 필요
-- 크론/Task Scheduler가 30분마다 `sync.sh`를 실행 중 — 스크립트 오류 시 동기화 중단됨
-- `sync.sh` 마지막에 `git pull`이 있어 코드 변경이 다음 실행 시 자동 반영됨
-- `sync.sh`는 `git add .`를 쓰지 않고 `openclaw/workspace claude-code timestamps state` 경로만 add함
-- 민감값이 포함된 `openclaw/openclaw.json`은 추적 금지 (`openclaw.template.json`만 관리)
+- When modifying `sync-timestamps.py`: verify on all platforms (use pathlib, unify paths with `as_posix()`)
+- Windows CP949 caveat: `encoding="utf-8"` required for `read_text()`/`write_text()`/`subprocess(text=True)`
+- When adding new sync targets: modify `CLAUDE_INCLUDES` or `sections` dict. Also update copy list in `setup-windows.sh`
+- cron/Task Scheduler runs `sync.sh` every 30 min — script errors halt sync
+- `sync.sh` ends with `git pull` so code changes auto-apply on next run
+- `sync.sh` does not use `git add .`; only adds `openclaw/workspace claude-code timestamps state` paths
+- `openclaw/openclaw.json` contains secrets — do not track (only `openclaw.template.json` is tracked)
```

### Estimated Token Savings

| Category | Before | After (est.) | Saved |
|----------|--------|-------------|-------|
| Project CLAUDE.md | 1,105 | ~442 | ~663 (~60%) |

---

## Next Steps

This is a **dry-run preview** -- no files were modified. To apply these changes:
1. Confirm you want to proceed with the Korean-to-English conversion
2. I will apply the changes to `/Users/kangnam/projects/ai-config-sync/CLAUDE.md`
3. Re-run measurement to verify actual savings

Proceed? (yes/no)
