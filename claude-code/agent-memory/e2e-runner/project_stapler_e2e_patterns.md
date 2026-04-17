---
name: Stapler E2E test patterns
description: Key patterns for writing E2E tests in the Stapler/Paperclip project
type: project
---

Stapler E2E tests live in `tests/e2e/` (not `ui/e2e/`) and are run with:
```
pnpm test:e2e
PAPERCLIP_E2E_BASE_URL=http://localhost:3100 pnpm test:e2e  # against running server
```

**Why:** The playwright.config.ts at tests/e2e/playwright.config.ts has testDir: "." and the webServer command starts `pnpm paperclipai run`.

**URL structure:** All company-scoped routes are prefixed with `/:issuePrefix/`, e.g. `/eebaa/company/settings`, `/eebaa/agents/:id/configuration`. The `issuePrefix` comes from the company API response. Navigate using: `/${company.issuePrefix.toLowerCase()}/${path}`.

**Company selection:** Set `localStorage.setItem("paperclip.selectedCompanyId", id)` via `page.evaluate()` before navigating to company-scoped pages. CompanyContext reads from this key.

**Agent creation:** role must be one of: ceo, chro, cto, cmo, cfo, engineer, designer, pm, qa, devops, researcher, general. Use "engineer" for tests.

**Bulk-apply API:** `POST /api/companies/:id/agents/bulk-apply` returns `{ data: { updatedAgentIds, mode } }` (wrapped in `data`).

**Button selectors:** Buttons often have aria-label != visible text. Use `getByText("text", { exact: true })` for reliable selection. Examples:
- "모든 에이전트 일괄 변경" (text) vs aria-label "모든 에이전트 어댑터 일괄 변경"
- "에이전트에 일괄 적용..." (text) vs aria-label "LM Studio 기본값을 에이전트에 일괄 적용"

**GlobalModal Step 3:** agents are NOT auto-selected — must click "전체 선택" before "다음" is enabled.

**InheritableField badge:** aria-label="Inherited from company default" when field is in inherit mode.
