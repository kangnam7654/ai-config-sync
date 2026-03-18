---
name: MoneyPrinter pre-public-release security audit
description: Pre-release audit for MoneyPrinter repo — found live credentials in client_secret.json, youtube-oauth2.json, and .env; deprecated oauth2client; pillow CVEs
type: project
---

Live credentials audit performed 2026-03-18 before making the repo public.

**Critical findings:**
- `Backend/client_secret.json`: real Google OAuth client_id + client_secret (`GOCSPX-FfTp_...`). Gitignored in .gitignore but must verify never committed.
- `Backend/youtube-oauth2.json`: live access_token + refresh_token + client_secret for YouTube upload/partner scopes. Gitignored via `*-oauth2.json`. Refresh token does NOT expire — must be revoked even if untracked.
- `.env`: 5 live API keys (GOOGLE_API_KEY=AIzaSyBq..., PEXELS_API_KEY, TIKTOK_SESSION_ID, ASSEMBLY_AI_API_KEY, GOOGLE_CLOUD_PROJECT=moneyprinter-489312). Gitignored correctly but keys must still be rotated before public release.

**Why:** Public GitHub release. Any committed credential = immediate exposure.
**How to apply:** Before any public push, verify with `git ls-files` and `git log --all -- <file>` that none of these ever appeared in a commit. If they did, rewrite history with `git filter-repo`.

**Other notable findings:**
- `docker-compose.yml`: hardcoded `:-moneyprinter` fallback password in Postgres env vars (MEDIUM)
- `Backend/finalize.py:16`: hardcoded macOS font path `/System/Library/Fonts/AppleSDGothicNeo.ttc` — breaks Docker/Linux (HIGH)
- `pyproject.toml`: `pillow==9.5.0` has CVE-2023-50447 (HIGH), `requests==2.31.0` has CVE-2024-35195 (MEDIUM), `oauth2client` deprecated
- `undetected-chromedriver` unpinned, no import found in codebase — likely dead dependency, remove
- `.gitignore` missing: `.coverage`, `htmlcov/`, `.pytest_cache/`, `contents/plans/`, `**/__pycache__/`
- `Backend/legacy/codex_auth.py:91`: JWT decoded without signature verification (MEDIUM, local-only risk)
- OAuth token for youtube stored in project dir without chmod 0o600 (HIGH), should go to `~/.moneyprinter/`
