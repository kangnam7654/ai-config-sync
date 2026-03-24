---
name: auto-dev
description: "전자동 앱 개발 파이프라인. 한 문장 입력('앱 하나 만들어')으로 아이디어 발굴 → 설계 → 구현 → 검증까지 36단계를 자동 실행한다. '앱 만들어', '서비스 개발하자', '프로젝트 시작하자', '앱 하나 만들어줘', '서비스 만들어', '새 프로젝트 셋업', 'build an app', 'develop a service', 'auto-dev', '딸깍' 요청에 트리거. 기존 코드 수정, 버그 픽스, 리팩터링에는 사용하지 않는다 — 처음부터 신규 앱/서비스를 만드는 요청에만 사용할 것. idea-forge로 아이디어를 이미 검증한 경우에도 이 스킬을 사용하여 구현까지 진행한다."
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

verify-loop가 동작 검증(#32), UI 패리티(#33), 사용성 테스트(#34), C-suite 론칭 디베이트(#35), 완성 보고(#36)를 수행한다.

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

---

## NEVER 규칙

1. NEVER: Phase 게이트를 건너뛰지 마라. Idea→Design은 CEO #8 PASS 필수, Design→Build는 CTO #25 PASS 필수.
2. NEVER: 에이전트가 다른 에이전트를 직접 호출하지 마라. 모든 에이전트 호출은 해당 Phase의 스킬(오케스트레이터)을 통해서만 수행한다.
3. NEVER: 루프 상한(10회)을 초과하여 재시도하지 마라. 10회 도달 시 설계문서의 섹션 9 루프 소진 테이블에 따라 처리한다.
4. NEVER: 동일 Phase 내에서 단계 순서를 변경하지 마라. (예외: #27 구현은 병렬 허용)

## ALWAYS 규칙

1. ALWAYS: 리뷰/검증 단계에서는 수학적 채점(기준별 0~10 × 가중치 → 총점)으로 PASS/FAIL을 판정한다. PASS: 총점 > 8.0 AND 주요 기준 >= 7.
2. ALWAYS: Phase 전환 시 이전 Phase의 전체 산출물을 다음 Phase에 전달한다.
3. ALWAYS: 실패 복귀 시 복귀 대상 단계의 산출물만 재생성한다. 그 이전 단계의 산출물은 유지한다.
4. ALWAYS: 📄 문서화 단계(#9, #16, #22, #26, #31)는 doc-loop 스킬을 자동(B) 모드 + LLM 모드로 호출한다.

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
