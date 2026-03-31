---
name: fit-check DB schema design
description: 핏체크(fit-check) AI 커리어 코치 웹앱의 Supabase PostgreSQL 스키마 설계 (14 테이블, Prisma 6, RLS) - CTO 리뷰 반영 rev.2
type: project
---

fit-check DB 스키마 rev.2를 2026-03-31에 완료. CTO 리뷰 피드백 5건 반영 후 재심사 대기 중.

**Why:** auto-dev pipeline Step #12 (CTO DB 리뷰) FAIL(7.45/10, PASS 기준 8.0). Critical 2건 + Major 2건 + referrals 테이블 누락 수정.

**How to apply:**
- 설계 문서: `/Users/kangnam/projects/dear-jeongbin/docs/llm/db-schema.md`
- ERD: `/Users/kangnam/projects/dear-jeongbin/docs/db-schema-erd.mmd` + `.png`
- 기술 스택: Supabase (PostgreSQL 15+) + Prisma 6 + Supabase Auth
- 14 테이블: profiles, resumes, gap_analyses, generated_documents, interview_questions, applications, credit_balances, credit_transactions, payments, referrals, organizations, teams, organization_members, user_events
- CTO 리뷰 반영 사항:
  1. [Critical] gap_analyses, generated_documents, interview_questions: 클라이언트 SELECT-only (INSERT/UPDATE/DELETE 제거)
  2. [Critical] payments: DELETE 완전 제거, 서버 사이드 write-only, immutable
  3. [Major] user_events: user_id NOT NULL 강제, auth.uid() = user_id 필수
  4. [Major] referrals 테이블 추가 (referrer_id, referred_id, status, bonus_credited)
  5. credit_balances, credit_transactions: 서버 사이드 write-only 재확인
- RLS Policy Matrix 요약 테이블 추가 (Section 4.2)
- 승인 후 Prisma 스키마 파일 + SQL 마이그레이션 생성 예정
