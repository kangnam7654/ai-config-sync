# auto-improve-loop Workflow Plan (Dry Run)

## 입력 분석

| 항목 | 값 |
|------|-----|
| 코드베이스 경로 | `/tmp/mock-webapp` |
| 목표 점수 | 8.0 (사용자가 "8점 이상"이라고 명시) |
| 최대 라운드 | 3 (사용자가 "최대 3라운드"라고 명시) |
| 집중 영역 | null (전체 — 사용자가 특정 영역을 지정하지 않음) |

---

## Step-by-Step 실행 계획

### Phase 0: 초기화

1. `improve-progress.yaml` 존재 여부 확인
   - 경로: `/tmp/mock-webapp/docs/llm/improve-progress.yaml`
   - **미존재** (첫 실행이므로) -> 초기 파일 생성
   - target_score: 8.0, max_rounds: 3, focus_areas: null, current_round: 0, overall_status: in_progress
   - rounds: 빈 배열

2. 종료 조건 사전 체크
   - current_round(0) < max_rounds(3) -> 계속 진행
   - latest_scores 비어 있음 -> 목표 달성 아님 -> 계속 진행

---

### Phase 1: 라운드 1 실행

#### 1-1. auto-improve 호출 (초회 — 추가 컨텍스트 없음)

auto-improve 스킬에 전달할 파라미터:

```
auto-improve를 실행하라.
코드베이스 경로: /tmp/mock-webapp
집중 영역: 전체
```

auto-improve는 내부적으로 37단계(Audit -> Design -> Build -> Verify)를 수행한다.
이 라운드에서는 이전 컨텍스트가 없으므로 표준 auto-improve를 그대로 실행.

#### 1-2. 라운드 1 종료 처리

auto-improve의 `completion.yaml` 결과를 읽어서:

1. `rounds` 배열에 라운드 1 결과 추가:
   - round: 1
   - timestamp: 현재 시간
   - status: completed (또는 failed)
   - baseline_scores: Audit Phase에서 측정한 초기 점수 (7개 영역)
   - final_scores: Verify Phase에서 측정한 최종 점수
   - items_addressed: 이번 라운드에서 해결한 항목 목록
   - items_remaining: 아직 남은 항목 목록
   - learnings: 이번 라운드에서 얻은 교훈

2. 메타데이터 갱신:
   - current_round: 1
   - latest_scores: 라운드 1의 final_scores로 갱신
   - remaining_p0_p1: P0/P1 항목 중 남은 수
   - all_scores_above_target: 모든 영역이 8.0 이상인지 판정

3. `git add docs/llm/improve-progress.yaml && git commit -m "auto-improve-loop: round 1 완료"`

#### 1-3. 종료 조건 평가

| 조건 | 판정 방법 |
|------|-----------|
| 모든 영역 >= 8.0 | latest_scores의 7개 영역 모두 확인 |
| 라운드 소진 (current_round >= 3) | 1 < 3 -> 아직 아님 |
| 정체 감지 | 라운드 1개뿐이므로 비교 불가 -> 해당 없음 |
| 회귀 감지 | 이전 라운드 없으므로 비교 불가 -> 해당 없음 |

- **모든 영역 >= 8.0이면**: 루프 종료 -> 최종 보고 생성 -> 끝
- **아니면**: 라운드 2로 진행

---

### Phase 2: 라운드 2 실행 (라운드 1에서 종료되지 않은 경우)

#### 2-1. auto-improve 호출 (반복 — 이전 컨텍스트 전달)

auto-improve 스킬에 전달할 파라미터:

```
auto-improve를 실행하라.
코드베이스 경로: /tmp/mock-webapp
집중 영역: 전체

[이전 라운드 컨텍스트]
improve-progress.yaml 경로: /tmp/mock-webapp/docs/llm/improve-progress.yaml

이 파일을 읽고 아래 규칙을 적용하라:
1. Audit Phase: 이전 라운드에서 이미 해결된 항목(items_addressed)은 재진단하지 마라.
   대신 해당 영역의 회귀 여부만 확인하라.
2. Audit Phase: 이전 라운드의 items_remaining을 우선 진단 대상으로 삼아라.
   새로 발견된 항목도 포함하되, 기존 remaining 항목이 우선순위가 높다.
3. Design Phase: 이전 라운드의 learnings를 참고하여 동일한 시행착오를 반복하지 마라.
4. Build Phase: 이전 라운드에서 수정한 코드에 대한 회귀 테스트를 포함하라.
5. Verify Phase: 이전 라운드 final_scores와 현재 라운드 final_scores를 비교하여
   점수가 하락한 영역이 있으면 반드시 보고하라.
```

#### 2-2. 라운드 2 종료 처리

라운드 1과 동일한 절차:
- rounds 배열에 라운드 2 추가
- current_round: 2로 갱신
- latest_scores 갱신
- git commit

#### 2-3. 종료 조건 평가

| 조건 | 판정 방법 |
|------|-----------|
| 모든 영역 >= 8.0 | latest_scores 전수 확인 |
| 라운드 소진 | 2 < 3 -> 아직 아님 |
| 정체 감지 | 라운드 1 vs 라운드 2 점수 비교. 모든 영역에서 변화가 +-0.5 이내이면 정체 |
| 회귀 감지 | 라운드 2 전체 평균 < 라운드 1 전체 평균이면 회귀 |

**Circuit Breaker 추가 체크**:
- 라운드 1의 items_remaining 중 라운드 2에서도 여전히 remaining인 항목 추적 (3라운드 연속 시 "해결 불가" 표기)

- **목표 달성 or 정체 감지 or 회귀 감지**: 루프 종료 -> 최종 보고
- **아니면**: 라운드 3으로 진행

---

### Phase 3: 라운드 3 실행 (라운드 2에서 종료되지 않은 경우)

#### 3-1. auto-improve 호출 (라운드 2와 동일 형태, 누적 컨텍스트 포함)

동일한 형태로 auto-improve를 호출하되, improve-progress.yaml에는 라운드 1, 2의 결과가 모두 누적되어 있으므로 auto-improve가 읽을 때 더 풍부한 컨텍스트를 갖게 된다.

#### 3-2. 라운드 3 종료 처리

- rounds 배열에 라운드 3 추가
- current_round: 3으로 갱신
- git commit

#### 3-3. 종료 조건 평가

| 조건 | 판정 방법 |
|------|-----------|
| 모든 영역 >= 8.0 | 목표 달성 -> 성공 종료 |
| 라운드 소진 | 3 >= 3 -> **라운드 소진** -> 부분 성공 종료 |
| 정체 감지 | 라운드 2 vs 3 비교 (2라운드 연속 변화 없음 여부) |
| 회귀 감지 | 평균 점수 하락 여부 |

**Circuit Breaker 추가 체크**:
- 3라운드 연속 items_remaining에 존재하는 항목이 있으면 "해결 불가"로 표기
- 3라운드 연속 전체 평균 하락이면 강제 종료 (이 경우 max_rounds=3이므로 어차피 종료)

**라운드 3 종료 시점에서 current_round(3) >= max_rounds(3)이므로 반드시 루프 종료**.

---

### Phase 4: 최종 보고 생성

종료 조건에 해당하면 (어느 라운드에서든) `improvement-final-report.md`를 생성한다.

- doc-loop 스킬을 자동(B) 모드 + LLM 모드로 호출
- 저장 경로: `/tmp/mock-webapp/docs/llm/improvement-final-report.md`

필수 섹션:
1. **요약**: 총 라운드 수, 종료 사유 (목표 달성 / 라운드 소진 / 정체 감지 / 회귀 감지), 최종 상태 1문장
2. **점수 추이**: 라운드별 7개 영역 점수 테이블
3. **개선 항목 전체 목록**: 라운드별로 해결한 항목 (ID, 제목, 영역, 해결 라운드)
4. **미해결 항목**: 남아있는 항목 + 미해결 사유
5. **회귀 이력**: 점수 하락 후 복구된 영역 (있는 경우)
6. **라운드별 교훈**: 각 라운드의 learnings 통합
7. **권장 다음 단계**: 추가 개선이 필요한 경우 권장 조치

최종 보고 생성 후 git commit.

---

## 상태 추적 메커니즘

| 요소 | 저장 위치 | 역할 |
|------|-----------|------|
| improve-progress.yaml | `/tmp/mock-webapp/docs/llm/improve-progress.yaml` | 라운드 간 유일한 통신 채널. 점수, 해결/미해결 항목, 교훈 누적 |
| completion.yaml | auto-improve가 생성 | 각 라운드의 auto-improve 결과. 이 파일에서 데이터를 추출하여 progress에 반영 |
| improvement-final-report.md | `/tmp/mock-webapp/docs/llm/improvement-final-report.md` | 루프 종료 시 최종 보고 |
| git commits | 매 라운드 종료 시 | 진행 상태 영속화. 중단 시 재개 가능 |

## 중단 시 재개 방법

세션이 중간에 끊어질 경우:
1. 새 세션에서 `auto-improve-loop` 재호출
2. `improve-progress.yaml`을 읽어서 `current_round` 확인
3. 마지막 `completed` 상태의 라운드 다음부터 재개
4. 중단된 라운드(status 없음)는 처음부터 재실행

## 종료 조건 요약 (우선순위 순)

| 순서 | 조건 | 결과 |
|------|------|------|
| 1 | 모든 영역 >= 8.0 | 목표 달성 (성공) |
| 2 | current_round >= 3 | 라운드 소진 (부분 성공) |
| 3 | 2라운드 연속 전 영역 변화 +-0.5 이내 | 정체 감지 (조기 종료) |
| 4 | 직전 라운드 대비 전체 평균 하락 | 회귀 감지 (경고 + 종료) |
