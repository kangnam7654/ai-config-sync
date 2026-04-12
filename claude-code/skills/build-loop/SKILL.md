---
name: build-loop
description: "auto-dev Build Loop (#27-#31). Orchestrates parallel implementation, DBA migration review, code/security review, tests, and Build Summary documentation. Called by auto-dev; also runs standalone."
---

**REQUIRED BACKGROUND:** 공통 loop 패턴은 `skills/_shared/loop-pattern.md` 참조. 이 스킬은 해당 패턴의 specialization이다.
<!-- Override: max 10 rounds instead of shared default 5 -->

# Build Loop

auto-dev 파이프라인의 Build Phase. design-spec.md를 입력받아 구현 → 리뷰 → 테스트 → 문서화를 오케스트레이션한다.

## 워크플로우

```
#27 구현 (frontend/backend/mobile/ai 병렬)
  ↓
#28 마이그레이션/쿼리 리뷰 (DBA) ←─ 지적 → #27 (최대 10회)
  ↓ PASS
#29 코드 리뷰 (code-reviewer + security-reviewer 병렬) ←─ 지적 → #27 (최대 10회)
  ↓ PASS
#30 테스트 (qa-engineer) ←─ FAIL → #27 (최대 10회)
  ↓ PASS
#30.5 설계 정합성 체크 (메인 모델) ←─ 누락 → #27 (최대 5회)
  ↓ PASS
#31 📄 Build Summary 문서화 (doc-loop)
```

---

## #27 구현 (병렬)

design-spec.md의 실행 계획(execution plan)을 읽고, 트랙별로 에이전트를 **병렬** 호출한다:

| 트랙 | 에이전트 | 조건 |
|------|---------|------|
| frontend | frontend-dev | tech_stack.frontend가 N/A가 아닐 때 |
| backend | backend-dev | tech_stack.backend가 N/A가 아닐 때 |
| mobile | mobile-dev | tech_stack.mobile이 "React Native"일 때 |
| ai | ai-engineer | 제품에 AI 기능이 포함될 때 |

각 에이전트에게 전달하는 컨텍스트:
- design-spec.md 전체 (아키텍처, UX/UI, 실행 계획)
- 해당 트랙의 파일 목록 + 구현 순서

각 트랙은 독립적으로 실행되며, 모든 트랙이 완료된 후 #28로 진행한다. 트랙 간 의존성이 있으면 (예: backend API가 있어야 frontend가 호출 가능) 의존 순서대로 순차 실행한다.

**산출물**: implementation.yaml (트랙별)

---

## #28 마이그레이션/쿼리 리뷰 (DBA) [조건부]

**SKIP 조건**: #27에서 생성된 DB/SQL/마이그레이션 파일이 없으면 SKIP → #29로 진행.

**DBA 에이전트**를 파이프라인 모드(Step 5)로 호출한다. 입력: #27에서 생성된 SQL 파일, 마이그레이션 파일.

5기준 채점: 마이그레이션 안전성(30%, primary >=7), 쿼리 성능(25%), 보안(20%), 인덱스 전략(15%), 스키마 준수(10%).

- **PASS** (total > 8.0 AND 마이그레이션 안전성 >= 7) → #29로 진행
- **FAIL** → DBA 피드백(구체적 파일+수정 지시)을 해당 트랙 에이전트에게 전달, #27로 복귀 (해당 트랙만 재구현)

**최대 10회 반복**. 10회 소진 시 CTO 에스컬레이션.

**산출물**: review-verdict.yaml

---

## #29 코드 리뷰 (병렬)

**code-reviewer 에이전트**와 **security-reviewer 에이전트**를 병렬 호출한다. 입력: #27 전체 코드.

각 에이전트가 review-verdict.yaml로 응답:
- 둘 다 **PASS** → #30으로 진행
- 하나라도 **FAIL** → 해당 피드백을 구현 에이전트에게 전달, #27로 복귀

**최대 10회 반복**. 10회 소진 시 CTO 에스컬레이션.

**산출물**: review-verdict.yaml (각 리뷰어별)

---

## #30 테스트 (qa-engineer)

**qa-engineer 에이전트**를 호출한다. 입력: #27 전체 코드 + design-spec.md (기대 동작 기준).

qa-engineer가 단위 테스트 + 통합 테스트를 작성하고 실행한다.

- **PASS** (모든 테스트 통과, 커버리지 >= 80%) → #31로 진행
- **FAIL** → qa-engineer 피드백(실패 테스트 + 원인)을 구현 에이전트에게 전달, #27로 복귀

**최대 10회 반복**. 10회 소진 시 사용자 보고: "테스트 10회 실패. 수동 개입 필요."

**산출물**: review-verdict.yaml

---

## #30.5 설계 정합성 체크 (메인 모델)

design-spec.md에 정의된 항목이 구현에 실제로 존재하는지 **메인 모델이 직접 체크**한다. 서브에이전트 호출 없음 — 체크리스트 매칭만 수행.

### 입력
- design-spec.md의 execution plan 섹션
- #27~#30의 implementation.yaml (트랙별 파일 목록)
- 프로젝트 소스 디렉토리

### 매칭 대상

design-spec의 아래 항목을 **모두** 추출하여 구현 존재 여부를 확인한다:

| 항목 유형 | 매칭 방법 |
|---|---|
| API 엔드포인트 | 백엔드 코드에서 라우터/핸들러 정의 Grep (예: `POST /api/todos` → `router.post('/todos'` 또는 `@app.post("/todos")`) |
| 화면/페이지 | 프론트엔드 코드에서 컴포넌트/라우트 정의 Grep |
| 데이터 모델/테이블 | DB 스키마 파일 또는 ORM 정의 파일에서 모델명 Grep |
| 핵심 기능 (idea-brief의 기능 목록) | API 엔드포인트 OR 화면에 최소 1개 매핑 필요 |

### 판정

- **PASS**: 모든 항목이 구현 파일에 존재 → #31로 진행
- **FAIL**: 누락 항목 존재 → #27로 복귀. 누락 목록을 해당 트랙 에이전트에게 전달.

**최대 5회 반복**. 기존 #28/#29/#30과 달리 상한이 낮은 이유: 이 단계의 실패는 "코드 품질"이 아닌 "구현 범위 누락"이므로 반복해도 근본 해결이 안 되면 설계 문제일 가능성이 크다. 5회 소진 시 CTO 에스컬레이션.

### 실패 케이스

누락 목록 포맷:
```yaml
parity_failure:
  missing_endpoints:
    - method: "POST"
      path: "/api/todos"
      spec_source: "design-spec.md#api-section"
  missing_screens:
    - name: "TodoList"
      spec_source: "design-spec.md#ux-section"
  missing_models:
    - name: "Todo"
      spec_source: "design-spec.md#db-schema"
```

### 왜 #30 이후인가

- #28/#29/#30은 코드 품질(안전성/보안/테스트)을 검증
- #30.5는 **범위 완성도**를 검증
- 테스트(#30)가 먼저 통과해야 의미 있음 — 구현이 동작하는데 누락이 있다면 그것이 "실수로 빠진 범위"
- Verify Phase #32(동작 검증)에 도달하기 전에 누락을 조기 차단하여 Cross-Phase 복귀 비용 절감

**산출물**: parity-verdict.yaml

---

## #31 Build Summary 문서화 (doc-loop)

**doc-loop 스킬**을 자동(B) 모드 + LLM 모드로 호출한다. #27~#30의 모든 산출물을 컨텍스트로 전달.

문서 내용: 구현 파일 목록, 리뷰 결과 (DBA + 코드 + 보안), 테스트 결과 + 커버리지, 실행 방법.

**산출물**: `{project}/docs/llm/build-summary.md`

---

## 루프 소진 에스컬레이션

| 루프 | 소진 횟수 | 소진 시 처리 |
|------|---------|------------|
| #28 DBA 리뷰 | 10회 | CTO 에스컬레이션. 위험 수용 또는 사용자 보고 |
| #29 코드 리뷰 | 10회 | CTO 에스컬레이션. 위험 수용 또는 사용자 보고 |
| #30 테스트 | 10회 | 사용자 보고: "테스트 10회 실패. 수동 개입 필요." 중단 |
| #30.5 정합성 체크 | 5회 | CTO 에스컬레이션. 설계-구현 불일치가 구조적 문제일 수 있음 |

CTO 에스컬레이션 시 auto-dev에게 아래 포맷으로 반환한다:

```yaml
phase_return:
  status: "ESCALATE"
  source_step: "#28"          # 실패가 발생한 단계
  source_phase: "build"       # 항상 "build"
  target_step: "CTO"          # "CTO" 또는 "user"
  target_phase: "escalation"  # 에스컬레이션
  reason: "DBA 리뷰 10회 소진: 인덱스 전략 미충족" # 1줄 요약
  attempt: 10                 # 소진된 횟수
  same_error_consecutive: true
```

## 경계

- 이 스킬은 오케스트레이션만 수행한다. 구현은 frontend/backend/mobile/ai 에이전트, 리뷰는 DBA/code-reviewer/security-reviewer, 테스트는 qa-engineer가 담당.
- Design Phase 산출물(design-spec.md)이 입력 전제 조건이다. design-spec.md가 없으면 실행하지 않고 design-loop 완료를 요청한다.
- Verify Phase는 verify-loop 스킬이 담당한다.
