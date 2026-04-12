# Schema Design Reference

## ID Types
- Use `bigint GENERATED ALWAYS AS IDENTITY` or UUIDv7 for primary keys
- NEVER use `int` for IDs — overflow risk on large tables
- NEVER use random UUIDv4 as primary key — index fragmentation due to random insertion order
- UUIDv7 is time-sorted; use when UUID format is required

## String Types
- Use `text` for all variable-length strings
- NEVER use `varchar(255)` without a documented maximum length requirement
- If a specific max length is enforced by business logic, `varchar(N)` is acceptable with a comment

## Timestamps
- Use `timestamptz` (timestamp with time zone) for ALL timestamp columns
- NEVER use `timestamp` (without timezone) — loses timezone context across environments
- Store and display in UTC; convert at application layer only

## Money / Decimal Values
- Use `numeric(precision, scale)` for monetary values
- NEVER use `float` or `real` — floating-point precision errors corrupt financial calculations

## Booleans
- Use `boolean` type for true/false flags
- NEVER use `int` 0/1 as a boolean substitute

## Foreign Keys
- ALL FK columns must have explicit `ON DELETE` behavior defined:
  - `ON DELETE CASCADE` — child rows deleted when parent is deleted
  - `ON DELETE SET NULL` — FK set to NULL when parent deleted (column must be nullable)
  - `ON DELETE RESTRICT` — prevents parent deletion if children exist
- ALL FK columns must have indexes (see query-opt.md for why)

## NOT NULL Constraints
- Apply `NOT NULL` to every column that is semantically required
- NEVER add a column with `NOT NULL` to a populated table without a `DEFAULT` value — this locks the table
- For large tables, add column WITHOUT default, then backfill in batches, then add `NOT NULL` constraint

## Normalization
- Achieve 3NF minimum
- Denormalization is acceptable ONLY with a comment explaining the reason (e.g., materialized view for read performance, JSONB for schema-flexible attributes)
- Flag all undocumented denormalization as P2 MEDIUM

## Naming Conventions
- ALL identifiers use `lowercase_snake_case`
- Table names: plural nouns (e.g., `users`, `order_items`)
- Boolean columns: prefix with `is_`, `has_`, `can_` (e.g., `is_active`, `has_subscription`)
- FK columns: `{referenced_table_singular}_id` (e.g., `user_id`, `order_id`)
- Timestamp audit columns: `created_at`, `updated_at`, `deleted_at`

## Checklist (P2 if violated)

- [ ] IDs use `bigint` or UUIDv7 (not `int`, not random UUIDv4 as PK)
- [ ] Strings use `text` (not `varchar(255)` without documented max length requirement)
- [ ] Timestamps use `timestamptz` (not `timestamp`)
- [ ] Money/decimal values use `numeric` (not `float` or `real`)
- [ ] Boolean flags use `boolean` (not `int` 0/1)
- [ ] All FKs defined with explicit `ON DELETE` behavior
- [ ] All FK columns have indexes
- [ ] `NOT NULL` applied where the column is semantically required
- [ ] 3NF achieved; any denormalization has a comment explaining why
- [ ] Identifiers use `lowercase_snake_case`
