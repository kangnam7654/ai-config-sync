# C++ Review Checklist

Detailed review rules for C++ code. Loaded by code-reviewer when diff contains `.cpp`, `.cc`, `.cxx`, `.c`, `.h`, `.hpp`, `.hxx` files.

## File Classification

| Category | Detection Rule | Action |
|---|---|---|
| **generated** | Header contains `// Generated`, `// DO NOT EDIT`, `// AUTO-GENERATED`; path matches `*_generated.*`, `*.pb.h`, `*.pb.cc`, `*_moc.cpp`, `ui_*.h` | Skip. Log: `[SKIP] {filepath}: generated ({matched rule}).` |
| **test** | Path contains `test/`, `tests/`, `_test.cpp`, `_test.cc`, `_unittest.cpp`, filename starts with `test_` | Apply test-specific rules (see below) |
| **header** | `.h`, `.hpp`, `.hxx` | Apply header-specific rules (include guards, forward declarations) |
| **third-party** | Path contains `third_party/`, `external/`, `vendor/` | Skip. Log: `[SKIP] {filepath}: third-party.` |

## Static Analysis Commands

```bash
# clang-tidy (if .clang-tidy config exists)
clang-tidy --quiet <files> 2>&1 || true

# cppcheck
cppcheck --enable=warning,style,performance --quiet <files> 2>&1 || true
```

If both unavailable: `[LIMITATION] No static analysis tools available. Manual-only review.`

## Review Rules

### CRITICAL — Memory Safety

| ID | Rule | Detail |
|---|---|---|
| CPP-MEM-1 | No raw `new` without matching `delete` in non-RAII context | Use `std::unique_ptr` or `std::shared_ptr`. Raw `new` allowed only inside custom allocator or placement new with documented lifetime. |
| CPP-MEM-2 | No use-after-free patterns | Returning reference/pointer to local variable, accessing freed memory, iterator invalidation after container modification |
| CPP-MEM-3 | No double-free patterns | Same pointer passed to `delete`/`free` via multiple code paths |
| CPP-MEM-4 | No buffer overflow | Array index from external input without bounds check, `strcpy`/`sprintf` instead of `strncpy`/`snprintf`, `memcpy` with unchecked size |
| CPP-MEM-5 | No dangling pointer/reference | Reference to temporary, pointer to stack-allocated object escaping scope, reference to moved-from object |
| CPP-MEM-6 | No uninitialized variable reads | All variables must be initialized before first read. Flag `int x; if (cond) x = 1; use(x);` patterns. |

### CRITICAL — Security

| ID | Rule | Detail |
|---|---|---|
| CPP-SEC-1 | No format string vulnerabilities | `printf(user_input)` forbidden. Use `printf("%s", user_input)`. Applies to all `*printf` family. |
| CPP-SEC-2 | No integer overflow in security-critical paths | Arithmetic on sizes, lengths, offsets from external input must use overflow-safe operations or explicit bounds checks |
| CPP-SEC-3 | No command injection | `system()`, `popen()` with unsanitized input forbidden. Use `execve()` family with argument array. |
| CPP-SEC-4 | No hardcoded secrets | String literals matching API key patterns, passwords, tokens |

### CRITICAL — Undefined Behavior

| ID | Rule | Detail |
|---|---|---|
| CPP-UB-1 | No signed integer overflow reliance | Signed overflow is UB. Use unsigned or explicit saturation/wrapping. |
| CPP-UB-2 | No null pointer dereference | Pointer from external source must be null-checked before dereference |
| CPP-UB-3 | No out-of-bounds access | Container access with `[]` on index from external input. Use `.at()` or explicit bounds check. |
| CPP-UB-4 | No data race | Shared mutable state across threads without `std::mutex`, `std::atomic`, or other synchronization |

### HIGH — Resource Management

| ID | Rule | Detail |
|---|---|---|
| CPP-RAII-1 | Use RAII for all resources | File handles, sockets, locks, memory must be managed by RAII wrappers. No manual `close()`/`unlock()`/`free()` in normal code paths. |
| CPP-RAII-2 | Rule of Five compliance | If a class defines any of destructor, copy constructor, copy assignment, move constructor, move assignment — it must define or `= delete` all five. |
| CPP-RAII-3 | No resource leak in exception paths | Resources acquired before a throwing call must be RAII-managed. `try/catch` with manual cleanup is insufficient (cleanup may throw). |
| CPP-RAII-4 | `std::lock_guard` or `std::unique_lock` for mutex | No manual `lock()`/`unlock()` pairs |

### HIGH — Modern C++ Idioms (C++17 minimum)

| ID | Rule | Bad | Good |
|---|---|---|---|
| CPP-MOD-1 | Smart pointers over raw pointers for ownership | `Widget* w = new Widget();` | `auto w = std::make_unique<Widget>();` |
| CPP-MOD-2 | `std::string_view` for non-owning string params | `const std::string&` for read-only param that doesn't store | `std::string_view` |
| CPP-MOD-3 | Range-based for over index-based | `for (int i = 0; i < v.size(); i++)` when index unused | `for (const auto& item : v)` |
| CPP-MOD-4 | `auto` for complex types from factory/iterator | `std::map<std::string, std::vector<int>>::iterator it = m.begin()` | `auto it = m.begin()` |
| CPP-MOD-5 | `constexpr` over `#define` for constants | `#define MAX_SIZE 100` | `constexpr int kMaxSize = 100;` |
| CPP-MOD-6 | `std::optional` over sentinel values | `return -1;` for "not found" | `return std::nullopt;` |
| CPP-MOD-7 | Structured bindings for pair/tuple | `auto p = map.find(k); if (p != map.end()) p->second` | `auto [it, found] = map.find(k)` or `if (auto [k, v] = *it; ...)` |

### HIGH — Concurrency

| ID | Rule | Detail |
|---|---|---|
| CPP-CONC-1 | No detached threads without lifetime management | `std::thread(...).detach()` must ensure all captured references outlive the thread |
| CPP-CONC-2 | `std::atomic` for lock-free shared state | Non-atomic read/write of shared variable across threads is a data race (UB) |
| CPP-CONC-3 | No recursive mutex unless documented | `std::recursive_mutex` indicates design issue. Requires comment justifying why. |
| CPP-CONC-4 | Condition variable with predicate | `cv.wait(lock)` without predicate is spurious-wakeup-vulnerable. Use `cv.wait(lock, pred)`. |

### MEDIUM — Code Quality

| ID | Rule | Threshold |
|---|---|---|
| CPP-QUAL-1 | Function body too long | > 60 non-blank, non-comment lines |
| CPP-QUAL-2 | Too many parameters | > 5 parameters. Suggest struct or builder pattern. |
| CPP-QUAL-3 | Nesting too deep | > 4 levels of indentation |
| CPP-QUAL-4 | Implicit narrowing conversion | `int x = long_value;` without explicit `static_cast`. Flag when target type is smaller. |
| CPP-QUAL-5 | C-style cast | `(int)x` instead of `static_cast<int>(x)`, `reinterpret_cast`, or `const_cast` |
| CPP-QUAL-6 | Missing `override` keyword | Virtual function override without `override` specifier |
| CPP-QUAL-7 | `using namespace` in header | `using namespace std;` in `.h`/`.hpp` files pollutes includer's namespace |

### MEDIUM — Headers

| ID | Rule | Detail |
|---|---|---|
| CPP-HDR-1 | Include guard or `#pragma once` | Every header must have one. Prefer `#pragma once` for new code. |
| CPP-HDR-2 | Forward-declare where possible | Prefer forward declaration over `#include` in headers when only pointer/reference is used |
| CPP-HDR-3 | No definitions in headers (except templates/inline) | Non-template, non-inline function definitions in headers cause ODR violations |

### LOW — Informational

| ID | Rule | Detail |
|---|---|---|
| CPP-DOC-1 | Missing Doxygen on public API | Public class, function, enum without `///` or `/** */` comment |
| CPP-QUAL-8 | Magic number | Numeric literal other than 0, 1, -1 without named constant. Exception: test files. |
| CPP-QUAL-9 | `TODO`/`FIXME` without ticket | Inline comment without linked issue identifier |

## Test File Rules

**Rules that apply**: All CRITICAL, RAII rules, concurrency rules.

**Rules that do NOT apply**: CPP-DOC-1, CPP-QUAL-8, CPP-QUAL-1 (flag only if >150 lines).

**Additional test checks**:

| ID | Check | Severity |
|---|---|---|
| CPP-TEST-1 | Test fixtures without `SetUp`/`TearDown` leaking resources | HIGH |
| CPP-TEST-2 | `ASSERT_*` vs `EXPECT_*` usage (ASSERT aborts, EXPECT continues) — use ASSERT for preconditions | MEDIUM |
| CPP-TEST-3 | Parameterized tests: 3+ similar test functions without `TEST_P` or `TYPED_TEST` | MEDIUM |
