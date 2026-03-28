---
name: dear-ant project patterns
description: Recurring issues and patterns found in dear-ant codebase (localStorage-based investment journal app)
type: project
---

Migration from Supabase API routes to `clientStore` (localStorage) is partially complete.

**Why:** App moved to offline-first localStorage model; API routes still exist but only history/page.tsx still calls them.

**Patterns to watch:**
- Date comparisons mix UTC ISO strings (stored) vs local date strings (UI) — causes off-by-one in KST/non-UTC timezones
- `crypto.randomUUID()` used in `client-store.ts` — not guarded by `isClient()`, will throw in SSR if called on server
- `saveAnswers` appends without pruning — unbounded localStorage growth after many survey completions
- Win-rate calculation in memo/page.tsx uses incorrect denominator (all memos, not just completed trades)

**How to apply:** Flag any new date string comparisons that mix `toISOString()` output with locally-derived date strings. Flag any new `setAll()` calls that lack a try/catch for QuotaExceededError.
