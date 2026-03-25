---
name: audit-loop
description: "auto-improve 파이프라인의 Audit Phase (#1~#10). 기존 코드베이스를 7개 관점(코드 품질, 보안, 아키텍처, DB, 테스트, Repo Health, UX/UI)에서 병렬 진단하고 CTO가 우선순위를 매겨 Audit Report를 산출한다. auto-improve 스킬이 호출하며, 독립 실행도 가능하다. '코드 진단해줘', '서비스 점검', '코드베이스 감사', 'audit loop 실행', '종합 진단' 요청에 트리거."
---

# audit-loop

기존 코드베이스를 7개 관점에서 병렬 진단 → CTO 종합 판정 → Audit Report 문서화.

auto-improve의 Phase 1을 담당한다. auto-dev에서 idea-forge가 "뭘 만들지?"를 결정하는 것처럼, audit-loop는 "뭐가 문제인지?"를 파악한다.

## 입력

- 코드베이스 경로 (필수)
- 진단 범위 (선택): 사용자가 특정 영역만 지정 가능. 미지정 시 전체 진단.

## 산출물

- `audit-report.md` (경로: `{project}/docs/llm/audit-report.md`)

---

## 단계별 워크플로우

### #1 대상 분석 + 범위 확정

**에이전트**: Explore (subagent_type=Explore)

코드베이스 구조를 파악하고 진단 범위를 확정한다.

**수행 내용**:
1. 프로젝트 루트의 파일 구조 탐색 (package.json, pyproject.toml, go.mod, Cargo.toml 등)
2. 기술 스택 식별 (언어, 프레임워크, DB, 프론트엔드)
3. 조건부 진단 판별:
   - DB 존재 여부: 마이그레이션 파일, ORM 모델, schema 파일, DB 연결 설정 확인
   - UI 존재 여부: 프론트엔드 코드, 템플릿, 컴포넌트 디렉토리 확인
4. 사용자 지정 범위가 있으면 해당 영역만, 없으면 전체

**산출물**: scope-map (내부 사용, 파일로 저장하지 않음)
```yaml
project_path: /path/to/project
tech_stack:
  languages: [Python, TypeScript]
  frameworks: [FastAPI, React]
  db: PostgreSQL  # 또는 null
  has_ui: true    # 또는 false
audit_scope:
  code_quality: true
  security: true
  architecture: true
  db: true        # DB 존재 시 true
  test: true
  repo_health: true  # 항상 true
  ux_ui: true        # UI 존재 시 true
user_focus: null  # 또는 사용자가 지정한 영역 목록
```

---

### #2~#8 병렬 진단

#1의 scope-map에 따라 해당하는 진단을 **모두 병렬**로 실행한다. 각 진단은 독립적이므로 서로의 결과를 기다리지 않는다.

scope-map에서 false인 항목은 건너뛴다 (예: DB가 없으면 #5 스킵, UI가 없으면 #8 스킵). #7 Repo Health는 항상 실행한다.

#### #2 코드 품질 진단 ⓟ

**에이전트**: code-reviewer

**프롬프트 템플릿**:
```
아래 코드베이스의 코드 품질을 종합 진단하라.
프로젝트 경로: {project_path}
기술 스택: {tech_stack}

진단 항목:
- 안티패턴 및 코드 스멜
- 코드 복잡도 (함수/클래스 단위)
- 코드 중복
- 네이밍 일관성
- 에러 처리 패턴
- 의존성 관리 상태

출력 형식:
1. 점수 (0-10): 항목별 점수 + 가중 평균 총점
2. 발견 목록: 심각도(Critical/High/Medium/Low)별 분류
3. 각 발견에 대해: 파일 경로, 라인 범위, 구체적 설명, 개선 방향
```

#### #3 보안 진단 ⓟ

**에이전트**: security-reviewer

**프롬프트 템플릿**:
```
아래 코드베이스의 보안 상태를 종합 진단하라.
프로젝트 경로: {project_path}
기술 스택: {tech_stack}

진단 항목:
- OWASP Top 10 취약점
- 의존성 취약점 (알려진 CVE)
- 인증/인가 구현 상태
- 민감 데이터 처리 (하드코딩된 시크릿, 로그 노출)
- 입력 검증 및 출력 인코딩
- CORS, CSP 등 보안 헤더

출력 형식: #2와 동일 (점수 + 심각도별 발견 목록 + 파일/라인/설명/개선방향)
```

#### #4 아키텍처 진단 ⓟ

**에이전트**: CTO

**프롬프트 템플릿**:
```
아래 코드베이스의 아키텍처 건전성을 진단하라.
프로젝트 경로: {project_path}
기술 스택: {tech_stack}

진단 항목:
- 모듈 간 결합도 및 응집도
- 계층 분리 (프레젠테이션/비즈니스/데이터)
- 확장성 병목
- 기술 부채 수준
- 설정/환경 관리
- 에러 전파 및 복구 패턴

출력 형식: #2와 동일
```

#### #5 DB 진단 ⓟ [조건부: DB 존재 시]

**에이전트**: DBA

**프롬프트 템플릿**:
```
아래 코드베이스의 데이터베이스 상태를 진단하라.
프로젝트 경로: {project_path}
DB 종류: {db_type}

진단 항목:
- 스키마 설계 품질 (정규화, 관계, 제약조건)
- 인덱스 전략
- 쿼리 성능 (N+1, 풀 테이블 스캔 패턴)
- 마이그레이션 이력 및 품질
- 연결 관리 (풀링, 타임아웃)
- 데이터 무결성 보장

출력 형식: #2와 동일
```

#### #6 테스트 진단 ⓟ

**에이전트**: qa-engineer

**프롬프트 템플릿**:
```
아래 코드베이스의 테스트 상태를 진단하라.
프로젝트 경로: {project_path}
기술 스택: {tech_stack}

진단 항목:
- 테스트 커버리지 측정 (가능한 경우 실행)
- 테스트 종류별 분포 (유닛/통합/E2E)
- 테스트 품질 (assertion 충분성, 경계값 테스트)
- 누락된 테스트 영역 식별
- 테스트 인프라 상태 (CI 설정, 테스트 러너)
- Flaky 테스트 패턴

출력 형식: #2와 동일
```

#### #7 Repo Health 진단 ⓟ

**에이전트**: Explore (subagent_type=Explore)

**프롬프트 템플릿**:
```
아래 코드베이스의 리포지토리 건강 상태를 진단하라.
프로젝트 경로: {project_path}

진단 항목:
- .gitignore 커버리지: 추적되면 안 되는 파일이 추적 중인지 (바이너리, 시크릿, 빌드 산출물)
- 대용량 파일: git에 추적 중인 바이너리/미디어 파일 (이미지, 폰트, 동영상, 오디오)
- git 히스토리 비대화: .git 디렉토리 크기, 자주 변경되는 대용량 파일, 불필요한 히스토리
- 브랜치 전략: 브랜치 구조, stale 브랜치, 커밋 위생 (메시지 품질, squash 여부)
- CI/CD 설정: GitHub Actions, 린터, 포매터 설정 유무
- 불필요한 파일: placeholder, stale artifact, 중복 파일

출력 형식: #2와 동일 (점수 + 심각도별 발견 목록 + 파일/라인/설명/개선방향)
```

---

#### #8 UX/UI + 동적 진단 ⓟ [조건부: UI 존재 시]

UI가 존재하는 프로젝트에서 코드 레벨(정적) + 실행 레벨(동적) 진단을 병렬 수행한다.

##### 8-A 정적 진단: ux-reviewer + ui-reviewer (병렬 2개)

**ux-reviewer 프롬프트**:
```
아래 코드베이스의 UX를 진단하라.
프로젝트 경로: {project_path}
프론트엔드 스택: {frontend_stack}

진단 항목: 태스크 완료 용이성, 인지 부하, 네비게이션, 접근성, 에러 복구
```

**ui-reviewer 프롬프트**:
```
아래 코드베이스의 UI를 진단하라.
프로젝트 경로: {project_path}
프론트엔드 스택: {frontend_stack}

진단 항목: 시각적 계층, 일관성, 트렌드 적합성, 반응형, 접근성
```

##### 8-B 동적 진단: simulator → ui-reviewer + user-tester

앱을 실제 실행하고 스크린샷 기반으로 진단한다. 코드만으로는 발견할 수 없는 런타임 시각 결함과 사용성 문제를 포착하는 것이 목적이다.

**단계**:

1. **simulator 에이전트**: 앱 실행 + 주요 화면 스크린샷 캡처
```
아래 앱을 실행하고 주요 화면의 스크린샷을 캡처하라.
프로젝트 경로: {project_path}
실행 명령: {run_command} (package.json scripts, README, 또는 관례로 추론)

수행:
1. 앱 실행 (dev server 등)
2. 주요 화면/페이지를 순회하며 스크린샷 캡처
3. 주요 유저 플로우 1~3개를 실행하며 각 단계 스크린샷 캡처
4. 발견한 런타임 에러, 콘솔 에러 기록

산출물: 스크린샷 파일 목록 + 에러 로그
```

2. **ui-reviewer 에이전트**: 캡처된 스크린샷 기반 시각적 결함 진단
```
아래 스크린샷들을 분석하여 시각적 결함을 진단하라.
스크린샷: {screenshot_paths}

진단 항목: 깨진 레이아웃, 정렬 이상, 텍스트 잘림/오버플로우, 빈 화면, 이미지 미로딩, 반응형 깨짐
출력 형식: #2와 동일 (점수 + 심각도별 발견 목록 + 스크린샷 경로/설명/개선방향)
```

3. **user-tester 에이전트**: 경량 사용성 점검
```
아래 스크린샷과 유저 플로우를 분석하여 사용성을 점검하라.
스크린샷: {screenshot_paths}
유저 플로우: {flow_descriptions}

진단 항목: 플로우 완료 가능 여부, 명확하지 않은 UI 요소, 누락된 피드백(로딩/에러/성공), 접근성 문제
출력 형식: #2와 동일
```

**8-B 실행 조건**: 앱 실행이 가능한 경우에만 수행. 실행 명령을 찾을 수 없거나 실행 실패 시 경고를 기록하고 8-A 결과만으로 진행한다.

**8-B 실행 순서**: simulator(1단계) 완료 후 ui-reviewer(2단계) + user-tester(3단계)를 병렬 실행.

##### 결과 통합

8-A(정적)와 8-B(동적)의 결과를 통합하여 UX/UI 진단 결과로 합산한다. 동적 진단에서만 발견된 항목은 `[동적]` 태그를 붙여 정적 진단과 구분한다.

---

### #9 CTO 종합 판정 게이트

**에이전트**: CTO

모든 병렬 진단(#2~#8) 결과를 수집한 뒤 실행한다.

**수행 내용**:
1. 각 진단 결과의 발견 항목을 통합
2. 심각도 × 영향 범위로 우선순위 매트릭스 작성
3. 개선 항목을 우선순위(P0 Critical → P1 High → P2 Medium → P3 Low)로 정렬
4. 게이트 판정

**게이트 판정 기준**:

| 조건 | 판정 | 다음 단계 |
|---|---|---|
| P0 또는 P1 발견이 1개 이상 | PROCEED | Phase 2로 진행 |
| P2만 존재 (P0/P1 없음) | PARTIAL | 사용자에게 범위 확인 |
| 모든 진단 점수 > 8.0 AND P0/P1/P2 없음 | SKIP | 종합 보고 후 종료 |

**프롬프트 템플릿**:
```
아래 진단 결과를 종합 분석하고 개선 우선순위를 판정하라.

[코드 품질 진단 결과]
{#2 결과}

[보안 진단 결과]
{#3 결과}

[아키텍처 진단 결과]
{#4 결과}

[DB 진단 결과]
{#5 결과 또는 "해당 없음"}

[테스트 진단 결과]
{#6 결과}

[Repo Health 진단 결과]
{#7 결과}

[UX/UI 진단 결과]
{#8 결과 또는 "해당 없음"}

판정 형식:
1. 베이스라인 점수표 (영역별 0-10)
2. 우선순위 매트릭스 (P0~P3)
3. 개선 항목 목록 (우선순위별, 각 항목에 예상 난이도 S/M/L 표기)
4. 게이트 판정: PROCEED / PARTIAL / SKIP
5. 판정 근거 1문장
```

**gate-decision.yaml 산출** (PROCEED/PARTIAL일 때):
```yaml
gate: audit-cto
decision: PROCEED  # 또는 PARTIAL 또는 SKIP
baseline_scores:
  code_quality: 6.5
  security: 7.0
  architecture: 5.5
  db: 8.0          # 또는 N/A
  test_coverage: 4.0
  repo_health: 5.0
  ux_ui: 6.0       # 또는 N/A
priority_items:
  p0: [{id: "SEC-001", title: "SQL injection in user search", area: "security"}]
  p1: [{id: "ARCH-001", title: "Circular dependency in core modules", area: "architecture"}]
  p2: [{id: "TEST-001", title: "No integration tests for payment flow", area: "test"}]
  p3: [{id: "CODE-001", title: "Inconsistent error handling", area: "code_quality"}]
improvement_scope:
  architecture: true
  db: false
  ux_ui: true
  estimated_effort: L
```

---

### #10 Audit Report 문서화

**doc-loop 스킬**을 자동(B) 모드 + LLM 모드로 호출한다.

**입력**: #1~#9의 모든 결과 (scope-map, 진단 결과 7종, gate-decision.yaml)

**audit-report.md 필수 섹션**:

| 섹션 | 내용 |
|---|---|
| 대상 개요 | 프로젝트 경로, 기술 스택, 진단 범위 |
| 베이스라인 점수 | 영역별 점수표 (0-10) |
| 우선순위 매트릭스 | P0~P3 항목 전체 목록 (ID, 제목, 영역, 심각도, 난이도) |
| 영역별 상세 진단 | 코드 품질, 보안, 아키텍처, DB, 테스트, Repo Health, UX/UI 각각의 발견 사항 |
| 개선 범위 | design-loop에 전달할 개선 대상 영역 및 항목 |
| 제약 조건 | 하위호환 요구사항, 마이그레이션 주의점, 기존 테스트 보존 필요성 |

---

## 루프 제한

각 에이전트 호출은 최대 10회 재시도. 10회 소진 시:

| 단계 | 10회 소진 처리 |
|---|---|
| #2~#8 진단 | 해당 영역을 "진단 불가"로 표기, 나머지 결과로 진행 |
| #9 CTO 판정 | 사용자에게 보고, 수동 판정 요청 |
| #10 문서화 | doc-loop 내부 5라운드 기준 적용 |

---

## NEVER 규칙

1. NEVER: #9 CTO 판정 없이 Phase 2로 진행하지 마라.
2. NEVER: 조건부 진단(#5 DB, #8 UX/UI)을 DB/UI가 없는 프로젝트에서 실행하지 마라.
3. NEVER: 병렬 진단(#2~#8) 결과를 기다리지 않고 #9를 실행하지 마라. 모든 병렬 진단이 완료(또는 실패 처리)된 후 #9를 실행한다.

## ALWAYS 규칙

1. ALWAYS: #2~#8은 최대한 병렬로 실행한다. 순차 실행은 기술적 제약이 있을 때만 허용한다.
2. ALWAYS: 각 진단의 점수는 0-10 스케일 + 가중 평균 총점으로 통일한다.
3. ALWAYS: audit-report.md에 베이스라인 점수를 포함한다. 이 점수는 Verify Phase의 Before/After 비교 기준점이다.

---

## 경계

- 이 스킬은 auto-improve의 Phase 1 오케스트레이터다.
- 에이전트를 직접 호출하지 않는다 — 메인 모델에게 에이전트 호출을 요청한다.
- 진단만 수행한다. 개선 설계/구현은 하지 않는다 (그것은 Phase 2~3의 역할).
- design-loop의 입력이 되는 audit-report.md를 산출하는 것이 최종 목표다.
