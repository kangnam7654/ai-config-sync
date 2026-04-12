# Market Research Reference

## Multi-Source Research Methodology

### Depth Levels

| Level | Sources | WebSearch Calls | WebFetch Calls | Use When |
|---|---|---|---|---|
| **quick** | 3–5 | max 5 | max 2 | Single-topic fact-checks, one-question lookups |
| **standard** | 8–12 | max 10 | max 5 | Comparisons, market data, multi-question research |
| **deep** | 15+ | max 15 | max 8 | Comprehensive landscape analysis, critical decision support |

### Proven Search Patterns

| Research Type | Effective Query Pattern | Example |
|---|---|---|
| Tech comparison | `"{A} vs {B} benchmark {year}"` + `"{A} migration from {B} experience"` | `"React vs Vue benchmark 2026"` |
| Market data | `"{keyword} market size TAM"` + `"site:statista.com {keyword}"` | `"AI code assistant market size TAM"` |
| Production experience | `"site:reddit.com {tech} production"` + `"{tech} postmortem"` | `"site:reddit.com Supabase production"` |
| Pricing/cost | `"{service} pricing {year}"` + `"{service} vs {competitor} cost comparison"` | `"Vercel pricing 2026"` |
| Adoption/trends | `"{tech} adoption rate"` + `"{tech} state of {ecosystem} survey"` | `"TypeScript adoption rate state of JS survey"` |
| Technical limits | `"{tech} limitations"` + `"{tech} scaling issues production"` | `"SQLite limitations scaling issues production"` |

### Source Search Angles

Execute searches from multiple angles within the assigned depth's tool budget:
- Direct topic searches + "vs" comparisons
- "{topic} benchmark {current year}" for quantitative data
- "{topic} production experience" for real-world signals
- Reddit, Hacker News, dev.to for practitioner opinions
- Korean sources (Naver, Korean tech blogs) when the user communicates in Korean
- Official documentation and changelogs for version-specific data
- GitHub stars/issues, npm downloads, Stack Overflow tags for health metrics

### Source Evaluation Criteria

| Criterion | Rule |
|---|---|
| **Recency** | Prefer last 12 months. Flag anything older with "[as of YYYY-MM]" |
| **Authority** | Official docs > recognized experts > blog posts > anonymous forums |
| **Corroboration** | Claims in 2+ independent sources → stated as fact. Single source → "Low confidence" |
| **Data vs Opinion** | Label: "[data]" for benchmarks/numbers, "[opinion]" for subjective views |
| **Conflict** | When sources contradict, present both sides with confidence rating "Low — contradictory sources [N] vs [M]" |

Use WebFetch on the 3–5 search results that directly answer the research questions. Skip results that do not contain quantitative data or firsthand experience.

## Technology Comparison Approach

When comparing 2+ technologies/tools/frameworks:
- Use measurable criteria only: GitHub stars, npm downloads, benchmark ms, $/mo pricing
- Build a comparison table with consistent criteria across all options
- Cross-validate numbers from multiple sources before reporting
- Flag version-specific data with the version number and date

## Competitor Analysis Patterns

Gather per competitor:
- Feature matrix (what it does / does not do)
- Pricing table (all tiers, per-unit costs)
- Public financials / funding rounds (if available)
- Market positioning (target segment, key differentiators)
- Community health (GitHub issues, Stack Overflow activity, Discord/Slack size)

## Output Format for Research Reports

```
# Research Report: {Topic}

> Researched: {YYYY-MM-DD}
> Depth: {quick | standard | deep}
> Requested by: {user | ceo | cso | agent-name}
> Sources consulted: {N}

## Executive Summary
- {Finding 1: most important data point with number/source}
- {Finding 2: second data point}
- {Finding 3: third data point}

## Findings

### {Section 1 title}
{Factual content with inline citations [1], [2]}

## Comparison Table
| Criteria | Option A | Option B | Source |
|---|---|---|---|
| {metric} | {value} | {value} | [N] |

## Data Gaps
- {Gap 1: what data is missing and why}

## Confidence Assessment
| Finding | Confidence | Basis |
|---|---|---|
| {key finding} | High / Medium / Low | {basis} |

## Sources
1. [{Title}]({URL}) — {1-line summary} — accessed {YYYY-MM-DD}
```

## Citation Requirements

- Attribute every data point to a numbered source in the Sources section — zero unattributed claims
- Require 2+ independent corroborating sources before stating any claim as fact
- Tag every data point with its date using "[as of YYYY-MM]" format
- Label data vs opinion explicitly: "[data]" for benchmarks/numbers, "[opinion]" for subjective views
- If data is unavailable: state "No publicly available data found for {X} as of {date}"
- Single source: mark finding as "Low confidence — single source [N]"
- List every URL accessed in Sources, even if unhelpful (mark as "[limited value]")
