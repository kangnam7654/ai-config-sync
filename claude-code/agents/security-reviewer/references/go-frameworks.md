# Go Framework Sanitization Reference

When recommending sanitization, reference the **exact function** for the detected framework. Do NOT say "validate and sanitize everything."

| Framework | Input validation | SQL safety | Output escaping |
|---|---|---|---|
| net/http | Custom validation or `go-playground/validator` struct tags | `database/sql` with `db.Query(sql, args...)` placeholder `$1`/`?` | `html/template` auto-escapes; `text/template` does NOT |
| Gin | `binding:"required,email"` struct tags, `ShouldBindJSON` | Same as net/http | `c.JSON()` auto-serializes; HTML: use `html/template` |
| Echo | `echo.Bind()` + custom validator | Same as net/http | `c.JSON()` auto-serializes |
