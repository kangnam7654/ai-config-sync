---
name: kangnam-client project structure
description: Tauri desktop app (Rust backend) with multi-provider LLM chat, OAuth, MCP sidecar, and skill eval system
type: project
---

## Stack
- Framework: Tauri 2.x (Rust backend + frontend in src/renderer)
- DB: SQLite via rusqlite, WAL mode, foreign_keys ON, busy_timeout 5000ms
- Auth: Multi-provider OAuth (Codex PKCE, Gemini PKCE+secret, Antigravity PKCE+secret, Copilot device-flow, Claude keychain/API key)
- Providers: claude, gemini, codex, copilot, antigravity — routed via `LLMRouter`
- MCP: sidecar bridge (`McpBridge`) for tool calls

## Project root: /Users/kangnam/projects/kangnam-client/kangnam-client

## Key Backend Files
- Entry: `src-tauri/src/lib.rs` — module registration + Tauri builder
- State: `src-tauri/src/state.rs` — `AppState { db, auth, router, mcp }`
- DB layer: `src-tauri/src/db/` (connection.rs, conversations.rs, skills.rs, schema.rs)
- Auth: `src-tauri/src/auth/` (manager.rs, oauth_server.rs, pkce.rs, token_store.rs, credentials.rs)
- Commands: `src-tauri/src/commands/` (chat.rs, conv.rs, skills.rs, eval.rs, cowork.rs, mcp.rs, auth.rs, settings.rs)
- Providers: `src-tauri/src/providers/` (router.rs, types.rs, claude.rs, gemini.rs, codex.rs, copilot.rs, antigravity.rs)
- Error module: `src-tauri/src/error.rs` (AppError enum with thiserror)

## DB Function Signatures (post-refactor)
- `list_conversations(conn) -> Result<Vec<Conversation>, rusqlite::Error>`
- `create_conversation(conn, provider, model) -> Result<Conversation, rusqlite::Error>`
- `delete_conversation(conn, id) -> Result<(), rusqlite::Error>` (CASCADE handles messages)
- `delete_all_conversations(conn) -> Result<(), rusqlite::Error>` (CASCADE)
- `update_title(conn, id, title) -> Result<(), rusqlite::Error>`
- `toggle_pin(conn, id) -> Result<(), rusqlite::Error>` (single CASE SQL)
- `auto_title_if_needed(conn, id, msg) -> Result<(), rusqlite::Error>`
- `get_messages(conn, id) -> Result<Vec<Message>, rusqlite::Error>`
- `add_message(conn, ...) -> Result<Message, rusqlite::Error>`
- `search_messages(conn, q) -> Result<Vec<SearchResult>, rusqlite::Error>`
- `list_skills(conn) -> Result<Vec<Skill>, rusqlite::Error>`
- `create_skill(conn, ...) -> Result<Skill, rusqlite::Error>`
- `add_skill_reference(conn, ...) -> Result<SkillReference, rusqlite::Error>`
- All Tauri commands convert with `.map_err(|e| e.to_string())?`

## Build Note
- After `cargo clean`, `cargo check` takes ~60s (full rebuild of dependencies)
- Stale build artifacts pointing to deleted `/Users/kangnam/projects/mcp-client/` will cause build-script failure — fix with `cargo clean`

**Why:** audit-report.md identified 49 improvement items; Steps 1-3 (security, error arch, DB) completed.
**How to apply:** Continue with Steps 4-7 from design-spec.md for architecture refactoring, UX improvements, and CI setup.
