---
name: verify-loop
description: "auto-dev Verify Loop (#32-#36). Orchestrates functional testing, UI verification (design parity), usability testing (persona mocking), C-suite launch debate, and completion report. Called by auto-dev; also runs standalone."
---

**REQUIRED BACKGROUND:** 공통 loop 패턴은 `skills/_shared/loop-pattern.md` 참조. 이 스킬은 해당 패턴의 specialization이다.
<!-- Override: max 10 rounds; cross-phase escalation (L1/L2/L3) instead of standard REJECT retry -->

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
- **FAIL** → **3단계 에스컬레이션** 규칙을 적용한다.

### 3단계 에스컬레이션 규칙

| Level | 트리거 | 복귀 대상 | 의미 |
|-------|--------|----------|------|
| **L1** | 최초 FAIL | #27 (Build) | 구현 버그. 해당 트랙에 에러 전달 |
| **L2** | 2회 연속 동일 에러 | #23 (Design/plan-loop) | 실행 계획/아키텍처 결함 가능성 |
| **L3** | L2 복귀 후에도 동일 계열 실패 | #4 (Idea/CEO 방향) 또는 사용자 보고 | 요구사항 자체가 불완전/모순일 가능성 |

**L3 트리거 조건 (OR)**:
- L2 복귀(design-loop 재실행) 후 다시 L2 조건이 성립 (같은 계열 에러 반복)
- L2 복귀 이후 `escalation_level >= 2`인 상태에서 또 다른 동일 계열 에러 발생
- L1+L2 합산 3회 이상 동일 에러

**L3 처리**:
- 1순위: `phase_return`의 `target_phase`를 `idea`로 설정하여 auto-dev에게 Idea Phase 복귀 요청
- 2순위 (Idea Phase에 실패 로그가 충분할 때): 사용자에게 "요구사항 재검토 필요" 보고 후 중단
- 메인 모델이 L3 판정 시 반드시 이전 2개 복귀의 실패 원인을 포함하여 반환

**최대 10회 반복**. 10회 소진 시 사용자 보고 후 중단.

### 에러 동일성 판정

각 FAIL의 에러 메시지를 기록한다. 이전 에러와 현재 에러가 아래 중 **하나라도** 동일하면 "동일 계열 에러"로 판정:
- 같은 화면 + 같은 에러 타입 (기존 기준)
- 같은 파일/모듈을 수정한 후에도 재발 (구조적 문제 시사)
- 같은 design-spec 항목(엔드포인트/컴포넌트/모델) 관련 실패

단순 문자열 일치가 아닌 **근본 원인이 같은지**를 메인 모델이 판정한다.

**산출물**: review-verdict.yaml (escalation_level 포함)

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

## #35 C-suite 디베이트 (4자)

호출자에 따라 디베이트 관점이 달라진다:
- **auto-dev**: 론칭 적합성 (시장 진입 준비 여부)
- **auto-improve**: 릴리즈 적합성 (개선 효과 vs 하위호환 리스크). CISO는 개선 사항이 보안 정책/컴플라이언스에 영향을 미치는지, 새로운 보안 위험을 도입하지 않는지 추가 검증.

4자 디베이트 프로토콜을 실행한다:

1. 메인 모델이 논제(전체 산출물 + 론칭/릴리즈 적합성)를 **CEO, CTO, CSO, CISO** 4개 에이전트에게 동시 전달
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

| FAIL 출처 | 복귀 대상 | 대상 Phase | 처리 | Level |
|----------|----------|-----------|------|-------|
| #32 → #27 | build-loop #27 | Build | auto-dev에게 build-loop 재실행 요청 | L1 |
| #32 → #23 | plan-loop #23 | Design | auto-dev에게 design-loop/plan-loop 재실행 요청 | L2 |
| #32 → #4 | idea-forge #4 | Idea | auto-dev에게 idea-forge 재실행 요청 (CEO 방향부터) | L3 |
| #33 → #19 | ux-ui-loop #19 | Design | auto-dev에게 design-loop/ux-ui-loop 재실행 요청 | L2 |
| #34 → #17 | ux-ui-loop #17 | Design | auto-dev에게 design-loop/ux-ui-loop 재실행 요청 | L2 |
| #35 → #27 | build-loop #27 | Build | auto-dev에게 build-loop 재실행 요청 | L1 |

verify-loop는 자체적으로 다른 Phase의 스킬을 호출하지 않는다. 복귀가 필요하면 auto-dev에게 아래 포맷으로 반환한다:

```yaml
phase_return:
  status: "FAIL"
  source_step: "#32"          # 실패가 발생한 단계
  source_phase: "verify"      # 항상 "verify"
  target_step: "#27"          # 복귀 대상 단계
  target_phase: "build"       # "build", "design", "idea" 중 하나
  reason: "POST /api/todos 500 에러" # 실패 원인 1줄 요약
  attempt: 1                  # 동일 복귀 시도 횟수
  same_error_consecutive: false # 직전 복귀와 동일 계열 에러인지
  escalation_level: 1         # 1=Build, 2=Design, 3=Idea
  prior_failures:             # L3 판정 시 이전 실패 이력 (L1/L2 에서는 비움)
    - level: 1
      target: "#27"
      reason: "POST /api/todos 500 에러"
    - level: 2
      target: "#23"
      reason: "같은 엔드포인트 재실패 (실행 계획 수정 후)"
```

auto-dev가 `target_phase`로 라우팅한다.

## 경계

- 이 스킬은 오케스트레이션만 수행한다. 동작 검증은 simulator, UI 패리티는 ui-reviewer, 사용성은 user-tester, 론칭 판정은 CEO/CTO/CSO/CISO가 담당.
- Build Phase 산출물(build-summary.md)과 Design Phase 산출물(design-spec.md)이 입력 전제 조건이다.
- Cross-Phase 복귀는 auto-dev에게 위임한다. verify-loop가 직접 build-loop이나 design-loop을 호출하지 않는다.
