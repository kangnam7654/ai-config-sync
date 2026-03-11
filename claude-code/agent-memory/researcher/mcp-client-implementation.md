# MCP Client Implementation Research
> Researched: 2026-03-11

## Official SDK

Package: `@modelcontextprotocol/sdk`
Version: 1.27.1 (as of 2026-03-11)
Install: `npm install @modelcontextprotocol/sdk zod`
v2 status: pre-alpha, Q1 2026 target. v1.x stays supported 6mo after v2 ships.

Tier 1 SDKs: TypeScript, Python, C#, Go
Tier 2: Java, Rust
Tier 3: Swift, Ruby, PHP, Kotlin

## Transport Import Paths (v1.x)

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
```

## Config Format (claude_desktop_config.json)

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"],
      "env": { "API_KEY": "..." }
    },
    "remote-server": {
      "url": "https://example.com/mcp",
      "headers": { "Authorization": "Bearer token" }
    }
  }
}
```

macOS path: ~/Library/Application Support/Claude/claude_desktop_config.json
Windows path: %APPDATA%\Claude\claude_desktop_config.json

## Multi-Server Pattern (critical for desktop apps)

Maintain 1 Client instance per server. Aggregate tools with server prefix to avoid collisions.

## Tool Calling Error Rates by Provider (Mastra research)
- Anthropic Claude: near 100% accuracy
- OpenAI models: ~73% before fix, 100% after embedding constraints in descriptions
- Gemini: ~73% before, ~97% after
- DeepSeek: ~60% before, ~87% after

Fix: embed schema constraints (format, pattern, min/max) directly in property descriptions.
