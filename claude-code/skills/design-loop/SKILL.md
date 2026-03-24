---
name: design-loop
description: "auto-dev 파이프라인의 Design Phase (#10~#26) 전체를 오케스트레이션한다. architecture-loop → ux-ui-loop → plan-loop → CTO Design 게이트 → Design Spec 문서화를 순차 실행한다. auto-dev 스킬이 호출하며, 독립 실행도 가능하다. '설계 전체 해줘', '아키텍처부터 UX/UI까지 설계', 'design loop 실행', 'Design Phase 시작' 요청에 트리거."
---

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

plan-loop가 planner 에이전트로 실행 계획 + 파일 구조를 작성하고, plan-critic이 검증한다.

### plan-critic FAIL 라우팅

plan-critic이 FAIL을 반환하면, 실패 유형에 따라 해당 서브-루프를 재실행한다:

| plan-critic FAIL 유형 | 재실행 대상 | 설명 |
|---|---|---|
| `아키텍처` | architecture-loop (#10) | 기술 스택이나 DB/API 구조에 문제 |
| `UX/UI` | ux-ui-loop (#17) | UX/UI 설계와 실행 계획의 불일치 |
| `실행계획` | plan-loop (#23) | 실행 계획 자체의 문제 (순서, 의존성) |
| `복합` | architecture-loop (#10)부터 순차 | 여러 영역에 걸친 문제 |

**최대 10회 반복**. 10회 소진 시 CTO 게이트(#25)로 에스컬레이션.

---

## Step 4: Design 게이트 (#25, CTO)

**CTO 에이전트**를 Design Gate 모드(Mode 6)로 호출한다. 입력: arch-spec.md + ux-ui-spec.md + 실행 계획(#23) + plan-critic verdict(#24).

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
- Idea Phase 산출물(idea-brief.md)이 입력 전제 조건이다. 없으면 실행하지 않고 idea-forge 완료를 요청한다.
