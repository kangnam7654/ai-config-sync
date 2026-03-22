# JSON Schemas

This document defines the JSON schemas used by agent-create.

Schemas are identical to skill-create's schemas — the eval infrastructure is shared. See the skill-create `references/schemas.md` for the canonical definitions. Key schemas summarized below for convenience.

---

## evals.json

Defines the evals for an agent. Located at `evals/evals.json` within the workspace.

```json
{
  "agent_name": "example-agent",
  "evals": [
    {
      "id": 1,
      "prompt": "User's example prompt that the agent should handle",
      "expected_output": "Description of expected result",
      "files": [],
      "expectations": [
        "The agent follows its 3-step workflow",
        "The output contains required sections"
      ]
    }
  ]
}
```

---

## grading.json

Output from the grader agent. Located at `<run-dir>/grading.json`.

Required fields in expectations array: `text`, `passed`, `evidence` (the viewer depends on these exact field names).

```json
{
  "expectations": [
    {
      "text": "The agent follows its defined workflow",
      "passed": true,
      "evidence": "Transcript shows all workflow steps executed in order"
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  },
  "execution_metrics": {},
  "timing": {},
  "claims": [],
  "user_notes_summary": {},
  "eval_feedback": {}
}
```

---

## benchmark.json

Output from benchmark aggregation. Located at `<iteration-dir>/benchmark.json`.

```json
{
  "metadata": {
    "skill_name": "agent-name",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },
  "runs": [
    {
      "eval_id": 1,
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85,
        "passed": 6,
        "total": 7,
        "time_seconds": 42.5,
        "tokens": 3800
      },
      "expectations": [],
      "notes": []
    }
  ],
  "run_summary": {},
  "notes": []
}
```

**Important:** The viewer reads field names exactly. `configuration` must be `"with_skill"` or `"without_skill"`. Results must be nested under `result`.

---

## timing.json

Captured from subagent task completion notifications. Located at `<run-dir>/timing.json`.

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

---

## comparison.json & analysis.json

See `agents/comparator.md` and `agents/analyzer.md` for their output formats.
