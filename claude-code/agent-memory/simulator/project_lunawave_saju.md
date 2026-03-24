---
name: lunawave_saju_simulator
description: Simulator config for 달결 (Saju) iOS app — device, bundle ID, build path
type: project
---

## App: 달결 (Saju)
- **Project path**: /Users/kangnam/projects/lunawave/ios/Saju/Saju.xcodeproj
- **Scheme**: Saju
- **Bundle ID**: com.saju.Saju
- **Target device**: iPhone 17 Pro, iOS 26.2, UDID: 3ED9A4F3-BFD5-4B1C-902D-0F9A1EB9ABC1
- **Build output**: /Users/kangnam/Library/Developer/Xcode/DerivedData/Saju-hgzfzxyvtnkqwnckhroyxlibdzag/Build/Products/Debug-iphonesimulator/Saju.app
- **Build command**: `xcodebuild -project Saju.xcodeproj -scheme Saju -destination 'platform=iOS Simulator,name=iPhone 17 Pro' -configuration Debug build`

**Why:** Saved to avoid re-discovering bundle ID and derived data path on each session.
**How to apply:** Use UDID directly for all simctl commands; use bundle ID com.saju.Saju for launch/terminate.
