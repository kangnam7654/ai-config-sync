---
name: kangnam-client UI Design System
description: Design tokens, color palette, typography, and layout specs for the kangnam-client Tauri desktop app (Claude Code wrapper)
type: project
---

kangnam-client uses a warm dark/light mode palette with terracotta accent (#d97757). Desktop Tauri app at 1440x900.

**Why:** The app wraps Claude Code CLI in a native desktop GUI. UI must feel like a polished chat app (inspired by Claude.ai design language) while supporting developer workflows (code blocks, tool results, agents, tasks).

**How to apply:**
- Dark mode default: bg-main #2b2a27 (warm brown), sidebar #1f1e1b, surface #353432
- Light mode: bg-main #faf9f5 (warm cream), sidebar #f0ede3, surface #ffffff
- Accent: #d97757 (terracotta) for "K" logo, avatars, send button, links
- Fonts: Pretendard (UI, 14.5px, weight 450), Noto Serif KR (assistant text, 15px), JetBrains Mono (code, 13px)
- Sidebar width: 260px, collapsible. Top bar: 48px with macOS drag region
- User bubbles: right-aligned, rounded-2xl with rounded-br-sm, bg-user-bubble
- Tool/Agent cards: rounded-xl with colored borders (yellow=tool, green=result, blue=agent, red=error)
- Composer: max-width 48rem, centered, rounded-2xl, shadow, bg-composer

**Figma file:** "Dear JB" file, page "kangnam-client UI"
- Node IDs: Screen1=85:585, Screen2=85:650, Screen3=85:757, Screen4=85:839, Screen5=85:904, Screen6=85:945, Screen7=85:964
