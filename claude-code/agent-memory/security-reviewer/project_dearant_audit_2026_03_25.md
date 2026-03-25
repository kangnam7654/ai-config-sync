---
name: dear-ant full audit 2026-03-25
description: Full OWASP security audit of the dear-ant Next.js app — anonymous investment report PWA
type: project
---

Full OWASP audit of /Users/kangnam/projects/dear-ant performed 2026-03-25.

**Why:** Pre-deployment security review requested by user.
**How to apply:** Reference for follow-up audits; note which issues are architecture decisions vs. fixable bugs.

## Stack
- Next.js 16.1.6, React 19.2.3, @supabase/supabase-js ^2.99.1
- No authentication — fully anonymous app
- Dual mode: Supabase (prod) or in-memory localStore (dev fallback)

## Findings Summary (with file:line)

### CRITICAL
- None found

### HIGH
1. **A01-1 / CORS**: No CORS headers configured in next.config.ts. Next.js same-origin default applies, but no explicit allowlist enforced. Medium-HIGH for future API expansion.
2. **A05-4 / Security Headers**: next.config.ts is empty — no `X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`, `Strict-Transport-Security`. All headers absent.
3. **A01-3 / IDOR via Supabase RLS**: RLS policies are `using (true)` — any user can SELECT all sessions, answers, reports from ANY other user. No ownership check. Data is anonymous but birth_date and mood history are PII-adjacent. No user-scoped reads.
4. **A04-1 / No rate limiting**: `POST /api/reports` (report generation, hits Supabase writes) has zero rate limiting. Abuse could exhaust Supabase quota or fill DB with junk.
5. **A08-1 / PATCH /api/memos/[id] raw body passthrough**: `localStore.updateMemo(id, body)` accepts raw parsed JSON body from client with no field allowlisting. TypeScript type `Partial<Pick<...>>` provides compile-time safety only, not runtime. Attacker can inject extra fields at runtime.

### MEDIUM
6. **A01-2 / No auth on any route**: All API routes are publicly accessible with no authentication. By design (anonymous app), but means ALL data is globally accessible when Supabase is enabled (any user reads any report via /api/reports/[id]).
7. **A02-3 / No HTTPS enforcement**: No `Strict-Transport-Security` header configured.
8. **A04-2 / Account enumeration**: N/A — no accounts in this app.
9. **A05-1 / No explicit debug guard**: No check that NODE_ENV=production disables verbose errors. `console.error('Report creation error:', error)` leaks to server logs but not client (acceptable). Error messages are generic strings — OK.
10. **A09-1 / No auth event logging**: N/A — no auth in this app.
11. **Supabase anon key in NEXT_PUBLIC**: `NEXT_PUBLIC_SUPABASE_ANON_KEY` is intentionally browser-exposed per Supabase design (anon key + RLS). Acceptable if RLS is correctly configured — but RLS is NOT correctly configured (see #3).

### LOW
12. **A07-3 / No session cookies**: No JWTs or session tokens in use — purely stateless anonymous app. N/A.
13. **Input length limits absent**: `stock_name`, `memo`, `birthDate` have no max length enforcement in API routes. Could be exploited for large payload storage abuse.
14. **Birth date not validated**: `body.userInfo.birthDate` is passed directly to `calculateBiorhythm()` which does `new Date(birthDate)`. Invalid dates produce NaN biorhythm values silently.

## Supabase RLS Assessment
- RLS enabled on all 4 tables: GOOD
- INSERT policies: `with check (true)` — anyone can insert: ACCEPTABLE for anonymous app
- SELECT policies: `using (true)` — anyone can select ALL rows from sessions, answers, reports: PROBLEMATIC
  - No UPDATE or DELETE policies exist for users table — only the service_role key can update/delete users
  - Missing SELECT policy on `users` table (no `create policy "Allow anonymous select" on users`)

## Dependency Audit
- next: 16.1.6 — very recent, no known CVEs
- react: 19.2.3 — very recent
- @supabase/supabase-js: ^2.99.1 — very recent
- pptxgenjs: ^4.0.1 (devDependency) — no known critical CVEs
- No npm audit tool run (node_modules may not be installed in audit environment)

## Overall Security Score
- API Route Security: 5/10
- Supabase/RLS: 4/10 (RLS enabled but policies too permissive)
- XSS: 9/10 (React auto-escaping, no dangerouslySetInnerHTML)
- CSRF: 7/10 (Next.js same-origin default, no custom CSRF needed for SPA)
- Input validation: 4/10 (no length limits, no type validation at API layer)
- Secrets/Env: 8/10 (env vars used, .gitignore covers .env*)
- Auth/Authz: 3/10 (by design anonymous, but Supabase data globally readable)
- Rate limiting: 1/10 (none)
- Dependency: 8/10 (all dependencies very recent)
- Security headers: 1/10 (none configured)
- **Overall: 5/10**
