---
name: token-optimize
description: "Measure and reduce token consumption in Claude Code system prompts. Use when the user mentions token optimization, context budget, prompt size reduction, or wants to check how many tokens their agents/skills/CLAUDE.md consume. Triggers on: 'token optimize', 'reduce tokens', 'system prompt too big', 'context budget', 'how many tokens', 'optimize tokens', 'token usage'."
---

# token-optimize

Measures and reduces tokens consumed by agent descriptions, skill descriptions, CLAUDE.md files, and memory files that load into every Claude Code conversation.

## Why this matters

Every conversation starts with a fixed token budget consumed by system prompt contents. Agent descriptions, skill descriptions, CLAUDE.md, and MEMORY.md all load unconditionally. Reducing these frees context for actual work. Korean text costs 2-4x more tokens than equivalent English for the same semantic content.

## Workflow

### Phase 1: Measure

Always run measurement first. Use the bundled script:

```bash
# Project only (default)
uv run python <skill-dir>/scripts/measure.py --project-dir <project-root>

# Project + global
uv run python <skill-dir>/scripts/measure.py --project-dir <project-root> --global

# JSON output for programmatic use
uv run python <skill-dir>/scripts/measure.py --project-dir <project-root> --global --json
```

Replace `<skill-dir>` with this skill's directory path and `<project-root>` with the current project's root directory.

Present the report to the user as a markdown table. Highlight the biggest optimization opportunities.

### Phase 2: Optimize

After showing the measurement report, propose specific optimizations and get user approval before making changes.

#### Scope rules

- **No flag (default)**: only optimize project CLAUDE.md and project memory/
- **`--global` flag**: also optimize agent descriptions, skill descriptions, global CLAUDE.md

If the user says just "optimize tokens" without specifying scope, default to project. Ask "Include global (agents, skills, global CLAUDE.md) too?" before touching global files.

#### Optimization techniques (in priority order)

**1. Korean → English conversion (highest impact, ~60% reduction per item)**

Korean text consumes 2-4x more tokens than English for the same meaning. Convert Korean descriptions and CLAUDE.md content to concise English.

Rules:
- Preserve all routing hints (e.g., "Code scanning → security-reviewer")
- Keep category tags (e.g., [Review], [Dev], [Design])
- Maintain the same semantic meaning — do not add or remove information
- Agent descriptions: keep to 1-2 sentences max
- CLAUDE.md: preserve all rules and constraints, just translate

**2. Description compression (agents only)**

Remove Examples and NOT-this-agent sections from agent description frontmatter. These sections typically account for 60-70% of description length. The routing information they contain should be condensed into brief phrases (e.g., "Deep security → security-reviewer").

Before:
```
"[Review] CISO — handles security governance...

Examples:
- \"보안 점검해줘\" → Launch ciso
- \"GDPR 확인\" → Launch ciso

NOT this agent:
- Code scanning → security-reviewer
- Strategy → cso"
```

After:
```
"[Review] Organizational security governance — policy, compliance, posture, threat modeling. Code scanning → security-reviewer."
```

**3. Duplicate detection (recommend only)**

Identify skills that overlap with agent capabilities (e.g., a db-advisor skill when a dba agent exists). Report duplicates to the user but do NOT delete automatically — let the user decide.

**4. Memory cleanup (project scope)**

Identify issues in project memory/:
- Non-memory files (templates, configs) that belong in skill directories
- Stale memories with expired `expires_when` conditions
- Report issues but do NOT delete — let the user decide

#### Change protocol

For every proposed change:
1. Show the current value and proposed new value
2. Show estimated token savings
3. Wait for user approval before applying
4. After all changes, re-run measurement and show before/after comparison

For batch changes (e.g., 15 agent descriptions), group them and show a summary table instead of individual diffs:

```
Agent description compression (13 items):
  ciso:      903 → ~40 tokens
  code-reviewer: 235 → ~40 tokens
  ...
  Total: 2,872 → ~415 tokens (saved ~2,457)
Proceed? (yes/no)
```

### Phase 3: Report

After optimization, present a summary:

```
Token Optimization Report
═══════════════════════════
Category              Before    After   Saved
─────────────────────────────────────────────
Agent descriptions     7,746    1,576  -6,170
Skill descriptions     6,096    2,316  -3,780
Global CLAUDE.md       4,841    1,742  -3,099
Project CLAUDE.md      1,105      ???    -???
─────────────────────────────────────────────
TOTAL                 19,788    ?,???  -?,???
```

## What this skill does NOT do

- Does not modify agent/skill body content (only frontmatter `description` fields)
- Does not delete skills or agents (only recommends)
- Does not modify files without user approval
- Does not touch conversation history, logs, or file-history
- Does not optimize the built-in Claude Code system prompt (that's Anthropic's domain)
