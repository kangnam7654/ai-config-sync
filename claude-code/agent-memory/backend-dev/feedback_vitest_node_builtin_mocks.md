---
name: vitest Node built-in module mocking pattern
description: How to correctly mock fs and child_process in vitest for dear-jeongbin/fit-check
type: feedback
---

For Node built-ins (`fs`, `child_process`) in vitest (jsdom), `vi.spyOn` and simple `vi.mock("fs", () => ({ promises: { readFile: vi.fn() } }))` do NOT intercept named imports reliably. The correct pattern:

**fs (named import `import { promises as fs } from "fs"`):**
```typescript
const mockReadFile = vi.fn();
vi.mock("fs", () => ({
  promises: { readFile: mockReadFile },
  default: { promises: { readFile: mockReadFile } },
}));
```

**child_process (named import `import { execFileSync } from "child_process"`):**
```typescript
const mockExecFileSync = vi.fn();
vi.mock("child_process", async (importOriginal) => {
  const actual = await importOriginal<typeof import("child_process")>();
  return {
    ...actual,
    default: { ...actual, execFileSync: mockExecFileSync },
    execFileSync: mockExecFileSync,
  };
});
```

`child_process` requires `importOriginal` spread because vitest demands a `default` export for it. `fs` does NOT need `importOriginal` — a plain object works.

**Why:** `vi.spyOn(fsModule.promises, "readFile")` spies on the test-file's import of `fs`, which may be a different module instance than what the SUT bound at its load time (jsdom creates separate module instances). The `vi.mock` factory approach replaces the module in the registry before the SUT loads, ensuring the SUT's named imports bind to our mocks.

**Also:** Use `vi.resetAllMocks()` in `beforeEach` (not `vi.clearAllMocks()`) to clear both call history AND implementations between tests, preventing implementation leakage from previous tests.

**How to apply:** Any time a module under test uses `import { ... } from "fs"` or `import { ... } from "child_process"`, use this pattern in vitest tests.
