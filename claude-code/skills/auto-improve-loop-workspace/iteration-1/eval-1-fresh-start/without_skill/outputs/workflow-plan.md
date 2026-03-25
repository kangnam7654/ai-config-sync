# Workflow Plan: Iterative Code Quality Improvement (Without Skill)

## Task Summary

- **Project**: `/tmp/mock-webapp`
- **Goal**: Raise all code quality scores to 8.0 or above
- **Max Rounds**: 3 (user-specified, overrides the 5 in existing progress file)
- **Current State**: Round 1 completed; Round 2 in progress. Latest scores range from 5.0 to 7.5 — all below target except `db` (7.5, still below 8.0).

---

## High-Level Approach

This is an **iterative improvement loop** with three phases per round: **Assess -> Fix -> Verify**. The loop continues until either (a) all scores reach 8.0+ or (b) 3 rounds are exhausted.

---

## Step-by-Step Workflow

### Phase 0: Session Initialization (One-time)

1. Run `git status` in `/tmp/mock-webapp` to check for uncommitted changes.
2. Run `git pull --rebase origin main` (or skip if no remote).
3. Read the existing progress file at `docs/llm/improve-progress.yaml` to understand current state.
4. Identify the project's tech stack by scanning file extensions, `package.json`, `requirements.txt`, `Cargo.toml`, etc.
5. Read all source files to build a mental model of the codebase.

### Phase 1: Assessment (Each Round)

For each round, evaluate the codebase across 7 dimensions and assign scores (1-10 scale):

| Dimension | What to Evaluate |
|-----------|-----------------|
| **code_quality** | Naming conventions, function length, cyclomatic complexity, DRY violations, dead code, consistent formatting |
| **security** | SQL injection, XSS, hardcoded secrets, input validation, auth/authz flaws, dependency vulnerabilities |
| **architecture** | Separation of concerns, circular dependencies, layering violations, proper abstraction levels |
| **db** | Schema design, indexing, N+1 queries, migration hygiene, connection pooling |
| **test_coverage** | % coverage, critical path coverage, test quality (not just existence), edge cases |
| **repo_health** | `.gitignore`, CI config, linting config, dependency management, README, commit hygiene |
| **ux_ui** | Accessibility (a11y), responsive design, error messages, loading states, consistent styling |

**Assessment Method:**
- Use `Grep` and `Read` tools to scan for known anti-patterns per dimension.
- For security: search for `eval(`, raw SQL string concatenation, hardcoded passwords/keys, missing CSRF tokens.
- For code_quality: check function lengths, file sizes, duplication patterns.
- For test_coverage: measure actual coverage if test framework exists; otherwise count test files vs source files.
- For architecture: trace import/require graphs for circular dependencies.
- For repo_health: check for `.gitignore`, linter configs, CI files, `package-lock.json`/`uv.lock`.

**Scoring Rules:**
- Each dimension scored 1-10 based on concrete findings (not gut feeling).
- Score criteria are anchored: 5 = "functional but many issues", 8 = "production-ready with minor issues", 10 = "exemplary".
- Document specific findings that justify each score (file path + line number + description).

### Phase 2: Prioritize and Fix (Each Round)

1. **Identify all issues** found during assessment. Tag each with:
   - `id`: `{AREA}-{NNN}` (e.g., `SEC-002`)
   - `area`: one of the 7 dimensions
   - `priority`: P0 (critical/blocking), P1 (important), P2 (nice-to-have)
   - `estimated_impact`: how many score points this fix would contribute

2. **Sort by priority**, then by estimated impact (descending). Within a round:
   - Fix ALL P0 items first.
   - Then fix P1 items, highest impact first.
   - Skip P2 items unless time/budget permits.

3. **Execute fixes** following these rules:
   - Read the target file with `Read` before editing.
   - Use `Edit` for surgical changes; `Write` only for new files.
   - For each fix, verify it doesn't break existing functionality:
     - Run the project's test suite (if it exists).
     - If no test suite, run a syntax/lint check.
   - If adding tests (for `test_coverage` dimension), use the project's existing test framework.

4. **Track fixes** in the progress YAML file after each item is addressed.

### Phase 3: Re-Evaluate (Each Round)

1. Re-run the same assessment from Phase 1.
2. Record new scores in the progress YAML.
3. **Stop condition check**:
   - If ALL 7 scores >= 8.0 --> STOP, report success.
   - If round_number >= 3 (max_rounds) --> STOP, report final state.
   - Otherwise --> increment round, go to Phase 1.

---

## Detailed Round Plan

### Round 1 (Already Completed)

According to the existing progress file, Round 1 already ran and produced these scores:
- code_quality: 6.5, security: 6.0, architecture: 6.5, db: 7.5, test_coverage: 5.0, repo_health: 6.0, ux_ui: 6.5
- Gap to target: all dimensions still below 8.0.

### Round 2 (Current — Would Execute)

**Priority Focus** (dimensions furthest from target):
1. `test_coverage` (5.0 -> need +3.0) — highest gap
2. `security` (6.0 -> need +2.0)
3. `repo_health` (6.0 -> need +2.0)
4. `code_quality` (6.5 -> need +1.5)
5. `architecture` (6.5 -> need +1.5)
6. `ux_ui` (6.5 -> need +1.5)
7. `db` (7.5 -> need +0.5) — lowest gap

**Known remaining items from Round 1:**
- `ARCH-001`: Circular dependency in core modules (P1)
- `TEST-001`: No integration tests for payment flow (P1)

**Expected actions:**
- Add integration tests for payment flow (addresses TEST-001).
- Break circular dependency (addresses ARCH-001).
- Add linter config + CI pipeline config (addresses repo_health).
- Add input validation middleware (addresses security).
- Refactor long functions, extract duplicated code (addresses code_quality).
- Add loading states and error boundaries (addresses ux_ui).
- Add missing DB indexes (addresses db).

### Round 3 (If Needed)

- Address any remaining gaps from Round 2 re-assessment.
- Focus on dimensions still below 8.0.
- This is the FINAL round per user constraint.

---

## State Tracking

### Progress File: `docs/llm/improve-progress.yaml`

Updated at the end of each round with:
```yaml
rounds:
  - round: N
    timestamp: ISO-8601
    status: completed | in_progress | skipped
    baseline_scores: {7 dimensions}
    final_scores: {7 dimensions}
    items_addressed: [{id, title, area, priority}]
    items_remaining: [{id, title, area, priority}]
    learnings: |
      - bullet points of lessons learned

current_round: N
overall_status: in_progress | target_reached | max_rounds_exhausted
latest_scores: {7 dimensions}
remaining_p0_p1: count
all_scores_above_target: true | false
```

### Per-Round Tracking

Within each round, I would maintain mental state of:
- Issues found (with IDs)
- Issues fixed (with verification)
- Issues deferred (with reason)

This is persisted in the YAML file's `items_addressed` and `items_remaining` arrays.

---

## Stop Conditions

| Condition | Action |
|-----------|--------|
| All 7 scores >= 8.0 | Stop. Set `overall_status: target_reached`. Report success. |
| Round counter reaches 3 | Stop. Set `overall_status: max_rounds_exhausted`. Report final scores and remaining gaps. |
| No improvement between rounds (all scores unchanged) | Stop early. Report stagnation — further improvement may require architectural changes beyond automated fixing. |
| Critical error (project won't build/run) | Stop. Roll back last change. Report the error. |

---

## What I Would NOT Do

1. **No design document required** — this is iterative improvement of existing code, not new feature development. The CLAUDE.md Design-First rule applies to new implementation, not refactoring.
2. **No new files unless necessary** — prefer editing existing files. Only create new files for tests, configs, or missing infrastructure.
3. **No architectural rewrites** — stay within the existing structure. Refactor, don't rewrite.
4. **No modifications outside project directory** — all changes within `/tmp/mock-webapp`.

---

## Challenges Without a Dedicated Skill

Without an `auto-improve-loop` skill, the following challenges apply:

1. **No automated scoring tool** — I must manually assess each dimension by reading code and searching for patterns. This is subjective and time-consuming.
2. **No structured loop control** — I must manually track round numbers, check stop conditions, and manage state transitions. Risk of losing context across long conversations.
3. **No standardized issue catalog** — I must build the issue list from scratch each round rather than having a predefined checklist of anti-patterns per dimension.
4. **No parallelization** — assessment of different dimensions happens sequentially in my reasoning, whereas a skill could dispatch sub-assessments in parallel.
5. **No scoring calibration** — without predefined rubrics, scores may drift between rounds (e.g., I might score "security: 7" in Round 2 more leniently than in Round 1).
6. **No diff-based re-assessment** — without tooling, re-assessment requires re-reading the entire codebase rather than only checking changed files.

---

## Estimated Effort

| Phase | Estimated Tool Calls | Notes |
|-------|---------------------|-------|
| Session init | 3-5 | git status, pull, read progress file, scan file tree |
| Assessment (per round) | 15-30 | Read files, grep for patterns across 7 dimensions |
| Fix (per round) | 10-40 | Depends on number of issues; each fix = read + edit + verify |
| Re-evaluate (per round) | 10-20 | Subset of assessment focusing on changed areas |
| **Total for 2 remaining rounds** | **50-190** | Wide range due to codebase size uncertainty |
