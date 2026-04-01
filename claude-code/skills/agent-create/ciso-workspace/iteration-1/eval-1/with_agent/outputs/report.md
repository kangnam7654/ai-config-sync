## Security Posture Report

### Application Security Profile
- Application type: CLI / automation tool (cron-based config synchronization)
- Tech stack: Python 3.10+, Bash, Git (no database, no web framework, no cache, no queue)
- Authentication: SSH key (Git over SSH to GitHub) / none (no application-level auth)
- Deployment: GitHub (public repository), local machines (macOS, Ubuntu, Windows), no container, no serverless
- External services: 1 service (GitHub — send/receive via git push/pull)
- Existing security controls:
  - `.gitignore` excludes credentials/, .env, auth-profiles.json, openclaw.json
  - `CLAUDE_INCLUDES` whitelist limits claude-code sync scope
  - `EXCLUDES` dict blocks sensitive patterns (history.jsonl, cache, debug, sessions)
  - `validate_filepath()` blocks path traversal (`.."`, null bytes, absolute paths)
  - `validate_hostname()` enforces RFC 952/1123 format
  - `validate_timestamp()` rejects negative/far-future values
  - `umask 077` for generated config files containing tokens
  - CI/CD runs pytest with coverage on 3 OS x 2 Python versions
  - Template pattern separates sensitive `openclaw.json` from tracked `openclaw.template.json`

### Data Classification

| Data Field | Location | Sensitivity | Current Control | Required Control | Gap |
|---|---|---|---|---|---|
| Google OAuth client_secrets (GOCSPX-*) | `claude-code/agent-memory/security-reviewer/project_kangnam_credentials.md`, `claude-code/agent-memory/llm-subscription-auth.md` | CONFIDENTIAL | None — committed to PUBLIC repo in plaintext | Must not be in any tracked file; remove from git history | **YES — CRITICAL** |
| GitHub Copilot client_id | `claude-code/agent-memory/llm-subscription-auth.md` | PUBLIC | Committed to repo | Public PKCE client ID — acceptable | NO |
| OpenClaw gateway token | `openclaw/openclaw.template.json` (placeholder only) | RESTRICTED | Template uses `<REPLACE_WITH_NEW_TOKEN>` placeholder; actual token excluded via .gitignore | Meets requirement | NO |
| API key instructions (example format `sk-ant-...`) | `setup-mac.sh`, `README.md` | PUBLIC | Example string only, not a real key | Meets requirement | NO |
| Hostname | `timestamps/*.json`, `state/*.md` | INTERNAL | Committed to public repo | Should be in private repo or redacted | YES |
| OS version, cron schedule | `state/*.md` | INTERNAL | Committed to public repo | Reveals machine environment to attackers; should be in private repo | YES |
| File path listings (agent-memory, skills, workspace contents) | `claude-code/`, `openclaw/workspace/` | INTERNAL | Committed to public repo | Reveals internal tooling, project names, agent configurations | YES |
| Agent/skill definitions (prompt content) | `claude-code/agents/`, `claude-code/skills/`, `openclaw/workspace/agents/` | INTERNAL | Committed to public repo | Proprietary prompt engineering; exposure risk is intellectual property loss | YES |
| Timestamp file paths | `timestamps/*.json` | INTERNAL | Committed to public repo | Reveals full directory structure of `~/.claude/` and `~/.openclaw/` | YES |
| GitHub auth token (runtime) | `openclaw/workspace/sync-openclaw.sh` line 41-42 | RESTRICTED | Token is generated at runtime via `gh auth token`, not hardcoded | Pattern embeds token in URL which may leak to shell history/process list; use credential helper instead | YES |

### Compliance Matrix

No compliance frameworks applicable — application does not process regulated end-user data (PII, payment data, health records). The synced data belongs to the developer/operator themselves. However, the OAuth client_secrets exposure described above affects other projects that are referenced in agent memory files.

### Threat Register

| ID | STRIDE | Threat | Likelihood | Impact | Risk Score | Current Control | Recommended Control |
|---|---|---|---|---|---|---|---|
| T-01 | Information Disclosure | OAuth client_secrets exposed in public Git history — `GOCSPX-4uHgMPm-...` and `GOCSPX-K58FWR4...` are committed to a PUBLIC repository. Anyone can clone the repo and extract these secrets. | 5 | 4 | **20 (CRITICAL)** | None | 1. Remove files from git history (git filter-repo). 2. Rotate affected Google OAuth credentials. 3. Make repo private or remove sensitive agent-memory files from sync scope. |
| T-02 | Information Disclosure | Machine fingerprinting via `state/*.md` — OS version, hostname, cron schedule, workspace file listings all publicly visible. Enables targeted attacks against specific machines. | 5 | 2 | **10 (MEDIUM)** | None | Make repository PRIVATE. State files contain no value to third parties and significant reconnaissance value to attackers. |
| T-03 | Tampering | Unauthenticated config injection — any collaborator with push access (or via fork+PR merge) can inject malicious content into `claude-code/` which gets auto-synced to `~/.claude/` on all machines every 30 minutes. | 2 | 5 | **10 (MEDIUM)** | Git SSH auth limits push to repo owner | Add GPG commit signing verification before applying synced content. Consider branch protection rules with required reviews. |
| T-04 | Information Disclosure | Intellectual property leakage — 1116 claude-code files and 614 openclaw files including custom agents, skills, prompt engineering, and project memory are publicly accessible. | 5 | 3 | **15 (HIGH)** | None | Make repository PRIVATE. These files represent significant proprietary work. |
| T-05 | Tampering | Cron job runs with full user permissions — `sync.sh` executes `git fetch`, Python script, and `git push` as the logged-in user. A compromised sync-timestamps.py could execute arbitrary code on all synced machines within 30 minutes. | 2 | 5 | **10 (MEDIUM)** | Code changes auto-pulled via `git pull --rebase` in sync.sh | Pin sync.sh to a known-good commit hash, or verify script integrity before execution. |
| T-06 | Elevation of Privilege | Windows `git reset --hard origin/main` overwrites ALL local files — the pull-only path in sync.sh (line 153) does a hard reset, which could overwrite locally-modified scripts or config with malicious versions from remote. | 2 | 4 | **8 (MEDIUM)** | Only runs on Windows/pull-only machines | Replace `git reset --hard` with selective file checkout for sync target directories only. |
| T-07 | Spoofing | Hostname spoofing in timestamps — an attacker who gains push access could create a `timestamps/victim-hostname.json` with future timestamps, causing the victim's next sync to overwrite local files with attacker-controlled content. | 2 | 4 | **8 (MEDIUM)** | `validate_hostname()` validates format but not authenticity | Add HMAC signature to timestamp files to verify author authenticity. |
| T-08 | Repudiation | No audit logging — sync operations produce only stdout/stderr output redirected to a local log file. No tamper-proof audit trail exists. If a malicious sync overwrites files, there is no reliable forensic record. | 3 | 2 | **6 (MEDIUM)** | Basic stdout logging to `/tmp/ai-config-sync.log` | Implement structured logging with timestamps, file hashes before/after sync, and retention policy. Log to append-only location. |
| T-09 | Denial of Service | Cron failure cascades — if sync.sh fails (e.g., network timeout, git conflict), the script exits with `set -e`. Subsequent runs may encounter stale locks or dirty git state, preventing all future syncs until manual intervention. | 3 | 1 | **3 (LOW)** | Push conflict handling with rebase retry (sync.sh lines 131-146) | Add git lock file cleanup at script start. Implement health check/alerting for consecutive sync failures. |
| T-10 | Information Disclosure | Sync log at world-readable path — cron writes to `/tmp/ai-config-sync.log` (state file shows this path), which is readable by all users on multi-user systems. | 3 | 2 | **6 (MEDIUM)** | None | Change log path to `~/.local/share/ai-config-sync/sync.log` with 600 permissions. setup.sh already creates this path with `chmod 700` but the actual cron entry in state file uses `/tmp/`. |

### Domain Scores

| Domain | Score | Key Finding |
|---|---|---|
| 1. Policy & Governance | 3/10 | No written security policy exists; CLAUDE.md contains development governance but no security-specific policies for data handling, incident response, or access control. |
| 2. Data Protection | 2/10 | Two Google OAuth client_secrets are committed in plaintext to a PUBLIC GitHub repository; no encryption at rest for synced configuration data; machine state information publicly exposed. |
| 3. Access Control | 4/10 | Git SSH key provides basic authentication for push; however, the repo is PUBLIC so all content is readable without auth; no MFA enforcement on GitHub account verified; no access review process. |
| 4. Threat & Vulnerability Mgmt | 4/10 | Input validation functions exist (hostname, filepath, timestamp) with good test coverage; CI/CD with pytest on 3 platforms; however, no dependency scanning, no threat model documented prior to this assessment, no security testing in pipeline. |
| 5. Incident Response Readiness | 1/10 | No incident response plan; no monitoring or alerting for sync failures or unauthorized changes; no communication plan; no designated security contact. |
| 6. Third-Party Risk | 5/10 | Single external dependency (GitHub) with well-understood security posture; SSH transport provides encryption in transit; however, no contractual security agreement beyond GitHub ToS; no assessment of GitHub Actions runner security for CI. |
| **Security Posture Score (SPS)** | **3.1/10** | |

SPS Calculation: (3 x 0.15) + (2 x 0.20) + (4 x 0.20) + (4 x 0.20) + (1 x 0.10) + (5 x 0.15) = 0.45 + 0.40 + 0.80 + 0.80 + 0.10 + 0.75 = **3.30/10**

### Verdict

**CRITICAL** (SPS 3.3 < 4.0): Security posture is insufficient for operation. Immediate action required on 2 CRITICAL items and 5 HIGH/MEDIUM items. The most urgent issue is that OAuth client secrets from other projects are exposed in a PUBLIC GitHub repository, creating immediate credential compromise risk.

### Remediation Roadmap

| Priority | Finding | Risk Score | Remediation | Effort | Impact on Operations |
|---|---|---|---|---|---|
| 1 | T-01: OAuth client_secrets in public git history | 20 (CRITICAL) | **Immediate**: (a) Run `git filter-repo` to remove `claude-code/agent-memory/security-reviewer/project_kangnam_credentials.md` and `claude-code/agent-memory/llm-subscription-auth.md` from ALL history. (b) Rotate both GOCSPX-* credentials in Google Cloud Console. (c) Force-push cleaned history. (d) Add these file patterns to `.gitignore`. | 2 hours + credential rotation in external projects | One-time force-push required; all clones must re-clone. Credential rotation affects dependent projects. |
| 2 | T-04 + T-02: Public repo exposes IP and machine state | 15 (HIGH) | **Change repository visibility to PRIVATE**. This single action mitigates T-01 exposure surface, T-02 machine fingerprinting, and T-04 intellectual property leakage simultaneously. | 5 minutes (GitHub Settings > Danger Zone > Change visibility) | No operational impact. All existing SSH clones continue to work. |
| 3 | T-03: Unauthenticated config injection via auto-sync | 10 (MEDIUM) | Enable GitHub branch protection on `main`: require signed commits, require PR review before merge. Add integrity check in sync.sh before applying synced content. | 2 hours | Adds manual approval step for external contributions (none currently exist since this is a personal repo, but defense-in-depth). |
| 4 | T-05: Auto-pulled code executes with full user permissions | 10 (MEDIUM) | Pin sync.sh execution: verify `sync-timestamps.py` hash before execution, or separate code updates from data sync (only auto-sync data directories, require manual pull for script changes). | 4 hours | Slightly more complex update process for script changes. |
| 5 | T-06: Windows hard reset overwrites all files | 8 (MEDIUM) | Replace `git reset --hard origin/main` with targeted checkout: `git checkout origin/main -- claude-code/ timestamps/` to only update sync target directories. | 1 hour | No operational impact; only sync target files are updated as before. |
| 6 | T-07: Hostname spoofing in timestamps | 8 (MEDIUM) | Add HMAC-SHA256 signature field to timestamp JSON using a per-machine secret stored outside the repo (e.g., `~/.config/ai-config-sync/hmac-key`). Verify signature before applying peer timestamps. | 6 hours | Requires initial key setup on each machine. REQUIRES NEW TOOLING: hmac key generation and verification logic in sync-timestamps.py. |
| 7 | T-10: Sync log at world-readable `/tmp/` path | 6 (MEDIUM) | Update the cron entry to use `~/.local/share/ai-config-sync/sync.log` instead of `/tmp/ai-config-sync.log`. The setup.sh already creates this directory with `chmod 700`. | 15 minutes | No operational impact. |
| 8 | T-08: No audit logging | 6 (MEDIUM) | Add structured JSON logging to sync-timestamps.py: log each file action (copy/overwrite/skip/delete) with before/after file hashes, timestamp, and peer source. Write to `~/.local/share/ai-config-sync/audit.jsonl`. | 4 hours | Adds ~50ms per sync cycle for hash computation. Disk usage ~1KB per sync cycle. |
| 9 | D1: No security policy | - | Create `docs/SECURITY.md` defining: data classification for synced files, incident response contacts, credential handling requirements, and access control expectations. | 2 hours | No operational impact. |
| 10 | D5: No incident response plan | - | Draft incident response playbook covering: (a) compromised credentials detected in repo, (b) malicious content synced to local machine, (c) unauthorized push to repo. Include step-by-step response for each scenario. | 3 hours | No operational impact. Establishes process for future incidents. |
| 11 | T-09: Cron failure cascades | 3 (LOW) | Add `git stash` or lock file cleanup at sync.sh start. Implement simple health check: if last N sync attempts failed, send notification (e.g., write to a health file checked by a separate monitor). | 2 hours | No operational impact. Improves reliability. |
