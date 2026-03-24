# ai-config-sync Audit Report

> Audit date: 2026-03-24
> Repo: `git@github.com:kangnam7654/ai-config-sync.git`
> Branch: `main`
> Total commits: 729 (700 auto-sync, 29 manual)
> Tracked files: 1,682
> Project size: 140 MB (working tree) / 66 MB (.git)

---

## 1. Executive Summary

ai-config-sync is a cross-platform (macOS/Ubuntu/Windows) configuration synchronization tool for OpenClaw workspace and Claude Code settings. It operates on a 30-minute cron cycle using a "newest-wins" file-level merge strategy.

The project functions correctly for its core purpose but has accumulated significant technical debt, primarily: tracked binary files inflating the repo, no automated tests, no concurrent-execution protection, and stale artifacts from hostname changes.

**Severity legend:** CRITICAL = data loss or security risk, HIGH = significant operational impact, MEDIUM = maintainability/efficiency concern, LOW = cosmetic or minor.

---

## 2. Security

### 2.1 [MEDIUM] `installed_plugins.json` exposes local filesystem paths

File: `/Users/kangnam/projects/ai-config-sync/claude-code/plugins/installed_plugins.json`

Contains 5 hardcoded absolute paths (e.g., `/Users/kangnam/.claude/plugins/cache/...`). These are synced across devices where the paths will differ. Not a direct security breach, but leaks the local directory structure to the repo.

**Recommendation:** Add `claude-code/plugins/installed_plugins.json` and `claude-code/plugins/install-counts-cache.json` to `.gitignore`, or strip local paths during sync.

### 2.2 [LOW] `settings.json` references non-synced symlinks

`settings.json` references `~/.claude/log-session.sh` and `~/.claude/statusline.sh`, which are symlinks to `~/projects/claude-code-hud/` -- a separate project not managed by this repo. These hooks will silently fail on devices without that project.

**Recommendation:** Either sync these scripts or add a fallback/existence check in the hook definitions.

### 2.3 [LOW] README example contains placeholder API key

Line 55 of `README.md`: `openclaw onboard --anthropic-api-key 'sk-ant-...'`. This is clearly a placeholder (not a real key), but could confuse contributors. Acceptable as-is.

---

## 3. Repository Health

### 3.1 [CRITICAL] Large binary files tracked in git -- 35+ MB

| Category | Count | Total Size | Path Pattern |
|---|---|---|---|
| Font files (.ttf) | 108 | 10.3 MB | `*/canvas-fonts/*.ttf` (duplicated in claude-code + openclaw) |
| Video/Audio (.mp4, .mp3) | 4 | 12.0 MB | `openclaw/workspace/video-pipeline/assets/` |
| Screenshots (.png) | 12+ | 13.4 MB | scattered across docs/, skills/, openclaw/ |

Additionally, the git history contains blobs from a previously removed `workspace/tools/flutter/` directory (NotoColorEmoji.ttf at 4.7 MB, other Flutter files). A `git filter-repo` was already run (evidence in `.git/filter-repo/`) but these objects persist in the pack file.

**Impact:** Clone time, disk usage, and sync overhead are all inflated. Every 30-minute sync commit potentially re-hashes these large files.

**Recommendation:**
1. Add `*.mp4`, `*.mp3`, `*.ttf` to `.gitignore` (or use Git LFS for fonts if they must be tracked).
2. Remove `openclaw/workspace/video-pipeline/assets/` from tracking -- these are content files, not configuration.
3. The 54 duplicate font files between `claude-code/skills/canvas-design/canvas-fonts/` and `openclaw/workspace/skills/canvas-design/canvas-fonts/` are byte-identical. Consider tracking them in only one location.

### 3.2 [HIGH] Timestamp JSON files grow unbounded and churn history

| File | Current Size |
|---|---|
| `Kangnamui-MacBookPro.json` | 220 KB (2,295 lines) |
| `Kangnamui-Macmini.json` | 212 KB |
| `kangnam-Desktop-Ubuntu.json` | 62 KB |

These files are rewritten every 30 minutes. Over 729 commits, the Ubuntu file alone has generated ~1.8 MB blobs repeated hundreds of times in git history. This is the primary driver of the 66 MB `.git` directory.

**Recommendation:** Consider storing timestamps outside git (e.g., as git notes, or in a separate branch that gets force-pushed), or squash old sync commits periodically.

### 3.3 [MEDIUM] Stale state file: `state/192.md`

`state/192.md` was generated when a Mac mini resolved its hostname as `192` (likely a network configuration issue where `hostname -s` returned an IP prefix). The corresponding `timestamps/192.json` was cleaned up, but `state/192.md` remains tracked.

**Recommendation:** Remove `state/192.md` from tracking.

### 3.4 [LOW] Untracked docs files in working tree

Three files sit untracked in `docs/`:
- `docs/auto-dev-design-decisions.md`
- `docs/auto-dev-workflow.mmd`
- `docs/auto-dev-workflow.png`

These appear to be design documents from the auto-dev skill development. They should either be committed or added to `.gitignore`.

### 3.5 [LOW] Placeholder docs

- `docs/taskflow/design.md`: "# mock design doc for test"
- `docs/taskflow/spec.md`: "# mock spec doc for test"

These are placeholder stubs with no real content. Should be removed or completed.

---

## 4. Code Quality: `sync-timestamps.py`

### 4.1 [HIGH] Bare `except:` clause (line 73)

```python
def mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except:
        return 0.0
```

A bare `except:` catches `KeyboardInterrupt` and `SystemExit`, masking critical errors. Should be `except OSError:`.

### 4.2 [MEDIUM] No input validation on `sys.argv`

`main()` directly accesses `sys.argv[1]` and `sys.argv[2]` without checking argument count. A missing argument produces an unhelpful `IndexError` traceback.

**Recommendation:** Add argument validation with a usage message.

### 4.3 [MEDIUM] `git_bytes` does not check `encoding` for Windows CP949

`git_bytes()` (line 65-67) runs without `encoding` parameter, which is intentional for binary content. However, the same function is used at line 216-218 to fetch file content that may include text files. On Windows, `subprocess.run` without `encoding` will use the system default. Since the content is written as raw bytes via `write_bytes()`, this is technically correct -- but the asymmetry between `git_cmd` (has encoding) and `git_bytes` (no encoding) could confuse future maintainers.

### 4.4 [LOW] No type annotations on most functions

Functions like `git_cmd`, `git_bytes`, `should_include` lack return type annotations. The codebase already uses `dict` type hints in some places but inconsistently.

### 4.5 [LOW] `walk_files` and `walk_all_files` share nearly identical traversal logic

Both functions walk a directory excluding `.git`. The only difference is whether `should_include` is applied and what is returned. A small DRY opportunity.

---

## 5. Code Quality: `sync.sh`

### 5.1 [HIGH] No concurrent execution guard

The cron job runs every 30 minutes. If a previous run is still executing (e.g., slow network, large diff), a second instance will start and both will attempt `git commit` / `git push`, likely causing conflicts or data corruption.

**Recommendation:** Add a `flock` or PID-file guard at the top:
```bash
LOCKFILE="/tmp/ai-config-sync.lock"
exec 200>"$LOCKFILE"
flock -n 200 || { echo "Another sync is running"; exit 0; }
```

### 5.2 [MEDIUM] `set -e` with `git push` fallback is fragile

Line 126: `if ! git push origin main 2>/dev/null; then` -- the `2>/dev/null` suppresses all push error output, making it impossible to diagnose failures. If the rebase-retry also fails, the error message is lost.

**Recommendation:** Log stderr to a file or print it on failure.

### 5.3 [MEDIUM] `git add -A` scoping includes unintended files

Line 120: `git add -A openclaw/workspace claude-code timestamps state`

The `-A` flag with path arguments adds all changes (including new untracked files) under those paths. This means any file dropped into `openclaw/workspace/` (such as `.html`, `.py`, `.mp4` files) gets automatically tracked. This is how video-pipeline assets ended up in git.

**Recommendation:** Either tighten the `-A` scope to specific subdirectories, or add exclusion patterns to `.gitignore` for file types that should not be synced (e.g., `*.mp4`, `*.mp3`, `*.html`).

### 5.4 [MEDIUM] `generate_state` uses `find` with `-newer` which may fail silently

Line 63-65: The `find` command references `$HOME/.openclaw/workspace/MEMORY.md`. If this file does not exist, `find` will error silently and `RECENT_FILES` will be empty. Not harmful but misleading.

### 5.5 [LOW] OpenClaw/Claude version detection always shows "N/A"

All three state files show `Version: N/A` for OpenClaw, Claude Code, and Model. The `openclaw --version` and `claude --version` commands are not found. This section provides no useful information.

**Recommendation:** Update the version detection logic or remove these fields until the tools are installed.

---

## 6. Code Quality: Setup Scripts

### 6.1 [LOW] `setup-mac.sh` does not handle the Claude Code sync

`setup-mac.sh` only sets up OpenClaw. Claude Code settings are not restored by this script. The Windows `setup-windows.sh` does handle Claude Code restoration.

**Recommendation:** Add Claude Code restoration to `setup-mac.sh` or document the gap.

### 6.2 [LOW] `setup-windows.sh` hardcoded item list may drift

Line 17 of `setup-windows.sh` has a hardcoded list: `CLAUDE.md settings.json agents plugins skills agent-memory memory todos teams stop-hook-git-check.sh`. This must be manually kept in sync with `CLAUDE_INCLUDES` in `sync-timestamps.py`. No enforcement mechanism exists.

---

## 7. Architecture

### 7.1 [MEDIUM] No test suite

The project has zero automated tests. The CLAUDE.md explicitly notes "no test framework." Given that `sync-timestamps.py` handles bidirectional file synchronization with conflict resolution, this is the highest-risk area for regressions.

The `sync-timestamps.py` file has 265 lines of logic including file I/O, git operations, timestamp comparison, and include/exclude filtering -- all highly testable with mocking.

**Recommendation:** Set up `pytest` with mock-based unit tests covering at minimum:
- `should_include()` with various section/path combinations
- `migrate_ts_keys()` edge cases
- The newest-wins merge logic (peer newer, local newer, file deleted)
- Input validation

### 7.2 [MEDIUM] Single-file Python architecture limits extensibility

All sync logic resides in one 265-line file. This is acceptable for the current scope but adding new sections (e.g., VS Code settings, SSH config) would increase complexity without structure.

### 7.3 [LOW] No logging mechanism

Both `sync.sh` and `sync-timestamps.py` use `print()` / `echo` for output. The cron job redirects stdout to `/tmp/ai-config-sync.log`, but there is no log rotation, timestamping, or log-level filtering.

---

## 8. Data Integrity

### 8.1 [MEDIUM] Timestamp file can be corrupted if sync is interrupted

If the process is killed between lines 254-259 (writing the new timestamp JSON), the file could be left empty or partially written. On next run, the `json.loads()` at line 140 will raise an exception and `set -e` will abort the entire sync.

**Recommendation:** Write to a temp file and `os.rename()` atomically:
```python
tmp = our_ts_file.with_suffix('.tmp')
tmp.write_text(json.dumps(new_ts, indent=2, ensure_ascii=False), encoding="utf-8")
tmp.rename(our_ts_file)
```

### 8.2 [LOW] "Newest-wins" can lose concurrent edits

If two devices edit the same file within the same 30-minute window, the device with the later mtime wins entirely. There is no merge, diff, or conflict marker. This is a known design choice documented in CLAUDE.md, but worth noting for the audit.

---

## 9. Documentation

### 9.1 [LOW] CLAUDE.md and README are well-maintained

The `CLAUDE.md` accurately describes the architecture, sync flow, and platform-specific behavior. The `README.md` provides clear setup instructions.

### 9.2 [LOW] `CLAUDE_INCLUDES` whitelist documentation gap

The `CLAUDE_INCLUDES` set in `sync-timestamps.py` controls which Claude Code items are synced, but this is not documented in `README.md` or `CLAUDE.md`. A new contributor would not know how to add a new sync target.

---

## 10. Summary of Findings by Severity

| Severity | Count | Key Items |
|---|---|---|
| CRITICAL | 1 | Large binary files (35+ MB fonts, videos, PNGs) tracked in git |
| HIGH | 3 | Bare except clause, no concurrent-execution guard, timestamp JSON churn |
| MEDIUM | 9 | No tests, stale state file, `git add -A` scoping, fragile error handling, etc. |
| LOW | 9 | Missing type annotations, placeholder docs, version detection N/A, etc. |

---

## 11. Recommended Action Plan (Priority Order)

1. **Immediate: Tighten `.gitignore`** -- Add `*.mp4`, `*.mp3`, `*.ttf`, `*.html` exclusions. Remove tracked binary files from the index.
2. **Immediate: Fix bare `except:`** in `sync-timestamps.py` line 73 to `except OSError:`.
3. **Short-term: Add `flock` guard** to `sync.sh` to prevent concurrent execution.
4. **Short-term: Atomic timestamp write** -- Use temp file + rename pattern.
5. **Short-term: Clean up stale artifacts** -- Remove `state/192.md`, `docs/taskflow/` placeholders.
6. **Medium-term: Set up pytest** -- Add unit tests for `sync-timestamps.py` core logic.
7. **Medium-term: Reduce timestamp churn** -- Consider squashing old sync commits or storing timestamps differently.
8. **Long-term: Git history cleanup** -- Run `git filter-repo` to remove historical large blobs (Flutter assets, videos) and re-push.
