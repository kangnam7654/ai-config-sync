# Idea Forge Pipeline Summary

## 실행 정보
- **실행일:** 2026-03-20
- **입력:** topic 없음, goal 없음 -> Phase 0부터 실행
- **파라미터:** max_rounds=2, target_market=한국 시장

## 파이프라인 흐름

```
Phase 0: 주제 탐색
  Step 0-1: Researcher (trend-scorer 연계) -> 7개 키워드 수집 + 트렌드 점수 평가
  Step 0-2: CEO -> "소상공인 AI 자동화" 선정
  -> Phase 1 진행

Phase 1: 아이디어 검증 루프 (2 rounds)
  Round 1: CEO "소상공인 AI 올인원 SaaS 가게메이트"
    -> Researcher: 시장/경쟁사/기술 조사
    -> CSO: REBUTTAL (2/5 긍정) - POS 파편화, 캐시노트 선점
    -> Writer: round-1.md 작성

  Round 2: CEO "요식업 AI 마케팅 자동화 SaaS 리뷰메이트" (피벗)
    -> Researcher: 경쟁사 상세 조사 (세일즈랩, 리본오토, 딜리봇 등)
    -> CSO: REBUTTAL 경계선 (4/5 긍정) - 경쟁 우위만 부정
    -> Writer: round-2.md 작성

  -> max_rounds 도달. 현재 최선안으로 Phase 2 진행.

Phase 2: BM 설계 + 문서화
  Step 5: bm-designer (파이프라인 모드)
    -> Phase 2 축약 (기존 리서치 데이터 활용, 갭 분석만 수행)
    -> Phase 3: 수익 모델 = 프리미엄 + 구독 하이브리드
    -> Phase 4: 유닛 이코노믹스 = LTV/CAC 1.1:1 (미달)
    -> Phase 5: CSO 전략 검증 = 관리 가능한 리스크 3개
    -> Phase 6: BM Score = 5.45/10 (C등급)
    -> Phase 7: BM 문서 = bm-plan.md

  Step 6: 최종 문서 생성 (병렬)
    -> AI용: bm-ai.md
    -> Human용: bm-human.md
```

## 산출물 목록

| 파일 | 설명 | 크기 |
|------|------|------|
| round-1.md | 라운드 1 브리핑 (CSO Rebuttal) | 2.7KB |
| round-2.md | 라운드 2 브리핑 (CSO 경계선 Rebuttal) | 2.8KB |
| bm-plan.md | BM 설계 전체 문서 (bm-designer 산출) | 12.5KB |
| bm-ai.md | 최종 문서 AI용 | 4.5KB |
| bm-human.md | 최종 문서 Human용 | 6.5KB |
| pipeline-summary.md | 이 파일 (파이프라인 요약) | - |

## 핵심 결과

- **선정 아이디어:** ReviewMate (리뷰메이트) - 요식업 AI 마케팅 자동화 SaaS
- **BM Score:** 5.45/10 (C등급)
- **약점 영역:** UE(유닛 이코노믹스 4/10), DEF(전략적 방어력 4/10)
- **권장 다음 단계:** MVP 개발 후 실사용 데이터로 전환율/Churn 검증

## 웹 검색 횟수
- Phase 0: 10회 (트렌드 키워드 발굴 + 평가)
- Phase 1 Round 1: 6회 (시장/경쟁사/기술 조사)
- Phase 1 Round 2: 5회 (경쟁사 상세 + 피벗 검증)
- Phase 2: 4회 (BM 벤치마크 수집)
- 총: 25회
