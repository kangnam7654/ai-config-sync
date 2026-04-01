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

## Dear, 정빈 Project (/Users/kangnam/projects/dear-jeongbin/fit-check)

앱명: "Dear, 정빈" — 정빈이를 위한 1인 사용 AI 커리어 코치. package.json name: "dear-jeongbin".

### Stack
- Next.js 16, TypeScript, Tailwind v4, Zod v4
- DB: PGlite (embedded PostgreSQL, file-based) — no external DB server needed
- ORM: Prisma 7 with `@prisma/adapter-pg` — PGlitePool duck-types pg.Pool
- AI: Claude Haiku SSE via @anthropic-ai/sdk
- No auth, no credits, no payments — 1인 앱

### Key files
- DB adapter: `src/lib/db/pglite-adapter.ts` — PGlitePool wraps PGlite as pg.Pool duck-type
- Prisma client: `src/lib/prisma/client.ts` — uses PGlitePool with `as any` cast
- Single user: `src/lib/constants/user.ts` — USER_ID = '00000000-0000-0000-0000-000000000001'
- Auth stub: `src/lib/middleware/auth.ts` — requireAuth() returns hardcoded USER_ID
- Credits stub: `src/hooks/use-credits.ts` — always returns balance: 9999 (no-op)
- DB path: `./data/pglite/` (gitignored), env var: DATABASE_PATH
- Schema init: ensureSchema() in pglite-adapter.ts runs on first PGlite connection

### Prisma 7 gotcha
- datasource in schema.prisma must NOT have `url` field — Prisma 7 driver adapter mode
- Use `adapter` passed to PrismaClient constructor instead
- `prisma.config.ts` datasource url is only for CLI tooling (generate), not runtime

### PGlite adapter pattern
- PGlite.query() returns `{ rows, affectedRows, fields }` — not pg.QueryResult
- PGlitePool.connect() → PGliteClient that wraps PGlite.query() with pg.PoolClient interface
- Cast `pool as any` when passing to PrismaPg() — type mismatch is intentional duck-typing

### Services (Supabase removed, Prisma ORM)
- resume.service.ts, application.service.ts, gap-analysis.service.ts, document.service.ts, interview.service.ts
- All use `prisma.*` from `@/lib/prisma/client`
- No credit deduction anywhere — unlimited use

### Tests: 85 passing, TypeScript clean (0 errors)

## Kangnam Client (/Users/kangnam/projects/kangnam-client/kangnam-client)

Tauri 2.x desktop app (Rust + React). See `project_kangnam_client.md` for full structure.
- DB functions now return `Result<T, rusqlite::Error>` — commands use `.map_err(|e| e.to_string())?`
- `db::connection::open_database()` is the canonical way to open a DB connection (WAL + FK + busy_timeout)
- Stale build artifacts → `cargo clean` if build script references `/Users/kangnam/projects/mcp-client/`
