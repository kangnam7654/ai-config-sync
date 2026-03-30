---
name: claude-code-hud audit and improvement plan
description: Pure-bash Claude Code HUD (4 scripts, 515 LOC) full 5-area audit completed 2026-03-30. Overall 5.37/10. Gate verdict PARTIAL. 24 improvement items across P0/P1/P2 scoped for implementation.
type: project
---

Full audit for claude-code-hud at /Users/kangnam/projects/claude-code-hud/, scored 2026-03-30.

**Scores**: Code Quality 6.15, Security 7.20, Architecture 8.20 (PASS), Test Coverage 0.40, Repo Health 7.10. Weighted overall: 5.37.

**Why:** Auto-improve pipeline audit phase. Architecture is sound (no rewrite needed), but safety/correctness, testability, and repo health have critical gaps.

**How to apply:**
- Audit report at docs/llm/audit-report.md defines 24 items: 7 P0 (safety), 7 P1 (testability+tests), 10 P2 (repo health)
- P0: set -e in log-session.sh, stdin validation, jq --arg injection fix, move cache from /tmp to ~/.claude/, numeric validation before arithmetic/bc, curl --fail for TLS safety
- P1: extract pure functions to lib/hud-utils.sh, add source-guard, BATS test framework, 27 test cases (14 format + 7 error + 6 timestamp)
- P2: GitHub Actions CI (shellcheck+bats), LICENSE, .shellcheckrc, .editorconfig, mktemp trap, readlink -f portability, SC2155 fixes
- Target: weighted overall 7.8+ after all phases
- Constraint: pure bash, no new runtime deps, backward-compatible with existing ~/.claude/settings.json
