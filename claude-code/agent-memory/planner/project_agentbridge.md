---
name: AgentBridge Project
description: Local WebSocket hub for LLM agent cross-repo messaging. Python asyncio, websockets, aiosqlite, Textual TUI. MIT open-source dev tool.
type: project
---

AgentBridge is a local WebSocket hub enabling LLM agents in different repos to exchange messages, results, and shared context in real-time.

**Why:** Developer wants a tool for multi-repo multi-agent coordination. Personal/learning project, no market validation required. CEO gate bypassed by user decision (2026-03-31).

**How to apply:**
- Tech: Python 3.12+, websockets v13+ (no ASGI framework), aiosqlite (raw SQL), Textual TUI, JSON serialization, uv package manager
- Protocol: JSON-RPC 2.0 style, 13 request methods + 4 notifications across session/message/context domains
- DB: 3 tables (sessions, messages, contexts) in SQLite WAL mode
- Project path: /Users/kangnam/projects/bagelcode/
- Design docs at: docs/llm/ (idea-brief, db-schema, websocket-protocol, arch-spec)
- Review amendments: FK CASCADE/RESTRICT, PRAGMA user_version=1, capabilities column, composite index, implicit last_seen_at update, message/history method, protocol_version in register response, error 1010 CONTEXT_VALUE_TOO_LARGE
