# CEO Agent Memory

## Active Products
- `01-buybuddy/` -- AI shopping assistant for IT/electronics (Feb 2026)
- `02-flirtiq/` -- AI conversation coaching + ghosting prediction dating app (Feb 2026, R2 submitted for CSO re-review)

## FlirtIQ Key Decisions (R2 -- Post CSO Review)
- Target: Korean market, 25-32 male primary persona
- Pricing: Free / Premium 9,900 KRW (Pro tier removed until PMF confirmed)
- AI: Claude Haiku 4.5 (coaching) + Sonnet 4.5 (Vision/OCR, Beta only)
- MVP: Alpha 2 weeks + Beta +1 week, PWA first
- Alpha: Reply Coach + Ghosting Predictor (text-only, Google OAuth)
- Beta: Vibe Check + FlirtIQ Score + payments + screenshots + Kakao OAuth
- Input: Text-First (copy/paste primary), Screenshot secondary (Beta)
- Privacy: No-Storage architecture -- images never reach server
- Ghosting UI: Traffic light (qualitative), no percentage numbers
- Positioning: "AI coaching/education" not "AI ghostwriting"
- Legal: Must obtain written legal opinion BEFORE dev starts (Week 0)
- Exit criteria: 90-day Red 2+ triggers pivot review

## FlirtIQ Financial Model (R2 -- Corrected)
- Conversion rate: 2-3% conservative (East Asia benchmark: 2.0%)
- Monthly churn: 14-15% (RevenueCat dating app data)
- LTV:CAC: 3.3:1 conservative, 5.3:1 realistic
- Year 2 revenue: 2.4B KRW conservative, 3.2B KRW realistic
- Free-tier AI cost must stay < 60% of MRR (cost cap mechanism)
- Break-even: ~300 paid users (~Month 6-9)

## Market Intelligence (Feb 2026)
- Korean dating app market: ~$144M/year (2025), growing
- WIPPY #1 revenue but Tinder overtook in Jan 2026
- Rizz app: 3.5M downloads, 1M MAU, **$30K/month revenue** (NOT $300K -- corrected)
- Rizz monetization is weak: $0.01 per download, <1% conversion
- No dedicated AI dating coach in Korean market yet
- East Asia dating app subscription conversion: 2.0% (RevenueCat 2025)
- Dating app 12-month retention: 17% (RevenueCat 2025)

## CEO Lessons from CSO Review
- Always verify revenue data from primary sources (not marketing blogs)
- "Conservative" projections must actually be below industry benchmarks
- Legal risk needs architectural solutions, not just "get a lawyer" disclaimers
- Free-tier AI costs can eat 85% of MRR if uncontrolled -- model this explicitly
- TAM should reflect actual addressable segment, not entire adjacent market

## Research Patterns
- SensorTower for Korean app market data
- Business of Apps for global benchmarks
- RevenueCat State of Subscription Apps for conversion/churn benchmarks
- TrendApps for actual app revenue verification
- Korean privacy law: PIPC 2025 AI guidelines, Article 15(1)(6) legitimate interest
