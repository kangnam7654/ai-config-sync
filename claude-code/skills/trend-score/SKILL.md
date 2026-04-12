---
name: trend-score
description: "Quantitative trend scoring — evaluates internet topics using 6 metrics (SVGR, SBI, NFI, STB, VOL, SEA) to produce ranked score tables. For numerical scores and rankings, not qualitative research. Works with /loop for periodic monitoring."
---

# Trend Score

이 스킬은 **researcher 에이전트**를 호출하는 래퍼다. 트렌드 스코어링의 핵심 로직(6개 지표, 점수 산출, 출력 포맷)은 researcher 에이전트가 담당한다 (Trend Scoring 모드).

## 워크플로우

### Step 1: 사용자 입력 파싱

사용자 요청에서 아래를 추출한다:
- **주제**: 사용자가 지정한 주제 목록 (없으면 "자동 발굴")
- **시장**: 한국(기본값) / 글로벌 / 특정 국가
- **카테고리**: 범용(기본값) / 지정된 카테고리
- **가중치 선호**: "인기" 키워드 → α=0.70, "스테디" 키워드 → β=0.70, 없으면 기본값

### Step 2: researcher 에이전트 호출

Agent 도구로 `researcher` 에이전트를 호출한다. 프롬프트에 Step 1에서 파싱한 파라미터를 전달한다 (researcher가 Trend Scoring 모드로 자동 분류):

```
아래 파라미터로 트렌드 스코어링을 수행하라:
- 주제: {주제 목록 또는 "자동 발굴"}
- 시장: {한국/글로벌}
- 카테고리: {범용/지정}
- 가중치: α={값}, β={값}
```

### Step 3: 결과 전달

researcher 에이전트의 출력(Trend Score Report)을 사용자에게 전달한다.

## /loop 연계

이 스킬은 `/loop`과 함께 사용하면 주기적 트렌드 모니터링이 된다.

사용 예: `/loop 6h /trend-score 기술 트렌드 한국 시장`

주기적 실행 시:
1. researcher 에이전트에 이전 리포트 경로를 함께 전달한다
2. 에이전트가 랭킹 변동(+N, -N, NEW, OUT)을 자동 계산한다
3. 결과를 `trend-report-{YYYY-MM-DD}.md` 파일로 저장한다

## 경계

- 이 스킬은 **오케스트레이션만** 수행한다. 스코어링 로직, 채점 기준, 출력 포맷은 researcher 에이전트의 `researcher/references/trend-scoring.md`에 있다.
- researcher 에이전트를 직접 호출하지 않고 이 스킬을 통해 호출해야 /loop 연계와 파일 출력이 동작한다.
