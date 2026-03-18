---
name: kangnam-client refactor audit (2026-03-18)
description: Security findings from the error-propagation refactor — map_err leaking internal state, dangerouslySetInnerHTML in CodeBlock, mixed unwrap_or_else vs map_err in Mutex locks, CSP unsafe-eval/unsafe-inline
type: project
---

Refactoring audited on 2026-03-18 introduced these security-relevant patterns:

1. `map_err(|e| e.to_string())?` on Mutex locks in conv.rs propagates `PoisonError` (which contains the guard's type name) to the frontend via Tauri IPC — technically a verbose internal-state leak but low practical risk in a local desktop app.
2. `dangerouslySetInnerHTML={{ __html: html }}` in CodeBlock (AssistantThread.tsx:487) — Shiki's output is pre-sanitized but this is still an XSS surface if `html` contained user-controlled content (it doesn't here — it's Shiki output).
3. `declare global { interface Window { api: typeof api } }` — TypeScript-only, no XSS surface, correct pattern.
4. CSP in tauri.conf.json contains `unsafe-eval` and `unsafe-inline` for script-src — reduces XSS protection.
5. Google OAuth `client_secrets` are loaded via `option_env!()` at compile time — CRITICAL finding from previous audit still applies (credentials.rs).
6. `chat_send` still uses `unwrap_or_else(|e| e.into_inner())` on Mutex locks (poison recovery) — intentional difference from conv.rs which uses `map_err`.
7. setTimeout cleanup pattern in use-assistant-runtime.ts is correct — ref-based, no stale closure issue.
8. `access_token` stored in plaintext SQLite (token_store.rs line 27 comment acknowledges this) — refresh tokens go to OS keychain correctly.

**Why:** Refactor changed 23 commands from bare return to Result<T, String>. The main risk is error message verbosity leaking internal state.
**How to apply:** Flag any future Mutex error propagation for review; CSP hardening is needed before any web-origin loading.
