## Security Posture Report

### Application Security Profile
- Application type: CLI (shell + Python scripts for cross-device config synchronization)
- Tech stack: Python 3.10+, Bash, Git (as transport layer), no database, no cache, no message queue
- Authentication: none (relies on Git SSH key for push access; no application-level auth)
- Deployment: self-hosted on personal devices (macOS, Ubuntu, Windows); cron/Task Scheduler (30-minute interval); no cloud/container/serverless
- External services: 3 services (GitHub - send/receive via git push/pull, Notion API - send/receive via `cal_sync.py`, Google Calendar - send/receive via `gog` CLI)
- Existing security controls: `.gitignore` excludes `credentials/`, `auth-profiles.json`, `.env`, `openclaw/openclaw.json`; `CLAUDE_INCLUDES` whitelist limits claude-code sync scope; `EXCLUDES` dict filters sensitive directories; `validate_filepath()` blocks path traversal (`..`, absolute paths, null bytes); `validate_timestamp()` rejects negative/future-drift values; `umask 077` on generated config files; gateway binds to loopback only; Notion API key loaded from environment variable (not hardcoded)

### Data Classification

| Data Field | Location | Sensitivity | Current Control | Required Control | Gap |
|---|---|---|---|---|---|
| Third-party name + title + phone number: "현정화 과장 010-3332-7533" | `openclaw/workspace/memory/2026-02-23.md:7` | CONFIDENTIAL (THIRD-PARTY PII) | None -- committed to PUBLIC GitHub repo | Immediate removal from repo + git history rewrite; never commit third-party PII | YES - CRITICAL |
| Owner's full home address: "서울 동작구 둔총동 올림픽파크 포레온 1단지 104동 206호" | `openclaw/workspace/notion_to_gcal_sync.sh:76` | CONFIDENTIAL | None -- committed to PUBLIC GitHub repo | Remove from repo; move to local-only file excluded by `.gitignore` | YES - CRITICAL |
| Owner's previous home address: "동작구 상도로 54길 54 이에스하임 12차 1동 401호" | `openclaw/workspace/notion_to_gcal_sync.sh:83` | CONFIDENTIAL | None -- committed to PUBLIC GitHub repo | Remove from repo | YES - CRITICAL |
| Owner's salary: "연봉 5,600만원" | `openclaw/workspace/memory/2026-02-23.md:8` | CONFIDENTIAL | None -- committed to PUBLIC GitHub repo | Remove from repo | YES - CRITICAL |
| Owner's employer + department + position | `openclaw/workspace/memory/2026-02-23.md:5-8` | CONFIDENTIAL | None -- committed to PUBLIC GitHub repo | Remove from repo | YES - CRITICAL |
| Owner's email: `kangnam7653@gmail.com` | `openclaw/workspace/cal_sync.py:13`, `notion_to_gcal_sync.sh:3,5`, `memory/2026-02-23.md:13`, `memory/2026-03-07.md:36` | CONFIDENTIAL | None -- committed to PUBLIC GitHub repo | Move to environment variable or local config | YES |
| Owner's Telegram ID: `5512922109` | `openclaw/workspace/memory/2026-02-23.md:44` | CONFIDENTIAL | None -- committed to PUBLIC GitHub repo | Remove from repo | YES |
| Notion Database ID | `openclaw/workspace/cal_sync.py:12` | INTERNAL | None -- committed to PUBLIC repo | Move to environment variable; database ID alone enables enumeration if API key is guessed/leaked | YES |
| Employment history (companies, dates, positions) | `openclaw/workspace/notion_to_gcal_sync.sh:72-122` | CONFIDENTIAL | None -- committed to PUBLIC GitHub repo | Remove from repo | YES - CRITICAL |
| Loan/financial events: "포레온 잔금 실행", "전세" | `openclaw/workspace/notion_to_gcal_sync.sh:77-78` | CONFIDENTIAL | None -- committed to PUBLIC GitHub repo | Remove from repo | YES |
| GitHub username in script pattern: `kangnam7654:${TOKEN}@github.com` | `openclaw/workspace/sync-openclaw.sh:42` | INTERNAL | Token fetched at runtime (not hardcoded) | Use SSH remote or git credential helper; URL-embedded tokens leak to process table/shell history | YES |
| Device hostnames and OS versions | `state/*.md` | INTERNAL | No access control | Acceptable for internal use; consider if PUBLIC repo exposure is intended | LOW |
| `openclaw.template.json` gateway token placeholder | `openclaw/openclaw.template.json:52` | PUBLIC (placeholder only) | Token placeholder `<REPLACE_WITH_NEW_TOKEN>` is not a real secret | Meets requirement (actual token in `.gitignore`-protected `openclaw.json`) | NO |
| Cron schedule and log paths | `state/Kangnamui-MacBookPro.md:17` | INTERNAL | None | Low risk; reveals sync interval and log location | LOW |

### Compliance Matrix

| Framework | Requirement | Article | Status | Evidence |
|---|---|---|---|---|
| PIPA | Consent collection with purpose for third-party PII | Art. 15 | FAIL | Third-party PII ("현정화 과장 010-3332-7533") committed to public repo without consent. No consent mechanism exists. |
| PIPA | Purpose limitation | Art. 3 | FAIL | Personal data (addresses, salary, employment history) synced to public GitHub repo exceeds the stated purpose of "config synchronization." |
| PIPA | Destruction after purpose fulfilled | Art. 21 | FAIL | No retention policy. Data persists indefinitely in git history even if deleted from HEAD. |
| PIPA | Encryption of personal data | Art. 29 | FAIL | No encryption at rest for any PII. Files are plaintext in a public git repository. |
| PIPA | Privacy policy disclosure | Art. 30 | UNVERIFIED | No privacy policy found. Personal-use tool may not require one, but third-party PII presence triggers this requirement. |
| PIPA | Cross-border transfer consent | Art. 17 | FAIL | Data is hosted on GitHub (US servers). No consent obtained from third party whose PII is stored. |
| GDPR | Data minimization | Art. 5(1)(c) | FAIL | Sync scope includes personal diary entries, addresses, salary, employment history -- far beyond "config sync" purpose. |
| GDPR | Right to erasure | Art. 17 | FAIL | No mechanism to erase specific data. Git history retains all data permanently. |
| GDPR | Encryption of personal data | Art. 32(1)(a) | FAIL | No encryption. Public plaintext repository. |

### Threat Register

| ID | STRIDE | Threat | Likelihood | Impact | Risk Score | Current Control | Recommended Control |
|---|---|---|---|---|---|---|---|
| T-01 | Information Disclosure | PII (third-party phone number, addresses, salary, employment history) exposed in PUBLIC GitHub repository -- accessible to anyone on the internet | 5 | 5 | 25 (CRITICAL) | None | 1. Make repo PRIVATE immediately. 2. Remove all PII from tracked files. 3. Rewrite git history (`git filter-repo`) to purge PII from all commits. 4. Move personal data files to `.gitignore`-excluded local paths. |
| T-02 | Information Disclosure | Owner's email, Telegram ID, Notion DB ID, home addresses committed to public repo enable targeted social engineering, doxxing, or account enumeration | 5 | 4 | 20 (CRITICAL) | None | Remove all personal identifiers from repo. Use environment variables for service IDs. |
| T-03 | Information Disclosure | `sync-openclaw.sh` embeds `gh auth token` output in HTTPS URL -- token visible in process table (`ps aux`), shell history, and potentially git config | 3 | 4 | 12 (HIGH) | Token fetched at runtime (not hardcoded) | Use SSH remote (`git@github.com:...`) or `GIT_ASKPASS` / credential helper. Remove this script from sync scope. |
| T-04 | Tampering | Any GitHub collaborator or compromised peer device can inject malicious files into `~/.claude/` (agents, skills, plugins) via the sync mechanism -- newest-wins means a tampered timestamp forces file acceptance | 3 | 4 | 12 (HIGH) | `validate_filepath()` blocks path traversal; `CLAUDE_INCLUDES` whitelist limits scope | Add content integrity verification (e.g., hash-based change detection). Consider signing commits from trusted devices. |
| T-05 | Spoofing | Attacker who gains push access to the repo can craft a `timestamps/*.json` file with future timestamps to force overwrite of any synced file on all peer devices | 2 | 4 | 8 (MEDIUM) | `validate_timestamp()` caps future drift at 24 hours | Reduce drift tolerance to 5 minutes. Add commit signature verification (`git verify-commit`). |
| T-06 | Repudiation | No audit logging for sync operations beyond stdout. `sync.sh` output goes to `/tmp/` log (volatile) or `~/.local/share/` (not backed up). No tamper-proof record of what was synced when. | 3 | 2 | 6 (MEDIUM) | Stdout prints sync actions | Write structured JSON logs to persistent, append-only location. Include file hashes and peer identifiers. |
| T-07 | Elevation of Privilege | Synced `agents/`, `skills/`, `plugins/` files execute with full Claude Code permissions. A malicious agent definition injected via sync could perform arbitrary file system operations. | 2 | 5 | 10 (MEDIUM) | `CLAUDE_INCLUDES` whitelist | Review synced agent/skill content before execution. Consider read-only sync for executable definitions with manual approval for changes. |
| T-08 | Denial of Service | `sync.sh` runs as cron every 30 minutes. A large file in the sync scope or a git conflict loop could consume disk/network resources indefinitely. | 2 | 2 | 4 (LOW) | `set -e` in scripts; rebase abort on conflict | Add file size limits to sync. Add timeout to cron command. Add max retry count for push conflicts. |

### Domain Scores

| Domain | Score | Key Finding |
|---|---|---|
| 1. Policy & Governance | 2/10 | No written security policy exists. No designated security responsibility. README mentions "보안 주의" but no actionable policy or incident response plan. Ad-hoc `.gitignore` rules are the only governance mechanism. |
| 2. Data Protection | 1/10 | CRITICAL: Multiple categories of PII (third-party phone number, home addresses, salary, employment history, email) are committed in plaintext to a PUBLIC GitHub repository. No encryption at rest or in transit beyond GitHub's TLS. No data classification scheme. No retention policy. |
| 3. Access Control | 3/10 | Git SSH key provides push access (not trivially bypassed). However, the repo is PUBLIC so all data is world-readable. No MFA enforcement on GitHub account verified. No per-device access restrictions beyond pull-only marker. `sync-openclaw.sh` token-in-URL pattern weakens credential security. |
| 4. Threat & Vulnerability Mgmt | 3/10 | No formal threat model. CI/CD has automated tests with coverage threshold (80%), but no dependency scanning, no security testing in pipeline, no SAST/DAST. Input validation exists for path traversal and timestamp drift, which is good. |
| 5. Incident Response Readiness | 1/10 | No incident response plan. No monitoring to detect unauthorized changes. No alerting. No communication plan. If PII breach is discovered (it already exists), there is no defined response procedure. |
| 6. Third-Party Risk | 3/10 | Three external services used (GitHub, Notion API, Google Calendar). No security assessment of any. Notion API key in environment variable is good practice, but Notion DB ID is hardcoded in public repo. No DPAs. No vendor inventory. GitHub's public repo setting means all synced data is effectively shared with the world. |
| **Security Posture Score (SPS)** | **2.15/10** | |

SPS = (2 x 0.15) + (1 x 0.20) + (3 x 0.20) + (3 x 0.20) + (1 x 0.10) + (3 x 0.15) = 0.30 + 0.20 + 0.60 + 0.60 + 0.10 + 0.45 = 2.25

Corrected: **2.25/10**

### Verdict

**CRITICAL** (SPS 2.25 < 4.0): Security posture is insufficient for operation. Immediate action required on 6 items.

The most urgent issue is that this is a PUBLIC GitHub repository containing third-party PII (name, title, phone number of a real person), the owner's home addresses (current and previous, with exact apartment numbers), salary information, complete employment history, personal email, and Telegram ID. This constitutes an active data exposure incident under PIPA Art. 15/17 and GDPR Art. 5(1)(c)/32(1)(a). The third-party PII exposure (현정화 과장 010-3332-7533) is particularly severe as it was committed without the data subject's consent.

### Remediation Roadmap

| Priority | Finding | Risk Score | Remediation | Effort | Impact on Operations |
|---|---|---|---|---|---|
| 1 | T-01: PII exposed in PUBLIC GitHub repo (third-party phone number, addresses, salary, employment history) | 25 (CRITICAL) | **Immediate**: (1) Run `gh repo edit kangnam7654/ai-config-sync --visibility private` to make repo private. (2) Remove all PII-containing files from tracked content: delete or redact `openclaw/workspace/memory/2026-02-23.md`, `openclaw/workspace/notion_to_gcal_sync.sh`, `openclaw/workspace/cal_sync.py` (hardcoded email/DB ID). (3) Run `git filter-repo` or `BFG Repo-Cleaner` to purge PII from all historical commits. (4) Force-push cleaned history. (5) Rotate any exposed credentials (Notion DB ID is now public). | 2 hours for immediate fix + 2 hours for history rewrite | Repo becomes private; external forks (if any) retain old data -- contact GitHub support for DMCA/PII removal if forks exist. Sync continues normally after force-push. |
| 2 | T-02: Owner's personal identifiers (email, Telegram ID, Notion DB ID) enable social engineering | 20 (CRITICAL) | (1) Move `CALENDAR_ID` and `NOTION_DB` to environment variables in `cal_sync.py`. (2) Remove email from `notion_to_gcal_sync.sh`. (3) Remove Telegram ID from memory files. (4) Add `openclaw/workspace/memory/` to EXCLUDES or make memory files local-only. | 1 hour | Cal sync scripts require env vars to be set on each device. |
| 3 | T-03: `sync-openclaw.sh` embeds GitHub token in HTTPS URL | 12 (HIGH) | (1) Replace URL-embedded token pattern with SSH remote: `git remote set-url origin git@github.com:kangnam7654/openclaw-config-sync.git`. (2) Delete `sync-openclaw.sh` from sync scope (it is a legacy script). | 30 minutes | None -- script is already replaced by current `sync.sh` which uses SSH. |
| 4 | T-04: Tampered peer can inject malicious files via newest-wins sync into `~/.claude/` | 12 (HIGH) | (1) Add commit signature verification: only accept sync from commits signed by trusted GPG/SSH keys. (2) Add content hash verification for agent/skill files. (3) Consider a "review before apply" mode for changes to executable definitions (agents, skills, plugins). REQUIRES NEW TOOLING: GPG key infrastructure or SSH signing keys on all devices. | 8 hours implementation + 1 hour/month key management | Adds verification step to sync; may block sync if signatures are missing. |
| 5 | T-07: Synced agent/skill/plugin files execute with full Claude Code permissions | 10 (MEDIUM) | (1) Implement a change review mechanism: when agent/skill files change via peer sync, log the diff and require manual confirmation before replacing local copies. (2) Add file integrity monitoring: hash all synced executable files and alert on unexpected changes. | 6 hours | Adds manual approval step for agent/skill changes, reducing sync automation for these file types. |
| 6 | T-05: Timestamp spoofing can force file overwrite | 8 (MEDIUM) | Reduce `_MAX_FUTURE_DRIFT_SECONDS` from 86400 (24h) to 300 (5 min). Add per-file hash comparison: only apply peer version if content actually differs (prevents timestamp-only attacks). | 2 hours | Clocks must be synced within 5 minutes across devices (NTP handles this automatically). |
| 7 | T-06: No audit logging for sync operations | 6 (MEDIUM) | (1) Add structured JSON logging to `sync-timestamps.py`: log each file action (applied_from_peer/kept_local/removed) with timestamp, peer name, file hash. (2) Write logs to `~/.local/share/ai-config-sync/audit.jsonl` (append-only). (3) Add log rotation (keep 90 days). | 4 hours | Adds ~50KB/month of log data. |
| 8 | D1: No security policy or incident response plan | - | (1) Draft a data handling policy defining what data categories are allowed in the sync scope. (2) Create an incident response checklist (who to notify, how to revoke access, how to purge data). (3) Review and update annually. | 3 hours initial + 1 hour/year | Governance overhead; prevents future PII leaks. |
| 9 | D4: No dependency scanning or security testing in CI/CD | - | Add `uv run pip-audit` or `safety check` to GitHub Actions workflow. Add a pre-commit hook that scans for PII patterns (phone numbers, email addresses, addresses) before allowing commits. REQUIRES NEW TOOLING: `pip-audit` or `safety`, `pre-commit`. | 3 hours | Adds ~30 seconds to CI/CD pipeline. Pre-commit hook adds ~2 seconds per commit. |
| 10 | T-08: No resource limits on sync | 4 (LOW) | Add `timeout 300` wrapper to cron command. Add max file size check (reject files > 10MB) in `sync_section()`. | 1 hour | Sync aborts after 5 minutes if stuck; very large files are skipped. |
