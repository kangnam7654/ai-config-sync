# Skills & Agents Consolidation Design

## Purpose

사용자 소유 Claude Code 에이전트 43개와 스킬 39개를 역할 패밀리 단위로 통합하고, `references/` 네이밍 통일 + `persona.md` 도입으로 유지보수성과 컨텍스트 효율성을 개선한다.

### Completion Criteria

1. `ls ~/.claude/agents/*.md | wc -l` == **33**
2. `find ~/.claude/skills -name SKILL.md | wc -l` == **38**
3. `find ~/.claude/agents ~/.claude/skills -type d -name "refs"` == **0건**
4. 7개 통합 에이전트에 `agents/{name}/persona.md` 존재: code-reviewer, critic, build-resolver, designer, writer, dba, researcher
5. `agents/go-reviewer.md`, `agents/python-reviewer.md` 삭제됨. `code-reviewer.md` 본문에 정적분석 실행 지시 존재
6. auto-dev 파이프라인 주요 경로 (plan-loop, build-loop, doc-loop) 호출 정상
7. `sync-timestamps.py` EXCLUDES에 `skills/**/*-workspace/**` 패턴 존재
8. `grep -rl "DELETED_AGENT_NAMES" ~/.claude` == 0건 (old name 잔존 없음)

### Non-goals

- 플러그인 에이전트/스킬 수정 (업데이트 시 덮어쓰임)
- C-suite 통합 (ceo/cso/cto/ciso — 견제 구조가 auto-dev 본질)
- Dev 에이전트 통합 (backend-dev/frontend-dev/mobile-dev 등 — 스택별 본질적 차이)
- tdd-guide 삭제 (superpowers:TDD와 다른 레이어 — 실행 vs 규율)
- plan-loop 삭제 (writing-plans와 상호보완 — 포맷 vs iterative scoring)
- 오피스 문서 스킬 통합 (pdf/pptx/docx/xlsx — 크기/도메인/라이브러리 완전 독립)

---

## Architecture

### 통합 에이전트 표준 파일 구조

```
~/.claude/agents/
├── {agent-name}.md              # 본문: 워크플로, 출력 포맷, NEVER rules, 도구
├── {agent-name}/
│   ├── persona.md               # 페르소나: 가치관, 의사결정 원칙 (통합 에이전트만)
│   └── references/              # 참조: 역할별 체크리스트/규칙 (조건부 로드)
│       ├── {role-1}.md
│       └── {role-N}.md
```

### 3-layer 분리 원칙

| Layer | 파일 | 담는 것 | 로드 시점 |
|---|---|---|---|
| **Process** | `{agent}.md` | 워크플로 단계, 출력 포맷, NEVER rules, 도구 목록 | 항상 (에이전트 호출 시) |
| **Persona** | `persona.md` | 핵심 가치관 1~3줄, 의사결정 스타일, tie-breaker | 항상 (본문 상단 REQUIRED BACKGROUND) |
| **Reference** | `references/*.md` | 역할별 상세 규칙, 체크리스트, 안티패턴 | 조건부 (self-routing 결과에 따라) |

### Self-Routing Mechanism

에이전트 본문 Step 1에서 입력 컨텍스트를 검사하여 어느 reference를 로드할지 자기 자신이 결정한다. 메인 모델은 에이전트 이름만 호출하고 내부 refs 구조를 알 필요 없다.

검출 수단: git diff 파일 확장자, 사용자 프롬프트 키워드, 프로젝트 매니페스트 파일 존재 여부.

매칭 없으면: 사용자에게 mode 확인 요청. 추측 금지.

이 패턴은 `advanced-code-reviewer.md` Step 3에서 이미 사용 중 (검증됨).

### Persona 파일 포맷

```markdown
# {Agent Name} Persona

## Core Value
{한 문장}

## Decision Principles
1. {원칙 1}
2. {원칙 2}
3. {원칙 3}

## Tie-Breakers
{여러 합리적 선택 충돌 시 우선순위}

## What This Persona Is NOT
{자주 오해받는 범위}
```

에이전트 본문 상단에서 로드:
```markdown
**REQUIRED BACKGROUND:** Read `agents/{name}/persona.md` before proceeding.
```

스킬에는 persona.md 도입하지 않는다 (스킬은 프로세스/툴킷이지 역할이 아님).

---

## File Changes

### 삭제 (12 files)

| 파일 | 이유 |
|---|---|
| `agents/go-reviewer.md` | advanced-code-reviewer/references/go-checklist.md와 100% 룰 일치 (검증 완료) |
| `agents/python-reviewer.md` | advanced-code-reviewer/references/python-checklist.md와 100% 룰 일치 (검증 완료) |
| `agents/doc-critic.md` | critic 에이전트로 통합 |
| `agents/plan-critic.md` | critic 에이전트로 통합 |
| `agents/build-error-resolver.md` | build-resolver 에이전트로 통합 |
| `agents/go-build-resolver.md` | build-resolver 에이전트로 통합 |
| `agents/ui-designer.md` | designer 에이전트로 흡수 |
| `agents/product-designer.md` | designer 에이전트로 흡수 |
| `agents/doc-writer-human.md` | writer 에이전트로 통합 |
| `agents/doc-writer-llm.md` | writer 에이전트로 통합 |
| `agents/database-reviewer.md` | dba 에이전트로 흡수 |
| `agents/trend-scorer.md` | researcher 에이전트로 흡수 |
| `skills/transport-search/` (전체) | travel 스킬로 통합 |
| `skills/travel-plan/` (전체) | travel 스킬로 통합 |

### 리네임 (3 operations)

| FROM | TO |
|---|---|
| `agents/advanced-code-reviewer.md` | `agents/code-reviewer.md` |
| `agents/advanced-code-reviewer/` | `agents/code-reviewer/` |
| `agents/reviewer.md` | `agents/qa-gate.md` |
| `agents/cto/refs/` | `agents/cto/references/` |

### 신규 생성

**에이전트 본문 (4 files):**

| 파일 | 설명 |
|---|---|
| `agents/critic.md` | doc-critic + plan-critic 통합. Mode detection (doc-human/doc-llm/plan) → rubric ref 로드 → scoring → PASS/REJECT |
| `agents/build-resolver.md` | build-error-resolver + go-build-resolver 통합. Build system detection → language ref 로드 → surgical fix |
| `agents/travel/SKILL.md` | transport-search + travel-plan 통합 |
| `skills/_shared/loop-pattern.md` | 9개 loop 스킬 공통 boilerplate 추출 |

**Persona 파일 (7 files):**

| 파일 | Core Value 요약 |
|---|---|
| `agents/code-reviewer/persona.md` | 이슈를 찾아 보고하라. 고치지 마라. Read-only. |
| `agents/critic/persona.md` | 채점 인플레이션 금지. 5점은 5점. 수학을 보여줘라. |
| `agents/build-resolver/persona.md` | Surgical minimal diffs only. 아키텍처 수정 금지. |
| `agents/designer/persona.md` | 말로 설명하지 말고 만들어라. 접근성 > 미관. |
| `agents/writer/persona.md` | 결과물은 기계가 파싱 가능하거나 행동 가능해야 한다. |
| `agents/dba/persona.md` | 모든 마이그레이션은 되돌릴 수 있어야 한다. |
| `agents/researcher/persona.md` | 사실만 수집한다. 전략적 결정은 ceo/cso 몫. 출처 없는 주장 금지. |

**Reference 파일:**

| 에이전트 | 신규 refs |
|---|---|
| `critic/references/` | `rubric-doc-human.md` (기존 doc-critic refs 이관), `rubric-doc-llm.md` (기존 이관), `rubric-plan.md` (plan-critic 6-criteria 추출) |
| `build-resolver/references/` | `go.md`, `js-ts.md`, `python.md`, `rust.md`, `java.md` |
| `designer/references/` | `ux-research.md`, `ui-figma.md`, `mockup-html.md`, `stitch.md` |
| `writer/references/` | `data-files.md`, `business-docs.md`, `human-docs.md`, `llm-docs.md` |
| `dba/references/` | `schema-design.md`, `query-opt.md`, `migration.md`, `security.md`, `anti-patterns.md`, `diagnostics.md`, `pipeline-mode.md` |
| `researcher/references/` | `market-research.md`, `trend-scoring.md`, `comparison.md` |
| `travel/references/` | `transport.md`, `planning.md`, `weather.md`, `booking-sites.md` |

### 수정 (기존 파일 업데이트)

| 파일 | 변경 요약 |
|---|---|
| `agents/code-reviewer.md` (구 advanced-code-reviewer) | frontmatter name 변경, Step 5 앞에 정적분석 실행 지시 1줄 추가, persona REQUIRED BACKGROUND 추가 |
| `agents/code-reviewer/references/go-checklist.md` | 맨 위에 scope 노트 1줄 추가 (review only, build fix → build-resolver) |
| `agents/qa-gate.md` (구 reviewer) | frontmatter name 변경 |
| `agents/designer.md` | mode detection step 추가, persona REQUIRED BACKGROUND 추가, ui-designer/product-designer 내용 refs로 분리 |
| `agents/writer.md` | mode detection step 추가, persona REQUIRED BACKGROUND 추가, doc-writer-human/llm 내용 refs로 분리 |
| `agents/dba.md` | database-reviewer의 P0~P3 severity/anti-patterns/diagnostics 흡수 (refs로 분리), persona REQUIRED BACKGROUND 추가 |
| `agents/researcher.md` | trend-scoring mode 흡수 (ref로 분리), persona REQUIRED BACKGROUND 추가 |
| `agents/cto.md` | 본문의 `cto/refs/` 참조를 `cto/references/`로 교체 |
| `sync-timestamps.py` | EXCLUDES["claude-code"]에 workspace 제외 패턴 추가 |
| **doc-loop SKILL.md** | subagent_type: doc-critic → critic, doc-writer-human/llm → writer |
| **plan-loop SKILL.md** | subagent_type: plan-critic → critic |
| **9개 loop SKILL.md** | 상단에 REQUIRED BACKGROUND _shared/loop-pattern.md, 공통 boilerplate 제거 |
| 기타 agents/skills | cross-reference grep & replace (old agent names → new names) |

---

## Implementation Order

### Phase 0: 사전 준비

0. sync cron 일시 정지
1. `git pull --rebase` + 백업 브랜치 `backup/pre-consolidation-20260412` 생성
2. `feat/skills-agents-consolidation` 작업 브랜치 생성
3. 현재 상태 스냅샷 (agents 43, skills 39 기록)
4. `build-error-resolver.md`, `designer.md`, `doc-writer-human.md`, `doc-writer-llm.md` 본문 분석 → 분할 전략 확정

### Phase 1: S4 Workspace 정리 (Commit 1)

5. `sync-timestamps.py` EXCLUDES에 workspace 패턴 추가
6. `git rm --cached -r claude-code/skills/*/*-workspace` (로컬 유지)
7. Commit: `chore: exclude *-workspace directories from sync`

### Phase 2: Overlap 정리 (Commit 2)

8. `agents/advanced-code-reviewer.md` Step 5 앞에 정적분석 지시 1줄 추가
9. `agents/advanced-code-reviewer/references/go-checklist.md` 상단에 scope 노트 추가
10. `agents/go-reviewer.md` 삭제
11. `agents/python-reviewer.md` 삭제
12. Commit: `refactor: consolidate go/python-reviewer into advanced-code-reviewer`

### Phase 3: refs → references 통일 (Commit 3)

13. `git mv agents/cto/refs agents/cto/references`
14. `agents/cto.md` 본문 refs/ → references/ replace
15. Commit: `refactor: unify reference folder naming to references/`

### Phase 4: 리네임 (Commit 4-5)

16. `advanced-code-reviewer.md` → `code-reviewer.md`, 디렉토리 리네임, frontmatter 변경
17. Cross-reference grep & replace ("advanced-code-reviewer" → "code-reviewer")
18. Commit 4: `refactor: rename advanced-code-reviewer to code-reviewer`
19. `reviewer.md` → `qa-gate.md`, frontmatter 변경
20. Cross-reference grep & replace (에이전트 이름으로서의 "reviewer" → "qa-gate")
21. Commit 5: `refactor: rename reviewer to qa-gate`

### Phase 5: 에이전트 통합 (Commit 6-11)

22. **A3 build-resolver**: 본문 작성 + refs 생성 + old 2개 삭제 + cross-ref update
23. Commit 6: `refactor: consolidate build resolvers into build-resolver`
24. **A8 researcher**: researcher.md 업데이트 + refs 생성 + trend-scorer 삭제 + cross-ref update
25. Commit 7: `refactor: consolidate trend-scorer into researcher`
26. **A7 dba**: dba.md 업데이트 + refs 생성 + database-reviewer 삭제 + cross-ref update
27. Commit 8: `refactor: consolidate database-reviewer into dba`
28. **A4 designer**: designer.md 업데이트 + refs 생성 + ui-designer/product-designer 삭제 + cross-ref update
29. Commit 9: `refactor: consolidate ui-designer/product-designer into designer`
30. **A2 critic**: critic.md 작성 + rubric refs 생성/이관 + doc-critic/plan-critic 삭제 + doc-loop/plan-loop subagent_type update
31. Commit 10: `refactor: consolidate doc-critic and plan-critic into critic`
32. **A5 writer**: writer.md 업데이트 + refs 생성 + doc-writer-human/llm 삭제 + doc-loop subagent_type update
33. Commit 11: `refactor: consolidate doc-writer agents into writer`

### Phase 6: Persona 생성 (Commit 12)

34. 7개 persona.md 파일 생성
35. 7개 에이전트 본문에 REQUIRED BACKGROUND 줄 추가
36. Commit 12: `feat: add persona.md for consolidated agents`

### Phase 7: Skills 통합 (Commit 13-14)

37. **S2 travel**: SKILL.md + refs 생성, transport-search/travel-plan 삭제
38. Commit 13: `refactor: merge transport-search and travel-plan into travel`
39. **S5 loop pattern**: `_shared/loop-pattern.md` 생성, 9개 loop SKILL.md에 REQUIRED BACKGROUND 추가 + boilerplate 제거
40. Discovery 안전성 검증 (SKILL.md 없으면 스킬 미인식). 실패 시 fallback: `docs/llm/shared/loop-pattern.md`
41. Commit 14: `refactor: extract shared loop pattern`

### Phase 8: 최종 검증 (Commit 15)

42. `scripts/verify-consolidation.sh` 실행 (수치/grep/persona 검증)
43. Layer 2 functional test: code-reviewer, critic, designer, writer, dba 수동 호출
44. Layer 3 integration: auto-dev 첫 3-5 step 수동 실행
45. CLAUDE.md 또는 관련 문서의 에이전트 목록 업데이트
46. Commit 15: `docs: update references after consolidation`
47. sync cron 재개

---

## Constraints

1. 각 Phase는 독립 git commit. revert 가능성 보장.
2. Cross-reference update는 해당 에이전트 삭제와 **같은 commit**에 포함 (atomicity).
3. Self-routing에서 매칭 없으면 사용자에게 확인 요청. 추측 금지.
4. Persona.md는 통합 에이전트 7개에만 생성. 단일 역할 에이전트는 현행 유지.
5. auto-dev 파이프라인 step 번호(#11, #12, #20, #27, #28, #29 등) 참조가 깨지면 해당 loop 스킬 본문 즉시 수정.
6. sync-timestamps.py의 `EXCLUDES` 패턴 추가는 Phase 1에서 먼저 실행하여 이후 phase에서 workspace 노이즈 방지.
7. 작업 기간 중 sync cron 일시 정지 필수.

---

## Decisions

### 선택한 접근법

- **Option B (중간 통폐합)** 선택. 역할 패밀리 단위 통합 + self-routing refs + persona.md 도입.
- **P-2 (통합 에이전트에만 persona 도입)**. 전체 도입(P-3)은 과잉, 미도입(P-1)은 통합 에이전트의 다중 역할 구분 부족.
- **Self-routing** (에이전트가 내부에서 ref 선택). Main-routing(메인 모델이 ref 힌트 주입)은 커플링 증가로 기각.
- **plan-loop 유지** (writing-plans와 상호보완). 초기엔 삭제 예정이었으나 검증 결과 레이어가 다름을 확인.
- **tdd-guide 유지** (superpowers:TDD와 상호보완). 초기엔 삭제 예정이었으나 검증 결과 실행 도구 vs 규율 철학으로 레이어가 다름을 확인.
- **S1 오피스 문서 통합 취소**. 파일별 1459줄 + 서로 다른 라이브러리. 토큰 절감 없음, 오히려 증가 가능.

### 기각된 대안

- **Option A (가벼운 정리)**: refs 통일 + 명백 중복만 제거. 43→38 수준으로 절감 효과 미미.
- **Option C (급진적 통합)**: C-suite → executive 1개, 모든 dev → developer 1개. 견제 구조 훼손, 스택별 특화 손실, 되돌리기 어려움.
- **P-3 (전체 에이전트 persona)**: 33개 전부에 persona.md 추가는 단일 역할 에이전트에 과잉.
- **Main-routing**: 메인 모델이 dispatch 시 ref 이름 힌트 전달. refs 구조 변경 시 메인 모델도 수정 필요 → tight coupling.
- **Plugin overlap 전면 삭제**: code-simplifier, planner, refactor-cleaner 등 borderline 케이스를 삭제하면 고유 기능 손실 위험.

---

## Risks & Mitigations

| Risk | 확률 | 영향 | Mitigation |
|---|---|---|---|
| Cross-reference 누락 (old name 잔존) | 높음 | 중간 | 매 commit 후 grep 검사. Phase 8.2에서 최종 검증. |
| auto-dev 파이프라인 파손 | 중간 | 높음 | A2/A5에서 loop 스킬 subagent_type을 동일 commit에 업데이트. Phase 8.3 샘플 실행. |
| Sync 충돌 (다른 기기 sync 실행) | 중간 | 높음 | 작업 시작 전 cron 일시 정지. 완료 후 수동 sync 1회 실행. |
| Self-routing 실패 (ref 미로드) | 낮음 | 중간 | advanced-code-reviewer에서 기검증된 패턴. 새 에이전트는 매칭 테이블이 더 단순. |
| Persona.md 미로드 | 낮음 | 낮음 | superpowers 스킬에서 검증된 REQUIRED BACKGROUND 패턴. 실패해도 기능 손실 없음. |
| `_shared/` 디스커버리 오탐 | 낮음 | 낮음 | SKILL.md 부재로 스킬 미인식 예상. 오탐 시 fallback: docs/llm/shared/로 이동. |
| git rm --cached 후 재추적 | 중간 | 낮음 | EXCLUDES 패턴 추가가 Phase 1에서 먼저 실행. |

---

## Verification Strategy

### Layer 1: Static (자동, 매 commit 후)

```bash
#!/bin/bash
# scripts/verify-consolidation.sh

echo "=== Agent count ==="
AGENTS=$(ls ~/.claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "Agents: $AGENTS (expected: 33)"

echo "=== Skill count ==="
SKILLS=$(find ~/.claude/skills -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
echo "Skills: $SKILLS (expected: 38)"

echo "=== refs/ folder check ==="
REFS=$(find ~/.claude/agents ~/.claude/skills -type d -name "refs" 2>/dev/null | wc -l | tr -d ' ')
echo "refs/ dirs: $REFS (expected: 0)"

echo "=== Persona check ==="
for a in code-reviewer critic build-resolver designer writer dba researcher; do
  test -f ~/.claude/agents/$a/persona.md && echo "OK: $a" || echo "MISSING: $a"
done

echo "=== Old name residual check ==="
OLD_NAMES="advanced-code-reviewer|go-reviewer|python-reviewer|ui-designer|product-designer|doc-critic|plan-critic|database-reviewer|trend-scorer|build-error-resolver|go-build-resolver|doc-writer-human|doc-writer-llm"
FOUND=$(grep -rl "$OLD_NAMES" ~/.claude/agents ~/.claude/skills 2>/dev/null | wc -l | tr -d ' ')
echo "Old name references: $FOUND (expected: 0)"
```

### Layer 2: Functional (수동, Phase 8)

| 에이전트 | 시나리오 | 확인 포인트 |
|---|---|---|
| code-reviewer | Python diff 리뷰 | ruff/mypy/bandit 실행, python-checklist 적용 |
| code-reviewer | Go diff 리뷰 | go vet/staticcheck 실행, go-checklist 적용 |
| critic | README 평가 | doc-human mode 감지, scorecard 출력 |
| critic | Implementation plan 평가 | plan mode 감지, 6-criteria scoring |
| designer | "로그인 화면 디자인" | mode detection, HTML/CSS 생성 |
| writer | "README 작성" | human-docs mode 감지 |
| dba | SQL migration 리뷰 | P0~P3 severity 출력 |

### Layer 3: Integration (수동, Phase 8.3)

auto-dev 첫 3-5 step 수동 실행 (idea-forge → architecture-loop → plan-loop). 에이전트 호출 실패 시 step + old name 기록.

### Rollback

- 단일 phase: `git revert <commit-sha>`
- 전체: `git reset --hard backup/pre-consolidation-20260412`
- A2/A5 revert 시 loop 스킬 수정도 함께 revert됨 (동일 commit)
