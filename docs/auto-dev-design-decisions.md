---
name: auto-dev-design-decisions
description: auto-dev 스킬 설계 토의 전체 현황. 확정 결정, 구현 작업 목록 포함. 구현 완료 시 삭제.
type: temp
expires_when: auto-dev 스킬 및 관련 에이전트 구현 완료
---

# auto-dev 파이프라인 설계 현황

> 최종 업데이트: 2026-03-24
> 상태: **설계 완료 — 구현 대기**

## 1. 컨셉

"앱 하나 만들어" → 딸-깍 → 동작하는 앱. 사람 개입 최소화한 전자동 개발 파이프라인.

### Scope

**IN-SCOPE**: 아래 조건을 모두 만족하는 요청만 auto-dev로 처리한다:
- 신규 앱 또는 서비스를 처음부터 만드는 요청
- 결과물이 동작하는 코드베이스인 요청
- 웹앱, 모바일앱(React Native), 또는 백엔드 API 중 하나 이상을 포함하는 요청

**OUT-OF-SCOPE**: 아래 요청은 auto-dev가 처리하지 않는다. 해당 요청 수신 시 "auto-dev는 신규 앱/서비스 개발 전용입니다." 응답 후 종료:
- 기존 코드 수정, 버그 수정, 리팩터링
- 인프라 배포, CI/CD 설정, 서버 관리
- 문서 작성, 데이터 분석, 비개발 업무

### NEVER 규칙

1. NEVER: 사용자 승인 없이 Phase 게이트를 건너뛰지 마라. Idea→Design은 CEO #8 PASS 필수, Design→Build는 CTO #25 PASS 필수.
2. NEVER: 에이전트가 다른 에이전트를 직접 호출하지 마라. 모든 에이전트 호출은 해당 Phase의 스킬(오케스트레이터)을 통해서만 수행한다.
3. NEVER: 루프 상한(10회)을 초과하여 재시도하지 마라. 10회 도달 시 반드시 섹션 9의 루프 소진 테이블에 따라 처리한다.
4. NEVER: SKIP 불가 단계(섹션 9 정의)의 실패를 무시하고 다음 단계로 진행하지 마라.
5. NEVER: 동일 Phase 내에서 단계 순서를 변경하지 마라. #10→#11→...→#25 순서는 고정이다. (예외: #27 구현은 병렬 허용)

### ALWAYS 규칙

1. ALWAYS: 리뷰/검증 단계에서는 수학적 채점(기준별 0~10 × 가중치 → 총점)으로 PASS/FAIL을 판정한다. PASS: 총점 > 8.0 AND 주요 기준 >= 7.
2. ALWAYS: Phase 전환 시 이전 Phase의 전체 산출물을 다음 Phase에 전달한다.
3. ALWAYS: 실패 복귀 시 복귀 대상 단계의 산출물만 재생성한다. 그 이전 단계의 산출물은 유지한다.
4. ALWAYS: 📄 문서화 단계(#9, #16, #22, #26, #31)는 doc-loop 스킬을 자동(B) 모드 + LLM 모드로 호출하여 실행한다. doc-loop 내부에서 doc-writer-llm → parity check → doc-critic 루프가 PASS할 때까지 최대 5라운드 반복한다.

## 2. 전체 파이프라인

| Phase | # | 이름 | 에이전트 | 스킬 | 실패 시 |
|---|---|---|---|---|---|
| **Idea** | 1 | 입력 분류 | — (메인 모델) | **auto-dev/idea-forge** | — |
| | 2 | 브레인스토밍 (선택) | CEO + 사용자 | **auto-dev/idea-forge** | — |
| | 3 | 트렌드 스코어링 (선택) | trend-scorer | **auto-dev/idea-forge** | — |
| | 4 | 방향 결정 + 아이디어 제시 | CEO | **auto-dev/idea-forge** | — |
| | 5 | 시장 조사 | researcher | **auto-dev/idea-forge** | — |
| | 6 | 전략 검증 | CSO | **auto-dev/idea-forge** | No-Go → 4 (최대 10회) |
| | 7 | BM 설계 | bm-designer | **auto-dev/idea-forge** | — |
| | 8 | Idea 최종 의사결정 | CEO | **auto-dev/idea-forge** | BM 수정→7 / 변경→4 (최대 10회) |
| | 9 | 📄 Idea Brief 문서화 | doc-writer-llm | **auto-dev/idea-forge** | — |
| **Design** | 10 | 기술 스택 + API 표준/규칙 | CTO | **auto-dev/design-loop/architecture-loop** | — |
| | 11 | DB 스키마 설계 | data-engineer | **auto-dev/design-loop/architecture-loop** | — |
| | 12 | DB 리뷰 | CTO | **auto-dev/design-loop/architecture-loop** | FAIL → 11 (최대 10회) |
| | 13 | API 상세 설계 | backend-dev | **auto-dev/design-loop/architecture-loop** | — |
| | 14 | API 리뷰 | CTO | **auto-dev/design-loop/architecture-loop** | FAIL → 13 (최대 10회) |
| | 15 | DB-API 정합성 검증 | CTO | **auto-dev/design-loop/architecture-loop** | FAIL(스키마)→#11, FAIL(엔드포인트)→#13, FAIL(양쪽)→#11 순차 (최대 10회) |
| | 16 | 📄 Arch Spec 문서화 | doc-writer-llm | **auto-dev/design-loop/architecture-loop** | — |
| | 17 | UX 설계 | product-designer | **auto-dev/design-loop/ux-ui-loop** | — |
| | 18 | UX 검증 (페르소나/플로우) | ux-reviewer | **auto-dev/design-loop/ux-ui-loop** | FAIL → 17 (최대 10회) |
| | 19 | UI 디자인 | product-designer | **auto-dev/design-loop/ux-ui-loop** | — |
| | 20 | UI 검증 (비주얼/트렌드) | ui-reviewer | **auto-dev/design-loop/ux-ui-loop** | FAIL → 19 (최대 10회) |
| | 21 | 디자인 디베이트 (정합성) | ux-reviewer ↔ ui-reviewer (메인 모델 중재) | **auto-dev/design-loop/ux-ui-loop** | 합의 실패→CTO (최대 10회) |
| | 22 | 📄 UX-UI Spec 문서화 | doc-writer-llm | **auto-dev/design-loop/ux-ui-loop** | — |
| | 23 | 실행 계획 + 파일 구조 | planner | **auto-dev/design-loop/plan-loop** | — |
| | 24 | 설계+계획 검증 | plan-critic | **auto-dev/design-loop/plan-loop** | FAIL(아키텍처)→#10, FAIL(UX/UI)→#17, FAIL(실행계획)→#23, FAIL(복합)→#10 순차 (최대 10회) |
| | 25 | Design 최종 의사결정 | CTO | **auto-dev/design-loop** | FAIL(아키텍처)→#10, FAIL(UX/UI)→#17, FAIL(실행계획)→#23, FAIL(복합)→사용자 보고 (최대 10회) |
| | 26 | 📄 Design Spec 문서화 | doc-writer-llm | **auto-dev/design-loop** | — |
| **Build** | 27 | 구현 (병렬) | frontend/backend/mobile/ai | **auto-dev/build-loop** | — |
| | 28 | 마이그레이션/쿼리 리뷰 | DBA | **auto-dev/build-loop** | 지적 → #27 (최대 10회) |
| | 29 | 코드 리뷰 (병렬) | code-reviewer, security-reviewer | **auto-dev/build-loop** | 지적 → #27 (최대 10회) |
| | 30 | 테스트 | qa-engineer | **auto-dev/build-loop** | FAIL → #27 (최대 10회) |
| | 31 | 📄 Build Summary 문서화 | doc-writer-llm | **auto-dev/build-loop** | — |
| **Verify** | 32 | 동작 검증 | simulator | **auto-dev/verify-loop** | FAIL → #27 (2회 연속 동일 에러 → #23, 최대 10회) |
| | 33 | UI 검증 | ui-reviewer | **auto-dev/verify-loop** | FAIL → 19 (최대 10회) |
| | 34 | 사용성 테스트 (페르소나 모킹) | user-tester | **auto-dev/verify-loop** | FAIL → 17 (최대 10회) |
| | 35 | C-suite 론칭 디베이트 | CEO ↔ CTO ↔ CSO (메인 모델 중재) | **auto-dev/verify-loop** | 코드 수정(Build 범위)→#27 / 설계 변경(Design/Idea 범위)→사용자 보고 (최대 10회) |
| | 36 | 완성 보고 | — (메인 모델) | **auto-dev/verify-loop** | — |

> **"---" 표기 규칙**: "---"은 해당 단계에 전용 실패 복귀 루프가 없음을 의미한다:
> - **후속 리뷰가 있는 단계** (#11→#12, #13→#14, #17→#18, #19→#20, #23→#24, #27→#28/#29/#30): 후속 리뷰에서 FAIL 시 복귀하여 재작성.
> - **리뷰 없이 통과하는 단계** (#1, #2, #3, #4, #5, #7, #10, #36): 산출물 생성 후 즉시 진행. 시스템 실패는 섹션 9 참조.
> - **📄 문서화 단계** (#9, #16, #22, #26, #31): doc-loop 스킬(자동 모드, LLM 모드)을 호출. 내부에서 doc-writer-llm → parity check → doc-critic 채점 루프를 PASS까지 실행(최대 5라운드). 흡수 규칙은 섹션 2.1 참조.
> - **ⓢ = Skip 가능**: #2(브레인스토밍), #3(트렌드 스코어링)은 입력 분류(#1)에 따라 건너뛸 수 있다.

### 2.1. 문서 라이프사이클 (흡수 후 삭제)

동시 존재 문서를 최소화하기 위해, 후속 문서가 이전 문서를 흡수하면 이전 문서를 삭제한다.

```
idea-brief.md (#9) ──────────────┐
                                  │
arch-spec.md (#16) ──────────────┤
                                  ├→ design-spec.md (#26) 생성 → 3개 삭제
ux-ui-spec.md (#22) ─────────────┤
                                  │
실행계획+CTO승인 ─────────────────┘

design-spec.md (#26) ─────────────── Verify Phase까지 유지 (기대 동작 기준)
build-summary.md (#31) ──────────── Verify Phase까지 유지 (실제 구현 기준)
```

| 문서 | 생성 | 삭제 시점 | 내용 |
|------|------|----------|------|
| `idea-brief.md` | #9 | #26 생성 시 흡수 삭제 | 앱명, 타겟, BM, 시장 요약 |
| `arch-spec.md` | #16 | #26 생성 시 흡수 삭제 | 기술스택, DB, API, 정합성, 테스트 도구 |
| `ux-ui-spec.md` | #22 | #26 생성 시 흡수 삭제 | 페르소나, 플로우, 디자인시스템, 목업 |
| `design-spec.md` | #26 | 파이프라인 종료 시 | 위 3개 흡수 + 실행계획 + CTO 승인 |
| `build-summary.md` | #31 | 파이프라인 종료 시 | 구현 파일, 테스트 결과, 실행방법 |

**동시 존재 최대**: 3개 (#22~#26 구간: idea-brief + arch-spec + ux-ui-spec)
**Verify Phase 시점**: 2개 (design-spec + build-summary)

## 3. 입력 분류 (#1)

메인 모델이 아래 판별 규칙을 **우선순위 순서대로** 적용하여 입력을 분류한다. 첫 번째로 매칭되는 유형으로 확정한다.

| 우선순위 | 유형 | 판별 조건 | 예시 | 시작 단계 |
|---|---|---|---|---|
| 1 | 같이 고민 | 입력이 질문형("~할까", "~좋을까", "어떤 게", "뭐가")이거나 명시적 협의 요청("같이", "고민", "추천") 포함 | "뭐가 좋을까", "같이 앱 아이디어 고민해줘" | #2 (브레인스토밍) → 확정 후 #3 or #4 진입 |
| 2 | 막연한 요청 | 입력에 구체적 앱 이름이나 기능 설명이 없고, 목적/조건만 제시 | "돈 되는 앱 만들어", "요즘 뜨는 거 만들어" | #3 (트렌드부터) |
| 3 | 아이디어 있음 | 입력에 구체적 앱 유형, 이름, 또는 핵심 기능이 1개 이상 명시 | "할일 앱 만들어", "레시피 공유 SNS 만들어" | #4 (CEO 정제부터, 트렌드 스킵) |

**매칭 실패 시**: 어떤 유형에도 해당하지 않는 경우, 사용자에게 "아이디어가 이미 정해져 있나요, 함께 고민하고 싶으신가요?" 확인 후 응답에 따라 분류한다.

## 4. Phase별 게이트키퍼

| 전환 | 게이트 | 담당 | 판단 기준 |
|---|---|---|---|
| Idea → Design | #8 | CEO | 비즈니스 비전과 맞는가 |
| Design → Build | #25 | CTO | 기술적으로 구현 가능하고 설계가 충분한가 |
| Build → Verify | — (게이트 없음) | — | Build 내부 리뷰(DBA/QA/코드리뷰)로 충분 |

## 5. 디베이트

### 2자 실행 프로토콜 (#21 디자인 디베이트)

1. 메인 모델이 논제(검증 대상 산출물 + 쟁점)를 양측 에이전트에게 동시 전달한다.
2. 각 에이전트는 review-verdict 템플릿으로 응답한다 (채점 + 피드백).
3. 메인 모델이 양측 피드백을 교환하고, 상충 항목 목록을 추출한다.
4. 상충 항목이 0개 → **합의 성립**. 양측 피드백을 병합하여 debate-result 템플릿으로 최종 verdict 생성.
5. 상충 항목이 1개 이상 → 각 에이전트에게 상충 항목만 재평가 요청. 이것이 **1라운드**.
6. 재평가 후 상충 항목이 0개 → 합의 성립 (단계 4와 동일).
7. 재평가 후에도 상충 → 다음 라운드 (단계 5로 복귀). **10라운드 소진 시 합의 실패**.

### 3자 디베이트 프로토콜 (#35 론칭 디베이트)

1. 메인 모델이 논제(전체 산출물 + 론칭 적합성)를 3개 에이전트(CEO, CTO, CSO)에게 동시 전달한다.
2. 각 에이전트는 review-verdict 템플릿으로 응답한다 (채점 + 피드백).
3. 메인 모델이 3개 피드백에서 상충 항목을 추출한다. 비교 쌍: CEO↔CTO, CTO↔CSO, CEO↔CSO (총 3쌍).
4. 상충 항목이 0개 → **합의 성립**. 3개 피드백을 병합하여 debate-result 템플릿으로 최종 verdict 생성.
5. 상충 항목이 1개 이상 → 각 에이전트에게 상충 항목 + 나머지 2명의 의견을 전달, 재평가 요청. 이것이 **1라운드**.
6. 재평가 후 상충 항목이 0개 → 합의 성립 (단계 4와 동일).
7. 재평가 후에도 상충 → 다음 라운드 (단계 5로 복귀). **10라운드 소진 시 사용자에게 3자 불일치 현황과 함께 점검 요청**.

### 합의 실패 시

| 디베이트 | # | 참여 | 합의 실패 시 |
|---|---|---|---|
| 디자인 디베이트 | #21 | ux-reviewer ↔ ui-reviewer (2자) | CTO가 양측 verdict를 입력받아 최종 판정 (review-verdict 템플릿 출력) |
| 론칭 디베이트 | #35 | CEO ↔ CTO ↔ CSO (3자) | 10라운드 소진 → 사용자에게 3자 verdict + 상충 항목 목록 전달, 점검 요청 (human-in-loop) |

## 6. 스킬 계층

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

각 스킬은 독립 사용 가능.

## 7. 확정된 결정사항

### 에이전트
- [x] **sys-architect 삭제 → CTO 신설**: C-suite 트리오 (CEO/CSO/CTO). 기술 스택, API 표준, 아키텍처 리뷰, Phase 게이트키퍼.
- [x] **database-reviewer → DBA 리네이밍**: 역할 동일 (쿼리 최적화, 마이그레이션 리뷰, 보안). Build Phase 리뷰 담당.
- [x] **trend-scorer 신설**: trend-score 스킬 로직을 에이전트로. 스킬은 래퍼로 유지.
- [x] **bm-designer 신설**: bm-design 스킬 로직을 에이전트로. 스킬은 래퍼로 유지.
- [x] **ux-reviewer 신설**: 페르소나 기반 UX 플로우 검증. #18, #21 담당.
- [x] **ui-reviewer 신설**: UI 비주얼/트렌드 검증. #20, #21, #33 담당.
- [x] **user-tester 신설**: 페르소나 모킹 사용성 테스트. #34 담당. FAIL → #17(UX 설계) 복귀.
- [x] **product-manager 불필요**: CEO가 아이디어 정제 + 브레인스토밍 담당.
- [x] **product-designer UX/UI 분리 안 함**: 실무에서도 겸업 일반적. 검증은 ux-reviewer/ui-reviewer가 분리 담당.

### 스킬
- [x] **스킬이 스킬을 부르는 최대 4단계 계층 구조** (위 스킬 계층 참고, doc-loop 유틸리티 호출 포함)
- [x] **trend-score, bm-design 스킬**: 각각 trend-scorer, bm-designer 에이전트의 래퍼로 변경
- [x] **service-dev → auto-dev로 대체**: auto-dev가 완전 상위호환. service-dev 폐기.
- [x] **idea-forge에 입력 분류 + 브레인스토밍 흡수**: idea-forge가 자기 완결적으로 동작

### 에이전트 설계 원칙
- [x] **에이전트 정의는 가볍게, 도메인 지식은 외부 refs로 분리**: 에이전트 .md는 역할/행동만 정의. 상세 체크리스트, 기준, 가이드는 refs/ 디렉토리에 별도 문서로. refs 개별 업데이트 가능하고, 여러 에이전트가 같은 refs 참조 가능.

### 설계 정책
- [x] **전 리뷰/검증 에이전트 수학적 채점**: 기준별 0~10점 × 가중치 → 총점. PASS: 총점 > 8.0 AND 주요 기준(최고 가중치) >= 7. 채점 기준은 각 에이전트 refs에 정의.
  - CTO: #12 DB, #14 API, #15 정합성, #25 게이트
  - ux-reviewer: #18 태스크완료(30%)>=7, 총점>8.0
  - ui-reviewer: #20 비주얼 — 계층(25%)>=7 AND 일관성(25%)>=7, 총점>8.0. #33 패리티 — 레이아웃(30%)>=7, 총점>8.0
  - user-tester: #34 완료율(30%)>=7, 총점>8.0
- [x] **설계문서 게이트**: auto-dev 한정, 사람 승인 대신 plan-critic + CTO가 PASS/FAIL 검증
- [x] **전문가 설계 + CTO 리뷰 패턴**: DB는 data-engineer→CTO 리뷰, API는 backend-dev→CTO 리뷰
- [x] **DB-API 정합성 검증(#15)**: CTO가 DB 스키마와 API 상세 설계의 크로스체크
- [x] **UX 검증 → UI 검증 → 디베이트 순서**: 각각 먼저 검증 후 정합성만 디베이트
- [x] **디자인 디베이트 패턴 (#21)**: ux-reviewer↔ui-reviewer 교차 토론. 메인 모델 중재. 합의 실패 → CTO 판정.
- [x] **C-suite 론칭 디베이트 (#35)**: CEO↔CTO↔CSO 3자 토론. 코드 수정(Build 범위)→#27, 설계 변경(Design/Idea 범위)→사용자 보고(human-in-loop). 10라운드 불일치→사용자 점검 요청.
- [x] **파일 구조는 planner에 흡수**: #23(실행 계획)에서 파일 구조도 함께 결정
- [x] **Figma 폐기, Stitch 전환**: Figma 워크플로우 전면 제거. 웹앱→HTML/CSS 목업, 네이티브/RN→Google Stitch MCP. CTO 기술 스택 결정에 따라 자동 선택.
- [x] **모바일 기본값: React Native**, Flutter 고려 대상에서 완전 제외
- [x] **전 루프 상한 10회**: 모든 실패 복귀 루프는 최대 10회
- [x] **Build → Verify 게이트 불필요**: Build 내부 리뷰(DBA/QA/코드리뷰)로 충분
- [x] **문서 라이프사이클**: sub-skill 경계마다 doc-writer-llm이 LLM용 문서 생성. 후속 문서가 이전 문서를 흡수 후 삭제. Verify 시점 동시 존재 문서 최대 2개.
- [x] **MCP 도구 매핑은 CTO 기술 스택에서 결정**: 에이전트 정의에 특정 MCP를 하드코딩하지 않음. CTO가 #10에서 testing_tools를 결정하고 design-spec.md에 기록. 후속 에이전트는 design-spec을 참조하여 도구 선택.
- [x] **📄 문서화 단계는 doc-loop 재사용**: 자체 품질 루프를 구현하지 않고 기존 doc-loop 스킬을 자동(B) + LLM 모드로 호출. 최대 깊이 4단계(auto-dev→design-loop→architecture-loop→doc-loop)이나 doc-loop은 도메인 서브-Phase가 아닌 유틸리티 호출.

## 8. 구현 작업 목록 (TODO)

### 신설 에이전트 (7개)
- [ ] CTO (sys-architect 대체). opus. 8곳 등장(#10,#12,#14,#15,#21합의실패,#24루프소진,#25,#35). refs 10개 (sys-architect 이관 4 + 신규 6). trade-off framework + ADR로 기술 결정. 리뷰는 수학적 채점 (PASS: >8.0 AND 주요>=7). 디베이트 판정은 양측 종합.
- [ ] trend-scorer. opus. trend-score 스킬 로직 그대로. WebSearch/WebFetch. 6개 지표 스코어링.
- [ ] bm-designer. opus. bm-design Phase 3+4+6만 (수익 모델 + 유닛 이코노믹스 + BM Score). 문서 생성 제외. WebSearch/WebFetch.
- [ ] ux-reviewer (#18, #21). opus. 페르소나 기반 채점: 태스크완료(30%), 인지부하(25%), 네비게이션(20%), 접근성(15%), 에러복구(10%). refs 분리.
- [ ] ui-reviewer (#20, #21, #33). opus. 비주얼 채점: 일관성(25%), 트렌드(20%), 계층(25%), 반응형(15%), 접근성(15%). #33은 별도 디자인 패리티 채점. refs 분리.
- [ ] user-tester (#34). opus. 페르소나 모킹 채점: 완료율(30%), 마찰도(25%), 학습용이(20%), 접근성(15%), 만족도(10%). FAIL→#17.
- [ ] DBA (database-reviewer 리네이밍). opus. schema design 제거 (data-engineer/#11 담당). 마이그레이션/쿼리 리뷰만. CTO 참조 추가.

### 기존 에이전트 수정 (2개)
- [ ] product-designer: Figma 워크플로우 전면 제거. 디자인 도구 분기: 웹앱→HTML/CSS 목업, 네이티브/RN→Stitch MCP. Stitch 도구: create_project, generate_screen_from_text, edit_screens, generate_variants. sys-architect→CTO 참조 변경.
- [ ] data-engineer: database-reviewer→DBA 명칭 변경, CTO 협업 관계 추가, model sonnet→opus 변경

### 기존 스킬 수정 (3개)
- [ ] trend-score → trend-scorer 에이전트 래퍼로 변경
- [ ] bm-design → bm-designer 에이전트 래퍼로 변경
- [ ] idea-forge → 파이프라인 확장 (입력 분류, 브레인스토밍, trend-scorer, bm-designer, CEO 게이트, Idea Brief 문서화 반영)

### 신설 스킬 (6개)
- [ ] auto-dev (상위 오케스트레이션)
- [ ] design-loop (Design Phase, 하위 3개 스킬 호출)
- [ ] architecture-loop (#10~#16: 기술 스택, DB, API, 정합성, Arch Spec 문서화)
- [ ] ux-ui-loop (#17~#22: UX, UI, 디베이트, UX-UI Spec 문서화)
- [ ] build-loop (#27~#31: 구현, 리뷰, 테스트, Build Summary 문서화)
- [ ] verify-loop (#32~#36: 동작검증, UI검증, 사용성, 론칭 디베이트, 완성 보고)

### 폐기 (1개)
- [ ] service-dev → auto-dev로 대체 후 삭제

### sys-architect → CTO 마이그레이션
- [ ] sys-architect에서 CTO refs로 이관:
  - [ ] refs/trade-off-framework.md (기술 스택 결정용 1-5 스코어링)
  - [ ] refs/precision-rules.md (vague 용어 금지, 측정 가능한 표현 강제)
  - [ ] refs/adr-template.md (Architecture Decision Record 템플릿)
  - [ ] refs/design-doc-template.md (설계문서 구조)
- [ ] CTO 신규 refs:
  - [ ] refs/tech-stack-guide.md (RN>Flutter, 플랫폼별 기본값, testing_tools 매핑 포함)
  - [ ] refs/db-review-checklist.md (#12 DB 리뷰 기준)
  - [ ] refs/api-review-checklist.md (#14 API 리뷰 기준)
  - [ ] refs/consistency-check.md (#15 DB-API 정합성 검증)
  - [ ] refs/design-gate-criteria.md (#25 Design→Build 게이트)
  - [ ] refs/launch-criteria.md (#35 론칭 판단 기준)
- [ ] sys-architect.md 삭제
- [ ] sys-architect 참조 제거 (CLAUDE.md, 에이전트 정의 내 모든 sys-architect 언급)

### 글로벌 설정 변경
- [ ] CLAUDE.md: auto-dev 스킬 트리거 규칙 추가
- [ ] CLAUDE.md: NEVER 규칙 #5 예외 조건 (auto-dev 한정 에이전트 자동 승인)

## 9. 엣지 케이스 및 실패 처리

### 루프 소진 (10회 도달)

| 루프 위치 | 10회 소진 시 행동 |
|---|---|
| #6 CSO 전략 검증 | 사용자에게 보고: "전략 검증 10회 실패. 아이디어를 근본적으로 재검토 필요." 파이프라인 중단. |
| #8 CEO Idea 게이트 | 사용자에게 보고: "Idea Phase 10회 반복 실패." 파이프라인 중단. |
| #12 DB 리뷰 | CTO가 최종 판정: PASS(위험 수용) 또는 ABORT. ABORT 시 사용자 보고 후 중단. |
| #14 API 리뷰 | #12와 동일. |
| #15 DB-API 정합성 | CTO가 최종 판정: PASS(위험 수용) 또는 ABORT. ABORT 시 사용자 보고 후 중단. |
| #18 UX 검증 | CTO 판정. ABORT 시 사용자 보고. |
| #20 UI 검증 | CTO 판정. ABORT 시 사용자 보고. |
| #21 디자인 디베이트 | CTO 판정 결과를 최종으로 확정. |
| #24 설계+계획 검증 | CTO 게이트(#25)로 에스컬레이션. CTO도 해결 불가 시 사용자 보고 후 중단. |
| #25 Design 게이트 | 사용자에게 보고: "Design Phase 해결 불가." 파이프라인 중단. |
| #28 DBA 리뷰 | CTO 에스컬레이션. 위험 수용 또는 사용자 보고. |
| #29 코드 리뷰 | CTO 에스컬레이션. 위험 수용 또는 사용자 보고. |
| #30 테스트 | 사용자 보고: "테스트 10회 실패. 수동 개입 필요." 중단. |
| #32 동작 검증 | 사용자 보고 후 중단. |
| #33 UI 검증 | 사용자 보고 후 중단. |
| #34 사용성 테스트 | 사용자 보고 후 중단. |
| #35 론칭 디베이트 | 3자 불일치 현황(각 에이전트 verdict + 상충 항목 목록)을 사용자에게 전달, 점검 요청. |

**기본 규칙**: 위 표에 명시되지 않은 루프가 10회 소진 시 → 사용자에게 보고하고 파이프라인 중단.

### 시스템 실패

| 실패 유형 | 처리 |
|---|---|
| 에이전트 응답 없음/타임아웃 | 3회 재시도 (30초 간격). 3회 실패 시 사용자 보고 후 중단. |
| 도구 호출 실패 (WebSearch, Stitch, Bash) | SKIP 가능 단계(#3 트렌드, #5 시장조사): 경고와 함께 진행. SKIP 불가 단계(그 외 모든 단계): 사용자 보고 후 중단. |
| 컨텍스트 윈도우 초과 | 현재 Phase 산출물을 파일로 저장하고, 사용자에게 "컨텍스트 한계 도달. 저장된 산출물로 이어서 진행하세요." 보고. |

### 입력 분류 실패 (#1)

| 상황 | 처리 |
|---|---|
| 개발 요청이 아닌 경우 ("서버 배포해줘", "버그 고쳐줘") | "auto-dev는 신규 앱/서비스 개발 전용입니다. 요청을 확인해주세요." 응답 후 종료. |
| 분류 불확실 (두 유형에 걸침) | 사용자에게 "아이디어가 이미 정해져 있나요, 함께 고민하고 싶으신가요?" 확인 후 진행. |

## 10. 산출물 템플릿

모든 단계의 산출물은 공통 헤더(step, agent, status, timestamp) + 단계별 content 블록으로 구성된다. 템플릿은 `refs/templates/` 디렉토리에 개별 파일로 관리한다.

### 공통 헤더 (모든 템플릿에 포함)

```yaml
step: {단계 번호}
agent: {에이전트 이름}
status: PASS | FAIL | ABORT | ESCALATE
timestamp: {ISO 8601}
```

### 템플릿 파일 목록

| 파일 | 적용 단계 | 설명 |
|---|---|---|
| `refs/templates/brainstorming.yaml` | #2 | 브레인스토밍 (아이디어 목록, 선택 결과, 세션 유형) |
| `refs/templates/trend-scoring.yaml` | #3 | 트렌드 스코어링 (주제별 점수, 모멘텀, 추천 방향) |
| `refs/templates/ceo-direction.yaml` | #4 | CEO 방향 결정 (앱 이름, 타겟 유저, 핵심 기능, 차별점) |
| `refs/templates/market-research.yaml` | #5 | 시장 조사 (TAM/SAM/SOM, 경쟁사, 기회, 리스크) |
| `refs/templates/bm-design.yaml` | #7 | BM 설계 (수익 모델, 가격, 유닛 이코노믹스, BM Score) |
| `refs/templates/idea-brief.yaml` | #9 | 📄 Idea Brief (앱명, 타겟, BM, 시장 요약 통합) |
| `refs/templates/tech-stack.yaml` | #10 | 기술 스택 + API 표준 + testing_tools (프레임워크, DB, 인증, 테스트 도구, ADR 경로) |
| `refs/templates/db-schema.yaml` | #11 | DB 스키마 (ERD Mermaid, 테이블 정의, 인덱스, 마이그레이션 경로) |
| `refs/templates/api-design.yaml` | #13 | API 상세 설계 (엔드포인트, 요청/응답 스키마, 인증 여부) |
| `refs/templates/arch-spec.yaml` | #16 | 📄 Arch Spec (기술스택+DB+API+정합성 통합) |
| `refs/templates/ux-design.yaml` | #17 | UX 설계 (페르소나, 유저 플로우, 와이어프레임 경로) |
| `refs/templates/ui-design.yaml` | #19 | UI 디자인 (디자인 시스템, 화면 목록, 목업 경로, 사용 도구) |
| `refs/templates/ux-ui-spec.yaml` | #22 | 📄 UX-UI Spec (페르소나+플로우+디자인시스템+디베이트 통합) |
| `refs/templates/execution-plan.yaml` | #23 | 실행 계획 (파일 구조, 구현 순서, 병렬 트랙, 설계문서 경로) |
| `refs/templates/design-spec.yaml` | #26 | 📄 Design Spec (idea-brief+arch-spec+ux-ui-spec 흡수+실행계획 통합) |
| `refs/templates/implementation.yaml` | #27 | 구현 (생성/수정 파일, 테스트, 실행 명령) |
| `refs/templates/build-summary.yaml` | #31 | 📄 Build Summary (구현 파일, 테스트 결과, 실행방법) |
| `refs/templates/review-verdict.yaml` | #6,#12,#14,#15,#18,#20,#24,#28,#29,#30,#32,#33,#34 | 리뷰/검증 (채점 기준별 점수, 총점, PASS/FAIL, 피드백). #25는 gate-decision 사용. |
| `refs/templates/gate-decision.yaml` | #8, #25 | 게이트키퍼 결정 (decision, reason, next_step, loop_count) |
| `refs/templates/debate-result.yaml` | #21, #35 | 디베이트 결과 (참여 에이전트, 라운드 수, 합의 요약, 액션 아이템) |
| `refs/templates/escalation.yaml` | 모든 human-in-loop | 사용자 보고 (요약, 상세, 저장된 산출물, 필요 액션) |
| `refs/templates/completion.yaml` | #36 | 완성 보고 (프로젝트명, 기술 스택, 산출물 경로, 실행 방법) |

## 11. 수치 요약

| 항목 | 수량 |
|---|---|
| Phase | 4개 (Idea, Design, Build, Verify) |
| 전체 단계 | 36개 |
| 에이전트 | 21개 (신설 7, 수정 2, 기존 12) |
| 스킬 | 9개 (신설 6, 수정 3) |
| 게이트키퍼 | 2개 (CEO #8, CTO #25) |
| 디베이트 | 2개 (디자인 #21, 론칭 #35) |
| 📄 문서화 단계 | 5개 (#9, #16, #22, #26, #31) |
| 루프 상한 | 전부 10회 |
| human-in-loop (정상 흐름) | 1곳 (#35 론칭 디베이트에서 설계 변경 필요 판정 시) |
| human-in-loop (실패 에스컬레이션) | 루프 소진 또는 시스템 실패 시 사용자 보고 (섹션 9 참조) |
| 동시 존재 문서 최대 | 3개 (#22~#26 구간), Verify 시점 2개 |
