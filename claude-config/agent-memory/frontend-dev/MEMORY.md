# Frontend-Dev Agent Memory

## Saju MVP Project Patterns

### Tech Stack
- Expo SDK 55 + Expo Router (file-based) + TypeScript
- NativeWind v4 (Tailwind for RN): use `className` on RN components — no cssInterop needed
- Zustand v5 for state, React Native Reanimated v4, MMKV available
- Path alias: `@/` maps to project root, so `@/src/lib/saju/types` = `./src/lib/saju/types`
- API base: `EXPO_PUBLIC_API_URL` env var (default `http://localhost:3000`)

### Design System (Dark Theme)
- **Main bg**: `bg-slate-950` (#020617)
- **Card**: `bg-slate-900 rounded-2xl border border-slate-800 p-4`
- **Header bg**: `#0f172a`, header text: `#fef3c7`
- **Primary text**: `text-amber-100`, secondary: `text-slate-300`, muted: `text-slate-400`
- **Button primary**: `bg-amber-500 rounded-xl py-4 px-6`, text: `text-slate-950 font-bold`
- **Button danger/rose**: `bg-rose-500 rounded-2xl`
- **Input**: `bg-slate-800 text-slate-100 rounded-xl px-3 py-3 text-base`
- **오행 colors**: wood=#10b981, fire=#f43f5e, earth=#f59e0b, metal=#e2e8f0, water=#3b82f6

### Key File Paths
- Types: `src/lib/saju/types.ts`
- Calculator: `src/lib/saju/calculator.ts` → `calculateFullSaju(params)`
- Compatibility: `src/lib/saju/compatibility.ts` → `calculateCompatibility(a, b)`
- Daily fortune: `src/lib/saju/daily-fortune.ts` → `calculateDailyFortune(saju, date?)`
- All exports: `src/lib/saju/index.ts`
- API client: `src/lib/api/client.ts` → `fetchSSE()`, `fetchJSON()`
- Stores: `src/stores/userStore.ts`, `src/stores/sajuStore.ts`
- Hooks: `src/hooks/useSajuCalculation.ts`, `src/hooks/useInterpretation.ts`

### NativeWind v4 Notes
- All standard RN components (View, Text, TouchableOpacity, etc.) accept `className`
- No StyleSheet needed — use className for all styles
- Preset: `require('nativewind/preset')` in tailwind.config.ts
- Import `global.css` in root layout

### Expo Router Patterns
- `useLocalSearchParams()` for URL params in stack screens
- `router.push({ pathname, params })` for navigation with params
- Tab screens: `app/(tabs)/name.tsx`, Stack screens: `app/category/screen.tsx`
- `SafeAreaView` from `react-native-safe-area-context`, use `edges={['bottom']}` on modal-style screens
- `KeyboardAvoidingView` for forms: `behavior={Platform.OS === 'ios' ? 'padding' : 'height'}`

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
