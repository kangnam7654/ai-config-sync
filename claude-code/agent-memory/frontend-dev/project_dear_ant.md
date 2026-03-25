---
name: Dear,ANT Design System
description: Visual design tokens, component conventions, and tech stack for the Dear,ANT investment companion app
type: project
---

## Tech Stack
- Next.js 16.1.6 App Router + TypeScript + Tailwind CSS v4
- TailwindCSS v4: custom tokens in `@theme inline` block in `src/app/globals.css`
- Path alias: `@/` maps to `src/`
- No tailwind.config file — v4 uses CSS-only config

## Design System (Warm Theme — applied v3)
- **Body bg**: `#fdf8f6` (warm-50), body text: `#2d2422`
- **Primary action**: `bg-warm-700` (#8b4f30), hover: `bg-warm-600` (#b86a42)
- **Card**: `bg-white border border-warm-100 rounded-2xl shadow-sm`
- **Letter card** (report summary): `bg-white border border-warm-200 rounded-2xl shadow-sm`
- **Accent label text**: `text-warm-600`
- **Streak/badge text**: `text-warm-600`
- **Hero gradient**: `bg-gradient-to-b from-warm-100 to-warm-50`
- **BottomNav active icon**: `#8b4f30` (warm-700), label: `text-warm-700`
- **BottomNav bg**: `bg-warm-50 border-t border-warm-200`
- **Font**: Pretendard Variable (imported via `pretendard/dist/web/variable/pretendardvariable-dynamic-subset.css`)
- **themeColor**: `#b86a42` (warm-600)

## Warm Color Tokens (in @theme inline)
- warm-50: #fdf8f6 (cream white)
- warm-100: #f9f0eb (soft peach)
- warm-200: #f3e0d5
- warm-400: #e8a87c
- warm-500: #d4845e
- warm-600: #b86a42
- warm-700: #8b4f30

## Key Components
- `AntCharacter` at `src/components/AntCharacter.tsx` — ant mascot, props: `size`, `expression` ('happy'|'thinking'|'excited'|'worried'|'cool'), `speech` (speech bubble text)
- `BottomNav` at `src/components/BottomNav.tsx` — hides on /result/* routes
- Speech bubble in AntCharacter uses `border-purple-100` / `text-purple-600` (character-specific purple accent kept intentionally)

## Animation Convention
- All `.animate-*` classes are in `globals.css`
- Wrapped in `@media (prefers-reduced-motion: no-preference)` as of v3
- Fallback: opacity:1 / transform:none for reduced-motion users

## Page Structure
- `/` home: `pt-12 pb-nav`, max-w-sm, warm gradient hero
- `/history`, `/memo`: `py-12 px-6 pb-nav`, max-w-md
- All pages use `pb-nav` (calc(70px + safe-area-inset-bottom))

**Why:** Design direction shifted from cold SaaS slate-gray to warm emotional companion (Calm-meets-trading-journal) in v3 redesign.
**How to apply:** Always use warm-* tokens for primary actions, borders, backgrounds. Keep purple only for AntCharacter SVG internals and existing data-viz (history trend chart).
