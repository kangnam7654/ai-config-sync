# Diagnostic Commands Reference

**WARNING: Only run these against dev/staging databases. Ask user for confirmation before running against ANY database.**

## Connection Test (Always Run First)

```bash
psql "$DATABASE_URL" -c "SELECT current_database(), current_user, version();"
```

Verify the connection is NOT production before proceeding with any diagnostic commands.

```bash
# Verify connection is NOT production
psql "$DATABASE_URL" -c "SELECT current_database(), inet_server_addr();"
```

## Slow Queries (requires pg_stat_statements extension)

```bash
psql "$DATABASE_URL" -c "SELECT query, mean_exec_time, calls, total_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

If `pg_stat_statements` is not installed: `CREATE EXTENSION IF NOT EXISTS pg_stat_statements;` (requires superuser).

## Table Sizes

```bash
psql "$DATABASE_URL" -c "SELECT schemaname, relname, n_live_tup, pg_size_pretty(pg_total_relation_size(relid)) AS total_size FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 20;"
```

Use to identify large tables that may have locking risk during DDL operations.

## Missing Indexes (Tables with High Sequential Scan Ratio)

```bash
psql "$DATABASE_URL" -c "SELECT relname, seq_scan, idx_scan, seq_scan - idx_scan AS diff FROM pg_stat_user_tables WHERE seq_scan > idx_scan ORDER BY diff DESC LIMIT 10;"
```

Tables where `seq_scan > idx_scan` are candidates for new indexes.

## Lock Monitoring

```bash
psql "$DATABASE_URL" -c "SELECT pid, mode, relation::regclass, granted FROM pg_locks WHERE NOT granted;"
```

Shows ungranted locks — blocked queries waiting for a lock to be released.

## EXPLAIN with Full Detail (dev/staging ONLY)

```bash
# For SELECT queries: full EXPLAIN with ANALYZE and BUFFERS
psql "$DATABASE_URL" -c "EXPLAIN (FORMAT JSON, ANALYZE, BUFFERS) <QUERY>;"

# For mutations (INSERT/UPDATE/DELETE): EXPLAIN without ANALYZE to avoid side effects
psql "$DATABASE_URL" -c "EXPLAIN (FORMAT JSON) <QUERY>;"

# Human-readable format for quick review
psql "$DATABASE_URL" -c "EXPLAIN (FORMAT TEXT, ANALYZE) <QUERY>;"
```

## EXPLAIN Output Interpretation

| Output Signal | Meaning | Action |
|---|---|---|
| `Seq Scan` on large table | No index used | Add index on filter/join column |
| `Rows Removed by Filter` >> actual rows | Poor index selectivity | Consider partial index or composite index |
| `actual time` >> `estimated time` | Stale table statistics | Run `ANALYZE table_name` |
| High `Buffers: shared read` | Cache miss | Consider `pg_prewarm` or query restructuring |
| `Hash Join` on large tables | May be acceptable | Verify estimated vs actual row counts |
| `Nested Loop` with large outer | N+1 risk | Batch fetch or restructure query |

## Static Analysis (When No DB Available)

When no database connection is available, prefix ALL findings with `STATIC_REVIEW:` and:
1. Check WHERE/JOIN columns against schema definition for index coverage
2. Apply anti-pattern detection from `anti-patterns.md`
3. Score `query_performance` with -1 penalty (max 9) in pipeline mode
4. Note: `STATIC_REVIEW: No non-production database available. Analysis based on SQL structure and stated schema only.`
