# Incident Response Playbook

**Organization:** KangNam Dev
**System:** ai-config-sync (Ubuntu / MacBook / Windows cross-platform config synchronization)
**Data Types:** Development configuration files (IDE settings, CLI settings, API key references)
**Team Size:** 1 developer
**Last Updated:** 2026-03-26

---

## 1. Scope and Objectives

This playbook covers incidents related to the ai-config-sync system, which synchronizes OpenClaw workspace and Claude Code settings across macOS, Ubuntu, and Windows machines using a newest-wins merge strategy via git. The system runs automatically every 30 minutes via cron (Unix) or Task Scheduler (Windows).

**Objectives:**
- Detect and contain configuration corruption or unauthorized modifications quickly
- Prevent propagation of compromised configurations across all synced machines
- Restore known-good configurations with minimal downtime
- Preserve evidence for post-incident analysis

---

## 2. Asset Inventory

| Asset | Path | Sync Direction | Sensitivity |
|---|---|---|---|
| OpenClaw workspace | `~/.openclaw/workspace` | Bidirectional (Mac/Ubuntu) | Medium -- contains agent memory, skills, prompts |
| Claude Code settings | `~/.claude` | Bidirectional (Mac/Ubuntu), Pull-only (Windows) | High -- contains `settings.json`, `CLAUDE.md`, skills, agents, plugins |
| API key references | `openclaw.template.json` | Template only (values never synced) | Critical -- template references sensitive credential paths |
| Timestamp metadata | `timestamps/{hostname}.json` | Bidirectional | Low -- operational metadata |
| Device state | `state/{hostname}.md` | Bidirectional | Low -- environment info |
| Git repository | GitHub remote `origin/main` | Push/Pull | Medium -- central sync hub |

**Whitelist-controlled files (Claude Code):** `settings.json`, `CLAUDE.md`, `stop-hook-git-check.sh`, `agents/`, `plugins/`, `skills/`, `agent-memory/`, `memory/`, `todos/`, `teams/`

---

## 3. Incident Classification

### Severity Levels

| Level | Definition | Examples | Response Time |
|---|---|---|---|
| SEV-1 Critical | Credential exposure or active unauthorized access | API keys committed to repo; `.env` or `openclaw.json` pushed; unauthorized git push detected | Immediate (< 15 min) |
| SEV-2 High | Configuration corruption propagating across machines | Malformed `settings.json` overwriting all devices; sync loop deleting valid files; malicious content injected into `CLAUDE.md` | < 1 hour |
| SEV-3 Medium | Sync failure or single-machine configuration issue | `sync.sh` cron failure; rebase conflict blocking sync; timestamp desync | < 4 hours |
| SEV-4 Low | Non-critical anomaly | State file not updating; cosmetic config drift; single excluded file leaking into repo | < 24 hours |

### Incident Categories

1. **Credential Exposure** -- Sensitive values (API keys, tokens) accidentally committed
2. **Configuration Corruption** -- Broken or malicious config propagated via newest-wins merge
3. **Unauthorized Modification** -- Unexpected changes to synced files from unknown source
4. **Sync System Failure** -- Cron/scheduler stops running, git operations fail
5. **Data Loss** -- Files deleted by sync logic or git operations unexpectedly
6. **Supply Chain Compromise** -- Malicious content injected into skills, agents, or plugins

---

## 4. Detection Methods

### Automated Detection

| Method | What It Detects | Implementation |
|---|---|---|
| Git push notification | Any change to the remote repository | GitHub webhook or email notification on `origin/main` push |
| Sync script exit code monitoring | Script errors (set -e causes immediate exit) | Cron job wrapper: `bash sync.sh 2>&1 \| tee -a /var/log/ai-config-sync.log; echo "EXIT:$?"` |
| Timestamp anomaly | Future timestamps (>24h drift) rejected by `validate_timestamp()` | Built into `sync-timestamps.py` |
| Path traversal attempt | `..` or absolute paths in peer timestamps | Built into `validate_filepath()` |
| Hostname validation | Malformed hostnames rejected | Built into `validate_hostname()` (RFC 952/1123) |

### Manual Detection (Periodic Review)

| Check | Frequency | Command |
|---|---|---|
| Review recent commits | Daily | `git log --oneline -20` |
| Verify no secrets in repo | Weekly | `git log --all --diff-filter=A --name-only -- '*.json' '*.env' '*credentials*'` |
| Check cron is active | Weekly | `crontab -l \| grep ai-config-sync` |
| Verify EXCLUDES effectiveness | Monthly | Check `openclaw/openclaw.json` is not tracked: `git ls-files openclaw/openclaw.json` |
| Audit CLAUDE_INCLUDES whitelist | Monthly | `python3 sync-timestamps.py --list-includes` and verify scope is appropriate |

---

## 5. Incident Response Procedures

### 5.1 SEV-1: Credential Exposure

**Trigger:** API key, token, password, or `openclaw.json` (with real values) found in git history.

**Steps:**

1. **CONTAIN (Immediate)**
   ```bash
   # Stop all sync jobs on all machines
   # Mac/Ubuntu:
   crontab -l | grep -v ai-config-sync | crontab -
   # Windows: schtasks /delete /tn "ai-config-sync" /f
   ```

2. **REVOKE CREDENTIALS**
   - Identify which credentials were exposed by reviewing the commit diff
   - Rotate every exposed key/token immediately at the provider's dashboard
   - Update local credential stores (`~/.openclaw/openclaw.json` etc.) with new values

3. **PURGE FROM GIT HISTORY**
   ```bash
   # Use git-filter-repo or BFG to remove the sensitive file from all history
   # Example with BFG:
   bfg --delete-files openclaw.json
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   git push origin main --force
   ```

4. **VERIFY**
   - Search entire git history: `git log --all -p -- '*openclaw.json*'`
   - Confirm the file is in `.gitignore` or excluded by the `git add` path list in `sync.sh`
   - Confirm `sync.sh` line 125 only adds: `openclaw/workspace claude-code timestamps state`

5. **RESTORE SYNC**
   - On each machine: `git fetch origin main && git reset --hard origin/main`
   - Re-enable cron/scheduler
   - Run `bash sync.sh` manually and verify clean operation

6. **POST-INCIDENT**
   - Add the leaked file pattern to `EXCLUDES` in `sync-timestamps.py` if not already excluded
   - Document the incident (see Section 7)

---

### 5.2 SEV-2: Configuration Corruption Propagation

**Trigger:** A corrupted or malicious configuration file has been propagated to one or more machines via the newest-wins merge.

**Steps:**

1. **CONTAIN**
   ```bash
   # Create .pull-only on all machines to prevent further propagation
   touch ~/.pull-only  # or in the sync dir
   # Or stop cron entirely
   crontab -l | grep -v ai-config-sync | crontab -
   ```

2. **IDENTIFY THE CORRUPT FILE(S)**
   ```bash
   # Check recent sync activity
   git log --oneline --name-only -10
   # Compare timestamps to find which peer introduced the change
   cat timestamps/*.json | python3 -m json.tool
   ```

3. **RESTORE FROM KNOWN-GOOD STATE**
   ```bash
   # Find last known-good commit
   git log --oneline -20
   # Restore specific file from a good commit
   git show <good-commit>:claude-code/settings.json > ~/.claude/settings.json
   git show <good-commit>:claude-code/settings.json > claude-code/settings.json
   ```

4. **FORCE CORRECT STATE TO REPO**
   ```bash
   git add claude-code/ openclaw/workspace/ timestamps/ state/
   git commit -m "fix: restore known-good config after corruption incident"
   git push origin main
   ```

5. **SYNC ALL MACHINES**
   - Remove `.pull-only` files
   - Run `bash sync.sh` on each machine
   - Verify configurations are correct

---

### 5.3 SEV-2: Supply Chain -- Malicious Skill/Agent/Plugin

**Trigger:** Suspicious or unauthorized content detected in `skills/`, `agents/`, or `plugins/` directories.

**Steps:**

1. **CONTAIN**
   - Stop sync on all machines
   - Do NOT execute any Claude Code commands until the malicious content is removed

2. **IDENTIFY**
   ```bash
   # List recently changed files in sensitive directories
   git log --oneline --name-only --since="7 days" -- claude-code/skills/ claude-code/agents/ claude-code/plugins/
   # Diff against known-good state
   git diff <last-known-good-commit> -- claude-code/skills/ claude-code/agents/ claude-code/plugins/
   ```

3. **REMOVE**
   ```bash
   # Remove the malicious files from repo and local
   rm -rf claude-code/skills/<malicious-skill>
   rm -rf ~/.claude/skills/<malicious-skill>
   git add -A claude-code/
   git commit -m "fix: remove malicious skill/agent/plugin"
   git push origin main
   ```

4. **AUDIT**
   - Review all remaining skills, agents, and plugins for tampering
   - Check `CLAUDE.md` files for injected instructions
   - Verify `CLAUDE_INCLUDES` whitelist has not been modified

---

### 5.4 SEV-3: Sync System Failure

**Trigger:** Sync has not run successfully for more than 1 hour (2 missed cycles).

**Steps:**

1. **DIAGNOSE**
   ```bash
   # Check if cron is running
   crontab -l | grep ai-config-sync
   # Check last sync time via state file
   cat state/$(hostname -s).md | head -5
   # Run sync manually to see errors
   bash sync.sh
   ```

2. **COMMON FIXES**

   | Symptom | Cause | Fix |
   |---|---|---|
   | `FETCH_HEAD` not found | No remote or first run | `git fetch origin main` |
   | Rebase conflict | Concurrent edits on same file | `git rebase --abort && git pull --rebase origin main` |
   | Push rejected | Remote has newer commits | Automatic retry built into `sync.sh`; if persistent, manual `git pull --rebase origin main` |
   | Python encoding error (Windows) | CP949 encoding issue | Verify `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` are set |
   | Permission denied | SSH key or file permission issue | `ssh -T git@github.com` to test; check file permissions |

3. **VERIFY RECOVERY**
   ```bash
   bash sync.sh
   git log --oneline -3  # Confirm new sync commit appeared
   ```

---

### 5.5 SEV-3: Data Loss

**Trigger:** Files unexpectedly deleted from local machine or repository after sync.

**Steps:**

1. **IDENTIFY WHAT WAS LOST**
   ```bash
   # Check git history for deleted files
   git log --diff-filter=D --name-only --oneline -20
   ```

2. **RESTORE FROM GIT**
   ```bash
   # Restore a specific file
   git show HEAD~1:path/to/deleted/file > restored-file
   # Or restore from a specific commit
   git show <commit>:path/to/file > restored-file
   ```

3. **RESTORE FROM LOCAL BACKUPS**
   - Check Time Machine (macOS) or filesystem snapshots
   - The local copies at `~/.openclaw/workspace` and `~/.claude` may still have the files if the deletion only affected the repo copy

4. **ROOT CAUSE**
   - Check if the file was removed from `CLAUDE_INCLUDES` whitelist
   - Check if a new `EXCLUDES` pattern is matching too broadly
   - Check if a peer with timestamp 0.0 triggered a "peer is newer" false positive

---

## 6. Recovery Procedures

### 6.1 Full System Recovery (Nuclear Option)

Use when the repository state is irrecoverably corrupted.

```bash
# 1. Back up current local configs
cp -r ~/.openclaw/workspace ~/backup-openclaw-$(date +%s)
cp -r ~/.claude ~/backup-claude-$(date +%s)

# 2. Reset repo to a known-good commit
git log --oneline -30  # Find the last good commit
git reset --hard <known-good-commit>
git push origin main --force  # WARNING: destructive

# 3. On each other machine
git fetch origin main
git reset --hard origin/main

# 4. Re-run sync from scratch
rm -f timestamps/*.json  # Clear stale timestamps
bash sync.sh

# 5. Verify
cat state/$(hostname -s).md
git log --oneline -5
```

### 6.2 Single Machine Recovery

```bash
# Reset this machine's repo copy to match remote
git fetch origin main
git reset --hard origin/main

# Re-run sync to restore local files from repo
bash sync.sh
```

### 6.3 Restore Specific Config File

```bash
# From git history
git log --oneline -- claude-code/settings.json
git show <commit>:claude-code/settings.json > ~/.claude/settings.json

# Also update repo copy
cp ~/.claude/settings.json claude-code/settings.json
```

---

## 7. Post-Incident Documentation

After every SEV-1 or SEV-2 incident, create a file at `docs/incidents/YYYY-MM-DD-brief-title.md` with:

```markdown
# Incident: [Brief Title]
**Date:** YYYY-MM-DD
**Severity:** SEV-N
**Duration:** Start time to resolution time
**Affected machines:** List of hostnames

## Timeline
- HH:MM -- Detection: How the incident was detected
- HH:MM -- Containment: Actions taken to stop propagation
- HH:MM -- Resolution: How the issue was fixed

## Root Cause
One paragraph describing the root cause.

## Impact
What was affected and for how long.

## Action Items
- [ ] Preventive measure 1
- [ ] Preventive measure 2
```

---

## 8. Preventive Controls Checklist

### Already Implemented in ai-config-sync

- [x] Path traversal prevention (`validate_filepath` rejects `..`, absolute paths, null bytes)
- [x] Hostname validation (RFC 952/1123 compliance)
- [x] Timestamp validation (rejects negative values and >24h future drift)
- [x] Whitelist-based sync for Claude Code (`CLAUDE_INCLUDES`)
- [x] Exclusion patterns for sensitive/transient files (`EXCLUDES` dict)
- [x] `openclaw.json` excluded from sync (only `openclaw.template.json` tracked)
- [x] Scoped `git add` -- only `openclaw/workspace`, `claude-code`, `timestamps`, `state` paths are staged
- [x] Windows pull-only mode prevents untrusted push from company machine
- [x] UTF-8 encoding enforced on all file I/O and subprocess calls

### Recommended Additional Controls

- [ ] Enable GitHub branch protection on `main` (require signed commits)
- [ ] Add a `git log` audit script that runs weekly and alerts on unexpected commit authors
- [ ] Add `.gitignore` entries for common secret file patterns (`*.env`, `*credentials*`, `*secret*`)
- [ ] Set up GitHub notification (email/webhook) on every push to `origin/main`
- [ ] Periodically run `git secrets --scan` or `trufflehog` against the repository
- [ ] Back up `~/.openclaw/workspace` and `~/.claude` to a separate location (Time Machine, rsync) independent of this sync system
- [ ] Add a pre-commit hook that rejects files matching sensitive patterns

---

## 9. Communication Plan

Since this is a single-developer operation, communication is simplified:

| Event | Action |
|---|---|
| SEV-1 detected | Immediately stop all work; follow playbook Section 5.1 |
| SEV-2 detected | Note the issue; follow playbook within 1 hour |
| Sync failure noticed | Check within 4 hours; sync has 30-min retry cycle so transient failures self-heal |
| Credential rotation completed | Update all machines' local credential stores before re-enabling sync |

If the team grows, expand this section to include notification channels (Slack, email) and escalation paths.

---

## 10. Playbook Review Schedule

| Frequency | Action |
|---|---|
| Quarterly | Review and update this playbook |
| After every SEV-1/SEV-2 | Update playbook with lessons learned |
| After sync system architecture change | Review all sections for accuracy |
| After adding new sync targets | Update Asset Inventory (Section 2) and EXCLUDES/INCLUDES |

---

## Appendix A: Key File Locations

| File | Purpose |
|---|---|
| `sync.sh` | Main sync orchestrator (cron entry point) |
| `sync-timestamps.py` | Newest-wins merge logic |
| `timestamps/{hostname}.json` | Per-machine file modification timestamps |
| `state/{hostname}.md` | Per-machine environment snapshot |
| `setup-mac.sh` | macOS/Ubuntu initial setup |
| `setup-windows.sh` | Windows initial setup |
| `CLAUDE.md` | Project-level Claude Code instructions |
| `openclaw/workspace/` | Synced OpenClaw workspace files |
| `claude-code/` | Synced Claude Code configuration files |

## Appendix B: Emergency Contacts and Resources

| Resource | Location |
|---|---|
| GitHub repository | `git@github.com:kangnam7654/ai-config-sync.git` |
| API key provider dashboards | Refer to `~/.openclaw/openclaw.json` for which providers are in use |
| Git documentation | `https://git-scm.com/docs` |
| BFG Repo-Cleaner (for history purging) | `https://rtyley.github.io/bfg-repo-cleaner/` |
