# Business Docs Reference

Applies when request involves: spec, report, proposal, RFC, PRD, meeting notes, postmortem, ADR, analysis.

## Scope

### IN scope
- **Specs**: PRD (Product Requirements Document), technical spec
- **Reports**: analysis, status, postmortem
- **Proposals**: RFC (Request for Comments), technical proposal
- **Meeting notes**: standup, sprint planning, retro, design review, decision meetings
- **ADRs**: Architecture Decision Records
- **Template creation**: Reusable templates for business document types

### OUT of scope
- Structured data files (CSV, JSON, YAML) → load `data-files.md` reference
- Human-readable documentation → load `human-docs.md` reference
- LLM-facing documents → load `llm-docs.md` reference

## Rules

### ALWAYS

1. ALWAYS ask the user for the target audience (engineering team, executive, external stakeholder) before writing a business document — IF the user does not specify, default to "engineering team"
2. ALWAYS include a "Decision" or "Action Items" section in business documents — every document MUST end with a clear next step

### NEVER

1. NEVER write a business document without the required sections defined in the templates below
2. NEVER use vague language in action items — every action item MUST have an owner (role or name) and a deadline (date or "by next [meeting/sprint/review]")

## Requirements Gathering

1. Identify the document type (PRD, technical spec, RFC, report, proposal, postmortem, ADR, meeting notes)
2. Identify the audience (engineering team, executive, external stakeholder)
3. Identify the context (project name, relevant code/data, prior decisions)
4. IF the user does not specify audience, state: "Defaulting to engineering team audience."

## Production Workflow

1. Select the matching template below
2. Fill every required section — do not leave placeholder text
3. Ensure every action item has an owner and deadline
4. Write the file to the path specified by the user, or propose a path following the pattern `docs/{type}/{descriptive-name}.md`

## Output Templates

### PRD (Product Requirements Document)

```markdown
# PRD: {Feature/Product Name}

**Author**: {name or role}
**Date**: {ISO 8601 date}
**Status**: Draft | Under Review | Approved | Superseded
**Stakeholders**: {comma-separated list of roles or names}

## Problem Statement

{2-5 sentences. What problem exists? Who is affected? What is the impact?}

## Goals

| # | Goal | Success Metric | Target Value |
|---|------|---------------|--------------|
| 1 | {goal} | {metric} | {number or threshold} |

## Non-Goals

- {Explicitly excluded item 1}
- {Explicitly excluded item 2}

## Requirements

### Functional Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|----|------------|----------|-------------------|
| FR-01 | {requirement} | P0/P1/P2 | {testable condition} |

### Non-Functional Requirements

| ID | Requirement | Target |
|----|------------|--------|
| NFR-01 | {requirement} | {measurable target} |

## User Stories

| # | As a... | I want to... | So that... |
|---|---------|-------------|-----------|
| 1 | {role} | {action} | {benefit} |

## Design Considerations

{Technical constraints, dependencies, risks. Reference architecture docs if they exist.}

## Timeline

| Milestone | Date | Deliverable |
|-----------|------|-------------|
| {milestone} | {date} | {deliverable} |

## Decision

{Current decision status and rationale. IF draft, state: "Pending stakeholder review."}

## Action Items

| # | Action | Owner | Deadline |
|---|--------|-------|----------|
| 1 | {action} | {owner} | {date} |
```

### Technical Spec

```markdown
# Technical Spec: {Feature Name}

**Author**: {name or role}
**Date**: {ISO 8601 date}
**Status**: Draft | Under Review | Approved | Superseded
**PRD Reference**: {link or "N/A"}

## Overview

{1-3 sentences. What is being built and why.}

## Architecture

{Component diagram description. Reference existing architecture docs. Describe new components only.}

## Data Model

{Tables, schemas, or data structures. Use code blocks for schema definitions.}

## API Design

| Method | Path | Request Body | Response | Error Codes |
|--------|------|-------------|----------|-------------|
| {HTTP method} | {path} | {schema ref} | {schema ref} | {codes} |

## Implementation Plan

| Phase | Scope | Estimated Effort |
|-------|-------|-----------------|
| 1 | {scope} | {days/weeks} |

## Security Considerations

- {Consideration 1 with mitigation}

## Testing Strategy

| Test Type | Scope | Coverage Target |
|-----------|-------|----------------|
| Unit | {scope} | {percentage} |
| Integration | {scope} | {percentage} |
| E2E | {scope} | {percentage} |

## Rollback Plan

{How to revert if deployment fails. Specific steps.}

## Decision

{Current decision status and rationale.}

## Action Items

| # | Action | Owner | Deadline |
|---|--------|-------|----------|
| 1 | {action} | {owner} | {date} |
```

### RFC (Request for Comments)

```markdown
# RFC: {Title}

**Author**: {name or role}
**Date**: {ISO 8601 date}
**Status**: Draft | Discussion | Accepted | Rejected | Superseded
**Discussion Deadline**: {ISO 8601 date}

## Summary

{3-5 sentences. What is being proposed and why.}

## Motivation

{Why is the current state insufficient? What triggered this RFC?}

## Proposal

{Detailed description of the proposed change. Code examples where applicable.}

## Alternatives Considered

| # | Alternative | Pros | Cons | Why Not Chosen |
|---|------------|------|------|----------------|
| 1 | {alternative} | {pros} | {cons} | {reason} |

## Migration Plan

{How to transition from current state to proposed state. Breaking changes listed explicitly.}

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| {risk} | Low/Medium/High | Low/Medium/High | {mitigation} |

## Open Questions

| # | Question | Status | Resolution |
|---|----------|--------|-----------|
| 1 | {question} | Open/Resolved | {answer if resolved} |

## Decision

{Current decision status. IF discussion ongoing, state: "Accepting comments until {deadline}."}

## Action Items

| # | Action | Owner | Deadline |
|---|--------|-------|----------|
| 1 | {action} | {owner} | {date} |
```

### Postmortem Report

```markdown
# Postmortem: {Incident Title}

**Date of Incident**: {ISO 8601 date}
**Author**: {name or role}
**Severity**: SEV-1 | SEV-2 | SEV-3 | SEV-4
**Duration**: {start time} — {end time} ({total duration})

## Summary

{2-3 sentences. What happened, how long it lasted, what was affected.}

## Impact

| Metric | Value |
|--------|-------|
| Users affected | {number or percentage} |
| Revenue impact | {amount or "None"} |
| Data loss | {description or "None"} |
| SLA breach | {yes/no — which SLA} |

## Timeline

| Time (UTC) | Event |
|-----------|-------|
| {HH:MM} | {event description} |

## Root Cause

{Technical explanation. Reference specific code, configs, or infrastructure. No blame on individuals.}

## Contributing Factors

- {Factor 1}
- {Factor 2}

## What Went Well

- {Positive outcome 1}

## What Went Wrong

- {Failure 1}

## Action Items

| # | Action | Type | Owner | Deadline | Status |
|---|--------|------|-------|----------|--------|
| 1 | {action} | Prevent/Detect/Mitigate | {owner} | {date} | Open |
```

### Analysis Report

```markdown
# Analysis: {Topic}

**Author**: {name or role}
**Date**: {ISO 8601 date}
**Requested by**: {name or role}

## Executive Summary

{3-5 sentences. Key finding, methodology, recommendation.}

## Methodology

{Data sources, tools used, time period, sample size.}

## Findings

### Finding 1: {Title}

{Description with supporting data. Include tables or references to data files.}

### Finding 2: {Title}

{Description with supporting data.}

## Recommendations

| # | Recommendation | Expected Impact | Effort | Priority |
|---|---------------|-----------------|--------|----------|
| 1 | {recommendation} | {impact} | Low/Medium/High | P0/P1/P2 |

## Limitations

- {Limitation 1 — how it affects conclusions}

## Decision

{Current decision status or "Awaiting review."}

## Action Items

| # | Action | Owner | Deadline |
|---|--------|-------|----------|
| 1 | {action} | {owner} | {date} |
```

### Meeting Notes

```markdown
# Meeting: {Topic}

**Date**: {ISO 8601 date}
**Attendees**: {comma-separated list}
**Duration**: {minutes} min
**Meeting Type**: Standup | Sprint Planning | Retro | Design Review | Decision Meeting | Ad-hoc

## Agenda

1. {Topic 1}
2. {Topic 2}

## Notes

### {Topic 1}

{Key points discussed. Use bullet points. Attribute statements to speakers: "[Name]: ..."}

### {Topic 2}

{Key points discussed.}

## Decisions Made

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | {decision} | {why} |

## Action Items

| # | Action | Owner | Deadline |
|---|--------|-------|----------|
| 1 | {action} | {owner} | {date} |

## Next Meeting

**Date**: {date or "TBD"}
**Agenda items carried over**: {list or "None"}
```

### ADR (Architecture Decision Record)

```markdown
# ADR-{NNN}: {Title}

**Date**: {ISO 8601 date}
**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-{NNN}
**Deciders**: {comma-separated list}

## Context

{What is the issue? What forces are at play? 3-5 sentences.}

## Decision

{What is the change being proposed or decided?}

## Consequences

### Positive

- {Consequence 1}

### Negative

- {Consequence 1 — with mitigation if applicable}

### Neutral

- {Consequence 1}

## Alternatives Considered

| # | Alternative | Why Not Chosen |
|---|------------|----------------|
| 1 | {alternative} | {reason} |
```

## Edge Cases

| Situation | Resolution |
|-----------|------------|
| Business document request lacks sufficient context | Ask up to 3 clarifying questions, each with a default value. IF the user says "just write it", proceed with all defaults and mark assumptions in a "## Assumptions" section at the end of the document. |
| User requests a document type not in the templates (e.g., "write a user guide") | Respond: "User guides are human-readable documentation — use the Human Docs mode for this task." Load `human-docs.md` reference and proceed. |
