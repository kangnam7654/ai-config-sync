---
name: lunawave security audit 2026-03-24
description: Full security audit of lunawave (달결) iOS+Rust backend — key findings and recurring patterns
type: project
---

Full OWASP Top 10 audit performed 2026-03-24.

**CRITICAL findings:**
- Hardcoded Google OAuth client_secrets in backend/src/routes/admin_llm.rs (lines ~263-264, 274-275): two live GOCSPX- secrets for "gemini" and "antigravity" providers. Same pattern as kangnam-client — recurring issue.
- Apple IAP verify_and_grant_points() (services/apple_iap_service.rs) skips JWS signature validation entirely. Any client can claim arbitrary transaction_id + product_id to receive points without a real purchase.
- CORS configured as `CorsLayer::new().allow_origin(Any)` in main.rs:44 — wildcard origin in production.
- grant_admin endpoint (admin_llm.rs:175) has off-by-one: blocks when admin_count > 1, allows when count == 1, meaning a second admin can always be added unauthenticated while exactly one admin exists.

**HIGH findings:**
- Apple ID token JWT signature validation disabled (insecure_disable_signature_validation) and exp validation disabled in auth.rs:141-143.
- Toss webhook signature check skipped entirely when toss_test_mode=true (billing.rs:77) — no guarantee production flag is set.
- Admin LLM endpoints (/admin/llm/*) exposed in public router with only manual JWT check — no rate limiting, brute-forceable.
- Keychain items stored without kSecAttrAccessible flag — default accessibility may allow access when device is locked.
- No rate limiting on /v1/auth/login, /v1/auth/register, /v1/auth/refresh endpoints.

**Why:** Recurring pattern of hardcoded OAuth secrets across this user's projects. Always check admin_llm.rs and any OAuth exchange proxy endpoints for embedded credentials.

**How to apply:** When auditing lunawave or similar projects, prioritize admin_llm.rs and any OAuth exchange routes for hardcoded secrets.
