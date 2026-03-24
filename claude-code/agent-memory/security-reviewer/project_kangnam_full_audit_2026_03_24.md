---
name: kangnam-client full security audit (2026-03-24)
description: Comprehensive OWASP + dependency audit of Tauri 2 LLM client covering auth, MCP, IPC, XSS, CSP, token storage, and sidecar security
type: project
---

Key findings from full audit 2026-03-24:

1. **CRITICAL [A05-2]** — `tauri.conf.json` CSP contains `unsafe-eval` and `unsafe-inline` in `script-src`. Reduces XSS defense to near-zero. Known from prior audit, still present.
2. **HIGH [A05-3]** — `ChatView.tsx` ChatErrorBoundary renders full stack trace (`this.state.error.stack`) and full error message in the DOM (line ~19). Visible to user in production.
3. **HIGH [A08-2]** — OAuth callback server (`oauth_server.rs`) has no accept timeout. A connection left in pending state blocks the entire auth flow indefinitely. Not a credential issue but a DoS risk.
4. **HIGH [A07-3]** — Access tokens stored in plaintext SQLite (auth_tokens table, access_token column). Refresh tokens go to OS keychain (correct), but access tokens are plaintext on disk.
5. **HIGH [A01-4]** — `mcp-bridge.ts` sidecar calls `new StdioClientTransport({ command: config.command, args: config.args })` with no validation of the `command` field. A malicious MCP config (command injection) could run arbitrary processes.
6. **MEDIUM [A03-1]** — `search_messages` in conversations.rs uses parameterized LIKE with `%{trimmed}%` — safe. All other DB queries are parameterized. No SQL injection found.
7. **MEDIUM [A05-1]** — `withGlobalTauri: true` in tauri.conf.json exposes all Tauri globals to the renderer. Unnecessarily broad surface — individual API imports are safer.
8. **MEDIUM [A05-4]** — CSP missing `X-Frame-Options`, `X-Content-Type-Options`. Security headers not set on Tauri window.
9. **MEDIUM [A04-2]** — Claude connect error messages (`Invalid token — 401 Unauthorized` vs `Token forbidden — 403`) distinguish specific auth failure modes, leaking provider-side error details.
10. **LOW [A02-2]** — `option_env!("GEMINI_CLIENT_SECRET")` and `option_env!("ANTIGRAVITY_CLIENT_SECRET")` — if these env vars are not set at build time, the binary panics at runtime on `.unwrap()` (manager.rs line 252 and 330). Should be `ok_or` with a clear error.
11. **ACCEPTABLE RISK** — `dangerouslySetInnerHTML={{ __html: html }}` in CodeBlock (AssistantThread.tsx ~line 486). Source is Shiki highlighter output on developer-defined code strings, not user-controlled HTML. Shiki sanitizes output.
12. **ACCEPTABLE RISK** — `devMode` toggle via Ctrl+Shift+D exposes dev-only providers. Gated by flag, not a security boundary violation for a local desktop app.

**Why:** Desktop app — no server-side exploits, but MCP command injection is the most critical active risk since users configure arbitrary MCP servers.
**How to apply:** Flag any future MCP command handling for validation; CSP hardening is the highest-ROI fix.
