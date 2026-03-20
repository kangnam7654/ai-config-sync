# Maestro Login Flow - Execution Report

## Date
2026-03-20

## Flow File
`login_flow.yaml`

## App ID
`com.example.app`

## Target Device
iPhone 17 Pro Max - iOS 26.2 (Simulator, 3EB5BC99-4872-4A9B-B415-879B8CB0F3E2)

## Flow Steps
1. Launch app (`com.example.app`)
2. Wait for animation to end
3. Tap email field (by accessibility id or text matching)
4. Input email: `test@example.com`
5. Tap password field (by accessibility id or text matching)
6. Input password: `password123`
7. Tap Submit button (by text matching)

## Execution Result
**FAILED** at step 1 (Launch app)

### Failure Reason
`Unable to launch app com.example.app` - The app is not installed on the simulator. This is expected since `com.example.app` is a placeholder app ID.

## Prerequisites for Successful Run
1. The app with bundle ID `com.example.app` must be installed on the simulator
2. The app must have email/password fields identifiable by accessibility id (`email`, `password`) or by label text
3. The app must have a "Submit" button

## Debug Output
Maestro debug artifacts (logs, screenshots, command traces) are saved in:
`./maestro-debug/`

## How to Run
```bash
export PATH="/opt/homebrew/opt/openjdk/bin:$PATH":"$HOME/.maestro/bin"
maestro test login_flow.yaml
```

## Notes
- Maestro CLI was freshly installed (requires Java runtime)
- Java: OpenJDK 25.0.2 (Homebrew)
- To use with a real app, replace `com.example.app` with the actual bundle ID
- Adjust email/password field selectors to match the actual app's UI hierarchy
- Test credentials (`test@example.com` / `password123`) should be replaced with valid credentials
