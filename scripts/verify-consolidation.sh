#!/bin/bash
set -euo pipefail

EXPECTED_AGENTS=33
EXPECTED_SKILLS=38
CLAUDE_DIR="$HOME/.claude"
OLD_NAMES="advanced-code-reviewer|go-reviewer|python-reviewer|ui-designer|product-designer|doc-critic|plan-critic|database-reviewer|trend-scorer|build-error-resolver|go-build-resolver|doc-writer-human|doc-writer-llm"
PERSONA_AGENTS="code-reviewer critic build-resolver designer writer dba researcher"

echo "=== Agent count ==="
AGENTS=$(ls "$CLAUDE_DIR/agents/"*.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$AGENTS" -eq "$EXPECTED_AGENTS" ]; then
  echo "PASS: Agents=$AGENTS (expected $EXPECTED_AGENTS)"
else
  echo "FAIL: Agents=$AGENTS (expected $EXPECTED_AGENTS)"
fi

echo "=== Skill count ==="
SKILLS=$(find "$CLAUDE_DIR/skills" -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$SKILLS" -eq "$EXPECTED_SKILLS" ]; then
  echo "PASS: Skills=$SKILLS (expected $EXPECTED_SKILLS)"
else
  echo "FAIL: Skills=$SKILLS (expected $EXPECTED_SKILLS)"
fi

echo "=== refs/ folder check ==="
REFS=$(find "$CLAUDE_DIR/agents" "$CLAUDE_DIR/skills" -type d -name "refs" 2>/dev/null | wc -l | tr -d ' ')
if [ "$REFS" -eq 0 ]; then
  echo "PASS: refs/ dirs=$REFS"
else
  echo "FAIL: refs/ dirs=$REFS (expected 0)"
  find "$CLAUDE_DIR/agents" "$CLAUDE_DIR/skills" -type d -name "refs" 2>/dev/null
fi

echo "=== Persona check ==="
for a in $PERSONA_AGENTS; do
  if [ -f "$CLAUDE_DIR/agents/$a/persona.md" ]; then
    echo "PASS: $a/persona.md exists"
  else
    echo "FAIL: $a/persona.md MISSING"
  fi
done

echo "=== Old name residual check ==="
FOUND=$(grep -rl "$OLD_NAMES" "$CLAUDE_DIR/agents" "$CLAUDE_DIR/skills" 2>/dev/null | grep -v ".git" | wc -l | tr -d ' ')
if [ "$FOUND" -eq 0 ]; then
  echo "PASS: No old name references"
else
  echo "FAIL: $FOUND files still reference old names:"
  grep -rl "$OLD_NAMES" "$CLAUDE_DIR/agents" "$CLAUDE_DIR/skills" 2>/dev/null | grep -v ".git"
fi

echo "=== Done ==="
