# Rust Review Checklist

Detailed review rules for Rust code. Loaded by code-reviewer when diff contains `.rs` files, `Cargo.toml`, or `Cargo.lock`.

## File Classification

| Category | Detection Rule | Action |
|---|---|---|
| **generated** | Header contains `// @generated`, `// DO NOT EDIT`, `// AUTO-GENERATED`; path matches `*_generated.rs`, inside `target/` dir | Skip. Log: `[SKIP] {filepath}: generated ({matched rule}).` |
| **test** | `#[cfg(test)]` module, files in `tests/` directory, `_test.rs` suffix | Apply test-specific rules (see below) |
| **build script** | `build.rs` | Review for security (command execution, path manipulation). Skip style rules. |
| **proc macro** | Crate type `proc-macro` in `Cargo.toml` | Flag for extra scrutiny — proc macros execute at compile time. |
| **third-party** | Path inside `vendor/` | Skip. Log: `[SKIP] {filepath}: vendored.` |

## Static Analysis Commands

```bash
cargo clippy --all-targets --all-features -- -D warnings 2>&1
cargo check 2>&1
```

If clippy unavailable: `[LIMITATION] clippy unavailable. Linting is manual-only.`

## Review Rules

### CRITICAL — Unsafe Code

| ID | Rule | Detail |
|---|---|---|
| RS-UNSAFE-1 | Every `unsafe` block must have a `// SAFETY:` comment | Comment must explain why the invariants are upheld. No `unsafe` without justification. |
| RS-UNSAFE-2 | No raw pointer dereference without bounds verification | `*ptr` inside `unsafe` must be preceded by null check and bounds validation |
| RS-UNSAFE-3 | No `unsafe impl Send/Sync` without proof | Must document why the type is safe to send/share across threads |
| RS-UNSAFE-4 | Minimize unsafe scope | `unsafe` block must contain only the unsafe operation itself, not surrounding safe code |
| RS-UNSAFE-5 | No `unsafe` to bypass borrow checker | If `unsafe` is used to work around a borrow checker error, the design is wrong. Refactor instead. |

### CRITICAL — Security

| ID | Rule | Detail |
|---|---|---|
| RS-SEC-1 | No `std::process::Command` with unsanitized input | User input in command args must be validated against an allowlist |
| RS-SEC-2 | No hardcoded secrets | String literals matching API key patterns, passwords, tokens |
| RS-SEC-3 | No `std::mem::transmute` between unrelated types | `transmute` between types of different sizes or unrelated layouts is instant UB |
| RS-SEC-4 | SQL injection via string formatting | `format!()` in SQL query strings. Use parameterized queries. |

### HIGH — Error Handling

| ID | Rule | Detail |
|---|---|---|
| RS-ERR-1 | No `.unwrap()` in library/production code | Use `?`, `.expect("reason")`, or explicit match. `.unwrap()` allowed in tests and examples only. |
| RS-ERR-2 | `.expect()` must have descriptive message | `expect("")` or single-word messages forbidden. Describe what invariant was violated. |
| RS-ERR-3 | Error types must implement `std::error::Error` | Custom error enums/structs must `impl Error`. Recommend `thiserror` for library, `anyhow` for application. |
| RS-ERR-4 | No panic in library code | `panic!()`, `todo!()`, `unimplemented!()` in library crate paths forbidden. Use `Result` return. |
| RS-ERR-5 | Error context on propagation | Bare `?` without `.context()` or `.map_err()` loses information. Add context at module boundaries. |

### HIGH — Ownership and Borrowing

| ID | Rule | Detail |
|---|---|---|
| RS-OWN-1 | No unnecessary `.clone()` | `.clone()` on `&T` where the borrow could be extended. Each `.clone()` must be justified by ownership requirement. |
| RS-OWN-2 | Prefer `&str` over `&String` in function params | `fn foo(s: &String)` → `fn foo(s: &str)`. Similarly `&Vec<T>` → `&[T]`, `&Box<T>` → `&T`. |
| RS-OWN-3 | No `Rc<RefCell<T>>` without justification | Indicates shared mutable state. Prefer restructuring to avoid. If required, add comment explaining why. |
| RS-OWN-4 | Lifetime elision where possible | Explicit lifetimes that match elision rules are redundant noise |

### HIGH — Concurrency

| ID | Rule | Detail |
|---|---|---|
| RS-CONC-1 | `Arc<Mutex<T>>` — verify no deadlock | Multiple `Arc<Mutex<>>` locked in different orders across functions. Document lock ordering. |
| RS-CONC-2 | No `std::sync::Mutex` in async code | Use `tokio::sync::Mutex` or `parking_lot::Mutex` in async contexts. `std::sync::Mutex` blocks the executor thread. |
| RS-CONC-3 | `MutexGuard` must not be held across `.await` | Holding `MutexGuard` across `.await` can cause deadlocks in single-threaded runtimes |
| RS-CONC-4 | Spawned tasks must be joined or explicitly detached | `tokio::spawn()` result must be stored and `.await`ed, or explicitly documented as fire-and-forget |

### HIGH — Async Code

Apply only to files using `async fn`, `.await`, `tokio::`, `async-std::`.

| ID | Rule | Detail |
|---|---|---|
| RS-ASYNC-1 | No blocking calls in async functions | `std::thread::sleep()`, `std::fs::*`, `std::net::*` inside `async fn` forbidden. Use `tokio::time::sleep()`, `tokio::fs::*`, `tokio::net::*`. |
| RS-ASYNC-2 | `Send` bound on spawned futures | Futures passed to `tokio::spawn()` must be `Send`. Non-Send types across `.await` prevent this. |
| RS-ASYNC-3 | No `block_on` inside async context | `Runtime::block_on()` inside already-async code causes panic or deadlock |

### MEDIUM — Code Quality

| ID | Rule | Threshold/Detail |
|---|---|---|
| RS-QUAL-1 | Function body too long | > 60 non-blank, non-comment lines |
| RS-QUAL-2 | Too many parameters | > 5 parameters. Suggest builder pattern or config struct. |
| RS-QUAL-3 | Nesting too deep | > 4 levels of indentation |
| RS-QUAL-4 | Missing `#[must_use]` on pure functions | Functions that return a value with no side effects should have `#[must_use]` |
| RS-QUAL-5 | `as` cast for numeric conversion | `x as u32` can silently truncate. Use `x.try_into().unwrap()` or `u32::try_from(x)?`. Exception: known-safe casts with comment. |
| RS-QUAL-6 | Unused `Result` | `Result` returned by function call not bound or propagated |
| RS-QUAL-7 | `pub` visibility too broad | `pub` on struct fields or functions that are only used within the crate. Use `pub(crate)` or `pub(super)`. |

### MEDIUM — Cargo / Dependencies

| ID | Rule | Detail |
|---|---|---|
| RS-CARGO-1 | New dependency added | Flag for justification. Check: is it maintained? Does it add `unsafe`? |
| RS-CARGO-2 | Wildcard dependency version | `foo = "*"` or `foo = ">=1"` forbidden. Use exact minor range: `foo = "1.2"`. |
| RS-CARGO-3 | Feature flags | New feature flags must be documented in `Cargo.toml` `[features]` section |
| RS-CARGO-4 | `Cargo.lock` for binaries | Binary crates must commit `Cargo.lock`. Library crates must not. |

### LOW — Informational

| ID | Rule | Detail |
|---|---|---|
| RS-DOC-1 | Missing doc comment on public API | `pub fn`, `pub struct`, `pub enum`, `pub trait` without `///` doc comment |
| RS-QUAL-8 | Magic number | Numeric literal other than 0, 1 without named constant. Exception: test code. |
| RS-QUAL-9 | `TODO`/`FIXME` without ticket | Inline comment without linked issue identifier |

## Test File Rules

Tests = `#[cfg(test)]` modules, `tests/` directory files, `#[test]` functions.

**Rules that apply**: All CRITICAL (unsafe, security), concurrency rules, error types.

**Rules that do NOT apply**: RS-DOC-1, RS-QUAL-8, RS-ERR-1 (`.unwrap()` allowed in tests), RS-QUAL-1 (flag only if >150 lines).

**Additional test checks**:

| ID | Check | Severity |
|---|---|---|
| RS-TEST-1 | 3+ similar test functions without parameterized test macro (`rstest`, `test-case`) | MEDIUM |
| RS-TEST-2 | `#[should_panic]` without `expected` message | MEDIUM |
| RS-TEST-3 | Async test without `#[tokio::test]` or equivalent runtime attribute | HIGH |
