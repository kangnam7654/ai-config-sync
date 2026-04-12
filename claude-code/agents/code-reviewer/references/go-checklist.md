> **Scope:** This checklist is for REVIEW only (read-only, no code fixes). For resolving Go build/vet errors, use the `build-resolver` agent.

# Go Review Checklist

Detailed review rules for Go code. Loaded by code-reviewer when diff contains `.go`, `go.mod`, or `go.sum` files.

## File Classification

| Category | Detection Rule | Action |
|---|---|---|
| **generated** | First 5 lines contain `Code generated` or `DO NOT EDIT`; path matches `*.pb.go`, `*.pb.gw.go`, `*_gen.go`, `*_generated.go`; inside `ent/`, `sqlc/`, `mock_*/` dir | Skip. Log: `[SKIP] {filepath}: generated ({matched rule}).` |
| **vendored** | Path starts with `vendor/` | Skip. Log: `[SKIP] {filepath}: vendored.` |
| **cgo** | Contains `import "C"` | Review Go code only. Skip C code in `/* */` blocks preceding `import "C"`. Note: "C code sections out of scope." |
| **build-tagged** | Contains `//go:build` or `// +build` in first 10 lines | Review normally. Note the constraint and applicable platforms. |
| **test** | Name matches `*_test.go` | Apply test-specific rules (see below) |
| **go.mod** | `go.mod` | Check dependencies, replace directives, go version |
| **go.sum** | `go.sum` | Only verify: if go.mod changed, go.sum should too. If go.sum changed without go.mod, flag HIGH. |

## Static Analysis Commands

```bash
go vet ./... 2>&1
staticcheck ./... 2>&1 || true
```

Do NOT run: `go mod tidy`, `go get`, `go build`, `golangci-lint` (unless `.golangci.yml` exists).

## Review Rules

### CRITICAL — Must Block

| ID | Issue | Detection Rule |
|---|---|---|
| GO-SEC-1 | SQL injection | String concatenation or `fmt.Sprintf` in `database/sql` `.Query()`, `.QueryRow()`, `.Exec()` instead of `?` or `$N` placeholders |
| GO-SEC-2 | Command injection | Variable interpolation in `exec.Command` / `exec.CommandContext` without allowlist validation |
| GO-SEC-3 | Path traversal | User-derived value passed to `os.Open`, `os.Create`, `os.ReadFile`, `os.WriteFile` without `filepath.Clean()` AND prefix check |
| GO-SEC-4 | Insecure TLS | `InsecureSkipVerify: true` in `tls.Config` |
| GO-SEC-5 | Hardcoded secret | String literal matching API key patterns, `password := "..."`, `secret := "..."`, `token := "..."` |
| GO-RACE-1 | Data race | Shared mutable state from multiple goroutines without `sync.Mutex`, `sync.RWMutex`, `sync/atomic`, or channel serialization |
| GO-ERR-1 | Ignored I/O error | `_` discarding error from `os`, `io`, `net`, `database/sql`, `net/http`, `crypto` packages |

### HIGH — Should Block Unless Justified

| ID | Issue | Detection Rule |
|---|---|---|
| GO-ERR-2 | Ignored non-I/O error | `_` discarding error from other functions |
| GO-ERR-3 | Missing error context | `return err` without `fmt.Errorf("ctx: %w", err)`. Exception: single-line functions where name provides context. |
| GO-ERR-4 | Panic in library | `panic()` outside `main()` or `init()` for recoverable errors |
| GO-CONC-1 | Goroutine leak | Goroutine without `context.Context` cancellation or `done` channel |
| GO-CONC-2 | Channel deadlock | `make(chan T)` where sender and receiver are in same goroutine |
| GO-CONC-3 | Missing defer Unlock | `mu.Lock()` without `defer mu.Unlock()` on next line |
| GO-MOD-1 | Local replace | `replace` directive pointing to local filesystem path |
| GO-MOD-2 | Go version change | `go` directive version changed |
| GO-MOD-3 | Major dependency bump | Major version increase in any `require` entry |

### MEDIUM — Should Fix Before Merge

| ID | Issue | Detection Rule |
|---|---|---|
| GO-QUAL-1 | Function over 60 lines | Count non-blank, non-comment lines between `func` and closing `}`. Threshold: 60. |
| GO-QUAL-2 | Cyclomatic complexity over 15 | Count `if`, `else if`, `case`, `for`, `&&`, `\|\|` in single function. Threshold: 15. |
| GO-QUAL-3 | Non-idiomatic control flow | `if cond { ... } else { return ... }` — invert to early return |
| GO-PERF-1 | String concat in loop | `+=` on `string` in `for` loop. Use `strings.Builder`. |
| GO-PERF-2 | Missing slice prealloc | `append()` in `for` loop with known iteration count. Use `make([]T, 0, n)`. |
| GO-PERF-3 | N+1 query | `database/sql` query inside `for` loop |
| GO-PAT-1 | Context not first param | Exported function with `context.Context` not as first parameter |
| GO-PAT-2 | Error message format | Error string starting with uppercase or ending with punctuation |
| GO-PAT-3 | Package naming | Package name with underscores, mixed case, or >12 characters |
| GO-PAT-4 | Mutable package var | `var` at package level with non-constant type. Exceptions: `sync.Once`, `sync.Pool`, `regexp.MustCompile` |

### LOW — Informational

| ID | Issue | Detection Rule |
|---|---|---|
| GO-DOC-1 | Missing GoDoc | Exported symbol without `//` comment on preceding line |
| GO-QUAL-4 | Unused parameter | Parameter not referenced in body (unless required by interface) |
| GO-QUAL-5 | Magic number | Numeric literal other than 0, 1, -1 without named constant. Exception: test files. |

## Test File Rules (`*_test.go`)

**Rules that apply**: All CRITICAL, goroutine leak (HIGH), error handling in test helpers (`testing.TB`).

**Rules that do NOT apply**: GO-DOC-1, GO-PAT-3, GO-QUAL-5, GO-QUAL-1 (flag only if >150 lines), GO-QUAL-3, GO-PAT-4.

**Additional test checks**:

| ID | Check | Severity |
|---|---|---|
| GO-TEST-1 | 3+ similar assertion blocks without table-driven pattern | MEDIUM |
| GO-TEST-2 | Test functions missing `t.Parallel()` without shared mutable state | LOW |
| GO-TEST-3 | Helper accepting `*testing.T`/`*testing.B` calling `t.Fatal`/`t.Error` without `t.Helper()` | MEDIUM |

## go.mod/go.sum Review

| Check | Severity |
|---|---|
| New `require` entry — flag for justification | MEDIUM |
| Major version bump (e.g., `v1.x` to `v2.x`) | HIGH |
| 3+ dependencies change simultaneously (minor/patch) | MEDIUM |
| `replace` directive to local path | HIGH |
| `go` directive version change | HIGH |
| `go.sum` changed but `go.mod` did not | HIGH |
