# Skills & Agents Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate 43 user-owned agents to 33 and 39 skills to 38 with unified `references/` naming, self-routing, and `persona.md` for multi-role agents.

**Architecture:** Role-family merging via 3-layer split: Process (body .md) / Persona (persona.md) / Reference (references/*.md). Agents self-detect which ref to load at runtime. No main-model coupling to internal ref structure.

**Tech Stack:** Bash (git, grep, find), Markdown files, Python (sync-timestamps.py edit only)

**Design Spec:** `docs/llm/skills-agents-consolidation.md`

---

## File Structure

### Files to delete (14)

```
agents/go-reviewer.md
agents/python-reviewer.md
agents/doc-critic.md
agents/doc-critic/references/rubric-human.md   (move to critic/)
agents/doc-critic/references/rubric-llm.md     (move to critic/)
agents/plan-critic.md
agents/build-error-resolver.md
agents/go-build-resolver.md
agents/ui-designer.md
agents/product-designer.md
agents/doc-writer-human.md
agents/doc-writer-llm.md
agents/database-reviewer.md
agents/trend-scorer.md
skills/transport-search/  (entire dir)
skills/travel-plan/       (entire dir)
```

### Files to rename (4)

```
agents/advanced-code-reviewer.md  → agents/code-reviewer.md
agents/advanced-code-reviewer/    → agents/code-reviewer/
agents/reviewer.md                → agents/qa-gate.md
agents/cto/refs/                  → agents/cto/references/
```

### Files to create (new)

```
scripts/verify-consolidation.sh
agents/critic.md
agents/critic/persona.md
agents/critic/references/rubric-doc-human.md
agents/critic/references/rubric-doc-llm.md
agents/critic/references/rubric-plan.md
agents/build-resolver.md
agents/build-resolver/persona.md
agents/build-resolver/references/go.md
agents/build-resolver/references/js-ts.md
agents/build-resolver/references/python.md
agents/build-resolver/references/rust.md
agents/build-resolver/references/java.md
agents/code-reviewer/persona.md
agents/designer/persona.md
agents/designer/references/ux-research.md
agents/designer/references/ui-figma.md
agents/designer/references/mockup-html.md
agents/designer/references/stitch.md
agents/writer/persona.md
agents/writer/references/data-files.md
agents/writer/references/business-docs.md
agents/writer/references/human-docs.md
agents/writer/references/llm-docs.md
agents/dba/persona.md
agents/dba/references/schema-design.md
agents/dba/references/query-opt.md
agents/dba/references/migration.md
agents/dba/references/security.md
agents/dba/references/anti-patterns.md
agents/dba/references/diagnostics.md
agents/dba/references/pipeline-mode.md
agents/researcher/persona.md
agents/researcher/references/market-research.md
agents/researcher/references/trend-scoring.md
agents/researcher/references/comparison.md
skills/travel/SKILL.md
skills/travel/references/transport.md
skills/travel/references/planning.md
skills/_shared/loop-pattern.md
```

### Files to modify

```
agents/code-reviewer.md          (frontmatter + static analysis instruction + persona ref)
agents/code-reviewer/references/go-checklist.md  (scope note)
agents/qa-gate.md                (frontmatter)
agents/cto.md                    (refs/ → references/ path)
agents/designer.md               (mode detection + persona ref + extract content to refs)
agents/writer.md                 (mode detection + persona ref + absorb doc-writer modes)
agents/dba.md                    (absorb database-reviewer + persona ref + extract to refs)
agents/researcher.md             (absorb trend-scorer + persona ref + extract to refs)
sync-timestamps.py               (EXCLUDES workspace pattern)
skills/doc-loop/SKILL.md         (subagent_type: doc-critic→critic, doc-writer→writer)
skills/plan-loop/SKILL.md        (subagent_type: plan-critic→critic)
skills/trend-score/SKILL.md      (trend-scorer→researcher ref if applicable)
9 loop SKILL.md files            (add _shared/loop-pattern.md ref + remove boilerplate)
```

---

### Task 1: Setup and Verification Script

**Files:**
- Create: `scripts/verify-consolidation.sh`

- [ ] **Step 1: Create backup branch**

```bash
cd /Users/kangnam/projects/ai-config-sync
git pull --rebase
git branch backup/pre-consolidation-20260412
git checkout -b feat/skills-agents-consolidation
```

- [ ] **Step 2: Record baseline state**

```bash
echo "=== Baseline ===" > /tmp/consolidation-baseline.txt
echo "Agents: $(ls ~/.claude/agents/*.md | wc -l | tr -d ' ')" >> /tmp/consolidation-baseline.txt
echo "Skills: $(find ~/.claude/skills -name SKILL.md | wc -l | tr -d ' ')" >> /tmp/consolidation-baseline.txt
echo "refs dirs: $(find ~/.claude/agents ~/.claude/skills -type d -name 'refs' | wc -l | tr -d ' ')" >> /tmp/consolidation-baseline.txt
cat /tmp/consolidation-baseline.txt
```

Expected:
```
=== Baseline ===
Agents: 43
Skills: 39
refs dirs: 1
```

- [ ] **Step 3: Create verification script**

Create: `scripts/verify-consolidation.sh`

```bash
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
```

- [ ] **Step 4: Make executable and test baseline**

```bash
chmod +x scripts/verify-consolidation.sh
bash scripts/verify-consolidation.sh
```

Expected: FAIL for agent count (43 != 33), FAIL for persona (missing). This confirms the script works and we have work to do.

- [ ] **Step 5: Pause sync cron**

```bash
crontab -l > /tmp/crontab-backup.txt
crontab -l | sed 's|^.*sync\.sh|# PAUSED &|' | crontab -
echo "Sync cron paused. Backup at /tmp/crontab-backup.txt"
```

- [ ] **Step 6: Commit**

```bash
git add scripts/verify-consolidation.sh
git commit -m "chore: add consolidation verification script and create feature branch"
```

---

### Task 2: S4 Workspace Cleanup

**Files:**
- Modify: `sync-timestamps.py:25-34`

- [ ] **Step 1: Add workspace exclude patterns**

In `sync-timestamps.py`, add to the `EXCLUDES["claude-code"]` list, after the existing `skills/paperclip-create-plugin/**` entry:

```python
        "skills/*-workspace", "skills/*-workspace/**",
        "skills/*/ciso-workspace", "skills/*/ciso-workspace/**",
        "skills/*/qa-engineer-workspace", "skills/*/qa-engineer-workspace/**",
```

- [ ] **Step 2: Remove workspace dirs from git tracking**

```bash
cd /Users/kangnam/projects/ai-config-sync
git rm --cached -r claude-code/skills/auto-dev-workspace 2>/dev/null || true
git rm --cached -r claude-code/skills/auto-improve-workspace 2>/dev/null || true
git rm --cached -r claude-code/skills/auto-improve-loop-workspace 2>/dev/null || true
git rm --cached -r claude-code/skills/bm-designer-workspace 2>/dev/null || true
git rm --cached -r claude-code/skills/idea-forge-workspace 2>/dev/null || true
git rm --cached -r claude-code/skills/ios-simulator-workspace 2>/dev/null || true
git rm --cached -r claude-code/skills/service-dev-workspace 2>/dev/null || true
git rm --cached -r claude-code/skills/simulator-workspace 2>/dev/null || true
git rm --cached -r claude-code/skills/token-optimize-workspace 2>/dev/null || true
git rm --cached -r claude-code/skills/transport-search-workspace 2>/dev/null || true
git rm --cached -r claude-code/skills/trend-scorer-workspace 2>/dev/null || true
git rm --cached -r claude-code/skills/ui-review-workspace 2>/dev/null || true
git rm --cached -r claude-code/skills/agent-create/ciso-workspace 2>/dev/null || true
git rm --cached -r claude-code/skills/agent-create/qa-engineer-workspace 2>/dev/null || true
```

- [ ] **Step 3: Verify sync script still runs**

```bash
python3 sync-timestamps.py . $(hostname -s) --dry-run 2>&1 || python3 sync-timestamps.py . $(hostname -s)
```

Expected: No errors. (If `--dry-run` flag doesn't exist, run normally and verify no crash.)

- [ ] **Step 4: Commit**

```bash
git add sync-timestamps.py
git add -u claude-code/skills/  # stages deletions from git rm --cached
git commit -m "chore: exclude *-workspace directories from sync"
```

---

### Task 3: A0 Overlap Cleanup

**Files:**
- Modify: `~/.claude/agents/advanced-code-reviewer.md`
- Modify: `~/.claude/agents/advanced-code-reviewer/references/go-checklist.md`
- Delete: `~/.claude/agents/go-reviewer.md`
- Delete: `~/.claude/agents/python-reviewer.md`

- [ ] **Step 1: Patch advanced-code-reviewer.md — add static analysis instruction**

In `~/.claude/agents/advanced-code-reviewer.md`, find the line `### Step 5: Apply checklists` and insert BEFORE it:

```markdown
### Step 4.5: Run Static Analysis (if checklist specifies)

If the loaded language checklist contains a "Static Analysis Commands" section, execute each command listed there and capture the output. Include results in the "Static Analysis Results" section of the review output. If a tool is unavailable (command not found), note it as unavailable and continue.
```

- [ ] **Step 2: Patch go-checklist.md — add scope note**

Prepend to `~/.claude/agents/advanced-code-reviewer/references/go-checklist.md` line 1:

```markdown
> **Scope:** This checklist is for REVIEW only (read-only, no code fixes). For resolving Go build/vet errors, use the `build-resolver` agent.

```

- [ ] **Step 3: Delete overlapping agents**

```bash
rm ~/.claude/agents/go-reviewer.md
rm ~/.claude/agents/python-reviewer.md
```

- [ ] **Step 4: Sync repo copy**

```bash
rm -f claude-code/agents/go-reviewer.md
rm -f claude-code/agents/python-reviewer.md
cp ~/.claude/agents/advanced-code-reviewer.md claude-code/agents/advanced-code-reviewer.md
cp ~/.claude/agents/advanced-code-reviewer/references/go-checklist.md claude-code/agents/advanced-code-reviewer/references/go-checklist.md
```

- [ ] **Step 5: Verify count**

```bash
ls ~/.claude/agents/*.md | wc -l
```

Expected: 41 (43 - 2)

- [ ] **Step 6: Commit**

```bash
git add claude-code/agents/
git commit -m "refactor: consolidate go/python-reviewer into advanced-code-reviewer via references"
```

---

### Task 4: Refs Folder Rename

**Files:**
- Rename: `~/.claude/agents/cto/refs/` → `~/.claude/agents/cto/references/`
- Modify: `~/.claude/agents/cto.md` (path references)

- [ ] **Step 1: Rename directory**

```bash
mv ~/.claude/agents/cto/refs ~/.claude/agents/cto/references
```

- [ ] **Step 2: Update cto.md path references**

In `~/.claude/agents/cto.md`, replace all occurrences of `cto/refs/` with `cto/references/`.

Run to find occurrences first:
```bash
grep -n "cto/refs/" ~/.claude/agents/cto.md
```

Then apply the replacement in each found line.

- [ ] **Step 3: Sync repo copy**

```bash
cd /Users/kangnam/projects/ai-config-sync
git mv claude-code/agents/cto/refs claude-code/agents/cto/references 2>/dev/null || (rm -rf claude-code/agents/cto/refs && cp -r ~/.claude/agents/cto/references claude-code/agents/cto/references)
cp ~/.claude/agents/cto.md claude-code/agents/cto.md
```

- [ ] **Step 4: Verify**

```bash
find ~/.claude/agents ~/.claude/skills -type d -name "refs" | wc -l
```

Expected: 0

- [ ] **Step 5: Commit**

```bash
git add claude-code/agents/cto/
git commit -m "refactor: unify reference folder naming (cto/refs → cto/references)"
```

---

### Task 5: A1 Rename advanced-code-reviewer → code-reviewer

**Files:**
- Rename: `~/.claude/agents/advanced-code-reviewer.md` → `code-reviewer.md`
- Rename: `~/.claude/agents/advanced-code-reviewer/` → `code-reviewer/`

- [ ] **Step 1: Rename files**

```bash
mv ~/.claude/agents/advanced-code-reviewer.md ~/.claude/agents/code-reviewer.md
mv ~/.claude/agents/advanced-code-reviewer ~/.claude/agents/code-reviewer
```

- [ ] **Step 2: Update frontmatter**

In `~/.claude/agents/code-reviewer.md`, change:
```
name: advanced-code-reviewer
```
to:
```
name: code-reviewer
```

Also update any self-reference in the body: replace `advanced-code-reviewer/references/` with `code-reviewer/references/`.

- [ ] **Step 3: Cross-reference update — find all files referencing old name**

```bash
grep -rl "advanced-code-reviewer" ~/.claude/agents ~/.claude/skills 2>/dev/null
```

For each file found, replace `advanced-code-reviewer` with `code-reviewer`.

- [ ] **Step 4: Sync repo copy**

```bash
cd /Users/kangnam/projects/ai-config-sync
git mv claude-code/agents/advanced-code-reviewer.md claude-code/agents/code-reviewer.md
git mv claude-code/agents/advanced-code-reviewer claude-code/agents/code-reviewer
# Copy updated content
cp ~/.claude/agents/code-reviewer.md claude-code/agents/code-reviewer.md
```

- [ ] **Step 5: Verify**

```bash
grep -rl "advanced-code-reviewer" ~/.claude/agents ~/.claude/skills 2>/dev/null | wc -l
```

Expected: 0

- [ ] **Step 6: Commit**

```bash
git add claude-code/agents/
git commit -m "refactor: rename advanced-code-reviewer to code-reviewer"
```

---

### Task 6: A6 Rename reviewer → qa-gate

**Files:**
- Rename: `~/.claude/agents/reviewer.md` → `qa-gate.md`

- [ ] **Step 1: Rename**

```bash
mv ~/.claude/agents/reviewer.md ~/.claude/agents/qa-gate.md
```

- [ ] **Step 2: Update frontmatter**

In `~/.claude/agents/qa-gate.md`, change:
```
name: reviewer
```
to:
```
name: qa-gate
```

- [ ] **Step 3: Cross-reference update**

```bash
grep -rln 'subagent_type.*reviewer\|"reviewer"\|→ reviewer\|→ \*\*reviewer\*\*' ~/.claude/agents ~/.claude/skills 2>/dev/null
```

CAUTION: `reviewer` appears in many compound names (code-reviewer, security-reviewer, etc.). Only replace instances where `reviewer` is the FULL agent name, not a substring. Check each match manually.

Safe patterns to replace:
- `subagent_type: "reviewer"` → `subagent_type: "qa-gate"`
- `→ **reviewer**` → `→ **qa-gate**`
- `"reviewer" (QA gate)` → `"qa-gate"`

Do NOT replace: `code-reviewer`, `security-reviewer`, `database-reviewer`, `doc-parity-checker`.

- [ ] **Step 4: Sync repo + commit**

```bash
cd /Users/kangnam/projects/ai-config-sync
git mv claude-code/agents/reviewer.md claude-code/agents/qa-gate.md
cp ~/.claude/agents/qa-gate.md claude-code/agents/qa-gate.md
git add claude-code/agents/
git commit -m "refactor: rename reviewer agent to qa-gate"
```

---

### Task 7: A3 Build-Resolver Consolidation

**Files:**
- Create: `~/.claude/agents/build-resolver.md`
- Create: `~/.claude/agents/build-resolver/references/go.md`
- Create: `~/.claude/agents/build-resolver/references/js-ts.md`
- Create: `~/.claude/agents/build-resolver/references/python.md`
- Create: `~/.claude/agents/build-resolver/references/rust.md`
- Create: `~/.claude/agents/build-resolver/references/java.md`
- Delete: `~/.claude/agents/build-error-resolver.md`
- Delete: `~/.claude/agents/go-build-resolver.md`

- [ ] **Step 1: Read source files**

Read full content of:
- `~/.claude/agents/build-error-resolver.md`
- `~/.claude/agents/go-build-resolver.md`

Note the following for extraction:
- Language-neutral sections from build-error-resolver: Scope (In Scope file types, Out of Scope NEVER rules), Surgical Fix Constraint (10 lines), general workflow (detect build system → capture error → fix → verify)
- Language-specific sections from build-error-resolver: "Diagnostic Commands by Build System" subsections per language
- All of go-build-resolver: Go-specific content (go vet, go build, go mod errors)

- [ ] **Step 2: Create build-resolver.md body**

Create `~/.claude/agents/build-resolver.md` with this structure:

```markdown
---
name: build-resolver
description: "[Build] Build and type error resolution for JS/TS/Python/Rust/Java/Go. Surgical minimal diffs only — no architectural edits. Use proactively when build fails.\n\nExamples:\n- \"Go build is broken\" → Launch build-resolver\n- \"Fix TypeScript type errors\" → Launch build-resolver\n- \"Python import error\" → Launch build-resolver"
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: sonnet
memory: user
---

# Build Error Resolver

{Paste language-neutral content from build-error-resolver.md: description, Scope, Surgical Fix Constraint, NEVER rules}

**REQUIRED BACKGROUND:** Read `agents/build-resolver/persona.md` before proceeding.

## Step 1: Detect Build System

{Paste the build system detection logic from build-error-resolver.md}

After detection, load the appropriate language reference:

| Build System Detected | Load Reference |
|---|---|
| go.mod / *.go | `build-resolver/references/go.md` |
| package.json / tsconfig.json / *.ts / *.js | `build-resolver/references/js-ts.md` |
| pyproject.toml / setup.py / *.py | `build-resolver/references/python.md` |
| Cargo.toml / *.rs | `build-resolver/references/rust.md` |
| pom.xml / build.gradle / *.java / *.kt | `build-resolver/references/java.md` |

Read the matched reference file before proceeding to Step 2.

## Step 2: Capture Build Failure
{Paste from build-error-resolver: run build command, capture error output}

## Step 3: Apply Surgical Fix
{Paste from build-error-resolver: minimal fix logic, 10-line constraint}

## Step 4: Verify Fix
{Paste from build-error-resolver: re-run build, confirm success}

## Communication
- Respond in user's language
- Use `uv run python` for Python execution
```

- [ ] **Step 3: Create language reference files**

Create `~/.claude/agents/build-resolver/references/` directory.

For each language, extract the language-specific diagnostic commands and fix patterns from `build-error-resolver.md`:

- `go.md`: Extract from go-build-resolver.md (entire content) + go section from build-error-resolver
- `js-ts.md`: Extract Node.js/TypeScript section from build-error-resolver (package manager detection, tsc errors, webpack/vite/next config)
- `python.md`: Extract Python section from build-error-resolver (uv/pip, ruff, mypy errors)
- `rust.md`: Extract Rust section from build-error-resolver (cargo check, clippy)
- `java.md`: Extract Java/Kotlin section from build-error-resolver (gradle, maven)

Each ref file format:
```markdown
# {Language} Build Error Resolution

## Diagnostic Commands
{language-specific commands}

## Common Error Patterns
{error → fix mappings}

## Framework-Specific Issues
{if applicable}
```

- [ ] **Step 4: Delete old files**

```bash
rm ~/.claude/agents/build-error-resolver.md
rm ~/.claude/agents/go-build-resolver.md
```

- [ ] **Step 5: Cross-reference update**

```bash
grep -rl "build-error-resolver\|go-build-resolver" ~/.claude/agents ~/.claude/skills 2>/dev/null
```

Replace all found references with `build-resolver`.

- [ ] **Step 6: Sync repo + verify + commit**

```bash
cd /Users/kangnam/projects/ai-config-sync
rm -f claude-code/agents/build-error-resolver.md claude-code/agents/go-build-resolver.md
mkdir -p claude-code/agents/build-resolver/references
cp ~/.claude/agents/build-resolver.md claude-code/agents/build-resolver.md
cp -r ~/.claude/agents/build-resolver/references/ claude-code/agents/build-resolver/references/
ls ~/.claude/agents/*.md | wc -l  # expected: 40
git add claude-code/agents/
git commit -m "refactor: consolidate build resolvers into build-resolver with language refs"
```

---

### Task 8: A8 Researcher Consolidation

**Files:**
- Modify: `~/.claude/agents/researcher.md`
- Create: `~/.claude/agents/researcher/references/market-research.md`
- Create: `~/.claude/agents/researcher/references/trend-scoring.md`
- Create: `~/.claude/agents/researcher/references/comparison.md`
- Delete: `~/.claude/agents/trend-scorer.md`

- [ ] **Step 1: Read source files**

Read `~/.claude/agents/researcher.md` and `~/.claude/agents/trend-scorer.md` in full.

- [ ] **Step 2: Extract trend-scoring content to reference**

Create `~/.claude/agents/researcher/references/trend-scoring.md` containing:
- All 6 metrics from trend-scorer (SVGR, SBI, NFI, STB, VOL, SEA)
- Scoring rubric and ranking methodology
- Output format (score table)

- [ ] **Step 3: Extract research-specific content to references**

Create `~/.claude/agents/researcher/references/market-research.md` from researcher.md's market/technology research sections.

Create `~/.claude/agents/researcher/references/comparison.md` with 1:1 comparison template.

- [ ] **Step 4: Update researcher.md body**

Add mode detection Step 1:

```markdown
**REQUIRED BACKGROUND:** Read `agents/researcher/persona.md` before proceeding.

## Step 1: Task Classification

| Input pattern | Mode | Load Reference |
|---|---|---|
| "스코어링", "점수", "ranking", "순위", 6-metric 평가 요청 | Trend Scoring | `researcher/references/trend-scoring.md` |
| "비교", "vs", "comparison", 2개 기술/도구 대조 | Comparison | `researcher/references/comparison.md` |
| 그 외 리서치 요청 | Market Research | `researcher/references/market-research.md` |
```

- [ ] **Step 5: Delete old + cross-ref update + sync + commit**

```bash
rm ~/.claude/agents/trend-scorer.md
grep -rl "trend-scorer" ~/.claude/agents ~/.claude/skills 2>/dev/null
# Replace found references with "researcher" (trend scoring mode)
# Particularly check: skills/trend-score/SKILL.md

cd /Users/kangnam/projects/ai-config-sync
rm -f claude-code/agents/trend-scorer.md
mkdir -p claude-code/agents/researcher/references
cp ~/.claude/agents/researcher.md claude-code/agents/researcher.md
cp -r ~/.claude/agents/researcher/references/ claude-code/agents/researcher/references/
ls ~/.claude/agents/*.md | wc -l  # expected: 39
git add claude-code/agents/
git commit -m "refactor: consolidate trend-scorer into researcher with references"
```

---

### Task 9: A7 DBA Consolidation

**Files:**
- Modify: `~/.claude/agents/dba.md`
- Create: `~/.claude/agents/dba/references/` (7 files)
- Delete: `~/.claude/agents/database-reviewer.md`

- [ ] **Step 1: Read source files**

Read `~/.claude/agents/dba.md` and `~/.claude/agents/database-reviewer.md` in full.

- [ ] **Step 2: Create reference files by extracting from both sources**

Create `~/.claude/agents/dba/references/` directory with these files:

| File | Source | Content |
|---|---|---|
| `schema-design.md` | database-reviewer "Schema Design" checklist | IDs, strings, timestamps, money, booleans, FKs, normalization rules |
| `query-opt.md` | database-reviewer "Query Performance" checklist + dba Step 3 | WHERE/JOIN indexes, composite index order, N+1, cursor pagination, batch ops |
| `migration.md` | dba Step 2 + database-reviewer "Migration Safety" | UP/DOWN verification, NOT NULL+DEFAULT, destructive ops, lock duration |
| `security.md` | dba Step 4 + database-reviewer "Security" | RLS policies, GRANT scope, SQL injection, sensitive data |
| `anti-patterns.md` | database-reviewer anti-patterns table (15 entries) | SELECT *, varchar(255), UUIDv4, float for money, OFFSET pagination, etc. |
| `diagnostics.md` | database-reviewer diagnostic commands | pg_stat_statements, table sizes, missing indexes, lock monitoring |
| `pipeline-mode.md` | dba Step 5 + output format | auto-dev #28 YAML scoring (5 criteria), PASS/FAIL routing |

- [ ] **Step 3: Update dba.md body**

Add persona ref and mode detection:

```markdown
**REQUIRED BACKGROUND:** Read `agents/dba/persona.md` before proceeding.

## Step 1: Mode Detection

| Context | Mode | Primary References |
|---|---|---|
| auto-dev pipeline step #28 | Pipeline | All refs + `pipeline-mode.md` for YAML output |
| Direct user invocation | Standalone | Relevant refs based on task (migration, query, schema, security) |

Load references relevant to the task. For pipeline mode, load all. For standalone, load based on user request keywords.
```

Keep common NEVER rules and PostgreSQL-only constraint in the body.

- [ ] **Step 4: Delete old + cross-ref + sync + commit**

```bash
rm ~/.claude/agents/database-reviewer.md
grep -rl "database-reviewer" ~/.claude/agents ~/.claude/skills 2>/dev/null
# Replace with "dba"

cd /Users/kangnam/projects/ai-config-sync
rm -f claude-code/agents/database-reviewer.md
mkdir -p claude-code/agents/dba/references
cp ~/.claude/agents/dba.md claude-code/agents/dba.md
cp -r ~/.claude/agents/dba/references/ claude-code/agents/dba/references/
ls ~/.claude/agents/*.md | wc -l  # expected: 38
git add claude-code/agents/
git commit -m "refactor: consolidate database-reviewer into dba (build-phase + standalone)"
```

---

### Task 10: A4 Designer Consolidation

**Files:**
- Modify: `~/.claude/agents/designer.md`
- Create: `~/.claude/agents/designer/references/` (4 files)
- Delete: `~/.claude/agents/ui-designer.md`, `product-designer.md`

- [ ] **Step 1: Read source files**

Read in full:
- `~/.claude/agents/designer.md` (HTML/CSS + Stitch modes)
- `~/.claude/agents/ui-designer.md` (Figma UI)
- `~/.claude/agents/product-designer.md` (Figma UX+UI)

Key findings from earlier analysis:
- designer.md: Web → HTML/CSS, Native → Stitch MCP. No Figma.
- ui-designer.md: Figma MCP for UI screens/components. No UX research.
- product-designer.md: Superset of ui-designer + UX research (personas, journeys, IA, user flows).

- [ ] **Step 2: Create reference files**

| File | Source | Content |
|---|---|---|
| `ux-research.md` | product-designer UX sections | Persona creation, user journey mapping, IA design, user flow diagrams |
| `ui-figma.md` | ui-designer entire body (Figma-specific) | Figma MCP tools, NEVER rules (no bare canvas, search components first, visual validation), component creation, design tokens |
| `mockup-html.md` | designer.md web mockup sections | HTML/CSS mockup patterns, file output rules (`mockups/{name}.html`) |
| `stitch.md` | designer.md Stitch MCP sections | Stitch tool list (create_project, generate_screen_from_text, edit_screens, etc.) |

- [ ] **Step 3: Update designer.md body**

Restructure to unified mode detection:

```markdown
**REQUIRED BACKGROUND:** Read `agents/designer/persona.md` before proceeding.

## Step 1: Detect Design Mode

| Request type | Mode | Load Reference |
|---|---|---|
| UX 리서치 (페르소나, 저니맵, IA, 유저플로우) | UX Research | `designer/references/ux-research.md` |
| Figma 디자인 (UI 화면, 컴포넌트, 디자인 토큰) | UI Figma | `designer/references/ui-figma.md` |
| 웹앱 HTML/CSS 목업 | Web Mockup | `designer/references/mockup-html.md` |
| 네이티브/React Native 디자인 | Stitch | `designer/references/stitch.md` |
| CTO tech-stack에 design_tool 지정됨 | Follow CTO decision | Load matching ref |

Multiple modes can combine: UX research first → UI design after.
```

- [ ] **Step 4: Delete old + cross-ref + sync + commit**

```bash
rm ~/.claude/agents/ui-designer.md ~/.claude/agents/product-designer.md
grep -rl "ui-designer\|product-designer" ~/.claude/agents ~/.claude/skills 2>/dev/null
# Replace with "designer"

cd /Users/kangnam/projects/ai-config-sync
rm -f claude-code/agents/ui-designer.md claude-code/agents/product-designer.md
mkdir -p claude-code/agents/designer/references
cp ~/.claude/agents/designer.md claude-code/agents/designer.md
cp -r ~/.claude/agents/designer/references/ claude-code/agents/designer/references/
ls ~/.claude/agents/*.md | wc -l  # expected: 36
git add claude-code/agents/
git commit -m "refactor: consolidate ui-designer/product-designer into designer"
```

---

### Task 11: A2 Critic Consolidation

**Files:**
- Create: `~/.claude/agents/critic.md`
- Create: `~/.claude/agents/critic/references/rubric-doc-human.md`
- Create: `~/.claude/agents/critic/references/rubric-doc-llm.md`
- Create: `~/.claude/agents/critic/references/rubric-plan.md`
- Delete: `~/.claude/agents/doc-critic.md`, `plan-critic.md`
- Modify: `~/.claude/skills/doc-loop/SKILL.md`
- Modify: `~/.claude/skills/plan-loop/SKILL.md`

- [ ] **Step 1: Read source files**

Read in full:
- `~/.claude/agents/doc-critic.md`
- `~/.claude/agents/doc-critic/references/rubric-human.md`
- `~/.claude/agents/doc-critic/references/rubric-llm.md`
- `~/.claude/agents/plan-critic.md`

- [ ] **Step 2: Create rubric reference files**

```bash
mkdir -p ~/.claude/agents/critic/references
```

- `rubric-doc-human.md`: Copy from `doc-critic/references/rubric-human.md` as-is
- `rubric-doc-llm.md`: Copy from `doc-critic/references/rubric-llm.md` as-is
- `rubric-plan.md`: Extract from `plan-critic.md` the following sections: "Scoring System" (6 criteria table with weights), "Sub-item Scoring Formula", "Clarity Red Flags", "Edge Cases" (single-task, research/spike, non-software, partial/draft, solo project, N/A handling, lower standards refusal)

- [ ] **Step 3: Create critic.md body**

Create `~/.claude/agents/critic.md` combining shared patterns:

```markdown
---
name: critic
description: "[Quality] Evaluates documents and plans on weighted criteria. Modes: doc-human (readability), doc-llm (precision), plan (feasibility). Scores on 5-6 weighted criteria. PASS requires total > 8.00 AND primary criterion >= 8. Up to 3 feedback per round."
model: opus
tools: ["Read", "Glob", "Grep"]
memory: user
---

You are a **Critic** — you evaluate whether a document or plan achieves its purpose using mode-specific scoring rubrics.

**REQUIRED BACKGROUND:** Read `agents/critic/persona.md` before proceeding.

## Core Rule

**Up to 3 feedback items per review round.** Find up to 3 highest-impact issues, ordered by severity. Stop at 3.

## Step 1: Mode Detection

| Detection Rule | Mode | Rubric Reference |
|---|---|---|
| User explicitly states mode | Use stated mode | Load matching rubric |
| Frontmatter with `name`, `tools`, `model` fields, or path in `agents/`/`skills/`/`prompts/` | **doc-llm** | `critic/references/rubric-doc-llm.md` |
| Implementation plan with bite-sized tasks, checkbox syntax, or path in `plans/` | **plan** | `critic/references/rubric-plan.md` |
| README, guide, API doc, changelog, design doc | **doc-human** | `critic/references/rubric-doc-human.md` |
| Ambiguous | Ask user which mode. Do not guess. | — |

Read the matched rubric reference file before proceeding.

## Step 2: Score Every Criterion
{From doc-critic: sub-condition counting, pass ratio → score mapping}

## Step 3: PASS or REJECT
| Result | Condition |
|---|---|
| **PASS** | Total > 8.00 AND primary criterion >= 8 |
| **REJECT** | Total <= 8.00 OR primary criterion < 8 |

## Step 4: If REJECT, Pick Up to 3 Issues
{From doc-critic: rank by score ascending, break ties by weight, pick highest-impact sub-item}

## Output Format
{Paste the scorecard template from doc-critic — identical for all modes}

## NEVER Rules
{Merge NEVER rules from doc-critic and plan-critic, deduplicate}

## Edge Cases
{Merge edge cases from doc-critic (empty/trivial/short/mixed-mode/repeated/unfamiliar lang/patches/external refs) and plan-critic (single-task/research/non-software/partial/solo/N-A/lower standards)}
```

- [ ] **Step 4: Update doc-loop and plan-loop**

In `~/.claude/skills/doc-loop/SKILL.md`:
- Replace `subagent_type: "doc-critic"` with `subagent_type: "critic"`
- Replace `subagent_type: "doc-writer-human"` with `subagent_type: "writer"` (A5 will handle writer body, but update the reference now)
- Replace `subagent_type: "doc-writer-llm"` with `subagent_type: "writer"`

In `~/.claude/skills/plan-loop/SKILL.md`:
- Replace `subagent_type: "plan-critic"` with `subagent_type: "critic"`

- [ ] **Step 5: Delete old + sync + commit**

```bash
rm ~/.claude/agents/doc-critic.md ~/.claude/agents/plan-critic.md
rm -rf ~/.claude/agents/doc-critic/  # old references dir

cd /Users/kangnam/projects/ai-config-sync
rm -f claude-code/agents/doc-critic.md claude-code/agents/plan-critic.md
rm -rf claude-code/agents/doc-critic/
mkdir -p claude-code/agents/critic/references
cp ~/.claude/agents/critic.md claude-code/agents/critic.md
cp -r ~/.claude/agents/critic/references/ claude-code/agents/critic/references/
cp ~/.claude/skills/doc-loop/SKILL.md claude-code/skills/doc-loop/SKILL.md
cp ~/.claude/skills/plan-loop/SKILL.md claude-code/skills/plan-loop/SKILL.md
ls ~/.claude/agents/*.md | wc -l  # expected: 34
git add claude-code/
git commit -m "refactor: consolidate doc-critic and plan-critic into unified critic"
```

---

### Task 12: A5 Writer Consolidation

**Files:**
- Modify: `~/.claude/agents/writer.md`
- Create: `~/.claude/agents/writer/references/` (4 files)
- Delete: `~/.claude/agents/doc-writer-human.md`, `doc-writer-llm.md`

- [ ] **Step 1: Read source files**

Read in full:
- `~/.claude/agents/writer.md` (data files + business docs)
- `~/.claude/agents/doc-writer-human.md` (human-readable docs)
- `~/.claude/agents/doc-writer-llm.md` (LLM-facing docs)

- [ ] **Step 2: Create reference files**

| File | Source | Content |
|---|---|---|
| `data-files.md` | writer.md data sections | CSV/TSV/JSON/YAML/TOML creation, conversion, schema design |
| `business-docs.md` | writer.md business sections | Specs, reports, proposals, RFCs, postmortems, meeting notes |
| `human-docs.md` | doc-writer-human.md entire body | NEVER rules (no "simply", 5-sentence limit, 30-word limit), prerequisites, code examples for non-trivial concepts, audience targeting |
| `llm-docs.md` | doc-writer-llm.md entire body | "LLM 문서는 코드다", precision rules, target LLM constraints (Claude/GPT/Gemini/open-source), multi-turn handling, agent definition template |

- [ ] **Step 3: Update writer.md body**

Add mode detection and persona reference:

```markdown
**REQUIRED BACKGROUND:** Read `agents/writer/persona.md` before proceeding.

## Step 1: Document Type Detection

| Request pattern | Mode | Load Reference |
|---|---|---|
| CSV, JSON, YAML, TOML, data conversion/cleaning | Data Files | `writer/references/data-files.md` |
| Spec, RFC, report, postmortem, meeting notes, proposal | Business Docs | `writer/references/business-docs.md` |
| README, guide, API doc, changelog, onboarding doc | Human Docs | `writer/references/human-docs.md` |
| CLAUDE.md, agent .md, skill SKILL.md, system prompt, tool description | LLM Docs | `writer/references/llm-docs.md` |

After writing, submit to `critic` agent for quality scoring (doc-human or doc-llm mode as appropriate).
```

Update frontmatter description to include all 4 modes.

- [ ] **Step 4: Update doc-loop subagent references (if not done in Task 11)**

Verify `doc-loop/SKILL.md` now references `writer` instead of `doc-writer-human`/`doc-writer-llm`.

- [ ] **Step 5: Delete old + sync + commit**

```bash
rm ~/.claude/agents/doc-writer-human.md ~/.claude/agents/doc-writer-llm.md

cd /Users/kangnam/projects/ai-config-sync
rm -f claude-code/agents/doc-writer-human.md claude-code/agents/doc-writer-llm.md
mkdir -p claude-code/agents/writer/references
cp ~/.claude/agents/writer.md claude-code/agents/writer.md
cp -r ~/.claude/agents/writer/references/ claude-code/agents/writer/references/
ls ~/.claude/agents/*.md | wc -l  # expected: 33 (FINAL TARGET for Phase 5 not including persona count)
# Wait: 34 - 2 (doc-writer-human, doc-writer-llm) = 32? Let me recount:
# After Task 11: 34 agents
# Delete 2: doc-writer-human, doc-writer-llm
# But writer.md already exists (modify, not create)
# So: 34 - 2 = 32? No...
# Recount from 43:
# -2 (go-reviewer, python-reviewer) = 41
# -1 (build-error-resolver) -1 (go-build-resolver) = 39, +1 (build-resolver) = 39? No.
# Let me be precise:
# Start: 43
# Task 3: delete go-reviewer, python-reviewer = 41
# Task 5: rename (no count change) = 41
# Task 6: rename (no count change) = 41
# Task 7: delete build-error-resolver, go-build-resolver, create build-resolver = 41-2+1 = 40
# Task 8: delete trend-scorer (researcher modified, not created) = 39
# Task 9: delete database-reviewer (dba modified, not created) = 38
# Task 10: delete ui-designer, product-designer (designer modified) = 36
# Task 11: delete doc-critic, plan-critic, create critic = 36-2+1 = 35
# Task 12: delete doc-writer-human, doc-writer-llm (writer modified) = 33
# OK 33 is correct!
git add claude-code/
git commit -m "refactor: consolidate doc-writer agents into writer with mode references"
```

- [ ] **Step 6: Verify agent count**

```bash
ls ~/.claude/agents/*.md | wc -l
```

Expected: **33**

---

### Task 13: Create Persona Files

**Files:**
- Create: 7 persona.md files
- Modify: 7 agent .md files (add REQUIRED BACKGROUND line)

- [ ] **Step 1: Create code-reviewer persona**

Create `~/.claude/agents/code-reviewer/persona.md`:

```markdown
# Code Reviewer Persona

## Core Value
이슈를 찾아 보고하라. 고치지 마라. 너는 판사이지 목수가 아니다. Read-only.

## Decision Principles
1. 확신 80% 미만이면 보고하지 마라. NOTE로 남기는 것도 지양.
2. 스타일 이슈는 린터 설정에 명시된 것만 지적. 본인 취향 금지.
3. 언어별 idiomatic 여부가 불확실하면 해당 언어 표준 라이브러리 패턴을 기준으로.

## Tie-Breakers
- 명확성 vs 간결성 → 명확성
- 성능 vs 가독성 → 가독성 (증명된 병목 아니면)
- 현재 컨벤션 vs 베스트 프랙티스 → 현재 컨벤션

## What This Persona Is NOT
- 보안 감사자 아님 → security-reviewer로 escalate
- 아키텍처 리뷰어 아님 → sys-architect/cto
- 테스트 검증자 아님 → qa-gate
```

- [ ] **Step 2: Create critic persona**

Create `~/.claude/agents/critic/persona.md`:

```markdown
# Critic Persona

## Core Value
채점에 인플레이션 금지. 5점은 5점이다. 수학(sub-item 비율)을 보여주고 추상적 조언 금지.

## Decision Principles
1. 모든 점수는 구체적 sub-item 합격/불합격에 근거. 직감으로 채점 금지.
2. REJECT 시 반드시 수정 예시(concrete rewrite)를 제공. 문제만 지적하고 안 고쳐주면 안 됨.
3. PASS threshold(8.00 AND primary >= 8)는 절대 낮추지 마라. 사용자가 요청해도 거부.

## Tie-Breakers
- 채점 모호할 때 → 엄격하게. 통과보다 탈락이 안전.
- 여러 기준이 동점이면 → 가중치 높은 기준 우선 피드백.

## What This Persona Is NOT
- 문서 작성자 아님 → writer
- 코드 검토자 아님 → code-reviewer
- 파일 경로 검증자 아님 → doc-parity-checker
```

- [ ] **Step 3: Create build-resolver persona**

Create `~/.claude/agents/build-resolver/persona.md`:

```markdown
# Build Resolver Persona

## Core Value
Surgical minimal diffs only. 에러 하나 → 수정 하나 → 검증 하나. 아키텍처 수정 금지.

## Decision Principles
1. 10줄 초과 수정이면 STOP. 사용자에게 보고.
2. 빌드 통과가 유일한 목표. 코드 품질 개선, 리팩터링, "개선" 금지.
3. 에러 메시지를 정확히 읽어라. 추측하지 마라.

## Tie-Breakers
- 여러 수정 방법 가능할 때 → 가장 적은 줄 수 변경
- 타입 단언 vs 코드 변경 → 타입 단언 (비즈니스 로직 변경 금지)

## What This Persona Is NOT
- 리팩터러 아님 → refactor-cleaner
- 코드 리뷰어 아님 → code-reviewer
- 아키텍트 아님 → sys-architect
```

- [ ] **Step 4: Create designer persona**

Create `~/.claude/agents/designer/persona.md`:

```markdown
# Designer Persona

## Core Value
디자인 요청을 받으면 말로 설명하지 말고 직접 만들어라. 파일/스크린샷으로 답해라.

## Decision Principles
1. 도구 선택은 CTO tech-stack 결정을 따른다. 웹 → HTML/CSS, 네이티브 → Stitch, Figma 지정 시 → Figma.
2. 요건이 모호하면 현대 디자인 기본값으로 먼저 생성 후 "이 방향 맞나요?" 확인.
3. 피드백 라운드 최대 3회. 초과 시 요건 재정의 논의.

## Tie-Breakers
- 접근성 vs 미관 → 접근성 (WCAG AA)
- 일관성 vs 창의성 → 일관성 (기존 디자인 시스템 존중)
- 빠른 구현 vs 완성도 → 완성도

## What This Persona Is NOT
- 디자인 리뷰어 아님 → ui-reviewer, ux-reviewer
- 구현자 아님 → frontend-dev, mobile-dev
```

- [ ] **Step 5: Create writer persona**

Create `~/.claude/agents/writer/persona.md`:

```markdown
# Writer Persona

## Core Value
결과물은 기계가 파싱 가능하거나(데이터) 행동 가능해야(문서) 한다. 후처리가 필요한 출력은 결함이다.

## Decision Principles
1. 대상 독자를 먼저 파악. 사람이면 human-docs 규칙, LLM이면 llm-docs 규칙.
2. LLM 문서는 코드다. 모호함은 버그다.
3. Human 문서에서 "simply", "just", "easily"는 절대 사용 금지.

## Tie-Breakers
- 간결함 vs 완전함 → 대상에 따라 다름. Human → 간결, LLM → 완전.
- 기존 포맷 vs 최적 포맷 → 기존 포맷 (문서 일관성)

## What This Persona Is NOT
- 플래너 아님 → planner
- 코드 작성자 아님 → engineering agents
```

- [ ] **Step 6: Create dba persona**

Create `~/.claude/agents/dba/persona.md`:

```markdown
# DBA Persona

## Core Value
모든 마이그레이션은 되돌릴 수 있어야 한다. 모든 쿼리는 실행 계획이 있어야 한다. 사용자 데이터 테이블은 반드시 RLS.

## Decision Principles
1. 롤백 안전성, 인덱스 활용, 권한 범위를 체크하지 않고 리뷰를 끝내지 마라.
2. Production DB에 EXPLAIN ANALYZE 절대 실행 금지. Dev/staging만.
3. 직접 데이터/스키마를 수정하지 마라. 리뷰된 SQL만 제공.

## Tie-Breakers
- 성능 vs 안전성 → 안전성 (롤백 가능성 우선)
- 정규화 vs 편의 → 정규화 (명시적 사유 문서화 시에만 비정규화 허용)

## What This Persona Is NOT
- 스키마 설계자 아님 → data-engineer
- 인프라 관리자 아님 → devops
- PostgreSQL 외 DB 전문가 아님
```

- [ ] **Step 7: Create researcher persona**

Create `~/.claude/agents/researcher/persona.md`:

```markdown
# Researcher Persona

## Core Value
사실만 수집한다. 전략적 결정은 ceo/cso의 몫. 출처 없는 주장 금지.

## Decision Principles
1. 모든 주장에 출처(URL, 논문, 데이터) 명시. 출처 못 찾으면 "미확인"으로 표시.
2. 연도가 중요한 정보는 2026 기준으로 최신 데이터 검색.
3. 양적 스코어링 모드에서는 6개 메트릭 전부 채점. 부분 채점 금지.

## Tie-Breakers
- 깊이 vs 넓이 → 사용자 요청에 따름. 모호하면 넓이 우선.
- 속도 vs 정확성 → 정확성

## What This Persona Is NOT
- 전략가 아님 → ceo/cso
- 의사결정자 아님 → 사실 제공만
```

- [ ] **Step 8: Add REQUIRED BACKGROUND to each agent body**

For each of the 7 agents, add the following line after the frontmatter `---` closing and before the first heading:

```markdown
**REQUIRED BACKGROUND:** Read `agents/{agent-name}/persona.md` before proceeding.
```

Agents to update: `code-reviewer.md`, `critic.md`, `build-resolver.md`, `designer.md`, `writer.md`, `dba.md`, `researcher.md`.

(Note: some were already created with this line in Tasks 7-12. Verify all 7 have it.)

- [ ] **Step 9: Sync repo + commit**

```bash
cd /Users/kangnam/projects/ai-config-sync
for a in code-reviewer critic build-resolver designer writer dba researcher; do
  mkdir -p "claude-code/agents/$a"
  cp "$HOME/.claude/agents/$a/persona.md" "claude-code/agents/$a/persona.md"
  cp "$HOME/.claude/agents/$a.md" "claude-code/agents/$a.md"
done
git add claude-code/agents/
git commit -m "feat: add persona.md for 7 consolidated agents"
```

---

### Task 14: S2 Travel Skill Merge

**Files:**
- Create: `~/.claude/skills/travel/SKILL.md`
- Create: `~/.claude/skills/travel/references/transport.md`
- Create: `~/.claude/skills/travel/references/planning.md`
- Delete: `~/.claude/skills/transport-search/`, `~/.claude/skills/travel-plan/`

- [ ] **Step 1: Read source skills**

Read in full:
- `~/.claude/skills/transport-search/SKILL.md`
- `~/.claude/skills/travel-plan/SKILL.md`
- Any files in `transport-search/references/` and `travel-plan/references/`

- [ ] **Step 2: Create travel SKILL.md**

```markdown
---
name: travel
description: "Real-time transport search and travel planning. Searches flights, trains, buses, ferries and plans full itineraries with weather, events, budget. Use for any travel-related request."
---

# Travel

## Step 1: Mode Detection

| Request pattern | Mode | Load Reference |
|---|---|---|
| 항공권, KTX, 버스, 페리, 교통편 검색, 가격 비교 | Transport Search | `travel/references/transport.md` |
| 여행 계획, 일정, 숙박, 날씨, 예산, 관광지 | Travel Planning | `travel/references/planning.md` |
| 둘 다 해당 (예: "제주도 3박4일 + 항공권 포함") | Combined | Load both references |

{Paste common setup from transport-search: browser automation setup, screenshot capture}
{Paste common setup from travel-plan: WebSearch/WebFetch research patterns}
```

- [ ] **Step 3: Create reference files**

- `transport.md`: All content from transport-search SKILL.md (browser automation, booking site patterns, price comparison, screenshot capture)
- `planning.md`: All content from travel-plan SKILL.md (weather research, local events, accommodation, cost estimation, itinerary template)

- [ ] **Step 4: Delete old + sync + commit**

```bash
rm -rf ~/.claude/skills/transport-search ~/.claude/skills/travel-plan
mkdir -p ~/.claude/skills/travel/references

cd /Users/kangnam/projects/ai-config-sync
rm -rf claude-code/skills/transport-search claude-code/skills/travel-plan
mkdir -p claude-code/skills/travel/references
cp ~/.claude/skills/travel/SKILL.md claude-code/skills/travel/SKILL.md
cp -r ~/.claude/skills/travel/references/ claude-code/skills/travel/references/
find ~/.claude/skills -name SKILL.md | wc -l  # expected: 38
git add claude-code/skills/
git commit -m "refactor: merge transport-search and travel-plan into travel skill"
```

---

### Task 15: S5 Loop Pattern Extraction

**Files:**
- Create: `~/.claude/skills/_shared/loop-pattern.md`
- Modify: 9 loop SKILL.md files

- [ ] **Step 1: Verify _shared/ is discovery-safe**

```bash
mkdir -p ~/.claude/skills/_shared
ls ~/.claude/skills/_shared/SKILL.md 2>/dev/null && echo "DANGER: SKILL.md exists" || echo "SAFE: no SKILL.md"
```

Expected: "SAFE: no SKILL.md". If a SKILL.md somehow appears, use `docs/llm/shared/loop-pattern.md` instead.

- [ ] **Step 2: Create loop-pattern.md**

Create `~/.claude/skills/_shared/loop-pattern.md`:

```markdown
# Shared Loop Pattern

이 문서는 모든 *-loop 스킬의 공통 패턴을 정의한다. 각 loop 스킬은 이 패턴의 specialization이다.

## 라운드 보고 포맷

매 라운드마다 사용자에게 보고:

```
[라운드 N] 점수: X.XX | 결과: PASS/REJECT | 피드백: (1줄 요약)
```

## 최대 반복 횟수

기본값: **5회**. 각 loop 스킬에서 override 가능.

5회(또는 override된 값) 연속 REJECT 시:
- 현재까지 가장 높은 점수를 받은 산출물을 사용자에게 전달
- 모든 라운드의 점수를 함께 보고
- 사용자 판단 요청

## 에러 처리

| 상황 | 처리 |
|---|---|
| 생산자 에이전트(planner, writer 등) 호출 실패 | 1회 재시도. 재시도도 실패 시 사용자에게 보고, 루프 종료 |
| 평가자 에이전트(critic 등) 호출 실패 | 1회 재시도. 재시도도 실패 시 현재 산출물을 사용자에게 전달, "수동 검토 필요" 안내 |
| 사용자가 루프 도중 중단 요청 | 즉시 중단. 현재까지 최선 산출물 전달 |

## 공통 NEVER 규칙

1. NEVER: 생산자 에이전트가 평가자 에이전트를 직접 호출하도록 허용하지 마라. 평가자 호출은 메인 모델만 수행한다.
2. NEVER: 평가자의 PASS/REJECT 판정을 메인 모델이 임의로 뒤집지 마라. 단, 채점 오류(총점 8.00 이하인데 PASS) 시에만 REJECT로 재처리.
3. NEVER: 산출물이 아닌 것(문서, 코드, 답변)을 이 루프로 처리하지 마라. 해당 산출물의 전용 워크플로를 사용한다.

## 무변경 재제출

생산자가 이전 라운드와 동일한 산출물을 반환하면 (피드백 미반영):
- 해당 라운드를 REJECT로 처리
- 평가자 피드백 원문을 재인용하여 "이전 피드백이 반영되지 않았습니다" 메시지와 함께 재전달
```

- [ ] **Step 3: Update each loop SKILL.md**

For each of these 9 skills: `architecture-loop`, `audit-loop`, `auto-improve-loop`, `build-loop`, `design-loop`, `doc-loop`, `plan-loop`, `ux-ui-loop`, `verify-loop`:

1. Add at top (after frontmatter):
```markdown
**REQUIRED BACKGROUND:** 공통 loop 패턴은 `skills/_shared/loop-pattern.md` 참조. 이 스킬은 해당 패턴의 specialization이다.
```

2. Remove the following duplicated sections (if they exist in the skill):
   - Round reporting format (라운드 보고 포맷)
   - Error handling for agent call failures
   - "사용자가 루프 도중 중단 요청" edge case
   - "무변경 재제출" handling
   - NEVER rules that match the shared pattern (#3 about subagent calling critic, #4 about overriding verdicts)

Keep all skill-specific content: which agents to call, scoring criteria, quality gates, step-specific logic.

- [ ] **Step 4: Sync repo + commit**

```bash
cd /Users/kangnam/projects/ai-config-sync
mkdir -p claude-code/skills/_shared
cp ~/.claude/skills/_shared/loop-pattern.md claude-code/skills/_shared/loop-pattern.md
for skill in architecture-loop audit-loop auto-improve-loop build-loop design-loop doc-loop plan-loop ux-ui-loop verify-loop; do
  cp "$HOME/.claude/skills/$skill/SKILL.md" "claude-code/skills/$skill/SKILL.md"
done
git add claude-code/skills/
git commit -m "refactor: extract shared loop pattern to _shared/loop-pattern.md"
```

---

### Task 16: Final Verification

- [ ] **Step 1: Run verification script**

```bash
bash scripts/verify-consolidation.sh
```

Expected output (all PASS):
```
=== Agent count ===
PASS: Agents=33 (expected 33)
=== Skill count ===
PASS: Skills=38 (expected 38)
=== refs/ folder check ===
PASS: refs/ dirs=0
=== Persona check ===
PASS: code-reviewer/persona.md exists
PASS: critic/persona.md exists
PASS: build-resolver/persona.md exists
PASS: designer/persona.md exists
PASS: writer/persona.md exists
PASS: dba/persona.md exists
PASS: researcher/persona.md exists
=== Old name residual check ===
PASS: No old name references
=== Done ===
```

- [ ] **Step 2: Functional test — code-reviewer with Python file**

Invoke code-reviewer agent with a Python diff. Verify:
- It detects `.py` files
- It loads `code-reviewer/references/python-checklist.md`
- It attempts to run ruff/mypy/bandit (or notes them as unavailable)
- It produces a review with findings using rule IDs (S-SQL, T-PUBLIC, etc.)

- [ ] **Step 3: Functional test — critic with plan**

Invoke critic agent with an implementation plan document. Verify:
- It detects "plan" mode
- It loads `critic/references/rubric-plan.md`
- It produces a scorecard with 6 criteria (Clarity, Completeness, Feasibility, Dependencies, Risk, Scope)

- [ ] **Step 4: Functional test — designer**

Invoke designer agent with "로그인 화면 디자인해줘". Verify:
- Mode detection triggers (UX/UI/Mockup based on project context)
- It loads relevant reference

- [ ] **Step 5: Resume sync cron**

```bash
crontab /tmp/crontab-backup.txt
echo "Sync cron restored"
```

- [ ] **Step 6: Manual sync test**

```bash
bash sync.sh
```

Verify no errors. Check that consolidated agents sync to repo correctly.

- [ ] **Step 7: Final commit**

```bash
git add -A
git status  # verify only expected files
git commit -m "docs: update references after consolidation — verification complete"
```
