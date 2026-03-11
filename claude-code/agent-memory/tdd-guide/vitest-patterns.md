# Vitest Patterns & Gotchas

## Mocking node:child_process execFile (promisify)

When `helpers.ts` (or any module) calls `promisify(execFile)` at module-load time
and the test mocks `node:child_process` with `vi.mock`, the mocked `execFile` is a
plain `vi.fn()` with NO custom promisify symbol.

Consequence: `promisify` falls back to the standard `(err, value)` two-arg callback
form. So `execFileAsync` resolves with whatever is passed as the **second** callback
argument (not `(stdout, stderr)` positional args).

`runCommand` destructures `{ stdout, stderr }` from the resolved value, so the mock
**must** resolve with an object:

```ts
execFileMock.mockImplementation((...args: any[]) => {
  const cb = args[args.length - 1];
  cb(null, { stdout: "output", stderr: "" });  // correct
  // cb(null, "output", "")                    // WRONG — resolves with a string
});
```

For errors, attach `.stdout` / `.stderr` to the Error object (as the real execFile does):

```ts
const error = Object.assign(new Error("Command failed"), {
  code: 1,
  stdout: "partial",
  stderr: "err detail",
});
cb(error);
```

## Top-level await inside describe()

Do NOT use `await import(...)` inside a `describe` block — esbuild (used by vitest)
does not support top-level await outside async functions at the describe scope.

Use a static import at the top of the file instead:

```ts
import * as childProcess from "node:child_process";
vi.mock("node:child_process", () => ({ execFile: vi.fn() }));
// Then inside describe:
const execFileMock = vi.mocked(childProcess.execFile);
```

## Coverage scoping

Set `coverage.include` to only the files under test, not `src/**/*.ts`.
Otherwise untested tool files drag coverage below the threshold.

```ts
coverage: {
  provider: "v8",
  include: ["src/helpers.ts"],   // only files this test suite covers
  thresholds: { lines: 80, functions: 80, branches: 80, statements: 80 },
},
```

## Fake timers + async

```ts
beforeEach(() => vi.useFakeTimers());
afterEach(() => vi.useRealTimers());

it("resolves after delay", async () => {
  let done = false;
  const p = sleep(1000).then(() => { done = true; });
  vi.advanceTimersByTime(999);
  await Promise.resolve(); // flush microtasks
  expect(done).toBe(false);
  vi.advanceTimersByTime(1);
  await p;
  expect(done).toBe(true);
});
```
