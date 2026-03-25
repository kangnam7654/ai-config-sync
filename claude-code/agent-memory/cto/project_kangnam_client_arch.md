---
name: kangnam-client architecture snapshot
description: Tauri 2 desktop LLM client architecture review baseline - Rust backend, React frontend, Node.js MCP sidecar. Deep review as of 2026-03-25.
type: project
---

Kangnam Client is a Tauri 2 desktop app (LLM chat client) with multi-provider support.

**Stack:** Rust (Tauri 2) backend, React 19 + TypeScript + Zustand 5 + @assistant-ui/react frontend, Node.js MCP bridge sidecar. SQLite (WAL mode). Vite 7, Tailwind 4.

**Codebase size:** ~6,955 Rust LOC / ~8,307 TypeScript LOC (as of 2026-03-25)

**Providers:** Claude, Codex (OpenAI), Gemini, Antigravity, Copilot, Mock. Each implements LLMProvider trait. Router holds Arc<dyn LLMProvider> per provider.

**Architecture health score (2026-03-25, v2): 5.85/10** -- FAIL (threshold: 8.0)

Critical findings:
- C1: Single Mutex<Connection> serializes all DB access (no pool)
- C2: cowork.rs uses recursive Box::pin for agent loop (stack overflow risk)
- C3: 3 static LazyLock globals create hidden coupling
- C4: 21 silently swallowed .ok() errors across DB writes

High findings:
- H1: AppError enum defined but unused -- all commands return Result<T, String>
- H2: Agent loop duplicated 3x (chat/agents/cowork) with ~80% identical code
- H3: Monolithic Zustand store (~60 fields, 353 lines)
- H4: onNew callback captures stale messages closure
- H5: Migration system has no version tracking

Medium: untyped IPC, eval uses raw serde_json::Value, router.create_fresh duplicates registry, AuthManager is 893-line god object, hardcoded token estimation heuristics, duplicate path resolution.

Positives: WAL+FK+busy_timeout, OS keychain for refresh tokens, PKCE+state validation, idempotent migrations, clean LLMProvider trait, meaningful DB tests.

**Previously written ADRs (2026-03-25):** ADR-001 through ADR-010 covering identified issues.

**Why:** Baseline for architecture reviews and improvement tracking.
**How to apply:** Reference when reviewing PRs or planning refactors. Priority order: C2 > C1 > H1 > H2 > H3 > C3 > H5 > M1. Items C1-C2 are required for production reliability.
