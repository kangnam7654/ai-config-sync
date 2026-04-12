# Anti-Patterns Reference

All 15 anti-patterns to flag during database review. Copy severity assignments verbatim when reporting findings.

## Anti-Patterns Table

| Anti-Pattern | Severity | Correct Pattern |
|---|---|---|
| `SELECT *` in application code | P3 | Explicit column list |
| `int` for IDs | P2 | `bigint` or UUIDv7 |
| `varchar(255)` without documented max | P2 | `text` |
| `timestamp` without timezone | P2 | `timestamptz` |
| Random UUIDv4 as primary key | P2 | UUIDv7 (time-sorted) or `bigint GENERATED ALWAYS AS IDENTITY` |
| `OFFSET` pagination on large tables | P1 | Cursor pagination |
| Unparameterized queries | P0 | Parameterized queries (`$1`, `$2`) |
| `GRANT ALL` to application users | P0 | Least privilege: specific `GRANT SELECT, INSERT, UPDATE` on needed tables |
| `ALTER TABLE ... ADD COLUMN ... DEFAULT` on large table (PG < 11) | P1 | Add column without default, then backfill in batches |
| Missing `ON DELETE` on FK | P2 | Explicit `ON DELETE CASCADE / SET NULL / RESTRICT` |
| `float`/`real` for monetary values | P2 | `numeric(precision, scale)` |
| Missing FK index | P1 | Create index on FK column alongside FK constraint |
| N+1 query pattern | P1 | JOIN or batch fetch (IN clause, eager loading) |
| `NOT NULL` column added without `DEFAULT` to populated table | P0 | Add nullable first, backfill, then add constraint |
| Missing RLS on multi-tenant table | P0 | Enable RLS with `(SELECT auth.uid())` policy |

## Severity Definitions

| Severity | Label | Criteria |
|---|---|---|
| P0 | CRITICAL | Data loss risk, security vulnerability (SQL injection, missing RLS on multi-tenant table), migration without rollback on production table |
| P1 | HIGH | Performance: query > 100ms (OLTP) or > 5s (analytics batch). Missing index on FK or frequently-filtered column. Locking risk on large tables |
| P2 | MEDIUM | Schema: violation of 3NF without documented justification. Suboptimal data type. Missing `NOT NULL` where semantically required |
| P3 | LOW | Style: naming convention violation (`camelCase` instead of `snake_case`). Missing but non-critical index. `SELECT *` in non-production code |

## Thresholds (Hard Numbers)

- **Slow query (OLTP)**: execution time > 100ms or estimated cost > 10,000
- **Slow query (analytics/batch)**: execution time > 5s or estimated cost > 500,000
- **Large table (lock-sensitive)**: > 1M rows or > 1GB total relation size
- **Normalization standard**: 3NF minimum. Flag all undocumented denormalization as P2 MEDIUM
