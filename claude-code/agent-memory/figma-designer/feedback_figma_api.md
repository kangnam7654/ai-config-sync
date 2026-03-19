---
name: Figma Plugin API quirks
description: Discovered API requirements when creating designs via Chrome DevTools Protocol in Figma desktop app
type: feedback
---

When creating Figma designs programmatically via CDP (Chrome DevTools Protocol port 9222):

1. **DROP_SHADOW effects require `blendMode: 'NORMAL'`** — omitting blendMode causes validation error.
   **Why:** Figma's newer API versions added required fields to effect objects.
   **How to apply:** Always include `blendMode: 'NORMAL'` in DROP_SHADOW and INNER_SHADOW effect objects.

2. **`layoutSizingHorizontal = 'FILL'` can only be set AFTER appending to auto-layout parent** — setting before appendChild throws error.
   **Why:** Figma validates that FILL sizing is only valid within auto-layout containers.
   **How to apply:** Always create node, append to parent, THEN set sizing to FILL.

3. **Frame height defaults to HUG (`primaryAxisSizingMode: 'AUTO'`)** — even after calling `frame.resize(393, 852)`, if layoutMode is VERTICAL, height auto-shrinks.
   **Why:** Auto-layout overrides resize for the primary axis when sizing mode is AUTO.
   **How to apply:** After resize, explicitly set `frame.primaryAxisSizingMode = 'FIXED'` to lock height.

4. **`figma.currentPage = page` fails in dynamic-page mode** — use `await figma.setCurrentPageAsync(page)` instead.
   **Why:** Figma desktop uses dynamic-page document access mode.
   **How to apply:** Always use async page switching. Similarly use `await figma.getNodeByIdAsync()` instead of `figma.getNodeById()`.

5. **CDP WebSocket URL for Figma**: `ws://127.0.0.1:9222/devtools/page/{TARGET_ID}`. Get targets from `http://127.0.0.1:9222/json`. Match by page title.

6. **Font loading required before text creation**: Always call `await figma.loadFontAsync({family, style})` before creating text nodes, even on the same page. Required styles: Regular, Medium, Semi Bold, Bold.
