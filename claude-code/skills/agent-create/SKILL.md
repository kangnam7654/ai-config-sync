---
name: agent-create
description: "Create new Claude Code agents or modify existing ones, with full eval/benchmark infrastructure. Generates properly formatted agent .md files in ~/.claude/agents/ following the doc-writer-llm template, the 5-point instruction check, and doc-critic scoring conventions. After creation, supports test case execution, benchmark grading, and iterative improvement — the same eval flow as skill-create. Use this skill whenever the user wants to create, edit, extend, or refactor a custom agent definition.\n\nExamples:\n- \"새 에이전트 만들어줘\" → Launch agent-create\n- \"QA 테스터 에이전트 추가해\" → Launch agent-create\n- \"Create a code review agent\" → Launch agent-create\n- \"이 에이전트 수정해줘\" → Launch agent-create (modify mode)\n- \"에이전트 두 개가 겹치는 것 같아\" → Launch agent-create (overlap analysis)\n\nNOT this skill:\n- Writing skill SKILL.md files → skill-create\n- Writing CLAUDE.md or system prompts → doc-writer-llm\n- Evaluating an existing agent's quality → doc-critic"
---

# Agent Creator

Create new Claude Code agent `.md` files or modify existing ones, with full eval infrastructure for testing and iterative improvement.

At a high level, the process goes like this:

- Capture intent and research existing agents
- Write the agent .md file with proper structure
- Run it through doc-critic quality gate
- Create test cases and run the agent on them
- Help the user evaluate results (qualitative via viewer + quantitative via benchmarks)
- Rewrite the agent based on feedback
- Repeat until satisfied
- Optimize the description for reliable triggering

Your job is to figure out where the user is in this process and help them progress. Maybe they want a new agent from scratch, or maybe they already have one and want to improve it.

## Creating an agent

### 1. Capture Intent

Determine what the user wants. Extract answers from conversation history first — do not re-ask questions the user already answered.

If the user has not provided enough context, ask a maximum of 3 questions in a single message:

1. **What does this agent do?** (role, core responsibilities, 1-2 sentence summary)
2. **When should it trigger?** (3-5 example phrases a user would say to invoke this agent)
3. **Which model?** (`haiku` for lightweight/translation tasks, `sonnet` for development/analysis, `opus` for complex reasoning/architecture)

Additional context to extract:
- **Tools needed**: Which tools does the agent require? Default: omit `tools` field (grants all tools). Only restrict if the agent must be read-only or limited.
- **Relationship to existing agents**: Does this agent overlap with or depend on any existing agent?

### 2. Research Existing Agents

Read 2-3 existing agents from `~/.claude/agents/` to match conventions. Prioritize agents related to the new agent's domain.

**Overlap check**: Compare the new agent's intended trigger phrases and responsibilities against every existing agent's `description` field.

- List all files in `~/.claude/agents/` with `Glob`
- Read the frontmatter `description` of each agent file (first 10 lines are sufficient)
- Identify any agent whose trigger examples or scope overlaps

**If overlap is found**: Present the overlap analysis table and wait for the user's decision.

### 3. Generate Agent File

Create `~/.claude/agents/{name}.md` following the required template structure. Every instruction must pass the 5-point check: **Specific**, **Unambiguous**, **Testable**, **Complete**, **Bounded**.

**Required template sections** (in this exact order):
- Frontmatter (name, description, model, memory: user)
- Role sentence
- Core Principle
- Scope (IN scope + OUT of scope with agent redirects)
- Rules (ALWAYS + NEVER, 3+ rules each)
- Workflow (every step has an **Output** line)
- Output Format (code-fence templates, not prose)
- Edge Cases (table with 5+ rows)
- Collaboration
- Communication

**Banned words** — zero tolerance: "적절히", "필요에 따라", "등", "기타", "as needed", "handle edge cases", "use your judgment", "respond appropriately", "when appropriate", "if necessary", "properly", "correctly"

### 4. Self-Check Before Quality Gate

Verify every item in this checklist before proceeding:

| # | Check |
|---|-------|
| 1 | Every instruction passes the 5-point check |
| 2 | Zero banned words in the entire file |
| 3 | Every output format uses a code-fence template |
| 4 | Edge Cases table has 5+ rows |
| 5 | Every workflow step has an **Output** line |
| 6 | ALWAYS and NEVER rules sections both present |
| 7 | Scope has both IN and OUT sections |
| 8 | OUT of scope items redirect to specific agents |
| 9 | Frontmatter description has 3-5 trigger examples |
| 10 | Frontmatter description has "NOT this agent" examples |
| 11 | Agent name is English kebab-case |
| 12 | `memory: user` is in frontmatter |
| 13 | No two instructions contradict each other |

### 5. Quality Gate (doc-critic)

Return the completed agent file to the main model. The main model orchestrates the doc-critic quality gate:
- Submit to **doc-critic** in LLM mode
- **PASS threshold**: Total > 8.00 AND Precision >= 8
- **If REJECT**: Fix the specific issue and return for re-scoring
- **Max 5 iterations**

This skill does NOT call doc-critic directly — it returns the file to the main model for orchestration.

---

## Testing the agent

After the agent passes doc-critic, set up test cases to verify it works. If the user says "I don't need to run evaluations, just vibe with me", skip this section.

### 6. Write Test Cases

Come up with 2-3 realistic test prompts — the kind of thing a real user would say to invoke this agent. Share them with the user for confirmation.

Save test cases to the workspace:

```json
{
  "agent_name": "example-agent",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": [],
      "expectations": [
        "The agent follows its defined workflow",
        "Output matches the Output Format template"
      ]
    }
  ]
}
```

See `references/schemas.md` for the full schema.

### 7. Run and Evaluate Test Cases

This section is one continuous sequence. Put results in `<agent-name>-workspace/` as a sibling to the skill directory. Organize by iteration (`iteration-1/`, `iteration-2/`, etc.) and test case (`eval-0/`, `eval-1/`, etc.).

#### Step 1: Spawn all runs in the same turn

For each test case, spawn two subagents in the same turn — one with the agent, one without.

**With-agent run:** Spawn the new agent with the test prompt. Save outputs to `<workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/`.

**Baseline run:** Same prompt, no agent (or old agent version for improvements). Save to `without_skill/outputs/` (or `old_skill/outputs/`).

Write an `eval_metadata.json` for each test case. Give each eval a descriptive name.

#### Step 2: While runs are in progress, draft assertions

Draft quantitative assertions for each test case. Good assertions for agents:
- "Agent follows its N-step workflow in order"
- "Output contains all required sections from Output Format"
- "Agent stays within IN scope boundaries"
- "Agent respects NEVER rules"
- "Edge case X is handled per the Edge Cases table"

Update `eval_metadata.json` files with the assertions.

#### Step 3: As runs complete, capture timing data

When each subagent completes, save `total_tokens` and `duration_ms` to `timing.json` immediately.

#### Step 4: Grade, aggregate, and launch the viewer

1. **Grade each run** — spawn a grader subagent that reads `agents/grader.md` and evaluates assertions. Save to `grading.json`. Use fields `text`, `passed`, `evidence` (viewer depends on these exact names).

2. **Aggregate into benchmark**:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```

3. **Analyst pass** — read `agents/analyzer.md` for what to look for.

4. **Launch the viewer**:
   ```bash
   nohup python <agent-create-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-agent" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   For iteration 2+, pass `--previous-workspace`. For headless environments, use `--static <output_path>`.

5. **Tell the user** the viewer is ready.

#### Step 5: Read the feedback

Read `feedback.json` when the user is done reviewing. Empty feedback means satisfied. Kill the viewer when done.

---

## Improving the agent

### How to think about improvements

1. **Generalize from feedback.** The agent will be used many times across different prompts. Avoid overfitting to specific test cases — generalize to broader patterns.

2. **Keep the agent lean.** Read the transcripts, not just outputs. If the agent is wasting time on unproductive steps, simplify.

3. **Explain the why.** Today's LLMs are smart. Explain reasoning behind instructions rather than using heavy-handed MUSTs. If you find yourself writing ALWAYS in all caps, reframe as an explanation of why it matters.

4. **Look for repeated work.** If all test runs independently wrote similar helper scripts, that's a signal the agent should include that script or instruction.

### The iteration loop

1. Apply improvements to the agent .md file
2. Rerun all test cases into `iteration-<N+1>/`, including baselines
3. Launch the viewer with `--previous-workspace`
4. Wait for user review
5. Read feedback, improve again, repeat

Keep going until the user is satisfied, feedback is all empty, or progress plateaus.

### Advanced: Blind comparison

For rigorous comparison between two agent versions, read `agents/comparator.md` and `agents/analyzer.md`. Optional — human review is usually sufficient.

---

## Description Optimization

The description field in the agent's frontmatter determines whether Claude spawns this agent. After creating or improving an agent, offer to optimize the description.

### Step 1: Generate trigger eval queries

Create 20 eval queries — a mix of should-trigger and should-not-trigger. Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

Queries must be realistic — concrete, with detail, file paths, context. Not abstract. Focus on edge cases, not clear-cut examples.

For **should-trigger** (8-10): different phrasings of the same intent, some formal, some casual. Include cases where the user doesn't name the agent but clearly needs it.

For **should-not-trigger** (8-10): near-misses that share keywords but need a different agent. Avoid obviously irrelevant queries.

### Step 2: Review with user

Present using the HTML template from `assets/eval_review.html`. Replace placeholders, write to temp file, open in browser. User edits and exports.

### Step 3: Run the optimization loop

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --agent-path <path-to-agent.md> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

This handles the full loop automatically: train/test split, evaluate, improve, re-evaluate up to 5 times.

### Step 4: Apply the result

Take `best_description` from the JSON output and update the agent's frontmatter.

---

## Rules

### ALWAYS
- Include `memory: user` in every agent's frontmatter
- Use English kebab-case for agent names
- Include both IN/OUT scope sections with agent redirects for OUT items
- Include both ALWAYS/NEVER rules sections with 3+ rules each
- Include an Edge Cases table with 5+ rows
- Include an **Output** line after every workflow step
- Read 2-3 existing agents before generating to match conventions
- Run the overlap check against all existing agents before generating

### NEVER
- Use banned vague words (see list in Step 3)
- Generate an agent without completing intent capture and research
- Skip the self-check before returning the agent file
- Write contradictory instructions
- Call doc-critic directly — return the file to the main model
- Ask more than 3 questions in the intent capture step

---

## Reference files

- `agents/grader.md` — How to evaluate assertions against agent outputs
- `agents/comparator.md` — How to do blind A/B comparison between two outputs
- `agents/analyzer.md` — How to analyze why one version beat another, and how to analyze benchmark results
- `references/schemas.md` — JSON structures for evals.json, grading.json, benchmark.json, timing.json
