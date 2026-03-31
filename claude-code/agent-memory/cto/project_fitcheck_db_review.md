---
name: fit-check-db-schema-review
description: fit-check DB schema review (#12) FAIL verdict, scored 7.45/10, 2 critical RLS issues (AI tables client INSERT + payments client DELETE), as of 2026-03-31
type: project
---

## fit-check DB Schema Review - 2026-03-31

**Project:** fit-check (dear-jeongbin repo)
**Path:** /Users/kangnam/projects/dear-jeongbin
**Schema doc:** docs/llm/db-schema.md (13 tables, 1307 lines)

**Verdict:** FAIL (total 7.45 < 8.0 threshold)
**Scores:** Normalization 8, Indexing 8, Security(RLS) 6, Scalability 7, Business Mapping 8

**Critical Issues (block PASS):**
1. gap_analyses, generated_documents, interview_questions have client INSERT RLS policies -- AI-generated data should be server-side write only
2. payments has client DELETE RLS policy -- payment records must be immutable

**Major Issues:**
3. user_events INSERT allows user_id IS NULL from authenticated clients
4. No referral tracking structure despite BM design requiring it

**Why:** RLS security score (6/10) dragged total below 8.0. Fix critical items -> Security ~8 -> total ~8.0+
**How to apply:** On resubmission, verify all AI-result tables and financial tables have SELECT-only client RLS. Check referral structure added or Phase 2 deferred.
