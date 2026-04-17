## Priority Rules

Priority order on conflict (highest → lowest):

1. **NEVER rules** in this file (require explicit user confirmation to override)
2. **Project `CLAUDE.md`** (project root or subdirectories)
3. **This global `CLAUDE.md`**
4. **Superpowers skills** (e.g., `superpowers:test-driven-development`, `superpowers:brainstorming`, `superpowers:writing-plans`)
5. **Default system prompt behavior**

When Design-First Development (below) conflicts with `superpowers:writing-plans` or `superpowers:brainstorming`, this file wins — but the superpowers workflow may still be used *inside* the design doc process.

When Design-First Development combines with `superpowers:test-driven-development`, the order is: **design doc → tests → implementation**. Tests are written after the design doc is user-approved, then implementation follows TDD within the design doc's scope.

## NEVER Rules

These rules apply without exception. Violation handling depends on intent:

- **Implicit violation** — user request that would trigger a rule without explicitly asking to override (e.g., "git pull 해줘"): silently apply the safe variant (e.g., automatically add `--rebase`). No warning needed.
- **Explicit override** — user explicitly asks to bypass the rule ("이번엔 그냥 해", "`--no-verify` 써도 돼", etc.): print the warning below and proceed only after user confirms "yes".

```
⚠️ Warning: Attempting to override NEVER rule #N: "{rule}". This may cause {specific risk}. Continue? (yes/no)
```

1. NEVER run `git pull` without `--rebase`. Use `git pull --rebase` (defaults to current branch) or `git pull --rebase <remote> <branch>` with explicit args. Do not hardcode `origin main` — the branch and remote depend on project context.
2. NEVER `git push` without explicit user request. Applies to all push variants including `--force`, `--force-with-lease`, and amended-commit pushes.
3. NEVER call system `python`/`python3` directly in personal projects — use `uv run python`. For third-party projects with existing non-uv tooling (poetry, pipenv, conda, rye), follow the project's convention.
4. NEVER install Python packages with `pip install` in personal projects — use `uv add <pkg>` or `uv pip install <pkg>`. For third-party projects, follow the project's tooling.
5. NEVER write implementation code for new features or significant refactoring before a design doc is complete and user-approved. **"Significant" means**: 3+ files touched, new abstractions/modules, new public API surface, DB schema changes, or new external dependencies. **Exceptions** (design doc NOT required): bug fixes, typo/doc/config/dependency-bump changes, test additions, and single-concept changes under ~30 LOC.
6. NEVER commit new feature code without tests. **Exceptions**: documentation-only commits, config file changes, test-only commits, infrastructure scripts (shell/Dockerfile/CI), and projects that have no test framework configured (this limitation must be acknowledged in the project's own CLAUDE.md).
7. NEVER use a non-Mermaid diagram format without explicit user approval (Mermaid is the default).
8. NEVER place diagram files (Mermaid `.mmd` source and their rendered `.png`) outside `docs/`. Does not apply to other image assets — logos, screenshots, UI resources, and test fixtures have no location constraint.
9. NEVER use agent-browser when WebSearch/WebFetch suffices. Reserve agent-browser for login-gated pages, dynamic SPAs, and multi-step interactive flows.
10. NEVER design workflows where subagents call other subagents. Only the main model orchestrates; subagents are leaf nodes.
11. NEVER read or write `~/projects/wikis/` (the personal second-brain wiki) without having pulled in the current session. Run `git -C ~/projects/wikis pull --rebase` once at first wiki access per session. If the wiki has no configured upstream yet, the pull is a no-op and you may proceed. Prevents stale reads and merge conflicts across devices.

## Agent Orchestration

(See NEVER rule #10 for the subagent orchestration constraint.)

### Trigger Routing

- **Documentation request** → trigger `doc-loop`. When output is a document (design doc, API doc, README, prompt).
- **Plan request** → trigger `plan-loop`. When output is an execution plan (implementation plan, refactoring plan, migration strategy).
- If ambiguous, ask user: "Do you need a document or an execution plan?"
- **New app/service** → trigger `auto-dev`. For building a new app from scratch. Not for modifying existing code, bug fixes, or refactoring.
- **Improve existing app** → trigger `auto-improve`. For auditing and improving an already-existing codebase across code quality, security, architecture, tests, and UX. Not for new apps (→ `auto-dev`).
- **Skill creation/modification** → use `skill-creator` skill.
- **Agent creation/modification** → use `agent-create` skill.

### Security Agent Routing (ciso vs security-reviewer)

| Request type | Agent | Keywords |
|---|---|---|
| Policy, compliance, posture assessment, threat modeling, incident response, vendor security, privacy | **ciso** | policy, compliance, GDPR, PIPA, SOC 2, threat modeling, incident, posture, governance |
| Code vulnerability scanning, OWASP, dependency audit, PR/diff security review | **security-reviewer** | vulnerability, injection, XSS, CSRF, audit, code review, diff, dependency |

Quick rule: "Need to scan code?" → security-reviewer. "Policy/org-level assessment?" → ciso.

## Design-First Development

### Gate Rule

See NEVER rule #5 for the authoritative rule and exceptions. Summary: new features or significant refactoring require both:

1. LLM design doc at `{project}/docs/llm/{feature-or-topic}.md`
2. User review and approval

**Exceptions** (per NEVER #5, design doc NOT required): bug fixes, typo/doc/config/dependency-bump changes, test additions, and single-concept changes under ~30 LOC.

**auto-dev pipeline exception**: CTO agent (#25 Design gate) validates instead of human approval.

### Design Docs Are for LLMs

The primary reader is the implementing LLM. Write with precision, not narrative. Use imperative instructions ("do X", not "X should be done"). When using doc-loop, apply LLM mode (writer LLM Docs mode + LLM mode scoring). User approval confirms direction, not human readability.

### Design Doc Location

- LLM design docs: `{project}/docs/llm/{YYYY-MM-DD}-{feature-or-topic}.md` (date = doc creation date, not today's date when editing)
- Human docs (README etc.): `{project}/docs/{feature-or-topic}/`
- Before creating a new LLM design doc, glob `{project}/docs/llm/*-{feature-or-topic}.md` to find existing docs for the same topic (match by `{feature-or-topic}` suffix, ignore date prefix). If one exists, update that file in place — do not create a new date-prefixed file.

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

- Format: Mermaid `.mmd` by default. Other formats (PlantUML, excalidraw, ASCII) allowed only after explicit user approval.
- Render: `mmdc -i input.mmd -o output.png -b transparent -s 4`
- On mmdc failure: report error to user, provide `.mmd` file only. Do not halt work.
- Location: both `.mmd` and `.png` in the relevant `docs/` directory.

### Design Doc Reference During Implementation

- Read the design doc before starting implementation.
- Re-read the relevant section before each step. Do not rely on memory.
- If deviating from the design doc, update it first, then implement.

### Interaction with the Wiki

Before writing a new design doc, consult the Personal Wiki (see section below):

1. Check the relevant `wiki/Projects/<Name>/MAP.md` for existing philosophy, ADRs, and architectural context.
2. If the design makes a *strategic* decision (not just local implementation), create or update an ADR in `wiki/Projects/<Name>/Decisions/` or `wiki/Decisions/` *alongside* the design doc.
3. If existing wiki content conflicts with the proposed design, resolve in the wiki first — do not let the repo design doc silently contradict the wiki.

The wiki holds the "why" (evergreen); the repo design doc holds the "how and when" (execution-scoped).

## Personal Wiki (Second Brain)

Wiki location: `~/projects/wikis/` (git repo). Schema: `~/projects/wikis/SCHEMA.md`.

The wiki is the user's compounding second brain — strategic knowledge that outlives any specific codebase. Follows Andrej Karpathy's LLM Wiki pattern:

- `raw/` — immutable source material (Raw Sources)
- `wiki/` — AI-maintained interlinked markdown (The Wiki)
- `SCHEMA.md` — conventions and frontmatter rules (The Schema)

### When to READ

Before answering strategic or conceptual questions, consult the wiki first:

- Product direction, vision, long-term goals
- Architecture rationale, design decisions (ADRs)
- Operational philosophy, principles
- Roadmap, historical context ("why did we decide X?")

Entry points: `wiki/Index.md`, `wiki/Projects/<Name>/MAP.md`. Follow `[[WikiLinks]]`. Prefer the wiki over re-deriving answers from code when the question is about intent, not implementation.

### When to WRITE

Compound knowledge goes into the wiki. Three inbound paths:

1. **Raw Sources** — external material the user drops into `raw/<topic>/`. Summarize and weave into `wiki/` pages. Raw files stay immutable; the wiki is the derived layer.
2. **Codebase discovery** — when you find load-bearing concepts not yet in the wiki (non-obvious invariants, architectural patterns, cross-cutting design decisions), propose a wiki entry.
3. **Conversations** — when the user articulates a strategic decision, philosophy, or design rationale in dialogue, capture it as a wiki page or ADR before the context is lost. This is how conversations compound into persistent knowledge.

Do NOT write to the wiki for: code-level details, execution plans, session-level state (use TodoWrite or auto memory instead).

### Wiki vs. Auto Memory vs. Repo docs

| | Wiki | Auto Memory | Repo docs |
|---|---|---|---|
| **Scope** | Project compound knowledge | Agent-user interaction context | Code lock-step |
| **Persists** | Evergreen (git-versioned) | Cross-session | Versioned with code |
| **Reader** | Human + AI | AI | Human + AI |
| **Examples** | Philosophy, ADRs, vision, roadmap | User profile, feedback rules | `DEVELOPING.md`, `doc/plans/`, `docs/llm/` |
| **Rule of thumb** | Survives code rewrites → Wiki | Only matters for this user → Memory | Must change when code changes → Repo |

### Schema Conventions

Follow `~/projects/wikis/SCHEMA.md` exactly:

- YAML frontmatter required: `created`, `updated`, `type`, `status`, `project`
- `status` values: `seed` / `growing` / `evergreen` / `archived`
- Each project has `Overview.md`, `MAP.md`, `History.md`
- Decisions: `wiki/Decisions/` (global/cross-project) or `wiki/Projects/<Name>/Decisions/` (project-scoped)
- `[[WikiLinks]]` for cross-references
- Individual pages keep only 1–2 recent change bullets; full changelog in `History.md`
- Before creating a new page, read the relevant `MAP.md` and follow existing naming

### Multi-device Git Workflow

The wiki is a git repo shared across devices. Maintain discipline:

1. **First wiki access per session** — `git -C ~/projects/wikis pull --rebase` (NEVER rule #11).
2. **After every wiki write** — commit immediately: `git -C ~/projects/wikis commit -am "<type>(<project>): <summary>"`. Do not batch across multiple logical changes.
3. **At session end or meaningful completion** — ask the user "Wiki 푸시할까?" (NEVER rule #2 requires explicit push authorization).
4. **On rebase conflict** — STOP. Report to the user. Do NOT attempt auto-resolve. Wiki content is high-value and hard to reconstruct if merged wrong.

Commit message convention (Conventional Commits):

- `feat(<project>)`: new page or major section
- `docs(<project>)`: content refinement
- `chore(<project>)`: frontmatter updates, link fixes
- `adr(<project>)`: ADR-<id> decision records
- Scope `wiki` for cross-project or repo-level changes (e.g., `chore(wiki): update SCHEMA.md`)

## Testing

### Prerequisites

Before running Python tests, verify `uv` is installed (`which uv`). If not installed, inform the user and do not proceed with Python tasks.

### Test Execution

Run tests after each logical unit of change (not after every single edit — batch mechanically related edits). Discover the test command from project config (`package.json` scripts, `pyproject.toml`, `Makefile`, `go.mod`, `Cargo.toml`) instead of assuming. Python tests in personal projects must be invoked via `uv run` (NEVER rule #3); third-party projects follow their own tooling. If no test framework is configured, report to user and propose setup — acknowledge the gap in the project's CLAUDE.md but do not block work silently.

- New features: write both unit tests and integration tests.
- Unit tests: mock all external dependencies (API, DB, filesystem, network).
- Integration tests: do not mock inter-module calls. Only mock external I/O.

### Coverage

Target: 80%+. Check: `uv run python -m pytest --cov --cov-fail-under=80`

For inherited codebases below 80%: measure current coverage, identify top 3 lowest modules, propose a test plan, execute after user approval.

## Refactoring

### Abstraction Heuristics

These are heuristics against premature abstraction, not absolute rules. Follow them by default and deviate with justification.

Avoid abstraction when:
- Function is called from only 1 place → prefer inline. **Exception**: extraction measurably improves testability (isolates side-effect boundary) or readability of a long caller.
- Class has ≤ 2 methods → prefer functions. **Exception**: languages (Java, Kotlin, C#, Scala) where standalone functions are awkward or idiomatic code requires a type.
- Inheritance depth > 3 → prefer composition.
- Generic/type parameters > 3 → prefer concrete types. **Exception**: library code where polymorphism across those parameters is the primary value.

When unsure, ask the user before abstracting.

### Refactoring Procedure (strict order)

1. Verify existing tests exist (if not, write tests first and commit).
2. Ensure all changes are committed before starting.
3. Write refactoring plan and report to user.
4. Execute refactoring.
5. Run tests. Fix if any fail.

## Memory Extension

> **Scope note**: Auto memory is for agent-user interaction context. Project-level compound knowledge (philosophy, ADRs, architecture) goes in the Personal Wiki (see section above), not memory. Rule of thumb: if a different human teammate reading the project cold would benefit → Wiki; if it only helps calibrate your collaboration with this user → Memory.

### temp type

Additional memory type beyond system defaults (user, feedback, project, reference).

- **Purpose**: multi-session implementation decisions that must persist across sessions but are deleted when the implementation lands. Do NOT use for single-conversation state — use TodoWrite or plans for that. This type does NOT override the system prompt's "do not save ephemeral task details" rule; `temp` is strictly for decisions that outlive a conversation but have a known expiry.
- **Required fields**: `type: temp`, `expires_when: deletion condition`
- **MEMORY.md notation**: `[TEMP]` tag + expiry condition
- **Deletion**: when `expires_when` condition is met, delete the memory file and remove from MEMORY.md.

## Development Environment

### Python

- `uv` tooling scope and exceptions: see NEVER rules #3 and #4.
- Package install (personal projects): `uv add <pkg>` for project dependency, `uv pip install <pkg>` for one-off/global.
- If `uv` is not installed in a personal project: inform the user and do not proceed.

### CLI Tools

- **mmdc** (mermaid-cli): Mermaid `.mmd` → PNG. On failure, report error and provide `.mmd` only.
- **agent-browser**: Use only for login-required pages, dynamic SPAs, browser interaction. Do not use when WebSearch/WebFetch suffices. Commands: `agent-browser open <url>`, `snapshot`, `screenshot`, `click`, `fill`, `text`, `close`

## Design Systems (awesome-design-md)

`~/.claude/design-md/design-md/` 에 66개 브랜드 DESIGN.md 파일이 있음 (source: https://github.com/VoltAgent/awesome-design-md).

### 사용법

UI 작업 시 사용자가 특정 디자인 스타일을 요청하면:
1. `~/.claude/design-systems/<brand>/DESIGN.md` 파일을 Read로 읽어서 참고
2. 또는 프로젝트 루트에 복사: `cp ~/.claude/design-systems/<brand>/DESIGN.md ./DESIGN.md`

### 사용 가능한 브랜드 목록

`airbnb`, `airtable`, `apple`, `bmw`, `cal`, `claude`, `clay`, `clickhouse`, `cohere`, `coinbase`, `composio`, `cursor`, `elevenlabs`, `expo`, `ferrari`, `figma`, `framer`, `hashicorp`, `ibm`, `intercom`, `kraken`, `lamborghini`, `linear.app`, `lovable`, `minimax`, `mintlify`, `miro`, `mistral.ai`, `mongodb`, `notion`, `nvidia`, `ollama`, `opencode.ai`, `pinterest`, `posthog`, `raycast`, `renault`, `replicate`, `resend`, `revolut`, `runwayml`, `sanity`, `semrush`, `sentry`, `spacex`, `spotify`, `stripe`, `supabase`, `superhuman`, `tesla`, `together.ai`, `uber`, `vercel`, `voltagent`, `warp`, `webflow`, `wise`, `x.ai`, `zapier`

업데이트: `git -C ~/.claude/design-md pull --rebase`
