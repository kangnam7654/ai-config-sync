# Idea Forge — TODO

## 상태: 설계 완료, 구현 대기

---

## 선행 작업 (스킬 수정)

### ~~1. trend-tracker 확장~~ → 불필요 (삭제)
> trend-scorer가 이미 Trending(SVGR, SBI, NFI) + Steady(STB, VOL, SEA) 6개 지표를 모두 커버.
> Idea Forge Phase 0에서 trend-scorer를 직접 호출하면 됨.

### 1. bm-designer 수정
- [x] Idea Forge에서 호출 시 Phase 1(인터뷰) 완전 생략 가능하도록 수정
- [x] 외부 컨텍스트 주입 인터페이스 추가 (Phase 0~1 축적 데이터 → Phase 1 대체)
- [x] Phase 2(시장 조사)도 기존 Researcher 데이터 활용하여 축약 가능하게
- [x] BM Score 산출 Phase 추가 (6개 지표 정량 평가, 가중 평균, A~D 등급)
- [x] skill-creator → doc-critic (LLM 모드) 심사 통과 (8.10/10, 라운드 8)

---

## 메인 작업: Idea Forge 스킬 생성

### 워크플로우 전체 구조

```
[입력 분기]
  ├─ topic/goal 있음 → Phase 1 직행
  └─ topic/goal 없음 → Phase 0 (주제 탐색)

Phase 0: 주제 탐색 (topic/goal 미제공 시만)
  Step 0-1: Researcher — trend-scorer 연계, 키워드 5~7개 수집
    - 선정 기준: 인기(3개월 상승/유지) + Steady(1년+ 꾸준) + 사업화 가능
    - 키워드별: 검색량 추이, 시장 성숙도, 경쟁 강도
  Step 0-2: CEO — 키워드 1개 선정 + 근거 + topic/goal/focus_keywords 자동 세팅
  → Phase 1로 진입

Phase 1: 아이디어 검증 루프 (라운드 N = 1 ~ max_rounds)
  Step 1: CEO — 제안 생성
    - 라운드 1: topic + goal + focus_keywords로 초기 제안
    - 라운드 2+: 누적 브리핑 문서 참고하여 개선된 제안
    - 출력: 문제 정의, 솔루션 가설, 타겟 고객, 차별화 포인트, 핵심 가정
  Step 2: Researcher — 팩트 조사
    - CEO 제안의 핵심 가정 + focus_keywords 기반
    - 시장 규모, 경쟁사, 기술 실현 가능성, 유사 사례
    - 출력: 구조화된 리서치 리포트 (출처 포함)
  Step 3: CSO — 전략적 검증
    - CEO 제안 + Researcher 리포트 함께 평가
    - 평가 기준: 시장 타당성, 실행 가능성, 리스크, 경쟁 우위, 재무적 잠재력
    - Accept → Phase 2로
    - Rebuttal → 구체적 약점 + 개선 방향 → Step 4로
  Step 4: (Rebuttal 시만) Writer — 라운드 브리핑 문서
    - prompt-writer로 AI용 누적 브리핑 작성
    - 필수 섹션: 시도한 제안 요약, CSO 거절 사유, Researcher 핵심 발견, 다음 라운드 제안 방향
    - doc-critic (LLM 모드) 심사 — REJECT 시 재작성 (최대 5회)
    - PASS → 라운드 N+1 Step 1로 복귀

  Early Exit:
    - CSO Accept → 즉시 Phase 2 진입
    - max_rounds 도달 + Rebuttal → 사용자에게 3옵션:
      1. 추가 라운드 (수 지정)
      2. 현재 최선안으로 BM 강행
      3. 중단

Phase 2: BM 설계 + 문서화
  Step 5: BM Designer — bm-designer 스킬 호출
    - CSO Accept 최종 제안 + 전체 리서치 데이터 기반
    - 축적 컨텍스트를 Phase 1(인터뷰) 대신 주입
    - 출력: 수익 모델, 가격 전략, 유닛 이코노믹스
  Step 6: Writer — 최종 문서 2종 (병렬)
    - AI용: prompt-writer → doc-critic LLM 모드
    - Human용: doc-writer → doc-critic HUMAN 모드
    - 각 문서 REJECT 시 재작성 (최대 5회)
    - 두 문서 모두 PASS → 사용자에게 전달
```

### 입력 파라미터

| 파라미터 | 필수 | 기본값 | 설명 |
|---------|------|--------|------|
| topic | X | Phase 0에서 자동 선정 | 브레인스토밍 주제 |
| goal | X | Phase 0에서 CEO가 설정 | 달성 목표 |
| focus_keywords | X | 자동 추출 | Researcher 조사 범위 키워드 |
| max_rounds | X | 10 | 최대 반복 라운드 수 |
| target_market | X | - | 타겟 시장/고객 |

### 산출물

| 산출물 | 형식 | 저장 경로 |
|--------|------|----------|
| 라운드별 브리핑 (AI용) | .md | docs/{topic}/rounds/round-N.md |
| 최종 BM 문서 (AI용) | .md | docs/{topic}/bm-ai.md |
| 최종 BM 문서 (Human용) | .md | docs/{topic}/bm-human.md |

### 진행 상황 보고 형식

```
[라운드 N/max] CEO 제안 → Researcher 조사 완료 → CSO: ACCEPT/REBUTTAL
  사유: (1줄 요약)
  다음: Phase 2 진입 / 라운드 N+1 진행
```

### Critic 루프 (공통 규칙)

- Writer/Planner 출력이 비어 있거나 3문장 이하 → Critic 호출하지 않고 즉시 REJECT, 재작성 요청
- Critic REJECT → 피드백을 Writer에게 전달하여 수정 → 재심사
- 최대 반복: 5회. 5회 연속 REJECT 시 사용자에게 보고
- 매 라운드 보고: `[라운드 N] 점수: X.XX | 결과: PASS/REJECT | 피드백: (1줄 요약)`
- 오케스트레이션은 메인 모델만 수행 (서브에이전트 내부 critic 호출 무시)

---

## 구현 순서

1. ~~bm-designer 수정~~ ✅ (doc-critic 8.10/10 PASS, 라운드 8)
2. ~~idea-forge 스킬 생성~~ ✅ (doc-critic 8.55/10 PASS, 라운드 4)
3. ~~통합 테스트~~ ✅ eval 3건 × (with-skill + baseline) = 6건 실행. Assertion 22/22 PASS. 피드백 없음(만족).
