---
name: fit-check MVP
description: AI career coach app (Gap Analysis + document generation) - Next.js 15 + Supabase + Claude Haiku 4.5 + TossPayments, 4-week MVP, solo dev
type: project
---

fit-check (핏체크) MVP project started 2026-03-31. Plan at `/Users/kangnam/projects/dear-jeongbin/docs/PLAN_FITCHECK_MVP.md`.

**Why:** CEO product - AI career coaching for job seekers (JD vs resume gap diagnosis + custom document generation + interview prep).

**How to apply:**
- Tech stack: Next.js 15 App Router + Supabase (PostgreSQL + Auth + Storage) + Prisma 6 + Claude Haiku 4.5 + TossPayments + Tailwind CSS 4 + shadcn/ui
- Monorepo single deploy on Vercel Pro (no separate backend)
- 14 DB tables, 38+ API endpoints, 24 screens (8 hi-fi spec, 16 design system based)
- Credit-based monetization (not subscription): starter 4900/10cr, pro 9900/30cr, all_in 19900/80cr
- Free tier: 3 Gap Analyses/month, document blur preview for conversion
- Key arch pattern: Supabase Auth JWT (httpOnly cookie) + Prisma service_role for server writes + RLS for client reads
- SSE streaming for AI endpoints (Gap Analysis, Document Generation)
- Project dir: `/Users/kangnam/projects/dear-jeongbin/`
- Spec docs: `docs/llm/arch-spec.md`, `docs/llm/ux-ui-spec.md`
