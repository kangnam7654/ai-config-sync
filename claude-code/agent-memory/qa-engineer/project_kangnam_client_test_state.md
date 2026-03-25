---
name: kangnam-client 프로젝트 테스트 현황 (2026-03-25)
description: React 19 + Tauri 2 (Rust) 데스크탑 LLM 클라이언트 테스트 스택 진단 결과
type: project
---

React 19 + TypeScript + Rust Tauri 2 기반 데스크탑 LLM 클라이언트.

**Why:** 테스트 커버리지 진단 요청 — 프론트엔드 22개 컴포넌트 중 테스트 유무 파악, Rust 백엔드 현황 파악 목적.

**How to apply:** 테스트 추가 작업 시 이 현황을 기준점으로 삼아라. 특히 Rust SSE 파서, auth/manager, db/skills는 테스트 우선순위가 높다.

## 진단 결과 요약 (총점: 3.3/10)

### 프론트엔드 테스트 현황
- 테스트 파일: 2개 (providers.test.ts, utils.test.ts)
- 테스트 대상 컴포넌트: 0/22 (컴포넌트 미테스트)
- 테스트 대상 lib: 2/4 (providers.ts, utils.ts — tauri-api.ts, app-store.ts 미테스트)
- 테스트 환경: `node` (DOM 없음) — React 컴포넌트 테스트 불가 상태
- Vitest 설정: environment: 'node' — jsdom/happy-dom 미설정

### Rust 테스트 현황
- 테스트 모듈이 있는 파일: 3/41 (db/conversations.rs, db/schema.rs, auth/pkce.rs)
- 전체 테스트 함수 수: 12개
- 미테스트 핵심 모듈: auth/manager.rs, auth/token_store.rs, providers/sse.rs, providers/claude.rs, providers/codex.rs, db/skills.rs, mcp/bridge.rs

### CI 상태
- GitHub Actions ci.yml: cargo test + npm test 양쪽 실행 (구조는 정상)
- cargo clippy에 `continue-on-error: true` 설정 (lint 실패를 CI 통과로 처리)
