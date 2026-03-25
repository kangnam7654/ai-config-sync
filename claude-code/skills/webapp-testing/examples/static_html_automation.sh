#!/bin/bash
# Example: Automating interaction with static HTML files using file:// URLs

HTML_FILE="$(cd "$(dirname "$0")" && pwd)/path/to/your/file.html"
FILE_URL="file://${HTML_FILE}"

# Navigate to local HTML file
agent-browser open "$FILE_URL"

# Take screenshot
agent-browser screenshot /tmp/static_page.png

# Discover interactive elements
agent-browser snapshot -i
# Output example:
#   @e1 input "Name"
#   @e2 input "Email"
#   @e3 button "Click Me"
#   @e4 button "Submit"

# Interact with elements
agent-browser click @e3
agent-browser fill @e1 "John Doe"
agent-browser fill @e2 "john@example.com"

# Submit form
agent-browser click @e4
agent-browser wait 500

# Take final screenshot
agent-browser screenshot /tmp/after_submit.png

# Close browser
agent-browser close

echo "Static HTML automation completed!"
