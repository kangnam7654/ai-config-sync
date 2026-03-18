---
name: kangnam-client credentials audit
description: Pre-public GitHub release credential audit — hardcoded Google OAuth client_secrets found in both Tauri Rust and legacy Electron code
type: project
---

Two Google OAuth `client_secret` values hardcoded in source (GOCSPX- prefix, not PKCE-only flows):
- `<REDACTED>` — Gemini provider
- `<REDACTED>` — Antigravity provider

Present in BOTH:
1. `src-tauri/src/auth/credentials.rs` (active Tauri backend, lines 25, 35)
2. `src/main/auth/auth-manager.ts` (legacy Electron code still in repo, lines 20, 29)

**Why:** These credentials belong to internal Google Cloud OAuth apps (Cloud Platform scope). Exposure allows anyone to impersonate the app's OAuth client and perform token exchanges on behalf of users.

**How to apply:** Must be removed before any public git push. Remediation: move to build-time environment injection or compile-time env! macro in Rust. The legacy Electron files should also be removed or the secrets stripped.

Other findings from audit 2026-03-18:
- `.gitignore` does NOT exclude `src/main/` legacy Electron directory
- Token storage in Rust backend uses plaintext SQLite (no safeStorage equivalent) — MEDIUM risk
- Copilot and Claude client_ids are public/PKCE-only — acceptable to expose
- Codex client_id is a published public OAuth app ID — acceptable to expose
