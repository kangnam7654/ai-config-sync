# Researcher Agent Memory

## Subscription-Based LLM Auth Landscape (researched 2026-03-11)

Key findings on subscription vs API key auth for LLM providers:

- **Anthropic Claude OAuth (sk-ant-oat01-)** was BLOCKED by Anthropic ~Feb 2026 for third-party apps. Only Console API keys (sk-ant-api03-) work now for third-party integrations. See: llm-subscription-auth.md
- **GitHub Copilot** uses a 2-step device flow: (1) gho_xxx OAuth token via device code, (2) exchange for short-lived Copilot token. VSCode client_id required. Not officially supported for third-party use.
- **Gemini CLI OAuth** (Google accounts): free tier = 60 req/min, 1000 req/day. Mirrors Code Assist endpoints. Pro/Ultra subscriptions give higher quotas.
- **OpenAI Codex OAuth**: browser-based OAuth using ChatGPT account, routes through subscription quota not pay-per-token. Official in Cline and Codex CLI.
- **Google Antigravity OAuth**: scopes = cloud-platform, userinfo.email, cclog, experimentsandconfigs. Auth URL = accounts.google.com/o/oauth2/auth.

## Key Tool Reference: llm-subscription-auth.md
Detailed notes on each provider's auth flow and status.

## MCP Client Implementation Landscape (researched 2026-03-11)

Key findings for building MCP client in a desktop LLM app:

- **SDK**: `@modelcontextprotocol/sdk` v1.27.1 (npm). v2 in pre-alpha (Q1 2026 target). Use v1.x for production.
- **Transports**: stdio (local process), Streamable HTTP (current spec 2025-03-26), SSE (deprecated but still needed for backward compat). stdio is the most common for desktop apps.
- **Backward compat**: Try StreamableHTTPClientTransport first; catch 4xx → fall back to SSEClientTransport.
- **Config format**: `mcpServers` JSON object. Keys = server names. Fields: `command`, `args`, `env`. Claude Desktop uses `claude_desktop_config.json`.
- **Tool calling loop**: list tools → convert to LLM format → send to LLM → get tool_use block → call MCP tool → append tool_result → loop until no more tool_use.
- **Multi-provider**: MCP tools must be adapted per provider. Anthropic uses `inputSchema`, OpenAI uses `{"type":"function","function":{...}}` wrapper. Mastra found 15%→3% error rate improvement by embedding constraints in descriptions.
- **Multi-server**: 1 Client instance per server. Aggregate tools with server prefix to avoid name collisions. Route callTool to the right client instance.
- See: mcp-client-implementation.md for full details.

## Desktop Framework Landscape for LLM Clients (researched 2026-03-11)

Key findings for solo developers building LLM chat clients:

- **ChatGPT Desktop**: Electron (confirmed, ~260MB, Windows app is a Chrome wrapper)
- **Claude Desktop**: Electron (engineers previously worked on Electron; code sharing with web app)
- **Cherry Studio**: Electron + electron-builder + electron-vite (TypeScript, AGPL-3.0)
- **Jan.ai**: Tauri v2 (migrated FROM Electron; TypeScript 67% + Rust 27%)
- **LM Studio**: Electron
- **Msty**: Framework not publicly confirmed

Benchmark data (empty app, from github.com/Elanis/web-to-desktop-framework-comparison):
- Bundle size: Electron ~346MB (Win) | Tauri ~3MB | Wails ~10MB | Flutter ~26MB
- Memory (Linux): Electron ~62MB | Tauri ~15MB | Wails ~87MB
- Startup (Windows): Electron ~303ms | Tauri ~724ms | Wails ~597ms | Flutter ~104ms
- Build time: Electron ~5s | Tauri ~260s (Rust compile) | Wails ~7s

Status in 2026:
- Electron: 120k GitHub stars, 1M+ weekly npm downloads. Mature, battle-tested.
- Tauri v2: Stable since Oct 2024. 103k stars. Adoption +35% YoY. Has OAuth plugin (tauri-plugin-oauth), notifications, system tray, auto-updater, deep-link, store - all official or well-supported.
- Wails v2: Stable. v3 still in alpha (v3.0.0-alpha.59 as of Jan 2026). 32k stars.
- Flutter Desktop: Stable but desktop is secondary to mobile. No WebView paradigm - uses its own renderer (Impeller).

Recommendation: **Electron for solo devs** (JS-only, zero new language, biggest ecosystem, all LLM SDKs are JS-first). **Tauri v2 for performance-focused** (needs Rust for non-trivial backend work). See desktop-framework-comparison.md for full report.

## UI Framework Landscape for LLM Chat Desktop (researched 2026-03-11)

### Framework Status (State of JS 2025 + Stack Overflow 2025)
- **React**: 39.5% usage (State of JS), 44.7% (SO). 52.1% admiration. Still #1 by usage. LLM training data advantage.
- **Svelte 5**: #3 for 3rd year in row. 62.4% admiration — highest of any framework. Runes system stable. ~40% smaller bundles than React. TypeScript DX complaints in Svelte 5.
- **Vue 3**: 17.6% usage (SO). Pinia dominant (80% adoption). Nuxt 4 stable. Vapor Mode expected 2026.
- **Solid.js**: ~35k GitHub stars. ~1.49M weekly npm downloads. 7.6KB runtime. Signals adopted by Angular/Vue/React compiler. Small but influential. 60%+ YoY growth.
- **Ripple**: New framework in 2025 top 5. Combines React+Solid+Svelte. Too new for production LLM clients.
- **Next.js/Remix in desktop**: Use static export mode (`output: 'export'`) with Tauri. SSR features don't apply to desktop. Overkill for pure desktop apps.

### Chat UI Libraries (React-only ecosystem)
- **assistant-ui**: 8.8k GitHub stars, 50k+ monthly npm. YC-backed. Radix-style primitives. Active (released 2026-03-10). BEST CHOICE for production LLM chat.
- **@llamaindex/chat-ui**: 572 stars. Tailwind CSS. highlight.js + KaTeX. Simple integration with Vercel AI useChat.
- **nlux**: Zero external dependencies, built for streaming. Adapters for ChatGPT, LangChain, HuggingFace.
- **chatscope/chat-ui-kit-react**: Older, general chat UI kit.
- **reachat**: Open-source, React-based chat components.

### Markdown/Code Rendering for LLM Output
- **react-markdown + remark-gfm + rehype-highlight**: Standard combination. Does NOT handle streaming incomplete syntax gracefully.
- **Streamdown**: Drop-in react-markdown replacement built for AI streaming. Handles incomplete Markdown chunks.
- **llm-ui**: Purpose-built for LLMs. Streaming-aware parser. Shiki for code highlighting.
- **Shiki**: VS Code-quality syntax highlighting. Heavy (~250KB WASM). Best for client-heavy apps. react-shiki wrapper available.
- **Prism/Highlight.js**: Lighter, faster startup. Lower quality. react-syntax-highlighter wraps both.
- **KaTeX**: Fast synchronous LaTeX. ~347KB bundle. Standard choice. react-katex available.
- **MathJax**: Better feature coverage, accessibility. Slower. Avoid for streaming LLM output.

### Real-world LLM Client Stacks
- Claude Desktop: Electron + React (web codebase shared)
- LobeChat: Next.js (React) + Electron + Ant Design + Zustand
- AnythingLLM: Electron + Vite + React
- Jan.ai: Tauri v2 (migrated from Electron)
- svelte-chat-ui: Svelte + Tauri (indie project)
- Alice desktop: Svelte 5 + Tauri 2.0

### Recommendation for LLM Chat Desktop UI
**React is the pragmatic choice** due to:
1. assistant-ui library (only production-grade LLM chat UI library exists for React)
2. LLM codegen advantage — React codebase = best AI assist
3. All markdown/streaming libs target React first
4. LobeChat, AnythingLLM, Claude Desktop all use React
**Svelte+Tauri** is the performance-maximalist choice for experienced devs willing to DIY chat UI components.

## Open-Source Text-to-Video on Apple Silicon (researched 2026-03-13)

Key findings for running Wan2.1 and alternatives on M-series Macs:

### Wan2.1 MPS Support Status
- **Official support: NO.** Wan2.1 repo has no official MPS/Metal backend. GitHub Issues #14 and #208 track this — open since release, community-driven only.
- **Workaround path**: Set `PYTORCH_ENABLE_MPS_FALLBACK=1`, use `--offload_model True --t5_cpu`, replace CUDA device init with MPS in code. PR #69 by bakhti-ai exists but was not merged.
- **ComfyUI route**: Works via GGUF quantized models (city96/Wan2.1-T2V-14B-gguf). GGUF format bypasses the Float8_e4m3fn / Float16 MPS type errors that hit safetensors models. Use Euler sampler + normal scheduler.
- **Community fork**: github.com/HighDoping/Wan2.1 has Apple Silicon patches. github.com/kbadri007/Wan2mac forks Wan2GP for Apple Silicon.

### Memory Requirements
- **1.3B model**: 6-8GB VRAM on NVIDIA. On Mac, practical minimum is ~16GB unified memory (model + system overhead).
- **14B model**: 8GB VRAM with offloading on NVIDIA. On Mac, 36GB+ unified memory needed for practical use; 64GB recommended.
- **14B fp8 GGUF**: Reportedly runnable on ~24-36GB unified memory via ComfyUI.

### Generation Speed (Real-World Reports, 2025)
- **RTX 4090**: 5-second 480p clip in ~5.3 min (14B model). Reference baseline.
- **RTX 3090**: 50 min for a full-resolution Wan 2.2 fp8 generation (1280x768).
- **M1 Pro (1.3B, 8 frames, 480p)**: ~10 min (1 min/step). 24 frames = 1.5hr+ unfinished. ~2-5x slower than RTX 4090.
- **M1 Ultra 128GB (14B/2.2 fp8, 1280x768)**: 48 HOURS vs 50 min on 3090. ~57x slower — indicates missing MPS optimization, not typical ratio.
- **M4 Max 128GB (1.3B, 32-48 frames)**: Successfully generated via MPS patches. ~100GB memory used during generation.
- **GGUF on Apple Silicon (generic report)**: ~5 min for 2 seconds of low-res video. "Extremely slow."

### Key Technical Blockers on MPS
1. `Float8_e4m3fn` dtype not supported by MPS backend — blocks safetensors fp8 models
2. PyTorch MPS NDArray size limit: cannot exceed 2^32 bytes — caps resolution/frame count
3. sinusoidal embeddings and rotary encodings need float32 cast (float64 not supported on MPS)

### Alternatives That Work Better on Apple Silicon
| Model | RAM Needed | Speed on Mac | Notes |
|---|---|---|---|
| LTX-Video (via MLX) | 32GB+ (64GB rec) | 5-15 min/video | Native MLX port. M1-M4 supported. ltx-video-mac app. |
| HunyuanVideo (MLX) | 36GB+ (90GB+ ideal) | ~16 min/clip (M3 Pro 36GB, fast mode) | HunyuanVideo_MLX project. 6-step fast mode needed. |
| CogVideoX-5B | 12GB+ | ~20x slower than RTX 4090 (reported) | Works via ComfyUI MPS. Quality decent. |
| AnimateDiff | 16GB+ | Moderate | AUTOMATIC1111 v1.6+ required. Shorter clips only. |

## Figma Programmatic Design Creation (researched 2026-03-14)

Key findings on creating editable Figma frames/nodes from outside Figma:

- **Figma REST API**: Fundamentally READ-ONLY for visual nodes. No POST/PUT for frames/text/shapes. Only variables, comments, dev resources, webhooks have write endpoints.
- **figma-use** (dannote/figma-use): CDP-based CLI, 100+ commands. Figma 126+ (Feb 2026) blocked `--remote-debugging-port`. Workaround: `figma-use daemon start --pipe`. JSX render supported.
- **figma-mcp-write-server** (oO/figma-mcp-write-server): 24 MCP tools via Plugin API. Requires Figma Desktop open + plugin running. Pre-release.
- **figma-console-mcp** (southleft): 58+ tools. Plugin API + WebSocket. Figma must be open.
- **OpenPencil** (openpencil.dev): Open-source Figma alternative. Reads/writes .fig files natively. MCP server with 90+ tools. Does NOT require Figma running. `bun add -g @open-pencil/mcp`. Pre-release (v0.9.0, Mar 2026, 2.3k stars).
- **react-figma**: React renderer targeting Figma Plugin API. Requires Figma open.
- **Codia AI API**: Commercial, `api.codia.ai/v1/open/image_to_design` — converts images to editable Figma nodes.
- See: figma-programmatic-creation.md for full decision matrix.

### Practical Recommendation for Mac Users
- **Best for quick testing**: ComfyUI + Wan2.1-T2V-1.3B-GGUF (Q4/Q6). Minimum 24GB unified memory.
- **Best quality on Mac**: LTX-Video via MLX (ltx-video-mac app, 32GB+) or HunyuanVideo_MLX (36GB+).
- **Wan2.1 14B on Mac**: Only practical on M2 Ultra/M3 Ultra/M4 Max 128GB. Expect 5-20x slower than RTX 4090.
- **Do not use**: Wan2GP (deepbeepmeep) — CUDA-only, no MPS adaptation.
- **PyTorch version**: Use 2.4.1 for LTX-Video. 2.2+ required for MPS video generation generally.

## ToS Compliance: Subscription OAuth in Third-Party LLM Clients (researched 2026-03-18)

Per-provider risk assessment triggered by Feb 2026 OpenClaw mass-ban wave:
- **Anthropic Claude OAT tokens**: CLEAR VIOLATION + server-blocked since Jan 9, 2026. Use API keys only.
- **Google Gemini/Antigravity OAuth**: CLEAR VIOLATION + account bans executed Feb 12-14, 2026.
- **GitHub Copilot device flow + header spoof**: LIKELY VIOLATION, no enforcement yet.
- **OpenAI Codex OAuth**: GRAY AREA, no enforcement (OpenClaw creator joined OpenAI).
- Flat-rate subscriptions are incompatible with third-party tool usage; providers enforce to protect margins.
- See: tos-subscription-oauth-compliance.md for full per-provider ToS clause analysis.

## Figma API & Plugin Rate Limits (researched 2026-03-19)

Key findings for Figma REST API, Plugin API, and Desktop Bridge:

### REST API Rate Limits (effective Nov 17, 2025)
Rate limits depend on Plan + Seat type + API Tier:
- **Tier 1** (file content/images): View/Collab = 6/month ALL plans; Dev/Full: Starter=10/min, Pro=15/min, Org=20/min
- **Tier 2** (standard ops): View/Collab = 5/min; Dev/Full: Starter=25/min, Pro=50/min, Org=100/min
- **Tier 3** (analytics): View/Collab = 10/min; Dev/Full: Starter=50/min, Pro=100/min, Org=150/min
- Uses leaky bucket algorithm. Returns 429 + Retry-After header when exceeded.
- Retry-After can be up to DAYS (reports of 4.5 days), not minutes.

### Figma MCP Server (Official) Rate Limits
- Starter + View/Collab: 6 tool calls/MONTH
- Pro/Org Dev/Full: 200 tool calls/DAY
- Enterprise Dev/Full: 600 tool calls/DAY

### Plugin API (Local Execution)
- NO published rate limits for in-process Plugin API calls (figma.* calls run in QuickJS sandbox)
- `importVariableByKeyAsync` and other async Plugin API calls DO hit Figma's servers → subject to REST-equivalent limits
- Frozen plugin behavior is about UI thread blocking, not rate limits

### Desktop Bridge / figma-console-mcp WebSocket
- WebSocket runs locally on ports 9223-9232 — NO Figma server rate limits for pure Plugin API calls
- Timeout protection: 15s default per request
- 5-min TTL cache for variables (server-side, LRU)
- Operations that hit `importVariableByKeyAsync` or other server-backed calls still subject to API limits

### figma-mcp-bridge (gethopp)
- Explicitly designed to bypass REST API rate limits via local WebSocket
- Port: ws://localhost:1994/ws. Single plugin connection (leader-follower for multi-server).

### Pricing (2025-2026)
- Starter: Free | Professional: $16/user/month | Organization & Enterprise: annual only
- Seat upgrade (View/Collab → Dev/Full) dramatically increases limits even within same plan
- File location matters: file must be IN the paid plan workspace, not Starter workspace

See: figma-api-rate-limits.md

## Claude Code OAuth API Internals (researched 2026-03-16, binary analysis v2.1.76)

- **Endpoint**: `https://api.anthropic.com/v1/messages` (same as regular API)
- **OAuth auth headers**: `Authorization: Bearer <accessToken>` + `anthropic-beta: oauth-2025-04-20`
- **API key auth headers**: `x-api-key: <key>` (no Authorization, no oauth beta)
- **anthropic-version**: `2023-06-01` (added by @anthropic-ai/sdk automatically)
- **Other default headers**: `x-app: cli`, `User-Agent: <version string>`
- **Token refresh**: `POST https://platform.claude.com/v1/oauth/token` with `client_id: 9d1c250a-e61b-44d9-88ed-5944d1962f5e`
- **BLOCKED**: Since ~Feb 20, 2026, `api.anthropic.com` returns 401 "OAuth authentication is currently not supported" for third-party use
- **Credentials file**: `~/.claude/.credentials.json` under `claudeAiOauth` key
- See: claude-code-oauth-api.md for full binary analysis details
