---
name: kangnam-client code quality baseline
description: Code quality audit of kangnam-client (React 19 + Tauri 2). Key patterns, dead code, and recurring issues found.
type: project
---

Codebase: React 19 + TypeScript + Rust Tauri 2 + SQLite. Desktop AI chat client.

**Key findings (2026-03-25 audit — full re-scan):**

### Dead code / redundancy
- `ModelSelector`, `ReasoningSelector`, `ProviderSelector` in `src/renderer/components/sidebar/` are **completely unused** — no import anywhere. Their logic is duplicated in `InputControls.tsx` which uses `lib/providers.ts`.
- `PROVIDER_INFO` constant in older `SettingsPanel.tsx` versions duplicated `ALL_PROVIDERS` in `lib/providers.ts`; now resolved — `ProvidersTab.tsx` imports `ALL_PROVIDERS` correctly.
- `ChatHeader` was a one-liner wrapper over `TopBar` (may have been removed — verify).
- `SettingsPanel.tsx` has been refactored into tabs (~185 lines now). Tabs live in `settings/tabs/`. Good split.

### Rust `.unwrap()` in production code (panics if None)
- `auth/manager.rs:142` — `CODEX.redirect_port.unwrap()` — panics if constant is `None`
- `auth/manager.rs:147` — `CODEX.auth_url.unwrap()` — panics if constant is `None`
- `auth/manager.rs:229` — `GEMINI.auth_url.unwrap()` — panics if constant is `None`
- `auth/manager.rs:304` — `ANTIGRAVITY.redirect_port.unwrap()` — panics if constant is `None`
- `auth/manager.rs:313` — `ANTIGRAVITY.auth_url.unwrap()` — panics if constant is `None`
- `providers/codex.rs:63` — `m.tool_calls.as_ref().unwrap()` — guarded by `is_some()` check above but brittle; inside `match` arm `assistant if m.tool_calls.is_some()` so safe in practice but still unwrap()
- `providers/claude.rs:219` — `body.as_object_mut().unwrap()` — always succeeds (body is json! object) but still unwrap()
- `providers/sse.rs:27,48` — `parts.last().unwrap()` — safe (split always yields >= 1 element) but still unwrap()
- `lib.rs:115` — `app.default_window_icon().unwrap()` — panics if no icon set in tauri.conf.json
- `auth/oauth_server.rs:49,121` — `stream.try_clone().unwrap()` — panics on OS error

### TypeScript anti-patterns
- `useAppStore.getState().devMode` called inside JSX render callback at `InputControls.tsx:89` — bypasses reactivity; should use `useAppStore(s => s.devMode)`
- `get()` used inside Zustand `set()` callbacks at `app-store.ts:275,281` — `get` is not imported; this will be a runtime ReferenceError. Should use `(s) => ({ ... })` pattern reading `s` directly.
- `JSON.parse(newServerJson)` at `SettingsPanel.tsx:169` — no try/catch; will throw on malformed JSON and crash the `onAdd` handler
- `loadData()` in `SettingsPanel.tsx` has no error handling (async function, errors silently dropped)

### Timing hack
- `WelcomeScreen.tsx:115` uses `requestAnimationFrame + setTimeout(50)` to sync event listener mount — fragile race condition

### Function complexity
- `add_message()` in `db/conversations.rs:198` has 9 positional parameters — all call sites pass trailing `None, None, None, None, None`; should be replaced with a builder or struct

### Migration pattern
- `db/schema.rs` uses bare `ALTER TABLE` statements with `.ok()` (silenced errors) for additive migrations — fine for SQLite but not versioned; if a migration fails silently, schema drift can occur without detection

### Duplicate token estimation logic
- `estimateTokens()` in `lib/providers.ts` and `estimate_token_count()` in `commands/chat.rs` are identical algorithms — one source of truth would be better (either compute on Rust side and pass to frontend, or vice versa)

**Why:** User requested comprehensive code quality diagnosis (2026-03-25).
**How to apply:** When working in this repo, the most impactful fixes are: (1) fix `get()` ReferenceError in app-store.ts, (2) add try/catch for JSON.parse in SettingsPanel, (3) replace `add_message` 9-param signature with a struct, (4) fix `.unwrap()` in auth/manager.rs.
