# Claude Code System Prompt Token Consumption Report

**Project:** ai-config-sync (`/Users/kangnam/projects/ai-config-sync`)
**Date:** 2026-03-30
**Tokenizer:** cl100k_base approximation (Claude's actual tokenizer may differ by ~5-15%)

---

## 1. User-Controlled Files (Direct Measurement)

Token estimates below use the standard approximation: ~1 token per 4 chars for English/code, ~1 token per 2-3 chars for Korean text. Counts are derived from the line counts and content observed via the Read tool.

| File | Lines | Est. Characters | Est. Tokens | Share |
|------|------:|----------------:|------------:|------:|
| **Global CLAUDE.md** (`~/.claude/CLAUDE.md`) | 164 | ~7,800 | ~2,400 | 37.5% |
| **Project CLAUDE.md** (`ai-config-sync/CLAUDE.md`) | 68 | ~3,400 | ~1,200 | 18.8% |
| Memory: `feedback_naming_convention.md` | 20 | ~1,300 | ~450 | 7.0% |
| Memory: `project_ui_review_rename.md` | 23 | ~1,400 | ~480 | 7.5% |
| Memory: `feedback_agent_skill_creation.md` | 11 | ~600 | ~200 | 3.1% |
| Memory: `reference_llm_provider_auth.md` | 10 | ~500 | ~180 | 2.8% |
| Memory: `MEMORY.md` (index) | 7 | ~500 | ~150 | 2.3% |
| **User-controlled subtotal** | **303** | **~15,500** | **~5,060** | **~79%** |

### Category Breakdown (user-controlled only)

| Category | Est. Tokens | Share of User Files |
|----------|------------:|-------------------:|
| CLAUDE.md files (global + project) | ~3,600 | 71% |
| Memory files (index + 4 entries) | ~1,460 | 29% |

---

## 2. System-Injected Context (Estimates)

These are injected by Claude Code itself and not directly controlled by user files, but they still consume context budget every conversation turn.

| Component | Est. Tokens | Notes |
|-----------|------------:|-------|
| Skill descriptions (49 skills in system-reminder) | ~2,500 | Each skill has 1-3 line description. 49 skills listed. |
| Deferred tools list (22 tools) | ~300 | MCP tools, WebFetch, NotebookEdit, etc. |
| Claude Code built-in system prompt | ~8,000-12,000 | Core instructions, safety rules, commit protocol, PR protocol, etc. |
| Tool definitions (7 built-in tools: Bash, Edit, Glob, Grep, Read, Write, Skill, ToolSearch) | ~3,000 | JSON schema definitions for each tool |
| Date, git status, env info | ~200 | Injected per conversation |
| **System-injected subtotal** | **~14,000-18,000** | |

---

## 3. Total Estimated System Prompt Size

| Category | Est. Tokens |
|----------|------------:|
| User-controlled files | ~5,060 |
| System-injected context | ~14,000-18,000 |
| **Total per conversation start** | **~19,000-23,000** |

---

## 4. Key Findings

### Top Token Consumers (user-controlled)

1. **Global CLAUDE.md (~2,400 tokens, 37.5%)** -- The single largest user-controlled file. Contains NEVER rules, agent orchestration, design-first development, testing, refactoring, memory extension, and dev environment sections. Significant Korean+English mixed content increases token cost.

2. **Project CLAUDE.md (~1,200 tokens, 18.8%)** -- Architecture documentation for the sync project. Loaded only in this project context.

3. **Memory files (~1,460 tokens, 23%)** -- Four memory entries plus the index. The `feedback_naming_convention.md` and `project_ui_review_rename.md` are the largest memory entries.

### System-Level Observations

- **49 skill descriptions** are injected into every conversation via system-reminder. This is a substantial ~2,500 token cost that grows with each new skill.
- **22 deferred tools** (MCP integrations for Google Calendar, Stitch, etc.) add ~300 tokens just for the listing.
- The built-in Claude Code system prompt (commit protocol, PR protocol, safety rules, tool usage instructions) is estimated at 8,000-12,000 tokens -- the single largest component.

### Ratio

Approximately **25-30% of the total system prompt is user-controlled**, while **70-75% is Claude Code infrastructure**. The user's CLAUDE.md and memory files are a relatively modest portion of the total context budget.

---

## 5. Optimization Opportunities

| Priority | Opportunity | Est. Savings |
|----------|------------|-------------:|
| Low | Consolidate/prune completed memory entries (e.g., `project_ui_review_rename.md` is marked complete) | ~480 tokens |
| Low | Global CLAUDE.md has some redundancy between Korean and English versions (the original Korean instructions vs the English rendering seen at runtime) | ~200-400 tokens |
| Medium | Skill descriptions (49 skills) -- disabling unused skills would reduce system-reminder size | ~50 tokens/skill |
| N/A | Built-in system prompt and tool definitions are not user-controllable | -- |

**Note:** At ~5,000 user-controlled tokens out of a 200K (or 1M with Opus) context window, optimization of user files has minimal practical impact on available context. The main benefit would be reducing per-turn input costs if cost is a concern, or freeing marginal space for very long conversations.
