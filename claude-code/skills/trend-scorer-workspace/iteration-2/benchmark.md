# Skill Benchmark: trend-scorer

**Model**: claude-opus-4-6
**Date**: 2026-03-20
**Evals**: 3 (1 run each per configuration)

## Summary

| Metric | with_skill | without_skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% ± 0% | 34% ± 16% | **+66%** |
| Time | 729.6s ± 700.8s | 197.4s ± 12.3s | +532.2s |
| Tokens | 89,077 ± 44,845 | 35,608 ± 1,683 | +53,469 |

## Per-Eval Breakdown

| Eval | with_skill Pass Rate | without_skill Pass Rate | Delta |
|------|---------------------|------------------------|-------|
| topic-comparison | 100% (8/8) | 12.5% (1/8) | +87.5% |
| auto-discovery | 100% (8/8) | 50% (4/8) | +50% |
| steady-weight | 100% (5/5) | 40% (2/5) | +60% |

## Analyst Notes

1. **with_skill은 3개 eval 모두 100%** — 스킬이 출력 형식을 완벽하게 통제
2. **without_skill은 콘텐츠 역량은 있으나 형식 부재** — 주제 발굴/출처 표기는 가능하지만 6개 지표 체계를 자체 생성 불가
3. **eval-2 시간 폭증** — auto-discovery(10개 주제)에서 1722초 소요. 주제 수 × 6개 지표 = 대량 WebSearch가 원인
4. **비차별적 assertions 2개** — "두 주제 모두 평가", "출처 표기"는 baseline도 통과
5. **스킬 핵심 가치** — 정량적 점수 체계(SVGR/SBI/NFI/STB/VOL/SEA → TS/SS → Final Score)
