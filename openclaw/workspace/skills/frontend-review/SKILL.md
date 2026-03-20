---
name: frontend-review
description: "Review and score app/web UI against current design trends using screenshot-based analysis. Use this skill whenever the user wants UI/UX feedback, design critique, trend comparison, or visual quality assessment of any existing interface — screenshots, live URLs, running local apps, or iOS Simulator apps. Triggers on: 'UI 리뷰해줘', 'this design looks off', 'compare our UI to competitors', 'is this UI modern enough', 'UI 분석', 'design audit', 'UI 점수 매겨줘', '화면 디자인 괜찮은지 봐줘', '경쟁 앱이랑 비교해줘', '시뮬레이터에서 돌아가는 앱 UI 봐줘', 'review the app running in the simulator'. Also trigger when the user shares a screenshot and asks for visual feedback, even without explicitly saying 'review'. When the user mentions an iOS Simulator app without providing a screenshot, this skill requests the main model to spawn ios-simulator agent for screenshot capture before proceeding with review. This skill REVIEWS existing UI — for BUILDING new UI, use frontend-design instead."
---

Evaluate existing app/web interfaces by combining screenshot analysis with current trend research. Produce an actionable scorecard with concrete improvement suggestions — every finding pairs a specific visual problem with an implementable fix including exact values.

## Relationship with frontend-design

These two skills form a review-then-build cycle:

- **frontend-review** (this skill): Diagnoses existing UI — finds problems, scores dimensions, suggests fixes with exact CSS/design values
- **frontend-design**: Creates new UI from scratch with bold aesthetic direction

Typical flow: frontend-review identifies issues → user takes findings to frontend-design for implementation. Include enough specifics (hex codes, px sizes, font names) that frontend-design can act directly on the findings.

## Boundaries

### ALWAYS
- Complete Step 2 (trend research) before scoring in Step 3 — scores without trend context are arbitrary opinion, not evidence-based assessment.
- Include source URLs for every trend data point cited in the report.
- Mark unobservable dimensions as N/O rather than estimating — a wrong score is worse than no score.
- Identify the domain category before starting trend research — domain determines which benchmarks are relevant.

### NEVER
- Generate implementation code (HTML/CSS/JS/React). This skill produces a diagnostic report only — code generation belongs to frontend-design.
- Modify the user's source files. The output is a review report, not a code change.
- Skip Step 2 (trend research), even if the user says "just score it quickly." Without trend context the Trend Alignment dimension cannot be scored, and other dimensions lose their market-relative grounding.
- Fabricate benchmark data or competitor references. If WebSearch returns insufficient trend data, state what was found and note the gap per the edge case table.
- Suggest visual changes without specifying exact values (hex codes, px/rem sizes, font names, border-radius). Vague advice is not actionable.

## Workflow

### Step 1: Collect UI Input

Accept one or more of these input types:

- **Screenshot file path(s)** → Read the image file(s) directly
- **Live URL** → Capture with `npx playwright screenshot --full-page {url} /tmp/ui-review-$(date +%s).png`
- **Local app** → Capture with `npx playwright screenshot --full-page http://localhost:{port} /tmp/ui-review-$(date +%s).png`
- **iOS Simulator app** → See "iOS Simulator 연동" section below
- **Figma reference** → Ask the user to export a screenshot

If no input is provided, ask: "리뷰할 UI를 제공해주세요 — 스크린샷 파일 경로, URL, 로컬 서버 포트, 또는 iOS 시뮬레이터 앱 중 하나를 알려주세요."

#### iOS Simulator 연동

iOS 시뮬레이터에서 실행 중인 앱의 UI를 리뷰할 때 사용한다. 이 스킬은 ios-simulator 에이전트를 직접 호출하지 않는다 (NEVER 규칙 #10: 서브에이전트 간 직접 호출 금지). 대신 메인 모델에게 스크린샷 캡처를 요청한다.

**스크린샷이 이미 있는 경우:** 일반 스크린샷과 동일하게 바로 리뷰를 진행한다.

**스크린샷이 없는 경우:** 아래 메시지를 메인 모델에게 반환한다:

```
iOS 시뮬레이터 스크린샷이 필요합니다.
ios-simulator 에이전트를 스폰하여 다음을 수행해주세요:
1. 현재 부팅된 시뮬레이터의 스크린샷 캡처 (xcrun simctl io booted screenshot)
2. 캡처된 스크린샷 경로를 이 스킬에 전달

필요 정보:
- 앱 bundle ID: {사용자가 제공한 경우 포함, 없으면 "현재 화면 캡처"}
- 특정 화면 이동 필요 여부: {딥링크나 특정 화면이 언급된 경우}
```

메인 모델이 ios-simulator 에이전트를 통해 스크린샷을 캡처한 후, 해당 이미지 경로를 받아 Step 2부터 진행한다.

**여러 화면 리뷰가 필요한 경우:** 메인 모델에게 ios-simulator 에이전트가 Maestro 플로우로 여러 화면을 순회하며 각 화면의 스크린샷을 캡처하도록 요청한다.

Identify the **domain category** (e.g., "fintech", "e-commerce", "SaaS dashboard", "social media"). This determines which competitors to benchmark against — comparing a fintech app to a social media app produces meaningless results unless the user explicitly requests cross-domain comparison.

### Step 2: Research Current Trends

Design quality is relative — what looks "good" depends on current market expectations. This step is mandatory because without trend context, scoring becomes arbitrary opinion rather than evidence-based assessment.

Run 3-5 WebSearch queries for the identified domain:

- `"{domain} app UI trends 2025 2026"`
- `"best {domain} app design awards 2025 2026"`
- `"{domain} UI design patterns mobile web"`
- `"top {domain} apps UI comparison"`
- `"{domain} 앱 디자인 트렌드 2025 2026"` (Korean sources for Korean apps)

Use WebFetch on top 2-3 results to extract specific design patterns, color palettes, layout approaches, and interaction patterns.

**Output format:**

```
## Trend Context: {domain}

### 조사 소스
1. [{Title}]({URL}) — {1-line summary}
2. [{Title}]({URL}) — {1-line summary}
3. [{Title}]({URL}) — {1-line summary}

### 트렌드 요약
- **색상**: {dominant palettes with hex values}
- **타이포그래피**: {font trends, size hierarchies}
- **레이아웃**: {grid, spacing, whitespace patterns}
- **네비게이션**: {navigation pattern trends}
- **마이크로인터랙션**: {animation/transition trends}
- **접근성**: {adopted standards}

### 벤치마크 앱/사이트
1. {name} — {why it's a benchmark} — {URL}
2. {name} — {why it's a benchmark} — {URL}
3. {name} — {why it's a benchmark} — {URL}
```

### Step 3: Analyze Screenshot (8 Dimensions)

Score each dimension 1-10. Reference specific elements by position (e.g., "top-left logo area", "bottom navigation bar") and approximate pixel coordinates when possible.

| # | Dimension | Key Questions |
|---|-----------|---------------|
| 1 | **Visual Hierarchy** | Most important content most prominent? Clear CTA? F/Z reading flow? |
| 2 | **Color & Contrast** | Harmonious palette (1 primary + 2 secondary + 2 neutral max)? WCAG 2.1 AA (4.5:1 body text, 3:1 large text)? |
| 3 | **Typography** | Readable at all sizes? Clear hierarchy (heading/subheading/body/caption)? Line height 1.4-1.6x? Max 2 font families? |
| 4 | **Spacing & Alignment** | Consistent rhythm (4px/8px grid)? Grid-aligned? Balanced whitespace? |
| 5 | **Layout & Composition** | Content density balanced? Responsive-ready? Sections clearly delineated? |
| 6 | **Navigation & Affordance** | Interactive elements clearly tappable (min 44x44px)? Intuitive navigation? Distinguishable states (hover, active, disabled)? |
| 7 | **Consistency** | Same-type elements styled identically? Coherent design system (border-radius, shadow, button styles)? |
| 8 | **Trend Alignment** | How does this compare to Step 2 benchmarks? Which current patterns are adopted? Which are missing? |

For dimensions not observable from a static screenshot (e.g., animations, transitions), mark as **"N/O (Not Observable)"** rather than guessing. Exclude N/O dimensions from the average score calculation.

### Step 4: Generate Findings Report

Include only dimensions scoring below 8. Rank by impact (highest-impact first). Maximum 10 findings — this keeps the report actionable rather than overwhelming.

Each finding must include all five fields:

- **위치**: Element position in screenshot (compass direction + approximate coordinates)
- **현재**: Exact description of current state
- **문제**: Why this is a problem — reference trend data from Step 2 or an accessibility standard
- **개선**: Exact fix with values (hex colors, px/rem sizes, font names, border-radius, etc.)
- **벤치마크**: Which competitor app does this well, and how

The reason for requiring exact values: vague advice like "improve the contrast" is not actionable. Specific advice like "change body text from #999 to #666 on #fff background (contrast ratio 4.48:1 → 5.74:1)" can be implemented immediately.

## Output Format

```markdown
# UI Review Report

> Reviewed: {YYYY-MM-DD}
> Target: {app/site name or URL}
> Domain: {domain category}
> Screenshots analyzed: {count}

## Trend Context

{from Step 2 — full section}

## Scorecard

| # | Dimension | Score | Justification |
|---|-----------|-------|---------------|
| 1 | Visual Hierarchy | {1-10} | {evidence from screenshot} |
| 2 | Color & Contrast | {1-10} | {evidence} |
| 3 | Typography | {1-10} | {evidence} |
| 4 | Spacing & Alignment | {1-10} | {evidence} |
| 5 | Layout & Composition | {1-10} | {evidence} |
| 6 | Navigation & Affordance | {1-10} | {evidence} |
| 7 | Consistency | {1-10} | {evidence} |
| 8 | Trend Alignment | {1-10} | {evidence} |

**Overall: {average of scored dimensions}/10**

## Findings

### Finding 1: [{dimension}] {problem title}
- **위치**: {element position}
- **현재**: {current state}
- **문제**: {why — reference trend/standard}
- **개선**: {exact fix with values}
- **벤치마크**: {competitor reference}

### Finding 2: [{dimension}] {problem title}
{same structure}

{... up to 10 findings}

## Quick Wins (< 1 hour each)
1. {specific change with exact values}
2. {specific change with exact values}
3. {specific change with exact values}

## Strategic Improvements (require design iteration)
1. {larger change requiring mockup/prototype}
2. {larger change requiring mockup/prototype}

## Verdict

| Rating | Range | Meaning |
|--------|-------|---------|
| Excellent | 8.0-10.0 | Industry-leading UI, minor polish only |
| Good | 6.0-7.9 | Solid foundation, targeted improvements needed |
| Needs Work | 4.0-5.9 | Significant gaps vs industry standard |
| Critical | 1.0-3.9 | Major redesign recommended |

**This UI scores {overall}/10 — {rating}.**
{1-2 sentence summary: biggest strength + biggest opportunity}
```

## Edge Cases

| Situation | Resolution |
|-----------|------------|
| Playwright not installed | Report: "Playwright가 설치되어 있지 않습니다. `npx playwright install chromium`을 실행하거나 스크린샷을 직접 제공해주세요." |
| Low-res screenshot (<720px wide) | Score only clearly observable dimensions, mark others N/O. Ask for higher resolution. |
| Static image (poster/banner), not app UI | Decline: "이 스킬은 앱/웹 UI 리뷰 전용입니다. 정적 이미지 디자인 리뷰는 지원하지 않습니다." |
| No trending apps found for domain | Broaden to adjacent domains. Note: "{domain}의 직접 트렌드 데이터가 부족하여 인접 도메인을 참고했습니다." |
| 5+ screenshots | Full review for first 3, summary scorecard (scores + 1-line each) for the rest. |
| Partially loaded or error state | Review visible elements only. Add finding noting incomplete state and requesting complete screenshot. |
| User requests specific competitor comparison | Add specified competitor to benchmarks. Capture or search for their UI screenshots. |
| Cross-domain comparison requested | Proceed but note reduced comparability in the Trend Context section. |
| iOS Simulator app but no simulator booted | Return to main model: "시뮬레이터가 부팅되어 있지 않습니다. ios-simulator 에이전트로 시뮬레이터를 부팅하고 앱을 실행한 후 스크린샷을 캡처해주세요." |
| iOS Simulator app but ios-simulator agent unavailable | Fall back to manual: "xcrun simctl io booted screenshot /tmp/ui-review-sim.png 으로 직접 스크린샷을 캡처해주세요." |
| Multiple iOS Simulator screens to review | Request main model to spawn ios-simulator with a Maestro flow that navigates screens and captures screenshots at each step. |

## Communication

- Respond in the user's language
- Reference positions using compass directions (top-left, center, bottom-right) and approximate pixel coordinates
- Always include source URLs when citing trend data
- Provide CSS/design values precise enough for frontend-design to implement directly
