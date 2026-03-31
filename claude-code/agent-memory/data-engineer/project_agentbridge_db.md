---
name: AgentBridge DB Schema Design
description: AgentBridge WebSocket 허브의 SQLite 스키마 설계 완료 - sessions, messages, contexts 3테이블, WAL 모드
type: project
---

AgentBridge 프로젝트의 SQLite DB 스키마 설계가 완료됨 (2026-03-31).

**Why:** LLM 에이전트 간 실시간 메시지 교환 허브의 영속 저장소 필요.

**How to apply:**
- 설계 문서: `/Users/kangnam/projects/bagelcode/docs/llm/agentbridge-db-schema.md`
- ERD: `/Users/kangnam/projects/bagelcode/docs/agentbridge-erd.mmd` / `.png`
- 3개 테이블: sessions (TEXT PK, UUIDv4), messages (INTEGER PK, AUTOINCREMENT), contexts (INTEGER PK, namespace+key UNIQUE)
- SQLite WAL 모드, aiosqlite, ORM 없음
- 사용자 승인 후 구현 단계 진행 가능
