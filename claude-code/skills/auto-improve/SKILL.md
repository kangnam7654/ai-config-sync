---
name: auto-improve
description: "기존 서비스/앱 종합 진단 + 개선 전자동 파이프라인. 코드베이스를 진단(코드 품질, 보안, 아키텍처, DB, 테스트, UX/UI)하고 우선순위를 매긴 뒤 설계 → 구현 → 검증까지 자동 실행한다. '점검해줘', '개선해줘', '서비스 진단', 'auto-improve', '코드 점검', '서비스 개선', 'improve this app', 'audit this codebase', '리팩터링해줘', '코드베이스 진단', '코드 리뷰하고 고쳐줘', '이 서비스 개선할 점 찾아줘', '전체 점검', '기술 부채 해결', 'tech debt cleanup' 요청에 트리거. 신규 앱 개발(auto-dev), 단순 버그 1개 수정, 인프라/배포에는 사용하지 않는다 — 기존 코드베이스의 종합 진단+개선이 필요한 요청에만 사용할 것."
---

# auto-improve

"이 서비스 점검해줘" → 종합 진단 → 개선 설계 → 구현 → 검증. 기존 코드베이스를 체계적으로 개선하는 전자동 파이프라인.

37단계, 4 Phase(Audit → Design → Build → Verify)를 오케스트레이션한다.

## Scope

**IN-SCOPE**: 아래 조건을 만족하는 요청:
- 기존 코드베이스의 종합 진단 + 개선
- 웹앱, 모바일앱, 백엔드 API, CLI 도구, 라이브러리 모두 포함
- 코드 품질, 보안, 아키텍처, 성능, 테스트, UX/UI 중 하나 이상의 개선

**OUT-OF-SCOPE**: "auto-improve는 기존 코드베이스 진단+개선 전용입니다." 응답 후 종료:
- 신규 앱/서비스 개발 → auto-dev 안내
- 단순 버그 1개 수정 → 직접 수정 안내
- 인프라 배포, CI/CD 설정, 서버 관리
- 문서 작성, 데이터 분석, 비개발 업무

## 스킬 계층

```
auto-improve
  ├── audit-loop (#1~#10)          ← NEW
  │     └── doc-loop (#9)
  ├── design-loop (#10~#26)       ← 재활용
  │     ├── architecture-loop (#10~#16)
  │     │     └── doc-loop (#16)
  │     ├── ux-ui-loop (#17~#22)  ← 조건부
  │     │     └── doc-loop (#22)
  │     ├── plan-loop (#23~#24)
  │     └── doc-loop (#26)
  ├── build-loop (#27~#31)        ← 재활용
  │     └── doc-loop (#31)
  └── verify-loop (#32~#36)       ← 재활용
```

## 워크플로우

```
[사용자 입력: 기존 코드베이스 경로 + 개선 범위(선택)]
  ↓
Audit Phase: audit-loop (#1~#10)
  ↓ #8 CTO 게이트 PROCEED → audit-report.md 산출
Design Phase: design-loop (#10~#26)
  ↓ #25 CTO 게이트 PASS → design-spec.md 산출
Build Phase: build-loop (#27~#31)
  ↓ → build-summary.md 산출
Verify Phase: verify-loop (#32~#36)
  ↓ #35 릴리즈 디베이트 PASS → completion.yaml 산출
[완성 보고 + Before/After 지표]
```

---

## Phase 1: Audit (#1~#9)

**audit-loop 스킬**을 호출한다. 사용자 입력(코드베이스 경로 + 선택적 범위 지정)을 전달.

audit-loop가 대상 분석(#1), 병렬 진단(#2~#8: 코드 품질·보안·아키텍처·DB·테스트·Repo Health·UX/UI), CTO 종합 판정(#9), Audit Report 문서화(#10)를 수행한다.

**Phase 전환 조건**: #9 CTO 게이트 PROCEED (개선 대상이 존재하고 우선순위 확정)

**게이트 결과 분기**:
- PROCEED → Phase 2로 진행
- SKIP → "진단 결과 개선이 필요한 항목이 없습니다." 보고 후 종료
- PARTIAL → 사용자에게 개선 범위 확인 후 진행

**산출물**: audit-report.md (베이스라인 점수, 우선순위별 개선 항목, 개선 범위)

---

## Phase 2: Design (#10~#26)

**design-loop 스킬**을 호출한다.

### 입력 문서 매핑

design-loop은 원래 idea-brief.md를 입력으로 기대한다. auto-improve에서는 audit-report.md가 이를 대체한다. design-loop 호출 시 아래 컨텍스트를 함께 전달하라:

```
입력 문서: audit-report.md (Audit Phase 산출물)
이 문서는 idea-brief.md를 대체한다.
기존 코드베이스 개선 프로젝트이므로:
- architecture-loop: 기존 아키텍처 기반으로 개선 사항만 설계하라
- ux-ui-loop: audit-report.md에서 UX/UI 개선이 필요한 경우에만 실행하라
- plan-loop: 하위호환성과 마이그레이션 경로를 반드시 포함하라
```

### 조건부 서브-루프 실행

audit-report.md의 개선 우선순위에 따라 design-loop 내부 서브-루프를 선택적으로 실행한다:

| audit 결과 | design-loop 내부 실행 |
|---|---|
| 아키텍처/DB/API 개선 필요 | architecture-loop 실행 |
| UX/UI 개선 필요 | ux-ui-loop 실행 |
| 둘 다 필요 | 둘 다 실행 |
| 코드 품질/보안/테스트만 | architecture-loop 최소 실행 (영향 범위 파악) |

plan-loop와 CTO Design 게이트(#25)는 항상 실행한다.

**Phase 전환 조건**: #25 CTO Design 게이트 PASS

**산출물**: design-spec.md (audit-report + arch-spec + ux-ui-spec 흡수 완료)

---

## Phase 3: Build (#27~#31)

**build-loop 스킬**을 호출한다. 입력: design-spec.md.

build-loop가 구현(#27 병렬), DBA 리뷰(#28), 코드/보안 리뷰(#29), 테스트(#30), Build Summary 문서화(#31)를 수행한다.

### auto-improve 추가 컨텍스트

build-loop 호출 시 아래 컨텍스트를 함께 전달하라:

```
기존 코드베이스 개선 프로젝트이므로:
- #27 구현: 기존 코드를 수정/개선하라. 기존 기능을 깨뜨리지 마라.
- #30 테스트: 기존 테스트가 모두 통과하는지 확인하라 (회귀 테스트).
  새 테스트 추가와 함께, 기존 테스트 스위트 전체 실행이 필수다.
```

**Phase 전환 조건**: 게이트 없음 (Build 내부 리뷰로 충분)

**산출물**: build-summary.md

---

## Phase 4: Verify (#32~#36)

**verify-loop 스킬**을 호출한다. 입력: design-spec.md + build-summary.md.

verify-loop가 동작 검증(#32), UI 검증(#33), 사용성 테스트(#34), C-suite 릴리즈 디베이트(#35), 완성 보고(#36)를 수행한다.

### auto-improve 추가 컨텍스트

verify-loop 호출 시 아래 컨텍스트를 함께 전달하라:

```
기존 코드베이스 개선 프로젝트이므로:
- #32 동작 검증: 개선된 기능 + 기존 기능 모두 동작 확인 (회귀 검증).
- #33 UI 검증: 개선 전/후 비교. audit-report.md의 베이스라인 점수와 비교하라.
- #35 릴리즈 디베이트 (4자: CEO/CTO/CSO/CISO): "론칭"이 아니라 "릴리즈" 관점.
  개선 효과 vs 하위호환 리스크를 중심으로 토론하라.
  CISO는 개선 사항이 보안 정책/컴플라이언스에 영향을 미치는지, 새로운 보안 위험을 도입하지 않는지 검증하라.
- #36 완성 보고: Before/After 지표를 반드시 포함하라.
  audit-report.md의 베이스라인 점수 vs 개선 후 점수를 항목별로 비교.
```

**산출물**: completion.yaml (Before/After 지표 포함)

### completion.yaml 확장 필드

```yaml
# auto-improve 전용 필드
improvement_summary:
  baseline_scores:
    code_quality: <audit 시점 점수>
    security: <audit 시점 점수>
    architecture: <audit 시점 점수>
    test_coverage: <audit 시점 점수>
    ux_ui: <audit 시점 점수 또는 N/A>
  final_scores:
    code_quality: <개선 후 점수>
    security: <개선 후 점수>
    architecture: <개선 후 점수>
    test_coverage: <개선 후 점수>
    ux_ui: <개선 후 점수 또는 N/A>
  regression_test_result: PASS/FAIL
  total_improvements: <개선된 항목 수>
  total_findings: <진단에서 발견된 총 항목 수>
```

---

## Cross-Phase 복귀 처리

verify-loop가 FAIL을 반환할 때, 복귀 대상이 다른 Phase에 있을 수 있다. auto-improve가 라우팅을 담당한다:

| verify-loop FAIL | 복귀 대상 | auto-improve 처리 |
|---|---|---|
| #32 FAIL → #27 | Build Phase | build-loop 재실행 |
| #32 FAIL → #23 (2회 동일 에러) | Design Phase | design-loop에 plan-loop 재실행 요청 |
| #33 FAIL → #19 | Design Phase | design-loop에 ux-ui-loop 재실행 요청 (UI부터) |
| #34 FAIL → #17 | Design Phase | design-loop에 ux-ui-loop 재실행 요청 (UX부터) |
| #35 코드 수정 → #27 | Build Phase | build-loop 재실행 |
| #35 설계 변경 → 사용자 | Human-in-loop | 사용자에게 보고, 판단 대기 |
| **회귀 실패** → #27 | Build Phase | build-loop 재실행 (회귀 수정 우선) |

Cross-Phase 복귀 시: 복귀 대상 Phase 스킬을 재실행한다. 이전 Phase의 산출물 중 복귀 대상 이전 단계의 산출물은 유지한다.

문서 라이프사이클 주의: Design Phase 재실행 시 design-spec.md가 이미 존재할 수 있다. 재실행된 서브-루프의 산출물로 design-spec.md를 업데이트한다.

---

## NEVER 규칙

1. NEVER: Phase 게이트를 건너뛰지 마라. Audit→Design은 CTO #8 PROCEED 필수, Design→Build는 CTO #25 PASS 필수.
2. NEVER: 에이전트가 다른 에이전트를 직접 호출하지 마라. 모든 에이전트 호출은 해당 Phase의 스킬(오케스트레이터)을 통해서만 수행한다.
3. NEVER: 루프 상한(10회)을 초과하여 재시도하지 마라. 10회 도달 시 사용자에게 보고 후 판단을 요청한다.
4. NEVER: 동일 Phase 내에서 단계 순서를 변경하지 마라. (예외: #2~#7 진단은 병렬 허용, #27 구현은 병렬 허용)
5. NEVER: 기존 기능을 깨뜨리는 변경을 회귀 테스트 없이 통과시키지 마라.

## ALWAYS 규칙

1. ALWAYS: 리뷰/검증 단계에서는 수학적 채점(기준별 0~10 × 가중치 → 총점)으로 PASS/FAIL을 판정한다. PASS: 총점 > 8.0 AND 주요 기준 >= 7.
2. ALWAYS: Phase 전환 시 이전 Phase의 전체 산출물을 다음 Phase에 전달한다.
3. ALWAYS: 실패 복귀 시 복귀 대상 단계의 산출물만 재생성한다. 그 이전 단계의 산출물은 유지한다.
4. ALWAYS: 문서화 단계(#9, #16, #22, #26, #31)는 doc-loop 스킬을 자동(B) 모드 + LLM 모드로 호출한다.
5. ALWAYS: Verify Phase의 완성 보고(#36)에 Before/After 점수 비교를 포함한다.
6. ALWAYS: audit-report.md의 베이스라인 점수를 모든 Phase에 전달하여 개선 효과 측정의 기준점으로 사용한다.

---

## 문서 라이프사이클

```
audit-report.md (#9) ──────────────┐
                                    │
arch-spec.md (#16) ────────────────┤
                                    ├→ design-spec.md (#26) 생성 → 3개 삭제
ux-ui-spec.md (#22) ───────────────┤
                                    │
실행계획+CTO승인 ───────────────────┘

design-spec.md (#26) ─────────── Verify Phase까지 유지
build-summary.md (#31) ──────── Verify Phase까지 유지
audit-report.md ─────────────── Verify Phase까지 유지 (Before/After 비교용)
```

Verify Phase 시점 동시 존재 문서: 3개 (audit-report + design-spec + build-summary).

auto-dev와의 차이: audit-report.md가 Verify Phase까지 유지된다. Before/After 점수 비교에 필요하기 때문이다. design-spec.md 생성 시 audit-report.md를 흡수하지 않고 별도 보존한다.

---

## 시스템 실패 처리

| 실패 유형 | 처리 |
|---|---|
| 에이전트 응답 없음/타임아웃 | 3회 재시도 (30초 간격). 3회 실패 시 사용자 보고 후 중단. |
| 도구 호출 실패 | SKIP 가능(#5 DB진단, #7 UX/UI진단): 경고와 함께 진행. SKIP 불가: 사용자 보고 후 중단. |
| 컨텍스트 윈도우 초과 | 현재 Phase 산출물을 파일로 저장하고, 사용자에게 보고. |

---

## 경계

- 이 스킬은 **최상위 오케스트레이터**다. 4개 Phase 스킬(audit-loop, design-loop, build-loop, verify-loop)을 순차 호출하고 Cross-Phase 복귀를 라우팅한다.
- 각 Phase 스킬이 내부 단계를 오케스트레이션한다. auto-improve는 개별 단계(#10, #11, ...)를 직접 관리하지 않는다.
- 에이전트를 직접 호출하지 않는다 — Phase 스킬에게 위임하고, Phase 스킬이 메인 모델에 에이전트 호출을 요청한다.
- design-loop, build-loop, verify-loop은 기존 스킬을 그대로 재활용한다. auto-improve가 추가 컨텍스트(개선 프로젝트 특성, audit-report.md 참조 등)를 전달하여 행동을 조정한다.
