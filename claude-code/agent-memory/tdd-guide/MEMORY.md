# TDD Agent Memory

## Node.js / Vitest Patterns

- See `vitest-patterns.md` for detailed vitest setup and mocking notes.

## Key Rules

- Always scope coverage `include` to the files under test — not the whole `src/`.
- Use `npx vitest run` for Node.js projects (never `uv run`).
- Python: always use `uv run python -m pytest`.
