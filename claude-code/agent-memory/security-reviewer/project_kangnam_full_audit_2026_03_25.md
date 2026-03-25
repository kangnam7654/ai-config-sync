---
name: kangnam-client comprehensive security audit (2026-03-25, updated)
description: Full OWASP Top 10 + dependency + secrets audit of kangnam-client Tauri 2 desktop LLM client — latest state
type: project
---

## Resolved from prior audits (cumulative)
1. **RESOLVED** — credentials.rs no longer contains hardcoded GOCSPX- secrets; migrated to `option_env!("GEMINI_CLIENT_SECRET")` and `option_env!("ANTIGRAVITY_CLIENT_SECRET")`.
2. **RESOLVED** — ChatErrorBoundary no longer renders `error.stack` in DOM; shows only generic "Something went wrong" UI.
3. **RESOLVED** — mcp.rs now has `validate_server_config()` gating all add/update paths; mcp-bridge.ts has non-empty command check and env sanitization.

## Current state (2026-03-25, second comprehensive scan)

### CRITICAL
- None.

### HIGH

1. **[A05-1] CSP unsafe-eval + unsafe-inline still present** — tauri.conf.json line 31
   `script-src 'self' 'unsafe-eval' 'unsafe-inline'`
   `unsafe-eval` enables XSS via eval()/Function() in renderer; `unsafe-inline` allows inline script injection.
   Required by Vite/React dev mode but must be resolved before public release.

2. **[A07-3] Access tokens stored in plaintext SQLite** — token_store.rs line 27-29
   `access_token` column stored without encryption in SQLite at `~/Library/Application Support/kangnam-client/data/kangnam-client.db`.
   Short-lived (< 1h for most providers) but any process with filesystem access can read all active tokens.
   Remediation: use OS keychain (keyring crate) for access_token as well, or apply SQLCipher encryption.

3. **[A10-1] MCP HTTP transport URL not validated against allowlist** — sidecar/mcp-bridge.ts line 111-143
   `createHttpTransport(url)` calls `new URL(url)` without blocking localhost/127.0.0.1/169.254.x.x.
   An MCP server config with `url: "http://127.0.0.1:PORT"` would reach local services (SSRF).
   Remediation: validate hostname against allowlist before connecting; block RFC1918 + link-local ranges.

4. **[A08-2/A05-3] oauth_server.rs error reflected in browser** — oauth_server.rs line 163
   `ERROR_HTML_TEMPLATE.replace("{{ERROR}}", error)` inserts the raw OAuth error string into HTML without escaping.
   If an attacker crafts an OAuth callback with `error=<script>alert(1)</script>` the HTML page shown to the user would contain unescaped HTML.
   The page is served locally (127.0.0.1) to the user's own browser during OAuth flow; severity is medium-high.
   Remediation: HTML-escape the error string before inserting into template.

5. **[A05-4] Security headers absent from CSP** — tauri.conf.json line 31
   `frame-ancestors` directive absent; `X-Content-Type-Options` not set.

### MEDIUM

1. **[A04-2] Claude error messages distinguish auth failure modes** — manager.rs lines 694-703
   `verify_claude_token()`: 401 → "Invalid token — 401 Unauthorized", 403 → "Token forbidden — 403", 400 → "Token rejected (400)".
   These status-specific messages are surfaced to the renderer via error events.

2. **[A05-1] withGlobalTauri: true** — tauri.conf.json line 13
   Exposes `window.__TAURI__` with all IPC calls to the renderer. Combined with CSP unsafe-inline this broadens the attack surface.

3. **[A04-2] COWORK_MESSAGES is process-global static** — commands/cowork.rs lines 14-15
   `COWORK_MESSAGES: Mutex<Vec<ChatMessage>>` is a `LazyLock` static. `cowork_follow_up` appends to it without any session token or ownership check. If another renderer or IPC caller invokes `cowork_follow_up` it injects into the in-progress cowork session. Low practical risk (desktop single-user app), but worth noting.

4. **[A09-1] No auth event logging** — manager.rs / auth commands
   Login success/failure events are emitted to the renderer via Tauri events but not written to any persistent log. Auth failures are silent beyond the returned error string.

### LOW

1. **[A09-2] Sensitive env vars in dev sidecar** — mcp-bridge.ts line 107
   `{ ...process.env, PATH: fullPath, ...sanitizeEnv(config.env) }` — sidecar inherits the full parent process.env including build-time env vars like GEMINI_CLIENT_SECRET.

2. **[A05-1] .gitignore missing .env entries** — .gitignore does not include `.env`, `.env.*`, or `*.pem`.
   If a developer creates a local .env file it would not be excluded from git by default.

3. **[A07-1] OAuth callback TcpListener binds on 0.0.0.0 (Codex/Antigravity)** — oauth_server.rs line 38
   Fixed-port listeners for Codex (1455) and Antigravity (51121) bind to `127.0.0.1:{port}` — this is CORRECT. Gemini uses dynamic port via `start_dynamic_oauth_server`. No issue.

### ACCEPTABLE RISK

1. `dangerouslySetInnerHTML` in CodeBlock (AssistantThread.tsx line 462) — source is Shiki output on `code` string. Shiki sanitizes its HTML output. The `code` value comes from the LLM response, not from user-controlled HTML. Not a real XSS vector.
2. `devMode` toggle via Ctrl+Shift+D — local desktop app, not a security boundary.
3. Claude API key token format validated (normalize_claude_token) — reduces risk of spoofed tokens.
4. CODEX OAuth credentials (client_id: `app_EMoamEEZ73f0CkXaXp7hrann`) are public/open-source client IDs per OpenAI Codex; no client_secret used. PKCE flow is used correctly.
5. COPILOT client_id (`Iv1.b507a08c87ecfe98`) is a public GitHub App client ID widely used by Copilot integrations.

**Why:** Tauri desktop app — no CORS/auth bypass risks from external web. Main attack surface remains MCP command injection (now partially mitigated), CSP (unchanged HIGH), access token plaintext storage, and OAuth error reflection.
**How to apply:** Priority fix order: (1) OAuth error HTML injection fix (trivial), (2) access_token encryption, (3) MCP HTTP URL allowlist, (4) CSP unsafe-eval/inline removal.
