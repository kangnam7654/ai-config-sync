---
name: fit-check project context
description: fit-check (핏체크) 프로젝트 API 설계 및 스택 컨텍스트
type: project
---

fit-check는 채용공고-이력서 Gap 진단 + 맞춤 서류 생성 AI 서비스 (한국 IT/사무직 경력직 타겟).

**Why:** 1인 MVP 4주 개발. Exit Criteria: 가입 50명 WTP 검증, 유료 전환 150-750명/year.

**How to apply:** 구현 시 단순성 우선. 크레딧 원자성은 Prisma $transaction 필수.

## Stack
- Framework: Next.js 15 App Router Route Handlers (TypeScript 5)
- ORM: Prisma 6
- DB: Supabase PostgreSQL 15+
- Auth: Supabase Auth (JWT, httpOnly cookie, @supabase/ssr)
- AI: Claude Haiku 4.5 (@anthropic-ai/sdk), SSE streaming
- Payment: 토스페이먼츠
- API: REST, /api/v1 prefix

## API Design doc
- 경로: `/Users/kangnam/projects/dear-jeongbin/docs/llm/api-design.md`
- 상태: DRAFT (2026-03-31)
- 38개 엔드포인트 정의

## 크레딧 규칙
- Gap Analysis: 무료 월 3회 (credit_balances.free_used_this_month), 이후 1크레딧
- 서류 생성 (자소서/경력기술서): 2크레딧, 무료 혜택 없음
- 면접 예상질문: 1크레딧, 무료 혜택 없음
- 크레딧 차감 + credit_transactions 기록은 반드시 Prisma $transaction으로 묶기

## 파일 구조 핵심
- Route Handlers: `app/api/v1/`
- 서비스 레이어: `lib/services/` (credit, payment, ai, resume)
- 미들웨어: `lib/middleware/` (auth, rate-limit)
- Supabase 클라이언트: `lib/supabase/server.ts`, `lib/supabase/client.ts`
