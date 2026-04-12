# Migration Safety Reference

## UP / DOWN Verification

- Every migration MUST have both UP and DOWN sections
- DOWN migration must be safe: no irreversible data loss on rollback
- Verify DOWN migration logic is correct by tracing it against the UP migration
- If DOWN migration would cause data loss (e.g., dropping a populated column), document this explicitly and require explicit user confirmation before applying

## NOT NULL + DEFAULT Rule

- NEVER add a `NOT NULL` column to a populated table without a `DEFAULT` value
  - In PostgreSQL < 11: rewrites the entire table, causing a full table lock
  - In PostgreSQL >= 11: instant for stable defaults (literals), still locks for volatile defaults (`now()`, `gen_random_uuid()`)
- Safe pattern for adding NOT NULL column to large table:
  1. `ALTER TABLE t ADD COLUMN col text;` (nullable, no lock)
  2. `UPDATE t SET col = 'default_value' WHERE col IS NULL;` (batched backfill)
  3. `ALTER TABLE t ALTER COLUMN col SET NOT NULL;` (fast CHECK constraint validation)

## Destructive Operation Checks

- Destructive operations requiring extra scrutiny: `DROP COLUMN`, `DROP TABLE`, `TRUNCATE`, `DELETE` without WHERE
- For each destructive operation, verify:
  1. Is there a rollback path? (Can deleted data be recovered from backup?)
  2. Is the operation idempotent? (Can it be safely re-run?)
  3. Is there a dependent object that will break? (Views, FK references, application code)
- Flag all destructive ops as P0 CRITICAL on applied migrations

## Lock Duration Estimation

- Estimate lock duration for any DDL on tables > 1M rows
- Operations that lock the entire table:
  - `ALTER TABLE ... ADD COLUMN ... NOT NULL DEFAULT volatile_value`
  - `ALTER TABLE ... ALTER COLUMN TYPE ...` (full rewrite)
  - Adding a `CHECK` constraint without `NOT VALID`
- Lock-safe alternatives:
  - `ALTER TABLE ... ADD CONSTRAINT ... NOT VALID` then `VALIDATE CONSTRAINT` separately
  - `CREATE INDEX CONCURRENTLY` instead of `CREATE INDEX`
  - For type changes: add new column, backfill, swap at application level, drop old column

## Data Backfill Separation

- Data backfill migrations MUST be separated from schema migrations
- Schema migration: adds/removes columns/tables/constraints
- Data migration: fills/transforms existing data
- Running them together increases lock duration and rollback complexity
- Backfill in batches of 1,000-10,000 rows: `WHERE id BETWEEN $batch_start AND $batch_end`

## Non-Blocking Patterns

```sql
-- Adding index without blocking writes
CREATE INDEX CONCURRENTLY idx_users_email ON users (email);

-- Adding NOT NULL column safely (3-step)
ALTER TABLE orders ADD COLUMN status text;
UPDATE orders SET status = 'pending' WHERE status IS NULL;
ALTER TABLE orders ALTER COLUMN status SET NOT NULL;

-- Adding constraint without full-table lock
ALTER TABLE orders ADD CONSTRAINT chk_amount_positive CHECK (amount > 0) NOT VALID;
ALTER TABLE orders VALIDATE CONSTRAINT chk_amount_positive;
```

## Checklist (P0 if violated for applied migrations)

- [ ] Rollback/down migration exists and is safe (no irreversible data loss)
- [ ] `ALTER TABLE` on large tables uses non-blocking patterns where possible (`CREATE INDEX CONCURRENTLY`, adding columns without volatile defaults)
- [ ] Lock duration estimated for tables > 1M rows
- [ ] Data backfill migrations separated from schema migrations
- [ ] Destructive operations (DROP, TRUNCATE, DELETE) are documented and reversible
