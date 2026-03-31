# Token Optimization Report (--global)

## Phase 1: Measurement

| Category | Tokens | Details |
|----------|--------|---------|
| Agent descriptions | 1,576 | 33 items |
| Skill descriptions | 2,223 | 42 items |
| Global CLAUDE.md | 1,742 | 163 lines |
| Project CLAUDE.md | 1,105 | 67 lines [KR] |
| Project MEMORY.md | 189 | 5 entries |
| **TOTAL** | **6,835** | |

---

## Phase 2: Optimization Opportunities

The measurement script identified 2 optimization opportunities. The global CLAUDE.md is already in English (previously optimized), so the remaining savings are smaller but still worthwhile.

### Opportunity 1: Agent Description Compression -- `refactor-cleaner` (~36 tokens)

**Current value** (116 tokens):
```
"[Refactor] Dead code cleanup and consolidation specialist. Use PROACTIVELY for removing unused code, duplicates, and refactoring.\n\nExamples:\n- \"Clean up unused code\" → Launch refactor-cleaner\n- \"Find and remove dead code\" → Launch refactor-cleaner\n- \"Consolidate duplicate utilities\" → Launch refactor-cleaner"
```

**Proposed value** (~40 tokens):
```
"[Refactor] Dead code cleanup and consolidation — removes unused code, duplicates, and unused dependencies. Architectural refactoring → cto."
```

**Rationale**: The Examples section repeats the same routing information already conveyed by the first sentence. Removing it and adding the one useful routing hint (cto for architectural refactoring) preserves all routing information in a fraction of the tokens.

**Estimated savings**: ~76 tokens

**File**: `/Users/kangnam/.claude/agents/refactor-cleaner.md` (line 3, `description` field)

---

### Opportunity 2: Project CLAUDE.md Korean-to-English (~663 tokens)

The project CLAUDE.md at `/Users/kangnam/projects/ai-config-sync/CLAUDE.md` contains Korean text that costs 2-4x more tokens than equivalent English. Here is the proposed English version:

**Current value** (1,105 tokens, 67 lines):
```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Ubuntu ↔ MacBook ↔ Windows 간 OpenClaw + Claude Code 설정을 양방향 동기화하는 프로젝트.

## Commands

\```bash
# 동기화 실행 (전 플랫폼)
bash sync.sh

# 동기화 핵심 로직만 실행 (디버깅용)
python3 sync-timestamps.py <sync_dir> <hostname>

# 초기 설정 (최초 1회)
bash setup-mac.sh       # macOS/Ubuntu
bash setup-windows.sh   # Windows (Git Bash)
\```

테스트 프레임워크 없음. 변경 시 `python3 sync-timestamps.py . $(hostname -s)` 로 직접 실행해서 확인.

## Architecture

### 동기화 흐름 (`sync.sh` → `sync-timestamps.py`)

`sync.sh`가 30분마다 크론/Task Scheduler로 실행됨:

1. `git fetch origin main` — remote 변경 가져오기
2. `sync-timestamps.py` — FETCH_HEAD의 피어 타임스탬프와 로컬 mtime 비교, **newest-wins** 방식으로 파일별 병합
3. `generate_state` — `state/{hostname}.md`에 기기 환경 정보 기록
4. `git add` (동기화 산출물 경로만) → `git commit` → `git push` (Windows는 pull-only로 skip)
5. `git pull --rebase` — 코드 변경 자동 반영 (Windows는 `git reset --hard origin/main`으로 대체)

### `sync-timestamps.py` 핵심 구조

- `sections` dict: section key → `(로컬 경로, repo 하위 경로)` 튜플로 매핑
  ...
\```
(full Korean content continues)
```

**Proposed value** (~442 tokens, 67 lines):
```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Bidirectional sync of OpenClaw + Claude Code settings across Ubuntu, MacBook, and Windows.

## Commands

\```bash
# Run sync (all platforms)
bash sync.sh

# Run core sync logic only (debugging)
python3 sync-timestamps.py <sync_dir> <hostname>

# Initial setup (one-time)
bash setup-mac.sh       # macOS/Ubuntu
bash setup-windows.sh   # Windows (Git Bash)
\```

No test framework. Verify changes by running `python3 sync-timestamps.py . $(hostname -s)` directly.

## Architecture

### Sync flow (`sync.sh` → `sync-timestamps.py`)

`sync.sh` runs every 30 minutes via cron/Task Scheduler:

1. `git fetch origin main` — fetch remote changes
2. `sync-timestamps.py` — compare peer timestamps from FETCH_HEAD with local mtime, **newest-wins** per-file merge
3. `generate_state` — write device environment info to `state/{hostname}.md`
4. `git add` (sync output paths only) → `git commit` → `git push` (Windows: pull-only, skip push)
5. `git pull --rebase` — auto-apply code changes (Windows: `git reset --hard origin/main` instead)

### `sync-timestamps.py` core structure

- `sections` dict: section key → `(local path, repo subpath)` tuple mapping
  - `workspace` → `(~/.openclaw/workspace, openclaw/workspace)`
  - `claude-code` → `(~/.claude, claude-code)`
- Peer timestamps read from `FETCH_HEAD`'s `timestamps/` directory via `git show` (fetched state, not working tree)
- Per-file comparison: `our_file_ts` vs `peer_file_ts` → if peer is newer, fetch content via `git show` and update both local + repo
- `CLAUDE_INCLUDES` whitelist limits claude-code sync targets
- `EXCLUDES` dict manages per-section exclusion patterns
- `TS_KEY_MIGRATIONS` for automatic legacy key name migration

## Platform sync scope

| Platform | OpenClaw | Claude Code |
|---|---|---|
| macOS (personal) | O | O |
| Ubuntu (personal) | O | O |
| Windows (work) | X (security) | O (pull-only) |

- If `~/.openclaw/workspace` does not exist, the OpenClaw section is auto-skipped
- Windows is pull-only: receives peer settings only, does not push

## Code modification notes

- When modifying `sync-timestamps.py`: verify on all platforms (use pathlib, unify paths with `as_posix()`)
- Windows CP949 caution: always pass `encoding="utf-8"` to `read_text()`/`write_text()`/`subprocess(text=True)`
- When adding new sync targets: modify `CLAUDE_INCLUDES` or `sections` dict. Also update the copy list in `setup-windows.sh`
- cron/Task Scheduler runs `sync.sh` every 30 min — script errors halt sync
- `sync.sh` ends with `git pull`, so code changes auto-apply on next run
- `sync.sh` does not use `git add .` — only adds `openclaw/workspace claude-code timestamps state` paths
- `openclaw/openclaw.json` contains sensitive values — do not track (only `openclaw.template.json` is managed)
```

**Estimated savings**: ~663 tokens (from 1,105 to ~442)

**File**: `/Users/kangnam/projects/ai-config-sync/CLAUDE.md`

---

### Memory Cleanup Notes

Reviewed all 4 project memory files. No stale or expired items found:

| Memory file | Type | Status |
|-------------|------|--------|
| `feedback_naming_convention.md` | feedback | Active -- ongoing convention |
| `reference_llm_provider_auth.md` | reference | Active -- reference pointer |
| `project_ui_review_rename.md` | project | Active -- has incomplete items |
| `feedback_agent_skill_creation.md` | feedback | Active -- ongoing rule |

No `temp` type memories with expired conditions. No non-memory files found in the memory directory.

### Duplicate Detection

No obvious duplicate skills/agents detected. All 33 agents and 42 skills serve distinct purposes.

---

## Phase 3: Projected Summary

If all proposed changes were applied:

```
Token Optimization Report
═══════════════════════════════════════════════════
Category              Before    After    Saved
───────────────────────────────────────────────────
Agent descriptions     1,576    1,500      -76
Skill descriptions     2,223    2,223        0
Global CLAUDE.md       1,742    1,742        0
Project CLAUDE.md      1,105      442     -663
Project MEMORY.md        189      189        0
───────────────────────────────────────────────────
TOTAL                  6,835    6,096     -739
```

**Total savings: ~739 tokens (10.8% reduction)**

---

## Action Items (Dry Run -- No Changes Made)

This is a **dry-run evaluation**. No files were modified. To apply these optimizations:

1. **Agent description compression** (`refactor-cleaner`): Approve to compress the description by removing the Examples section. Saves ~76 tokens.
2. **Project CLAUDE.md Korean→English**: Approve to translate all Korean content to concise English. Saves ~663 tokens.

Note: The global CLAUDE.md (1,742 tokens) is already in English and was previously optimized. No further savings identified there.
