---
name: kangnam-client architecture snapshot
description: Tauri 2 desktop LLM client architecture review baseline - Rust backend, React frontend, Node.js MCP sidecar. As of 2026-03-24.
type: project
---

Kangnam Client is a Tauri 2 desktop app (LLM chat client) with multi-provider support.

**Stack:** Rust (Tauri 2) backend, React 19 + Zustand + assistant-ui frontend, Node.js MCP bridge sidecar.

**Providers:** Claude, Codex (OpenAI), Gemini, Antigravity, Copilot, Mock. Each implements LLMProvider trait.

**Key architecture characteristics:**
- Single Mutex<Connection> for SQLite DB in AppState (contention risk under load)
- SSE streaming parsed per-provider with significant code duplication
- MCP bridge is a separate Node.js process communicating via JSON-RPC over stdin/stdout
- Frontend uses single monolithic Zustand store (~180 state fields + actions)
- Auth handles OAuth PKCE, device flow, keychain integration
- Agent loop in chat.rs handles tool-call cycles with MCP
- Cowork mode uses recursive Box::pin for agent loop continuation
- Eval system runs background tasks with separate DB connections
- Static LazyLock globals for ACTIVE_REQUESTS and COWORK_ABORT/COWORK_MESSAGES

**Why:** Baseline for architecture reviews and improvement tracking.
**How to apply:** Reference when reviewing PRs or planning refactors in this project.
