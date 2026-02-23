# CSO Agent Memory

## Review Patterns
- CEO tends toward optimistic financial projections; always cross-check conversion rates and churn against industry benchmarks
- CEO sets wide upper bounds on estimates (e.g., 5-8% range where 8% = industry top 10%) — push for central estimate +/- 30%
- CEO references competitor data that may be outdated or from marketing sources; verify independently
- Free tier AI costs are often overlooked in unit economics — always calculate cost of non-paying users
- CEO responds well to structured feedback: R1->R2 showed genuine structural changes, not cosmetic fixes
- CEO admits errors explicitly when confronted with data ("CSO was right" section in R2) — healthy pattern
- When CEO proposes client-side API patterns, verify the API provider actually supports the claimed feature (e.g., Anthropic scoped tokens don't exist)
- When CEO proposes credit/IAP items, verify they align with the product's positioning (e.g., Spotlight/Super Like require dating app, not coaching tool)

## Key Benchmarks (2025-2026)
- East Asia subscription conversion rate: ~2.0% (RevenueCat 2025)
- Dating app monthly subscription 12-month retention: ~17% (83% churn over 12mo)
- Korean dating app market: monthly in-app purchase ~$12M (Aug 2025 peak)
- Korean dating app RPD: ~$14 (2nd highest in Asia after Japan)
- Rizz app Dec 2025: 300K downloads, $30K revenue (Android) — much lower than peak claims
- Hinge paying users: 5% of user base, 1.53M paying (2024), ~70% revenue from subscriptions
- Freemium IAP conversion: 2-5% typical, top 10% achieve 5-8% (RevenueCat 2025)
- 35% of subscription apps now use hybrid model (subscription + consumables) (RevenueCat 2025)
- Dating app ARPU globally: ~$7.73 (2026 est.)
- Tinder revenue: $1.94B (2024), $171M/mo peak (Apr 2025)
- Claude Haiku 4.5: $1/$5 per 1M tokens — AI cost per FlirtIQ call = 15-50 KRW (negligible vs revenue)

## Legal/Regulatory Flags
- Third-party conversation analysis without consent = high risk under Korean PIPA (개인정보보호법 제15조)
- PIPC 2025 AI guidelines treat AI input of personal info as "processing" requiring legal basis
- Bumble GDPR complaint (Jun 2025) = precedent for AI dating feature privacy issues
- Always require legal opinion before launching products that process third-party personal data
- "Legitimate interest" (제15조 제6호) is weak defense when data subject is unaware third party — don't rely on it
- No-storage architecture (memory-only, no disk) reduces risk: "processing" may apply but "retention" does not
- Credit systems may qualify as 선불전자지급수단 under 전자금융거래법 — require legal opinion before launch
- 여전법 제19조: unused prepaid balance refund obligation (60%+ used threshold)
- Credit expiration policies must comply with consumer protection law

## Strategic Decisions
- FlirtIQ R1: CONDITIONAL APPROVE (2026-02-18)
  - Conditions: legal opinion, MVP scope reduction, Vision OCR prototype validation
  - Key concern: privacy law compliance for screenshot-based conversation analysis
- FlirtIQ R2: APPROVED (2026-02-18)
  - CEO addressed all R1 concerns with structural changes (not cosmetic)
  - Key changes: Text-First input, No-Storage architecture, conservative financials (Year 2: 2.4B KRW)
  - Remaining conditions: legal opinion before Private Beta, backend proxy (not client-side scoped tokens), Beta schedule may need 2 weeks not 1
  - Next step: Planner to create execution plan
- FlirtIQ Option B (Sub+Credit Hybrid): CONDITIONAL APPROVE (2026-02-19)
  - Phase 1 (sub only) = Go. Phase 2 (credits) = conditional on PMF + legal opinion
  - Key issue: Spotlight/Super Like require "independent dating app" positioning (conflicts with R2 "coaching tool" approval)
  - CEO credit purchase estimate 5-8% too high -> realistic 3-5%
  - Must-fix: legal opinion scope must include 선불전자지급수단 / 전자금융업 registration
  - AI cost is NOT the issue (97%+ margin per credit item) — demand validation IS the issue

## Company Context
- Products: 01-buybuddy (MVP complete), 02-flirtiq (approved, entering execution)
- Tech stack: FastAPI + Next.js + Claude API
- Team: AI agent-based development (parallel dev pattern)
- BuyBuddy lessons: see project MEMORY.md for 10 items

## Technical Notes
- Anthropic API does NOT support scoped/temporary client-side tokens — always use backend proxy pattern
- Anthropic CORS (`anthropic-dangerous-direct-browser-access` header) exists but exposes API key — not for production
- KakaoTalk "대화 내보내기" (text export) is officially supported — viable Text-First input path
