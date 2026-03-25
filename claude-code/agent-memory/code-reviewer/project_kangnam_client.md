---
name: kangnam-client code quality baseline
description: Initial code quality audit of kangnam-client (React 19 + Tauri 2). Key patterns, dead code, and recurring issues found.
type: project
---

Codebase: React 19 + TypeScript + Rust Tauri 2 + SQLite. Desktop AI chat client.

**Key findings (2026-03-25 audit):**
- `ModelSelector`, `ReasoningSelector`, `ProviderSelector` in `src/renderer/components/sidebar/` are **completely unused** — no import anywhere. Their logic is duplicated in `InputControls.tsx` which uses `lib/providers.ts`.
- `PROVIDER_MODELS`, `DEFAULT_MODELS`, `REASONING_EFFORTS`, `REASONING_SUPPORTED_PROVIDERS` are copy-pasted between `ModelSelector.tsx` and `lib/providers.ts`. Canonical source is `lib/providers.ts`.
- `PROVIDER_INFO` constant in `SettingsPanel.tsx` (lines 11-17) duplicates `ALL_PROVIDERS` in `lib/providers.ts`. Should import from providers lib.
- `SettingsPanel.tsx` is 1816 lines — monolithic file with 8+ internal components.
- `useAppStore.getState().devMode` called inside render callback (`.map`) at `SettingsPanel.tsx:233` — bypasses reactivity.
- `ChatHeader` is a one-liner wrapper over `TopBar` with no reason to exist separately.
- `loadData()` in `SettingsPanel.tsx` has no error handling.
- `JSON.parse(newServerJson)` at `SettingsPanel.tsx:177` has no try/catch — will throw on malformed JSON.
- `WelcomeScreen.tsx:113` uses `requestAnimationFrame + setTimeout(50)` timing hack to sync event listener mount.
- `StopButton` in `AssistantThread.tsx` and `onCancel` in `use-assistant-runtime.ts` duplicate stop-and-reload logic.
- Rust `auth/manager.rs` calls `.unwrap()` on `CODEX.redirect_port` and `auth_url` (lines 142, 147, 229, 304, 313) — will panic if constants are `None`.
- `dangerouslySetInnerHTML` in `AssistantThread.tsx:462` uses Shiki-generated HTML (safe — server-generated, no user input). `CoworkView.tsx:575` uses a custom `renderMarkdown()` that does `escapeHtml()` — safe.

**Why:** User requested "unused buttons, awkward UI" review. Sidebar selectors dead code is the primary UI finding.
**How to apply:** When working in this repo, recommend deleting sidebar/ModelSelector.tsx, sidebar/ProviderSelector.tsx, sidebar/ReasoningSelector.tsx as first cleanup step.
