---
name: fit-check DB-API Consistency Check
description: fit-check consistency check #15 FAIL 7.15/10, 5 mismatches (2 critical, 2 major, 1 minor), next_step 11, as of 2026-03-31
type: project
---

fit-check DB-API consistency check FAIL, score 7.15/10, 5 mismatches identified.

**Why:** DB schema (PASS 8.63) and API design (PASS 8.725) individually passed review, but cross-validation revealed phantom columns (credit_transactions.status, resumes.deleted_at, payments.canceled_at/cancel_reason) and enum mismatches (user_events.event_type).

**How to apply:**
- M01 (critical): credit_transactions needs status column for rollback tracking
- M02 (critical): resumes soft delete (deleted_at) not in DB -- recommend changing API to hard delete
- M03 (major): payments needs canceled_at + cancel_reason columns
- M04 (major): event_type enum mismatch between DB (9 types) and API (6 types)
- M05 (minor): referral_code derivation rule needs explicit documentation
- Classification: BOTH (schema + endpoint mismatches)
- next_step: 11 (DB schema revision first, then API revision)
