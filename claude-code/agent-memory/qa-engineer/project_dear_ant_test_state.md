---
name: dear-ant 프로젝트 테스트 현황 (2026-03-25)
description: Next.js 16 + React 19 투자 심리 분석 앱 - 테스트 인프라 전무, 커버리지 0%
type: project
---

# dear-ant 프로젝트 테스트 현황

**감사일**: 2026-03-25
**프로젝트 경로**: /Users/kangnam/projects/dear-ant
**프레임워크**: Next.js 16.1.6 + React 19 + TypeScript + Supabase

## 테스트 인프라 현황

- 테스트 프레임워크: Vitest v4.1.1 (설정 완료)
  - vitest.config.ts: jsdom 환경, globals: true, setupFiles: vitest.setup.ts
  - vitest.setup.ts: @testing-library/jest-dom/vitest import
  - test 스크립트: `npm test` → `vitest run`, `npm run test:watch` → `vitest`
- 테스트 파일: 1개 (src/lib/__tests__/local-store.test.ts)
- 통과 테스트: 18/18
- 커버리지: local-store.ts 전체 경로 커버 (별도 --coverage 실행 필요)

## 핵심 비즈니스 로직 파일

- src/lib/report-engine.ts — 투자 성향 분석 엔진 (순수 함수 집합, 테스트하기 매우 쉬움)
  - calculateTotalScore, getDecisionMode, getRiskTendency, getInvestMood (경계값 로직)
  - calculateBiorhythm (날짜 의존, 고정 날짜 모킹 필요)
  - calculateMoodScore (variance 계산)
  - generateReport (공개 진입점)
- src/lib/local-store.ts — 인메모리 Map 기반 CRUD (globalThis 패턴)
  - createReport, getReport, listReports (20개 제한)
  - createMemo, getMemo, updateMemo, deleteMemo, listMemos (50개 제한)
- src/lib/questions.ts — 정적 데이터 (7개 질문, score 값 검증 필요)
- src/app/calculator/page.tsx — calcSavings, calcStock (금융 계산, 이자소득세 15.4%, 금투세 22%)
- src/app/compound/page.tsx — calculateCompound, calculateSimple (복리/단리 계산)

## API 엔드포인트

- POST /api/reports — SurveyData → Report 생성 (Supabase/localStore 분기)
- GET /api/reports/[id] — 리포트 단건 조회
- GET /api/history — 리포트 목록 (최근 20개)
- GET /api/memos — 메모 목록
- POST /api/memos — 메모 생성 (stock_name, memo 필수 검증)
- GET/PATCH/DELETE /api/memos/[id] — 메모 단건 조작

## 추천 테스트 스택

- 단위/통합: Vitest (Next.js 16과 호환, jest 대신 권장)
- 컴포넌트: @testing-library/react
- E2E: Playwright

## 우선순위 갭

- P0: report-engine.ts 단위 테스트 (핵심 비즈니스 로직, 경계값 다수)
- P0: local-store.ts 단위 테스트 (데이터 영속성 계층)
- P0: API 라우트 통합 테스트 (400/404/500 응답 검증)
- P1: calcSavings/calcStock/calculateCompound 단위 테스트 (금융 계산 정확도)
- P1: POST /api/memos 유효성 검사 테스트
- P2: 컴포넌트 테스트 (CountUp, BottomNav)
- P2: E2E — 설문 → 리포트 생성 → 결과 확인 전체 플로우
