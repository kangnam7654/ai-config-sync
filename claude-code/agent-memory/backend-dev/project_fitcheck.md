---
name: fit-check project details
description: Stack, file structure, API conventions, and critical implementation notes for the fit-check MVP at /Users/kangnam/projects/dear-jeongbin/fit-check
type: project
---

fit-check는 채용공고-이력서 Gap 진단 + 맞춤 서류 생성 AI 서비스 (한국 IT/사무직 경력직 타겟).

**Why:** 1인 MVP 4주 개발 (2026-04-01 ~ 2026-04-28). Exit Criteria: Month 3까지 가입 100명 + 유료 전환 1명 이상.

**How to apply:** 구현 시 단순성 우선. 크레딧 원자성은 Prisma $transaction 필수. design-spec.md를 구현 전 반드시 읽을 것.

## Stack (실제 설치된 버전)

- Framework: Next.js 16.2.1 App Router Route Handlers (TypeScript 5)
- ORM: Prisma 7.6.0 + `@prisma/adapter-pg` (pg 어댑터 필수)
- DB: Supabase PostgreSQL 15+
- Auth: Supabase Auth (JWT, httpOnly cookie, @supabase/ssr 0.10)
- AI: Claude Haiku 4.5 (@anthropic-ai/sdk 0.80), SSE streaming
- Payment: 토스페이먼츠 REST API
- Validation: Zod v4.3.6
- Testing: Vitest 4.1.2

## Critical Prisma 7 Notes

- `url`/`directUrl`은 `schema.prisma`에 없어야 함 — `prisma.config.ts`에서 관리
- `PrismaClient`는 반드시 `{ adapter: new PrismaPg({ connectionString }) }` 로 생성
- JsonValue 칼럼에 `Record<string,unknown>` 넣을 때: `JSON.parse(JSON.stringify(obj))` 패턴 사용

## Critical Zod v4 Notes

- `ZodError.issues` (`.errors`가 아님)
- enum 파라미터: `{ error: "msg" }` (`.errorMap`이 아님)
- `z.record(z.string(), z.unknown())` 패턴 사용

## Critical Next.js 16 Notes

- Dynamic route params는 Promise: `{ params }: { params: Promise<{ id: string }> }` — `await params` 필수

## API Design doc

- 경로: `/Users/kangnam/projects/dear-jeongbin/docs/llm/design-spec.md` (FINAL, 2026-03-31)
- 38개 엔드포인트, 9개 도메인

## 크레딧 규칙

- Gap Analysis: 무료 월 3회 (credit_balances.free_used_this_month), 이후 1크레딧
- 서류 생성 (자소서/경력기술서): 2크레딧, 무료 혜택 없음
- 면접 예상질문: 1크레딧, 무료 혜택 없음
- 크레딧 차감 플로우: deductCredit() → status=pending → AI 성공 시 completeCreditTransaction() → 실패 시 rollbackCreditTransaction()

## 파일 위치 (구현 완료)

- 프로젝트 루트: `/Users/kangnam/projects/dear-jeongbin/fit-check/`
- Prisma 스키마: `prisma/schema.prisma` (14 테이블, url 없음)
- Prisma 설정: `prisma.config.ts` (DATABASE_URL 사용)
- Supabase 마이그레이션: `supabase/migrations/V001-V005`
- Prisma 클라이언트: `src/lib/prisma/client.ts` (PrismaPg 어댑터 사용)
- 서비스 레이어: `src/lib/services/` (credit, payment, ai, resume, gap-analysis, document, interview, application, referral, event)
- Route Handlers: `src/app/api/v1/` (38개 엔드포인트)
- 미들웨어: `middleware.ts` (rate-limit + auth redirect)
- 테스트: `tests/unit/services/` (34개 테스트, 100% pass)
