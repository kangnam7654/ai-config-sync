# ai-config-sync Security Assessment Report

> Assessment Date: 2026-03-26
> Repo: `kangnam7654/ai-config-sync` (GitHub PUBLIC)
> Branch: `main` (no branch protection)
> Assessor: Claude (automated)

---

## Executive Summary

**Overall Risk Rating: HIGH**

This repository synchronizes personal development tool configurations (OpenClaw, Claude Code) across multiple machines via a public GitHub repository. The core sync logic (`sync-timestamps.py`) has solid input validation and path traversal defenses. However, the PUBLIC visibility of the repo combined with sensitive information already present in git history creates significant exposure. The most critical finding is that Google OAuth `client_secret` values are recorded verbatim in an agent-memory file within the public git history.

---

## 1. CRITICAL Findings

### 1-1. Google OAuth Client Secrets Exposed in Public Git History

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| File | `claude-code/agent-memory/security-reviewer/project_kangnam_credentials.md` |
| Commit | `0875d00e` (2026-03-18) |
| Status | Currently in HEAD, publicly accessible |

The file contains two plaintext Google OAuth `client_secret` values (`GOCSPX-` prefix). Although these secrets belong to a different project (`kangnam-client`), they are published in this PUBLIC repository's history. Anyone can read them. These are non-PKCE OAuth secrets, meaning an attacker could use them to impersonate the OAuth client and perform token exchanges on behalf of users.

**Remediation (Immediate):**
1. Revoke and rotate both `GOCSPX-*` secrets in Google Cloud Console immediately.
2. Remove the file from the current branch.
3. Since the repo is public, the secrets are already compromised regardless of history rewriting. Rotation is the only effective mitigation.
4. Consider running `git filter-repo` or BFG Repo Cleaner to strip the file from history, then force-push.

### 1-2. Repository is PUBLIC -- Design Tool Config Sync as Public Repo

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Scope | Entire repository |

This repo syncs personal `~/.claude/` configuration files (agents, skills, memory, settings) and `~/.openclaw/workspace/` content to a PUBLIC GitHub repository. This means:

- All Claude Code agent definitions, skills, and memory files are world-readable.
- Machine hostnames, OS versions, cron schedules, and filesystem paths are exposed via `state/*.md`.
- `installed_plugins.json` contains absolute local filesystem paths (e.g., `/Users/kangnam/.claude/plugins/cache/...`).
- Agent-memory files reveal project names, architecture decisions, and audit findings for other private projects.

**Remediation:**
- **Option A (Recommended):** Switch this repository to PRIVATE. Run: `gh repo edit kangnam7654/ai-config-sync --visibility private`.
- **Option B:** If the repo must remain public, strip all personal configuration data and keep only the sync tooling (scripts + sync-timestamps.py). Move actual config data to a separate private repo.

### 1-3. No Branch Protection on `main`

| Field | Value |
|-------|-------|
| Severity | HIGH |
| Scope | Repository settings |

The `main` branch has no protection rules. The automated cron job pushes directly to `main` every 30 minutes. Any compromised machine or leaked SSH key could push arbitrary content to the repo without review. Since this repo syncs configurations back to local machines, a supply-chain attack could inject malicious agent definitions or skill prompts that execute on all synced devices.

**Remediation:**
- Enable branch protection requiring at least one review for non-automated commits.
- For automated sync commits, use a dedicated deploy key with limited scope rather than a personal SSH key.

---

## 2. HIGH Findings

### 2-1. `skipDangerousModePermissionPrompt: true` Synced Across All Machines

| Field | Value |
|-------|-------|
| Severity | HIGH |
| File | `claude-code/settings.json` (line 41) |

This setting disables Claude Code's safety confirmation prompts for dangerous operations (file deletion, destructive git commands, etc.) on every machine that receives the sync. If an attacker compromises one synced configuration, all machines inherit the weakened safety posture.

**Remediation:**
- Remove `skipDangerousModePermissionPrompt` from the synced `settings.json`.
- If needed, set it locally per-machine outside the sync scope.
- Add it to `EXCLUDES` or create a machine-specific settings overlay mechanism.

### 2-2. Automated Push with Personal SSH Key

| Field | Value |
|-------|-------|
| Severity | HIGH |
| File | `sync.sh` |
| Remote | `git@github.com:kangnam7654/ai-config-sync.git` |

The cron job runs `git push origin main` using the system's SSH key (likely the user's personal GitHub SSH key with access to all repositories). If any synced machine is compromised, the attacker gains push access to this repo and potentially other repos accessible by that SSH key.

**Remediation:**
- Create a dedicated deploy key (or fine-grained personal access token) scoped to only this repository with write access.
- Configure the cron job to use this limited-scope credential.

### 2-3. Information Disclosure via `state/*.md` Files

| Field | Value |
|-------|-------|
| Severity | HIGH |
| Files | `state/Kangnamui-MacBookPro.md`, `state/kangnam-Desktop-Ubuntu.md`, `state/192.md` |

State files reveal:
- OS versions and architectures (attack surface mapping).
- Exact cron job commands and log file paths.
- Absolute filesystem paths (`/home/kangnam/projects/...`, `/tmp/ai-config-sync.log`).
- Recent workspace file names revealing project names and internal tools.
- Machine hostnames across the network.

**Remediation:**
- If the repo remains public, exclude `state/` from git tracking or redact sensitive fields.
- If switched to private, this becomes an acceptable risk.

---

## 3. MEDIUM Findings

### 3-1. Windows Pull-Only Uses `git reset --hard origin/main`

| Field | Value |
|-------|-------|
| Severity | MEDIUM |
| File | `sync.sh` (line 153) |

```bash
git reset --hard origin/main 2>/dev/null
```

In pull-only mode, the script runs `git reset --hard`, which silently discards any local changes. If a user accidentally modifies files in the sync directory on Windows, those changes are permanently lost without warning. More critically, if an attacker pushes malicious content to `origin/main`, the Windows machine unconditionally accepts it.

**Remediation:**
- Add a pre-check that logs what will be discarded before reset.
- Consider using `git checkout` for specific paths rather than a blanket `--hard` reset.

### 3-2. No Commit Signing or Verification

| Field | Value |
|-------|-------|
| Severity | MEDIUM |
| Scope | All commits |

None of the sync commits are GPG/SSH signed. Combined with no branch protection, an attacker who gains push access could forge commits appearing to come from any committer identity. The sync system would then distribute the forged content to all machines.

**Remediation:**
- Enable commit signing for sync commits.
- Configure branch protection to require signed commits.

### 3-3. `sync.sh` Cron Log Written to World-Readable Locations

| Field | Value |
|-------|-------|
| Severity | MEDIUM |
| File | `state/Kangnamui-MacBookPro.md`, `state/192.md` |

Some machines write sync logs to `/tmp/ai-config-sync.log`, which is world-readable on most Unix systems. Sync logs may contain file paths, hostnames, and error messages revealing configuration details.

**Remediation:**
- Use `setup.sh`'s recommended path: `~/.local/share/ai-config-sync/sync.log` with `chmod 700` on the directory.
- Update existing cron entries to use the secure path.

### 3-4. Plugin Marketplace Data Synced Without Integrity Verification

| Field | Value |
|-------|-------|
| Severity | MEDIUM |
| Files | `claude-code/plugins/marketplaces/` (excluded by .gitignore), `claude-code/plugins/installed_plugins.json` |

While `marketplaces/` is excluded from git, `installed_plugins.json` and `known_marketplaces.json` are synced. These files could be tampered with to redirect plugin installations to malicious sources. The `installed_plugins.json` also leaks absolute filesystem paths.

**Remediation:**
- Add `installed_plugins.json` and `known_marketplaces.json` to `EXCLUDES` for the `claude-code` section, or exclude them from `CLAUDE_INCLUDES`.
- Plugin installation metadata is machine-specific and should not be synced.

---

## 4. LOW Findings

### 4-1. Hostname Validation Allows Overly Broad Patterns

| Field | Value |
|-------|-------|
| Severity | LOW |
| File | `sync-timestamps.py` (line 43) |

The hostname regex `^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$` is RFC-compliant but allows up to 63 characters. The hostname is used as a JSON filename (`timestamps/{hostname}.json`) and in state file paths. While not exploitable given the regex constraints, extremely long hostnames could cause filesystem issues on some platforms.

**Status:** Acceptable risk. No action required.

### 4-2. Git Commit Author Email Leaks Internal Network Info

| Field | Value |
|-------|-------|
| Severity | LOW |
| Scope | Git history |

The commit `0875d00e` uses the email `kangnam@192.168.nate.com`, revealing an internal network hostname pattern. Other commits reveal local machine hostnames in email addresses.

**Remediation:**
- Configure a consistent git author email across all machines (e.g., `kangnam7654@users.noreply.github.com`).

### 4-3. `.venv` Directory Present in Repo Root

| Field | Value |
|-------|-------|
| Severity | LOW |
| Path | `.venv/` |

The `.venv/` directory exists in the working tree. While `.venv` is not in `.gitignore`, it does not appear to be tracked by git. However, without an explicit `.gitignore` entry, there is risk of accidental commit.

**Remediation:**
- Add `.venv/` to `.gitignore`.

---

## 5. Positive Security Controls (Already Implemented)

| Control | Location | Assessment |
|---------|----------|------------|
| Path traversal prevention | `validate_filepath()` in `sync-timestamps.py` | GOOD -- blocks `..`, absolute paths, null bytes |
| Hostname validation | `validate_hostname()` in `sync-timestamps.py` | GOOD -- RFC 952/1123 compliant regex |
| Timestamp validation | `validate_timestamp()` in `sync-timestamps.py` | GOOD -- rejects negative, non-numeric, and future-drift > 24h |
| Peer section validation | `load_peer_timestamps()` in `sync-timestamps.py` | GOOD -- validates section keys against `_KNOWN_SECTIONS` whitelist |
| Whitelist-based sync for Claude Code | `CLAUDE_INCLUDES` in `sync-timestamps.py` | GOOD -- only explicitly listed items are synced |
| Section-based exclusion patterns | `EXCLUDES` dict in `sync-timestamps.py` | GOOD -- excludes history, cache, debug data |
| Symlink removal | `sync_section()` line 376 | GOOD -- removes symlinks in claude-code section |
| Sensitive config template pattern | `openclaw.template.json` + `.gitignore` for `openclaw.json` | GOOD -- real config never committed |
| Token generation with `openssl rand` | `setup-mac.sh`, `setup.sh` | GOOD -- 24-byte hex token, created with `umask 077` |
| Scoped `git add` | `sync.sh` line 125 | GOOD -- only adds specific subdirectories, not `git add .` |
| CI/CD testing | `.github/workflows/test.yml` | GOOD -- multi-platform, multi-Python-version test matrix with coverage threshold |
| UTF-8 encoding enforcement | `sync-timestamps.py`, `sync.sh` (PYTHONUTF8=1) | GOOD -- prevents CP949 encoding issues on Windows |
| Gateway loopback binding | `openclaw.template.json` `gateway.bind: loopback` | GOOD -- gateway only accessible locally |
| Peer timestamp filename validation | `load_peer_timestamps()` regex | GOOD -- restricts to `[a-zA-Z0-9._-]+\.json` |

---

## 6. Threat Model Summary

| # | Threat | Severity | Likelihood | Impact | Finding |
|---|--------|----------|------------|--------|---------|
| T-01 | Credential exposure via public git history | CRITICAL | CONFIRMED | Credential compromise | 1-1 |
| T-02 | Personal config data exposed on public repo | CRITICAL | CONFIRMED | Information disclosure | 1-2 |
| T-03 | Supply-chain attack via compromised sync push | HIGH | Medium | Arbitrary config injection across all machines | 1-3, 2-2 |
| T-04 | Safety bypass propagation | HIGH | High | Dangerous mode enabled on all synced machines | 2-1 |
| T-05 | Attacker-controlled content via unprotected main | HIGH | Medium | Malicious agents/skills distributed | 1-3 |
| T-06 | Attack surface mapping via state files | HIGH | High (repo is public) | OS/network/path reconnaissance | 2-3 |
| T-07 | Silent overwrite on pull-only machines | MEDIUM | Low | Local data loss, malicious content acceptance | 3-1 |
| T-08 | Commit forgery | MEDIUM | Low | Trust erosion, traceability loss | 3-2 |
| T-09 | Log exposure via world-readable paths | MEDIUM | Medium | Path and config leakage | 3-3 |

---

## 7. Prioritized Remediation Plan

| Priority | Finding | Action | Effort | Impact |
|----------|---------|--------|--------|--------|
| **P0** | 1-1 | Rotate both `GOCSPX-*` secrets in Google Cloud Console NOW | 10 min | Eliminates credential compromise |
| **P0** | 1-2 | Switch repo to PRIVATE: `gh repo edit --visibility private` | 1 min | Eliminates all public exposure |
| **P1** | 1-1 | Remove `project_kangnam_credentials.md` from repo + scrub history with BFG | 30 min | Prevents future re-exposure |
| **P1** | 1-3 | Enable branch protection on `main` | 5 min | Prevents unauthorized pushes |
| **P1** | 2-2 | Create a deploy key scoped to this repo only | 15 min | Limits blast radius of machine compromise |
| **P2** | 2-1 | Remove `skipDangerousModePermissionPrompt` from synced settings | 5 min | Restores safety prompts per-machine |
| **P2** | 3-4 | Exclude `installed_plugins.json`, `known_marketplaces.json` from sync | 5 min | Stops leaking local paths + machine-specific data |
| **P2** | 3-3 | Fix cron entries to use `~/.local/share/ai-config-sync/sync.log` with 700 perms | 10 min | Prevents log disclosure |
| **P3** | 3-2 | Enable commit signing | 15 min | Adds commit authenticity |
| **P3** | 4-2 | Standardize git author email across machines | 5 min | Reduces info leakage |
| **P3** | 4-3 | Add `.venv/` to `.gitignore` | 1 min | Prevents accidental commit |

---

## 8. Architecture-Level Observations

### Sync Trust Model

The current architecture implicitly trusts all synced machines equally. Any machine that can push to `origin/main` can modify the configuration of all other machines. There is no mechanism to:

- Verify the authenticity of sync commits (no signing).
- Restrict which files a specific machine can modify (any pusher can change any synced file).
- Detect or alert on unexpected configuration changes.

For a personal-use sync tool, this is an acceptable trade-off if the repo is PRIVATE and branch protection is enabled. For a PUBLIC repo, this trust model is fundamentally broken.

### Newest-Wins Conflict Resolution

The `newest-wins` strategy based on mtime comparison is simple and effective for this use case. However, clock skew between machines beyond the 24-hour drift limit could cause data loss. The `validate_timestamp()` guard mitigates extreme cases.

### Python Code Quality

The `sync-timestamps.py` code is well-structured with clear separation of concerns, proper input validation, and cross-platform considerations (pathlib, UTF-8 encoding). The test suite covers validation functions, timestamp operations, and sync logic with mocked git operations.

---

## Appendix: Files Reviewed

| File | Purpose |
|------|---------|
| `sync-timestamps.py` | Core sync logic (444 lines) |
| `sync.sh` | Shell orchestration script (163 lines) |
| `setup.sh` | Interactive unified setup (162 lines) |
| `setup-mac.sh` | macOS/Ubuntu setup (deprecated) |
| `setup-windows.sh` | Windows Git Bash setup |
| `.gitignore` | Tracking exclusions |
| `.github/workflows/test.yml` | CI pipeline |
| `openclaw/openclaw.template.json` | Config template |
| `claude-code/settings.json` | Claude Code settings (synced) |
| `claude-code/stop-hook-git-check.sh` | Git status check hook |
| `claude-code/plugins/installed_plugins.json` | Plugin metadata |
| `claude-code/plugins/blocklist.json` | Plugin blocklist |
| `state/*.md` | Machine state reports |
| `timestamps/*.json` | Sync timestamps |
| `tests/` | Test suite (8 files) |
| `pyproject.toml` | Project configuration |
| `CLAUDE.md` | Project instructions |
| `README.md` | Documentation |
| Git history | Full commit history and diff analysis |
