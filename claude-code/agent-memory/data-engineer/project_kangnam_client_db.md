---
name: kangnam-client DB schema state
description: kangnam-client Tauri desktop app의 SQLite 스키마 현황 및 개선 설계 완료 상태
type: project
---

kangnam-client는 Tauri 2 + React 19 기반 데스크톱 LLM 클라이언트로, SQLite를 로컬 저장소로 사용한다.

**Why:** audit-report에서 DB 점수 5.3/10으로 인덱스 부재, FTS5 미사용, 마이그레이션 시스템 부재가 지적됨.

**How to apply:**
- DB 스키마 개선 설계문서: `docs/llm/db-schema-improvement.md`
- ERD: `docs/llm/db-schema-erd.mmd` (PNG 렌더링 완료)
- 마이그레이션 V001-V005 설계 완료, 사용자 승인 후 구현 단계 진행 예정
- 핵심 테이블: conversations, messages, prompts, mcp_servers, auth_tokens, skill_eval_* (6개)
- connection.rs에서 WAL 모드 + foreign_keys ON 설정
- busy_timeout 5000 -> 10000 변경 설계됨
