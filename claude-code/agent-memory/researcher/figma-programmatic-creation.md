---
name: Figma Programmatic Design Creation Landscape
description: Research on tools/APIs to create editable Figma frames/nodes programmatically from outside Figma (CLI, MCP, API) — March 2026, updated 2026-03-19 with full MCP comparison
type: reference
---

# Figma Programmatic Creation — Key Findings (2026-03-14)

## Verdict on Each Approach

### 1. Figma REST API — CANNOT CREATE NODES
- The REST API is fundamentally **read-only** for design content.
- POST/PUT endpoints exist ONLY for: comments, dev resources, variables (design tokens), webhooks.
- No endpoints exist for creating frames, rectangles, text, or any visual design elements.
- 2024-2025 changelog: zero additions of node-creation endpoints.

### 2. Figma Plugin API — WRITE-CAPABLE, BUT REQUIRES FIGMA APP OPEN
- The Plugin API (runs inside Figma) has full read/write to document.
- Cannot run headlessly — must have Figma Desktop open with a file loaded.
- All community MCP "write" servers use the Plugin API as the underlying mechanism.

### 3. Figma CDP (Chrome DevTools Protocol) — BLOCKED IN FIGMA 126+
- **figma-use** (github.com/dannote/figma-use): CLI with 100+ commands via CDP.
  - `npm install -g figma-use`
  - Start: `open -a Figma --args --remote-debugging-port=9222` (pre-v126)
  - Figma 126+ (released Feb 2026) **blocked** `--remote-debugging-port`.
  - Workaround: `figma-use daemon start --pipe` (uses stdio pipes instead)
  - Current status: 495 stars, 310 commits, workaround exists but fragile
  - JSX syntax for creating a 393×852 frame:
    ```tsx
    <Frame style={{ w: 393, h: 852, bg: '#FFFFFF', p: 24, gap: 16, flex: 'col' }}>
      <Rectangle style={{ w: '100%', h: 100, bg: '#3B82F6', rounded: 8 }} />
      <Text style={{ size: 16, color: '#000' }}>Label</Text>
    </Frame>
    ```
  - `figma-use render ./Screen.figma.tsx` — renders JSX to Figma
  - Supports: Frame, Rectangle, Ellipse, Text, Line, Star, Polygon, Vector, Group, Icon, Image

### 4. Community MCP Servers (Plugin API-backed)

#### figma-mcp-write-server (github.com/oO/figma-mcp-write-server)
- 24 tools: figma_nodes, figma_text, figma_fills, figma_strokes, figma_effects, figma_auto_layout, figma_constraints, etc.
- **Requires**: Figma Desktop open + plugin manually installed and started per session
- Pre-release (<1.0.0). Active (113 commits). MIT license.
- Mechanism: WebSocket from MCP server → Figma plugin

#### figma-console-mcp (github.com/southleft/figma-console-mcp)
- 58+ tools in local mode. Can create frames, components, manage variables.
- **Requires**: Figma Desktop + Desktop Bridge plugin via WebSocket
- Cloud Mode available (no local Node.js needed) — routes through cloud relay

#### thirdstrandstudio/mcp-figma — READ-ONLY (31 tools, all GET operations)

### 5. Official Figma MCP Server — LIMITED WRITE
- `generate_figma_design`: converts live web UI (browser URL) to Figma layers
- `generate_diagram`: Mermaid → FigJam
- **Cannot** create frames/text/rectangles from scratch via direct API
- Requires Figma Desktop + active connection

### 6. react-figma (github.com/react-figma/react-figma)
- React renderer that targets Figma's Plugin API
- Write React components → renders to Figma
- **Requires**: Figma open + plugin installed
- npm: `npm i react react-figma --save`
- Status: 1,362 commits, actively maintained

### 7. OpenPencil (openpencil.dev) — BEST HEADLESS OPTION
- Open-source AI-native design editor. Reads/writes native .fig files.
- Uses Kiwi binary codec with round-trip fidelity (copy-paste compat with Figma)
- MCP server: `bun add -g @open-pencil/mcp` — 90+ tools
- CLI: `bun add -g @open-pencil/cli` — headless inspect/export
- **Does NOT require Figma to be running** — standalone app
- GUI required for live editing via MCP (but CLI works headlessly for file ops)
- 2.3k GitHub stars. v0.9.0 released March 9, 2026.
- Status: "Active development. Not ready for production use."
- MCP Claude Code config:
  ```json
  { "mcpServers": { "openpencil-mcp": { "command": "openpencil-mcp" } } }
  ```

### 8. Pencil.dev (pencil.dev) — CODE-FIRST DESIGN TOOL
- Different product from OpenPencil. VS Code/Cursor extension + desktop app.
- Own `.pen` format — NOT .fig files
- MCP server starts automatically when Pencil app opens
- **Not headless** — requires Pencil desktop running
- Integrated with Shadcn/UI, Lunarus design systems

## Screenshot-to-Figma Tools (External APIs)
- **Codia AI** (codia.ai): Has `https://api.codia.ai/v1/open/image_to_design` endpoint for programmatic image→Figma conversion. Creates actual editable nodes.
- **html.to.design**: Plugin-based, no public API
- **image.to.design**: Plugin-based, no public API
- **Builder.io plugin**: Plugin-based only

## Decision Matrix

| Approach | Headless? | Figma Required? | Write Capable? | Stability |
|---|---|---|---|---|
| Figma REST API | Yes | No | No (read-only) | Stable |
| figma-use (CDP) | Partially | Yes (Desktop) | Yes (full) | Fragile (v126+ blocked) |
| figma-mcp-write-server | No | Yes (Desktop+plugin) | Yes (24 tools) | Pre-release |
| figma-console-mcp | No | Yes (Desktop+plugin) | Yes (58+ tools) | Beta |
| react-figma | No | Yes (Desktop+plugin) | Yes | Stable |
| OpenPencil MCP | Partially | No (own app) | Yes (90+ tools) | Pre-release |
| Codia AI API | Yes | No | Yes (via cloud) | Commercial |

## MCP Tool Comparison Matrix (2026-03-19 Full Research)

| Tool | Stars | 툴 수 | Write | rename_node | Free 계정 | 연결 방식 | Claude Code |
|---|---|---|---|---|---|---|---|
| figma-console-mcp (southleft) | 1.1k | 57-63 | YES | figma_rename_node 있음 | Yes (무료 계정 가능) | WebSocket+Plugin | 이슈있음(mcp-remote 우회) |
| cursor-talk-to-figma-mcp (grab) | 5.8k | 40+ | YES | 없음 | Yes | WebSocket+Plugin | 가능 |
| Figma-Context-MCP (GLips/Framelink) | 13.8k | 13 | NO (읽기전용) | 없음 | Yes (REST API Key) | REST API | 가능 |
| Official Figma MCP | N/A | 13 | generate_figma_design만 | 없음 | 6회/월 제한 | REST+Remote | 공식 지원 |
| figma-mcp-bridge (gethopp) | 82 | 미공개 | 미확인 | 미확인 | Yes (API 제한 우회) | WebSocket+Plugin | 가능 |
| figma-mcp-write-server (oO) | 20 | 24 | YES | 미확인 | Yes | WebSocket+Plugin | 가능 |
| claude-talk-to-figma-mcp (arinspunk) | 524 | 미확인 | YES | 미확인 | Yes | WebSocket+Plugin | 가능 |
| paper.design MCP | N/A | 21 | YES | rename_nodes 있음 | Yes (100콜/주 무료) | HTTP localhost | 가능 |

### Winner for Claude Code write+rename+free:
1st choice: **figma-console-mcp (southleft)** — 57+ tools, figma_rename_node 확인, 무료 계정 가능, Claude Code 우회법 있음
2nd choice: **cursor-talk-to-figma-mcp (grab)** — 5.8k stars, 가장 많은 커뮤니티, rename_node 없지만 나머지 완비

## Recommended Approach for iPhone Wireframe Recreation (393x852)

**Option A (Most Reliable Today)**: figma-console-mcp or figma-mcp-write-server
- Keep Figma Desktop open with a blank file → run MCP server → prompt Claude Code to create frames
- Works now, but requires Figma running

**Option B (Headless, Future-proof)**: OpenPencil MCP
- Install OpenPencil, open a .fig file → connect MCP → prompt to create 393x852 frames with UI elements → save as .fig → import to Figma
- Not production-stable yet, but the architecture is right

**Option C (Direct CLI)**: figma-use with pipe daemon
- `figma-use daemon start --pipe` → write JSX → `figma-use render Screen.figma.tsx`
- Most direct but brittle due to Figma blocking CDP in v126+
