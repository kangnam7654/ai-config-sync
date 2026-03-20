---
name: Dalgyeol (달결) Saju App
description: iOS saju/fortune app project at /Users/kangnam/projects/saju2 - dark purple theme, SwiftUI+MVVM, Rust backend
type: project
---

Dalgyeol (달결) is a saju-based fortune/AI consultation iOS app at `/Users/kangnam/projects/saju2`.

**Why:** Active product with ongoing UI improvements and feature development.

**How to apply:**
- iOS source at `ios/Saju/Saju/`, backend at `backend/`
- Design system: dark purple theme (#1A0E2E bg, #251746 card, #A855F7 accent)
- Color constants are defined per-file as `private extension Color` (not global)
- Each Home subview has its own color prefix (df*, tarot*, checkin*, ad*, nt*)
- CommonBackground image asset used as scrolling backdrop
- HomeView UI improvement plan at `docs/design/PLAN_HOMEVIEW_UI_IMPROVEMENT.md`
- UI trend research at `docs/design/UI_TREND_REPORT.md`
- All plans are iOS-only (SwiftUI) unless backend changes explicitly needed
- Existing MVVM pattern: ViewModel signature changes require careful coordination
