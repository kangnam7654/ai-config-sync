# Researcher Agent Memory

## Subscription-Based LLM Auth Landscape (researched 2026-03-11, verified source code)

Key findings — exact values from open-source repos. Full details in llm-subscription-auth.md

- **OpenAI Codex OAuth**: client_id=`app_EMoamEEZ73f0CkXaXp7hrann`, auth=`https://auth.openai.com/oauth/authorize`, token=`https://auth.openai.com/oauth/token`, redirect=`http://localhost:1455/auth/callback`, scopes=`openid profile email offline_access`, API=`https://chatgpt.com/backend-api/codex/responses`
- **Gemini CLI OAuth**: client_id=`681255809395-oo8ft2oprdrnp9e3aqf6av3hmdib135j.apps.googleusercontent.com`, secret=`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`, scopes=cloud-platform+email+profile, API=`https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent` (non-standard request envelope)
- **Google Antigravity OAuth**: client_id=`1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com`, secret=`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`, redirect=`http://localhost:51121/oauth-callback`, extra scopes: cclog+experimentsandconfigs vs Gemini CLI
- **GitHub Copilot Device Flow**: client_id=`Iv1.b507a08c87ecfe98` (official, used by VSCode/JetBrains/vim), device code at `github.com/login/device/code`, Copilot token at `api.github.com/copilot_internal/v2/token`, API=`api.githubcopilot.com/chat/completions`, header=`Copilot-Integration-Id: vscode-chat`
- **Anthropic Claude OAuth (sk-ant-oat01-)**: BLOCKED by Anthropic ~Feb 2026. Only Console API keys (sk-ant-api03-) work for third-party.

## Key Tool Reference: llm-subscription-auth.md
Full details with all endpoints, headers, token refresh flows.

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
