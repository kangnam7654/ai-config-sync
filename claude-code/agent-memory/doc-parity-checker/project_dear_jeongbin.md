---
name: Dear Jeongbin Project Conventions
description: Tauri+Rust backend (src-tauri/src/) + Next.js frontend (src/) project. Common mismatch patterns between design docs and actual code.
type: project
---

# Dear Jeongbin Project Notes

**Stack**: Tauri 2 + Axum (Rust backend at src-tauri/src/) + Next.js 16 frontend (src/)

**Why**: Personal AI career coaching app for girlfriend. Not commercial.

## Path Conventions

- Rust source: `src-tauri/src/` (glob results show relative `src/` when run from src-tauri/)
- Frontend: `src/` at project root
- DB path: `~/.dear-jeongbin/data.db`
- venv path: `~/.dear-jeongbin/export-venv/`
- Port: **35470** (range 35470-35479, dynamic) — NOT 3100 as stated in early design docs

## Common Mismatch Patterns

1. **Design docs describe planned state, not final**: Many docs (portfolio-features.md, export-pptxgenjs.md) describe intermediate plans that were superseded by later docs.
2. **Function parameter names drift**: Design docs specify `template_id` but code uses `layout_id`; `mime_type` param dropped from `extract_text`.
3. **Struct fields differ**: `PptxTheme` has `primary_mid` field not in docs, lacks `font_en`; `TemplateSeed` lacks `palette` field.
4. **Const names differ**: Doc says `PRESET_IDS: &[&str]` but actual is `PRESETS: &[PresetInfo]`; no `preset_info()` function.
5. **Async vs sync**: `seed_default_templates` is sync (`pub fn`), not `async fn` as doc claims.
6. **AppState signature**: Doc says `new(db_path: &Path)` + `conn()` method; actual is `new(db: DbPool)` no `conn()`.
7. **Binary name**: `cargo run --bin server` does not work; correct is `cargo run` (binary named `dear-jeongbin`).
8. **db/migrations.rs**: Planned but never created; only `db/mod.rs` and `db/schema.rs` exist.
9. **portfolios/[id]/page.tsx**: Planned but never created; only `portfolios/result/page.tsx` exists.
10. **export-panel.tsx location**: `src/components/features/resumes/export-panel.tsx`, not `export/export-panel.tsx`.

## Cargo.toml Discrepancies vs Design Doc

- `rusqlite`: actual `0.32`, doc says `0.33`
- `quick-xml`: actual `0.38`, doc says `0.37`
- `tauri features`: actual `[]`, doc says `["shell-open"]`
- `axum-extra`: not present (doc says it would be added)
- `docx-rs`, `comrak`: not present (portfolio-features.md planned them but they were abandoned)
