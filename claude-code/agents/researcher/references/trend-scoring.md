# Trend Scoring Reference

## Metrics Overview

6 metrics divided into two categories:

**Trending metrics (TS):**
- **SVGR** — Search Volume Growth Rate (검색량 증가율)
- **SBI** — Social Buzz Index (SNS 버즈)
- **NFI** — News Frequency Index (뉴스 빈도)

**Steady metrics (SS):**
- **STB** — Stability Score (안정성)
- **VOL** — Base Volume Score (기반 볼륨)
- **SEA** — Seasonality Regularity (계절성)

## Data Collection

For each topic, run WebSearch queries per metric:

| Metric | WebSearch query pattern |
|---|---|
| SVGR | `"{topic} Google Trends"` or `"{topic} 네이버 트렌드"` |
| SBI | `"{topic} site:reddit.com"`, `"{topic} 트위터 반응"` |
| NFI | `"{topic} 뉴스 {현재월}"` |
| STB | `"{topic} Google Trends 12개월"` or `"{topic} 장기 트렌드"` |
| VOL | `"{topic} 검색량"`, `"{topic} 인기도"` |
| SEA | `"{topic} 계절 트렌드"`, `"{topic} 연간 패턴"` |

**N/A handling:**
- WebSearch returns 0 results for a metric → mark N/A
- N/A metrics excluded from weighted average; remaining weights re-distributed proportionally
- 3+ N/A metrics on a single topic → flag "데이터 부족 — 신뢰도 낮음"
- All 6 metrics N/A → exclude topic from ranking, note reason at report bottom

## Scoring Rubrics (0–10 integer scale)

Every score MUST include a 1-sentence evidence citation: `{score} — {evidence source summary}`.

**SVGR (검색량 증가율):**
- 9–10: Recent week 3x+ above 4-week average, "폭발적 증가" in multiple sources
- 7–8: 2x+ above average, "급증" confirmed
- 5–6: 1.2–2x above average, steady interest
- 3–4: Flat or minimal increase
- 1–2: Under 5 search results, minimal recent mentions
- 0: No results (N/A)

**SBI (SNS 버즈):**
- 9–10: 1000+ upvotes posts within 1 week, multi-platform viral
- 7–8: 500+ upvotes posts or 3+ active discussion threads
- 5–6: 10+ related posts but low engagement (<100 each)
- 3–4: Under 5 related posts, minimal reactions
- 1–2: 1–2 posts found in past month
- 0: No social posts (N/A)

**NFI (뉴스 빈도):**
- 9–10: 10+ major outlet headlines in past week, portal main page exposure
- 7–8: 5–9 major articles in past week
- 5–6: 3–4 articles in past week
- 3–4: 1–2 articles in past week
- 1–2: 1–2 articles in past month
- 0: No news (N/A)

**STB (안정성):**
- 9–10: 12-month graph nearly flat, "꾸준한 관심" confirmed
- 7–8: Minor fluctuations only, no spikes/drops
- 5–6: 1–2 notable changes but overall trend maintained
- 3–4: 3+ large fluctuations or declining trend
- 1–2: Extreme volatility (single spike then disappear)
- 0: No 12-month data (N/A)

**VOL (기반 볼륨):**
- 9–10: Top tier in Google Trends comparison, estimated "수십만+" monthly searches
- 7–8: Upper tier, sustained high interest
- 5–6: Mid-level search volume
- 3–4: Niche topic, limited audience
- 1–2: Very low search volume
- 0: No volume data (N/A)

**SEA (계절성):**
- 9–10: Clear annual recurring pattern (e.g., Black Friday, 수능)
- 7–8: Pattern exists but timing/intensity varies
- 5–6: Weak seasonality, pattern hard to confirm
- 3–4: Non-seasonal but irregular fluctuations
- 1–2: Completely non-seasonal, irregular
- 0: Pattern undeterminable (N/A)

## Composite Score Formulas

```
Trending Score (TS) = (SVGR × 0.40) + (SBI × 0.35) + (NFI × 0.25)
Steady Score (SS)   = (STB × 0.40) + (VOL × 0.35) + (SEA × 0.25)
Final Score         = (TS × α) + (SS × β)
```

Default weights: α=0.55, β=0.45

Weight adjustment from user keywords:
- "인기", "핫한", "급상승", "떠오르는" → α=0.70, β=0.30
- "꾸준", "스테디", "안정", "장기" → α=0.30, β=0.70
- Both present or neither → α=0.55, β=0.45

## Output Format

```markdown
# Trend Score Report
> 평가일: {날짜} | 시장: {한국/글로벌} | 카테고리: {범용/지정}
> 가중치: Trending α={값}, Steady β={값}

## 종합 랭킹

| 순위 | 주제 | Final | TS | SS | SVGR | SBI | NFI | STB | VOL | SEA |
|------|------|-------|-----|-----|------|-----|-----|-----|-----|-----|
| 1 | {topic} | {X.X} | {X.X} | {X.X} | {0-10} | {0-10} | {0-10} | {0-10} | {0-10} | {0-10} |

## 주제별 상세 분석

### 1위: {주제명} (Final: X.X)
- **왜 높은가**: {1-2문장 핵심 근거}
- **Trending 근거**: SVGR {점수} — {데이터 출처 요약}
- **Steady 근거**: STB {점수} — {데이터 출처 요약}
- **주의점**: {있으면 기재}
```

If previous report exists in the same directory, add a `변동` column: `+N`, `-N`, `=`, `NEW`, `OUT`.

## NEVER Rules

1. NEVER use paid APIs (Google Trends API, SEMrush, Ahrefs, Moz, SimilarWeb). WebSearch/WebFetch only.
2. NEVER evaluate more than 15 topics in a single run. If input exceeds 15, ask the user to narrow scope.
3. NEVER assign a score without data evidence. If WebSearch returns 0 results for a metric, mark N/A.
4. NEVER provide investment advice, buy/sell recommendations, or revenue projections. Trend data analysis only.
5. NEVER output a report without the Final Score formula and weights stated in the report header.

## Topic Discovery (auto-discover mode)

Run WebSearch queries to find 5–15 candidate topics:

Korean market queries:
- `"2026 트렌드 키워드"`, `"요즘 핫한 키워드 {현재월}"`
- `"네이버 실시간 검색어"`, `"구글 트렌드 한국"`

Global market queries:
- `"trending topics {month} 2026"`, `"Google Trends rising"`
- `"Reddit popular today"`, `"HackerNews front page"`

Select 5–15 topics. Avoid overly broad terms (e.g., "AI" → refine to "AI 에이전트 프레임워크").

Market scope:
- No explicit mention → Korean market (Naver + Google Korea sources)
- "글로벌", "미국", English keywords → Global market
