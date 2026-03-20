## Simulator Session Report

### Environment
- Device: iPhone 17 Pro Max (3EB5BC99-4872-4A9B-B415-879B8CB0F3E2)
- iOS Version: 26.2
- Maestro Version: 2.3.0

### Actions Performed
1. Verified xcrun simctl availability -- SUCCESS
2. Installed Maestro 2.3.0 -- SUCCESS
3. Configured Java runtime (OpenJDK 25.0.2 via Homebrew) -- SUCCESS
4. Identified booted simulator (iPhone 17 Pro Max) -- SUCCESS
5. Created Maestro login flow (login-submit.yaml) -- SUCCESS
6. Captured pre-test screenshot -- SUCCESS
7. Executed Maestro test on device 3EB5BC99-4872-4A9B-B415-879B8CB0F3E2 -- FAILED (app not installed)
8. Captured post-test screenshot -- SUCCESS

### Maestro Flow Results
- Flow: maestro/login-submit.yaml
- Status: FAILED
- Failure Reason: `com.example.app` is not installed on the simulator. The `launchApp` step could not find the app bundle. To resolve, install the .app or .ipa file first using `xcrun simctl install <UDID> <path-to-app>`, then re-run the test.

### Flow File
```yaml
appId: com.example.app
---
- launchApp
- tapOn: "Email"
- inputText: "user@example.com"
- tapOn: "Password"
- inputText: "password123"
- tapOn: "Submit"
- assertVisible: "Welcome"
```

### Screenshots
- screenshots/01-before-test.png -- Simulator state before test (app was on home/other screen)
- screenshots/02-after-test.png -- Simulator state after test attempt
- screenshots/03-maestro-failure-screenshot.png -- Maestro's captured failure screenshot

### Issues Found
- `com.example.app` is not installed on the simulator. The Maestro flow file is valid and ready to use once the app is installed. Install command: `xcrun simctl install 3EB5BC99-4872-4A9B-B415-879B8CB0F3E2 /path/to/YourApp.app`
