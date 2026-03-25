# Auto-Improve Context for Round 2

This document contains the context to pass to the next improvement round.

## Project

- Path: `/tmp/mock-webapp`
- Progress file: `/tmp/mock-webapp/docs/llm/improve-progress.yaml`

## Resume State

- Resuming from: Round 2 (was `in_progress`, no round 2 work was committed)
- Effective baseline: Round 1's `final_scores`
- Rounds remaining: 4 (rounds 2-5 of max 5)

## Baseline Scores (Round 1 Final)

```yaml
code_quality: 6.5
security: 6.0
architecture: 6.5
db: 7.5
test_coverage: 5.0
repo_health: 6.0
ux_ui: 6.5
```

Target: 8.0 for all areas.

## Priority Queue for Round 2

### Must-Fix (P1 items carried from round 1)

1. **TEST-001** — No integration tests for payment flow
   - Area: test_coverage (score: 5.0, gap: -3.0, largest gap)
   - Implementation notes:
     - payment 모듈 테스트 시 mock DB가 필요함 (round 1 learning)
     - user search API 시그니처가 round 1에서 변경됨 — 새 시그니처를 사용할 것 (round 1 learning)

2. **ARCH-001** — Circular dependency in core modules
   - Area: architecture (score: 6.5, gap: -1.5)
   - Approach: dependency inversion 또는 shared interface 추출

### Should-Improve (score-based, no specific item ID)

3. **security** (score: 6.0, gap: -2.0) — Audit for additional vulnerabilities beyond SEC-001 (SQL injection, fixed in round 1).
4. **repo_health** (score: 6.0, gap: -2.0) — Linting, CI, documentation gaps.
5. **code_quality** (score: 6.5, gap: -1.5) — May improve as side effect of ARCH-001 fix.
6. **ux_ui** (score: 6.5, gap: -1.5) — Lower priority, address if time permits.
7. **db** (score: 7.5, gap: -0.5) — Nearly at target, minimal effort needed.

## Items Already Addressed (Do Not Re-Fix)

- **SEC-001** — SQL injection in user search (fixed in round 1, security score went from 4.0 to 6.0)

## Round 1 Learnings (Apply in Round 2)

1. payment 모듈 테스트 시 mock DB 필요 — Set up a mock DB fixture (e.g., SQLite in-memory or test doubles) before writing payment integration tests.
2. user search API 시그니처가 변경됨 — The user search API signature was modified as part of the SEC-001 fix. Any tests or code referencing the old signature must use the updated one.

## Score Deltas from Round 1 (for trend tracking)

| Area | Before R1 | After R1 | Delta |
|------|-----------|----------|-------|
| code_quality | 5.5 | 6.5 | +1.0 |
| security | 4.0 | 6.0 | +2.0 |
| architecture | 6.0 | 6.5 | +0.5 |
| db | 7.5 | 7.5 | 0.0 |
| test_coverage | 3.0 | 5.0 | +2.0 |
| repo_health | 5.0 | 6.0 | +1.0 |
| ux_ui | 6.0 | 6.5 | +0.5 |

Average improvement per area in round 1: +1.0. At this rate, 2 more rounds should reach 8.0 for most areas, but test_coverage and security need accelerated improvement.

## Completion Criteria

- All 7 scores >= 8.0 → `overall_status: completed`
- OR max_rounds (5) exhausted → `overall_status: max_rounds_reached`

## Instructions for the Improvement Agent

1. Read `improve-progress.yaml` to confirm the state matches this context.
2. Focus round 2 on TEST-001 and ARCH-001 (the two remaining P1 items).
3. Apply the learnings listed above during implementation.
4. After fixes, re-evaluate all 7 areas and update `improve-progress.yaml`.
5. If any new P0/P1 items are discovered during the round, add them to `items_remaining`.
6. Record new learnings for the next round.
7. Update `current_round` to 3 if target not yet met.
