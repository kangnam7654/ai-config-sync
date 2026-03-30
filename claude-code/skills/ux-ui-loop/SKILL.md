---
name: ux-ui-loop
description: "auto-dev UX-UI Loop (#17-#22). Orchestrates UX design, UX review, UI design, UI review, design debate, UX-UI Spec documentation. Called by design-loop; also runs standalone."
---

# UX-UI Loop

auto-dev 파이프라인 Design Phase의 두 번째 서브-루프. UX 설계 → 검증 → UI 디자인 → 검증 → 정합성 디베이트 → 문서화를 오케스트레이션한다.

## 워크플로우

```
#17 UX 설계 (designer)
  ↓
#18 UX 검증 (ux-reviewer) ←─ FAIL → #17 (최대 10회)
  ↓ PASS
#19 UI 디자인 (designer)
  ↓
#20 UI 검증 (ui-reviewer) ←─ FAIL → #19 (최대 10회)
  ↓ PASS
#21 디자인 디베이트 (ux↔ui, 메인 모델 중재) ←─ 합의 실패 → CTO 판정 (최대 10회)
  ↓ 합의/판정
#22 📄 UX-UI Spec 문서화 (doc-loop)
```

---

## #17 UX 설계 (designer)

**designer 에이전트**를 호출한다. 입력: idea-brief.md + arch-spec.md (기술 제약).

```
다음 프로젝트의 UX를 설계하라:

제품 정보: {idea-brief.md 요약}
기술 제약: {arch-spec.md의 design_tool, tech_stack 요약}

산출물:
1. 페르소나 정의 (이름, 나이, 역할, 목표, 페인포인트, 기술 수준)
2. 유저 플로우 (화면→액션 시퀀스)
3. 정보 구조 (IA, 섹션 트리)
4. 와이어프레임/목업 경로
```

**산출물**: ux-design.yaml

---

## #18 UX 검증 (ux-reviewer)

**ux-reviewer 에이전트**를 호출한다. 입력: #17 산출물.

5기준 채점: 태스크 완료(30%, primary >=7), 인지 부하(25%), 네비게이션(20%), 접근성(15%), 에러 복구(10%).

- **PASS** (total > 8.0 AND 태스크 완료 >= 7) → #19로 진행
- **FAIL** → ux-reviewer 피드백을 designer에게 전달, #17로 복귀

**최대 10회 반복**. 10회 소진 시 CTO 판정.

**산출물**: review-verdict.yaml

---

## #19 UI 디자인 (designer)

**designer 에이전트**를 호출한다. 입력: #17 UX 설계 (검증 통과) + arch-spec.md.

```
검증 완료된 UX 설계를 기반으로 UI를 디자인하라:

UX 설계: {#17 산출물}
디자인 도구: {arch-spec.md의 design_tool — HTML/CSS 또는 Stitch MCP}

산출물:
1. 디자인 시스템 (색상, 타이포, 간격, border-radius, 컴포넌트)
2. 화면별 목업 (경로 포함)
3. 사용한 도구
```

**산출물**: ui-design.yaml

---

## #20 UI 검증 (ui-reviewer)

**ui-reviewer 에이전트**를 Mode A (Visual Review)로 호출한다. 입력: #19 산출물.

5기준 채점: 계층(25%, primary >=7), 일관성(25%, primary >=7), 트렌드(20%), 반응형(15%), 접근성(15%).

- **PASS** (total > 8.0 AND 계층 >= 7 AND 일관성 >= 7) → #21로 진행
- **FAIL** → ui-reviewer 피드백을 designer에게 전달, #19로 복귀

**최대 10회 반복**. 10회 소진 시 CTO 판정.

**산출물**: review-verdict.yaml

---

## #21 디자인 디베이트 (ux-reviewer ↔ ui-reviewer)

2자 디베이트 프로토콜을 실행한다:

1. 메인 모델이 논제(#17 UX + #19 UI의 정합성)를 ux-reviewer와 ui-reviewer에게 동시 전달
2. 각 에이전트가 review-verdict로 응답 (채점 + 피드백)
3. 메인 모델이 양측 피드백을 교환, 상충 항목 추출
4. 상충 0개 → 합의 성립 → debate-result 생성
5. 상충 1개 이상 → 각 에이전트에게 상충 항목만 재평가 요청 (1라운드)
6. 재평가 후 상충 0개 → 합의
7. 재평가 후에도 상충 → 다음 라운드 (단계 5로 복귀)

**10라운드 소진 시**: CTO 에이전트를 Design Debate Arbitration 모드(Mode 5)로 호출. CTO가 최종 판정.

**산출물**: debate-result.yaml

---

## #22 UX-UI Spec 문서화 (doc-loop)

**doc-loop 스킬**을 자동(B) 모드 + LLM 모드로 호출한다. #17~#21의 모든 산출물을 컨텍스트로 전달.

문서 내용: 페르소나, 유저 플로우, IA, 디자인 시스템 (색상/타이포/간격), 화면별 목업, 디베이트 결과.

**산출물**: `{project}/docs/llm/ux-ui-spec.md`

이 문서는 design-spec.md (#26) 생성 시 흡수되어 삭제된다.

---

## 루프 소진 에스컬레이션

| 루프 | 10회 소진 시 |
|------|------------|
| #18 UX 검증 | CTO 판정. ABORT 시 사용자 보고 |
| #20 UI 검증 | CTO 판정. ABORT 시 사용자 보고 |
| #21 디베이트 | CTO 판정 결과를 최종으로 확정 |

## 경계

- 이 스킬은 오케스트레이션만 수행한다. UX/UI 설계는 designer, UX 검증은 ux-reviewer, UI 검증은 ui-reviewer가 담당.
- 아키텍처 설계는 architecture-loop가 담당한다.
- 디베이트 합의 실패 시 CTO가 판정하지만, CTO 호출은 이 스킬이 메인 모델에 요청한다.
