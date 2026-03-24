---
name: architecture-loop
description: "auto-dev 파이프라인의 Architecture Loop (#10~#16). 기술 스택 결정, DB 스키마 설계/리뷰, API 설계/리뷰, DB-API 정합성 검증, Arch Spec 문서화를 오케스트레이션한다. design-loop 스킬이 호출하며, 독립 실행도 가능하다. '아키텍처 설계해줘', '기술 스택 정하고 DB/API 설계까지', 'architecture loop 실행' 요청에 트리거."
---

# Architecture Loop

auto-dev 파이프라인 Design Phase의 첫 번째 서브-루프. 기술 스택 결정부터 DB-API 정합성 검증까지 오케스트레이션하고, 검증 통과한 아키텍처를 `arch-spec.md`로 문서화한다.

## 워크플로우

```
#10 기술 스택 (CTO)
  ↓
#11 DB 스키마 설계 (data-engineer)
  ↓
#12 DB 리뷰 (CTO) ←─ FAIL → #11 (최대 10회)
  ↓ PASS
#13 API 상세 설계 (backend-dev)
  ↓
#14 API 리뷰 (CTO) ←─ FAIL → #13 (최대 10회)
  ↓ PASS
#15 DB-API 정합성 (CTO) ←─ FAIL(스키마)→#11, FAIL(엔드포인트)→#13, FAIL(양쪽)→#11 순차 (최대 10회)
  ↓ PASS
#16 📄 Arch Spec 문서화 (doc-loop)
```

---

## #10 기술 스택 + API 표준 (CTO)

**CTO 에이전트**를 호출한다. 입력: idea-brief.md (Idea Phase 산출물).

```
idea-brief.md를 읽고 이 프로젝트의 기술 스택을 결정하라.
Tech Stack Decision 모드(Mode 1)로 실행.
```

CTO가 tech-stack YAML + ADR을 산출한다. 이 산출물이 이후 모든 단계의 기술 제약 조건이 된다.

**산출물**: tech-stack.yaml + ADR 파일

---

## #11 DB 스키마 설계 (data-engineer)

**data-engineer 에이전트**를 호출한다. 입력: #10 tech-stack.yaml + idea-brief.md.

```
다음 기술 스택과 제품 요구사항에 맞는 DB 스키마를 설계하라:

기술 스택: {#10 tech-stack.yaml의 database 필드}
제품 요구사항: {idea-brief.md 요약}

산출물: ERD (Mermaid erDiagram), 테이블 정의, 인덱스, RLS 정책, 마이그레이션 경로.
```

**산출물**: db-schema.yaml

---

## #12 DB 리뷰 (CTO)

**CTO 에이전트**를 DB Schema Review 모드(Mode 2)로 호출한다. 입력: #11 산출물.

- **PASS** (total > 8.0 AND primary >= 7) → #13으로 진행
- **FAIL** → CTO 피드백을 data-engineer에게 전달, #11로 복귀

**최대 10회 반복**. 10회 소진 시 CTO가 최종 판정: PASS(위험 수용) 또는 ABORT.

**산출물**: review-verdict.yaml

---

## #13 API 상세 설계 (backend-dev)

**backend-dev 에이전트**를 호출한다. 입력: #10 tech-stack.yaml + #11 db-schema.yaml (리뷰 통과 버전).

```
다음 기술 스택과 DB 스키마에 맞는 API를 설계하라:

기술 스택: {#10 api_standard 필드}
DB 스키마: {#11 산출물}

산출물: 엔드포인트 목록, 요청/응답 스키마, 인증 요구사항.
```

**산출물**: api-design.yaml

---

## #14 API 리뷰 (CTO)

**CTO 에이전트**를 API Design Review 모드(Mode 3)로 호출한다. 입력: #13 산출물.

- **PASS** → #15로 진행
- **FAIL** → CTO 피드백을 backend-dev에게 전달, #13으로 복귀

**최대 10회 반복**. 10회 소진 시 CTO가 최종 판정.

**산출물**: review-verdict.yaml

---

## #15 DB-API 정합성 검증 (CTO)

**CTO 에이전트**를 DB-API Consistency Check 모드(Mode 4)로 호출한다. 입력: #11 db-schema + #13 api-design (둘 다 리뷰 통과 버전).

- **PASS** → #16으로 진행
- **FAIL(SCHEMA_MISMATCH)** → #11로 복귀
- **FAIL(ENDPOINT_MISMATCH)** → #13으로 복귀
- **FAIL(BOTH)** → #11부터 순차 재실행 (#11→#12→#13→#14→#15)

**최대 10회 반복**. 10회 소진 시 CTO가 최종 판정.

**산출물**: review-verdict.yaml (mismatch classification 포함)

---

## #16 Arch Spec 문서화 (doc-loop)

**doc-loop 스킬**을 자동(B) 모드 + LLM 모드로 호출한다. #10~#15의 모든 산출물을 컨텍스트로 전달.

문서 내용: 기술 스택 + ADR, DB 스키마 (ERD, 테이블, 인덱스), API 명세 (엔드포인트, 스키마), DB-API 정합성 결과, 테스트 도구 매핑.

**산출물**: `{project}/docs/llm/arch-spec.md`

이 문서는 design-spec.md (#26) 생성 시 흡수되어 삭제된다.

---

## 루프 소진 에스컬레이션

| 루프 | 10회 소진 시 |
|------|------------|
| #12 DB 리뷰 | CTO 최종 판정: PASS(위험 수용) 또는 ABORT → 사용자 보고 |
| #14 API 리뷰 | CTO 최종 판정: PASS(위험 수용) 또는 ABORT → 사용자 보고 |
| #15 정합성 | CTO 최종 판정: PASS(위험 수용) 또는 ABORT → 사용자 보고 |

## 경계

- 이 스킬은 오케스트레이션만 수행한다. 기술 결정은 CTO, 스키마 설계는 data-engineer, API 설계는 backend-dev가 담당.
- UX/UI 설계는 ux-ui-loop 스킬이 담당한다.
- 실행 계획은 plan-loop 스킬(기존)이 담당한다.
