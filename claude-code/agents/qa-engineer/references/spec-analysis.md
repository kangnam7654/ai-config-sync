# Spec Analysis — Design Document to Test Plan

This reference file contains the complete spec analysis workflow, extraction rules, output format, and edge case handling. Read this file when qa-engineer enters Spec Analysis mode.

## 6-Step Workflow

### Step 1: Locate and read the design document

Read the design document at the provided path. If no path is provided, search `docs/` directories using Glob for `**/docs/**/*.md` and ask the user which document to analyze.

**Output**: List the sections found and confirm which of the 6 required sections are present (Purpose, Architecture, Data Flow, API Design, File Structure, Decision Rationale).

### Step 2: Parse each section for testable requirements

Extract testable requirements using these rules:

| Section | What to extract |
|---------|----------------|
| Purpose | Success criteria → each criterion becomes >= 1 test case |
| Architecture | Component interfaces → test each interface boundary (data in, data out) |
| Data Flow | Each step in input→processing→output chain → test each transition |
| API Design | Each endpoint/function → valid input, invalid input, edge cases, error codes |
| File Structure | File creation/modification targets → verify files are created/modified after operations |
| Decision Rationale | Rejected alternatives → test that rejected behavior does NOT occur |

**Output**: Categorized list of raw testable requirements, grouped by source section.

### Step 3: Cross-reference against the codebase

For each extracted requirement, verify implementation status using Grep and Glob:

- `Implemented` — code exists and matches the design doc description
- `Partially Implemented` — code exists but differs (note the difference)
- `Not Yet Implemented` — no matching code found

**Output**: Each requirement annotated with implementation status and the file/line where found (or "not found").

### Step 4: Generate test cases

Transform each requirement into a structured test case:

1. Scenario name: `{action}_{condition}_{expected_result}` (e.g., `create_user_with_duplicate_email_returns_409`)
2. Classify type:
   - `unit` — single function in isolation, all external deps mocked
   - `integration` — 2+ internal modules or module against external I/O
   - `e2e` — complete user journey through the running application
3. Assign priority:
   - **P0** — failure causes data loss, security breach, payment error, or service outage
   - **P1** — failure breaks a core user flow (login, main feature, CRUD operations)
   - **P2** — failure affects non-critical features (UI polish, secondary flows, admin-only)
4. Specify concrete inputs and expected results — no vague descriptions

**Output**: Complete list of structured test cases in the table format below.

### Step 5: Identify coverage gaps

Compare test cases against the design doc:

1. Requirements mentioned but not covered by any test case
2. Error paths implied by the architecture but not described in the design doc
3. Security-sensitive operations lacking dedicated test cases
4. Boundary conditions (empty inputs, maximum sizes, concurrent access) not covered

**Output**: Numbered list of gaps with recommendations for additional test cases.

### Step 6: Compile and save the Test Plan

Assemble all results into the output format below. Save to `docs/{feature}/test-plan.md`.

**Output**: The complete Test Plan file, saved to disk.

## Output Format

```markdown
# Test Plan: {Feature Name}

**Source**: `{design document path}`
**Generated**: {YYYY-MM-DD}
**Implementation Status**: {X of Y requirements implemented}

## Summary

| Type | Count | P0 | P1 | P2 |
|------|-------|----|----|----|
| Unit | {N} | {N} | {N} | {N} |
| Integration | {N} | {N} | {N} | {N} |
| E2E | {N} | {N} | {N} | {N} |
| **Total** | **{N}** | **{N}** | **{N}** | **{N}** |

## Test Cases

### {Section Name from Design Doc}

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 1 | {action_condition_result} | unit | P0 | {concrete input} | {concrete expected output} | Implemented |
| 2 | {action_condition_result} | integration | P1 | {concrete input} | {concrete expected output} | Not Yet Implemented |

{Repeat for each section}

## Gaps

| # | Gap Description | Recommendation | Suggested Type | Suggested Priority |
|---|----------------|----------------|---------------|-------------------|
| 1 | {what is missing} | {what test to add} | {unit/integration/e2e} | {P0/P1/P2} |

## Cross-Reference

| Design Doc Section | Requirements Found | Test Cases Generated | Coverage |
|-------------------|-------------------|---------------------|----------|
| Purpose | {N} | {N} | {N/N = X%} |
| Architecture | {N} | {N} | {N/N = X%} |
| Data Flow | {N} | {N} | {N/N = X%} |
| API Design | {N} | {N} | {N/N = X%} |
| File Structure | {N} | {N} | {N/N = X%} |
| Decision Rationale | {N} | {N} | {N/N = X%} |
```

## Edge Cases

| Situation | Resolution |
|-----------|------------|
| Design doc is missing required sections | Report which sections are missing. Extract from available sections. Add gap entry: "Section {name} missing — cannot generate test cases for this area." |
| Design doc references external APIs | Generate integration test cases with mock note: "Requires mock for {service name}." |
| No success criteria in Purpose section | Flag as gap. Derive implicit criteria from other sections. |
| Contradictions between sections | Flag each contradiction in Gaps. Do not generate test cases for contradictory requirements — ask user to resolve. |
| Mermaid diagrams in architecture | Parse diagram text for component names and relationships. Generate interface boundary tests for each connection. |
| Security requirements mentioned | Generate P0 test cases + explicit negative tests: unauthorized access, invalid tokens, injection inputs. |
| Database schema (ERD) present | Generate tests for: CRUD per entity, referential integrity, index performance, migration up/down. |
| Multiple design docs for same feature | Read all. Merge requirements, deduplicate test cases, note which doc each requirement came from. |
| Feature is fully implemented | Set all test cases to "Implemented". Recommend running the test plan to verify implementation matches spec. |
| Zero implementation exists | Set all to "Not Yet Implemented". The test plan serves as a pre-implementation blueprint. |

## Rules Specific to Spec Analysis

### ALWAYS
- Read the full design document before extracting any test cases
- Verify referenced files and functions exist in the codebase using Grep/Glob
- Produce >= 1 test case per section that contains functional requirements
- Include both happy-path and error-path test cases for every API endpoint or data flow
- Assign each test case exactly one type (unit/integration/e2e) and one priority (P0/P1/P2)

### NEVER
- Write test code — output test case specifications only
- Skip the codebase cross-reference step
- Assign all test cases the same priority
- Produce duplicate test cases across sections
- Produce fewer than 5 test cases for a design doc with 3+ sections containing functional content
