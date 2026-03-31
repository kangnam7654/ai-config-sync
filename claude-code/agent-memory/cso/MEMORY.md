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
- CEO maintains multiple pricing versions across proposal/DB/docs that diverge over time -- always cross-check actual DB migrations + launch docs against proposal claims

## Key Benchmarks (2025-2026)
- A2A protocol: 150+ org partners, Linux Foundation (AAIF) governance (as of 2026-03)
- MCP: 97M installs (2026-03-25), adopted by Anthropic/OpenAI/Google/MS
- VS Code 1.109 (2026-01): native multi-agent orchestration (Claude+Codex+Copilot)
- Claude Code Agent Teams: shipped Feb 2026 with Opus 4.6, mailbox inter-agent communication
- CrewAI: $18M total funding, 100K+ certified devs, Fortune 500 adoption, estimated <$20M ARR
- AI code tools market: $7.88B (2025), projected $70.55B (2034) — Grand View Research
- Claude Code market share: 41% of professional developers (2026 Q1), surpassing Copilot 38%
- East Asia subscription conversion rate: ~2.0% (RevenueCat 2025)
- Dating app monthly subscription 12-month retention: ~17% (83% churn over 12mo)
- Korean dating app market: monthly in-app purchase ~$12M (Aug 2025 peak)
- Korean dating app RPD: ~$14 (2nd highest in Asia after Japan)
- Rizz app Dec 2025: 300K downloads, $30K revenue (Android) — much lower than peak claims
- Hinge paying users: 5% of user base, 1.53M paying (2024), ~70% revenue from subscriptions
- Freemium IAP conversion: 2-5% typical, top 10% achieve 5-8% (RevenueCat 2025)
- RevenueCat 2026: freemium download-to-paid median = 2.1% (hard paywall = 10.7%, 5x better)
- RevenueCat 2026: long trials (17-32 days) convert at 42.5% median; short (<4 days) at 25.5%
- RevenueCat 2026: only 10% of apps run true hybrid (IAP+ads+sub), mostly gaming (4x average)
- 35% of subscription apps now use hybrid model (subscription + consumables) (RevenueCat 2025)
- Dating app ARPU globally: ~$7.73 (2026 est.)
- Tinder revenue: $1.94B (2024), $171M/mo peak (Apr 2025)
- Claude Haiku 4.5: $1/$5 per 1M tokens — AI cost per call = 10-50 KRW (negligible vs revenue)
- Korean iOS rewarded video eCPM: $29 (Q1 2024 peak, Appodeal) — use $18-22 for conservative planning
- Rewarded ad fill rate: Tier 1 = 80-90%, new/low-traffic apps = 60-70%
- 점신(테크랩스) 2024 revenue: 978억, 2025 target: 1,380억, MAU ~79만, cumulative 1,900만 users
- 포스텔러(운칠기삼): cumulative 860만 users, annual revenue 100억+
- Korean fortune/divination market TAM: ~1.4조 (혁신의숲), mobile app market ~1,400억+
- 선불전자지급수단 등록 면제: 발행잔액 30억 미만 AND 연 총발행액 500억 미만
- Apple Small Business Program: 15% commission for <$1M annual revenue (vs standard 30%)

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
- Dalgyeol BM R1: CONDITIONAL (Score 6.9/10) (2026-03-20) — [project_dalgyeol_bm_review.md](project_dalgyeol_bm_review.md)
- AgentBridge R1: OPPOSE (Score 2.85/10) (2026-03-31) — [project_agentbridge_review.md](project_agentbridge_review.md)
  - Fatal: A2A/MCP convergence + VS Code native multi-agent + Claude Code Agent Teams = platform layer absorbing the product
  - SOM $60-360M overestimated 10-50x; CrewAI (category leader) < $20M ARR
  - 4th product before any revenue from first 3 = portfolio dilution
  - Recommended: open-source side project, not product; focus on Dalgyeol launch
- Dalgyeol BM R2: CONDITIONAL (Score 6.1/10) (2026-03-26) — score DECREASED
  - 4 conditions: legal opinion (carried), pricing unification (worsened to 3 versions), UA strategy (new), competition plan (carried)
  - 3 incompatible pricing schemes: proposal vs DB migrations vs launch-checklist
  - Conservative DAU 1,000 revenue estimate: ~676K KRW/mo (CEO low-end 700K is plausible)
  - RevenueCat 2026: freemium conversion median = 2.1%; CEO assumes 10% paying = top-quartile

## Company Context
- Products: 01-buybuddy (MVP complete), 02-flirtiq (approved, planning phase), 03-dalgyeol (Phase 3 complete, near launch)
- Dalgyeol tech stack: Rust/Axum + SwiftUI + PostgreSQL + multi-LLM (Claude, Codex, Copilot, Gemini)
- Team: 1-person bootstrap + AI agent-based development (parallel dev pattern)
- BuyBuddy lessons: see project MEMORY.md for 10 items
- Dalgyeol fixed costs: ~12,300 KRW/mo (near-zero risk)

## Technical Notes
- Anthropic API does NOT support scoped/temporary client-side tokens — always use backend proxy pattern
- Anthropic CORS (`anthropic-dangerous-direct-browser-access` header) exists but exposes API key — not for production
- KakaoTalk "대화 내보내기" (text export) is officially supported — viable Text-First input path
