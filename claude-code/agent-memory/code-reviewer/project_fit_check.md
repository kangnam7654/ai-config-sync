---
name: fit-check project patterns
description: fit-check MVP code quality baseline — critical payment/credit bugs, open redirect, free-count off-by-one, and missing idempotency guard
type: project
---

fit-check is a Next.js 15 + Supabase + Prisma + Claude Haiku + 토스페이먼츠 MVP (167 source files, 31 API routes, 24 pages).

**Why:** First full MVP review requested 2026-03-31. Focus on credit atomicity, payment re-verification, SSE streaming, gap-analysis.

**How to apply:** When touching payment/credit code, verify these known issues are resolved before approving:

1. `payment.service.ts` `confirmPayment`: no guard against double-confirm (status already "done") → double credit grant risk.
2. `payment.service.ts` `cancelPayment`: calls Toss API with `PENDING-{orderId}` key if payment never confirmed — will get a 400 from Toss but is caught and rethrown; not a silent data corruption but wastes a network call.
3. `payment.service.ts` `confirmPayment` first_purchase detection: counts AFTER `addCredits` writes the current payment row as "done", so `previousPayments === 1` fires correctly for the first purchase but is fragile (uses count instead of explicit flag).
4. `credit.service.ts` `deductCredit`: `txType` is hardcoded `"consume"` for both free and paid paths (ternary is `isFree ? "consume" : "consume"`) — no differentiation between free and paid consume in the ledger.
5. `gap-analysis.service.ts` `createGapAnalysisStream`: `free_remaining` in the SSE start event uses `Math.max(0, 2 - freeUsedThisMonth)` (hardcoded 2) instead of `3 - freeUsedThisMonth`, off-by-one relative to the 3-free-per-month rule.
6. `auth/callback/route.ts`: `next` query param is concatenated to origin without validation — open redirect vulnerability.
7. `rate-limit.ts`: in-process Map; not shared across serverless instances — rate limiting is non-functional in multi-instance deploys (Vercel, etc.).
8. `referral.service.ts`: `completReferralBonus` (typo: missing 'e') is never called from `payment.service.ts` after first purchase — referral bonus is never granted.
9. `resume.service.ts` `uploadResumeFile`: text extraction is a stub placeholder, not real content.
10. `auth/login/route.ts`: `access_token` is returned in JSON response body — tokens should travel only via HttpOnly cookies.
