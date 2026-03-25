# auto-improve-loop Resume Workflow Plan

## 현재 상태 요약

| 항목 | 값 |
|------|-----|
| progress 파일 | `/tmp/mock-webapp/docs/llm/improve-progress.yaml` |
| current_round | 2 (아직 시작 안 됨) |
| overall_status | in_progress |
| 완료된 라운드 | Round 1 (completed) |
| target_score | 8.0 |
| max_rounds | 5 |
| focus_areas | null (전체) |
| remaining_p0_p1 | 2 |

## Step 1: 상태 로드 및 사전 체크

1. `improve-progress.yaml`을 읽는다 -- 이미 완료.
2. 종료 조건 사전 체크를 수행한다:
   - 모든 영역 점수 >= 8.0? **아니오** (최고 점수 db=7.5도 미달)
   - current_round(2) >= max_rounds(5)? **아니오**
   - 2라운드 연속 정체? **판단 불가** (라운드 1개뿐)
   - 회귀 감지? **판단 불가** (라운드 1개뿐)
   - **결론: 종료 조건 미충족. Round 2 진행.**

3. rounds 배열에 round 2 항목이 없는 것을 확인한다 -- 중단된 라운드가 아니라 아직 시작하지 않은 라운드이므로 처음부터 실행한다.

## Step 2: Round 2 실행 -- auto-improve 호출

auto-improve를 호출하되, `auto-improve-context.md`에 작성된 이전 라운드 컨텍스트를 함께 전달한다.

### 우선순위 전략

**Round 2의 핵심 목표**: items_remaining의 P1 2건을 해결하고, target 대비 gap이 큰 영역을 집중 개선한다.

| 순위 | 항목 | 근거 |
|------|------|------|
| 1 | TEST-001: No integration tests for payment flow | test_coverage가 5.0으로 target 대비 gap 3.0 (최대). P1이므로 즉시 착수. learnings에 따라 mock DB 사전 구성 |
| 2 | ARCH-001: Circular dependency in core modules | architecture 6.5 (gap 1.5). P1. 순환 의존성 해결은 다른 영역(code_quality, repo_health)에도 파급 효과 |
| 3 | 새로 발견되는 security/repo_health 항목 | 둘 다 6.0 (gap 2.0). Audit에서 새 항목이 나올 가능성 높음 |

### learnings 활용 계획

- **payment 모듈 mock DB**: TEST-001 작업 시 Design Phase에서 mock DB 설정 방법을 먼저 명세하고, Build Phase에서 mock DB fixture를 먼저 생성한 뒤 integration test를 작성한다.
- **user search API 시그니처 변경**: Audit Phase에서 user search API를 호출하는 모든 코드를 탐색하여 새 시그니처와 정합성이 맞는지 확인한다. 불일치가 있으면 새 항목으로 등록한다.

### 회귀 테스트 포함 항목

- SEC-001 (SQL injection fix) -- user search 관련 쿼리가 여전히 parameterized인지 확인
- user search API 시그니처 변경 -- 호출부가 새 시그니처를 사용하는지 확인

## Step 3: Round 2 종료 -- 상태 업데이트

auto-improve 완료 후, completion.yaml에서 결과를 추출하여 `improve-progress.yaml`을 업데이트한다.

### 업데이트 항목

1. **rounds 배열에 round 2 추가**:
   ```yaml
   - round: 2
     timestamp: "2026-03-25T{현재시각}"
     status: completed  # 또는 failed
     baseline_scores:  # Round 1의 final_scores를 그대로 사용
       code_quality: 6.5
       security: 6.0
       architecture: 6.5
       db: 7.5
       test_coverage: 5.0
       repo_health: 6.0
       ux_ui: 6.5
     final_scores:  # Round 2 Verify Phase 결과
       code_quality: {새 점수}
       security: {새 점수}
       ...
     items_addressed:  # Round 2에서 해결한 항목
       - id: TEST-001 (예상)
       - id: ARCH-001 (예상)
       - {새로 발견+해결한 항목}
     items_remaining:  # 미해결 항목
       - {Round 2에서 미해결된 기존 항목}
       - {새로 발견되었으나 미해결된 항목}
     learnings: |
       - {Round 2에서 얻은 교훈}
   ```

2. **current_round**: 2 -> 3

3. **latest_scores**: Round 2 final_scores로 갱신

4. **remaining_p0_p1**: 재계산 (Round 2 items_remaining 중 P0/P1 개수)

5. **all_scores_above_target**: 모든 영역이 8.0 이상인지 재평가

6. **git commit**: `improve-progress.yaml` 변경사항을 커밋

## Step 4: 종료 조건 평가

Round 2 완료 후 아래 4가지 조건을 순서대로 평가한다:

| 조건 | 평가 방법 | 충족 시 동작 |
|------|----------|-------------|
| 모든 영역 >= 8.0 | latest_scores의 모든 값 확인 | 목표 달성, 루프 종료 -> 최종 보고 |
| current_round(3) >= max_rounds(5) | 숫자 비교 | 이 시점에서는 미충족 |
| 2라운드 연속 정체 | Round 1 final vs Round 2 final 비교, 모든 영역 변화가 +-0.5 이내인지 | 정체 감지, 루프 종료 -> 최종 보고 |
| 전체 평균 하락 | Round 1 평균 vs Round 2 평균 비교 | 회귀 감지, 경고 후 종료 -> 최종 보고 |

### 분기

- **종료 조건 충족**: `improvement-final-report.md`를 doc-loop 스킬로 생성. overall_status를 completed 또는 stopped으로 갱신.
- **종료 조건 미충족**: Round 3으로 진행. 동일한 프로세스를 반복.

### Circuit Breaker 체크

- ARCH-001이 Round 1에서 remaining, Round 2에서도 remaining이면: 2회 연속. 아직 3회가 아니므로 "해결 불가" 판정은 하지 않지만, Round 3에서도 남으면 해결 불가로 표기.
- TEST-001도 동일하게 추적.

## 예상 시나리오별 다음 행동

### 시나리오 A: Round 2에서 큰 개선 (평균 7.0+)
- 종료 조건 미충족이지만 진전이 있으므로 Round 3 진행
- Round 3에서 남은 gap이 작은 영역(db 등)을 target 이상으로 끌어올리는 데 집중

### 시나리오 B: Round 2에서 정체 (모든 영역 +-0.5)
- 정체 감지로 루프 종료
- 최종 보고에서 "2라운드 시도했으나 구조적 한계로 추가 개선 어려움" 보고

### 시나리오 C: Round 2에서 회귀 (평균 하락)
- 회귀 감지 경고 출력 후 루프 종료
- 최종 보고에서 하락 원인 분석 포함

### 시나리오 D: Round 2에서 목표 달성 (모든 영역 >= 8.0)
- 성공 종료
- 최종 보고 생성, overall_status를 completed로 갱신
