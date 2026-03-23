# TDD Patterns — Unit & Integration Tests

This reference file contains the complete TDD workflow, test type definitions, assertion patterns, and edge case handling. Read this file when qa-engineer enters TDD mode.

## TDD Cycle: RED → GREEN → REFACTOR

Each behavior increment follows this exact sequence. Do not skip or reorder steps.

### Step 1: RED — Write a Failing Test

1. Create or open the test file (e.g., `tests/test_<module>.py`)
2. Write exactly **one** test function for the next smallest behavior increment
3. Include at least 1 meaningful assertion (see Meaningful Assertion below)
4. Run the test suite and confirm the test **fails**

If the test passes immediately: stop and investigate. The test is wrong or the behavior already exists. Do not proceed to Step 2 until you see a failure.

**Output**: The failing test code and the exact failure message from the test runner.

### Step 2: GREEN — Write Minimal Implementation

1. Write the **minimum** production code required to make the failing test pass
2. Do not add extra logic, handle other edge cases, or anticipate future needs
3. Run the test suite and confirm the test **passes**

If the test still fails: fix the implementation (not the test) until it passes.

**Output**: The implementation code and confirmation that all tests pass.

### Step 3: REFACTOR — Improve Code Quality

1. Look for duplication, unclear names, or overly complex logic in both production and test code
2. Refactor while keeping all tests green
3. Run the full test suite after each refactor change
4. If any test fails after refactoring: undo the refactor and try a smaller change

**Output**: Description of what was refactored and confirmation that all tests still pass.

### Step 4: Repeat

Go back to Step 1 for the next behavior increment. Continue until the feature is complete.

### Step 5: Coverage Check

After feature completion:
```bash
uv run python -m pytest --cov --cov-fail-under=80
```

If coverage is below 80%: identify untested paths and add tests using the RED-GREEN-REFACTOR cycle.

**Output**: Coverage percentage and list of any uncovered paths.

## Meaningful Assertion (Definition)

A meaningful assertion verifies a **specific expected value or state**, not the absence of an error.

**Meaningful (use these patterns):**
```python
assert add(2, 3) == 5                          # Specific return value
assert user.name == "alice"                     # Specific attribute value
assert result == []                             # Specific empty state
with pytest.raises(ZeroDivisionError):          # Specific exception type
    divide(1, 0)
```

**Not meaningful (never use these alone):**
```python
add(2, 3)                                       # No assertion
assert user                                     # Only truthiness check
try:
    process(data)
except Exception:
    pytest.fail()                               # Only checks "no error"
```

## Test Types

### Unit Tests

- **Purpose**: Test a single function or method in isolation
- **Mocking rule**: Mock ALL external dependencies (network, DB, filesystem, third-party APIs)
- **Speed target**: Each unit test completes in < 100ms
- **File location**: `tests/unit/test_<module>.py` or `tests/test_<module>.py`

### Integration Tests

- **Purpose**: Test interaction between 2+ internal modules, or a module against a real external system
- **Mocking rule**: Mock only external I/O (third-party APIs, cloud services). Internal module calls must remain real.
- **Speed target**: Each integration test completes in < 5s
- **File location**: `tests/integration/test_<feature>.py`

## Edge Cases to Test

Every feature must include tests for these categories. Before declaring a feature complete, verify that at least categories 1-5 have dedicated test functions:

1. **None/null input** — function receives `None` where a value is expected
2. **Empty collections** — empty list, empty string, empty dict
3. **Invalid types** — string where int is expected, wrong object type
4. **Boundary values** — 0, -1, MAX_INT, empty string vs single char
5. **Error paths** — network timeout, file not found, permission denied
6. **Special characters** — Unicode, emojis, SQL injection strings, path traversal strings
7. **Large input** — 10k+ items for performance-sensitive code

**Compliance check**: After writing all tests, scan the test file for coverage of categories 1-5. If any category has zero test functions, add at least one test for that category before reporting completion.

## Legacy Code Handling

### Code without existing tests

1. Write **characterization tests** that capture current behavior, even if it seems wrong:
   ```python
   def test_legacy_calculate_tax_current_behavior():
       result = calculate_tax(100, region="CA")
       assert result == 8.25  # Captured from actual execution
   ```
2. Achieve >= 80% coverage on the module before any refactoring
3. Only after characterization tests are in place, proceed with standard TDD

### Untestable code (tightly coupled, global state)

1. Refactor for testability first: extract dependencies into parameters, replace global state with explicit arguments
2. Each refactoring step must be covered by a characterization test before the change and a unit test after
3. Only after the code is testable, proceed with normal TDD

## Slow Test Suite Handling

If total test runtime exceeds 30 seconds:

1. **Diagnose**: `uv run python -m pytest tests/ --durations=10`
2. **Parallelize**: `uv run python -m pytest tests/ -q -n auto`
3. **Split**: `tests/unit/` (target < 10s) vs `tests/integration/` (target < 60s)

## Anti-Patterns to Avoid

- Testing implementation details instead of behavior (assert outputs, not internal method calls)
- Shared mutable state between tests (each test sets up and tears down its own state)
- Missing assertions (a test without a meaningful assertion is not a test)
- Over-mocking (mocking everything means testing nothing — mock only external boundaries)
- Catch-all exception handling (let unexpected exceptions propagate; only catch expected ones with `pytest.raises`)
- Test names that do not describe behavior (use `test_<action>_<condition>_<expected_result>`)

## Quality Checklist

Before declaring a feature complete:

- [ ] Every public function has >= 1 unit test
- [ ] Every API endpoint has >= 1 integration test
- [ ] Each test function contains >= 1 meaningful assertion
- [ ] Edge cases covered: None, empty, invalid type, boundary values
- [ ] Error paths tested: >= 1 test per documented exception
- [ ] External deps mocked in unit tests
- [ ] Internal calls NOT mocked in integration tests
- [ ] Tests are independent (no execution order dependency)
- [ ] Test names follow `test_<action>_<condition>_<expected_result>`
- [ ] Coverage >= 80%
- [ ] Full suite passes
