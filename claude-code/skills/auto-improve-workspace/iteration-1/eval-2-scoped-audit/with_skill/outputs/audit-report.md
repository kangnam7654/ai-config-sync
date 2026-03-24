# Audit Report: ai-config-sync (Scoped)

> Scoped audit: **security** + **test** only. Other areas (code quality, architecture, DB, UX/UI) are out of scope.

## 1. Target Overview

| Field | Value |
|---|---|
| Project Path | `/Users/kangnam/projects/ai-config-sync` |
| Languages | Python (sync-timestamps.py), Bash (sync.sh, setup-mac.sh, setup-windows.sh) |
| Frameworks | None (standalone scripts) |
| DB | None |
| UI | None |
| Audit Scope | security, test |

### scope-map

```yaml
project_path: /Users/kangnam/projects/ai-config-sync
tech_stack:
  languages: [Python, Bash]
  frameworks: []
  db: null
  has_ui: false
audit_scope:
  code_quality: false   # out of scope
  security: true
  architecture: false   # out of scope
  db: false             # N/A (no DB)
  test: true
  ux_ui: false          # N/A (no UI)
user_focus: [security, test]
```

---

## 2. Baseline Scores

| Area | Score (0-10) | Notes |
|---|---|---|
| Security | 4.5 | Multiple findings across severity levels |
| Test Coverage | 1.0 | No test framework, no tests, no CI |

---

## 3. Security Diagnostic (#3)

### 3.1 Scores by Sub-area

| Sub-area | Score | Weight | Weighted |
|---|---|---|---|
| Hardcoded Secrets / Credential Exposure | 3.0 | 0.25 | 0.75 |
| Input Validation | 5.0 | 0.20 | 1.00 |
| Dependency Vulnerabilities | 7.0 | 0.10 | 0.70 |
| Sensitive Data Handling | 4.0 | 0.20 | 0.80 |
| File System Security | 5.0 | 0.15 | 0.75 |
| Error Handling / Info Leakage | 5.0 | 0.10 | 0.50 |
| **Weighted Total** | | | **4.5** |

### 3.2 Findings

#### SEC-001 [Critical] GitHub Token Embedded in Remote URL

- **File**: `openclaw/workspace/sync-openclaw.sh`, lines 41-42
- **Description**: `gh auth token` output is interpolated directly into a HTTPS remote URL (`https://kangnam7654:${TOKEN}@github.com/...`). This token is stored in `.git/config` as plaintext, persists across reboots, and is visible in `git remote -v` output. If the repo is ever shared or the machine is compromised, the GitHub token leaks.
- **Severity**: Critical
- **Improvement**: Use SSH remote (`git@github.com:...`) or use a Git credential helper (`git credential-store`, `gh auth setup-git`) that stores tokens outside the repo config. Never embed tokens in URLs.

#### SEC-002 [High] openclaw.json Copied to Sync Repo

- **File**: `openclaw/workspace/sync-openclaw.sh`, line 33
- **Description**: `cp "$OPENCLAW_DIR/openclaw.json" .` copies the actual config (which contains gateway auth tokens) into the sync repo working tree. Although `.gitignore` in the main project excludes `openclaw/openclaw.json`, the `sync-openclaw.sh` script operates in a separate repo (`~/openclaw-sync`) where this file gets committed via `git add .` (line 52).
- **Severity**: High
- **Improvement**: Never copy `openclaw.json` into a git-tracked directory. If config sync is needed, strip sensitive fields first, or use the template-only approach already adopted in the main project.

#### SEC-003 [High] Bare `except:` Swallows All Errors

- **File**: `sync-timestamps.py`, line 73
- **Description**: `mtime()` uses bare `except:` which catches `KeyboardInterrupt`, `SystemExit`, and all exceptions silently. A malicious or corrupted symlink could cause an unexpected error that gets silently swallowed, potentially leading to data loss (mtime returns 0.0, making the file appear older than peers, causing overwrite).
- **Severity**: High
- **Improvement**: Replace `except:` with `except OSError:` to only catch file-system errors.

#### SEC-004 [Medium] No Input Validation for CLI Arguments

- **File**: `sync-timestamps.py`, lines 127-128
- **Description**: `sys.argv[1]` and `sys.argv[2]` are used directly without validation. Missing arguments produce an unhelpful `IndexError`. The hostname is used as a filename (`timestamps/{hostname}.json`) without sanitization -- a hostname containing path traversal characters (e.g., `../../../etc/passwd`) could write outside the intended directory.
- **Severity**: Medium
- **Improvement**: Validate `len(sys.argv)`, sanitize hostname (allow only `[a-zA-Z0-9_-]`), and validate that `sync_dir` exists and is a directory.

#### SEC-005 [Medium] Peer Timestamp JSON Parsed Without Schema Validation

- **File**: `sync-timestamps.py`, lines 157-160
- **Description**: Peer timestamp files are parsed from `FETCH_HEAD` via `json.loads()` with no schema validation. A malicious peer could inject crafted JSON with path traversal keys (e.g., `"../../etc/passwd": 99999999999.0`) causing file writes outside the intended sync directory.
- **Severity**: Medium
- **Improvement**: Validate that all filepath keys in peer timestamps are relative paths without `..` components. Reject any key containing `..` or starting with `/`.

#### SEC-006 [Medium] `git_bytes` Return Used Without Validating Content

- **File**: `sync-timestamps.py`, lines 216-223
- **Description**: When peer content is fetched via `git show`, the raw bytes are written to both the local filesystem (`~/.claude/...` or `~/.openclaw/workspace/...`) and the repo without any content validation. Combined with SEC-005, a malicious peer could place arbitrary content at sensitive file paths.
- **Severity**: Medium
- **Improvement**: Validate that `filepath` is a safe relative path (no `..`, no absolute, no null bytes) before writing.

#### SEC-007 [Low] Timestamp File Permissions World-Readable

- **File**: `timestamps/*.json`
- **Description**: Timestamp JSON files are created with default permissions (`644`), readable by all users. These files contain the full directory listing of `~/.claude` and `~/.openclaw/workspace`, revealing the user's file structure.
- **Severity**: Low
- **Improvement**: Consider restricting permissions to `600` for timestamp files, or accept the risk since the repo is private and file names (not contents) are exposed.

#### SEC-008 [Low] `sync.sh` Uses `set -e` Without Error Handler

- **File**: `sync.sh`, line 7
- **Description**: `set -e` causes immediate exit on any error, but there is no `trap` to clean up partial states (e.g., half-committed git operations, partial file copies). This could leave the repo in an inconsistent state.
- **Severity**: Low
- **Improvement**: Add `trap cleanup EXIT` to handle partial states gracefully.

---

## 4. Test Diagnostic (#6)

### 4.1 Scores by Sub-area

| Sub-area | Score | Weight | Weighted |
|---|---|---|---|
| Test Coverage | 0.0 | 0.30 | 0.00 |
| Test Type Distribution | 0.0 | 0.20 | 0.00 |
| Test Quality | 0.0 | 0.20 | 0.00 |
| Missing Test Areas | 0.0 | 0.15 | 0.00 |
| Test Infrastructure | 3.0 | 0.15 | 0.45 |
| **Weighted Total** | | | **0.45 (rounded to 1.0 for baseline)** |

### 4.2 Findings

#### TEST-001 [Critical] No Test Framework, No Tests

- **Description**: The project has **zero tests**. There is no `tests/` directory, no `pyproject.toml`, no `pytest` configuration, no test runner of any kind. The CLAUDE.md explicitly states: "Test framework is not set up. After changes, verify by directly running `python3 sync-timestamps.py . $(hostname -s)`."
- **Severity**: Critical
- **Improvement**: Set up pytest with a `tests/` directory and `pyproject.toml`. The core logic in `sync-timestamps.py` is highly testable (pure functions like `should_include`, `migrate_ts_keys`, `walk_files`).

#### TEST-002 [Critical] No CI/CD Pipeline

- **Description**: No `.github/workflows/`, no CI configuration of any kind. Changes are pushed directly to `main` via automated cron jobs without any automated validation.
- **Severity**: Critical
- **Improvement**: Add a minimal GitHub Actions workflow that runs pytest on push.

#### TEST-003 [High] Core Sync Logic Untested

- **Description**: The `newest-wins` merge logic in `sync-timestamps.py` is the critical path of the entire project. It handles file conflict resolution, peer timestamp comparison, and bidirectional file synchronization. All of this runs unattended via cron every 30 minutes. A bug here silently overwrites or deletes files across all synced machines.
- **Functions needing tests**:
  - `should_include(filepath, section)` -- whitelist/blacklist logic
  - `migrate_ts_keys(ts)` -- key migration
  - `walk_files(base, section)` -- file discovery with filtering
  - `main()` (integration) -- end-to-end sync with mock git and filesystem
- **Severity**: High
- **Improvement**: Unit tests for each function, integration test with a temp directory simulating a sync scenario.

#### TEST-004 [High] Shell Scripts Untested

- **Description**: `sync.sh`, `setup-mac.sh`, `setup-windows.sh` have no tests. `sync.sh` runs destructive git operations (`git reset --hard`, `git push`) via cron every 30 minutes without validation.
- **Severity**: High
- **Improvement**: Add integration tests using `bats` (Bash Automated Testing System) or at minimum, add `--dry-run` / `--check` modes to shell scripts for manual verification.

#### TEST-005 [Medium] No Regression Safety Net for Cross-Platform Behavior

- **Description**: The project syncs across macOS, Ubuntu, and Windows. Platform-specific behavior (CP949 encoding on Windows, path separators, `hostname` command differences) is untested. The CLAUDE.md warns about Windows CP949 issues, but there are no tests validating encoding handling.
- **Severity**: Medium
- **Improvement**: Add parameterized tests that simulate Windows-like paths and encoding scenarios.

---

## 5. CTO Synthesis (#8)

### 5.1 Priority Matrix

| Priority | ID | Title | Area | Difficulty |
|---|---|---|---|---|
| P0 | SEC-001 | GitHub token embedded in remote URL | security | S |
| P0 | TEST-001 | No test framework, no tests | test | M |
| P1 | SEC-002 | openclaw.json copied to sync repo | security | S |
| P1 | SEC-003 | Bare `except:` swallows all errors | security | S |
| P1 | TEST-002 | No CI/CD pipeline | test | S |
| P1 | TEST-003 | Core sync logic untested | test | M |
| P1 | TEST-004 | Shell scripts untested | test | L |
| P2 | SEC-004 | No input validation for CLI arguments | security | S |
| P2 | SEC-005 | Peer timestamp JSON parsed without schema validation | security | S |
| P2 | SEC-006 | `git_bytes` return used without content validation | security | S |
| P2 | TEST-005 | No cross-platform regression tests | test | M |
| P3 | SEC-007 | Timestamp file permissions world-readable | security | S |
| P3 | SEC-008 | `sync.sh` missing error trap | security | S |

### 5.2 Gate Decision

```yaml
gate: audit-cto
decision: PROCEED
baseline_scores:
  code_quality: N/A    # out of scope
  security: 4.5
  architecture: N/A    # out of scope
  db: N/A              # no DB
  test_coverage: 1.0
  ux_ui: N/A           # no UI
priority_items:
  p0:
    - {id: "SEC-001", title: "GitHub token embedded in remote URL", area: "security"}
    - {id: "TEST-001", title: "No test framework, no tests", area: "test"}
  p1:
    - {id: "SEC-002", title: "openclaw.json copied to sync repo", area: "security"}
    - {id: "SEC-003", title: "Bare except: swallows all errors", area: "security"}
    - {id: "TEST-002", title: "No CI/CD pipeline", area: "test"}
    - {id: "TEST-003", title: "Core sync logic untested", area: "test"}
    - {id: "TEST-004", title: "Shell scripts untested", area: "test"}
  p2:
    - {id: "SEC-004", title: "No input validation for CLI arguments", area: "security"}
    - {id: "SEC-005", title: "Peer timestamp JSON without schema validation", area: "security"}
    - {id: "SEC-006", title: "git_bytes return without content validation", area: "security"}
    - {id: "TEST-005", title: "No cross-platform regression tests", area: "test"}
  p3:
    - {id: "SEC-007", title: "Timestamp file permissions world-readable", area: "security"}
    - {id: "SEC-008", title: "sync.sh missing error trap", area: "security"}
improvement_scope:
  security: true
  test: true
  estimated_effort: M
```

### 5.3 Rationale

P0/P1 items total 7 (2 P0 + 5 P1). The combination of zero test coverage with an unattended cron-based sync system that writes to sensitive config directories (`~/.claude`, `~/.openclaw`) creates high risk of silent data loss or credential exposure. PROCEED is warranted -- security hardening and test framework setup should be addressed before further feature development.

---

## 6. Constraints

- **Backward Compatibility**: All fixes must maintain the existing `newest-wins` sync behavior across 3 platforms.
- **Cron Safety**: Since `sync.sh` runs every 30 minutes via cron, any breaking change immediately affects all synced machines.
- **No pyproject.toml**: Test framework setup requires creating `pyproject.toml` and `tests/` from scratch.
- **Synced Config Files**: Changes to `sync-timestamps.py` propagate automatically to all machines via the sync mechanism itself -- this is both a benefit (fast rollout) and a risk (bugs propagate fast).
