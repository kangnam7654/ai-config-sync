## Priority Rules

Project `CLAUDE.md` (in project root or subdirectories) overrides this global `CLAUDE.md` on conflict. Exception: NEVER rules cannot be overridden by project CLAUDE.md — explicit user confirmation is required.

## NEVER Rules

These rules apply without exception. If the user asks to override, print the warning below and proceed only after user confirms "yes":

```
⚠️ Warning: Attempting to override NEVER rule #N: "{rule}". This may cause {specific risk}. Continue? (yes/no)
```

1. NEVER run `git pull` without `--rebase`. Always use `git pull --rebase origin main`.
2. NEVER `git push` in projects with no remote.
3. NEVER call system `python`/`python3` directly. Always use `uv run python`.
4. NEVER run `pip install` directly. Use `uv add <pkg>` or `uv pip install <pkg>`.
5. NEVER write implementation code before design doc is complete + user-approved.
6. NEVER commit code without tests.
7. NEVER use diagram formats other than Mermaid.
8. NEVER place `.mmd` or diagram `.png` files outside `docs/`.
9. NEVER use agent-browser when WebSearch/WebFetch suffices.
10. NEVER let subagents call other subagents directly. Only the main model orchestrates.

## Agent Orchestration

Subagents cannot call other subagents. The main model orchestrates all loops.

### Trigger Routing

- **Documentation request** → trigger `doc-loop`. When output is a document (design doc, API doc, README, prompt).
- **Plan request** → trigger `plan-loop`. When output is an execution plan (implementation plan, refactoring plan, migration strategy).
- If ambiguous, ask user: "Do you need a document or an execution plan?"
- **New app/service** → trigger `auto-dev`. For building a new app from scratch. Not for modifying existing code, bug fixes, or refactoring.
- **Skill creation/modification** → follow `skill-create` workflow.
- **Agent creation/modification** → follow `agent-create` workflow.

### Security Agent Routing (ciso vs security-reviewer)

| Request type | Agent | Keywords |
|---|---|---|
| Policy, compliance, posture assessment, threat modeling, incident response, vendor security, privacy | **ciso** | policy, compliance, GDPR, PIPA, SOC 2, threat modeling, incident, posture, governance |
| Code vulnerability scanning, OWASP, dependency audit, PR/diff security review | **security-reviewer** | vulnerability, injection, XSS, CSRF, audit, code review, diff, dependency |

Quick rule: "Need to scan code?" → security-reviewer. "Policy/org-level assessment?" → ciso.

## Design-First Development

### Gate Rule

Implementation code is allowed only after both conditions are met:
1. LLM design doc exists at `{project}/docs/llm/{feature-or-topic}.md`
2. User has reviewed and approved the design doc

**Exception: auto-dev pipeline** — CTO agent (#25 Design gate) validates instead of human approval.

### Design Docs Are for LLMs

The primary reader is the implementing LLM. Write with precision, not narrative. Use imperative instructions ("do X", not "X should be done"). When using doc-loop, apply LLM mode (doc-writer-llm + LLM mode scoring). User approval confirms direction, not human readability.

### Design Doc Location

- LLM design docs: `{project}/docs/llm/{feature-or-topic}.md`
- Human docs (README etc.): `{project}/docs/{feature-or-topic}/`
- If a design doc for the same topic exists, update it instead of creating a new file.

### Required Design Doc Sections

| Section | Minimum requirement |
|---------|-------------------|
| Purpose | 1-sentence problem statement + verifiable completion criteria |
| File changes | Full paths of files to create/modify + change summary per file |
| Implementation order | Numbered steps with target file and function names |
| Function/API signatures | Exact signatures + parameter types + return types |
| Constraints | Rules to follow (naming, error handling, consistency with existing code) |
| Decisions | 1 line for chosen approach + 1 line for rejected alternatives with reasons |

### DB Schema (only for projects requiring a DB)

Write DB schema first when a design doc requires a DB. Include: ERD (Mermaid erDiagram), table definitions, relationships, indexes.

### Diagram Rules

- Format: Mermaid `.mmd` files only.
- Render: `mmdc -i input.mmd -o output.png -b transparent -s 4`
- On mmdc failure: report error to user, provide `.mmd` file only. Do not halt work.
- Location: both `.mmd` and `.png` in the relevant `docs/` directory.

### Design Doc Reference During Implementation

- Read the design doc before starting implementation.
- Re-read the relevant section before each step. Do not rely on memory.
- If deviating from the design doc, update it first, then implement.

## Testing

### Prerequisites

Before running Python tests, verify `uv` is installed (`which uv`). If not installed, inform the user and do not proceed with Python tasks.

### Test Execution

Run tests after every code change. Language-specific commands:

| Language | Command | Prerequisite |
|----------|---------|-------------|
| Python | `uv run python -m pytest tests/ -q` | `uv` installed |
| Node.js | `npm test` | test script in `package.json` |
| Go | `go test ./...` | `go.mod` exists |
| Rust | `cargo test` | `Cargo.toml` exists |

If no test framework is configured, do not skip tests. Report to user and suggest setup first.

- New features: write both unit tests and integration tests.
- Unit tests: mock all external dependencies (API, DB, filesystem, network).
- Integration tests: do not mock inter-module calls. Only mock external I/O.

### Coverage

Target: 80%+. Check: `uv run python -m pytest --cov --cov-fail-under=80`

For inherited codebases below 80%: measure current coverage, identify top 3 lowest modules, propose a test plan, execute after user approval.

## Refactoring

### Abstraction Rules

Do NOT abstract when:
- Function is called from only 1 place → do not extract to a separate module.
- Class has ≤ 2 methods → use functions instead.
- Inheritance depth > 3 → use composition.
- Generic/type parameters > 3 → use concrete types.

### Refactoring Procedure (strict order)

1. Verify existing tests exist (if not, write tests first and commit).
2. Ensure all changes are committed before starting.
3. Write refactoring plan and report to user.
4. Execute refactoring.
5. Run tests. Fix if any fail.

## Memory Extension

### temp type

Additional memory type beyond system defaults (user, feedback, project, reference).

- **Purpose**: temporary decisions to delete when a specific implementation is complete.
- **Required fields**: `type: temp`, `expires_when: deletion condition`
- **MEMORY.md notation**: `[TEMP]` tag + expiry condition
- **Deletion**: when `expires_when` condition is met, delete the memory file and remove from MEMORY.md.

## Development Environment

### Python

- Never call system `python`/`python3`. Always use `uv run python`.
- Package install: `uv add <pkg>` (project dependency) or `uv pip install <pkg>` (one-off).
- If `uv` is not installed, do not proceed with Python tasks.

### CLI Tools

- **mmdc** (mermaid-cli): Mermaid `.mmd` → PNG. On failure, report error and provide `.mmd` only.
- **agent-browser** (v0.10.0): Use only for login-required pages, dynamic SPAs, browser interaction. Do not use when WebSearch/WebFetch suffices. Commands: `agent-browser open <url>`, `snapshot`, `screenshot`, `click`, `fill`, `text`, `close`
