---
name: reviewers 프로젝트 테스트 현황 (2026-04-24)
description: Rust backend + React/Vite frontend, Playwright E2E 설정 완료
type: project
---

# reviewers 프로젝트 테스트 현황

**Path:** `/Users/kangnam/projects/reviewers`
**Stack:** Rust (Axum) backend + React 18 + Vite 5 frontend

## 테스트 스택

- Backend (Rust): `cargo test` — integration tests in `crates/backend/tests/`
- Frontend (Vitest): `npm test` — unit/integration tests in `web/tests/`
- E2E (Playwright): `npm run test:e2e` — `web/tests/e2e/`

## Playwright E2E 설정 (Task 30, 2026-04-24 완료)

- Config: `web/playwright.config.ts`
- Test: `web/tests/e2e/happy-path.spec.ts` — 1 test, 1/1 pass
- Backend env: `REVIEWERS_HELPER_BIN=/nonexistent` → MockHelper 폴백 (ADR-001 확인됨)
- LLM env: `REVIEWERS_LLM_PROVIDER=dummy`

**Why:** `vite.config.js` (stale compiled artifact without proxy config) was shadowing `vite.config.ts` (with proxy), causing all `/api/*` requests to return HTML fallback instead of proxying to backend. Deleted `vite.config.js` and `vite.config.d.ts` artifacts.

**How to apply:** If Vite proxy stops working in this project, check for `vite.config.js` artifacts that shadow `vite.config.ts`.

## 주요 발견 사항

- `StartRunForm`의 `<Label>Persona</Label>` / `<Label>Task</Label>` — `htmlFor` 없음 → `getByLabel()` 안 됨. `page.locator('label', { hasText: /^Persona$/ }).locator('..').getByRole('combobox')` 패턴 사용.
- Persona 다이얼로그 Save 버튼: 뷰포트 크기 1280x900 설정으로 해결 (기본 780px 높이에서는 out-of-viewport).
- backend 환경변수: `REVIEWERS_PORT`, `REVIEWERS_DATA_DIR`, `REVIEWERS_LLM_PROVIDER`, `REVIEWERS_HELPER_BIN`
- Vite 서버: `--host 127.0.0.1` 플래그로 IPv4 바인딩 필요 (playwright config URL이 127.0.0.1 사용)
