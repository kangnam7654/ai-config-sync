---
name: llm-provider-auth
description: "LLM 프로바이더 구독 인증 구현 가이드. Codex(ChatGPT), Gemini CLI, Antigravity, GitHub Copilot, Claude의 OAuth/인증 플로우와 API 엔드포인트를 포함. API 키 없이 구독만으로 LLM API를 사용하는 방법. \"프로바이더 연동\", \"OAuth 구현\", \"LLM 인증\", \"구독으로 API 쓰기\" 등의 요청에 트리거."
---

# LLM Provider Subscription Auth Guide

API 키 결제 없이 **기존 구독**(ChatGPT Plus/Pro, Gemini Pro, Copilot 등)으로 LLM API를 사용하는 인증 구현 가이드.

## 전체 아키텍처

```
사용자 → 브라우저 OAuth → 로컬 HTTP 서버에서 코드 수신 → 토큰 교환 → API 호출
```

공통 요소:
- PKCE (Proof Key for Code Exchange) — 시크릿 없이 안전한 코드 교환
- 로컬 HTTP 서버 — OAuth redirect 수신용 (localhost)
- 토큰 저장 — access_token + refresh_token + expires_at
- 자동 갱신 — 만료 5분 전에 refresh_token으로 갱신

---

## 1. OpenAI Codex (ChatGPT Plus/Pro)

### 인증: PKCE OAuth (시크릿 없음)

```
Auth Flow: Authorization Code + PKCE
Client ID: app_EMoamEEZ73f0CkXaXp7hrann
Auth URL:  https://auth.openai.com/oauth/authorize
Token URL: https://auth.openai.com/oauth/token
Redirect:  http://localhost:1455/auth/callback (고정 포트)
Scopes:    openid profile email offline_access
```

### 인증 흐름

```typescript
// 1. PKCE 생성
const { codeVerifier, codeChallenge } = generatePKCE()
const state = generateState()

// 2. 브라우저 열기
const authUrl = `https://auth.openai.com/oauth/authorize?` + new URLSearchParams({
  response_type: 'code',
  client_id: 'app_EMoamEEZ73f0CkXaXp7hrann',
  redirect_uri: 'http://localhost:1455/auth/callback',
  scope: 'openid profile email offline_access',
  state,
  code_challenge: codeChallenge,
  code_challenge_method: 'S256'
})
// shell.openExternal(authUrl)

// 3. 로컬 서버에서 콜백 대기 (localhost:1455)
// → ?code=xxx&state=yyy 수신

// 4. 토큰 교환
const response = await fetch('https://auth.openai.com/oauth/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    grant_type: 'authorization_code',
    client_id: 'app_EMoamEEZ73f0CkXaXp7hrann',
    code: result.code,
    redirect_uri: 'http://localhost:1455/auth/callback',
    code_verifier: codeVerifier
  })
})
// → { access_token, refresh_token, expires_in }
```

### API 호출

```
POST https://chatgpt.com/backend-api/codex/responses
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "model": "gpt-5.4",
  "instructions": "system prompt",
  "input": [{ "role": "user", "content": [{ "type": "input_text", "text": "..." }] }],
  "stream": true,
  "tools": [{ "type": "function", "name": "...", "description": "...", "parameters": {...} }]
}
```

응답: SSE 스트리밍. `response.output_text.delta` 이벤트에서 텍스트 추출.

### 토큰 갱신

```typescript
await fetch('https://auth.openai.com/oauth/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    grant_type: 'refresh_token',
    client_id: 'app_EMoamEEZ73f0CkXaXp7hrann',
    refresh_token: refreshToken
  })
})
```

---

## 2. Google Gemini CLI (Gemini Pro)

### 인증: PKCE + Client Secret

```
Auth Flow: Authorization Code + PKCE + Secret
Client ID:     681255809395-oo8ft2oprdrnp9e3aqf6av3hmdib135j.apps.googleusercontent.com
Client Secret: <REDACTED>
Auth URL:      https://accounts.google.com/o/oauth2/v2/auth
Token URL:     https://oauth2.googleapis.com/token
Redirect:      http://127.0.0.1:<동적포트>/oauth2callback
Scopes:        https://www.googleapis.com/auth/cloud-platform
               https://www.googleapis.com/auth/userinfo.email
               https://www.googleapis.com/auth/userinfo.profile
```

**주의**: Redirect URI가 **동적 포트**. 서버 시작 후 할당된 포트를 redirect_uri에 사용.

### 인증 흐름

Codex와 동일하되:
- `access_type: 'offline'` + `prompt: 'consent'` 추가 (refresh_token 받기 위해)
- 토큰 교환 시 `client_secret` 필수

### API 호출

```
POST https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "generationConfig": { "candidateCount": 1, "temperature": 1 },
  "systemInstruction": { "parts": [{ "text": "system prompt" }] },
  "contents": [{ "role": "user", "parts": [{ "text": "..." }] }],
  "tools": [{ "functionDeclarations": [{ "name": "...", "description": "...", "parameters": {...} }] }]
}
```

응답: SSE. `candidates[0].content.parts[].text` 에서 텍스트 추출.

### 토큰 갱신

```typescript
await fetch('https://oauth2.googleapis.com/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    grant_type: 'refresh_token',
    client_id: GEMINI.clientId,
    client_secret: GEMINI.clientSecret,
    refresh_token: refreshToken
  })
})
// Google은 refresh_token을 로테이션하지 않음 — 기존 것 유지
```

---

## 3. Antigravity (Gemini + Claude)

### 인증: PKCE + Client Secret (Gemini와 동일 구조, 다른 credentials)

```
Client ID:     1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com
Client Secret: <REDACTED>
Auth URL:      https://accounts.google.com/o/oauth2/v2/auth
Token URL:     https://oauth2.googleapis.com/token
Redirect:      http://localhost:51121/oauth-callback (고정 포트)
Scopes:        (Gemini와 동일) + cclog + experimentsandconfigs
```

### API 호출

Gemini와 동일한 엔드포인트 (`cloudcode-pa.googleapis.com/v1internal`)이지만 다른 quota pool.

추가 요청 필드:
```json
{
  "thinkingConfig": { "thinkingLevel": "medium" }
}
```

---

## 4. GitHub Copilot (Copilot 구독)

### 인증: Device Flow (브라우저 없는 기기용)

```
Client ID:      Iv1.b507a08c87ecfe98
Device Code:    https://github.com/login/device/code
Token URL:      https://github.com/login/oauth/access_token
Copilot Token:  https://api.github.com/copilot_internal/v2/token
Scope:          read:user
```

### 인증 흐름 (3단계)

```typescript
// 1단계: Device Code 요청
const response = await fetch('https://github.com/login/device/code', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
  body: JSON.stringify({ client_id: 'Iv1.b507a08c87ecfe98', scope: 'read:user' })
})
// → { device_code, user_code, verification_uri, interval }

// 사용자에게 user_code 보여주고 verification_uri 열기
// 사용자가 github.com/login/device에 코드 입력할 때까지 대기

// 2단계: 폴링 (interval 초 간격)
const pollResponse = await fetch('https://github.com/login/oauth/access_token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
  body: JSON.stringify({
    client_id: 'Iv1.b507a08c87ecfe98',
    device_code: deviceCode,
    grant_type: 'urn:ietf:params:oauth:grant-type:device_code'
  })
})
// error: 'authorization_pending' → 계속 폴링
// error: 'slow_down' → interval + 5초로 늦추기
// access_token 있으면 → 성공 (GitHub OAuth token)

// 3단계: GitHub token → Copilot token 교환
const copilotResponse = await fetch('https://api.github.com/copilot_internal/v2/token', {
  headers: {
    Authorization: `token ${githubToken}`,
    Accept: 'application/json',
    'Editor-Version': 'vscode/1.85.1',
    'Editor-Plugin-Version': 'copilot/1.155.0'
  }
})
// → { token: "tid=...;...", expires_at: 1234567890 }
// Copilot token은 ~25분마다 만료 → GitHub token으로 재교환
```

### API 호출

```
POST https://api.githubcopilot.com/chat/completions
Authorization: Bearer <copilot_token>
Content-Type: application/json
Editor-Version: vscode/1.85.1
Copilot-Integration-Id: vscode-chat

{
  "model": "claude-sonnet-4",
  "messages": [{ "role": "user", "content": "..." }],
  "stream": true,
  "tools": [{ "type": "function", "function": { "name": "...", "description": "...", "parameters": {...} } }]
}
```

응답: OpenAI 호환 SSE 형식. `choices[0].delta.content` 에서 텍스트 추출.

### 토큰 갱신

GitHub token은 장기 유효. Copilot token만 ~25분마다 재교환.

---

## 5. Anthropic Claude

### 방법 A: Console API Key (유료 크레딧)

```
API URL: https://api.anthropic.com/v1/messages
Header:  x-api-key: sk-ant-api03-...
         anthropic-version: 2023-06-01
```

### 방법 B: Setup Token (Pro/Max 구독, OAuth)

```
Token:  sk-ant-oat01-... (claude setup-token 명령으로 생성)
Header: Authorization: Bearer <token>
        anthropic-version: 2023-06-01
        anthropic-beta: claude-code-20250219,oauth-2025-04-20
```

**중요**: `anthropic-beta: claude-code-20250219,oauth-2025-04-20` 헤더가 없으면 401 반환.

### API 호출

```
POST https://api.anthropic.com/v1/messages
Content-Type: application/json
anthropic-version: 2023-06-01
anthropic-beta: claude-code-20250219,oauth-2025-04-20  (OAT 토큰인 경우)
Authorization: Bearer <token>  (OAT) 또는 x-api-key: <key> (API key)

{
  "model": "claude-sonnet-4-6",
  "max_tokens": 16384,
  "system": "system prompt",
  "messages": [{ "role": "user", "content": "..." }],
  "stream": true,
  "tools": [{ "name": "...", "description": "...", "input_schema": {...} }],
  "thinking": { "type": "enabled", "budget_tokens": 5000 }
}
```

Thinking 사용 시 추가 beta: `interleaved-thinking-2025-05-14`

**OAT 토큰 + 모델명 주의**: 날짜 suffix 없는 이름 사용 (`claude-sonnet-4-6`, NOT `claude-sonnet-4-6-20250514`)

### 토큰 연결 시 검증

```typescript
// 저장 전에 실제 API 호출로 유효성 확인
const headers = isOAT
  ? { 'Authorization': `Bearer ${token}`, 'anthropic-beta': 'claude-code-20250219,oauth-2025-04-20' }
  : { 'x-api-key': token }

const res = await fetch('https://api.anthropic.com/v1/messages', {
  method: 'POST',
  headers: { ...headers, 'content-type': 'application/json', 'anthropic-version': '2023-06-01' },
  body: JSON.stringify({ model: 'claude-haiku-4-5', max_tokens: 1, messages: [{ role: 'user', content: 'hi' }] })
})
// 401 → 유효하지 않은 토큰
// 200, 429 → 유효한 토큰
```

---

## 공통 유틸리티

### PKCE 생성

```typescript
import crypto from 'crypto'

function generatePKCE() {
  const codeVerifier = crypto.randomBytes(32).toString('base64url')
  const codeChallenge = crypto
    .createHash('sha256')
    .update(codeVerifier)
    .digest('base64url')
  return { codeVerifier, codeChallenge }
}

function generateState() {
  return crypto.randomBytes(16).toString('hex')
}
```

### 로컬 OAuth 서버

```typescript
import http from 'http'
import { URL } from 'url'

function waitForOAuthCallback(port: number, path: string) {
  return new Promise<{ code: string; state: string }>((resolve, reject) => {
    const server = http.createServer((req, res) => {
      const url = new URL(req.url!, `http://localhost:${port}`)
      if (url.pathname === path) {
        const code = url.searchParams.get('code')
        const state = url.searchParams.get('state')
        res.writeHead(200, { 'Content-Type': 'text/html' })
        res.end('<html><body><h2>Success! You can close this window.</h2></body></html>')
        server.close()
        if (code && state) resolve({ code, state })
        else reject(new Error('Missing code or state'))
      }
    })
    server.listen(port)
    setTimeout(() => { server.close(); reject(new Error('OAuth timeout')) }, 120000)
  })
}
```

### 토큰 저장 구조

```typescript
interface StoredToken {
  provider: string
  access_token: string
  refresh_token: string | null
  expires_at: number | null  // Unix timestamp
  metadata: Record<string, unknown> | null
}
```

---

## 요약 테이블

| Provider | Auth Flow | Client ID | API Endpoint | Auth Header |
|----------|-----------|-----------|--------------|-------------|
| Codex | PKCE | `app_EMoam...` | `chatgpt.com/backend-api/codex/responses` | `Bearer` |
| Gemini | PKCE+Secret | `681255...` | `cloudcode-pa.googleapis.com/v1internal` | `Bearer` |
| Antigravity | PKCE+Secret | `107100...` | 위와 동일 | `Bearer` |
| Copilot | Device Flow | `Iv1.b507...` | `api.githubcopilot.com/chat/completions` | `Bearer` |
| Claude (API) | API Key | - | `api.anthropic.com/v1/messages` | `x-api-key` |
| Claude (Sub) | Setup Token | - | 위와 동일 | `Bearer` + beta |

## Tool 포맷 차이

```
Codex:    { type: "function", name, description, parameters }
Gemini:   { functionDeclarations: [{ name, description, parameters }] }
Copilot:  { type: "function", function: { name, description, parameters } }
Claude:   { name, description, input_schema }
```
