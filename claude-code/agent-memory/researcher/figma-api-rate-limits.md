---
name: figma-api-rate-limits
description: Figma REST API, Plugin API, Desktop Bridge (figma-console-mcp) rate limits as of Nov 2025 update. Includes plan/seat tier table and workarounds.
type: reference
---

# Figma API Rate Limits (effective Nov 17, 2025)

## REST API Rate Limit Table

| Tier | Seat Type | Starter | Professional | Organization | Enterprise |
|------|-----------|---------|--------------|--------------|------------|
| Tier 1 (file/images) | View, Collab | 6/month | 6/month | 6/month | 6/month |
| Tier 1 | Dev, Full | 10/min | 15/min | 20/min | 20/min+ |
| Tier 2 (standard) | View, Collab | 5/min | 5/min | 5/min | 5/min |
| Tier 2 | Dev, Full | 25/min | 50/min | 100/min | — |
| Tier 3 (analytics) | View, Collab | 10/min | 10/min | 10/min | 10/min |
| Tier 3 | Dev, Full | 50/min | 100/min | 150/min | — |

## Figma MCP Server (Official) — Daily Limits

| Plan | Seat | Limit |
|------|------|-------|
| Starter | Any | 6 tool calls/MONTH |
| Pro, Organization | View, Collab | 6 tool calls/MONTH |
| Pro, Organization | Dev, Full | 200 tool calls/DAY |
| Enterprise | Dev, Full | 600 tool calls/DAY |

## Algorithm
- Leaky bucket algorithm
- Returns HTTP 429 + `Retry-After` header
- Retry-After can be DAYS (real report: 396,749 seconds = ~4.5 days) for exceeded Tier 1

## Headers in 429 Response
- `X-Figma-Plan-Tier`: your plan (e.g., "pro")
- `X-Figma-Rate-Limit-Type`: limit category ("low" = treated as free/low tier)
- `Retry-After`: seconds to wait

## Plugin API (Local)
- No published rate limits for in-process Plugin API (figma.* calls in QuickJS sandbox)
- Async operations that call Figma servers (e.g., importVariableByKeyAsync) DO hit limits
- "Frozen plugin" behavior is about UI thread blocking, NOT rate limits

## Desktop Bridge WebSocket (figma-console-mcp southleft)
- Local WebSocket on ports 9223-9232
- Pure Plugin API calls via bridge: NO Figma server rate limits
- 15s timeout per request (default)
- 5-min TTL variable cache (LRU, server-side)
- Server-backed Plugin API calls still subject to REST-equivalent limits

## figma-mcp-bridge (gethopp)
- Explicitly designed to bypass REST API limits
- Port: ws://localhost:1994/ws
- Single plugin connection; leader-follower election for multi-MCP-server setups
- Streams live document data without HTTP calls to Figma API

## Pricing (2025-2026)
- Starter: Free
- Professional: $16/user/month (or ~$12/user/month annual)
- Organization: Annual only (price not published publicly, ~$45+/user/month historically)
- Enterprise: Annual only, custom pricing

## Workarounds for Rate Limiting
1. Upgrade plan (Starter → Professional → Organization)
2. Upgrade seat type (View/Collab → Dev/Full) — biggest single impact
3. Move file into paid plan workspace (file location determines rate limit bucket)
4. Use Desktop Bridge / Plugin API route instead of REST API (figma-console-mcp, figma-mcp-bridge)
5. Implement caching + batching in integration code
6. Check Retry-After header and back off accordingly

## Sources
- https://developers.figma.com/docs/rest-api/rate-limits/
- https://help.figma.com/hc/en-us/articles/34963238552855-What-if-I-m-rate-limited
- https://developers.figma.com/docs/figma-mcp-server/plans-access-and-permissions/
- https://github.com/gethopp/figma-mcp-bridge
- https://github.com/southleft/figma-console-mcp
- https://deepwiki.com/southleft/figma-console-mcp/3.5-desktop-bridge-plugin
