# E2E Playwright Patterns — Browser-Based Testing

This reference file contains the complete E2E workflow, Playwright commands, Page Object Model patterns, flaky test handling, and CI configuration. Read this file when qa-engineer enters E2E mode.

## Critical User Journey (Definition)

Write E2E tests only for flows that meet at least one of these criteria:

1. **Involves money or payment** — checkout, subscription, refund, billing update, coupon redemption
2. **Creates or deletes user data** — account registration, account deletion, profile update, content creation/deletion
3. **Top 5 most-used flows by page views** — when analytics are unavailable, treat these as critical: login/logout, main dashboard/home, primary search, primary listing/detail, settings

Flows that meet none of these criteria should be tested with unit or integration tests instead.

## Priority Assignment

- **P0**: Involves money/payment
- **P1**: Creates/deletes user data
- **P2**: Top 5 most-used flows

## Playwright Commands

```bash
npx playwright test                        # Run all E2E tests
npx playwright test tests/auth.spec.ts     # Run specific file
npx playwright test --headed               # Run with visible browser
npx playwright test --debug                # Playwright Inspector
npx playwright test --trace on             # Full trace recording
npx playwright test --repeat-each=5        # Repeat each test N times (flakiness check)
npx playwright show-report                 # View HTML test report
npx playwright test --reporter=json        # JSON output for CI parsing
```

## Workflow

### 1. Plan

For each critical user journey, define three scenario types:

- **Happy path** — the expected successful flow
- **Error cases** — invalid input, network failure, permission denied
- **Edge cases** — empty states, boundary values, concurrent actions

**Output**: List of journeys with their priority (P0/P1/P2) and scenario types.

### 2. Create

- Use the **Page Object Model (POM)** pattern — one class per page/component
- Use Playwright's accessible locators (`getByRole`, `getByLabel`, `getByText`) or `data-testid` attributes as locators. Do NOT use CSS class selectors (`.my-class`), element IDs (`#my-id`), or XPath. If neither accessible locators nor `data-testid` are viable, add `data-testid` to the source code and document what was added.
- Add `expect()` assertions at every key step, not only at the end of the flow
- Use proper waits: `waitForResponse()`, `waitForURL()`, `expect(locator).toBeVisible()`
- File structure: `tests/e2e/{journey-name}.spec.ts`
- Tag critical journey tests: `test('@critical checkout completes with valid card', ...)`

**Output**: The test file(s) with POM classes and test functions.

### 3. Execute

- Run locally >= 3 times (`--repeat-each=3`) to verify stability before committing
- Quarantine any test that fails intermittently: `test.fixme(true, 'Flaky — Issue #NNN')`
- Ensure screenshots and traces are configured for failure capture

**Output**: Pass/fail results across all repeat runs. Any quarantined tests listed with issue numbers.

## Setup Patterns

### Playwright Not Installed

If `npx playwright test` fails with "not found" or "no browsers installed":

```bash
npm init playwright@latest
npx playwright install --with-deps
npx playwright --version
```

**Output**: Report setup steps taken and Playwright version installed.

### Authentication (storageState)

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /global-setup\.ts/ },
    {
      name: 'e2e',
      dependencies: ['setup'],
      use: { storageState: 'tests/e2e/.auth/state.json' },
    },
  ],
});
```

Create `tests/e2e/global-setup.ts` for login. Add `.auth/` to `.gitignore`.

### Database Seeding

```typescript
export default defineConfig({
  globalSetup: require.resolve('./tests/e2e/seed.ts'),
  globalTeardown: require.resolve('./tests/e2e/teardown.ts'),
});
```

Each test must tolerate running in any order — seed scripts set a known baseline, but tests must not depend on execution order.

### CI Configuration

- Run headless (Playwright default — do not set `headless: false` in config)
- Enable retries: `retries: process.env.CI ? 2 : 0`
- Upload `test-results/` directory as artifact on failure
- Single worker if resource-constrained: `workers: process.env.CI ? 1 : undefined`
- Per-test timeout: `timeout: 30_000` (30 seconds)

## Flaky Test Handling

| Cause | Fix |
|-------|-----|
| Race condition — element not ready | `expect(locator).toBeVisible()` before interaction |
| Network timing — API response not arrived | `page.waitForResponse(url)` before asserting |
| Animation in progress | `expect(locator).toBeVisible()` or disable animations in test config |
| Shared state between tests | Independent setup per test with `beforeEach` |
| Non-deterministic data | Use seeded test data, not production/random data |

Quarantine pattern:
```typescript
test('flaky: checkout total calculation', async ({ page }) => {
  test.fixme(true, 'Flaky — intermittent timeout on price API. Issue #123');
});

// Verify flakiness: npx playwright test tests/e2e/checkout.spec.ts --repeat-each=10
```

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Critical journey pass rate | 100% | `npx playwright test --grep @critical --reporter=json` |
| Overall pass rate | > 95% | `npx playwright test --reporter=json` |
| Flaky test rate | < 5% | `npx playwright test --repeat-each=5 --reporter=json` |
| Suite duration | < 10 minutes | Check `stats.duration` in JSON report |
| Quarantined tests | 0 (aspirational) | `grep -r "test.fixme" tests/e2e/ --include="*.spec.ts" \| wc -l` |
