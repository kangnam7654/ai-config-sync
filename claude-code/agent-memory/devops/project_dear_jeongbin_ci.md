---
name: dear-jeongbin CI setup
description: GitHub Actions CI pipeline for dear-jeongbin — SSH keys required, known test failures, job structure
type: project
---

CI pipeline added at `.github/workflows/test.yml` (318 LOC) on 2026-04-27.

4 jobs: `rust` | `frontend` | `e2e-mock` | `e2e-real` (last depends on first two).

**Why:** Private repo with 2000 free Actions minutes/month. ubuntu-latest only (macOS is 10x cost).

**Critical blockers before CI goes fully green:**
1. `SSH_PRIVATE_KEY` secret must be added to dear-jeongbin repo settings. The key's public half must be a read-only deploy key on BOTH `kangnam7654/canvas-sdk` AND `kangnam7654/llm-router`. Without this, the `rust` and `e2e-real` jobs fail at "Load SSH key" step.
2. `canvas-sdk` is a local path dep (`../../canvas-sdk/`) — CI clones it as a sibling via SSH.
3. `llm-router` is a git SSH dep (tag v0.4.1) — also requires SSH access.

**Known pre-existing test failures (continue-on-error):**
- Rust: 7 tests (jd_analysis content + tera_media)
- Vitest: 21 tests (sidebar, action-cards, settings-page etc.)
- E2E mock + E2E real: hard failures (no continue-on-error)

**vitest.config.ts fix also committed:** Added `include: ["tests/unit/**/*.{test,spec}.{ts,tsx}"]` + `exclude: ["tests/e2e/**"]` to prevent Playwright specs from being picked up by Vitest.

**How to apply:** When working on CI, tests, or Rust deps — check SSH_PRIVATE_KEY secret is configured first. Branch protection setup is manual (Settings → Branches → require: rust, frontend, e2e-mock, e2e-real).
