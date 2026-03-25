#!/bin/bash
# Example: Discovering buttons, links, and inputs on a page

# Navigate to page and wait for it to fully load
agent-browser open http://localhost:5173
agent-browser wait --load networkidle

# Discover all interactive elements (buttons, inputs, links)
echo "=== Interactive Elements ==="
agent-browser snapshot -i
# Output example:
#   @e1 link "Home"
#   @e2 link "About"
#   @e3 input "Search"
#   @e4 button "Submit"
#   @e5 input "Email"

# Full accessibility tree (more detail, more tokens)
echo ""
echo "=== Full Accessibility Tree ==="
agent-browser snapshot -c
# Compact output with all elements

# Scoped discovery (only within a specific section)
echo ""
echo "=== Scoped to #main ==="
agent-browser snapshot -s "#main" -i

# Take screenshot for visual reference
agent-browser screenshot /tmp/page_discovery.png
echo ""
echo "Screenshot saved to /tmp/page_discovery.png"

# Close browser
agent-browser close
