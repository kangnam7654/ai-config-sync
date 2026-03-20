# Mobile App Verification Reference (iOS Simulator)

## Dependencies

| Tool | Install Command | Verify Command | Purpose |
|---|---|---|---|
| Xcode Command Line Tools | `xcode-select --install` | `xcrun simctl help` | Simulator control: boot, install, screenshot, URL open |
| Maestro | `curl -Ls "https://get.maestro.mobile.dev" \| bash` | `maestro --version` | UI automation: tap, scroll, type, swipe, assert |

## `xcrun simctl` Command Reference

```bash
# ─── Device Management ───

# List all devices
xcrun simctl list devices

# List available device types
xcrun simctl list devicetypes

# List available runtimes
xcrun simctl list runtimes

# List only booted devices
xcrun simctl list devices booted

# Create a new simulator
xcrun simctl create "My iPhone" "iPhone 16 Pro" "com.apple.CoreSimulator.SimRuntime.iOS-18-0"

# Boot / Shutdown
xcrun simctl boot <UDID>
xcrun simctl shutdown <UDID>
xcrun simctl shutdown all

# Erase (reset to factory — REQUIRES USER CONFIRMATION)
xcrun simctl erase <UDID>

# Delete unavailable simulators
xcrun simctl delete unavailable

# ─── App Management ───

# Install .app bundle
xcrun simctl install booted /path/to/App.app

# Uninstall app
xcrun simctl uninstall booted com.example.app

# Launch app
xcrun simctl launch booted com.example.app

# Terminate app
xcrun simctl terminate booted com.example.app

# Get app container path
xcrun simctl get_app_container booted com.example.app

# ─── Media Capture ───

# Screenshot
xcrun simctl io booted screenshot /path/to/output.png

# Video recording (terminate process to stop)
xcrun simctl io booted recordVideo /path/to/output.mp4

# ─── URLs and Deep Links ───

# Open URL in simulator browser
xcrun simctl openurl booted "https://example.com"

# Open deep link
xcrun simctl openurl booted "myapp://deeplink/path"

# ─── Push Notifications ───

# Send push notification
# payload.json: {"aps": {"alert": "Test notification", "sound": "default"}}
xcrun simctl push booted com.example.app /path/to/payload.json

# ─── Location ───

# Set GPS coordinates
xcrun simctl location booted set <lat>,<lng>

# ─── Logs ───

# Stream device logs
xcrun simctl spawn booted log stream --level debug

# Show recent crash logs
xcrun simctl spawn booted log show --predicate 'eventMessage contains "crash"' --last 1m
```

## Maestro Command Reference

```bash
# Run a single flow
maestro test path/to/flow.yaml

# Run all flows in directory
maestro test path/to/flows/

# Record flow execution as video
maestro record path/to/flow.yaml

# Interactive studio mode (create flows by interacting with the app)
maestro studio

# Check Maestro health and connectivity
maestro doctor
```

## Maestro YAML Flow Syntax

```yaml
appId: com.example.myapp
---
# ─── App Lifecycle ───
- launchApp
- clearState

# ─── Tap Actions ───
- tapOn: "Button Text"
- tapOn:
    id: "accessibility_id"
- tapOn:
    point: "50%,50%"

# ─── Text Input ───
- inputText: "Hello World"
- eraseText: 10

# ─── Scroll ───
- scrollDown
- scrollUp
- scroll:
    direction: DOWN
    duration: 500

# ─── Swipe ───
- swipe:
    direction: LEFT
    duration: 300

# ─── Assertions ───
- assertVisible: "Expected Text"
- assertNotVisible: "Hidden Text"
- assertVisible:
    id: "element_id"

# ─── Wait ───
- waitForAnimationToEnd
- extendedWaitUntil:
    visible: "Loaded Content"
    timeout: 10000

# ─── Screenshots ───
- takeScreenshot: "step_name"

# ─── Conditional Execution ───
- runFlow:
    when:
      visible: "Optional Button"
    file: optional-step.yaml

# ─── Repeat ───
- repeat:
    times: 3
    commands:
      - tapOn: "Next"
      - assertVisible: "Page"

# ─── Navigation ───
- pressKey: back
- hideKeyboard
- openLink: "myapp://screen"
```

## Maestro Flow File Naming Convention

Save flows in the project's `maestro/` directory:
- Pattern: `{feature}-{action}.yaml`
- `{action}` is the primary user action from the task description
- "로그인 후 Submit" → `login-submit.yaml`
- "장바구니에서 결제" → `cart-checkout.yaml`
- "프로필 수정" → `profile-edit.yaml`
- "회원가입 플로우" → `signup-complete.yaml`

## Push Notification Payload Templates

### Simple Alert
```json
{
  "aps": {
    "alert": "Test notification",
    "sound": "default"
  }
}
```

### Rich Notification
```json
{
  "aps": {
    "alert": {
      "title": "New Message",
      "subtitle": "From John",
      "body": "Hey, are you free tonight?"
    },
    "sound": "default",
    "badge": 1
  }
}
```

### Silent Push
```json
{
  "aps": {
    "content-available": 1
  },
  "custom-key": "custom-value"
}
```
