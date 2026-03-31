# Backend Dev Agent Memory

## Saju MVP Project (/Users/kangnam/projects/saju)

### Stack
- Framework: Hono + @hono/node-server (Node.js ESM, TypeScript)
- AI: @anthropic-ai/sdk — use `anthropic.messages.stream()` for SSE
- Saju calc: @fullstackfamily/manseryeok (getGapja, getPillarByHangul)
- Validation: zod + @hono/zod-validator

### Backend Structure
- Entry: `backend/src/index.ts` — Hono app, mounts /api/interpret and /api/fortune
- Routes: `backend/src/routes/interpretation.ts` (SSE streaming), `fortune.ts` (today-pillar JSON)
- Services: `backend/src/services/claude.ts` — wraps anthropic stream → ReadableStream SSE
- Prompts: `backend/src/prompts/saju.ts`, `gunghap.ts`, `daily.ts`
- Middleware: `cors.ts` (ALLOWED_ORIGINS env), `rate-limit.ts` (30 req/min in-memory)

### SSE Pattern (Hono)
- Use `c.header()` + `c.body(stream)` — NOT `new Response(stream, ...)` (type error)
- Content-Type: text/event-stream, each chunk: `data: {"text": "..."}\n\n`, final: `data: [DONE]\n\n`

### manseryeok API
- `getGapja(year, month, day)` → `{ yearPillar, yearPillarHanja, monthPillar, monthPillarHanja, dayPillar, dayPillarHanja }`
- `getPillarByHangul(hangul)` → `{ tiangan: { hangul, hanja, element }, dizhi: { hangul, hanja, element }, element, yinYang }`
- Port: 3000

## FlirtIQ Project (02-flirtiq)

### Infrastructure
- PostgreSQL port: **5433** (5432 used by BuyBuddy)
- Redis port: **6380** (6379 used by BuyBuddy)
- Working dir: `/home/kangnam/projects/ai-products/02-flirtiq/backend/`
- Docker Compose at: `/home/kangnam/projects/ai-products/02-flirtiq/docker-compose.yml`

### Key Files
- Config: `app/config.py` (pydantic-settings, reads .env)
- DB: `app/db/database.py` (async engine), `app/db/base.py` (Base class)
- Models: `app/models/` (user, conversation, analysis, usage_credit)
- Schemas: `app/schemas/` (auth, conversation, usage)
- Services: `app/services/` (auth_service, pii_service, usage_service)
- Routes: `app/api/` (auth, conversations, health, usage)
- AI module: `app/ai/` (managed by ai-engineer — client, prompts, cost_tracker)

### Auth Pattern
- Bearer token via `HTTPBearer` dependency
- `get_current_user()` in `app/api/auth.py` — import this for protected routes
- Mock mode: empty `GOOGLE_CLIENT_ID` → returns test user

### Port Conflict Pattern
- When BuyBuddy (01-buybuddy) is running, ports 5432/6379 are occupied
- FlirtIQ uses 5433/6380 to avoid conflicts
- Always check for port conflicts when adding new projects

## fit-check Project (/Users/kangnam/projects/dear-jeongbin)

See `project_fitcheck.md` for stack, API design doc location, credit rules, file structure.
- API design doc: `docs/llm/api-design.md` (38 endpoints, DRAFT 2026-03-31)

## Kangnam Client (/Users/kangnam/projects/kangnam-client/kangnam-client)

Tauri 2.x desktop app (Rust + React). See `project_kangnam_client.md` for full structure.
- DB functions now return `Result<T, rusqlite::Error>` — commands use `.map_err(|e| e.to_string())?`
- `db::connection::open_database()` is the canonical way to open a DB connection (WAL + FK + busy_timeout)
- Stale build artifacts → `cargo clean` if build script references `/Users/kangnam/projects/mcp-client/`
