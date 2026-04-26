---
name: dear-jeongbin E2E patterns
description: Playwright setup, WS mocking strategy, test harness route, and iframe click approach for dear-jeongbin zone-edit E2E tests
type: project
---

## Project: dear-jeongbin E2E setup

**Repo**: `~/projects/dear-jeongbin`
**Config**: `playwright.config.ts` at repo root, Chromium-only, single worker, 30s timeout

### Server setup
- Backend (Rust Axum) must be running: `npm run server` (port 35470)
- Frontend (Vite) must be running: `npm run dev` (port 35480)
- `playwright.config.ts` uses `reuseExistingServer: true` — only the Vite server is in the webServer config; the Axum server is NOT (it fails to spawn in Playwright's subprocess due to rustup PATH issues)
- **Why Axum not in webServer**: `npm run server` calls `cargo run` which needs rustup in PATH — Playwright's process environment doesn't have it. Set up the server manually before running tests.

### WebSocket mocking
- All WS tests use `page.routeWebSocket(/\/api\/v1\/ws/, ...)` via `tests/e2e/fixtures/ws-mock.ts`
- The WS URL is intercepted at the browser level (before Vite proxy). The regex `/\/api\/v1\/ws/` matches `ws://localhost:35480/api/v1/ws`
- For streaming methods (`exports.edit_zone`, `exports.edit_zones_batch`): send `stream.event` notifications with `request_id = String(id)` first, then a final JSON-RPC response `{jsonrpc: "2.0", id, result: null}` to resolve the stream promise
- The ws-client uses `request_id` field in the notification params to match streams

### Test harness page
- `/e2e-zone-test` — lazy route in `src/router.tsx` → `src/app/e2e-zone-test/page.tsx`
- Mounts `PreviewPanel` directly with 7-zone keynote HTML fixture (no auth, no DB, no backend needed)
- Accepts `?exportId=<id>` query param
- DO NOT link this from any production UI page

### Iframe zone clicking
- Zones live inside `<iframe sandbox="allow-same-origin">` with `srcDoc`
- Playwright frame locators work for assertions (`page.frameLocator('iframe[title="Export Preview"]').locator('[data-edit-zone="..."]')`)
- For triggering clicks (to fire the delegated click listener on `doc`), use `page.evaluate()` + `new MouseEvent("click", { metaKey, ctrlKey })` dispatched on the zone element
- `page.click()` inside iframe doesn't work because `pointerEvents` on the iframe is toggled by zone-edit mode; `page.evaluate()` bypasses that

### Locator gotcha
- `page.getByText("2개 영역")` matches 2 elements in MultiZoneEditPanel (header span + description paragraph)
- Use `page.locator("text=일괄 편집 · 2개 영역")` (exact header text) instead

**Why:** Feedback from first run — strict mode violation on text locator.
**How to apply:** When asserting MultiZoneEditPanel zone count, always use the full header text "일괄 편집 · N개 영역".
