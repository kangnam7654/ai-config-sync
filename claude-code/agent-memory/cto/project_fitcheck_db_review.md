---
name: fit-check-db-schema-review
description: fit-check DB schema review (#12) PASS verdict (re-review), scored 8.63/10, all 4 previous issues resolved, 3 minor items remain, as of 2026-03-31
type: project
---

## fit-check DB Schema Review - 2026-03-31 (Re-review)

**Project:** fit-check (dear-jeongbin repo)
**Path:** /Users/kangnam/projects/dear-jeongbin
**Schema doc:** docs/llm/db-schema.md (14 tables, ~1488 lines, rev.2)

**Verdict:** PASS (total 8.63 > 8.0, primary normalization 8.5 >= 7)
**Scores:** Normalization 8.5, Indexing 8.5, Security(RLS) 9.0, Scalability 8.0, Business Mapping 9.0

**Previous Issues (all resolved):**
1. [Critical] AI tables client INSERT removed -> SELECT-only
2. [Critical] payments DELETE removed -> immutable, server write-only
3. [Major] user_events user_id NOT NULL enforced, auth.uid() = user_id
4. [Major] referrals table added with self-referral CHECK, referred_id UNIQUE

**Remaining Minor Items (non-blocking):**
- user_events partitioning threshold not specified (recommend at 1M rows)
- payments DB-level DELETE rule/trigger for defense-in-depth (optional)
- credit_balances "no expiry" policy should be explicit in table comment

**Why:** Previous FAIL was 7.45 driven by RLS security score of 6. Re-review shows security jumped to 9.0 after all CTO feedback incorporated.
**How to apply:** Schema is approved. Next step is #13 (API design by backend-dev). DBA reviews partitioning/optimization in Build Phase.
