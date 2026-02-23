# Backend Dev Agent Memory

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
