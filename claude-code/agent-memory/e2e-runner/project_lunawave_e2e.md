---
name: lunawave E2E patterns
description: Playwright patterns for lunawave web — cookie injection, script name, CI flag, skip convention, SajuBasicView locators
type: project
---

## Script and config
- Test script: `pnpm e2e` (not `pnpm test:e2e`) — maps to `playwright test`
- Dev port: 3100 (not 3000/3001, those are taken on this machine)
- `webServer.reuseExistingServer: true` — but only skips spawn when `CI=1`; to run against an already-running server locally use `CI=1 PLAYWRIGHT_BASE_URL=http://localhost:3100 pnpm e2e ...`
- Projects: `chromium-desktop` (Desktop Chrome 1280px) and `chromium-mobile` (Pixel 7) — user rule: test only chromium-desktop for /saju and similar content pages

## Auth injection pattern
- Requires both `TEST_JWT_ACCESS_TOKEN` and `TEST_NEXTAUTH_TOKEN` env vars
- Cookie name is `next-auth.session-token` (http) or `__Secure-next-auth.session-token` (https)
- Skip guard at describe level: `test.skip(!TOKEN_A || !TOKEN_B, 'reason')`
- Mobile guard in `beforeEach`: `if (testInfo.project.name.includes('mobile')) test.skip(true, '...')`

## SajuBasicView locators (v0.0.3)
- Page h1: `getByRole('heading', { level: 1, name: '사주팔자' })` — renders before Suspense
- Suspense anchor (wait before asserting inner content): `page.getByText('일간(日干):')`
- Polarity chip: `page.getByText(/^(양\(陽\)|음\(陰\))$/)` — exact regex because both variants are valid
- GongmangView header: `page.getByText(/공망/)` — SectionHeader renders as span, not heading role
- ShinsalListView header: `page.getByText('길흉 신살')` — data-conditional; guard with `.count()` before asserting

## Conditional component pattern
When a component renders null on empty data (ShinsalListView returns null when shinsal.length === 0):
```ts
const el = page.getByText('길흉 신살');
if (await el.count() === 0) return; // graceful no-op
await expect(el).toBeVisible();
```

**Why:** shinsal presence depends on the test account's birth chart — forcing .toBeVisible() would create a flaky test tied to data.
