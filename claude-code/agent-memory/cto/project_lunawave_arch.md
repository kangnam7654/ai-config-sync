---
name: Lunawave (Dalgyeol) Architecture State
description: Architecture health baseline for Rust+Swift saju fortune app - comprehensive diagnostic scores and prioritized issues as of 2026-03-24
type: project
---

Lunawave/Dalgyeol -- saju fortune + AI consult platform.

**Stack**: Rust (Axum 0.8, sqlx 0.8, tokio) backend + SwiftUI iOS (MVVM) + PostgreSQL on Fly.dev.

**Metrics (2026-03-24)**:
- Backend: ~96 .rs files, ~13.9K LOC (saju engine alone ~3200 LOC)
- iOS: ~72 .swift files, ~13K LOC
- 20 DB migrations (no DOWN scripts)
- admin_llm.rs 1118 LOC (largest file, includes HTML)

**Comprehensive Diagnostic Scores (2026-03-24)**:
- Code Quality: 5.5/10
- Security: 4.4/10 (lowest risk-adjusted)
- Architecture: 6.0/10
- DB: 5.85/10
- Testing: 3.99/10 (lowest absolute)
- UX/UI: 6.50/10
- Weighted Average: 5.37/10

**P0 Critical Issues (11 items)**:
1. SEC-01: Google OAuth client_secret hardcoded in admin_llm.rs:263,275 -- CREDENTIAL ROTATION NEEDED
2. SEC-02: Apple JWT insecure_disable_signature_validation in auth.rs:141
3. SEC-03: CORS allow_origin(Any) in main.rs:45
4. SEC-04: admin_llm::routes() on public router (mod.rs:30)
5. SEC-05: Apple IAP JWS verification not implemented
6. SEC-06: grant_admin off-by-one (>1 should be >=1) in admin_llm.rs:175
7. ARCH-01: wallet_service::add_ledger_entry non-transactional (race condition, double-spend)
8. CODE-01: let _ = signup bonus in auth_service.rs:69,274
9. DB-01: get_balance SUM full scan, cache exists but unused on read path
10. TEST-01: No CI/CD pipeline
11. UX-01: Zero accessibility (Dynamic Type 0, VoiceOver 0, 580 hardcoded fonts)

**Gate Decision**: PROCEED -- design-loop for architecture + db + ux_ui required.

**Why:** Baseline for improvement tracking. SEC-01 requires immediate manual credential rotation before design-loop.
**How to apply:** Reference these scores when reviewing improvement PRs. Track P0 count reduction per phase.
