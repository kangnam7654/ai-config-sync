---
name: saju2_ios_dark_purple_theme
description: Dark purple theme palette and known issues in the saju2 iOS project (달결 app), as of 2026-03-16 thorough review
type: project
---

The iOS app uses a dark purple theme (not the warm beige described in CLAUDE.md, which is outdated).

**Palette:**
- Background: #1A0E2E
- Card: #251746
- Accent/Purple: #A855F7
- Deep Purple: #7C3AED
- Primary Text: #F0E6FF
- Subtext: #9B8CB5
- Border: #3D2660 (also #2F1E50 in Consult screens)
- Gradient colors: #2D1B4E, #1F1040, #1B2A4E, #3D1B3E, #1B3D2E, #2F1E50

**Summary of Issues Found (2026-03-16 full review):**

CRITICAL / HIGH:
1. LoginView.swift:88 — Google button textColor is Color(hex: "1A0E2E") on white bg → correct (dark text on white). OK.
   Actually looking more carefully: textColor: Color(hex: "1A0E2E") = very dark purple, on white. This is fine.
2. InquiryView.swift:68-79 — TextField("example@email.com") on Color.iqCard (#251746) background has NO .foregroundColor modifier. System default is black/dynamic, which will be invisible on dark background.
3. WalletView.swift (PointsView) ledger rows — delta>0 uses `.blue`, delta<0 uses `.red`. System `.blue`/`.red` are readable on dark backgrounds but are unthemed.
4. Shadows everywhere: `.shadow(color: .black.opacity(0.04), radius: 10)` — nearly invisible on #1A0E2E bg. Purely decorative artifact.
5. ServiceSelectView.swift — uses system colors: Color.blue, Color(.systemGray6), .secondary. No dark theme applied.
6. ReviewView.swift / ReportView.swift — use system Form (white/light background), completely untouched.
7. ReadingCreateView.swift — uses system Form, completely untouched.
8. ConsentsView.swift — uses system List, completely untouched.
9. DatePicker in ProfileEditView.swift (.wheel style) renders with system default appearance; may appear with light background on dark screen.
10. Link color #5B6CFF at 11pt on dark bg: contrast is ~4.4:1 (just below WCAG AA 4.5:1 for normal text <18pt).
11. SplashView spinner color #7C3AED on #1A0E2E: ~3.2:1 contrast (below 4.5:1 for AA).
12. NavigationBar background not explicitly set in any view — relies on transparent/bleed-through from background image. If background image fails to load, nav bar may show system default white.
13. CLAUDE.md design system section still describes warm theme — out of date.

**Why:** CLAUDE.md still references warm theme but all screens have been migrated to dark purple.
**How to apply:** When adding new screens, use dark purple palette. Flag legacy Form-based screens (ServiceSelectView, ReviewView, ReportView, ReadingCreateView, ConsentsView) as untouched and needing migration.
