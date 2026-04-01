# Python Framework Sanitization Reference

When recommending sanitization, reference the **exact function** for the detected framework. Do NOT say "validate and sanitize everything."

| Framework | Input validation | SQL safety | Template escaping |
|---|---|---|---|
| Django | `django.core.validators`, `forms.CharField(max_length=...)`, `serializers.Serializer` (DRF) | ORM by default; raw SQL: `cursor.execute(sql, [params])` | Auto-escaped in templates; `mark_safe()` must be audited |
| Flask | `flask-wtf` validators, `marshmallow.Schema`, `pydantic.BaseModel` | SQLAlchemy `text(:param)`; raw: `db.execute(sql, {"param": val})` | Jinja2 auto-escapes; `|safe` filter must be audited |
| FastAPI | `pydantic.BaseModel` with field validators, `Query(max_length=...)` | SQLAlchemy `text(:param)` or `asyncpg` `$1` params | N/A (API-only); JSON responses auto-serialized |
