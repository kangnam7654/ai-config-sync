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
- Tab navigation: TEXT LABELS DO NOT WORK (FloatingTabBar is custom View, Maestro can't find text). Use COORDINATES:
  - **iPhone 17 Pro (402×874pt)**: 홈 `23%,90%` | 상담 `41%,90%` | 리포트 `59%,90%` | 마이 `77%,90%`
    - Tab bounds: 홈 [79,774][105,797], 상담 [150,774][179,797], 리포트 [229,775][245,796], 마이 [299,776][319,796]
  - **iPhone 17 Pro Max (440×956pt)**: 홈 `12%,94%` | 상담 `38%,94%` | 리포트 `63%,94%` | 마이 `88%,94%`
    - Tab bounds: 홈 [2,874][108,922], 상담 [112,874][218,922], 리포트 [222,874][328,922], 마이 [332,874][438,922]
  - NOTE: 퍼센트 좌표는 기기별 화면 크기에 따라 다름 — always verify bounds via `maestro hierarchy` on first use
  - Tab accessibility labels in hierarchy: "홈 탭", "상담 탭", "리포트 탭", "마이 탭" — but Maestro `tapOn: id:` does NOT work for these (resource-id is the SF symbol name, not the label)
- Back navigation: `tapOn: point: "8%, 9%"` — hits the nav bar back chevron reliably (from within app, not from ReadingDetailView)
- Login flow: tap "이메일로 시작하기" → `tapOn: point: "50%,65%"` (로그인 링크) → tap "이메일" → inputText → tap "비밀번호" → inputText → tap "로그인"
  - NOTE: "이미 계정이 있으신가요? **로그인**" 버튼은 markdown bold 때문에 텍스트/레이블로 탭 불가. 좌표 `50%,65%` 사용
  - Screen pixel height: 2622. Link is at y=1600~1700px = ~63~65%
- Keyboard dismissal: tap the screen title text (e.g. "이메일 로그인") to dismiss keyboard — hideKeyboard command fails for custom inputs
- Password AutoFill dialog: does NOT appear reliably; if it appears use pressKey: Escape
- Strong password prompt after login: tap "지금 안 함" to dismiss
- DatePicker (profile form): tap date field → tap "YYYY년 MM월" to switch to scroll picker → swipe within `(30%,27%)~(30%,17%)` for DOWN scroll (later dates), `(30%,17%)~(30%,27%)` for UP scroll (earlier dates) → tap "YYYY년 MM월" again to return to calendar → tap day number
- DatePicker (compatibility form): tap date field → tap "Month YYYY" → swipe within `(50%,27%)~(50%,17%)` range — picker closes if swipe goes outside (do not exceed y=17%)
- clearText command does NOT exist in Maestro 2.3.0 — just use inputText (it appends; pre-empty the field by tapping a fresh placeholder)

## Test Data Created (2026-03-25)
- Profile: 민지, 본인, 여성, 양력 1998-03-15 (saved successfully)
- Compatibility test: 준호 + Sep 20, 1995 (목표: Jul 20, 1995이었으나 피커 한계로 Sep)
  - Result: 66점 (좋은 궁합), 연애 91 / 소통 41 / 가치관 66 / 생활 64

## iOS 26.2 / iPhone 17 Pro Screen Details
- Simulator window position: (791, 107) size 456x972 macOS pts
- Screen content group: (818, 187) size 402x874 macOS pts
- Scale: cliclick coords = screen_x = 818 + ios_x, screen_y = 187 + ios_y (1:1 scale)
- cliclick back button (nav bar): screen (848, 262) or use Maestro point "8%, 9%"
- Email login button: screen y=672 (ios_y=485 from screen top)

## iOS 26.2 / iPhone 17 Pro Max Screen Details (added 2026-03-25)
- Simulator window position: (662, 44) size 476x1016 macOS pts
- Simulator toolbar height: 52pt → iOS content starts at y=96
- iOS screen: 440x956pt (@3x = 1320x2868px)
- Build command: `xcodebuild ... -destination 'platform=iOS Simulator,id=3EB5BC99-4872-4A9B-B415-879B8CB0F3E2'`
- UDID: 3EB5BC99-4872-4A9B-B415-879B8CB0F3E2
- Use `--udid 3EB5BC99-4872-4A9B-B415-879B8CB0F3E2` with maestro when Pro Max is target
- "전체 운세 보기" button (홈 화면): use `tapOn: "전체 운세 보기"` (text label works!) → navigates to ReadingDetailView with score rings
- Key flow: appstore-screenshots.yaml (촬영 5화면 한번에 실행)

## SplashView Timing
- Splash shows for 1.5 seconds total (SajuApp.swift: `showSplash = false` at 1.5s)
- Text animation: 0.2s delay + 0.8s easeOut = fully visible at ~1.0s
- Screenshot window to catch splash with "달결" text: ~1.0~1.4s after xcrun simctl launch
- Command: `sleep 1.2 && xcrun simctl io <UDID> screenshot splash.png`
- EastSeaDokdo-Regular font, 160pt, "달" above "결", offset ±18 for staggered look

## Key Element Bounds (402×874 screen, confirmed 2026-03-25)
- 마이페이지 설정 row: [20,504][382,554] → tap "50%,60%"
- 마이페이지 로그아웃 row: [20,693][382,739] → tap "50%,82%"
- 홈 "자세히 보기" button: [40,350][196,402] → tap "29%,43%"
- 포인트 "충전" button: accessible via `tapOn: "충전"` (text label works)
- 이메일 로그인 "이메일" / "비밀번호" fields: accessible via text label tapOn

## Logout Dialog
- "로그아웃 하시겠습니까?" alert with 취소 / 로그아웃 buttons
- Confirm tap: `tapOn: point: "75%,55%"` (right button position in alert)

## Known Issues
- MyPageView scrolls past profile card on initial load after navigating away — requires fresh app launch to see profile card at top
- ProfileListView navigation works only when app just launched fresh (not from within scrolled MyPage)
- iOS 26.2 Passwords app is separate; strong password dialog blocks SecureField interaction
- After login, "암호를 저장하겠습니까?" dialog appears — dismiss with `tapOn: "지금 안 함"`

**Why:** Saved to avoid re-discovering all these details on each session.
**How to apply:** Use test account for login flows. Use coordinate-based tap for navigation. For MyPage profile card, ensure app is freshly launched.
