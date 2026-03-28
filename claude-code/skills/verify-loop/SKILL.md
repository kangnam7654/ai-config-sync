---
name: verify-loop
description: "auto-dev 파이프라인의 Verify Loop (#32~#36). 동작 검증, UI 검증(디자인 패리티), 사용성 테스트(페르소나 모킹), C-suite 론칭 디베이트, 완성 보고를 오케스트레이션한다. auto-dev 스킬이 호출하며, 독립 실행도 가능하다. '앱 검증해줘', '동작 테스트하고 론칭 준비 확인', 'verify loop 실행' 요청에 트리거."
---

# Verify Loop

auto-dev 파이프라인의 마지막 Phase. 구현된 앱의 동작, UI, 사용성을 검증하고, C-suite 론칭 디베이트를 거쳐 완성 보고를 산출한다.

## 워크플로우

```
#32 동작 검증 (simulator)
  ├─ FAIL → #27 (Build로 복귀, 2회 연속 동일 에러 → #23 실행계획 복귀)
  ↓ PASS
#33 UI 검증 (ui-reviewer Mode B)
  ├─ FAIL → #19 (UI 디자인 복귀)
  ↓ PASS
#34 사용성 테스트 (user-tester)
  ├─ FAIL → #17 (UX 설계 복귀)
  ↓ PASS
#35 C-suite 론칭 디베이트 (CEO ↔ CTO ↔ CSO ↔ CISO, 4자)
  ├─ 코드 수정 필요 → #27 (Build로 복귀)
  ├─ 설계 변경 필요 → 사용자 보고 (human-in-loop)
  ├─ 보안 미충족 → #27 (Build로 복귀, 보안 조치 구현)
  ↓ PASS
#36 완성 보고 (메인 모델)
```

---

## #32 동작 검증 (simulator)

**simulator 에이전트**를 호출한다. 입력: build-summary.md의 실행 명령.

simulator가 앱을 실행하고 주요 유저 플로우를 동작 확인한다.

- **PASS** → #33으로 진행
- **FAIL** → #27(구현)로 복귀. 에러 내용을 해당 트랙 에이전트에게 전달.
  - **2회 연속 동일 에러**: #23(실행 계획)으로 복귀. 실행 계획 자체에 문제가 있을 수 있음.

**최대 10회 반복**. 10회 소진 시 사용자 보고 후 중단.

**이전 에러 추적**: 각 FAIL의 에러 메시지를 기록한다. 이전 에러와 현재 에러가 동일하면 (같은 화면, 같은 에러 타입) "동일 에러"로 판정.

**산출물**: review-verdict.yaml

---

## #33 UI 검증 — 디자인 패리티 (ui-reviewer)

**ui-reviewer 에이전트**를 Mode B (Design Parity)로 호출한다.

입력:
- 원본 목업: design-spec.md의 화면별 목업 경로
- 구현 스크린샷: #32 simulator가 캡처한 스크린샷

5기준 채점: 레이아웃 일치(30%, primary >=7), 색상/타이포(25%), 간격/여백(20%), 컴포넌트(15%), 반응형(10%).

- **PASS** (total > 8.0 AND 레이아웃 >= 7) → #34로 진행
- **FAIL** → #19(UI 디자인)로 복귀. 이는 Design Phase의 ux-ui-loop가 다시 실행됨을 의미한다.

**최대 10회 반복**. 10회 소진 시 사용자 보고 후 중단.

**산출물**: review-verdict.yaml

---

## #34 사용성 테스트 (user-tester)

**user-tester 에이전트**를 호출한다. 입력: 실행 중인 앱 + design-spec.md의 페르소나 정의.

5기준 채점: 완료율(30%, primary >=7), 마찰도(25%), 학습 용이성(20%), 접근성(15%), 만족도(10%).

- **PASS** (total > 8.0 AND 완료율 >= 7) → #35로 진행
- **FAIL** → #17(UX 설계)로 복귀. 사용성 문제의 근본 원인이 UX 설계에 있기 때문.

**최대 10회 반복**. 10회 소진 시 사용자 보고 후 중단.

**산출물**: review-verdict.yaml

---

## #35 C-suite 론칭 디베이트 (4자)

4자 디베이트 프로토콜을 실행한다:

1. 메인 모델이 논제(전체 산출물 + 론칭 적합성)를 **CEO, CTO, CSO, CISO** 4개 에이전트에게 동시 전달
2. 각 에이전트가 review-verdict로 응답 (채점 + 피드백)
   - CEO: 시장 적합성, 비즈니스 가치
   - CTO: 기술 품질, 아키텍처 안정성
   - CSO: 전략적 리스크, 재무 타당성
   - CISO: 보안 정책 준수, PII 보호, 컴플라이언스, 위협 모델 적합성
3. 메인 모델이 4개 피드백에서 상충 항목 추출 (6쌍 비교: CEO↔CTO, CEO↔CSO, CEO↔CISO, CTO↔CSO, CTO↔CISO, CSO↔CISO)
4. 상충 0개 → **합의 성립** → debate-result 생성
5. 상충 1개 이상 → 각 에이전트에게 상충 항목 + 나머지 3명 의견 전달, 재평가 요청 (1라운드)
6. 재평가 후 상충 0개 → 합의
7. 재평가 후에도 상충 → 다음 라운드

**10라운드 소진 시**: 사용자에게 4자 verdict + 상충 항목 목록을 전달하고 점검 요청 (human-in-loop).

합의된 결과 처리:
- **PASS** → #36으로 진행
- **코드 수정 필요** (Build Phase 범위) → #27(구현)으로 복귀
- **보안 미충족** (CISO FAIL) → #27(구현)으로 복귀. CISO의 remediation roadmap을 구현 에이전트에게 전달.
- **설계 변경 필요** (Design/Idea Phase 범위) → 사용자에게 보고 (human-in-loop)

**산출물**: debate-result.yaml

---

## #36 완성 보고 (메인 모델)

메인 모델이 전체 파이프라인 산출물을 종합하여 완성 보고를 생성한다.

```yaml
step: "36"
agent: "main-model"
status: "COMPLETE"
timestamp: "{ISO 8601}"
project_name: "{프로젝트 이름}"
tech_stack:
  - "{기술 1}"
  - "{기술 2}"
artifacts:
  design_doc: "{design-spec.md 경로}"
  source_code: "{소스코드 루트 경로}"
  test_report: "{테스트 결과 경로}"
run_method: "{실행 방법 (명령어)}"
total_steps_executed: "{실행된 단계 수}"
total_loops: "{총 루프 횟수}"
human_escalations: "{사용자 보고 횟수}"
```

**산출물**: completion.yaml

---

## Cross-Phase 복귀 처리

이 스킬의 FAIL 복귀 대상은 다른 Phase의 스킬 범위에 해당한다:

| FAIL 출처 | 복귀 대상 | 대상 Phase | 처리 |
|----------|----------|-----------|------|
| #32 → #27 | build-loop #27 | Build | auto-dev에게 build-loop 재실행 요청 |
| #32 → #23 | plan-loop #23 | Design | auto-dev에게 design-loop/plan-loop 재실행 요청 |
| #33 → #19 | ux-ui-loop #19 | Design | auto-dev에게 design-loop/ux-ui-loop 재실행 요청 |
| #34 → #17 | ux-ui-loop #17 | Design | auto-dev에게 design-loop/ux-ui-loop 재실행 요청 |
| #35 → #27 | build-loop #27 | Build | auto-dev에게 build-loop 재실행 요청 |

verify-loop는 자체적으로 다른 Phase의 스킬을 호출하지 않는다. 복귀가 필요하면 auto-dev에게 아래 포맷으로 반환한다:

```yaml
phase_return:
  status: "FAIL"
  source_step: "#32"          # 실패가 발생한 단계
  source_phase: "verify"      # 항상 "verify"
  target_step: "#27"          # 복귀 대상 단계
  target_phase: "build"       # "build" 또는 "design"
  reason: "POST /api/todos 500 에러" # 실패 원인 1줄 요약
  attempt: 1                  # 동일 복귀 시도 횟수
  same_error_consecutive: false # 직전 복귀와 동일 에러인지
```

auto-dev가 `target_phase`로 라우팅한다.

## 경계

- 이 스킬은 오케스트레이션만 수행한다. 동작 검증은 simulator, UI 패리티는 ui-reviewer, 사용성은 user-tester, 론칭 판정은 CEO/CTO/CSO/CISO가 담당.
- Build Phase 산출물(build-summary.md)과 Design Phase 산출물(design-spec.md)이 입력 전제 조건이다.
- Cross-Phase 복귀는 auto-dev에게 위임한다. verify-loop가 직접 build-loop이나 design-loop을 호출하지 않는다.
