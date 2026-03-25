# Web App Verification Reference

## agent-browser CLI Setup

```bash
# Check installation
agent-browser --version

# Install Chromium (first time only)
agent-browser install

# If not installed
npm install -g agent-browser && agent-browser install
```

## Core Workflow Pattern

agent-browser is a CLI tool — execute shell commands directly instead of writing script files.

```bash
# 1. Open page
agent-browser open http://localhost:3000

# 2. Inspect elements (get refs like @e1, @e2)
agent-browser snapshot -i

# 3. Interact using refs
agent-browser click @e1
agent-browser fill @e2 "text"

# 4. Capture result
agent-browser screenshot /tmp/simulator-screenshots/result.png

# 5. Close browser
agent-browser close
```

## Navigation

```bash
agent-browser open <url>               # Navigate to URL
agent-browser open <url> --headed      # Show browser window (debug)
agent-browser back                     # Go back
agent-browser forward                  # Go forward
agent-browser reload                   # Reload page
agent-browser close                    # Close browser session
```

## Snapshot (Element Discovery)

The `snapshot` command returns an accessibility tree with deterministic refs (`@e1`, `@e2`, ...) for each element. Use refs instead of CSS/XPath selectors.

```bash
agent-browser snapshot                 # Full accessibility tree
agent-browser snapshot -i              # Interactive elements only (buttons, inputs, links)
agent-browser snapshot -c              # Compact output (less tokens)
agent-browser snapshot -d 3            # Limit depth
agent-browser snapshot -s "#main"      # Scope to CSS selector
```

## Element Interaction

```bash
# Click (use ref from snapshot)
agent-browser click @e1

# Fill input field (clears existing value first)
agent-browser fill @e2 "test@example.com"

# Type without clearing (appends)
agent-browser type @e2 "additional text"

# Press key
agent-browser press Enter
agent-browser press Control+a

# Scroll
agent-browser scroll down 500
agent-browser scroll up 300

# File upload
agent-browser upload @e1 /path/to/file.pdf

# Drag and drop
agent-browser drag @e1 @e2
```

## Semantic Locators (Alternative to Refs)

When refs are ambiguous or you need to find elements by meaning:

```bash
agent-browser find role button click --name "Submit"
agent-browser find text "로그인" click
agent-browser find label "이메일" fill "user@test.com"
agent-browser find testid "submit-btn" click
```

## Information Extraction

```bash
agent-browser get text @e1             # Element text content
agent-browser get html @e1             # innerHTML
agent-browser get value @e1            # Input field value
agent-browser get url                  # Current page URL
agent-browser get title                # Page title
```

## Screenshots

```bash
# Viewport screenshot
agent-browser screenshot /tmp/simulator-screenshots/viewport.png

# Full page screenshot
agent-browser screenshot --full /tmp/simulator-screenshots/full-page.png

# Screenshot to auto-generated path
agent-browser screenshot
```

## Waiting Strategies

```bash
# Wait for element to appear
agent-browser wait @e1

# Wait for text to appear on page
agent-browser wait --text "성공"

# Wait for URL pattern
agent-browser wait --url "**/dashboard"

# Wait for network idle
agent-browser wait --load networkidle

# Wait for specific time (ms)
agent-browser wait 2000
```

## Multi-Step Flow Verification

Example: Login flow verification

```bash
# Step 1: Navigate to login
agent-browser open http://localhost:3000/login
agent-browser wait --load networkidle
agent-browser screenshot /tmp/simulator-screenshots/step-01-login-page.png

# Step 2: Discover form elements
agent-browser snapshot -i
# Output: @e1 input "Email", @e2 input "Password", @e3 button "Sign In"

# Step 3: Fill credentials
agent-browser fill @e1 "test@example.com"
agent-browser fill @e2 "password123"
agent-browser screenshot /tmp/simulator-screenshots/step-02-credentials-filled.png

# Step 4: Submit and wait for redirect
agent-browser click @e3
agent-browser wait --url "**/dashboard"
agent-browser screenshot /tmp/simulator-screenshots/step-03-dashboard-loaded.png

# Step 5: Verify dashboard content
agent-browser snapshot -i
agent-browser get title
# Output: "Dashboard - MyApp"

agent-browser screenshot /tmp/simulator-screenshots/step-04-verification-complete.png

# Step 6: Close
agent-browser close
```

## Authentication Handling

```bash
# Cookie-based auth: set cookies
agent-browser cookies set session "session-token-here"

# Local storage
agent-browser storage local set auth_token "bearer-token-here"

# Save and restore session state
agent-browser state save /tmp/simulator-web/auth-state.json
# Later: restore
agent-browser state load /tmp/simulator-web/auth-state.json
```

## Responsive Viewport Testing

```bash
# Open with specific viewport
agent-browser open http://localhost:3000 --viewport 375x812
agent-browser screenshot /tmp/simulator-screenshots/responsive-mobile.png

agent-browser open http://localhost:3000 --viewport 768x1024
agent-browser screenshot /tmp/simulator-screenshots/responsive-tablet.png

agent-browser open http://localhost:3000 --viewport 1280x720
agent-browser screenshot /tmp/simulator-screenshots/responsive-desktop.png

agent-browser open http://localhost:3000 --viewport 1920x1080
agent-browser screenshot /tmp/simulator-screenshots/responsive-wide.png
```

## Network Monitoring

```bash
# Mock an API response
agent-browser network route "https://api.example.com/users" --body '{"users": []}'

# Block a request (e.g., analytics)
agent-browser network route "https://analytics.example.com/*" --abort
```

## Common Selectors Priority

Use element refs from `snapshot` output. When using semantic locators:

1. `agent-browser find testid "..."` — most stable
2. `agent-browser find role button --name "Submit"` — accessible role selectors
3. `agent-browser find text "Button Text"` — visible text
4. `agent-browser find label "Email"` — form labels
5. Direct ref from `agent-browser snapshot -i` — always available
