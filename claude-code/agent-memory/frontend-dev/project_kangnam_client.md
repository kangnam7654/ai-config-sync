---
name: kangnam-client project patterns
description: Tech stack, design system, file conventions and key paths for kangnam-client (Tauri desktop LLM chat client)
type: project
---

## Tech Stack
- Tauri 2 + React + TypeScript + Vite
- Styling: inline styles + CSS variables (no Tailwind utility classes in components, only Tailwind config for utility generation)
- State: Zustand (single `useAppStore` from `stores/app-store.ts`)
- Chat UI: `@assistant-ui/react` + `@assistant-ui/react-markdown`
- Syntax highlighting: Shiki (lazy-loaded, `github-dark` theme)
- IPC: `window.api` (set by `lib/tauri-api.ts` — Tauri only, no Electron)

## Design System (CSS variables)
- `--bg-main`, `--bg-sidebar`, `--bg-surface`, `--bg-hover`
- `--text-primary`, `--text-secondary`, `--text-muted` (#8a8a8a dark / #999 light)
- `--accent` (#d97757 dark / #c96a4c light)
- `--accent-soft`: rgba(217,119,87,0.15)
- `--danger`: #ef4444, `--success`: #10b981
- Dark theme default; `[data-theme="light"]` override on `:root`
- Theme switch via `document.documentElement.setAttribute('data-theme', theme)`

## Key File Paths
- Utils: `src/renderer/lib/utils.ts` — `cn()`, `fileToDataUrl()`
- Providers: `src/renderer/lib/providers.ts` — `ALL_PROVIDERS`, `getVisibleProviders()`, `getProviderInfo()`
- API adapter: `src/renderer/lib/tauri-api.ts` — sets `window.api`
- Store: `src/renderer/stores/app-store.ts` — `useAppStore`
- Shared components: `src/renderer/components/shared/` (e.g. `Starburst.tsx`)
- Chat components: `src/renderer/components/chat/`
- Sidebar components: `src/renderer/components/sidebar/`
- Settings: `src/renderer/components/settings/SettingsPanel.tsx`
- Styles: `src/renderer/styles/globals.css`

## Component Conventions
- Styling: inline styles using CSS variables; Tailwind utility classNames for hover/focus states
- No separate CSS modules — global CSS only for shared utilities
- `aria-hidden="true"` on all decorative SVG icons
- `aria-label` on all icon-only buttons
- `title={conv.title}` on truncated text spans for tooltip
- Error boundaries: `ChatErrorBoundary` in `ChatView.tsx` — logs to console, shows user-friendly message (no stack trace in DOM)

## IPC Patterns
- All Tauri commands via `window.api.*` — never call `invoke()` directly from components
- DO NOT change Tauri IPC command names or event names
- `.catch(console.error)` on all unhandled promise rejections from `window.api.*`

## Architecture Notes
- `WelcomeScreen` is a separate component in `components/chat/WelcomeScreen.tsx` (extracted from ChatView)
- Shared SVG Starburst: `components/shared/Starburst.tsx` — props: `size`, `color`, `animated`
- `fileToDataUrl` utility is in `lib/utils.ts` (not local to components)
- `PROVIDERS` deprecated export was removed from `lib/providers.ts`; use `ALL_PROVIDERS` or `getVisibleProviders()` instead

**Why:** audit-report.md identified 49 improvement items; this project is in active quality/UX improvement phase per design-spec.md.
