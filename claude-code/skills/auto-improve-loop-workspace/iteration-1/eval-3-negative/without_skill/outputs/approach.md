# Approach: "이 서비스 좀 개선해줘" for /tmp/mock-webapp

## What I Would Do (DRY RUN)

### Step 1: Understand the codebase

Scan the entire `/tmp/mock-webapp` directory to understand the tech stack, project structure, entry points, dependencies, and existing tests. Read key files like `package.json`, `requirements.txt`, `pyproject.toml`, main application entry point, config files, and any existing documentation.

### Step 2: Identify improvement areas

Based on the codebase scan, compile a list of concrete issues across these dimensions:
- Code quality: dead code, inconsistent naming, missing type hints, overly complex functions
- Security: injection vulnerabilities, hardcoded secrets, missing input validation
- Architecture: circular dependencies, tight coupling, missing abstractions where warranted
- Test coverage: untested critical paths, missing integration tests
- Repo health: missing linting config, no CI setup, outdated dependencies
- UX/UI: if frontend exists, accessibility issues, inconsistent error handling

### Step 3: Prioritize and present to user

Sort issues by severity (P0 security/data-loss risks first, then P1 architectural issues, then P2 quality improvements). Present the full list to the user and ask which items to address, or propose a reasonable batch.

### Step 4: Design-first for significant changes

Per the project's CLAUDE.md rules, write a design document in `docs/llm/` before implementing any non-trivial change. Get user approval.

### Step 5: Implement, test, commit

For each approved improvement: implement the fix, write/update tests, run the test suite, and commit with a clear message.

## Would I Set Up a Loop?

**No. My natural approach is a one-time improvement pass, not a loop.**

Here is what I would actually do:

1. Audit the codebase once, producing a prioritized list of issues.
2. Present the list to the user for approval.
3. Implement the approved fixes in priority order, one at a time.
4. After each fix, run tests to verify nothing broke.
5. Once the agreed-upon fixes are done, report the results and stop.

I would not:
- Create a scoring system or grade the codebase numerically.
- Set up an iterative loop that re-evaluates and discovers new issues after each round.
- Track progress in a YAML file across multiple rounds.
- Define a target score and keep looping until all dimensions reach it.
- Automatically decide on the next round of improvements without user input.

The request "이 서비스 좀 개선해줘" (improve this service) is open-ended, so I would ask the user what specific areas they care about most, then do a single focused pass. If the user later says "more improvements," I would do another single pass. There is no autonomous loop mechanism in my default behavior.

## What's Missing Without a Loop

The existing `improve-progress.yaml` in this project shows a structured multi-round improvement process with:
- Baseline scoring across 7 dimensions
- A target score (8.0) driving iteration
- Round-by-round tracking with items addressed vs. remaining
- Accumulated learnings carried forward between rounds
- Automatic continuation until all scores meet the target

Without an explicit skill or instruction to follow this pattern, I would not spontaneously create such a loop. Each improvement session would be independent, with no persistent tracking of progress across sessions and no automated re-evaluation cycle.
