---
name: auto-dev
description: "Fully automated app development pipeline. Runs 36 steps from ideation to design, implementation, and verification from a single sentence input. For new apps/services only — not for modifying existing code, bug fixes, or refactoring."
---

# auto-dev

"앱 하나 만들어" → 딸-깍 → 동작하는 앱. 사람 개입 최소화한 전자동 개발 파이프라인.

36단계, 4 Phase(Idea → Design → Build → Verify)를 오케스트레이션한다.

## Scope

**IN-SCOPE**: 아래 조건을 모두 만족하는 요청만 처리:
- 신규 앱 또는 서비스를 처음부터 만드는 요청
- 결과물이 동작하는 코드베이스인 요청
- 웹앱, 모바일앱(React Native), 또는 백엔드 API 중 하나 이상을 포함

**OUT-OF-SCOPE**: "auto-dev는 신규 앱/서비스 개발 전용입니다." 응답 후 종료:
- 기존 코드 수정, 버그 수정, 리팩터링
- 인프라 배포, CI/CD 설정, 서버 관리
- 문서 작성, 데이터 분석, 비개발 업무

## 스킬 계층

```
auto-dev
  ├── idea-forge (#1~#9)
  │     └── doc-loop (#9)
  ├── design-loop (#10~#26)
  │     ├── architecture-loop (#10~#16)
  │     │     └── doc-loop (#16)
  │     ├── ux-ui-loop (#17~#22)
  │     │     └── doc-loop (#22)
  │     ├── plan-loop (#23~#24)
  │     └── doc-loop (#26)
  ├── build-loop (#27~#31)
  │     └── doc-loop (#31)
  └── verify-loop (#32~#36)
```

## 워크플로우

```
[사용자 입력]
  ↓
Idea Phase: idea-forge (#1~#9)
  ↓ #8 CEO 게이트 PASS → idea-brief.md 산출
Design Phase: design-loop (#10~#26)
  ↓ #25 CTO 게이트 PASS → design-spec.md 산출
Build Phase: build-loop (#27~#31)
  ↓ → build-summary.md 산출
Verify Phase: verify-loop (#32~#36)
  ↓ #35 론칭 디베이트 PASS → completion.yaml 산출
[완성 보고]
```

---

## Phase 1: Idea (#1~#9)

**idea-forge 스킬**을 호출한다. 사용자 입력을 그대로 전달.

idea-forge가 입력 분류(#1), 브레인스토밍/트렌드(#2~#3), CEO 방향 결정(#4), 시장 조사(#5), CSO 전략 검증(#6), BM 설계(#7), CEO 게이트(#8), Idea Brief 문서화(#9)를 수행한다.

**Phase 전환 조건**: #8 CEO 게이트 PASS (gate-decision.yaml의 decision = "PASS")

**산출물**: idea-brief.md

### 복잡도 분류 (Idea→Design 전환 시)

idea-brief.md 산출 후, auto-dev가 아래 기준으로 프로젝트 복잡도를 분류한다:

| 복잡도 | 조건 (모두 충족) | 축소 대상 단계 |
|--------|----------------|--------------|
| Simple | 핵심 기능 ≤3개 AND 트랙 1개(FE only 또는 BE only) AND DB 테이블 ≤3개 | #3(트렌드), #5(시장조사) 이미 SKIP 가능. 추가로: #21(디자인 디베이트→단독 CTO 판정), #33(UI패리티→간소화), #34(사용성→간소화), #35(4자 디베이트→CTO 단독 판정) |
| Standard | 위 조건 미충족 | 전체 36단계 |

Simple 분류 시:
- #21, #35: 4자/2자 디베이트 대신 CTO 에이전트 단독 판정으로 대체 (라운드 불필요)
- #33, #34: 최대 반복 3회로 축소 (기본 10회 → 3회)
- 분류 결과를 사용자에게 보고: "Simple 프로젝트로 분류. #21/#33/#34/#35 축소 적용."

---

## Phase 2: Design (#10~#26)

**design-loop 스킬**을 호출한다. 입력: idea-brief.md.

design-loop가 architecture-loop(#10~#16), ux-ui-loop(#17~#22), plan-loop(#23~#24), CTO Design 게이트(#25), Design Spec 문서화(#26)를 수행한다.

**Phase 전환 조건**: #25 CTO Design 게이트 PASS (gate-decision.yaml의 decision = "PASS")

**산출물**: design-spec.md (idea-brief + arch-spec + ux-ui-spec 흡수 완료)

---

## Phase 3: Build (#27~#31)

**build-loop 스킬**을 호출한다. 입력: design-spec.md.

build-loop가 구현(#27 병렬), DBA 리뷰(#28), 코드/보안 리뷰(#29), 테스트(#30), Build Summary 문서화(#31)를 수행한다.

**Phase 전환 조건**: 게이트 없음 (Build 내부 리뷰로 충분)

**산출물**: build-summary.md

---

## Phase 4: Verify (#32~#36)

**verify-loop 스킬**을 호출한다. 입력: design-spec.md + build-summary.md.

verify-loop가 동작 검증(#32), UI 패리티(#33), 사용성 테스트(#34), C-suite 론칭 디베이트(#35, CEO/CTO/CSO/CISO 4자), 완성 보고(#36)를 수행한다.

**산출물**: completion.yaml

---

## Cross-Phase 복귀 처리

verify-loop가 FAIL을 반환할 때, 복귀 대상이 다른 Phase에 있을 수 있다. auto-dev가 라우팅을 담당한다:

| verify-loop FAIL | 복귀 대상 | auto-dev 처리 |
|---|---|---|
| #32 FAIL → #27 | Build Phase | build-loop 재실행 |
| #32 FAIL → #23 (2회 동일 에러) | Design Phase | design-loop에 plan-loop 재실행 요청 |
| #33 FAIL → #19 | Design Phase | design-loop에 ux-ui-loop 재실행 요청 (UI부터) |
| #34 FAIL → #17 | Design Phase | design-loop에 ux-ui-loop 재실행 요청 (UX부터) |
| #35 코드 수정 → #27 | Build Phase | build-loop 재실행 |
| #35 설계 변경 → 사용자 | Human-in-loop | 사용자에게 보고, 판단 대기 |

Cross-Phase 복귀 시: 복귀 대상 Phase 스킬을 재실행한다. 이전 Phase의 산출물 중 복귀 대상 이전 단계의 산출물은 유지한다 (ALWAYS 규칙 #3).

문서 라이프사이클 주의: Design Phase 재실행 시 design-spec.md가 이미 존재할 수 있다. 재실행된 서브-루프의 산출물로 design-spec.md를 업데이트한다.

### 복귀 반환 포맷

Phase 스킬이 auto-dev에게 복귀를 요청할 때 아래 YAML 구조로 반환한다:

```yaml
phase_return:
  status: "FAIL"
  source_step: "#32"          # 실패가 발생한 단계
  source_phase: "verify"      # 현재 Phase
  target_step: "#27"          # 복귀 대상 단계
  target_phase: "build"       # 복귀 대상 Phase
  reason: "POST /api/todos 500 에러" # 실패 원인 1줄 요약
  attempt: 1                  # 동일 복귀 시도 횟수
  same_error_consecutive: false # 직전 복귀와 동일 에러인지
```

auto-dev는 `target_phase`로 라우팅하고, `attempt`와 `same_error_consecutive`를 추적하여 2회 동일 에러 시 상위 Phase로 에스컬레이션한다.

---

## NEVER 규칙

1. NEVER: Phase 게이트를 건너뛰지 마라. Idea→Design은 CEO #8 PASS 필수, Design→Build는 CTO #25 PASS 필수.
2. NEVER: 에이전트가 다른 에이전트를 직접 호출하지 마라. 모든 에이전트 호출은 해당 Phase의 스킬(오케스트레이터)을 통해서만 수행한다.
3. NEVER: 루프 상한을 초과하여 재시도하지 마라. 각 루프의 상한과 소진 처리는 아래 "루프 소진 처리" 테이블을 따른다.
4. NEVER: SKIP 불가 단계의 실패를 무시하고 다음 단계로 진행하지 마라. SKIP 가능 여부는 아래 "단계 분류" 테이블을 따른다.
5. NEVER: 동일 Phase 내에서 단계 순서를 변경하지 마라. (예외: #27 구현은 병렬 허용)

## ALWAYS 규칙

1. ALWAYS: 리뷰/검증 단계에서는 수학적 채점(기준별 0~10 × 가중치 → 총점)으로 PASS/FAIL을 판정한다. PASS: 총점 > 8.0 AND 주요 기준 >= 7.
2. ALWAYS: Phase 전환 시 이전 Phase의 전체 산출물을 다음 Phase에 전달한다.
3. ALWAYS: 실패 복귀 시 복귀 대상 단계의 산출물만 재생성한다. 그 이전 단계의 산출물은 유지한다.
4. ALWAYS: 📄 문서화 단계(#9, #16, #22, #26, #31)는 doc-loop 스킬을 자동(B) 모드 + LLM 모드로 호출한다.

---

## 단계 분류 (SKIP 가능 여부)

| 단계 | SKIP 가능 | 조건 |
|------|----------|------|
| #2 브레인스토밍 | O | 사용자가 구체적 아이디어를 제시한 경우 ("같이 고민" 유형 아닐 때) |
| #3 트렌드 스코어링 | O | 사용자가 구체적 아이디어를 제시한 경우 + 도구 실패 시 |
| #5 시장 조사 | O | 도구(WebSearch/WebFetch) 실패 시 경고 출력 후 진행 |
| #28 DBA 리뷰 | O | DB/SQL/마이그레이션 파일이 없을 때 |
| 그 외 모든 단계 | X | FAIL 시 루프 재시도 또는 에스컬레이션 |

## 루프 소진 처리

각 루프의 상한과 소진 시 처리를 정의한다. "내부"는 해당 스킬 내 반복, "외부"는 상위 스킬에서의 재호출을 의미한다.

| 루프 | 상한 | 소진 시 처리 |
|------|------|------------|
| #6 CSO 전략 검증 | 10회 | 사용자 보고: "전략 검증 10회 실패" + 중단 |
| #8 CEO Idea 게이트 | 10회 | 사용자 보고: "Idea Phase 10회 실패" + 중단 |
| #12 DB 스키마 리뷰 | 10회 | CTO 최종 판정 (위험 수용 or ABORT) |
| #14 API 리뷰 | 10회 | CTO 최종 판정 |
| #15 DB-API 정합성 | 10회 | CTO 최종 판정 |
| #18 UX 검증 | 10회 | CTO 판정 |
| #20 UI 검증 | 10회 | CTO 판정 |
| #21 디자인 디베이트 | 10회 (라운드) | CTO 최종 판정 확정 |
| #23-#24 plan-loop | 내부 5회, 외부 10회 | 내부 소진→design-loop에 FAIL 반환. 외부 소진→CTO 게이트(#25) 에스컬레이션 |
| #25 Design 게이트 | 10회 | 사용자 보고: "Design Phase 해결 불가" + 중단 |
| #28 DBA 리뷰 | 10회 | CTO 에스컬레이션 |
| #29 코드/보안 리뷰 | 10회 | CTO 에스컬레이션 |
| #30 테스트 | 10회 | 사용자 보고 + 중단 |
| #32 동작 검증 | 10회 | 사용자 보고 + 중단 |
| #33 UI 패리티 | 10회 | 사용자 보고 + 중단 |
| #34 사용성 테스트 | 10회 | 사용자 보고 + 중단 |
| #35 론칭 디베이트 | 10회 (라운드) | 사용자 보고 (human-in-loop 전환) |

---

## 문서 라이프사이클

```
idea-brief.md (#9) ──────────────┐
                                  │
arch-spec.md (#16) ──────────────┤
                                  ├→ design-spec.md (#26) 생성 → 3개 삭제
ux-ui-spec.md (#22) ─────────────┤
                                  │
실행계획+CTO승인 ─────────────────┘

design-spec.md (#26) ─────────── Verify Phase까지 유지
build-summary.md (#31) ────────── Verify Phase까지 유지
```

Verify Phase 시점 동시 존재 문서: 2개 (design-spec + build-summary).

---

## 시스템 실패 처리

| 실패 유형 | 처리 |
|---|---|
| 에이전트 응답 없음/타임아웃 | 3회 재시도 (30초 간격). 3회 실패 시 사용자 보고 후 중단. |
| 도구 호출 실패 | SKIP 가능(#3 트렌드, #5 시장조사): 경고와 함께 진행. SKIP 불가: 사용자 보고 후 중단. |
| 컨텍스트 윈도우 초과 | 현재 Phase 산출물을 파일로 저장하고, 사용자에게 보고. |

---

## 경계

- 이 스킬은 **최상위 오케스트레이터**다. 4개 Phase 스킬(idea-forge, design-loop, build-loop, verify-loop)을 순차 호출하고 Cross-Phase 복귀를 라우팅한다.
- 각 Phase 스킬이 내부 단계를 오케스트레이션한다. auto-dev는 개별 단계(#10, #11, ...)를 직접 관리하지 않는다.
- 에이전트를 직접 호출하지 않는다 — Phase 스킬에게 위임하고, Phase 스킬이 메인 모델에 에이전트 호출을 요청한다.
