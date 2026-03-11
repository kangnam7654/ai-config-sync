# LLM Subscription Auth — Verified OAuth Parameters
> Last updated: 2026-03-11

## 1. OpenAI Codex CLI OAuth

**Source**: openai/codex (official), numman-ali/opencode-openai-codex-auth, open-hax/codex, openclaw issue #24927

### Client Credentials
- **client_id**: `app_EMoamEEZ73f0CkXaXp7hrann`
- **client_secret**: None (public PKCE client)

### Endpoints
- **Authorization URL**: `https://auth.openai.com/oauth/authorize`
- **Token URL**: `https://auth.openai.com/oauth/token`
- **Redirect URI**: `http://localhost:1455/auth/callback`

### Scopes
`openid profile email offline_access`

NOTE: `api.responses.write` scope is NOT available via this OAuth client. Only chat/completions works; /v1/responses endpoint requires platform API key.

### PKCE
- Method: S256
- Library: `@openauthjs/openauth/pkce`

### Token Refresh
- POST to `https://auth.openai.com/oauth/token`
- Body: `grant_type=refresh_token&client_id=app_EMoamEEZ73f0CkXaXp7hrann&refresh_token=<token>`
- Refresh triggered when token will expire within 5 minutes

### API Endpoint (ChatGPT subscription)
- **Base URL**: `https://chatgpt.com/backend-api/`
- **Completions/Responses**: `https://chatgpt.com/backend-api/codex/responses`
- **Headers**: `Authorization: Bearer <access_token>`, `Content-Type: application/json`

### Storage
- Tokens stored at `~/.codex/auth.json`

---

## 2. Gemini CLI OAuth

**Source**: google-gemini/gemini-cli — packages/core/src/code_assist/oauth2.ts and server.ts

### Client Credentials
- **client_id**: `681255809395-oo8ft2oprdrnp9e3aqf6av3hmdib135j.apps.googleusercontent.com`
- **client_secret**: `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`

### Endpoints
- **Authorization URL**: Standard Google OAuth — `https://accounts.google.com/o/oauth2/v2/auth` (via google-auth-library)
- **Token URL**: `https://oauth2.googleapis.com/token`
- **Redirect URI (web flow)**: `http://127.0.0.1:{dynamic_port}/oauth2callback`
- **Redirect URI (user code flow)**: `https://codeassist.google.com/authcode`
- **Userinfo**: `https://www.googleapis.com/oauth2/v2/userinfo`

### Scopes
```
https://www.googleapis.com/auth/cloud-platform
https://www.googleapis.com/auth/userinfo.email
https://www.googleapis.com/auth/userinfo.profile
```

### PKCE
- Method: S256
- Access type: `offline`
- Prompt: `consent`

### API Endpoint (Code Assist / subscription)
- **Base URL**: `https://cloudcode-pa.googleapis.com`
- **API version**: `v1internal`
- **Full base**: `https://cloudcode-pa.googleapis.com/v1internal`
- **Streaming**: `https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse`
- **Non-streaming**: `https://cloudcode-pa.googleapis.com/v1internal:generateContent`
- **Headers**: `Content-Type: application/json`, `Authorization: Bearer <access_token>` (via google-auth-library)

### Request Format (differs from public API!)
```json
{
  "model": "...",
  "project": "...",
  "request": { "contents": [...] }
}
```
NOT the standard `GenerateContentRequest` format.

### Quota
- Free tier: 60 req/min, 1000 req/day
- Gemini Pro/Ultra: higher quotas

### Token Refresh
- Handled automatically by `google-auth-library` via refresh token
- Cached locally (encrypted storage)

---

## 3. Google Antigravity OAuth (opencode-antigravity-auth)

**Source**: NoeFabris/opencode-antigravity-auth — src/constants.ts, src/antigravity/oauth.ts

### Client Credentials
- **client_id**: `1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com`
- **client_secret**: `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`

### Endpoints
- **Authorization URL**: `https://accounts.google.com/o/oauth2/v2/auth`
- **Token URL**: `https://oauth2.googleapis.com/token`
- **Redirect URI**: `http://localhost:51121/oauth-callback`
- **Userinfo**: `https://www.googleapis.com/oauth2/v1/userinfo?alt=json`

### Scopes
```
https://www.googleapis.com/auth/cloud-platform
https://www.googleapis.com/auth/userinfo.email
https://www.googleapis.com/auth/userinfo.profile
https://www.googleapis.com/auth/cclog
https://www.googleapis.com/auth/experimentsandconfigs
```
(2 extra scopes vs Gemini CLI: cclog + experimentsandconfigs)

### PKCE
- Method: S256
- Access type: `offline`
- Prompt: `consent`

### API Endpoints
- **Primary (prod)**: `https://cloudcode-pa.googleapis.com`
- **Autopush**: `https://autopush-cloudcode-pa.sandbox.googleapis.com`
- **Daily sandbox**: `https://daily-cloudcode-pa.sandbox.googleapis.com`

### Required Headers
```
User-Agent: <platform-specific>
X-Goog-Api-Client: <client metadata>
Client-Metadata: <platform info>
Authorization: Bearer <access_token>
x-goog-user-project: <project_id>
```

### Token Refresh
- `refreshAccessToken()` function
- Refresh token stored in structured format via `parseRefreshParts()` / `formatRefreshParts()`

---

## 4. GitHub Copilot Device Flow

**Source**: jmdaly/llm-github-copilot, Alorse/copilot-to-api, cavanaug/opencode-copilot-vscode, VSCodium discussion #1487, blog.xshoji.com

### Client Credentials
- **client_id**: `Iv1.b507a08c87ecfe98` (official GitHub Copilot Plugin app — same client ID used by VSCode, JetBrains, copilot.vim, copilot.el, and third-party tools)
- NOTE: `01ab8ac9400c4e429b23` appears in some older community guides but `Iv1.b507a08c87ecfe98` is the primary confirmed client_id per xshoji blog and multiple open-source implementations

### Device Flow Endpoints
1. **Request device code**:
   - POST `https://github.com/login/device/code`
   - Body: `client_id=Iv1.b507a08c87ecfe98&scope=read:user`
   - Response: `device_code`, `user_code`, `verification_uri`, `expires_in`, `interval`

2. **Poll for access token**:
   - POST `https://github.com/login/oauth/access_token`
   - Body: `client_id=Iv1.b507a08c87ecfe98&device_code=<code>&grant_type=urn:ietf:params:oauth:grant-type:device_code`
   - Response: `access_token` (format: `gho_xxx`)

3. **Exchange for Copilot token**:
   - GET `https://api.github.com/copilot_internal/v2/token`
   - Header: `Authorization: token <github_access_token>`
   - Response: short-lived Copilot token (~25-30 min expiry)

### API Endpoint
- **Chat completions**: `https://api.githubcopilot.com/chat/completions`
- **Models**: `https://api.githubcopilot.com/models`
- (deprecated: `copilot-proxy.githubusercontent.com` — migrated to api.githubcopilot.com Feb 2024)

### Required Headers for API Calls
```
Authorization: Bearer <copilot_token>
Content-Type: application/json
Copilot-Integration-Id: vscode-chat
editor-version: vscode/1.85.1
editor-plugin-version: copilot/1.155.0
user-agent: <any>
```

### Token Storage
- GitHub token: `~/.local/share/copilot-api/github_token` (0o600 permissions)
- Copilot token: in-memory only, auto-refreshed before expiry

### Notes
- GitHub does NOT offer a public API for Copilot Chat — all implementations are reverse-engineered
- Account type routing: individual/business/enterprise use different header sets
- Excessive automated use may trigger GitHub's abuse detection
