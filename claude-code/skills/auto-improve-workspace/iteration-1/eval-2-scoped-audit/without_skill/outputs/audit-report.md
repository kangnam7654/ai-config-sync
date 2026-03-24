# ai-config-sync Audit Report: Security & Test Coverage

> Project: `/Users/kangnam/projects/ai-config-sync`
> Date: 2026-03-24
> Scope: Security findings + Test coverage assessment only

---

## 1. Security Audit

### 1.1 Credential & Secret Exposure

| ID | Severity | Location | Finding | Recommendation |
|----|----------|----------|---------|----------------|
| S-01 | **HIGH** | `openclaw/workspace/sync-openclaw.sh:41-42` | GitHub token embedded in remote URL via `gh auth token`. The token is interpolated into a plaintext URL (`https://kangnam7654:${TOKEN}@github.com/...`) and passed to `git remote set-url`. This URL may be logged in shell history, process listings, or git config. | Use SSH remote (`git@github.com:...`) or `GIT_ASKPASS` / credential helper instead of URL-embedded tokens. |
| S-02 | LOW | `openclaw/openclaw.template.json:52` | Template contains placeholder `<REPLACE_WITH_NEW_TOKEN>`. The actual `openclaw.json` is correctly gitignored. | No action needed; placeholder is safe. Current `.gitignore` entry `openclaw/openclaw.json` is correct. |
| S-03 | LOW | `setup-mac.sh:34-35` | Token generation via `openssl rand -hex 24` written to temp file (`$CONFIG_FILE.tmp`), then deleted. Race condition window exists where temp file contains token. | Use pipe or process substitution to avoid writing token to temp file, or ensure `umask 077` before creation. |
| S-04 | INFO | `setup-mac.sh:50` | Example API key prefix `sk-ant-...` printed to stdout. This is documentation only, not a real key. | No action needed. |

### 1.2 Input Validation

| ID | Severity | Location | Finding | Recommendation |
|----|----------|----------|---------|----------------|
| S-05 | **MEDIUM** | `sync-timestamps.py:127-128` | `sys.argv[1]` and `sys.argv[2]` are used without validation. `hostname` is used directly in file path construction (`ts_dir / f"{hostname}.json"`) and in `git show` commands. A malicious hostname containing path traversal characters (e.g., `../../etc`) or shell metacharacters could write outside `timestamps/`. | Add hostname validation: reject values containing `/`, `\`, `..`, or non-alphanumeric characters (except `-` and `_`). Verify `sync_dir` is the expected repo directory. |
| S-06 | **MEDIUM** | `sync-timestamps.py:153-157` | Peer filenames from `git ls-tree` output are used to construct `git show` commands and parsed as peer identifiers. A malicious peer could craft a filename in `timestamps/` to inject unexpected values. | Validate that `peer` (from `Path(fname).stem`) matches expected hostname pattern before processing. |
| S-07 | LOW | `sync-timestamps.py:73` | Bare `except:` catches all exceptions including `KeyboardInterrupt` and `SystemExit`. | Use `except OSError:` instead. |
| S-08 | LOW | `sync-timestamps.py:160` | `except Exception: pass` silently swallows JSON parse errors for peer timestamps. A corrupted or malicious timestamp file would be silently ignored. | Log a warning when peer timestamp parsing fails. |

### 1.3 File System Security

| ID | Severity | Location | Finding | Recommendation |
|----|----------|----------|---------|----------------|
| S-09 | **MEDIUM** | `sync-timestamps.py:220-223` | `write_bytes` from peer content is written to both local (`~/.claude/` or `~/.openclaw/workspace/`) and repo paths without content validation. If a peer pushes a malicious file (e.g., a symlink target or oversized file), it is blindly written to the local filesystem. | Add file size limits. Validate that the target path stays within the expected directory after resolution (`resolve()`). Consider content-type validation for known file types. |
| S-10 | **MEDIUM** | `sync-timestamps.py:236-240` | Symlink cleanup only runs for `claude-code` section. Symlinks in `workspace` section are not cleaned. A peer could push a symlink pointing outside the sync directory. | Extend symlink removal to all sections, or reject symlinks during the file write phase. |
| S-11 | LOW | `sync.sh:138` | `git reset --hard origin/main` on Windows discards all local changes without confirmation. This is documented (Windows = pull-only), but any local edits on Windows are silently lost. | Add a guard: check for uncommitted changes before reset and warn. |

### 1.4 Configuration Security

| ID | Severity | Location | Finding | Recommendation |
|----|----------|----------|---------|----------------|
| S-12 | **MEDIUM** | `claude-code/settings.json:41` | `"skipDangerousModePermissionPrompt": true` is synced across all machines. This setting disables safety prompts in Claude Code, increasing risk of unintended destructive operations on any synced machine. | Consider whether this setting should be per-machine rather than synced. Add it to an exclude list or make it machine-specific. |
| S-13 | LOW | `claude-code/settings.json:12` | Hook command `~/.claude/log-session.sh` is referenced but not included in the sync whitelist (`CLAUDE_INCLUDES`). If this script does not exist on a peer machine, the hook silently fails. | Either add `log-session.sh` and `statusline.sh` to `CLAUDE_INCLUDES`, or document that these are machine-local scripts. |

### 1.5 .gitignore Completeness

| ID | Severity | Location | Finding | Recommendation |
|----|----------|----------|---------|----------------|
| S-14 | LOW | `.gitignore` | `auth-profiles.json` is correctly excluded. `credentials/`, `.env`, `.env.local`, `sessions/` are correctly excluded. `openclaw/openclaw.json` (contains real token) is correctly excluded. | .gitignore is adequate for known sensitive files. |
| S-15 | INFO | `.gitignore:14` | `claude-code/plugins/marketplaces/` is gitignored but the directory exists locally with git submodules. This is correct behavior. | No action needed. |

### 1.6 Timestamp Data Leakage

| ID | Severity | Location | Finding | Recommendation |
|----|----------|----------|---------|----------------|
| S-16 | LOW | `timestamps/*.json` | Timestamp files expose the full file tree of `~/.claude/` and `~/.openclaw/workspace/` including file names and exact modification times. This reveals the user's installed skills, agents, teams, todos, and workspace structure to anyone with repo access. | Ensure the repo remains private. Consider hashing file paths if privacy of file names is a concern. |

---

## 2. Test Coverage Audit

### 2.1 Current State

| Metric | Value |
|--------|-------|
| Test framework configured | **No** |
| `tests/` directory | **Does not exist** |
| `pyproject.toml` / `setup.py` | **Does not exist** |
| `pytest.ini` / `tox.ini` | **Does not exist** |
| Existing test files for project code | **0** |
| Current test coverage | **0%** |

The project's `CLAUDE.md` explicitly states: "테스트 프레임워크 없음. 변경 시 `python3 sync-timestamps.py . $(hostname -s)`로 직접 실행해서 확인."

### 2.2 Code to Cover

| File | Lines | Functions | Testability |
|------|-------|-----------|-------------|
| `sync-timestamps.py` | 264 | 10 (`migrate_ts_keys`, `should_include`, `git_cmd`, `git_bytes`, `mtime`, `walk_files`, `walk_all_files`, `unlink_if_file`, `prune_empty_dirs`, `main`) | High for pure functions, medium for I/O functions |
| `sync.sh` | 148 | 2 (`detect_platform`, `generate_state`) + main flow | Low (requires OS-specific mocking) |
| `setup-mac.sh` | 64 | - (linear script) | Low (requires macOS + npm + openclaw) |
| `setup-windows.sh` | 44 | - (linear script) | Low (requires Windows + schtasks) |

### 2.3 Recommended Test Plan

**Priority 1 -- Pure-logic functions (unit tests, no I/O mock needed):**

| Function | Test Cases | Est. Count |
|----------|------------|------------|
| `migrate_ts_keys` | Normal migration, no-op when new key exists, empty dict, multiple migrations | 4 |
| `should_include` | Excluded patterns (workspace), excluded patterns (claude-code), whitelist match, whitelist miss, nested paths, edge cases | 6 |

**Priority 2 -- I/O functions (need filesystem mock/tempdir):**

| Function | Test Cases | Est. Count |
|----------|------------|------------|
| `mtime` | Existing file, non-existent file, permission error | 3 |
| `walk_files` | Normal tree, excluded files filtered, non-existent base, empty dir, symlinks | 5 |
| `walk_all_files` | Normal tree, .git excluded, empty base | 3 |
| `unlink_if_file` | Regular file, symlink, directory (should skip), non-existent | 4 |
| `prune_empty_dirs` | Nested empty dirs, non-empty dirs preserved, non-existent base | 3 |

**Priority 3 -- Integration tests (need git repo + tempdir):**

| Scenario | Test Cases | Est. Count |
|----------|------------|------------|
| `main` end-to-end | Local newer wins, peer newer wins, new file from peer, deleted file cleanup, timestamp JSON round-trip, encoding (UTF-8 filenames) | 6 |
| `git_cmd` / `git_bytes` | Successful command, failed command, encoding | 3 |

**Total estimated tests: 37**

### 2.4 Estimated Effort to Reach 80% Coverage

| Step | Action | Effort |
|------|--------|--------|
| 1 | Add `pyproject.toml` with pytest config | 15 min |
| 2 | Create `tests/` directory structure | 5 min |
| 3 | Priority 1 tests (pure logic, 10 tests) | 1 hour |
| 4 | Priority 2 tests (I/O with tempdir, 18 tests) | 2 hours |
| 5 | Priority 3 tests (integration, 9 tests) | 3 hours |
| **Total** | | **~6 hours** |

Priority 1 alone would cover `migrate_ts_keys` and `should_include` (2 of 10 functions = ~20% function coverage but these are the most logic-dense). Priority 1 + 2 would likely reach 60-70% line coverage. All three priorities are needed for the 80% target.

---

## 3. Summary

### Security Risk Matrix

| Severity | Count | IDs |
|----------|-------|-----|
| HIGH | 1 | S-01 |
| MEDIUM | 4 | S-05, S-06, S-09, S-10, S-12 |
| LOW | 6 | S-03, S-07, S-08, S-11, S-13, S-16 |
| INFO | 2 | S-04, S-15 |

### Top 3 Actions (by impact)

1. **Fix S-01**: Remove token-in-URL pattern from `sync-openclaw.sh`. Switch to SSH or credential helper.
2. **Fix S-05 + S-06**: Add hostname/peer name validation in `sync-timestamps.py` to prevent path traversal.
3. **Start test coverage**: Add `pyproject.toml` + Priority 1 unit tests for `should_include` and `migrate_ts_keys` as the minimum viable test suite. These are the functions most likely to break when sync rules change.
