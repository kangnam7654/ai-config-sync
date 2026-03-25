---
name: kangnam-client 프로젝트 테스트 현황 (2026-03-25)
description: React 19 + Tauri 2 (Rust) 데스크탑 LLM 클라이언트 테스트 스택 상세 진단 결과 (2차 갱신)
type: project
---

React 19 + TypeScript + Rust Tauri 2 기반 데스크탑 LLM 클라이언트.

**Why:** 테스트 커버리지 진단 요청 — 프론트엔드 35개 소스파일, Rust 42개 소스파일 전체 진단 목적.

**How to apply:** 테스트 추가 작업 시 이 현황을 기준점으로 삼아라. P0/P1 항목 우선 작업.

## 진단 결과 요약 (총점: 3.3/10)

### 전체 커버리지
- Frontend: 2 / 35 파일 = 5.7%
- Rust: 3 / 42 파일 = 7.1%
- 전체: 5 / 77 파일 = 6.5%
- 총 테스트 함수: 33개 (TS: 21개, Rust: 12개), E2E: 0개

### 테스트 파일 목록
- `src/renderer/lib/utils.test.ts` — cn() 7개 단위 테스트 (품질 양호)
- `src/renderer/lib/providers.test.ts` — estimateTokens/getVisibleProviders/getContextWindow/getProviderInfo 14개 (범위 기반 assertion이 일부 약함)
- `src-tauri/src/auth/pkce.rs` — 3개 (길이만 검증, 알고리즘 정확성 미검증)
- `src-tauri/src/db/conversations.rs` — 7개 통합 테스트 (in-memory SQLite, 품질 양호)
- `src-tauri/src/db/schema.rs` — 2개 (migration idempotency + 테이블 존재 확인)

### 주요 미테스트 영역 (우선순위 순)
- P0: `providers/sse.rs` — parse_sse_event, split_sse_events, split_lines (전체 스트리밍 파이프라인)
- P0: `vitest.config.ts` — environment: 'node' (DOM 없음, React 컴포넌트/store 테스트 불가)
- P1: `db/skills.rs` — create/update/delete/get_skill_instructions (references 조합 로직)
- P1: `db/agents.rs` — CRUD + allowed_tools JSON 직렬화
- P1: `auth/manager.rs` — normalize_claude_token, get_status, get_access_token 만료 분기
- P1: `stores/app-store.ts` — pushToolCall, appendStreamingText 등 복합 상태 변환
- P2: `auth/token_store.rs` — keychain 추상화 없어 테스트 어려움
- P2: `mcp/bridge.rs` — JSON-RPC 매핑, 타임아웃 처리
- P3: E2E (Playwright) — 전무

### CI 상태
- GitHub Actions ci.yml: cargo test + npm test 양쪽 실행 (구조 정상)
- cargo clippy에 `continue-on-error: true` 설정 (lint 실패를 CI 통과로 처리 — 문제)
- cargo tarpaulin 미설정 (커버리지 수치 측정 불가)
- Playwright 미설정

### 테스트 인프라 상태
- Vitest: 4.1, environment: 'node' (jsdom/happy-dom 미설정)
- @testing-library/react: 미설치
- Playwright: 미설치
- Rust in-memory SQLite 패턴: conversations.rs에서 확립됨 (재사용 가능)
