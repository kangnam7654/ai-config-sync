# Security Reviewer Memory

## Project Memories
- [kangnam-client credentials audit](./project_kangnam_credentials.md): Hardcoded Google OAuth client_secrets in both Tauri Rust backend and legacy Electron code — CRITICAL finding, pre-public audit performed 2026-03-18
- [kangnam-client refactor audit](./project_kangnam_refactor_audit.md): Error-propagation refactor audit 2026-03-18 — map_err IPC state leak (LOW), dangerouslySetInnerHTML in CodeBlock (MEDIUM), CSP unsafe-eval/unsafe-inline (HIGH), mixed Mutex poison strategy (MEDIUM availability concern)
- [MoneyPrinter pre-release audit](./project_moneyprinter_prerelease_audit.md): Pre-public-release audit 2026-03-18 — live creds in client_secret.json + youtube-oauth2.json (CRITICAL), 5 live keys in .env, hardcoded macOS font path, pillow CVE, docker default password, missing .gitignore entries
