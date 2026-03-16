---
name: Claude Code OAuth API internals
description: How Claude Code CLI uses sk-ant-oat01- OAuth tokens to call the Anthropic API - endpoint, headers, request format extracted from binary v2.1.76
type: reference
---

## Source: Binary analysis of Claude Code v2.1.76 (arm64 Mach-O)

### API Endpoint
- **Messages API**: `https://api.anthropic.com/v1/messages`
- BASE_API_URL = `https://api.anthropic.com` (hardcoded in binary as `gA8.BASE_API_URL`)

### Authentication Headers

**When OAuth (claudeai subscription) mode is active (`s8()` returns true):**
```
Authorization: Bearer <accessToken>
anthropic-beta: oauth-2025-04-20
```
The `x-api-key` header is NOT sent. `apiKey` is set to `null` in the SDK constructor.

**When API key mode is active:**
```
x-api-key: <apiKey>
```
No `Authorization` header, no `anthropic-beta: oauth-2025-04-20`.

### Full Default Headers sent on every request
```
x-app: cli
User-Agent: <vv()>   (Claude Code version string)
anthropic-version: 2023-06-01   (set by @anthropic-ai/sdk automatically)
Content-Type: application/json
```
Plus optionally: `x-claude-remote-container-id`, `x-claude-remote-session-id`, `x-client-app`, `x-anthropic-additional-protection: true`

### SDK Constructor (key code from binary)
```js
// OAuth mode: apiKey=null, authToken=accessToken
let w = {
  apiKey: s8() ? null : _ || QZ(),        // null if OAuth
  authToken: s8() ? e8()?.accessToken : undefined,  // OAuth token
  defaultHeaders: z,   // x-app, User-Agent, etc.
  maxRetries: T,
  timeout: 600000,
  dangerouslyAllowBrowser: true,
};
return new YE(w);  // YE = Anthropic SDK class
```

### How SDK sends Bearer token (from @anthropic-ai/sdk inside binary)
```js
async bearerAuth(_) {
  if (this.authToken == null) return;
  return [{ Authorization: `Bearer ${this.authToken}` }];
}
```

### The oauth-2025-04-20 beta header placement
The `anthropic-beta: oauth-2025-04-20` header is added:
1. In the `qz()` helper function used for non-SDK internal API calls (usage, profile, settings)
2. NOT automatically added to the Anthropic SDK's messages call by the SDK itself
3. For the SDK messages call, it's included in the `betas` array parameter only if `s8()` is OAuth mode AND the beta identifier is needed

The `betas` array is built by `UN(model)` function and passed as `betas: P` to `beta.messages.create()`, which converts it to `anthropic-beta` header.

### Internal OAuth API Endpoints (not the messages API)
All use `BASE_API_URL = https://api.anthropic.com`:
- `GET  /api/oauth/profile` - user profile
- `GET  /api/oauth/usage` - rate limit usage
- `GET  /api/oauth/account/settings` - account settings
- `GET  /api/oauth/claude_cli/client_data` - CLI config data
- `POST /api/oauth/claude_cli/create_api_key` - create API key
- `GET  /api/oauth/claude_cli/roles` - user roles
- `POST /api/oauth/file_upload` - file upload

### Token Refresh Endpoint
```
POST https://platform.claude.com/v1/oauth/token
Body: { grant_type: "refresh_token", refresh_token: "sk-ant-ort01-...", client_id: "9d1c250a-e61b-44d9-88ed-5944d1962f5e" }
```

### OAuth Config (hardcoded in binary as `gA8`)
```json
{
  "BASE_API_URL": "https://api.anthropic.com",
  "CONSOLE_AUTHORIZE_URL": "https://platform.claude.com/oauth/authorize",
  "CLAUDE_AI_AUTHORIZE_URL": "https://claude.ai/oauth/authorize",
  "TOKEN_URL": "https://platform.claude.com/v1/oauth/token",
  "API_KEY_URL": "https://api.anthropic.com/api/oauth/claude_cli/create_api_key",
  "CLIENT_ID": "9d1c250a-e61b-44d9-88ed-5944d1962f5e",
  "MCP_PROXY_URL": "https://mcp-proxy.anthropic.com",
  "MCP_PROXY_PATH": "/v1/mcp/{server_id}"
}
```

### Credentials File: ~/.claude/.credentials.json
```json
{
  "claudeAiOauth": {
    "accessToken": "sk-ant-oat01-...",
    "refreshToken": "sk-ant-ort01-...",
    "expiresAt": 1234567890123,
    "scopes": ["user:inference", "user:profile", "org:create_api_key", "user:sessions:claude_code", "user:mcp_servers", "user:file_upload"],
    "subscriptionType": "max",
    "rateLimitTier": "default_claude_max_20x"
  }
}
```

### Request Body (standard Messages API format)
```json
{
  "model": "claude-sonnet-4-5",
  "max_tokens": 32000,
  "system": [...],
  "messages": [...],
  "tools": [...],
  "betas": ["oauth-2025-04-20"],
  "metadata": { "user_id": "user_<hash>_account_<uuid>_session_<id>" }
}
```

### CRITICAL: Third-party use is BLOCKED since ~Feb 20, 2026
When sending `Authorization: Bearer sk-ant-oat01-...` to `api.anthropic.com/v1/messages`:
- Returns HTTP 401: `{"type":"error","error":{"type":"authentication_error","message":"OAuth authentication is currently not supported."}}`
- This is enforced server-side — the tokens only work from Claude Code CLI itself
- Anthropic uses undisclosed server-side checks to identify requests as originating from Claude Code CLI

### The Unsolved Mystery (from opencode GitHub issue #417)
A developer confirmed: after matching all headers exactly, there's still something "after the headers" (in the request body) that Anthropic checks. The maintainer declined to elaborate. Likely candidates: `user_id` metadata format, specific `betas` values, or `x-app: cli` header.
