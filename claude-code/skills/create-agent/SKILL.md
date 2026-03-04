---
name: create-agent
description: "Use when the user wants to create a new custom agent for Claude Code. Generates a properly formatted agent .md file in ~/.claude/agents/ following the user's established conventions.\n\nExamples:\n- \"/create-agent\" → Launch skill to create a new agent\n- \"새 에이전트 만들어줘\" → Launch skill\n- \"QA 테스터 에이전트 추가해\" → Launch skill with context"
---

# Create Agent Skill

Generate a new custom agent `.md` file in `~/.claude/agents/` that matches the user's existing agent conventions.

## Workflow

### 1. Gather Requirements

Ask the user for the following (skip any they already provided):

- **name**: kebab-case agent name (e.g., `qa-tester`, `tech-writer`)
- **role**: What this agent does (1-2 sentences)
- **model**: `haiku` (lightweight tasks), `sonnet` (development/analysis), or `opus` (complex reasoning/strategy)

### 2. Analyze Existing Agents

Read 2-3 existing agents from `~/.claude/agents/` to match the current conventions:
- Frontmatter format (name, description, model, memory, tools)
- Section structure (role intro → responsibilities → expertise → workflow → collaboration → communication)
- Tone and detail level

### 3. Generate Agent File

Create `~/.claude/agents/{name}.md` with this structure:

```markdown
---
name: {name}
description: "{1-2 sentence description with 3-5 usage examples}"
model: {model}
memory: user
---

{Role introduction paragraph - 1-2 sentences, senior professional persona}

## Core Responsibilities

{4-6 numbered responsibilities}

## Technical Expertise (or domain-specific equivalent)

{Relevant skills, tools, frameworks organized by category}

## Workflow

{Step-by-step working process}

## Collaboration

- Work with relevant existing agents
- Follow **planner**'s task assignments (if applicable)

## Communication

- Respond in user's language
- Use `uv run python` for Python execution

**Update your agent memory** as you discover {domain-specific learnings}.
```

### 4. Configuration Decisions

- **tools**: Only restrict if the agent should NOT have full tool access (e.g., read-only agents). Default: omit (grants all tools).
- **model**: Match complexity to cost:
  - `haiku`: Translation, git ops, simple formatting
  - `sonnet`: Code writing, analysis, debugging
  - `opus`: Strategy, complex reasoning, architecture decisions

### 5. Verify

- Confirm the file was created at the correct path
- Show the user the complete agent file for review

## Rules

- Match the style and depth of existing agents — don't be more verbose or more terse
- Description examples in frontmatter should use the arrow format: `"Do X" → Launch {name}`
- Always include `memory: user` in frontmatter
- Korean persona descriptions are fine if user speaks Korean, but agent names must be English kebab-case
- Don't add unnecessary sections — keep it focused on the agent's actual domain
