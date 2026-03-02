# Planner Agent Memory

## Active Projects
- **BuyBuddy MVP**: AI Shopping Agent for IT/Electronics, plan at `/home/kangnam/projects/ai-products/01-buybuddy/docs/PLAN_BUYBUDDY_MVP.md`
- **FlirtIQ MVP**: AI Dating Conversation Coach (Privacy-First), plan at `/home/kangnam/projects/ai-products/02-flirtiq/docs/PLAN.md`
- **FlirtIQ Phase 1 Subscription**: Plan at `/home/kangnam/projects/ai-products/02-flirtiq/docs/PLAN_PHASE1_SUBSCRIPTION.md`

## Planning Patterns
- Frontend can always start with mock data (parallel with backend)
- AI engineer tasks often depend on backend search/data services
- Reviewer enters at integration phase (Milestone 3+)
- Always include .env.example in plans (no real secrets in repo)
- Beta scope must be split into 3a/3b when 5+ major features are in one week
- CSO often requires Beta to be 1.5-2 weeks, not 1 week

## Team Coordination
- backend-dev + ai-engineer collaborate on AI API endpoints
- ai-engineer owns: prompt engineering, cost tracking, mock client, OCR prototype
- frontend-dev works independently with mock data until integration milestone
- Task IDs follow pattern: {milestone}.{sequence}
- Week 0 prep tasks (legal, biz registration, PG signup) run in parallel with dev

## API Contract Patterns
- Always define API contract in PLAN.md as single source of truth (SSOT)
- backend-dev writes Pydantic schemas first -> frontend-dev mirrors in src/types/index.ts
- All IDs: UUID as string (never number)
- Auth: Authorization: Bearer <token> header (never query param)
- Rate limit exceeded: 402 error with reset_at timestamp
- PII detected: 422 error with masked_text for user review

## Free-tier Cost Control (FlirtIQ Pattern)
- Hard limit (not soft): 402 error on exceed, no blurring
- Redis counter cache with DB persistence for durability
- Rules-based analysis for free tier -> AI only for premium (reduces AI cost)
- Cost Cap auto-mechanism: monitor Free AI cost / MRR ratio
  - >60%: warn, >80%: auto-reduce free limit

## Privacy-First Architecture (for sensitive products)
- "Server never knows the counterpart" principle
- Screenshot: backend proxy + memory-only + immediate deletion (no disk write)
- Text input: server-side PII detection (Korean name patterns, phone numbers)
- PII masking before any AI call
- Reviewer must check: no file write, no S3 upload, no temp file creation for images

## Subscription/Billing Pattern (FlirtIQ Phase 1)
- Separate `subscriptions` table even if `users.is_premium` exists (lifecycle tracking)
- Single writer pattern: only subscription_service.py modifies is_premium
- Cancel = soft cancel (access until period end, not immediate revoke)
- Mock payment service as adapter layer -> swap with real PG later
- Price from config env var, not hardcoded
- Background task (hourly) for subscription expiry + webhook fallback
- 409 Conflict for duplicate active subscription attempts

## Product Structure Convention
- Format: `ai-products/{##-product-name}/` (numbered prefix)
- Standard dirs: backend/, frontend/, docs/, docker-compose.yml
- Products created via: CEO -> CSO -> Planner -> Team Dev -> Review
- Current products:
  - 01-buybuddy/ -- AI shopping agent (Feb 2026)
  - 02-flirtiq/ -- AI dating coach (Feb 2026)
