#!/bin/bash
# Example: Monitoring browser state during automation

URL="http://localhost:5173"  # Replace with your URL

# Navigate to page
agent-browser open "$URL"
agent-browser wait --load networkidle

# Take initial snapshot to understand page state
echo "=== Page State ==="
agent-browser get title
agent-browser get url

# Discover elements and interact
agent-browser snapshot -i

# Click on navigation (example: Dashboard link)
agent-browser find text "Dashboard" click
agent-browser wait --load networkidle

# Check page state after navigation
echo ""
echo "=== After Navigation ==="
agent-browser get title
agent-browser get url

# Take screenshot for verification
agent-browser screenshot /tmp/after_navigation.png

# Close browser
agent-browser close

echo ""
echo "Monitoring completed. Screenshot saved to /tmp/after_navigation.png"
