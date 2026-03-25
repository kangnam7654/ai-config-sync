---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications using agent-browser CLI. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
license: Complete terms in LICENSE.txt
---

# Web Application Testing

To test local web applications, use agent-browser CLI commands directly from the shell.

**Helper Scripts Available**:
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)

**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is absolutely necessary. These scripts can be very large and thus pollute your context window. They exist to be called directly as black-box scripts rather than ingested into your context window.

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify structure
    │         ├─ Success → Use agent-browser to open file:// URL and interact
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper to start server + run agent-browser commands
        │
        └─ Yes → Reconnaissance-then-action:
            1. agent-browser open <url>
            2. agent-browser wait --load networkidle
            3. agent-browser snapshot -i (discover interactive elements)
            4. agent-browser screenshot (capture current state)
            5. Execute actions with discovered refs
```

## Example: Using with_server.py

To start a server, run `--help` first, then use the helper:

**Single server:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- bash -c '
  agent-browser open http://localhost:5173
  agent-browser wait --load networkidle
  agent-browser screenshot /tmp/webapp-test.png
  agent-browser close
'
```

**Multiple servers (e.g., backend + frontend):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- bash -c '
    agent-browser open http://localhost:5173
    agent-browser wait --load networkidle
    agent-browser snapshot -i
    agent-browser screenshot /tmp/webapp-test.png
    agent-browser close
  '
```

## Core Commands

```bash
# Navigation
agent-browser open <url>               # Open page
agent-browser close                    # Close browser

# Element discovery
agent-browser snapshot                 # Full accessibility tree with refs
agent-browser snapshot -i              # Interactive elements only

# Interaction (use refs from snapshot)
agent-browser click @e1                # Click element
agent-browser fill @e2 "text"          # Fill input (clears first)
agent-browser type @e2 "text"          # Type without clearing
agent-browser press Enter              # Key press

# Information
agent-browser get text @e1             # Get element text
agent-browser get url                  # Current URL
agent-browser get title                # Page title

# Waiting
agent-browser wait --load networkidle  # Wait for network idle
agent-browser wait --text "Success"    # Wait for text to appear
agent-browser wait @e1                 # Wait for element

# Screenshots
agent-browser screenshot /tmp/out.png  # Viewport screenshot
agent-browser screenshot --full /tmp/out.png  # Full page
```

## Reconnaissance-Then-Action Pattern

1. **Discover elements**:
   ```bash
   agent-browser open http://localhost:5173
   agent-browser wait --load networkidle
   agent-browser snapshot -i
   agent-browser screenshot /tmp/inspect.png
   ```

2. **Identify refs** from snapshot output (e.g., `@e1 button "Login"`, `@e2 input "Email"`)

3. **Execute actions** using discovered refs:
   ```bash
   agent-browser fill @e2 "test@example.com"
   agent-browser click @e1
   ```

## Out of Scope — Do NOT Use This Skill For

- **Unit tests** (use pytest, jest, etc. directly — no browser needed)
- **API-only testing** (use curl, httpie, or requests — no UI involved)
- **Mobile app testing** (agent-browser does not support native iOS/Android apps)
- **Load/performance testing** (use k6, locust, or similar dedicated tools)

## Edge Cases

- **`networkidle` timeout**: If `agent-browser wait --load networkidle` hangs beyond 10s, try `agent-browser wait 3000` as fallback, then proceed with `agent-browser snapshot` to check current state.
- **Server fails to start**: Check stderr output from `with_server.py`. Common causes: port already in use (kill the process or change port), missing dependencies (`npm install` / `pip install -r requirements.txt`), missing `.env` file.
- **agent-browser not installed**: Run `npm install -g agent-browser && agent-browser install`. On CI, ensure agent-browser is in the global path.
- **Page shows blank/white screen**: The app may require specific env vars or a backend. Take a screenshot first with `agent-browser screenshot /tmp/debug.png`, then inspect with `agent-browser snapshot`.
- **Element not found**: Use `agent-browser wait @ref` before interacting. If the ref is stale, run `agent-browser snapshot -i` again to get fresh refs.

## Common Pitfall

- **Don't** run `agent-browser snapshot` before waiting for the page to load on dynamic apps
- **Do** run `agent-browser wait --load networkidle` before inspection

## Best Practices

- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of the scripts available in `scripts/` can help. These scripts handle common, complex workflows reliably without cluttering the context window. Use `--help` to see usage, then invoke directly.
- Always close the browser with `agent-browser close` when done
- Use `agent-browser snapshot -i` to discover interactive elements — this is more token-efficient than full snapshot
- Use `agent-browser find` semantic locators when refs from snapshot are ambiguous
- Capture screenshots after every significant interaction for verification evidence

## Reference Files

- **examples/** - Examples showing common patterns:
  - `element_discovery.sh` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.sh` - Using file:// URLs for local HTML
  - `console_logging.sh` - Monitoring browser state during automation
