---
name: dear-ant-architecture
description: Dear,ANT (Next.js 16 + Supabase investment mood analyzer) architecture review baseline, scored 6.13/10, 4 P0 issues, as of 2026-03-25
type: project
---

## Dear,ANT Architecture Review - 2026-03-25

**Stack:** Next.js 16 App Router, React 19, Supabase, Tailwind CSS 4, TypeScript 5
**Overall Score:** 6.13/10 (FAIL, threshold 8.0)
**Primary Criterion:** Architecture Pattern 7/10 (PASS, threshold 7)

### P0 Issues (blockers)
1. Supabase schema missing 5 columns (invest_mood, biorhythm_*, today_keywords) that API reads/writes
2. In-memory fallback store loses all data on server restart/deploy
3. RLS policies wide-open -- any anonymous user can read/write all records
4. NEXT_PUBLIC_ anon key used in server-side API routes (should use service role key)

### P1 Issues
- No API input validation
- Interface definitions duplicated across 3+ page files
- Storage branching (Supabase vs local) copy-pasted in 3 routes, no abstraction
- Memos API has no Supabase path (always local-only)
- memo/page.tsx is 740+ lines (god component)
- No standardized error format

### Strengths
- Business logic (report-engine.ts) is well-isolated, pure, testable
- Minimal dependency tree (4 runtime deps)
- State management appropriate (Context for Toast only)
- Clean App Router file structure

### Key Metrics
- ~2.1K LoC TypeScript
- 0% test coverage
- 5 API routes, 7 pages, 8 components, 2 hooks
- scripts/ directory (14 files, 300KB) unrelated to app

**Why:** Baseline for tracking improvement if user addresses issues.
**How to apply:** Reference P0 list when reviewing any future PR or design doc for this project.
