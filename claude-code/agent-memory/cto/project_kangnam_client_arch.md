---
name: kangnam-client architecture snapshot
description: Tauri 2 desktop LLM client architecture review baseline - Rust backend, React frontend, Node.js MCP sidecar. Deep review as of 2026-03-25.
type: project
---

Kangnam Client is a Tauri 2 desktop app (LLM chat client) with multi-provider support.

**Stack:** Rust (Tauri 2) backend, React 19 + TypeScript + Zustand + @assistant-ui/react frontend, Node.js MCP bridge sidecar. SQLite (WAL mode). Vite 7, Tailwind 4.

**Providers:** Claude, Codex (OpenAI), Gemini, Antigravity, Copilot, Mock. Each implements LLMProvider trait. Router holds Arc<dyn LLMProvider> per provider.

**Architecture health score (2026-03-25): 6.5/10**

Key findings:
- Single Mutex<Connection> for SQLite DB in AppState (contention risk under concurrent requests)
- SSE streaming parsed per-provider with significant code duplication across 5 provider implementations
- MCP bridge is a separate Node.js process communicating via JSON-RPC over stdin/stdout
- Frontend uses single monolithic Zustand store (~320 lines, ~60+ state fields + actions)
- Auth handles OAuth PKCE, device flow, keychain integration -- large 894-line manager.rs
- Agent loop in chat.rs handles tool-call cycles with MCP
- Cowork mode uses recursive Box::pin for agent loop continuation (stack overflow risk on deep tool chains)
- Eval system runs background tasks with separate DB connections
- Static LazyLock globals for ACTIVE_REQUESTS and COWORK_ABORT/COWORK_MESSAGES
- SettingsPanel.tsx is 1816 lines -- monolithic god component
- 38 silently swallowed errors (.ok()) in Rust backend
- 13 silently dropped row errors via .filter_map(|r| r.ok())
- Eval commands use raw serde_json::Value instead of typed structs for returns
- Frontend test coverage: 2 test files (utils.test.ts, providers.test.ts); backend has inline #[test] in conversations.rs and schema.rs
- No type-safe IPC contract between frontend and backend (tauri-api.ts uses manual `as` casts)
- Token estimation duplicated between Rust (chat.rs) and TypeScript (providers.ts)
- window.api global state path (settings, path resolution) duplicated between lib.rs and state.rs

**ADR decisions (2026-03-25):** 10 ADRs written to docs/adr/:
- ADR-001: SettingsPanel split (directory-based, tabs/ subdirectory)
- ADR-002: SQLite indexes + FTS5 (trigger-based sync, external content table)
- ADR-003: Migration system (self-implemented version-based, _migrations table)
- ADR-004: Mutex -> r2d2-sqlite pool (max_size=4)
- ADR-005: AppError unification (typed IPC errors with code+message)
- ADR-006: cowork.rs recursion -> loop (match chat.rs pattern)
- ADR-007: access_token to keychain (remove plaintext from SQLite)
- ADR-008: CSP unsafe-eval removal (Shiki bundle builder + wasm-unsafe-eval)
- ADR-009: MCP SSRF validation (URL blocklist + env allowlist)
- ADR-010: Zustand store slices (7 domain slices + persist middleware)

**Why:** Baseline for architecture reviews and improvement tracking.
**How to apply:** Reference when reviewing PRs or planning refactors in this project. ADRs are the source of truth for implementation decisions.
