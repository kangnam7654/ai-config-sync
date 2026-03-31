---
name: fit-check 프로젝트 테스트 현황
description: Next.js 16 + Prisma + Anthropic AI 크레딧 과금 서비스, TDD로 테스트 스위트 구축 완료 (2026-03-31)
type: project
---

## 프로젝트 개요

- **경로**: `/Users/kangnam/projects/dear-jeongbin/fit-check/`
- **스택**: Next.js 16, React 19, Prisma (PostgreSQL), Anthropic Claude Haiku, Toss Payments, Supabase Auth
- **테스트 프레임워크**: Vitest 4.x + @testing-library/react
- **설계 문서**: `/Users/kangnam/projects/dear-jeongbin/docs/llm/design-spec.md`

## 테스트 현황 (2026-03-31)

| 항목 | 수치 |
|------|------|
| 테스트 파일 | 19개 |
| 총 테스트 케이스 | 170개 |
| 전체 커버리지 (statements) | 78.18% |
| 전체 커버리지 (lines) | 78.51% |

## 테스트 파일 구조

```
tests/
  setup.ts                         — 환경변수 + Next.js headers mock
  unit/
    services/
      credit.service.test.ts       — 기존 16개 + checkCreditAvailability 5개
      payment.service.test.ts      — 기존 7개 + confirmPayment 성공/cancelPayment 확장
      ai.service.test.ts           — 기존 5개
      resume.service.test.ts       — 기존 7개
      application.service.test.ts  — 기존 5개
      gap-analysis.service.test.ts — 신규: listGapAnalyses, getGapAnalysis, createGapAnalysisStream
      document.service.test.ts     — 신규: listDocuments, getDocument, createDocumentStream
      interview.service.test.ts    — 신규: listInterviewQuestions, generateInterviewQuestions
      referral.service.test.ts     — 신규: applyReferralCode, completeReferralBonus
    api/
      auth.test.ts                 — POST /api/v1/auth/signup
      gap-analysis.test.ts         — GET/POST /api/v1/gap-analyses
      payments.test.ts             — POST /api/v1/payments/prepare, /confirm
      credits.test.ts              — GET /api/v1/credits/balance
    components/
      score-gauge.test.tsx         — ScoreGauge 점수/등급/크기 렌더링
      blur-preview.test.tsx        — BlurPreview 잠금/CTA
      credit-badge.test.tsx        — CreditBadge 로딩/잔액/색상
      sse-progress.test.tsx        — SSEProgress 단계/오류/재시도
  integration/
    credit-flow.test.ts            — deduct→complete/rollback 전체 흐름
    payment-flow.test.ts           — prepare→confirm→크레딧 충전 전체 흐름
```

## 서비스별 커버리지 (핵심)

| 서비스 | Stmts | Lines |
|--------|-------|-------|
| credit.service.ts | 89.23% | 88.88% |
| document.service.ts | 98.52% | 98.46% |
| gap-analysis.service.ts | 94.68% | 96.59% |
| interview.service.ts | 95.74% | 95.12% |
| referral.service.ts | 91.89% | 91.66% |
| payment.service.ts | 76.63% | 78.21% |

## 중요 패턴

### Zod v4 UUID 검증
- `z.string().uuid()`는 Zod v4에서 엄격한 UUID 형식 요구
- 테스트에서 `"00000000-0000-0000-0000-000000000001"` 같은 형식은 실패
- 올바른 예: `"123e4567-e89b-42d3-a456-426614174000"`

### createAISSEStream mock 패턴
- `createAISSEStream`은 `onComplete` 콜백으로 `fullText`를 서비스에 전달
- mock에서는 `mockImplementation(makeAIStreamFactory(jsonString))` 패턴 사용
- factory가 stream 내에서 `onComplete` 콜백을 직접 호출해야 함

### vi.mock 호이스팅 주의
- `vi.mock` 내 factory에서 top-level 변수 참조 금지 (호이스팅 문제)
- 컴포넌트 hook mock은 `vi.mocked(hookFn)` 패턴 사용

### interview.service 이중 rollback
- AI 파싱 실패 시: inner try에서 1번 + outer catch에서 1번 = 총 2번 rollback
- `$transaction` 호출 횟수: deduct(1) + inner rollback(1) + outer rollback(1) = 3번

**Why:** 비즈니스 로직 분석 기준 문서
**How to apply:** 통합 테스트에서 $transaction 호출 횟수 어설션 시 실제 서비스 코드 흐름 확인 필요
