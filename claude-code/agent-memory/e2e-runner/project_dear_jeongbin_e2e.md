---
name: dear-jeongbin E2E patterns
description: Playwright setup, WS mocking strategy, real-backend setup, AI stub, DB isolation, iframe click approach for dear-jeongbin zone-edit E2E tests
type: project
---

## Project: dear-jeongbin E2E setup

**Repo**: `~/projects/dear-jeongbin`
**Config**: `playwright.config.ts` at repo root, Chromium-only, single worker, 45s timeout

### Two test suites

1. **Mock tests** (`zone-edit.spec.ts`) — WebSocket intercepted, no backend needed. Run: `npx playwright test tests/e2e/zone-edit.spec.ts`
2. **Real backend tests** (`zone-edit-real.spec.ts`) — real Axum + real SQLite + AI stub. Run: `REAL_BACKEND=1 npx playwright test tests/e2e/zone-edit-real.spec.ts`

### Server setup
- Backend (Rust Axum): port 35470. `npm run server` (calls `cargo run --bin server`)
- Frontend (Vite): port 35480. `npm run dev`
- Backend webServer stanza only active when `REAL_BACKEND=1`. Requires `RUSTUP_HOME` and `CARGO_HOME` to be passed through (HOME override breaks rustup).
- DB isolation: set `HOME=~/.dear-jeongbin-e2e-tmp`. The DB lands at `HOME/.dear-jeongbin/data.db` and never touches user's production DB.
- **rustup PATH issue**: When HOME is overridden, rustup can't find toolchain config. Must also pass `RUSTUP_HOME=$HOME/.rustup` and `CARGO_HOME=$HOME/.cargo` (user's real HOME, not test HOME).

### AI stub (DEAR_JEONGBIN_AI_STUB=1)
- Gated in `src-tauri/src/services/ai.rs` → `build_provider_for_task()`
- When env var is "1", returns `StubProvider` instead of calling real LLM
- Single-zone: returns `<div data-edit-zone="stub">STUB EDITED</div>`
- Batch: parses `zone id=\`...\`` from prompt lines (batch template format) and returns JSON `{"zones":[{"id":"...","html":"..."},...]}` matching each zone
- NEVER set in production; logs a tracing::warn when active

### HTTP health endpoint
- `GET /api/v1/health` → `{"status":"ok","version":"..."}` — used as Playwright webServer readiness probe
- Route registered in `src-tauri/src/handlers/mod.rs` (added alongside /ws route)

### WebSocket mocking (mock tests only)
- All mock WS tests use `page.routeWebSocket(/\/api\/v1\/ws/, ...)` via `tests/e2e/fixtures/ws-mock.ts`
- The WS URL is intercepted at the browser level (before Vite proxy). The regex `/\/api\/v1\/ws/` matches `ws://localhost:35480/api/v1/ws`
- For streaming methods (`exports.edit_zone`, `exports.edit_zones_batch`): send `stream.event` notifications with `request_id = String(id)` first, then a final JSON-RPC response `{jsonrpc: "2.0", id, result: null}` to resolve the stream promise

### Test harness page
- `/e2e-zone-test` — lazy route in `src/router.tsx` → `src/app/e2e-zone-test/page.tsx`
- Mounts `PreviewPanel` directly with 7-zone keynote HTML fixture (no auth, no DB, no backend needed for mock tests)
- Accepts `?exportId=<id>` query param — maps to `zoneExportId` in PreviewPanel
- Both mock AND real tests reuse this harness (real tests use real backend but same UI harness)
- DO NOT link from any production UI page

### Iframe zone clicking
- Zones live inside `<iframe sandbox="allow-same-origin">` with `srcDoc`
- Playwright frame locators work for assertions (`page.frameLocator('iframe[title="Export Preview"]').locator('[data-edit-zone="..."]')`)
- For triggering clicks, use `page.evaluate()` + `new MouseEvent("click", { metaKey, ctrlKey })` dispatched on the zone element
- `page.click()` inside iframe doesn't work because `pointerEvents` on the iframe is toggled by zone-edit mode

### DB verification in real tests
- `tests/e2e/fixtures/seed.ts` — `querySqlite()`, `countOverrides()`, `insertOverride()`, `clearOverrides()`
- Uses `sqlite3` CLI (pre-installed on macOS/Linux) to shell out to the test DB
- DB path: `TEST_HOME/.dear-jeongbin/data.db`
- Each test clears its own override bucket at start (`clearOverrides(kind, exportId)`) so tests are independent

### Zone edit panel button labels
- Single-zone submit: "적용" (not "수정 적용")
- Batch submit: "일괄 적용"
- Reset override: "원본으로" (visible only when override exists in DB)
- Success toast after single edit: "영역이 수정되었습니다"
- Success toast after batch: "${count}개 영역이 수정되었습니다"
- Reset toast: "원본으로 되돌렸습니다"
- Override banner: "이미 수정된 영역입니다" (shown in ZoneEditPanel when override exists, loaded async)

### Locator gotcha
- `page.getByText("2개 영역")` matches 2 elements in MultiZoneEditPanel (header span + description paragraph)
- Use `page.locator("text=일괄 편집 · 2개 영역")` (exact header text) instead

**Why:** Feedback from first run — strict mode violation on text locator.
**How to apply:** When asserting MultiZoneEditPanel zone count, always use the full header text "일괄 편집 · N개 영역".

### Known type mismatch (not blocking)
- Backend sends `{type: "complete", override: ...}` for single-zone stream event
- Frontend ZoneEditPanel listens for `type === "result"` — so `currentOverride` state won't update in-session
- The DB IS persisted correctly, and on reload the override IS shown ("이미 수정된 영역입니다")
- Tests handle this: assert toast "영역이 수정되었습니다" (from promise resolve, not type check), then reload to verify persistence
