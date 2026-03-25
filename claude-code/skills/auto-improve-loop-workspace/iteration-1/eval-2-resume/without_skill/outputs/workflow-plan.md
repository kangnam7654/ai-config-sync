# Workflow Plan: Resume auto-improve-loop from Round 2

## Current State (from improve-progress.yaml)

- **Round 1**: Completed (2026-03-24T14:00:00)
- **Current round**: 2 (status: in_progress, interrupted before any work was recorded)
- **Target score**: 8.0 across all areas
- **Max rounds**: 5 (3 remaining after round 1)
- **Remaining P0/P1 items**: 2
  - ARCH-001: Circular dependency in core modules (architecture, P1)
  - TEST-001: No integration tests for payment flow (test, P1)

### Latest Scores (post-round 1)

| Area | Score | Gap to 8.0 |
|------|-------|------------|
| code_quality | 6.5 | -1.5 |
| security | 6.0 | -2.0 |
| architecture | 6.5 | -1.5 |
| db | 7.5 | -0.5 |
| test_coverage | 5.0 | -3.0 |
| repo_health | 6.0 | -2.0 |
| ux_ui | 6.5 | -1.5 |

### Round 1 Learnings

- payment 모듈 테스트 시 mock DB 필요
- user search API 시그니처가 변경됨

---

## Step-by-Step Resume Plan

### Step 1: Validate Round 1 Completion

Since round 2 was marked `in_progress` but no round 2 entry exists in the `rounds` list, the interruption happened before any round 2 work was committed. This means:
- No partial changes from round 2 need to be rolled back.
- Round 1's final_scores are the current baseline for round 2.

**Action**: Verify the codebase matches round 1's final state by checking git log for the last successful commit. If there are uncommitted changes from a partial round 2, stash or discard them after user confirmation.

### Step 2: Prioritize Items for Round 2

Based on the gap analysis (largest gaps first) and remaining P1 items:

1. **test_coverage (5.0, gap: -3.0)** — Largest gap. Address TEST-001 (payment flow integration tests) plus add unit tests for undertested modules.
2. **security (6.0, gap: -2.0)** — No specific remaining item tagged, but score is low. Audit for additional vulnerabilities beyond the fixed SQL injection.
3. **repo_health (6.0, gap: -2.0)** — Add linting config, CI checks, documentation improvements.
4. **architecture (6.5, gap: -1.5)** — Address ARCH-001 (circular dependency in core modules).

**Round 2 focus**: test_coverage and architecture (the two remaining P1 items) because:
- They have explicit, actionable items (TEST-001, ARCH-001).
- test_coverage has the largest gap (-3.0).
- Fixing ARCH-001 may also improve code_quality score.

### Step 3: Execute Round 2 Improvements

#### 3a. Fix ARCH-001 — Circular dependency in core modules

1. Read the project source to identify the circular import chain.
2. Map the dependency graph of core modules.
3. Apply one of: dependency inversion, extract shared interface module, or lazy imports.
4. Verify no circular imports remain (e.g., `uv run python -c "import core_module"` for each).
5. Run existing tests to confirm no regressions.

#### 3b. Fix TEST-001 — Integration tests for payment flow

1. Read the payment module code to understand the flow (endpoints, DB interactions, external API calls).
2. Apply round 1 learning: set up mock DB fixture for payment tests.
3. Apply round 1 learning: use the updated user search API signature (changed in round 1).
4. Write integration tests covering: successful payment, payment failure, refund, edge cases (duplicate payment, timeout).
5. Mock only external I/O (payment gateway API, DB), not inter-module calls (per testing rules).
6. Run tests and verify coverage increase.

#### 3c. Additional test coverage improvements

1. Run coverage report (`uv run python -m pytest --cov`) to identify lowest-covered modules.
2. Add unit tests for the top 3 least-covered modules.
3. Target: raise test_coverage score from 5.0 toward 7.0+.

#### 3d. Security hardening (if time permits within round scope)

1. Scan for common vulnerabilities: XSS, CSRF, insecure deserialization, hardcoded secrets.
2. Fix any P0/P1 findings.
3. Add input validation where missing.

### Step 4: Run Full Evaluation

After all round 2 changes:
1. Run the full test suite: `uv run python -m pytest tests/ -q`
2. Run coverage: `uv run python -m pytest --cov --cov-fail-under=80`
3. Re-score all 7 areas using the same rubric as round 1.
4. Compare new scores against latest_scores to measure improvement.

### Step 5: Update improve-progress.yaml

Add a round 2 entry to the `rounds` list with:
- `round: 2`
- `timestamp`: current time
- `status: completed`
- `baseline_scores`: copy of round 1's final_scores
- `final_scores`: new scores from step 4
- `items_addressed`: list of items fixed (ARCH-001, TEST-001, plus any new items)
- `items_remaining`: any P1+ items still unresolved
- `learnings`: new learnings from round 2

Update top-level fields:
- `current_round`: 3 (or keep at 2 if target met)
- `overall_status`: `completed` if all scores >= 8.0, otherwise `in_progress`
- `latest_scores`: new scores
- `remaining_p0_p1`: updated count
- `all_scores_above_target`: true/false

### Step 6: Decide Whether to Continue

- If `all_scores_above_target` is true: mark `overall_status: completed`, stop.
- If not and `current_round` <= `max_rounds` (5): proceed to round 3 with the same loop.
- If `current_round` > `max_rounds`: mark `overall_status: max_rounds_reached`, report final state to user.

---

## How Previous Round's Data Is Used

| Data from Round 1 | How It's Used in Round 2 |
|---|---|
| `final_scores` | Becomes round 2's `baseline_scores`; used to calculate gap-to-target and prioritize work areas |
| `items_remaining` (ARCH-001, TEST-001) | Direct work items for round 2 — these are addressed first |
| `items_addressed` (SEC-001) | Skipped — already fixed, no rework needed |
| `learnings` (mock DB, API sig change) | Applied during implementation: mock DB setup for payment tests, updated API signature in test assertions |
| `latest_scores` | Used to verify which areas are still below target (all except db at 7.5) |
| `remaining_p0_p1: 2` | Confirms there are exactly 2 must-fix items; no new P0s were introduced |
