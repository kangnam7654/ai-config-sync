# Data Files Reference

Applies when request involves: CSV, TSV, JSON, YAML, TOML, "convert", "export", "clean", "transform", "schema".

## Scope

### IN scope
- **Structured data files**: CSV, TSV, JSON, YAML, TOML — creation, conversion, cleaning, schema design
- **Data transformation**: Format conversion (JSON↔YAML, CSV↔JSON), schema migration, data cleaning, deduplication
- **Template creation**: Reusable templates for data file types

### OUT of scope
- Business documents (specs, RFCs, reports) → load `business-docs.md` reference
- Human-readable documentation → load `human-docs.md` reference
- LLM-facing documents → load `llm-docs.md` reference

## Rules

### ALWAYS

1. ALWAYS validate data file output against the format specification before delivering (CSV: RFC 4180, JSON: RFC 8259, YAML: YAML 1.2, TOML: TOML v1.0.0)
2. ALWAYS include a header row in CSV/TSV files
3. ALWAYS use UTF-8 encoding for all output files
4. ALWAYS add UTF-8 BOM (`\xEF\xBB\xBF`) to CSV files — required for Excel compatibility on Windows and macOS
5. ALWAYS double-quote CSV fields that contain commas, double quotes, newlines, or leading/trailing whitespace
6. ALWAYS escape double quotes inside CSV fields by doubling them (`""`)
7. ALWAYS use ISO 8601 format for dates (`2026-03-18`) and datetimes (`2026-03-18T14:30:00+09:00`) in all data files
8. ALWAYS use 2-space indentation for JSON and YAML files

### NEVER

1. NEVER produce CSV files that violate RFC 4180 — no unquoted fields containing delimiters, no inconsistent column counts across rows, no missing line endings
2. NEVER use trailing commas in JSON files
3. NEVER mix tabs and spaces for indentation within a single file
4. NEVER output YAML with implicit type coercion hazards unquoted — quote these values: `yes`, `no`, `on`, `off`, `true`, `false`, `null`, `~`, bare numbers that are identifiers (e.g., version `3.10` must be `"3.10"` not `3.1`)
5. NEVER output data files with inconsistent schemas — every row/object in a collection MUST have the same keys in the same order
6. NEVER silently drop data during transformation — IF source data cannot be mapped to the target format, report the unmappable items to the user before proceeding

## Requirements Gathering

1. Identify the source data (user-provided, file on disk, or generated)
2. Identify the target format (CSV, TSV, JSON, YAML, TOML)
3. Identify the consumer (Excel, API, config loader, database import, human review)
4. IF source data exists, read it and report: row count, column count, detected encoding, any anomalies (missing values, inconsistent types)

## Data File Format Rules

### CSV (RFC 4180 compliant)

```
Encoding: UTF-8 with BOM (\xEF\xBB\xBF)
Line ending: CRLF (\r\n)
Delimiter: comma (,)
Quoting: double-quote (") — REQUIRED for fields containing: comma, double-quote, newline, leading/trailing whitespace
Escape: double the quote character ("" inside quoted fields)
Header: REQUIRED — first row is always column names
Column names: snake_case, ASCII only, no spaces
Null values: empty field (two consecutive delimiters)
Dates: ISO 8601 (2026-03-18)
Datetimes: ISO 8601 with timezone (2026-03-18T14:30:00+09:00)
Numbers: no thousands separator, period for decimal (1234.56)
Booleans: true/false (lowercase)
```

Validation command:
```bash
uv run python -c "
import csv, io, sys
with open('OUTPUT_FILE', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    header = next(reader)
    col_count = len(header)
    for i, row in enumerate(reader, 2):
        assert len(row) == col_count, f'Row {i}: expected {col_count} columns, got {len(row)}'
    print(f'Valid CSV: {col_count} columns, {i} rows')
"
```

### TSV

```
Encoding: UTF-8 (no BOM)
Line ending: LF (\n)
Delimiter: tab (\t)
Quoting: NONE — tabs and newlines within fields are replaced with spaces
Header: REQUIRED
Column names: snake_case, ASCII only
Null values: empty field (two consecutive tabs)
```

### JSON (RFC 8259 compliant)

```
Encoding: UTF-8 (no BOM)
Indentation: 2 spaces
Trailing commas: PROHIBITED
Key ordering: alphabetical within each object level
Strings: double-quoted, with proper escape sequences (\n, \t, \\, \", \uXXXX)
Numbers: no leading zeros (except 0.x), no trailing decimal point
Null: JSON null (not "null" string)
Top-level structure: object {} or array [] — never a bare value
```

Validation command:
```bash
uv run python -c "
import json, sys
with open('OUTPUT_FILE', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f'Valid JSON: {type(data).__name__}, {len(data)} entries')
"
```

### YAML (YAML 1.2)

```
Encoding: UTF-8 (no BOM)
Indentation: 2 spaces (no tabs)
Document markers: start with --- on first line
String quoting: REQUIRED for values that YAML auto-coerces: yes, no, on, off, true, false, null, ~, bare floats that are version strings (3.10 → "3.10")
Multi-line strings: use | (literal block) for preserving newlines, > (folded block) for wrapping
Comments: use # with a space before the comment text, aligned to column when annotating adjacent lines
Null values: ~ (tilde)
Anchors/aliases: permitted only when reducing duplication of 3+ identical blocks
```

Validation command:
```bash
uv run python -c "
import yaml, sys
with open('OUTPUT_FILE', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)
    print(f'Valid YAML: {type(data).__name__}')
"
```

### TOML (v1.0.0)

```
Encoding: UTF-8 (no BOM)
Indentation: none for top-level keys, 2 spaces for inline continuation
Strings: basic ("...") for values with escape sequences, literal ('...') for paths and regex
Dates: RFC 3339 (2026-03-18T14:30:00+09:00)
Arrays: one element per line for 3+ elements, inline for 1-2 elements
Tables: [section.subsection] dot notation
Comments: # with a space before comment text
```

Validation command:
```bash
uv run python -c "
try:
    import tomllib
except ImportError:
    import tomli as tomllib
with open('OUTPUT_FILE', 'rb') as f:
    data = tomllib.load(f)
    print(f'Valid TOML: {len(data)} top-level keys')
"
```

## Production Workflow

1. Generate the file content following the exact format rules above
2. Validate the output using the appropriate validation command
3. IF validation fails, fix the error and re-validate. Repeat until validation passes.
4. Write the file to the path specified by the user, or propose a path following the pattern `{descriptive-name}.{ext}`

## Edge Cases

| Situation | Resolution |
|-----------|------------|
| Source CSV uses semicolon delimiter (European locale) | Auto-detect delimiter by parsing first 5 rows. Convert to comma delimiter in output. Inform user: "Source used semicolon delimiter; converted to RFC 4180 comma delimiter." |
| JSON source contains comments (`//` or `/* */`) | Strip comments before parsing. Inform user: "Source contained non-standard JSON comments; stripped during conversion." |
| YAML source uses YAML 1.1 boolean values (`yes`/`no`) | Convert to YAML 1.2 compliant values (`true`/`false`). Quote original values if they were used as strings. Inform user of the conversion. |
| CSV data contains mixed encodings (some rows UTF-8, some Latin-1) | Detect encoding per-row using byte analysis. Convert all to UTF-8. Report rows that required conversion. IF conversion fails for a row, replace undecodable bytes with U+FFFD and report affected rows. |
| User provides data with more than 50 columns | Warn the user: "This dataset has {N} columns. CSV files with 50+ columns are difficult to work with in spreadsheets. Consider splitting into multiple files or using JSON/YAML instead." Proceed with the user's chosen format after acknowledgment. |
| TOML source or target requires nested arrays of tables | Use `[[section]]` syntax. Validate with Python `tomllib`. IF the nesting exceeds 3 levels, suggest flattening with dot-notation keys and explain the tradeoff. |
| Data contains PII (emails, phone numbers, SSN patterns, credit card numbers) | Detect common PII patterns. STOP before writing the file. Warn user: "Detected potential PII in columns: {list}. Confirm you want to proceed, or specify columns to redact." Do not write the file until user confirms. |
| Requested format conversion would lose data (e.g., nested JSON → flat CSV) | Report what will be lost: "Converting nested JSON to flat CSV will lose: {list of nested fields}. Options: (1) flatten with dot-notation column names, (2) output only top-level fields, (3) use a different format. Choose 1/2/3." |
| Empty source data (0 rows, empty object/array) | Create a valid file with headers/schema only (no data rows). Report: "Source data was empty. Output contains schema/headers only." |
