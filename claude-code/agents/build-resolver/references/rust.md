# Rust Build Error Resolution

## Diagnostic Commands

```bash
# Step 1: Check Cargo.toml exists
ls Cargo.toml || echo "MISSING_CARGO_TOML"

# Step 2: Build
cargo build 2>&1

# Step 3: Check (includes additional warnings)
cargo check 2>&1
```

## Common Error Patterns

| Error Pattern | Exact Fix |
|---------------|-----------|
| `cannot find value/type 'X' in this scope` | Add `use` statement or fix the path |
| `mismatched types` | Add `.into()`, explicit cast, or fix the type annotation |
| `borrow of moved value` | Add `.clone()`, change to reference `&`, or restructure ownership |
| `unused variable` | Prefix with `_` (e.g., `_unused`) |

## Framework-Specific Issues

### Toolchain Mismatch

If error contains `feature is not stable`:
1. Check `rust-toolchain.toml` or `rust-toolchain` for the required channel
2. Report: "Project requires Rust {channel}, switch with `rustup override set {channel}`"
3. Do NOT attempt code fixes for toolchain version errors

### Clippy Warnings Blocking Build

If `cargo build` is configured to treat warnings as errors (`RUSTFLAGS="-D warnings"`):
1. Run `cargo clippy 2>&1` to get the full list of warnings
2. Fix each warning at the exact reported location
3. Common clippy fixes: use `_` prefix for unused vars, add `#[allow(dead_code)]` only when explicitly approved by user

### Cargo.lock Integrity

If error mentions lock file issues:
1. Ask user for confirmation before regenerating
2. If confirmed: `cargo update` to regenerate `Cargo.lock`
3. For specific package version pin: `cargo update -p <package> --precise <version>`
