# Python Build Error Resolution

## Diagnostic Commands

```bash
# Step 1: Check pyproject.toml or setup.py exists
ls pyproject.toml setup.py setup.cfg 2>/dev/null || echo "NO_BUILD_CONFIG"

# Step 2: Type-check (if mypy or pyright is configured)
uv run python -m mypy . 2>&1 || uv run python -m pyright . 2>&1

# Step 3: Build
uv run python -m build 2>&1 || uv run python setup.py build 2>&1
```

## Common Error Patterns

| Error Pattern | Exact Fix |
|---------------|-----------|
| `ModuleNotFoundError` | Add missing dependency: `uv add <package>` |
| `ImportError: cannot import name 'X'` | Fix the import path or check the package version |
| `SyntaxError` | Fix the syntax at the reported line |
| `mypy: Incompatible types` | Add type annotation or cast with `typing.cast()` |

## Framework-Specific Issues

### uv / pip Dependency Resolution

- Always use `uv add <package>` for adding dependencies (never bare `pip install`)
- For version conflicts, inspect `pyproject.toml` and `uv.lock` for constraint clashes
- Run `uv sync` to re-resolve after manual edits to `pyproject.toml`

### Import Errors

If `ModuleNotFoundError` occurs:
1. Check if the package is listed in `pyproject.toml` dependencies
2. If missing: `uv add <package>`
3. If present but still failing: run `uv sync` to ensure environment is up to date
4. If it's a local module import: check `sys.path` and project layout (src layout vs flat layout)

### ruff / mypy Type Errors

- For `mypy: Incompatible return value type`: add explicit return type annotation
- For `mypy: Argument 1 to "X" has incompatible type`: use `typing.cast()` or fix the source type
- For `ruff` lint errors blocking build: fix the reported issue at the exact line (ruff errors are precise)
