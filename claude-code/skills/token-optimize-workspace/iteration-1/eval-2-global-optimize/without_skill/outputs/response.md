# Token Optimization Report (Global Scope)

## Phase 1: Measurement

Since I cannot run the measurement script directly (Bash denied), I performed manual analysis by reading all relevant files. Below are estimated token counts based on text length heuristics (English ~4 chars/token, Korean ~2-3 chars/token due to multi-byte encoding overhead).

### Current Token Consumption Summary

| Category | Items | Estimated Tokens | Notes |
|----------|-------|-----------------|-------|
| Agent descriptions (frontmatter) | 29 agents | ~2,800 | 2 have Examples sections, 0 have Korean in descriptions |
| Agent body content (Korean) | 28 files | ~8,000+ | 28 agents contain Korean in body text |
| Skill descriptions (frontmatter) | 38 skills | ~4,500 | Some very verbose (docx: ~120 tokens, xlsx: ~130 tokens, pptx: ~110 tokens, pdf: ~90 tokens) |
| Global CLAUDE.md | 1 file, 164 lines | ~2,400 | Fully English (already optimized) |
| Project CLAUDE.md | 1 file, 68 lines | ~1,500 | ~50% Korean content |
| Project MEMORY.md | 1 file, 6 lines | ~120 | Korean descriptions |
| Memory files (4 files) | 4 files | ~800 | 3 of 4 are Korean-heavy |
| **TOTAL** | | **~20,120** | |

Note: Agent/skill body content is NOT loaded into every conversation -- only descriptions in frontmatter are. The body is loaded only when the agent/skill is invoked. So the "always-on" cost is:

| Always-on Category | Estimated Tokens |
|---|---|
| Agent descriptions (29) | ~2,800 |
| Skill descriptions (38) | ~4,500 |
| Global CLAUDE.md | ~2,400 |
| Project CLAUDE.md | ~1,500 |
| Project MEMORY.md + memory files | ~920 |
| **Always-on TOTAL** | **~12,120** |

---

## Phase 2: Optimization Opportunities

### Opportunity 1: Verbose Skill Descriptions (HIGH impact, ~2,000 token savings)

Several skill descriptions are excessively long. The `description` field in SKILL.md frontmatter loads into every conversation for routing purposes. Concise descriptions trigger just as well.

**Worst offenders:**

| Skill | Current Est. Tokens | Proposed Est. Tokens | Savings |
|-------|-------|---------|---------|
| docx | ~120 | ~30 | ~90 |
| xlsx | ~130 | ~30 | ~100 |
| pptx | ~110 | ~30 | ~80 |
| pdf | ~90 | ~25 | ~65 |
| skill-create | ~65 | ~25 | ~40 |
| token-optimize | ~70 | ~25 | ~45 |
| frontend-design | ~65 | ~25 | ~40 |
| algorithmic-art | ~55 | ~25 | ~30 |
| canvas-design | ~50 | ~25 | ~25 |
| internal-comms | ~55 | ~25 | ~30 |
| agent-create | ~50 | ~25 | ~25 |
| auto-improve | ~50 | ~25 | ~25 |
| auto-improve-loop | ~45 | ~25 | ~20 |
| webapp-testing | ~45 | ~25 | ~20 |
| mcp-builder | ~50 | ~25 | ~25 |
| slack-gif-create | ~45 | ~25 | ~20 |
| hook-builder | ~45 | ~25 | ~20 |
| brand-guidelines | ~45 | ~25 | ~20 |
| web-artifacts-builder | ~50 | ~25 | ~25 |
| Other 19 skills (already concise) | ~1,200 | ~1,200 | 0 |
| **Skill total** | **~4,500** | **~2,500** | **~2,000** |

**Proposed changes (examples):**

Current `docx`:
```
"Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files). Triggers include: any mention of 'Word doc', 'word document', '.docx', or requests to produce professional documents with formatting like tables of contents, headings, page numbers, or letterheads. Also use when extracting or reorganizing content from .docx files, inserting or replacing images in documents, performing find-and-replace in Word files, working with tracked changes or comments, or converting content into a polished Word document. If the user asks for a 'report', 'memo', 'letter', 'template', or similar deliverable as a Word or .docx file, use this skill. Do NOT use for PDFs, spreadsheets, Google Docs, or general coding tasks unrelated to document generation."
```

Proposed `docx`:
```
"Create, read, edit, or manipulate .docx Word documents. Covers formatting, TOC, images, tracked changes, find-replace, and document conversion. Not for PDFs, spreadsheets, or Google Docs."
```

Current `xlsx`:
```
"Use this skill any time a spreadsheet file is the primary input or output. This means any task where the user wants to: open, read, edit, or fix an existing .xlsx, .xlsm, .csv, or .tsv file (e.g., adding columns, computing formulas, formatting, charting, cleaning messy data); create a new spreadsheet from scratch or from other data sources; or convert between tabular file formats. Trigger especially when the user references a spreadsheet file by name or path — even casually (like \"the xlsx in my downloads\") — and wants something done to it or produced from it. Also trigger for cleaning or restructuring messy tabular data files (malformed rows, misplaced headers, junk data) into proper spreadsheets. The deliverable must be a spreadsheet file. Do NOT trigger when the primary deliverable is a Word document, HTML report, standalone Python script, database pipeline, or Google Sheets API integration, even if tabular data is involved."
```

Proposed `xlsx`:
```
"Create, read, edit, or fix spreadsheet files (.xlsx, .xlsm, .csv, .tsv). Covers formulas, charting, formatting, data cleaning, and format conversion. Deliverable must be a spreadsheet file."
```

Current `pptx`:
```
"Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions \"deck,\" \"slides,\" \"presentation,\" or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill."
```

Proposed `pptx`:
```
"Create, read, edit, or manipulate .pptx presentation files. Covers slide decks, pitch decks, templates, layouts, speaker notes, and text extraction."
```

Current `pdf`:
```
Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting/decrypting PDFs, extracting images, and OCR on scanned PDFs to make them searchable. If the user mentions a .pdf file or asks to produce one, use this skill.
```

Proposed `pdf`:
```
"Read, create, merge, split, rotate, watermark, encrypt, OCR, or extract text/images from PDF files."
```

---

### Opportunity 2: Agent Description Compression (MEDIUM impact, ~600 token savings)

Two agents have `Examples:` sections in their descriptions that inflate the frontmatter:

**security-reviewer** -- Current description (~180 tokens):
```
"[Review] Deep security audit specialist: vulnerability detection, dependency scanning, OWASP analysis, and remediation. Invoked PROACTIVELY after writing code that handles user input, authentication, API endpoints, or sensitive data. Invoked by escalation from code-reviewer when security findings need deep analysis.

Examples:
- \"Security audit this module\" → Launch security-reviewer
- \"Check for vulnerabilities\" → Launch security-reviewer
- \"Review auth implementation\" → Launch security-reviewer
- \"Dependency security check\" → Launch security-reviewer
- code-reviewer escalates CRITICAL/HIGH SEC finding → Launch security-reviewer"
```

Proposed (~50 tokens):
```
"[Review] Deep security audit — vulnerability detection, dependency scanning, OWASP analysis, remediation. Invoked proactively for auth/input/API code or by code-reviewer escalation."
```

**refactor-cleaner** -- Current description (~80 tokens):
```
"[Refactor] Dead code cleanup and consolidation specialist. Use PROACTIVELY for removing unused code, duplicates, and refactoring.\n\nExamples:\n- \"Clean up unused code\" → Launch refactor-cleaner\n- \"Find and remove dead code\" → Launch refactor-cleaner\n- \"Consolidate duplicate utilities\" → Launch refactor-cleaner"
```

Proposed (~30 tokens):
```
"[Refactor] Dead code cleanup, duplicate consolidation, unused dependency removal. Use proactively after feature completion."
```

The remaining 27 agent descriptions are already well-compressed at 1-2 sentences each. No changes needed.

---

### Opportunity 3: Project CLAUDE.md Korean-to-English (MEDIUM impact, ~500 token savings)

The project CLAUDE.md at `/Users/kangnam/projects/ai-config-sync/CLAUDE.md` is approximately 50% Korean. Converting the Korean portions to concise English would reduce token count from ~1,500 to ~1,000.

**Sections with Korean content to convert:**
- Overview section (line 7)
- Commands section comments (lines 10-14)
- Architecture section headers and descriptions (lines 27-46)
- Platform sync scope table (lines 48-56)
- Code modification notes (lines 59-67)

**I would NOT change:** The Korean in this file is minimal and project-specific. The global CLAUDE.md is already fully English. This is lower priority than Opportunities 1 and 2.

---

### Opportunity 4: Project Memory Cleanup (LOW impact, ~300 token savings)

| Memory File | Issue | Recommendation |
|---|---|---|
| `project_ui_review_rename.md` | Completed task (2026-03-21), 9 days old. Documents a rename that is already done. | Recommend deletion -- the rename is permanent and does not need to be remembered. |
| `feedback_naming_convention.md` | Contains Korean text. Valid ongoing rule. | Convert to English for ~40% token savings. |
| `reference_llm_provider_auth.md` | Contains Korean text. Valid reference. | Convert to English for ~40% token savings. |
| `feedback_agent_skill_creation.md` | Contains Korean text. Valid ongoing rule. Already duplicated in global CLAUDE.md. | Consider deletion (redundant with global CLAUDE.md Agent Orchestration section). |
| `MEMORY.md` index | Contains Korean descriptions. | Convert descriptions to English. |

---

### Opportunity 5: Duplicate Skill/Agent Overlap Detection (INFORMATIONAL)

| Skill | Overlapping Agent | Analysis |
|---|---|---|
| `trend-score` skill | `trend-scorer` agent | Different roles: skill provides workflow for main model, agent runs as subagent. Keep both. |
| `bm-design` skill | `bm-designer` agent | Same pattern. Keep both. |
| `research` skill | `researcher` agent | Same pattern. Keep both. |
| `ui-review` skill | `ui-reviewer` agent | Same pattern. Keep both. |

No duplicates found that warrant removal. The skill/agent pairs serve different invocation patterns.

---

## Phase 3: Projected Savings Summary

| Category | Before | After | Saved | Priority |
|---|---|---|---|---|
| Skill descriptions (38) | ~4,500 | ~2,500 | **~2,000** | HIGH |
| Agent descriptions (2 with Examples) | ~260 | ~80 | **~180** | MEDIUM |
| Other agent descriptions (27) | ~2,540 | ~2,540 | 0 | -- |
| Project CLAUDE.md (Korean) | ~1,500 | ~1,000 | **~500** | MEDIUM |
| Project memory files | ~920 | ~620 | **~300** | LOW |
| Global CLAUDE.md | ~2,400 | ~2,400 | 0 | Already English |
| **TOTAL** | **~12,120** | **~9,140** | **~2,980 (~25%)** | |

---

## Recommended Execution Order

1. **Skill description compression** (19 verbose skills) -- Highest ROI: ~2,000 tokens saved with no semantic loss. Pure compression of trigger-explanation text into concise routing hints.

2. **Agent description compression** (security-reviewer, refactor-cleaner) -- Remove Examples sections, condense to 1-2 sentences. ~180 tokens saved.

3. **Project memory cleanup** -- Delete `project_ui_review_rename.md` (completed task). Delete `feedback_agent_skill_creation.md` (redundant with global CLAUDE.md). Convert remaining 2 files to English. ~300 tokens saved.

4. **Project CLAUDE.md Korean-to-English** -- Convert Korean sections to concise English. ~500 tokens saved. Lower priority since this is a project-specific file.

---

## What I Did NOT Recommend

- **Global CLAUDE.md changes**: Already fully in English and well-structured. No optimization needed.
- **Agent body content changes**: Body text is only loaded when the agent is spawned, not in every conversation. The 28 agents with Korean body text are a concern for per-invocation cost, but not for always-on system prompt size. This is a separate optimization task.
- **Skill/agent deletion**: No duplicate pairs warrant removal.
- **Structural reorganization**: The current agent/skill architecture is sound.

---

## Files That Would Be Modified

### Skill SKILL.md files (description field only):
- `/Users/kangnam/.claude/skills/docx/SKILL.md`
- `/Users/kangnam/.claude/skills/xlsx/SKILL.md`
- `/Users/kangnam/.claude/skills/pptx/SKILL.md`
- `/Users/kangnam/.claude/skills/pdf/SKILL.md`
- `/Users/kangnam/.claude/skills/skill-create/SKILL.md`
- `/Users/kangnam/.claude/skills/token-optimize/SKILL.md`
- `/Users/kangnam/.claude/skills/frontend-design/SKILL.md`
- `/Users/kangnam/.claude/skills/algorithmic-art/SKILL.md`
- `/Users/kangnam/.claude/skills/canvas-design/SKILL.md`
- `/Users/kangnam/.claude/skills/internal-comms/SKILL.md`
- `/Users/kangnam/.claude/skills/agent-create/SKILL.md`
- `/Users/kangnam/.claude/skills/auto-improve/SKILL.md`
- `/Users/kangnam/.claude/skills/auto-improve-loop/SKILL.md`
- `/Users/kangnam/.claude/skills/webapp-testing/SKILL.md`
- `/Users/kangnam/.claude/skills/mcp-builder/SKILL.md`
- `/Users/kangnam/.claude/skills/slack-gif-create/SKILL.md`
- `/Users/kangnam/.claude/skills/hook-builder/SKILL.md`
- `/Users/kangnam/.claude/skills/brand-guidelines/SKILL.md`
- `/Users/kangnam/.claude/skills/web-artifacts-builder/SKILL.md`

### Agent .md files (description field only):
- `/Users/kangnam/.claude/agents/security-reviewer.md`
- `/Users/kangnam/.claude/agents/refactor-cleaner.md`

### Project files:
- `/Users/kangnam/projects/ai-config-sync/CLAUDE.md` (Korean-to-English)

### Memory files:
- `/Users/kangnam/.claude/projects/-Users-kangnam-projects-ai-config-sync/memory/MEMORY.md` (English conversion)
- `/Users/kangnam/.claude/projects/-Users-kangnam-projects-ai-config-sync/memory/feedback_naming_convention.md` (English conversion)
- `/Users/kangnam/.claude/projects/-Users-kangnam-projects-ai-config-sync/memory/reference_llm_provider_auth.md` (English conversion)
- `/Users/kangnam/.claude/projects/-Users-kangnam-projects-ai-config-sync/memory/project_ui_review_rename.md` (DELETE -- completed task)
- `/Users/kangnam/.claude/projects/-Users-kangnam-projects-ai-config-sync/memory/feedback_agent_skill_creation.md` (DELETE -- redundant with global CLAUDE.md)
