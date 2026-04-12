# Database Security Reference

## RLS Policy Verification

- RLS MUST be enabled on ALL multi-tenant tables
- No exception for "internal-only" tables unless documented with explicit justification
- Correct RLS pattern uses `(SELECT auth.uid())` subselect — NOT `auth.uid()` directly
  - Subselect evaluates once per query, not once per row → prevents per-row function call overhead
  - Direct `auth.uid()` call is a performance issue AND harder to optimize

### Correct RLS Pattern

```sql
-- CORRECT: subselect prevents per-row evaluation
CREATE POLICY "user_isolation" ON orders
  FOR ALL
  USING (user_id = (SELECT auth.uid()));

-- INCORRECT: direct function call evaluated per row
CREATE POLICY "user_isolation" ON orders
  FOR ALL
  USING (user_id = auth.uid());
```

## RLS Index Requirement

- Every RLS policy filter column MUST have an index
- RLS policies run for every row access — unindexed filter columns cause sequential scans under RLS
- Example: if RLS policy filters on `user_id`, `user_id` must be indexed
- Verify: `\d+ table_name` to see indexes and check against policy filter columns

## GRANT Scope (Least Privilege)

- Application roles: `GRANT SELECT, INSERT, UPDATE, DELETE ON specific_table TO app_role`
- NEVER `GRANT ALL` to application-level database users
- NEVER `GRANT` superuser or `CREATEROLE` to application roles
- Read-only roles: `GRANT SELECT` only
- Admin roles (migrations): separate role, not used by application runtime

### Correct Grant Pattern

```sql
-- CORRECT: explicit per-table, per-operation grants
GRANT SELECT, INSERT, UPDATE ON orders TO app_user;
GRANT SELECT ON products TO app_user;

-- INCORRECT: overly broad
GRANT ALL ON ALL TABLES IN SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON DATABASE mydb TO app_user;
```

## SQL Injection Detection

- Scan all SQL strings for unparameterized values:
  - String concatenation: `"SELECT * FROM users WHERE id = " + user_id` → P0 CRITICAL
  - Template literals with user input: `` `SELECT * FROM ${tableName}` `` → P0 CRITICAL
- Safe pattern: parameterized queries with `$1`, `$2`, etc.
- ORM-generated SQL: generally safe, but review raw query escape hatches (`$queryRaw`, `sql.raw()`)
- Dynamic table/column names cannot be parameterized — require explicit allowlist validation

## Sensitive Column Flagging

- Identify columns containing PII: `email`, `phone`, `ssn`, `address`, `date_of_birth`, `ip_address`
- Identify columns containing secrets: `password_hash`, `api_key`, `token`, `secret`
- Verify these columns are:
  - NOT included in `SELECT *` queries exposed to application layer
  - NOT visible in views without explicit justification
  - Protected by column-level security if needed: `REVOKE SELECT (sensitive_col) FROM app_role`

## Checklist (P0 if violated)

- [ ] RLS enabled on all multi-tenant tables, using `(SELECT auth.uid())` subselect pattern
- [ ] RLS policy filter columns are indexed
- [ ] No `GRANT ALL` to application users — least privilege enforced
- [ ] No unparameterized queries (SQL injection risk)
- [ ] Sensitive columns (PII, secrets) flagged for encryption or access restriction
