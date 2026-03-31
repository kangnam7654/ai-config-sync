---
name: fit-check DB schema design
description: 핏체크(fit-check) AI 커리어 코치 웹앱의 Supabase PostgreSQL 스키마 설계 (14 테이블, Prisma 6, RLS) - DB-API 정합성 검증 반영 rev.3
type: project
---

fit-check DB 스키마 rev.3를 2026-03-31에 완료. DB-API 정합성 검증 피드백 5건(M01-M05) 반영 후 재심사 대기 중.

**Why:** CTO DB-API 정합성 검증에서 FAIL. DB 스키마와 API 설계 간 불일치 5건 발견. Critical 2건(M01 credit tx status, M02 resumes delete 전략), Major 2건(M03 payments 취소, M04 event enum), Minor 1건(M05 referral_code).

**How to apply:**
- 설계 문서: `/Users/kangnam/projects/dear-jeongbin/docs/llm/db-schema.md`
- ERD: `/Users/kangnam/projects/dear-jeongbin/docs/db-schema-erd.mmd` + `.png`
- 기술 스택: Supabase (PostgreSQL 15+) + Prisma 6 + Supabase Auth
- 14 테이블: profiles, resumes, gap_analyses, generated_documents, interview_questions, applications, credit_balances, credit_transactions, payments, referrals, organizations, teams, organization_members, user_events
- rev.3 변경사항:
  1. [M01/Critical] credit_transactions.status 추가 (pending/completed/rolled_back) - AI 호출 실패 시 롤백 추적
  2. [M02/Critical] resumes hard delete 유지 결정 (DB 변경 없음, API 측 수정)
  3. [M03/Major] payments에 canceled_at + cancel_reason 추가 - 결제 취소 API 지원
  4. [M04/Major] user_events event_type 9개 합의 목록으로 DB-API 동기화
  5. [M05/Minor] profiles.referral_code(UNIQUE, auto-generated) 추가 - 레퍼럴 링크 식별자
- 승인 후 Prisma 스키마 파일 + SQL 마이그레이션 생성 예정
