---
name: fit-check-tech-stack
description: fit-check (AI career gap analyzer) tech stack decision - Next.js 15 + Supabase + Vercel + Prisma, monorepo single-deploy, as of 2026-03-31
type: project
---

## fit-check Tech Stack Decision - 2026-03-31

**Project:** fit-check (dear-jeongbin repo) -- AI career gap analysis + custom resume/cover letter generation
**Path:** /Users/kangnam/projects/dear-jeongbin

**Stack:** Next.js 15 App Router (Route Handlers as backend), Supabase (PostgreSQL + Auth + Storage), Prisma 6, Vercel Pro, Tailwind CSS 4 + shadcn/ui, Zustand + TanStack Query, Claude Haiku 4.5 (@anthropic-ai/sdk), tosspayments, Sentry + PostHog

**Key Decisions:**
- Rejected CEO's FastAPI proposal: single-language (TS) monolith over Python+TS dual-server for 1-person 4-week MVP
- Rejected Redis: JWT sessions + Next.js fetch cache sufficient
- Rejected bare S3: Supabase Storage with RLS auto-integration
- Auth: Supabase Auth (Email + Kakao OAuth MVP, Google Phase 2)
- API: REST, /api/v1/, snake_case, SSE for AI streaming
- Monthly cost est: 281,300 KRW (56% of 500K budget)

**Why:** 1-person dev + 4-week MVP demanded maximum simplification. Supabase bundles Auth+DB+Storage+RLS. Vercel is Next.js native host.
**How to apply:** Reference this stack when reviewing DB schema (#12), API design (#14), and consistency check (#15). All DB tables must have RLS with auth.uid().
