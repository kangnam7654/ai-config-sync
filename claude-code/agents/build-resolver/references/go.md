# Go Build Error Resolution

## Diagnostic Commands

Run in this exact order. Stop at the first command that produces errors and begin resolution before continuing:

```bash
# Step 1: Check go.mod exists
ls go.mod || echo "MISSING_GOMOD"

# Step 1.5: Check for go.work (workspace mode)
ls go.work 2>/dev/null && echo "GO_WORKSPACE_MODE"

# Step 1.6: Detect Go version mismatch
GO_MOD_VER=$(grep '^go ' go.mod | awk '{print $2}')
GO_BIN_VER=$(go version | awk '{print $3}' | sed 's/go//')
echo "go.mod requires: $GO_MOD_VER, system has: $GO_BIN_VER"

# Step 2: Build
go build ./...

# Step 3: Vet
go vet ./...

# Step 4: Module integrity
go mod verify
```

Run these only after Steps 1–4 pass:

```bash
staticcheck ./... 2>/dev/null || true
golangci-lint run 2>/dev/null || true
```

## Common Error Patterns

| Error Pattern | Exact Fix |
|---------------|-----------|
| `undefined: X` | Add missing import, or fix identifier casing to match declaration |
| `cannot use X as type Y` | Insert explicit type conversion `Y(x)` or dereference `*x` |
| `X does not implement Y` | Add the missing method with the exact receiver type and signature from the interface definition |
| `import cycle not allowed` | Move shared types into a new `internal/shared` package; update imports in both sides |
| `cannot find package "P"` | Run `go get P@latest` then `go mod tidy` |
| `declared but not used` | Remove the unused variable. Use `_` blank identifier only if the variable is from a multi-return |
| `multiple-value in single-value context` | Expand to `result, err := fn()` with explicit `err` handling |
| `no required module provides package` | Run `go get package@latest && go mod tidy` |
| `ambiguous import` | Add explicit `replace` directive in `go.mod` to resolve the ambiguity |
| `410 Gone` or `403 Forbidden` on `go get`/`go mod download` | Check `go env GOPRIVATE` — add the module prefix if missing |
| `go.mod requires go >= X.Y` | System Go is too old — report version mismatch, do NOT attempt code fixes |

**Go-specific notes:**
- For CGo failures (`gcc:`, `cgo:`, `ld:` errors): report missing compiler/headers, do NOT attempt code fixes
- For `go.work` workspace mode: run `go work sync` before build attempts
- NEVER modify `vendor/` directly — use `go mod vendor` to regenerate
- NEVER add `//nolint` directives without explicit user approval
- NEVER run `go clean -modcache` without user confirmation

## Framework-Specific Issues

### Missing `go.mod`

If diagnostic Step 1 outputs `MISSING_GOMOD`:
1. Detect module path: read the most common import path from `*.go` files in the directory using `grep -r "package " --include="*.go" -l`
2. Run `go mod init <detected_module_path>`
3. Run `go mod tidy`
4. Re-run the full diagnostic sequence

### CGo Build Failures

Errors matching `gcc:`, `cc1:`, `cgo:`, `ld:`, or `#include .* no such file`:
1. Check if gcc/cc is installed: `which gcc || which cc`
2. If the compiler is **not installed**: STOP. Report to user: "CGo compilation requires a C compiler (gcc/clang). Install it and retry." Do NOT attempt to fix.
3. If the compiler **is installed** but headers are missing: report the exact missing header and the OS-specific install command (e.g., `apt install libxxx-dev` or `brew install xxx`)
4. If `CGO_ENABLED=0` would resolve the issue (pure Go alternative exists), suggest `CGO_ENABLED=0 go build ./...` as a workaround

### Cross-Compilation (GOOS/GOARCH Mismatch)

Errors matching `cannot find package` or linker errors when `GOOS` or `GOARCH` environment variables differ from the host:
1. Run `go env GOOS GOARCH GOHOSTOS GOHOSTARCH` to detect mismatch
2. If GOOS != GOHOSTOS or GOARCH != GOHOSTARCH, report: "Cross-compilation detected (target: {GOOS}/{GOARCH}, host: {GOHOSTOS}/{GOHOSTARCH})"
3. If the error is CGo-related during cross-compilation: suggest `CGO_ENABLED=0` or installing the appropriate cross-compiler toolchain
4. If the error is missing platform-specific files: check for `_GOOS.go` or `_GOARCH.go` suffixed files and build constraints

### Vendoring Issues

If `vendor/` directory exists in the module root:
1. Check `go.mod` for `// +build tools` or tooling inconsistencies
2. Run `go mod vendor` to regenerate the vendor directory
3. Run `go build -mod=vendor ./...` to verify
4. If `go mod vendor` itself fails, run `go mod tidy` first, then `go mod vendor` again

### Build Tags / Build Constraints

Errors referencing `//go:build` or `// +build` constraints:
1. Read the build constraint line from the failing file
2. Check if the required tag is passed: `go build -tags="tagname" ./...`
3. Report to user which tags are required: "File {path} requires build tag `{tag}`. Build with: `go build -tags=\"{tag}\" ./...`"
4. NEVER remove or modify build constraints to fix a build — they are intentional

### `go generate` Errors

If `go generate ./...` was run and produced errors:
1. Do NOT attempt to fix `go generate` tool failures (protoc, stringer, mockgen failures are outside scope)
2. Report the exact error and which `//go:generate` directive produced it
3. Continue resolving remaining non-generate build errors

### Go Workspace Mode (`go.work`)

If diagnostic Step 1.5 outputs `GO_WORKSPACE_MODE`:
1. Run `go work sync` before attempting any build
2. If `go build ./...` fails with `no required module provides package` within a workspace, check that all workspace modules are listed in `go.work` via `cat go.work`
3. If a `use` directive points to a non-existent directory, report to user: "go.work references missing directory `{dir}`. Remove the stale `use` directive or restore the module."
4. Run `go build ./...` from the workspace root (the directory containing `go.work`), not from individual module directories

### Private Module Authentication Failure

Errors matching `410 Gone`, `403 Forbidden`, or `401 Unauthorized` during `go mod download` or `go get`:
1. Identify the private module path from the error output
2. Check current GOPRIVATE setting: `go env GOPRIVATE`
3. If the failing module's path is NOT covered by GOPRIVATE, report to user: "Module `{module}` requires private access. Set GOPRIVATE: `go env -w GOPRIVATE={module_prefix}`"
4. If GOPRIVATE is already set correctly, check Git credential access: `git ls-remote https://{module_host}/{module_path}` — if this also fails, report: "Git credentials for `{module_host}` are missing or expired. Configure access before retrying."
5. NEVER store or request credentials — only diagnose and report

### Build Cache Corruption

If the same build error persists after 2 correct fix attempts where the source code is verified to be valid:
1. Run `go build -x ./... 2>&1 | head -50` to inspect whether stale cached artifacts are being reused
2. Report to user: "Build cache may contain stale artifacts. Run `go clean -cache` to reset the build cache, then retry."
3. NEVER run `go clean -cache` without explicit user confirmation (it forces full rebuild of all dependencies)
4. After the user confirms and runs `go clean -cache`, re-run the full diagnostic sequence from Step 1

### Go Version Mismatch

If diagnostic Step 1.6 shows the `go.mod` version is newer than the system Go version (e.g., go.mod says `1.22` but system has `1.21`):
1. Report to user: "go.mod requires Go {go_mod_ver} but system has Go {go_bin_ver}. Upgrade Go or lower the go directive in go.mod."
2. NEVER downgrade the `go` directive in `go.mod` without explicit user approval — it may drop required language features
3. If the system version is newer than go.mod, this is not an error — proceed with the build normally
4. If the build fails with `go.mod requires go >= X.Y` or `module requires Go X.Y`, this confirms the version mismatch is the root cause — do NOT attempt code-level fixes

## Module Troubleshooting

Run these commands in sequence when module errors persist after `go mod tidy`:

```bash
# Step 1: Inspect replace directives
grep "replace" go.mod

# Step 2: Explain why a module is needed
go mod why -m <package>

# Step 3: Pin a specific version
go get <package>@<version>

# Step 4: Only with user confirmation — clear and re-download module cache
go clean -modcache && go mod download
```

## Stop Conditions (Go-Specific)

Stop and report immediately if ANY of these are true:
- The same error recurs after **3 fix attempts** on the same file and line
- A fix attempt introduces **more errors** than it resolves
- The fix requires changing **more than 10 lines**
- The error requires changes to files **outside the Go module root**
- The error is a CGo toolchain/compiler installation issue
- The error is from `go generate` tooling
- The error is a Go version mismatch (`go.mod` requires a newer Go than the system provides)
- The error is a private module authentication failure (401/403/410)
