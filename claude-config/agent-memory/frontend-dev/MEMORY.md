# Frontend-Dev Agent Memory

## FlirtIQ Project Patterns

### Tech Stack
- Next.js 16 App Router + TypeScript + Tailwind CSS
- Path alias: `@/` maps to `src/`
- API base: `NEXT_PUBLIC_API_URL` env var (default `http://localhost:8000`)

### Design System
- **Gradient**: `from-pink-500 to-purple-600` (primary brand gradient)
- **Card**: `rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-[#1a1a2e]`
- **Button primary**: `rounded-xl bg-gradient-to-r from-pink-500 to-purple-600 text-white font-semibold hover:opacity-90 active:scale-95 transition-all`
- **Button secondary**: `rounded-xl border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400`
- **Max width**: `max-w-md mx-auto` (mobile-first)
- **Bottom padding**: `pb-24` for pages with BottomNav

### API Client Pattern
- `api.get<T>(path)`, `api.post<T>(path, body)` helper in `src/lib/api.ts`
- Namespace methods like `api.subscription.status()` for grouped endpoints
- Auth via `Authorization: Bearer <token>` header (auto-added in request())
- 401 → auto redirect to /login

### Component Conventions
- `"use client"` at top for interactive components
- `isPremium?: boolean` prop pattern for premium-aware components (don't compute from local state)
- PremiumBadge sizes: `sm` (inline 10px) and `md` (with star icon)

### Auth Pattern
- `isLoggedIn()` from `src/lib/auth.ts` — checks token existence
- User info: fetch `/api/auth/me` for `UserResponse` (includes `is_premium`)
- `is_premium` is server-authoritative: read from API, never set locally

### Key Files
- Types: `src/types/index.ts` (SSOT, mirrors backend Pydantic schemas)
- API client: `src/lib/api.ts`
- Subscription components: `src/components/subscription/`
- Shared components: `src/components/shared/`

### Premium Gating UI
- Blurred placeholder: `blur-sm` + absolute overlay with lock icon
- PremiumGate component: use for full-page gates (daily limit exceeded)
- Inline blur: use for partial content gating within results

### Known Backend Endpoints
- `GET /api/auth/me` → `UserResponse` (confirmed)
- `GET /api/subscription/status` → `SubscriptionStatusResponse`
- `POST /api/subscription/checkout` → `CheckoutResponse`
- `POST /api/subscription/confirm` → `SubscriptionResponse`
- `POST /api/subscription/cancel` → `CancelResponse`
