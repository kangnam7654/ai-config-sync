# service-dev 스킬 설계문서

## 1. 목적

서비스 개발의 전체 라이프사이클(lifecycle, 기획부터 문서화까지의 전 과정)을 오케스트레이션(orchestration, 여러 에이전트/스킬의 실행 순서와 조건을 제어하는 것)하는 Claude Code 스킬을 정의한다.

### 해결하려는 문제

서비스를 개발할 때 기획, 설계, 구현, 문서화가 분절되어 진행되면 산출물 누락과 품질 저하가 발생한다. 각 단계의 진입/종료 조건이 명시되지 않으면 불완전한 상태에서 다음 단계로 넘어가는 문제도 생긴다.

### 성공 기준

- 6개 Phase(phase, 단계)의 진입 조건과 종료 조건이 명확하게 정의되어 있다.
- 각 Phase는 기존 에이전트/스킬을 호출하며, 내부 품질 루프를 재정의하지 않는다.
- Phase 간 산출물 전달 경로가 빠짐없이 기술되어 있다.

## 2. 사전 지식

이 문서를 이해하려면 다음 개념과 도구에 대한 지식이 필요하다.

### 필수 개념

- **Claude Code 스킬 시스템**: SKILL.md 기반 스킬 정의, frontmatter(name, description) 구조
- **글로벌 CLAUDE.md 오케스트레이션**: Writer→Doc-Critic 루프, Planner→Plan-Critic 루프의 동작 방식
- **Critic 루프**: 초안 작성 → Critic 심사 → PASS/REJECT 판정 → REJECT 시 피드백 반영 후 재심사하는 반복 구조

### 필수 도구

- **Claude Code**: 스킬 실행 환경
- **idea-forge 스킬**: Phase 0에서 호출하는 아이디어 발굴/검증 스킬
- **Figma MCP** (선택): Phase 2에서 디자인 작업 시 사용

### 관련 에이전트

| 에이전트 | 역할 |
|---------|------|
| planner | 아키텍처 설계 및 구현 계획 수립 |
| plan-critic | 플랜 품질 심사 |
| doc-writer | 사람용 문서 작성 |
| prompt-writer | AI용 문서 작성 |
| doc-critic | 문서 품질 심사 (HUMAN/LLM 모드) |
| go-reviewer | Go 코드 리뷰 (또는 일반 코드 리뷰 에이전트) |
| e2e-runner | E2E 테스트 실행 |

## 3. 아키텍처

service-dev 스킬은 6개 Phase로 구성된다. 각 Phase는 독립적인 산출물을 생성하고, 게이트(gate, 다음 단계 진입을 위한 필수 조건)를 통과해야 다음 Phase로 진행한다.

### Phase 전체 구조

![Phase 간 상태 전이 다이어그램](./architecture.png)

Phase 0(Ideate)에서 시작하여 Phase 5(Document)까지 순차적으로 진행한다. Phase 2(Design)는 선택적(optional)이다. 사용자가 디자인을 요청하지 않으면 Phase 1에서 Phase 3으로 건너뛴다.

### 핵심 설계 원칙

- **기존 오케스트레이션 위임**: Phase 내부의 Critic 루프는 글로벌 CLAUDE.md에 정의된 구조를 그대로 사용한다.
- **게이트 기반 전환**: 모든 Phase 전환에는 명시적 조건(사용자 승인, Critic PASS 등)이 필요하다.
- **모듈 단위 사이클**: Phase 4에서는 모듈별로 dev→review→refactor→test 사이클을 반복한다.

## 4. Phase별 상세

### Phase 0: Ideate

**역할**: 서비스 아이디어를 확보한다.

**호출 대상**: idea-forge 스킬 (또는 사용자 직접 입력)

**입력**:
- idea-forge 스킬의 산출물 (검증 완료된 아이디어 + BM)
- 또는 사용자가 직접 제공하는 아이디어 (idea-forge 스킵)

**산출물**:
- 서비스 개요
- 핵심 기능 목록
- 타겟 사용자
- BM 요약

**내부 동작**: idea-forge를 호출하는 경우, idea-forge의 자체 워크플로우(Phase 0~2)를 따른다. 사용자가 아이디어를 직접 제공하면 위 4가지 산출물을 정리하여 다음 Phase로 전달한다.

**산출물 예시** (할일 관리 SaaS를 개발하는 경우):

```text
서비스 개요:
  팀 단위 할일 관리 SaaS. Slack 연동으로 할일 생성/알림을 지원한다.

핵심 기능 목록:
  1. 할일 CRUD (생성, 조회, 수정, 삭제)
  2. 팀 워크스페이스 (멤버 초대, 권한 관리)
  3. Slack 연동 (슬래시 커맨드로 할일 생성, 마감일 알림)
  4. 대시보드 (팀별 진행률, 개인별 통계)

타겟 사용자:
  5~20인 규모 스타트업의 개발팀. 기존 도구(Jira, Notion)가 과하다고 느끼는 팀.

BM 요약:
  프리미엄 모델. 5인 이하 무료, 6인 이상 월 $5/인.
  핵심 유료 기능: Slack 연동, 대시보드 통계, API 접근.
```

### Phase 1: Plan

**역할**: 아키텍처를 설계하고 구현 계획을 수립한다.

**호출 대상**: Planner → Plan-Critic 루프 (글로벌 CLAUDE.md 오케스트레이션)

**입력**: Phase 0 산출물 (서비스 개요, 핵심 기능, 타겟, BM)

**산출물**:
- 아키텍처 설계 (`docs/{service-name}/design.md`)
- 기술 스택 선정
- 모듈 분해 (모듈별 책임 정의)
- 구현 순서 (의존성 기반 정렬)
- DB 스키마 (필요 시, ERD 포함)

**내부 동작**: Planner가 초안을 작성하면 Plan-Critic이 심사한다. REJECT 시 피드백을 반영하여 재작성한다. PASS할 때까지 반복하며, 최대 5회로 제한한다.

**Critic 루프 예시**:

```text
[라운드 1] 점수: 6.20 | 결과: REJECT | 피드백: 모듈 간 의존성 미정의
[라운드 2] 점수: 7.80 | 결과: REJECT | 피드백: DB 스키마 누락
[라운드 3] 점수: 8.50 | 결과: PASS | 피드백: 전체 요구사항 충족
```

### Phase 2: Design (Optional)

**역할**: UI/UX 디자인을 제작한다.

**호출 대상**: Figma MCP

**실행 조건**: 사용자가 명시적으로 요청한 경우에만 실행한다.

**입력**: Phase 1 산출물 (아키텍처, 모듈 분해)

**산출물**: Figma 디자인 (wireframe, hi-fi)

**내부 동작**:
1. Wireframe 제작 → 사용자 승인
2. Hi-fi 디자인 제작 → 사용자 승인

각 단계에서 사용자 승인이 필요하다. 승인 없이 다음 단계로 진행하지 않는다.

**Phase 2를 건너뛰는 경우**:
- CLI 도구, 백엔드 API 등 UI가 불필요한 서비스
- Figma MCP가 설정되어 있지 않은 환경

### Phase 3: Spec

**역할**: AI가 개발 시 참조할 스펙 문서를 작성한다.

**호출 대상**: Writer → Doc-Critic 루프 (LLM 모드)

**입력**:
- Phase 1 산출물 (아키텍처, 모듈 분해)
- Phase 2 산출물 (디자인, Phase 2를 실행한 경우)

**산출물**: AI용 개발 스펙 문서 (`docs/{service-name}/spec.md`)

스펙 문서에 포함되는 항목:
- 모듈별 요구사항
- API 스키마 (엔드포인트, 요청/응답 형식)
- 데이터 모델 (엔티티, 관계)
- 에러 처리 규칙
- 코딩 컨벤션 및 제약 조건

**내부 동작**: prompt-writer 또는 doc-writer가 초안을 작성한다. doc-critic이 LLM 모드로 심사한다. PASS할 때까지 반복하며, 최대 5회로 제한한다.

**spec.md 구조 예시** (할일 관리 SaaS의 `todos` 모듈):

```markdown
# 개발 스펙: todos 모듈

## 모듈 요구사항
- 할일의 생성, 조회, 수정, 삭제를 처리한다.
- 할일은 반드시 하나의 워크스페이스에 소속된다.
- 마감일 경과 시 상태를 자동으로 "overdue"로 변경한다.

## API 스키마

### POST /api/todos
요청:
  { "title": string, "due_date": string|null, "assignee_id": string }
응답 (201):
  { "id": string, "title": string, "status": "pending", "created_at": string }
에러:
  400 — title이 빈 문자열인 경우
  403 — 워크스페이스 멤버가 아닌 경우

### GET /api/todos?status={status}&assignee={id}
응답 (200):
  { "items": [...], "total": number, "page": number }

## 데이터 모델
- todos 테이블: id, title, status, due_date, assignee_id, workspace_id, created_at
- status enum: pending, in_progress, done, overdue

## 에러 처리 규칙
- 존재하지 않는 todo_id 접근 시 404를 반환한다.
- assignee_id가 워크스페이스 멤버가 아니면 400을 반환한다.
```

### Phase 4: Build

**역할**: 코드를 구현하고 테스트를 통과시킨다.

**호출 대상**: 개발 에이전트, 코드 리뷰 에이전트, e2e-runner

**입력**: Phase 3 산출물 (`spec.md` 참조)

**산출물**:
- `src/` 디렉토리 (프로덕션 코드)
- `tests/` 디렉토리 (테스트 코드)
- 전체 테스트 통과 + Coverage 80% 이상

#### 모듈별 사이클

각 모듈에 대해 아래 사이클을 반복한다.

```text
1. dev      → 코드 작성 → git commit
2. review   → 코드 리뷰 (go-reviewer 등) → 피드백 반영 → git commit
3. refactor → 가독성 개선, 코드 정리 → git commit
4. test     → Unit 테스트 작성 → 통과 확인 → git commit
```

매 단계에서 git commit을 수행한다. 이렇게 하면 각 단계의 변경 사항을 추적할 수 있다.

**모듈별 사이클 진행 예시** (할일 관리 SaaS의 `todos` 모듈):

```text
=== 모듈: todos ===

[dev] src/todos/router.py — POST/GET/PATCH/DELETE 엔드포인트 구현
      src/todos/service.py — 비즈니스 로직 (상태 전이, 마감일 검증)
      src/todos/models.py — SQLAlchemy 모델 정의
      → git commit -m "feat(todos): implement CRUD endpoints and service layer"

[review] go-reviewer 피드백:
         - service.py: update_todo()에서 status 전이 검증 누락
         - router.py: assignee_id 존재 여부 검증을 service 계층으로 이동
         → 피드백 반영 후
         → git commit -m "fix(todos): add status transition validation, move assignee check to service"

[refactor] service.py: validate_status_transition()을 별도 함수로 추출
           router.py: 응답 직렬화를 schema 클래스로 분리
           → git commit -m "refactor(todos): extract validation logic, separate response schemas"

[test] tests/unit/test_todos_service.py — 상태 전이 10케이스, 마감일 검증 5케이스
       tests/unit/test_todos_router.py — 엔드포인트별 정상/에러 응답
       → 전체 통과 확인
       → git commit -m "test(todos): add unit tests for service and router (15 cases)"

=== 모듈: workspaces === (다음 모듈로 진행)
...
```

#### 모든 모듈 완료 후

모든 모듈의 사이클이 끝나면 아래 검증을 순서대로 수행한다.

1. **통합 테스트**: 모듈 간 연동 검증
2. **E2E 테스트**: e2e-runner 에이전트를 통한 전체 시나리오 검증
3. **Coverage 확인**: Unit 테스트 커버리지 80% 이상 달성 확인

세 가지 검증을 모두 통과해야 Phase 5로 진행한다.

### Phase 5: Document

**역할**: 사람이 읽을 문서를 작성한다.

**호출 대상**: doc-writer → Doc-Critic 루프 (HUMAN 모드)

**입력**: Phase 4 산출물 (완성된 코드, 테스트)

**산출물**:
- `README.md`
- 개발 과정 기록
- API 문서
- 배포 가이드

**내부 동작**: doc-writer가 초안을 작성한다. doc-critic이 HUMAN 모드로 심사한다. HUMAN 모드에서는 사용자가 직접 문서를 평가한다. PASS할 때까지 반복하며, 최대 5회로 제한한다.

**README.md 구조 예시**:

```markdown
# TaskFlow — 팀 할일 관리 SaaS

한 줄 설명: Slack 연동 팀 할일 관리 도구.

## 사전 준비
- Python 3.12+, PostgreSQL 16+, Node.js 20+
- Slack App 생성 및 Bot Token 발급

## 빠른 시작
1. 저장소 클론
2. 환경 변수 설정 (.env.example 참고)
3. DB 마이그레이션 실행
4. 개발 서버 시작

## API 문서
- POST /api/todos — 할일 생성
- GET /api/todos — 할일 목록 조회
- (전체 목록은 docs/taskflow/api.md 참조)

## 배포
- Docker Compose로 로컬 배포
- fly.io 또는 Railway 배포 가이드 (docs/taskflow/deploy.md)
```

**개발 과정 기록 예시**:

```markdown
# 개발 과정 기록

## Phase 0: Ideate (2026-03-20)
- idea-forge에서 "팀 생산성 도구" 주제로 탐색
- CSO 2라운드 만에 Accept

## Phase 1: Plan (2026-03-21)
- Plan-Critic 3라운드 만에 PASS (8.50/10)
- 기술 스택: FastAPI + PostgreSQL + React

## Phase 4: Build (2026-03-22 ~ 03-25)
- 모듈 구현 순서: todos → workspaces → slack-integration → dashboard
- todos 모듈 리뷰에서 상태 전이 검증 누락 발견, 즉시 수정
- 최종 Coverage: 87%
```

## 5. 데이터 흐름

각 Phase의 산출물이 다음 Phase의 입력으로 전달되는 경로를 나타낸다.

![Phase 간 데이터 흐름](./dataflow.png)

### 단계별 전달 경로

| 단계 | 출발 | 산출물 | 도착 | 입력으로 사용되는 항목 |
|------|------|--------|------|----------------------|
| 1 | Phase 0 | 서비스 개요, 핵심 기능, 타겟, BM | Phase 1 | Planner의 설계 컨텍스트 |
| 2 | Phase 1 | 아키텍처, 모듈 분해, 기술 스택 | Phase 2 | 디자인 대상 화면/컴포넌트 식별 |
| 3 | Phase 1 | 아키텍처, 모듈 분해, 구현 순서 | Phase 3 | 스펙 문서의 구조 및 범위 |
| 4 | Phase 2 | Figma 디자인 | Phase 3 | UI 컴포넌트 스펙, 화면 흐름 |
| 5 | Phase 3 | `spec.md` | Phase 4 | 모듈별 구현 요구사항 참조 |
| 6 | Phase 4 | 코드, 테스트 | Phase 5 | 문서화 대상 (API, 설정, 사용법) |

Phase 2를 건너뛴 경우, 단계 4(Phase 2 → Phase 3)는 생략된다. Phase 3은 Phase 1 산출물만으로 스펙 문서를 작성한다.

### 산출물 저장 경로

| Phase | 산출물 | 저장 경로 |
|-------|--------|----------|
| Phase 1 | 아키텍처 설계 | `docs/{service-name}/design.md` |
| Phase 1 | 아키텍처 다이어그램 | `docs/{service-name}/architecture.mmd`, `.png` |
| Phase 3 | AI용 개발 스펙 | `docs/{service-name}/spec.md` |
| Phase 4 | 프로덕션 코드 | `src/` |
| Phase 4 | 테스트 코드 | `tests/` |
| Phase 5 | 사용자 문서 | `README.md`, `docs/` 하위 |

## 6. Phase 간 전환 조건

| 전환 | 게이트 조건 | 비고 |
|------|-----------|------|
| Phase 0 → Phase 1 | 사용자가 아이디어를 승인한다 | idea-forge 산출물 또는 직접 입력 |
| Phase 1 → Phase 2 | Plan-Critic PASS + 사용자 승인 + 사용자가 디자인을 요청한다 | Phase 2는 optional |
| Phase 1 → Phase 3 | Plan-Critic PASS + 사용자 승인 + 디자인 불필요 | Phase 2 건너뜀 |
| Phase 2 → Phase 3 | 사용자가 디자인(wireframe + hi-fi)을 승인한다 | Figma 산출물 확정 |
| Phase 3 → Phase 4 | Doc-Critic PASS (LLM 모드) + 사용자 승인 | spec.md 확정 |
| Phase 4 → Phase 5 | 모든 테스트(unit + 통합 + E2E) 통과 + Coverage 80% 이상 | 자동 검증 |
| Phase 5 → 완료 | Doc-Critic PASS (HUMAN 모드) | 사용자가 문서 품질을 확인 |

모든 Phase 전환에는 하나 이상의 게이트가 존재한다. 게이트를 통과하지 못하면 현재 Phase에 머무른다.

## 7. API 설계

해당 없음.

service-dev는 Claude Code 스킬(SKILL.md)이다. REST API 엔드포인트나 함수 시그니처를 외부에 노출하지 않는다. Phase 간 전환과 산출물 전달은 스킬 내부의 워크플로우 정의로 제어한다.

## 8. 파일 구조

### 스킬 파일

```text
~/.claude/skills/service-dev/
└── SKILL.md              # 스킬 본체 (Phase 정의, 전환 조건, 워크플로우)
```

### 서비스 프로젝트 산출물

```text
{project}/
├── docs/
│   └── {service-name}/
│       ├── design.md          # Phase 1 산출물: 아키텍처 설계
│       ├── spec.md            # Phase 3 산출물: AI용 개발 스펙
│       ├── architecture.mmd   # Phase 1 산출물: 아키텍처 다이어그램 원본
│       └── architecture.png   # Phase 1 산출물: 아키텍처 다이어그램 렌더링
├── README.md                  # Phase 5 산출물: 프로젝트 소개 문서
├── src/                       # Phase 4 산출물: 프로덕션 코드
└── tests/                     # Phase 4 산출물: 테스트 코드
```

`docs/{service-name}/` 경로는 글로벌 CLAUDE.md의 Design-First Development 규칙을 따른다. 이 경로 밖에 설계 문서를 두지 않는다.

## 9. 의사결정 근거

### 채택: Phase 4에서 모듈 단위 사이클 (dev→review→refactor→test)

모듈 단위로 사이클을 반복한다. 각 모듈이 사이클을 완료한 후 다음 모듈로 넘어간다.

**이유**:
- 버그를 조기에 발견할 수 있다.
- 리뷰어가 하나의 모듈에 집중할 수 있어 리뷰 컨텍스트가 유지된다.
- 모듈별로 독립적인 commit 히스토리가 남아 추적이 용이하다.

### 기각: 전체 dev → 전체 review → 전체 refactor → 전체 test

모든 모듈의 코드를 먼저 작성한 후, 전체를 한번에 리뷰하고, 전체를 리팩터링하고, 전체를 테스트하는 방식이다.

**기각 이유**:
- 리뷰 시점에 전체 코드를 파악해야 하므로 컨텍스트 부하가 크다.
- 초반 모듈의 버그가 후반 모듈 작성 완료 후에야 발견된다.
- 리팩터링 범위가 너무 넓어져 회귀(regression, 기존에 동작하던 기능이 깨지는 것) 위험이 높다.

### 채택: Phase 내부 Critic 루프를 재정의하지 않음

스킬은 "어떤 Phase를 언제 실행하는가"만 정의한다. Phase 내부의 품질 루프(Writer→Critic, Planner→Critic)는 글로벌 CLAUDE.md에 정의된 오케스트레이션에 위임한다.

**이유**:
- 글로벌 CLAUDE.md에 이미 Critic 루프가 정의되어 있다. 중복 정의는 유지보수 부담을 높인다.
- 스킬이 Critic 루프를 재정의하면 글로벌 규칙과 충돌할 수 있다.
- 글로벌 규칙이 변경되면 스킬도 자동으로 업데이트된 동작을 따른다.

### 기각: Critic 루프를 스킬 내부에서 재정의

스킬이 자체적으로 Writer→Critic 루프의 최대 반복 횟수, PASS 기준 등을 정의하는 방식이다.

**기각 이유**:
- 글로벌 규칙과 스킬 규칙이 충돌 시 어느 쪽을 우선할지 판단하기 어렵다.
- 글로벌 규칙 변경 시 모든 스킬을 개별적으로 업데이트해야 한다.

### 채택: Design (Phase 2)을 optional로 설정

사용자가 명시적으로 요청한 경우에만 Phase 2를 실행한다. 요청하지 않으면 Phase 1에서 Phase 3으로 건너뛴다.

**이유**:
- CLI 도구, 백엔드 API 등 UI가 불필요한 서비스가 있다.
- Figma MCP가 설정되어 있지 않은 환경에서는 실행할 수 없다.
- 모든 서비스에 디자인을 강제하면 불필요한 작업이 발생한다.

### 기각: 단일 Phase로 모든 것을 처리

기획, 설계, 구현, 문서화를 하나의 Phase에서 순차적으로 수행하는 방식이다.

**기각 이유**:
- Phase 간 게이트(사용자 승인, Critic PASS)가 없으면 품질을 보장할 수 없다.
- 중간 산출물이 명시적으로 정의되지 않아 추적이 불가능하다.
- 문제 발생 시 어느 단계에서 문제가 생겼는지 식별하기 어렵다.
