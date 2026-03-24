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
- **Build output (custom derivedData)**: /tmp/saju-build/Build/Products/Debug-iphonesimulator/Saju.app
- **Build command**: `xcodebuild -project /Users/kangnam/projects/lunawave/ios/Saju/Saju.xcodeproj -scheme Saju -destination 'platform=iOS Simulator,id=3ED9A4F3-BFD5-4B1C-902D-0F9A1EB9ABC1' -derivedDataPath /tmp/saju-build -configuration Debug build`
- **Install**: `xcrun simctl install 3ED9A4F3-BFD5-4B1C-902D-0F9A1EB9ABC1 /tmp/saju-build/Build/Products/Debug-iphonesimulator/Saju.app`
- **Launch**: `xcrun simctl launch 3ED9A4F3-BFD5-4B1C-902D-0F9A1EB9ABC1 com.saju.Saju`
- **Simulator status as of 2026-03-24**: Booted (iPhone 17 Pro, iOS 26.2)

**Why:** Saved to avoid re-discovering bundle ID and derived data path on each session.
**How to apply:** Use UDID directly for all simctl commands; use bundle ID com.saju.Saju for launch/terminate. -derivedDataPath /tmp/saju-build keeps build artifacts in a predictable location.
