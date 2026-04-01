# service-dev 스킬: taskflow 프로젝트 재개 처리

## 1. 재개 감지 (중단 및 재개 절차 적용)

스킬의 "중단 및 재개" 섹션에 따라 `docs/taskflow/` 디렉토리를 확인하여 어떤 Phase까지 완료되었는지 판단합니다.

### 산출물 존재 여부 확인

| 산출물 | 존재 여부 | 판단 |
|--------|-----------|------|
| `docs/taskflow/design.md` | O | Phase 1 (Plan) 완료 |
| `docs/taskflow/spec.md` | O | Phase 3 (Spec) 완료 |
| `src/` 디렉토리 | X | Phase 4 (Build) 미시작 |
| `README.md` | X | Phase 5 (Document) 미시작 |

### 판단 결과

스킬의 판단 기준에 따라:
- `design.md` 존재 -> Phase 1 완료
- `spec.md` 존재 -> Phase 3 완료
- `src/` 디렉토리 없음 -> Phase 4 미시작

**결론: Phase 3까지 완료. Phase 4 (Build)부터 재개해야 합니다.**

## 2. 컨텍스트 복원

스킬 지시에 따라 완료된 Phase의 산출물을 읽어 컨텍스트를 복원합니다.

### 읽은 산출물

- **design.md** (Phase 1 산출물): `# mock design doc for test`
- **spec.md** (Phase 3 산출물): `# mock spec doc for test`

### 복원된 컨텍스트 평가

두 문서 모두 mock 데이터(1줄짜리 제목만 존재)입니다. 실제 서비스 개발이라면 이 시점에서 다음을 사용자에게 보고합니다:

> **문제 발견**: `design.md`와 `spec.md`의 내용이 불충분합니다. Phase 4 (Build)를 진행하려면 spec.md에 모듈별 요구사항, API 스키마, 데이터 모델, 에러 처리 규칙이 정의되어 있어야 합니다. 현재 spec.md에는 제목만 존재합니다.
>
> 선택지:
> 1. Phase 3 (Spec)으로 돌아가 spec.md를 완성한 후 Build로 진행
> 2. Phase 1 (Plan)으로 돌아가 design.md부터 재작성

## 3. Phase 4 진행 시 수행할 작업 (spec이 완전했다면)

spec.md가 완전한 상태였다면, 아래 절차를 따릅니다:

### 3-1. 사용자 확인

> Phase 3 (Spec)까지 완료된 것을 확인했습니다. Phase 4 (Build)를 시작하겠습니다. 진행하시겠습니까?

### 3-2. 모듈별 사이클 실행

design.md의 구현 순서에 따라 각 모듈에 대해:

```
Step 1: dev      — spec.md를 참조하여 코드 작성 → git commit
Step 2: review   — 코드 리뷰 (5개 체크리스트) → 피드백 반영 → git commit
Step 3: refactor — 가독성 개선 → git commit
Step 4: test     — Unit 테스트 작성 및 통과 확인 → git commit
```

### 3-3. 모든 모듈 완료 후

1. 통합 테스트 실행
2. E2E 테스트 실행
3. Coverage 80% 이상 확인

### 3-4. Phase 4 게이트

세 가지 검증 모두 통과 시 Phase 5 (Document)로 진행.

## 4. 스킬이 적용한 규칙 요약

| 규칙 | 적용 내용 |
|------|-----------|
| 재개 판단 기준 | `docs/{service-name}/` 내 산출물 존재 여부로 Phase 판단 |
| 컨텍스트 복원 | 완료된 Phase의 산출물을 읽어 컨텍스트 확보 |
| Phase 건너뛰기 금지 | Phase 2 (Design)만 optional, 나머지는 순차 필수 |
| spec 기반 개발 | Phase 4에서 spec.md에 정의되지 않은 기능 구현 금지 |
| 불충분한 산출물 감지 | 산출물 내용이 부실하면 이전 Phase로 돌아갈 것을 제안 |
| 사용자 승인 필수 | Phase 전환 전 반드시 사용자 확인 |

## 5. 최종 판단

이 시나리오에서는 design.md와 spec.md가 mock 데이터이므로, 실제 실행이라면 **Phase 3 (Spec)으로 돌아가 문서를 완성하는 것을 권장**합니다. spec.md에 모듈별 요구사항이 없는 상태에서 Phase 4를 시작하면 NEVER 규칙 #3("spec.md에 정의되지 않은 기능을 구현하지 마라")에 위반됩니다.
