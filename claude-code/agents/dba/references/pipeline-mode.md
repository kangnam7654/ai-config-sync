# Pipeline Mode Reference (auto-dev #28)

## Overview

This reference applies ONLY when dba is invoked as step #28 in the auto-dev pipeline. In this mode, output MUST be the `review-verdict` YAML format — no markdown report.

## 5-Criterion Weighted Scoring

| Criterion | Weight | What to Evaluate |
|---|---|---|
| **migration_safety** | 0.30 | Rollback exists, no unguarded destructive ops, NOT NULL defaults |
| **query_performance** | 0.25 | No unnecessary sequential scans, proper indexes, no N+1 |
| **security** | 0.20 | RLS on user tables, no SQL injection, least-privilege grants |
| **index_strategy** | 0.15 | FK indexes, no over-indexing, appropriate index types |
| **schema_compliance** | 0.10 | Implementation matches reviewed design schema (#12 PASS output) |

Weighted total = sum of (score × weight) for each criterion.

## PASS Condition

```
PASS: total > 8.0 AND migration_safety >= 7
```

Both conditions must be true. A high total score does not override a low migration_safety score.

## Next Step Routing

- **PASS** → `next_step: 29` (code review)
- **FAIL** → `next_step: 27` (return to implementation for fixes)

## YAML Output Template

```yaml
step: "28"
agent: "dba"
status: "{PASS | FAIL}"
timestamp: "{ISO 8601}"
score:
  total: "{가중 평균}"
  criteria:
    - name: "migration_safety"
      weight: "0.30"
      score: "{0-10}"
      detail: "{롤백 유무, 파괴적 연산 건수, NOT NULL 이슈}"
    - name: "query_performance"
      weight: "0.25"
      score: "{0-10}"
      detail: "{순차 스캔 건수, N+1 패턴 건수, 인덱스 활용률}"
    - name: "security"
      weight: "0.20"
      score: "{0-10}"
      detail: "{RLS 적용률, SQL injection 취약점 건수, GRANT 범위}"
    - name: "index_strategy"
      weight: "0.15"
      score: "{0-10}"
      detail: "{FK 인덱스 누락 건수, 과잉 인덱스 건수}"
    - name: "schema_compliance"
      weight: "0.10"
      score: "{0-10}"
      detail: "{설계 스키마 대비 구현 일치율}"
  primary_criterion: "migration_safety"
  primary_score: "{해당 점수}"
pass_condition: "total > 8.0 AND primary_score >= 7"
verdict: "{PASS | FAIL}"
feedback:
  - "{수정 지시: [파일명] — [구체적 변경 사항]}"
next_step: "{29 (PASS) | 27 (FAIL)}"
```

## Scoring Adjustments

- No DB available for EXPLAIN: apply -1 penalty to `query_performance` (max score becomes 9)
- ORM-generated SQL unavailable: note `ORM 생성 SQL 미확인. ORM 설정 파일 기준 정적 리뷰.` in query_performance detail
- Additive-only migration (ADD COLUMN nullable) with no DOWN section: `migration_safety = 7` (acceptable minimum, note: "Additive-only 변경. 롤백 미필수이나 DOWN 섹션 권장.")
