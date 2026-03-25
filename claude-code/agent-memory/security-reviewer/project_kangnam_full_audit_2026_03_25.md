---
name: kangnam-client comprehensive security audit (2026-03-25)
description: Full OWASP Top 10 + dependency + secrets audit of kangnam-client Tauri 2 desktop LLM client
type: project
---

Key changes since 2026-03-24 audit:

## Resolved from prior audits
1. **RESOLVED** — credentials.rs no longer contains hardcoded GOCSPX- secrets; migrated to `option_env!("GEMINI_CLIENT_SECRET")` and `option_env!("ANTIGRAVITY_CLIENT_SECRET")`.
2. **RESOLVED** — ChatErrorBoundary no longer renders `error.stack` in DOM; shows only generic "Something went wrong" UI.
3. **RESOLVED** — mcp.rs now has `validate_server_config()` gating all add/update paths; mcp-bridge.ts has non-empty command check and env sanitization.

## Findings from 2026-03-25 audit

### CRITICAL
- None.

### HIGH
1. **[A05-1] CSP unsafe-eval + unsafe-inline still present** — tauri.conf.json line 31 `script-src 'self' 'unsafe-eval' 'unsafe-inline'`. No change from prior audit.
2. **[A08-2] OAuth callback server has no accept() timeout** — oauth_server.rs `wait_for_oauth_callback` and `OAuthCallbackReceiver::wait()`: `listener.accept()` blocks indefinitely. The outer `tokio::time::timeout(120s)` wraps the JoinHandle (for blocking tasks spawned with `spawn_blocking`), but `set_read_timeout` / `set_accept_timeout` is NOT set on the TcpListener itself. If the blocking thread is stuck in `accept()`, the 120s Tokio timeout will fire and the JoinHandle will complete with a JoinError — this means the 120s timeout DOES work for the outer flow. Risk is lower than previously classified — downgrading to MEDIUM. See justification in report.
3. **[A07-3] Access tokens stored in plaintext SQLite** — token_store.rs line 26-29. access_token column is stored without encryption. Short-lived tokens (< 1h) but readable by any process with filesystem access to the app data dir.
4. **[A10-1] MCP HTTP transport URL not validated against allowlist** — mcp-bridge.ts `createHttpTransport(url)` passes user-supplied URL to `new URL(url)` without blocking localhost/169.254.x.x. An MCP config pointing to `http://127.0.0.1:INTERNAL_PORT` could reach local services.
5. **[A05-4] Security headers absent** — CSP missing `frame-ancestors 'none'` / X-Frame-Options equivalent; no `X-Content-Type-Options`.

### MEDIUM
1. **[A04-2] Claude error messages distinguish auth failure modes** — manager.rs verify_claude_token(): 401 → "Invalid token", 403 → "Token forbidden", 400 → "Token rejected" — these surface provider-specific details to the renderer error event.
2. **[A05-1] withGlobalTauri: true** — tauri.conf.json line 13: exposes all Tauri globals to renderer window.
3. **[A03-2] Dev-mode sidecar launch is broken but noteworthy** — bridge.rs find_sidecar() returns `"npx"` with no args in dev mode; spawns `npx` without the `.ts` path. Dev-only code path, not production risk, but illustrates untested code in launch path.
4. **[BLOKLIST BUG] sanitizeEnv Set mismatch** — mcp-bridge.ts line 84: `BLOCKED_ENV_KEYS.has(key.toUpperCase())` but Set entries are uppercase strings — this is CORRECT logic, no bug. False alarm.

### LOW
1. **[A09-2] Sensitive env vars in dev sidecar** — mcp-bridge.ts line 107: `{ ...process.env, PATH: fullPath, ...sanitizeEnv(config.env) }` — the sidecar inherits the full parent process.env including any GEMINI_CLIENT_SECRET / ANTIGRAVITY_CLIENT_SECRET build-time env vars. These will be in the spawned child's environment.

### ACCEPTABLE RISK
1. `dangerouslySetInnerHTML` in CodeBlock — source is Shiki output on model-generated code strings. Shiki sanitizes its HTML output. Not user-controlled HTML.
2. `devMode` toggle via Ctrl+Shift+D — local desktop app, not a security boundary.
3. Claude API key token format validated (normalize_claude_token) — reduces risk of spoofed tokens.

**Why:** Tauri desktop app — no CORS/auth bypass risks. Main attack surface remains MCP command injection (now partially mitigated) and CSP (unchanged HIGH). Access token plaintext storage is the most actionable HIGH.
**How to apply:** Priority fix order: (1) CSP unsafe-eval/inline removal, (2) access_token encryption, (3) MCP HTTP URL allowlist.
