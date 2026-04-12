# Query Optimization Reference

## Index Strategy for WHERE / JOIN Columns

- Every column appearing in a WHERE clause on a large table (> 10,000 rows) must have an index
- Every JOIN column must have an index on the joined table's side
- Composite index column order: equality columns first, then range columns, then sort columns
  - Example: `CREATE INDEX ON orders (user_id, status, created_at)` for `WHERE user_id = $1 AND status = $2 ORDER BY created_at`
- FK columns ALWAYS require indexes — missing FK index causes sequential scans on join

## Sequential Scan Detection

- Sequential scans on tables > 10,000 rows without explicit justification → P1 HIGH
- Exception: full table scan is acceptable when > 50% of rows are expected to match
- In EXPLAIN output, look for `Seq Scan` on large tables; `Index Scan` or `Index Only Scan` is preferred
- `Bitmap Index Scan` + `Bitmap Heap Scan` is acceptable for moderate selectivity

## N+1 Query Detection

- Identify N+1 patterns: repeated single-row fetches in loops (e.g., fetching user for each order)
- Fix: JOIN or IN clause to batch fetch, or use ORM eager loading (`include`/`with`)
- Symptom in logs: same query repeated N times with different ID values

## Pagination

- NEVER use `OFFSET` pagination on tables > 10,000 rows
  - `OFFSET N` forces the DB to scan and discard N rows on every page request
  - Performance degrades linearly with page depth
- Use cursor-based pagination: `WHERE id > $last_id ORDER BY id LIMIT N`
- For complex sort orders, encode the sort key as the cursor

## Batch Operations

- NEVER insert rows in a loop — use multi-row `INSERT INTO ... VALUES (...), (...), (...)`
- For bulk loads (> 10,000 rows), use `COPY` command
- Batch UPDATE/DELETE: process in chunks of 1,000-10,000 rows with `WHERE id BETWEEN $start AND $end`

## EXPLAIN Analysis Methodology

1. Always start with `EXPLAIN (FORMAT TEXT)` to get a readable plan
2. On dev/staging, use `EXPLAIN (FORMAT JSON, ANALYZE, BUFFERS)` for actual timing
3. NEVER run `EXPLAIN ANALYZE` on production
4. Key metrics to examine:
   - `Seq Scan` on large tables → needs index
   - `Rows Removed by Filter` >> actual rows → index selectivity issue
   - `actual time` significantly higher than `estimated time` → stale statistics (run `ANALYZE`)
   - High `Buffers: shared read` → cache miss, consider `pg_prewarm` or query restructuring
5. Static analysis when no DB: check WHERE/JOIN columns against schema for index coverage

## Partial Indexes

- `WHERE deleted_at IS NULL` for soft-delete tables — only indexes active rows
- `WHERE status = 'active'` for status-filtered queries — reduces index size
- `WHERE is_processed = false` for queue tables

## Covering Indexes

- `INCLUDE (col1, col2)` to satisfy queries from index alone, avoiding heap fetches
- Use when SELECT columns are not in the WHERE/JOIN clause but are frequently accessed together

## CREATE INDEX CONCURRENTLY

- Always use `CREATE INDEX CONCURRENTLY` for adding indexes to production tables
- Avoids write lock during index build
- Takes longer but does not block application queries

## Checklist (P1 if violated)

- [ ] All WHERE clause columns have appropriate indexes
- [ ] All JOIN columns have appropriate indexes
- [ ] Composite indexes use correct column order: equality columns first, then range, then sort
- [ ] No sequential scans on tables > 10,000 rows without explicit justification
- [ ] No N+1 query patterns (detected via repeated similar queries or ORM lazy loading)
- [ ] Cursor-based pagination used instead of OFFSET on tables > 10,000 rows
- [ ] Batch operations used for bulk inserts (multi-row INSERT or COPY, not loops)
