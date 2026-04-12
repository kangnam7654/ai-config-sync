---
name: design-loop
description: "auto-dev Design Phase (#10-#26). Orchestrates architecture-loop → ux-ui-loop → plan-loop → CTO Design gate → Design Spec documentation. Called by auto-dev; also runs standalone."
---

**REQUIRED BACKGROUND:** 공통 loop 패턴은 `skills/_shared/loop-pattern.md` 참조. 이 스킬은 해당 패턴의 specialization이다.
<!-- Override: max 10 rounds for sub-loop re-invocations; delegates producer↔critic loops to architecture-loop, ux-ui-loop, plan-loop -->

# Design Loop

auto-dev 파이프라인의 Design Phase (#10~#26). 3개 서브-루프를 순차 호출하고, CTO Design 게이트를 통과한 뒤, 전체 설계를 design-spec.md로 통합 문서화한다.

## 스킬 계층

```
design-loop (#10~#26)
  ├── architecture-loop (#10~#16)  ← 서브 스킬
  ├── ux-ui-loop (#17~#22)         ← 서브 스킬
  ├── plan-loop (#23~#24)          ← 기존 스킬
  ├── #25 Design 게이트 (CTO)      ← 직접 처리
  └── #26 Design Spec 문서화       ← doc-loop 호출
```

## 워크플로우

```
architecture-loop (#10~#16)
  ↓ arch-spec.md 산출
ux-ui-loop (#17~#22)
  ↓ ux-ui-spec.md 산출
plan-loop (#23~#24)
  ├─ FAIL(아키텍처) → architecture-loop 재실행 (#10)
  ├─ FAIL(UX/UI) → ux-ui-loop 재실행 (#17)
  ├─ FAIL(실행계획) → plan-loop 재실행 (#23)
  └─ FAIL(복합) → architecture-loop부터 순차 (#10)
  ↓ PASS
#25 Design 게이트 (CTO)
  ├─ ARCH_REVISION → architecture-loop 재실행 (#10)
  ├─ UXUI_REVISION → ux-ui-loop 재실행 (#17)
  ├─ PLAN_REVISION → plan-loop 재실행 (#23)
  ├─ ESCALATE → 사용자 보고
  └─ PASS ↓
#26 📄 Design Spec 문서화 (doc-loop)
  → idea-brief + arch-spec + ux-ui-spec 3개 흡수 → design-spec.md 생성 → 3개 삭제
```

---

## Step 1: Architecture Loop (#10~#16)

**architecture-loop 스킬**을 호출한다. 입력: idea-brief.md (Idea Phase 산출물).

architecture-loop가 기술 스택 결정, DB 스키마 설계/리뷰, API 설계/리뷰, DB-API 정합성 검증을 수행하고 `arch-spec.md`를 산출한다.

---

## Step 2: UX-UI Loop (#17~#22)

**ux-ui-loop 스킬**을 호출한다. 입력: idea-brief.md + arch-spec.md.

ux-ui-loop가 UX 설계/검증, UI 디자인/검증, 디자인 디베이트를 수행하고 `ux-ui-spec.md`를 산출한다.

---

## Step 3: Plan Loop (#23~#24)

**plan-loop 스킬**(기존)을 호출한다. 입력: arch-spec.md + ux-ui-spec.md.

plan-loop가 planner 에이전트로 실행 계획 + 파일 구조를 작성하고, critic이 검증한다.

### plan-loop FAIL 처리

plan-loop는 내부에서 planner↔critic을 **최대 5라운드** 반복한다. plan-loop가 PASS를 반환하면 #25로 진행한다.

plan-loop가 FAIL을 반환하면 (5라운드 소진 또는 critic이 해결 불가로 판단), design-loop가 critic의 피드백 내용을 분석하여 실패 유형을 판별하고 해당 서브-루프를 재실행한다:

| 피드백 내용 → 실패 유형 | 재실행 대상 | 판별 기준 |
|---|---|---|
| 아키텍처 | architecture-loop (#10) | 피드백에 기술 스택, DB 스키마, API 구조 문제 언급 |
| UX/UI | ux-ui-loop (#17) | 피드백에 UX 플로우, UI 구성, 디자인 불일치 언급 |
| 실행계획 | plan-loop (#23) | 피드백에 구현 순서, 의존성, 작업 분해 문제만 언급 |
| 복합 | architecture-loop (#10)부터 순차 | 피드백이 2개 이상 영역에 걸침 |

**외부 루프 최대 10회**. 이 10회는 서브-루프 재호출 횟수 (plan-loop 내부 5라운드와 별개). 10회 소진 시 CTO 게이트(#25)로 에스컬레이션.

---

## Step 4: Design 게이트 (#25, CTO)

**CTO 에이전트**를 Design Gate 모드(Mode 6)로 호출한다. 입력: arch-spec.md + ux-ui-spec.md + 실행 계획(#23) + critic verdict(#24).

CTO gate-decision.yaml 산출:

| Decision | 처리 |
|---|---|
| `PASS` | #26으로 진행 |
| `ARCH_REVISION` | architecture-loop 재실행 (#10) |
| `UXUI_REVISION` | ux-ui-loop 재실행 (#17) |
| `PLAN_REVISION` | plan-loop 재실행 (#23) |
| `ESCALATE` | 사용자에게 보고 (복합 실패) |

**최대 10회 반복**. 10회 소진 시 사용자 보고: "Design Phase 해결 불가."

---

## Step 5: Design Spec 문서화 (#26)

**doc-loop 스킬**을 자동(B) 모드 + LLM 모드로 호출한다.

이 단계에서 **문서 흡수**가 발생한다:

1. doc-loop가 아래 3개 문서를 흡수하여 `design-spec.md` 생성:
   - `idea-brief.md` (#9에서 생성)
   - `arch-spec.md` (#16에서 생성)
   - `ux-ui-spec.md` (#22에서 생성)
2. design-spec.md에 실행 계획(#23) + CTO 게이트 승인(#25) 내용도 포함
3. 생성 완료 후 **3개 원본 문서를 삭제**

design-spec.md는 Build Phase와 Verify Phase 전체에서 "기대 동작"의 기준 문서로 사용된다.

**산출물**: `{project}/docs/llm/design-spec.md`

---

## 경계

- 이 스킬은 **서브-루프 오케스트레이션 + FAIL 라우팅 + 문서 흡수**를 담당한다.
- 각 서브-루프의 내부 로직은 architecture-loop, ux-ui-loop, plan-loop가 담당한다.
- CTO 에이전트 호출은 이 스킬이 메인 모델에 요청한다 (NEVER rule: 에이전트 직접 호출 금지).
- Build Phase 이후는 build-loop, verify-loop가 담당한다.
- 입력 전제 조건: idea-brief.md (auto-dev) 또는 audit-report.md (auto-improve). 둘 다 없으면 실행하지 않고 선행 Phase 완료를 요청한다.
