# Incident Response Playbook

**Organization:** KangNam Dev
**System:** ai-config-sync (Ubuntu / MacBook / Windows config synchronization)
**Data Types:** Development config files (IDE settings, CLI settings, API key references)
**Team Size:** 1 developer
**Last Updated:** 2026-03-26

---

## 1. Purpose and Scope

This playbook defines procedures for detecting, triaging, containing, and recovering from security incidents affecting the ai-config-sync system. The system synchronizes OpenClaw workspace and Claude Code settings across macOS, Ubuntu, and Windows machines via a private Git repository on a 30-minute cron cycle.

### In-Scope Assets

| Asset | Location | Sensitivity |
|-------|----------|-------------|
| sync repository (GitHub private) | `github.com:kangnam7654/ai-config-sync` | High -- contains config paths, API key references |
| `~/.openclaw/workspace` | macOS, Ubuntu | Medium -- workspace configs, skills, agents |
| `~/.claude` | macOS, Ubuntu, Windows (pull-only) | High -- settings.json, CLAUDE.md, skills, plugins, memory |
| `openclaw.template.json` | repo root | Low -- template only, no secrets |
| `openclaw/openclaw.json` | **NOT tracked** (excluded) | Critical -- contains actual API keys |
| `timestamps/*.json` | repo | Low -- metadata only |
| `state/*.md` | repo | Low -- machine info (OS, versions) |
| Cron jobs / Task Scheduler entries | each machine | Medium -- automation control |

### Out of Scope

- Infrastructure incidents at GitHub (covered by GitHub's own incident process)
- General OS-level compromise unrelated to synced config files

---

## 2. Severity Classification

| Severity | Definition | Examples | Response Time |
|----------|-----------|----------|---------------|
| **SEV-1 Critical** | Active credential exposure or unauthorized access confirmed | API key pushed to repo; SSH key in synced files; unauthorized git push detected | Immediate (within 15 min) |
| **SEV-2 High** | Potential credential exposure or sync integrity compromised | `openclaw.json` accidentally committed; rebase conflict overwrites local config with malicious content; unknown peer hostname in timestamps/ | Within 1 hour |
| **SEV-3 Medium** | Sync disruption or suspicious activity without confirmed exposure | Cron job stopped running; `sync.sh` errors repeatedly; unexpected file in `claude-code/` directory | Within 4 hours |
| **SEV-4 Low** | Minor anomaly, no security impact | Timestamp drift > 24h rejected; empty directory accumulation; state file format error | Next business day |

---

## 3. Incident Detection

### 3.1 Automated Detection Points

| Signal | Where to Check | Indicates |
|--------|---------------|-----------|
| Unknown hostname in `timestamps/` | `git log --all -- timestamps/` | Unauthorized device added to sync |
| `openclaw.json` appears in git history | `git log --all --diff-filter=A -- openclaw/openclaw.json` | Credential file accidentally committed |
| Unexpected files in `claude-code/` outside CLAUDE_INCLUDES whitelist | Compare repo contents vs `CLAUDE_INCLUDES` set in `sync-timestamps.py` | Whitelist bypass or manual commit of sensitive file |
| `sync.sh` exit code non-zero in cron log | `grep sync /var/log/syslog` or `crontab -l` output cross-ref | Sync pipeline broken |
| `git log` shows commits from unknown author | `git log --format='%an %ae' \| sort -u` | Compromised repo access |
| Peer timestamp with future value > 24h | Logged as `[WARN]` by `validate_timestamp()` | Tampered timestamp or clock skew attack |

### 3.2 Manual Review Checklist (Weekly)

1. Review `git log --oneline -20` for unexpected commits or authors.
2. Verify `timestamps/` contains only known hostnames.
3. Confirm `openclaw/openclaw.json` is NOT in the repo: `git ls-files openclaw/openclaw.json` should return empty.
4. Check `.gitignore` still excludes sensitive patterns.
5. Review `state/*.md` files for unexpected OS or hostname entries.

---

## 4. Incident Response Procedures

### 4.1 SEV-1: Credential Exposure

**Trigger:** API key, token, or secret value confirmed present in git history or accessible to unauthorized party.

**Steps:**

1. **Contain (0-15 min)**
   - Immediately revoke the exposed credential at the provider (OpenAI, Anthropic, etc.).
   - Disable cron/Task Scheduler on ALL machines to stop sync:
     ```bash
     # macOS/Ubuntu
     crontab -l | grep -v ai-config-sync | crontab -
     # Windows (Git Bash as admin)
     schtasks /delete /tn "ai-config-sync" /f
     ```
   - If the repo is public or access is uncertain, make the GitHub repo private immediately or delete it.

2. **Eradicate (15-60 min)**
   - Remove the secret from git history using `git filter-repo`:
     ```bash
     # Install if needed: pip install git-filter-repo
     git filter-repo --path openclaw/openclaw.json --invert-paths --force
     ```
   - Force push the cleaned history:
     ```bash
     git push origin main --force
     ```
   - On each machine, re-clone the repo from scratch (do NOT pull into existing clone).

3. **Recover (1-4 hours)**
   - Generate new credentials at each affected provider.
   - Update `openclaw/openclaw.json` locally on each machine with new credentials.
   - Verify `.gitignore` contains `openclaw/openclaw.json`.
   - Re-enable cron/Task Scheduler on each machine.
   - Run `bash sync.sh` manually on one machine and verify clean operation.

4. **Post-Incident**
   - Add a pre-commit hook to reject files matching `*.json` in `openclaw/` root (except `openclaw.template.json`):
     ```bash
     # .git/hooks/pre-commit
     if git diff --cached --name-only | grep -qE '^openclaw/openclaw\.json$'; then
       echo "ERROR: openclaw.json must not be committed"
       exit 1
     fi
     ```
   - Document the incident in a post-mortem note.

---

### 4.2 SEV-2: Unauthorized Peer or Sync Integrity Compromise

**Trigger:** Unknown hostname in `timestamps/`, unexpected git author, or config file overwritten with suspicious content.

**Steps:**

1. **Contain (0-60 min)**
   - Disable cron on all machines (same commands as SEV-1 Step 1).
   - Identify the unauthorized entry:
     ```bash
     ls timestamps/
     git log --all --format='%H %an %ae %s' | grep -v "your-known-email"
     ```
   - If an unknown peer hostname exists, check who has access to the GitHub repo: `gh api repos/kangnam7654/ai-config-sync/collaborators`.

2. **Eradicate**
   - Remove the unauthorized peer's timestamp file:
     ```bash
     git rm timestamps/<unknown-hostname>.json
     git rm state/<unknown-hostname>.md
     git commit -m "Remove unauthorized peer: <unknown-hostname>"
     git push origin main
     ```
   - Rotate GitHub deploy keys or personal access tokens.
   - If the repo was accessed by an unauthorized party, rotate ALL credentials referenced in synced configs.

3. **Recover**
   - Review `git diff HEAD~10..HEAD` to identify any config changes made by the unauthorized peer.
   - Revert suspicious changes: `git revert <commit-hash>`.
   - Re-enable cron after confirming clean state.

4. **Post-Incident**
   - Enable GitHub branch protection on `main` (require signed commits if feasible).
   - Add hostname validation to `sync.sh` with an allowlist.

---

### 4.3 SEV-3: Sync Pipeline Failure

**Trigger:** `sync.sh` fails repeatedly, rebase conflicts unresolved, cron not running.

**Steps:**

1. **Diagnose**
   - Run sync manually and capture output:
     ```bash
     bash sync.sh 2>&1 | tee /tmp/sync-debug.log
     ```
   - Check for rebase conflict state:
     ```bash
     git status
     # If "rebase in progress":
     git rebase --abort
     ```
   - Check cron is registered:
     ```bash
     crontab -l | grep ai-config-sync
     ```

2. **Fix**
   - **Rebase conflict:** `git rebase --abort`, then `git pull --rebase origin main`. If conflict persists, `git stash && git pull --rebase origin main && git stash pop`.
   - **Cron missing:** Re-register:
     ```bash
     (crontab -l 2>/dev/null; echo "*/30 * * * * cd /path/to/ai-config-sync && bash sync.sh >> /tmp/sync.log 2>&1") | crontab -
     ```
   - **Python error:** Run directly to isolate:
     ```bash
     python3 sync-timestamps.py /path/to/ai-config-sync $(hostname -s)
     ```

3. **Verify**
   - Run `bash sync.sh` twice in succession; both should succeed.
   - Confirm `git log -1` shows a fresh sync commit with correct hostname.

---

### 4.4 SEV-4: Minor Anomaly

**Trigger:** Timestamp validation warnings, empty directories, state file format issues.

**Steps:**

1. Review the specific warning in sync output.
2. If timestamp drift: check system clock on the affected machine (`date` vs NTP).
3. If stale files in repo: run `sync-timestamps.py` which auto-prunes excluded files and empty directories.
4. No immediate action required; monitor on next sync cycle.

---

## 5. Communication

| Audience | Channel | When |
|----------|---------|------|
| Self (developer) | Terminal output + `/tmp/sync.log` | Every sync cycle |
| GitHub (audit) | Git commit history | Every sync cycle |
| Future self | Post-mortem in `docs/` directory | After SEV-1 or SEV-2 |

Since this is a single-developer project, there is no external escalation path. All incidents are self-managed. If a SEV-1 involves a third-party service (e.g., compromised API key used on Anthropic/OpenAI), contact that provider's security team via their documented abuse/security channel.

---

## 6. Prevention Measures

### 6.1 Currently Implemented

| Control | Implementation |
|---------|---------------|
| Secret file exclusion | `openclaw.json` excluded from git tracking; `openclaw.template.json` only |
| Whitelist sync for claude-code | `CLAUDE_INCLUDES` set restricts synced files |
| Exclude patterns | `EXCLUDES` dict blocks history, cache, debug, telemetry files |
| Path traversal prevention | `validate_filepath()` blocks `..`, absolute paths, null bytes |
| Timestamp validation | `validate_timestamp()` rejects negative and future-drifted (>24h) values |
| Hostname validation | `validate_hostname()` enforces RFC 952/1123 |
| Windows pull-only | Windows machines receive configs but never push (reduced attack surface) |
| Scoped git add | `sync.sh` adds only `openclaw/workspace claude-code timestamps state` paths, not `git add .` |

### 6.2 Recommended Additions

| Control | Priority | Description |
|---------|----------|-------------|
| Pre-commit hook for secrets | High | Reject commits containing `openclaw.json` or patterns matching API keys |
| Signed commits | Medium | `git config commit.gpgsign true` to detect unauthorized commits |
| Peer hostname allowlist | Medium | Hardcode known hostnames; reject unknown peers in `load_peer_timestamps()` |
| File integrity checksums | Low | Store SHA-256 hashes alongside timestamps for tamper detection |
| Backup before sync | Low | Snapshot `~/.claude` and `~/.openclaw/workspace` before each sync cycle |

---

## 7. Recovery Resources

| Resource | Location |
|----------|----------|
| Sync script | `sync.sh` (repo root) |
| Core sync logic | `sync-timestamps.py` (repo root) |
| macOS/Ubuntu setup | `setup-mac.sh` |
| Windows setup | `setup-windows.sh` |
| Machine state snapshots | `state/<hostname>.md` |
| Timestamp records | `timestamps/<hostname>.json` |
| Config template | `openclaw/openclaw.template.json` |

### Full Recovery from Scratch

If a machine is compromised or needs complete re-setup:

1. Revoke all credentials on the compromised machine.
2. On a clean machine, clone the repo: `git clone git@github.com:kangnam7654/ai-config-sync.git`
3. Run the appropriate setup script: `bash setup-mac.sh` or `bash setup-windows.sh`.
4. Manually recreate `~/.openclaw/openclaw.json` from `openclaw.template.json` with fresh credentials.
5. Run `bash sync.sh` to pull latest configs from peers.
6. Verify sync output shows no errors and `state/<hostname>.md` is generated correctly.

---

## 8. Playbook Maintenance

- Review this playbook quarterly or after any SEV-1/SEV-2 incident.
- Update the asset table when new sync sections or machines are added.
- Update severity definitions if the project scope changes (e.g., team size increases, new data types synced).
