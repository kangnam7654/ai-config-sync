---
name: lunawave_saju_simulator
description: Simulator config for 달결 (Saju) iOS app — device, bundle ID, build path, Maestro patterns, test account
type: project
---

## App: 달결 (Saju)
- **Project path**: /Users/kangnam/projects/lunawave/ios/Saju/Saju.xcodeproj
- **Scheme**: Saju
- **Bundle ID**: com.saju.Saju
- **Target device**: iPhone 17 Pro, iOS 26.2, UDID: 3ED9A4F3-BFD5-4B1C-902D-0F9A1EB9ABC1
- **Build output (custom derivedData)**: /tmp/saju-build/Build/Products/Debug-iphonesimulator/Saju.app
- **Build command**: `xcodebuild -project /Users/kangnam/projects/lunawave/ios/Saju/Saju.xcodeproj -scheme Saju -destination 'platform=iOS Simulator,id=3ED9A4F3-BFD5-4B1C-902D-0F9A1EB9ABC1' -derivedDataPath /tmp/saju-build -configuration Debug build`
- **Install**: `xcrun simctl install 3ED9A4F3-BFD5-4B1C-902D-0F9A1EB9ABC1 /tmp/saju-build/Build/Products/Debug-iphonesimulator/Saju.app`
- **Launch**: `xcrun simctl launch 3ED9A4F3-BFD5-4B1C-902D-0F9A1EB9ABC1 com.saju.Saju`
- **Simulator status as of 2026-03-25**: Booted (iPhone 17 Pro, iOS 26.2)
- **Backend API**: https://saju-api.fly.dev

## Test Account
- **Email**: test99@test.com
- **Password**: testtest123
- **Nickname**: testuser99
- **User ID**: 5257f548-9b8f-4170-86c2-4b58a5ddc1cf
- Created via: `curl -X POST https://saju-api.fly.dev/v1/auth/register`

## Maestro Setup
- **Maestro version**: 2.3.0 at ~/.maestro/bin/maestro
- **Flow files**: /Users/kangnam/projects/lunawave/maestro/
- **Key flows**: login-full.yaml, capture-tabs.yaml, capture-mypage-details.yaml

## Maestro Patterns That Work
- Tab navigation: `tapOn: "홈"`, `tapOn: "상담"`, `tapOn: "리포트"`, `tapOn: "마이"` — uses tab text labels
- Back navigation: `tapOn: point: "8%, 9%"` — hits the nav bar back chevron reliably
- Login flow: tap "이메일로 시작하기" → tap "이미 계정이 있으신가요? 로그인" → tap field by text → inputText → tap title to dismiss keyboard → tap "로그인"
- Keyboard dismissal: tap the screen title text (e.g. "이메일 로그인") to dismiss keyboard — hideKeyboard command fails for custom inputs
- Password AutoFill dialog: does NOT appear reliably; if it appears use pressKey: Escape
- Strong password prompt after login: tap "지금 안 함" to dismiss

## iOS 26.2 / iPhone 17 Pro Screen Details
- Simulator window position: (791, 107) size 456x972 macOS pts
- Screen content group: (818, 187) size 402x874 macOS pts
- Scale: cliclick coords = screen_x = 818 + ios_x, screen_y = 187 + ios_y (1:1 scale)
- cliclick back button (nav bar): screen (848, 262) or use Maestro point "8%, 9%"
- Email login button: screen y=672 (ios_y=485 from screen top)

## Known Issues
- MyPageView scrolls past profile card on initial load after navigating away — requires fresh app launch to see profile card at top
- ProfileListView navigation works only when app just launched fresh (not from within scrolled MyPage)
- iOS 26.2 Passwords app is separate; strong password dialog blocks SecureField interaction

**Why:** Saved to avoid re-discovering all these details on each session.
**How to apply:** Use test account for login flows. Use Maestro with text-label tap for navigation. For MyPage profile card, ensure app is freshly launched.
