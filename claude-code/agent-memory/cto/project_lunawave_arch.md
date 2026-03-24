---
name: Lunawave (Dalgyeol) Architecture State
description: Architecture health baseline for Rust+Swift saju fortune app - tech stack, known issues, code metrics as of 2026-03-24
type: project
---

Lunawave/Dalgyeol -- saju fortune + AI consult platform.

**Stack**: Rust (Axum 0.8, sqlx 0.8, tokio) backend + SwiftUI iOS (MVVM) + PostgreSQL on Fly.dev.

**Metrics (2026-03-24)**:
- Backend: ~88 .rs files, ~8500 LOC (saju engine alone ~3200 LOC)
- iOS: ~65 .swift files, ~10500 LOC in Views
- 90 unit tests passing, 11 integration tests fail (no DB)
- 21 clippy warnings (none critical)
- 20 DB migrations

**Key architecture issues identified**:
1. CRITICAL: Apple OAuth `insecure_disable_signature_validation` in auth.rs:141
2. CRITICAL: CORS `allow_origin(Any)` in production
3. HIGH: No rate limiting middleware (AppError::RateLimited defined but never applied)
4. HIGH: N+1 queries in reading_service::list_readings (loop fetches outputs per reading)
5. HIGH: wallet_service::add_ledger_entry has no transactional locking (race condition)
6. HIGH: 21 route handlers duplicate manual body extraction pattern (axum::body::to_bytes)
7. MEDIUM: All iOS models use `let id: String` while backend DTOs use `Uuid` (works because serde serializes UUID as string, but fragile)
8. MEDIUM: No RLS policies in any migrations despite multi-user data
9. MEDIUM: reading_service::create_reading is 306 lines -- God Function
10. MEDIUM: 33 SELECT * queries in services layer

**Why:** Baseline for future reviews and refactoring prioritization.
**How to apply:** Reference these scores when evaluating PRs or planning technical debt sprints.
