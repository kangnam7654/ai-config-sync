---
name: fit-check-api-design-review
description: fit-check API design re-review (#14) PASS verdict 8.725/10, all 9 prior issues resolved, 3 minor + 1 cosmetic remain, next is consistency check #15, as of 2026-03-31
type: project
---

## fit-check API Design Re-Review - 2026-03-31

**Project:** fit-check (dear-jeongbin repo)
**Path:** /Users/kangnam/projects/dear-jeongbin
**API doc:** docs/llm/api-design.md (37 endpoints, 11 domains, rev.1.1)

**Verdict:** PASS (total 8.725 > 8.0, primary Security 8.5 >= 7)
**Scores:** RESTfulness 9.0, Security 8.5, Performance 8.5, Error Handling 8.5, Business Mapping 9.0

**Previous FAIL (v1.0) Issues -- All 9 Resolved:**
- Critical 1: BM pricing mismatch -> formal credit pricing table added (Gap=1, Doc=2, Interview=1)
- Critical 2: No account deletion -> DELETE /api/v1/account with cascade + PIPA compliance
- Major 3: No CSRF -> Double Submit Cookie on 3 payment endpoints
- Major 4: 500 error undocumented -> 10-code error table, stack trace suppression
- Major 5: Email verification -> MVP omission explicitly documented with rationale
- 4 minor issues (PATCH, Cache-Control, pagination, rollback) all resolved

**Remaining Non-blocking Issues:**
1. [Minor] credit_transactions.status column referenced in API doc but missing from DB schema -- must resolve in Step 15
2. [Minor] DELETE /api/v1/account path not under /auth/ -- file structure may confuse
3. [Minor] BM design doc still says "1 credit = 1 Gap + 1 doc" -- needs sync
4. [Cosmetic] SSE error details use numeric fields vs Record<string, string> envelope type

**Why:** All critical and major blockers from v1.0 were thoroughly addressed. Security posture significantly improved with CSRF, account deletion, error code table. Business alignment resolved with formal pricing table.
**How to apply:** Proceed to Step 15 (DB-API Consistency Check). The credit_transactions.status schema gap is the primary item to validate there.
