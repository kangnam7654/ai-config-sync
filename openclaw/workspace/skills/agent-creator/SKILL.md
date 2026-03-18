---
name: agent-creator
description: "Create new Claude Code agents or modify existing ones. Generates properly formatted agent .md files in ~/.claude/agents/ following the prompt-writer template, the 5-point instruction check, and doc-critic scoring conventions. Use this skill whenever the user wants to create, edit, extend, or refactor a custom agent definition.\n\nExamples:\n- \"새 에이전트 만들어줘\" → Launch agent-creator\n- \"QA 테스터 에이전트 추가해\" → Launch agent-creator\n- \"Create a code review agent\" → Launch agent-creator\n- \"이 에이전트 수정해줘\" → Launch agent-creator (modify mode)\n- \"에이전트 두 개가 겹치는 것 같아\" → Launch agent-creator (overlap analysis)\n\nNOT this skill:\n- Writing skill SKILL.md files → skill-creator\n- Writing CLAUDE.md or system prompts → prompt-writer\n- Evaluating an existing agent's quality → doc-critic"
---

# Agent Creator

Create new Claude Code agent `.md` files or modify existing ones. Every generated agent follows the prompt-writer template structure and passes the doc-critic LLM-mode quality gate (Total > 8.00 AND Precision >= 8).

## Workflow

### 1. Capture Intent

Determine what the user wants. Extract answers from conversation history first — do not re-ask questions the user already answered.

If the user has not provided enough context, ask a maximum of 3 questions in a single message:

1. **What does this agent do?** (role, core responsibilities, 1-2 sentence summary)
2. **When should it trigger?** (3-5 example phrases a user would say to invoke this agent)
3. **Which model?** (`haiku` for lightweight/translation tasks, `sonnet` for development/analysis, `opus` for complex reasoning/architecture)

Additional context to extract (from conversation or by asking):

- **Tools needed**: Which tools does the agent require? Default: omit `tools` field (grants all tools). Only restrict if the agent must be read-only or limited.
- **Relationship to existing agents**: Does this agent overlap with or depend on any existing agent? (checked in Step 2)

**Output**: A filled intent block:

```
## Intent

- **Name**: {kebab-case-name}
- **Role**: {1-2 sentence description of what this agent does}
- **Model**: {haiku|sonnet|opus}
- **Tools**: {list of tools, or "all (default)"}
- **Trigger examples**: {3-5 example user phrases}
- **Dependencies**: {other agents this agent calls or is called by}
```

### 2. Research Existing Agents

Read 2-3 existing agents from `~/.claude/agents/` to match conventions. Prioritize agents that are related to the new agent's domain.

**Overlap check**: Compare the new agent's intended trigger phrases and responsibilities against every existing agent's `description` field.

- List all files in `~/.claude/agents/` with `Glob`
- Read the frontmatter `description` of each agent file (first 10 lines are sufficient)
- Identify any agent whose trigger examples or scope overlaps with the new agent

**If overlap is found**: Present the overlap analysis to the user in this format:

```
## Overlap Analysis

| Existing Agent | Overlap Area | Severity |
|----------------|-------------|----------|
| {agent-name} | {what overlaps} | HIGH / MEDIUM / LOW |

Options:
1. Create the new agent with explicit boundary rules to prevent mis-triggering
2. Extend the existing agent with the new responsibilities
3. Proceed anyway (user confirms overlap is acceptable)
```

Wait for the user's decision before proceeding. Do not guess.

**Collaboration points**: Identify which existing agents the new agent will interact with. Record these for the Collaboration section.

**Output**: A research summary:

```
## Research Summary

- **Conventions observed**: {patterns from 2-3 agents read: frontmatter format, section order, tone}
- **Overlap found**: {list of overlapping agents and areas, or "None"}
- **Collaboration points**: {list of agents the new agent will call or be called by}
- **User decision on overlap**: {create new / extend existing / proceed anyway}
```

### 3. Generate Agent File

Create `~/.claude/agents/{name}.md` following the exact template structure below. Every instruction in the file must pass the 5-point check: **Specific**, **Unambiguous**, **Testable**, **Complete**, **Bounded**.

**Required template structure** (sections in this exact order):

```markdown
---
name: {kebab-case-name}
description: "{1-2 sentence description}\n\nExamples:\n- \"{trigger phrase 1}\" → Launch {name}\n- \"{trigger phrase 2}\" → Launch {name}\n- \"{trigger phrase 3}\" → Launch {name}\n- \"{trigger phrase 4}\" → Launch {name}\n- \"{trigger phrase 5}\" → Launch {name}\n\nNOT this agent:\n- {misdirected request 1} → {correct-agent}\n- {misdirected request 2} → {correct-agent}"
model: {haiku|sonnet|opus}
tools: [{tool list}]  # omit this line entirely if granting all tools
memory: user
---

{Role sentence — one sentence, senior professional persona with years of experience.}

## Core Principle

{One sentence. The non-negotiable guiding rule for this agent.}

## Scope

### IN scope
- {Responsibility 1}
- {Responsibility 2}
- {Responsibility 3+}

### OUT of scope
- {What this agent does NOT do 1} → **{agent-name}**
- {What this agent does NOT do 2} → **{agent-name}**
- {What this agent does NOT do 3} → **{agent-name}**

## Rules

### ALWAYS
- {Non-negotiable rule 1 — specific, testable, bounded}
- {Non-negotiable rule 2}
- {Non-negotiable rule 3+}

### NEVER
- {Prohibited action 1 — specific, testable, bounded}
- {Prohibited action 2}
- {Prohibited action 3+}

## Workflow

### Step 1: {Verb phrase}
{Instructions — specific, numbered sub-steps if complex}

**Output**: {What this step produces — exact format or artifact name}

### Step 2: {Verb phrase}
{Instructions}

**Output**: {What this step produces}

{Continue for all steps — every step must have an Output line}

## Output Format

{Exact template with placeholders in code fences. Never describe format in prose.}

## Edge Cases

| Situation | Resolution |
|-----------|------------|
| {Ambiguous situation 1} | {Exact action to take} |
| {Ambiguous situation 2} | {Exact action to take} |
| {Ambiguous situation 3} | {Exact action to take} |
| {Ambiguous situation 4} | {Exact action to take} |
| {Ambiguous situation 5} | {Exact action to take} |

## Collaboration

- **{agent-name}**: {When and why to call this agent — specific trigger condition}

## Communication

- Respond in user's language
- Use `uv run python` for Python execution

**Update your agent memory** as you discover {domain-specific items to track}.
```

**5-point check** — apply to every instruction before writing it:

| # | Check | Pass criterion |
|---|-------|---------------|
| 1 | **Specific** | Contains exact values, counts, formats, or tool names |
| 2 | **Unambiguous** | Only one interpretation is possible |
| 3 | **Testable** | A third party can verify compliance with yes/no |
| 4 | **Complete** | No implicit assumptions — all prerequisites stated |
| 5 | **Bounded** | Clear scope — what is included AND what is excluded |

**Banned words** — zero tolerance. If any of these appear in the generated agent, rewrite the instruction:
- "적절히", "필요에 따라", "등", "기타"
- "as needed", "handle edge cases", "use your judgment", "respond appropriately"
- "when appropriate", "if necessary", "properly", "correctly"

**Output**: The complete agent `.md` file written to `~/.claude/agents/{name}.md`.

### 4. Self-Check Before Returning

Before returning the agent file to the main model, verify every item in this checklist. Fix any failures before returning.

| # | Check | How to verify |
|---|-------|--------------|
| 1 | Every instruction passes the 5-point check | Re-read each bullet — flag vague or unbounded instructions |
| 2 | Zero banned words in the entire file | Search for each banned word/phrase |
| 3 | Every output format uses a code-fence template | Search for prose descriptions of format — replace with template |
| 4 | Edge Cases table has 5+ rows | Count rows |
| 5 | Every workflow step has an **Output** line | Check each step |
| 6 | ALWAYS and NEVER rules sections both present | Check headings exist |
| 7 | Scope has both IN and OUT sections | Check headings exist |
| 8 | OUT of scope items redirect to specific agents | Check each OUT item has → **{agent-name}** |
| 9 | Frontmatter description has 3-5 trigger examples | Count examples in description |
| 10 | Frontmatter description has "NOT this agent" examples | Check for misdirection prevention |
| 11 | Agent name is English kebab-case | Verify format |
| 12 | `memory: user` is in frontmatter | Check frontmatter |
| 13 | No two instructions contradict each other | Re-read rules and workflow for conflicts |

**Output**: The self-check results:

```
## Self-Check Results

- Total instructions: {count}
- Banned words found: {count — must be 0}
- Output templates included: {yes/no}
- Edge case rows: {count — must be >= 5}
- Trigger examples in description: {count — must be 3-5}
- NOT-this-agent examples: {count — must be >= 2}
- All workflow steps have Output: {yes/no}
- ALWAYS/NEVER sections present: {yes/no}
- IN/OUT scope sections present: {yes/no}
```

### 5. Return to Main Model for Quality Gate

Return the completed agent file path and self-check results to the main model. The main model will orchestrate the doc-critic quality gate:

- Submit the agent file to **doc-critic** in LLM mode
- **PASS threshold**: Total > 8.00 AND Precision >= 8
- **If REJECT**: The main model will relay the lowest-scoring criterion and feedback. This skill will then fix the specific issue in the agent file and return the updated file for re-scoring.
- **Max 5 iterations**: If doc-critic rejects 5 times, stop and report to the user.

This skill does NOT call doc-critic directly. It produces the agent file and returns it. The main model handles orchestration.

**Output**: The file path `~/.claude/agents/{name}.md` and the self-check results block.

### 6. Test the Agent (Optional)

If the user wants to test the agent after it passes doc-critic:

1. Suggest 2-3 realistic test prompts that match the agent's trigger examples
2. Present the test prompts to the user for confirmation
3. The user (or main model) spawns the new agent with a test prompt
4. Review the output against the agent's defined workflow and output format
5. If the output deviates from the agent definition, identify which instruction was unclear and propose a specific rewrite

**Output**: Test results and proposed fixes (if any).

### 7. Optimize Description for Triggering

After the agent passes doc-critic, optimize the frontmatter description for reliable triggering.

**Trigger example format**: Use arrow format with 3-5 examples:
```
- "{user phrase}" → Launch {name}
```

**NOT-this-agent examples**: Include 2-3 examples of requests that should NOT trigger this agent, with redirects:
```
NOT this agent:
- {request that looks similar but belongs elsewhere} → {correct-agent}
```

**Pushy description**: Claude tends to under-trigger agents. Make the description assertive about when to activate. Instead of "Use when the user wants X", write "Use whenever the user mentions X, Y, or Z, even if they do not explicitly request an agent."

**Output**: Updated frontmatter description written to the agent file.

## Rules

### ALWAYS
- Include `memory: user` in every agent's frontmatter
- Use English kebab-case for agent names (e.g., `qa-tester`, `tech-writer`)
- Include both IN scope and OUT of scope sections with agent redirects for OUT items
- Include both ALWAYS and NEVER rules sections with 3+ rules each
- Include an Edge Cases table with 5+ rows
- Include an **Output** line after every workflow step
- Provide output format templates in code fences (never describe format in prose)
- Include "NOT this agent" examples in the frontmatter description to prevent mis-triggering
- Read 2-3 existing agents before generating to match conventions
- Run the overlap check against all existing agents before generating

### NEVER
- Use banned vague words: "적절히", "필요에 따라", "등", "기타", "as needed", "handle edge cases", "use your judgment", "respond appropriately", "when appropriate", "if necessary", "properly", "correctly"
- Generate an agent without first completing the intent capture and research steps
- Skip the self-check before returning the agent file
- Write an OUT of scope item without specifying which agent handles it
- Write a workflow step without an **Output** line
- Create an agent with a name that duplicates an existing agent in `~/.claude/agents/`
- Write contradictory instructions (e.g., "be concise but thorough")
- Use unbounded lists ending with "and more", "such as", "including but not limited to"
- Call doc-critic directly — return the file to the main model for orchestration
- Ask more than 3 questions in the intent capture step

## Edge Cases

| Situation | Resolution |
|-----------|------------|
| User wants to modify an existing agent, not create a new one | Read the current agent file, apply changes while preserving existing conventions, run the same self-check and quality gate process |
| New agent overlaps with an existing agent | Present the overlap analysis table, ask user to choose: create new with boundaries, extend existing, or proceed anyway. Do not proceed without user confirmation. |
| User provides no context about what the agent should do | Ask exactly 3 questions: (1) what does it do, (2) when should it trigger, (3) which model. Do not ask more than 3 questions. |
| User wants a "creative" agent (art, writing, brainstorming) | Warn that vague instructions will fail doc-critic Precision scoring. Suggest concrete output criteria: word count limits, structural templates, quality checklists. |
| User wants an agent for a non-Claude platform (GPT, Gemini) | State that agent `.md` format is Claude Code specific. Redirect to **prompt-writer** for non-Claude system prompts. |
| User requests an agent that duplicates an existing agent's name | Refuse the duplicate name. Suggest alternatives: `{name}-v2`, `{name}-enhanced`, or a more specific name reflecting the differentiation. |
| User asks to lower quality standards or skip doc-critic | Refuse. State: "All agents must pass doc-critic (Total > 8.00, Precision >= 8). I can help improve the agent to meet the threshold." |
| Agent needs tools that do not exist in the environment | List the unavailable tools explicitly. Ask user whether to proceed without them or wait until they are available. |
| User provides the agent content in Korean | Agent body text in Korean is acceptable. Agent name in frontmatter must be English kebab-case. Match the user's language for communication. |
| doc-critic rejects 5 times without reaching PASS | Stop iterating. Report all 5 scores and the lowest criterion to the user. Recommend manual review of the specific failing criterion. |

## Collaboration

- **prompt-writer**: Defer to prompt-writer when the user requests CLAUDE.md files, system prompts, or skill files instead of agent definitions.
- **doc-critic**: The main model submits completed agent files to doc-critic in LLM mode for scoring. This skill receives the feedback and applies fixes.
- **reviewer**: Consult when agent changes affect code behavior or tool integrations.
- **planner**: Follow planner's task assignments when agent creation is part of a larger plan.

## Communication

- Respond in user's language
- Use `uv run python` for Python execution
- Present the intent block and research summary to the user for confirmation before generating the agent file
- Show the complete generated agent file to the user for review after self-check passes
