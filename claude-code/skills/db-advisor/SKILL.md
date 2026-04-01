---
name: db-advisor
description: PostgreSQL database patterns for query optimization, schema design, indexing, and security. Based on Supabase best practices.
origin: ECC
---

# PostgreSQL Patterns

Quick reference for PostgreSQL best practices. For detailed guidance, use the `database-reviewer` agent.

## Out of Scope

This skill covers **PostgreSQL only**. Do NOT use for:
- **MySQL/MariaDB** — syntax and optimization strategies differ significantly
- **SQLite** — lacks many PostgreSQL features (CTEs with DML, advanced indexing, RLS)
- **MongoDB** — document database, entirely different paradigm
- **Oracle DB** — proprietary syntax and optimizer behavior
- **SQL Server** — different execution engine and indexing model

If the user's database is not PostgreSQL, flag it explicitly and suggest they seek database-specific guidance.

## When to Activate

- Writing SQL queries or migrations
- Designing database schemas
- Troubleshooting slow queries
- Implementing Row Level Security
- Setting up connection pooling

## Workflow

1. **Detect context**: Identify the database operation from the user's query (schema design, query optimization, indexing, RLS, configuration)
2. **Match to pattern**: Find the relevant section below (Index Cheat Sheet, Common Patterns, Anti-Pattern Detection, Configuration)
3. **Provide GOOD/BAD example**: Always show the recommended pattern AND the anti-pattern to avoid, with explanation of why
4. **Add caveats**: Note version requirements, table size considerations, and trade-offs specific to their use case

## Quick Reference

### Index Cheat Sheet

| Query Pattern | Index Type | Example |
|--------------|------------|---------|
| `WHERE col = value` | B-tree (default) | `CREATE INDEX idx ON t (col)` |
| `WHERE col > value` | B-tree | `CREATE INDEX idx ON t (col)` |
| `WHERE a = x AND b > y` | Composite | `CREATE INDEX idx ON t (a, b)` |
| `WHERE jsonb @> '{}'` | GIN | `CREATE INDEX idx ON t USING gin (col)` |
| `WHERE tsv @@ query` | GIN | `CREATE INDEX idx ON t USING gin (col)` |
| Time-series ranges | BRIN | `CREATE INDEX idx ON t USING brin (col)` |

### Data Type Quick Reference

| Use Case | Correct Type | Avoid |
|----------|-------------|-------|
| IDs | `bigint` | `int`, random UUID |
| Strings | `text` | `varchar(255)` |
| Timestamps | `timestamptz` | `timestamp` |
| Money | `numeric(10,2)` | `float` |
| Flags | `boolean` | `varchar`, `int` |

### Common Patterns

**Composite Index Order:**
```sql
-- Equality columns first, then range columns
CREATE INDEX idx ON orders (status, created_at);
-- Works for: WHERE status = 'pending' AND created_at > '2024-01-01'
```

**Covering Index:**
```sql
CREATE INDEX idx ON users (email) INCLUDE (name, created_at);
-- Avoids table lookup for SELECT email, name, created_at
```

**Partial Index:**
```sql
CREATE INDEX idx ON users (email) WHERE deleted_at IS NULL;
-- Smaller index, only includes active users
```

**RLS Policy (Optimized):**
```sql
CREATE POLICY policy ON orders
  USING ((SELECT auth.uid()) = user_id);  -- Wrap in SELECT!
```

**UPSERT:**
```sql
INSERT INTO settings (user_id, key, value)
VALUES (123, 'theme', 'dark')
ON CONFLICT (user_id, key)
DO UPDATE SET value = EXCLUDED.value;
```

**Cursor Pagination:**
```sql
SELECT * FROM products WHERE id > $last_id ORDER BY id LIMIT 20;
-- O(1) vs OFFSET which is O(n)
```

**Queue Processing:**
```sql
UPDATE jobs SET status = 'processing'
WHERE id = (
  SELECT id FROM jobs WHERE status = 'pending'
  ORDER BY created_at LIMIT 1
  FOR UPDATE SKIP LOCKED
) RETURNING *;
```

### Anti-Pattern Detection

```sql
-- Find unindexed foreign keys
SELECT conrelid::regclass, a.attname
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
WHERE c.contype = 'f'
  AND NOT EXISTS (
    SELECT 1 FROM pg_index i
    WHERE i.indrelid = c.conrelid AND a.attnum = ANY(i.indkey)
  );

-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC;

-- Check table bloat
SELECT relname, n_dead_tup, last_vacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

### Configuration Template

```sql
-- Connection limits (adjust for RAM)
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET work_mem = '8MB';

-- Timeouts
ALTER SYSTEM SET idle_in_transaction_session_timeout = '30s';
ALTER SYSTEM SET statement_timeout = '30s';

-- Monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Security defaults
REVOKE ALL ON SCHEMA public FROM public;

SELECT pg_reload_conf();
```

## Edge Cases

- **PostgreSQL version < 12**: Generated columns, JSONB path queries (`jsonb_path_query`), and CTEs with `SEARCH`/`CYCLE` are NOT available. Always ask or check `SELECT version()` before recommending these features. For older versions, suggest equivalent workarounds (e.g., triggers instead of generated columns).
- **Conflicting patterns (normalization vs denormalization)**: State the trade-off explicitly. Normalization reduces data redundancy and ensures consistency (good for OLTP). Denormalization reduces joins and improves read performance (good for OLAP/reporting). Recommend normalization by default; denormalize only when query performance on specific read paths is measurably insufficient.
- **Very large tables (>100M rows)**: Recommend table partitioning (RANGE on timestamp columns is most common). Example: `CREATE TABLE orders (... ) PARTITION BY RANGE (created_at);` with monthly partitions. Also suggest `BRIN` indexes for sequential data and warn that `VACUUM` may need tuning (`autovacuum_vacuum_scale_factor` lowered to 0.01).
- **Missing `pg_stat_statements`**: If the user asks about slow queries but `pg_stat_statements` is not enabled, provide the setup: `CREATE EXTENSION pg_stat_statements;` and note it requires `shared_preload_libraries = 'pg_stat_statements'` in postgresql.conf (requires restart).
- **RLS performance pitfall**: Subqueries in RLS policies execute per-row. Always wrap `auth.uid()` in a `SELECT` subquery (as shown in the pattern above) to ensure it evaluates once, not per-row.

## Related

- Agent: `database-reviewer` - Full database review workflow
- Skill: `migration-advisor` - Database migration patterns

---

*Based on Supabase Agent Skills (credit: Supabase team) (MIT License)*
