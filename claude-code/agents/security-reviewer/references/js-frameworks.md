# JavaScript/TypeScript Framework Sanitization Reference

When recommending sanitization, reference the **exact function** for the detected framework. Do NOT say "validate and sanitize everything."

| Framework | Input validation | SQL safety | Output escaping |
|---|---|---|---|
| Express | `zod.object({...}).parse(req.body)`, `joi.object({...}).validate()`, `express-validator.body().isEmail()` | `knex('table').where('id', id)`, `pg` with `$1` params, Prisma ORM | `res.json()` auto-serializes; HTML: use `DOMPurify.sanitize()` |
| Next.js | `zod` in Server Actions / API routes, `next-safe-action` | Prisma ORM, Drizzle ORM | React auto-escapes JSX; `dangerouslySetInnerHTML` must use `DOMPurify.sanitize()` |
| NestJS | `class-validator` decorators + `ValidationPipe`, `zod` with `ZodValidationPipe` | TypeORM parameterized queries, Prisma ORM | `class-transformer` for response serialization |
