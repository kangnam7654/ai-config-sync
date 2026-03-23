# Test Plan: service-dev Skill

**Source**: `docs/service-dev/design.md`
**Generated**: 2026-03-23
**Implementation Status**: 27 of 31 requirements implemented

## Summary

| Type | Count | P0 | P1 | P2 |
|------|-------|----|----|----|
| Unit | 12 | 2 | 7 | 3 |
| Integration | 14 | 3 | 8 | 3 |
| E2E | 5 | 1 | 3 | 1 |
| **Total** | **31** | **6** | **18** | **7** |

## Test Cases

### Purpose (Section 1)

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 1 | verify_six_phases_have_entry_and_exit_conditions | unit | P0 | SKILL.md Phase definitions | All 6 Phases (0-5) have at least one gate condition defined; no Phase transition lacks a condition | Implemented |
| 2 | verify_phases_delegate_to_existing_agents_not_redefine_critic_loops | integration | P1 | SKILL.md Phase 1,3,5 internal logic | Phase 1 calls planner + plan-critic, Phase 3 calls doc-writer + doc-critic (LLM mode), Phase 5 calls doc-writer-human + doc-critic (HUMAN mode); no Critic loop parameters (max iterations, pass threshold) are redefined in SKILL.md | Implemented |
| 3 | verify_artifact_delivery_path_between_all_phases | integration | P1 | Phase 0-5 artifact definitions | Phase 0 output (4 items) flows to Phase 1 input; Phase 1 output flows to Phase 2/3; Phase 3 spec.md flows to Phase 4; Phase 4 code/tests flow to Phase 5. No missing handoff. | Implemented |

### Architecture (Section 3)

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 4 | execute_phase0_via_idea_forge_path | integration | P1 | User triggers service-dev with idea-forge artifacts available | idea-forge skill is invoked; its output (service overview, features, target, BM) is captured and passed to Phase 1 | Implemented |
| 5 | execute_phase0_via_direct_input_path | integration | P1 | User provides idea directly without idea-forge | Skill collects 4 required artifacts (service overview, features, target users, BM summary) from user input and structures them | Implemented |
| 6 | skip_phase2_when_design_not_requested | integration | P1 | User indicates design is not needed at Phase 1 gate | Phase 2 is skipped entirely; flow proceeds from Phase 1 directly to Phase 3; Phase 3 receives only Phase 1 artifacts | Implemented |
| 7 | execute_phase2_when_design_requested | integration | P1 | User requests design at Phase 1 gate + Figma MCP available | Phase 2 executes wireframe then hi-fi; each requires user approval before proceeding | Implemented |
| 8 | skip_phase2_when_figma_mcp_unavailable | unit | P1 | Figma MCP is not configured in environment | User is notified Figma MCP is unavailable; Phase 2 is skipped; flow proceeds to Phase 3 | Implemented |
| 9 | gate_based_transition_blocks_on_failure | unit | P0 | Plan-Critic returns REJECT at Phase 1 gate | Phase does not advance to Phase 2 or 3; skill stays in Phase 1 and re-runs Planner-Critic loop | Implemented |
| 10 | phase4_module_cycle_executes_four_steps_in_order | integration | P1 | spec.md with 2+ modules defined | For each module: dev -> review -> refactor -> test executed sequentially; git commit after each step; next module only starts after current module completes all 4 steps | Implemented |

### Data Flow (Section 5)

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 11 | phase0_output_contains_four_required_artifacts | unit | P1 | Phase 0 completion | Output contains exactly: service overview, feature list, target users, BM summary. Missing any one blocks Phase 1 entry. | Implemented |
| 12 | phase1_output_saved_to_correct_path | unit | P1 | Phase 1 completion with service-name="taskflow" | `docs/taskflow/design.md` created; `docs/taskflow/architecture.mmd` created; `docs/taskflow/architecture.png` created | Implemented |
| 13 | phase3_receives_phase1_and_phase2_artifacts_when_both_exist | integration | P1 | Phase 2 completed with Figma designs | Phase 3 Writer receives: architecture docs (Phase 1) AND Figma design references (Phase 2) as input context | Implemented |
| 14 | phase3_receives_only_phase1_artifacts_when_phase2_skipped | integration | P1 | Phase 2 was skipped | Phase 3 Writer receives only Phase 1 architecture/module artifacts; no Phase 2 references are included | Implemented |
| 15 | phase4_references_spec_md_during_build | integration | P0 | spec.md exists at `docs/{service-name}/spec.md` | Phase 4 dev step reads spec.md to determine module requirements; implementation follows spec.md API schema and data model definitions | Implemented |
| 16 | phase5_receives_phase4_code_and_tests | integration | P1 | Phase 4 completed with src/ and tests/ | Phase 5 doc-writer has access to completed source code and test results for documentation | Implemented |

### API Design (Section 7)

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 17 | skill_does_not_expose_external_api | unit | P2 | SKILL.md definition | No REST API endpoints, no externally callable function signatures are defined. All interaction is via Claude Code skill invocation. | Implemented |

### File Structure (Section 8)

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 18 | skill_md_exists_at_correct_path | unit | P0 | File system check | `~/.claude/skills/service-dev/SKILL.md` exists and contains valid frontmatter (name: service-dev) | Implemented |
| 19 | phase1_creates_design_artifacts_in_docs_directory | e2e | P1 | Full Phase 0->1 execution with service-name="myapp" | Files created: `docs/myapp/design.md`, `docs/myapp/architecture.mmd`, `docs/myapp/architecture.png` | Not Yet Implemented |
| 20 | phase3_creates_spec_in_docs_directory | e2e | P1 | Full Phase 0->3 execution | File created: `docs/{service-name}/spec.md` with required sections (module requirements, API schema, data model, error rules, coding conventions) | Not Yet Implemented |
| 21 | phase4_creates_src_and_tests_directories | e2e | P1 | Full Phase 0->4 execution | Directories created: `src/` (with module subdirectories) and `tests/` (with unit test files) | Not Yet Implemented |
| 22 | phase5_creates_readme | e2e | P2 | Full Phase 0->5 execution | `README.md` created at project root with sections: project intro, prerequisites, quick start, API overview, deployment | Not Yet Implemented |
| 23 | artifacts_never_saved_outside_docs_service_name | unit | P1 | Any Phase execution | No design.md, spec.md, architecture.mmd, or architecture.png files are created outside `docs/{service-name}/` | Implemented |

### Phase Transition Conditions (Section 6)

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 24 | gate_phase0_to_phase1_requires_user_approval | integration | P0 | Phase 0 artifacts ready, user has not approved | Skill waits for explicit user approval; does not auto-advance to Phase 1 | Implemented |
| 25 | gate_phase1_to_phase3_requires_plan_critic_pass_and_user_approval | integration | P0 | Plan-Critic score below threshold | Skill does not advance; re-runs Planner with feedback; max 5 iterations | Implemented |
| 26 | gate_phase3_to_phase4_requires_doc_critic_llm_pass | integration | P1 | Doc-Critic LLM mode returns REJECT | Skill stays in Phase 3; Writer revises spec.md; max 5 iterations before escalating to user | Implemented |
| 27 | gate_phase4_to_phase5_requires_all_tests_pass_and_coverage_80 | unit | P0 | Unit tests pass but coverage = 75% | Phase 4 does not advance to Phase 5; reports top 3 lowest-coverage modules to user | Implemented |
| 28 | gate_phase5_to_complete_requires_doc_critic_human_pass | integration | P1 | Doc-Critic HUMAN mode, user rejects document | Skill stays in Phase 5; doc-writer revises; max 5 iterations | Implemented |

### Decision Rationale (Section 9)

| # | Scenario | Type | Priority | Input | Expected Result | Impl Status |
|---|----------|------|----------|-------|----------------|-------------|
| 29 | phase4_does_not_use_monolithic_build_then_review_approach | unit | P2 | Phase 4 execution with 3 modules | Modules are NOT all built first then all reviewed. Each module completes its full dev->review->refactor->test cycle before the next module starts. | Implemented |
| 30 | skill_does_not_redefine_critic_loop_parameters | unit | P2 | SKILL.md content | SKILL.md does not contain max iteration counts, pass score thresholds, or PASS/REJECT criteria for Critic loops. These are delegated to global CLAUDE.md. | Implemented |
| 31 | single_phase_approach_is_not_used | e2e | P2 | Full service-dev execution | Execution is divided into discrete Phases with gates between them; no single-pass execution from ideation to documentation | Implemented |

## Gaps

| # | Gap Description | Recommendation | Suggested Type | Suggested Priority |
|---|----------------|----------------|---------------|-------------------|
| 1 | Design doc Section 4 (Phase 3) references `prompt-writer` agent, but no `prompt-writer.md` exists in `~/.claude/agents/`. SKILL.md uses `doc-writer-llm` instead. | Clarify discrepancy: either add prompt-writer agent or update design doc to reference doc-writer-llm. Add test to verify the correct agent is invoked in Phase 3. | integration | P1 |
| 2 | No error-path test for idea-forge failure scenario (CSO REJECT 5 times). SKILL.md defines this edge case but no test verifies the fallback to user-provided idea. | Add test: `phase0_idea_forge_fails_after_5_rejects_prompts_user_for_manual_input` | integration | P1 |
| 3 | No test for Plan-Critic reaching max iterations (5 REJECT in a row). SKILL.md defines escalation to user but no test covers this boundary. | Add test: `phase1_plan_critic_rejects_5_times_escalates_to_user` | integration | P1 |
| 4 | No test for Phase 4 repeated test failure (3 consecutive failures on same test). SKILL.md defines user notification but no test covers this edge case. | Add test: `phase4_same_test_fails_3_times_reports_to_user` | integration | P1 |
| 5 | No test for session interruption and resume. SKILL.md defines resume logic (check docs/{service-name}/ for existing artifacts to determine completed Phase). | Add test: `resume_from_phase3_when_design_md_and_spec_md_exist` | e2e | P1 |
| 6 | No test for Phase 4 request to implement feature not in spec.md. SKILL.md NEVER rule #3 requires redirecting to Phase 3 for spec update. | Add test: `phase4_unspecified_feature_request_redirects_to_phase3` | integration | P0 |
| 7 | No boundary test for empty module list from Phase 1. If Planner produces zero modules, Phase 4 has nothing to build. | Add test: `phase4_with_zero_modules_reports_error` | unit | P1 |
| 8 | No security-specific test. Phase 4 Step 2 review checklist includes security checks (hardcoded secrets, SQL injection), but no test verifies this check is actually performed. | Add test: `phase4_review_detects_hardcoded_secrets_in_code` | unit | P1 |
| 9 | No test for NEVER rule #5: Phase 4 must not skip test step for any module. | Add test: `phase4_blocks_next_module_if_test_step_skipped` | unit | P0 |
| 10 | Design doc mentions `docs/{service-name}/` path constraint (artifacts never outside), but no test verifies NEVER rule #4 from SKILL.md for runtime enforcement. | Add test: `artifact_write_to_outside_path_is_rejected` | unit | P1 |

## Cross-Reference

| Design Doc Section | Requirements Found | Test Cases Generated | Coverage |
|-------------------|-------------------|---------------------|----------|
| Purpose (Section 1) | 3 | 3 | 3/3 = 100% |
| Architecture (Section 3) | 7 | 7 | 7/7 = 100% |
| Data Flow (Section 5) | 6 | 6 | 6/6 = 100% |
| API Design (Section 7) | 1 | 1 | 1/1 = 100% |
| File Structure (Section 8) | 6 | 6 | 6/6 = 100% |
| Phase Transition Conditions (Section 6) | 5 | 5 | 5/5 = 100% |
| Decision Rationale (Section 9) | 3 | 3 | 3/3 = 100% |
