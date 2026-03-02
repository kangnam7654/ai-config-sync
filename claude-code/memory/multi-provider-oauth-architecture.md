# 멀티 LLM 프로바이더 OAuth 인증 아키텍처

WhatHealth에서 검증된 패턴. iOS + Rust(Axum) 기반이지만 다른 스택에도 적용 가능.

## 핵심 개념

```
[iOS 앱] ──OAuth 흐름──→ [프로바이더 (Apple/Google/OpenAI)]
    │                              │
    │        인증코드/토큰 전달       │
    ▼                              ▼
[백엔드 서버] ←── 토큰 교환 ──→ [프로바이더 API]
    │
    ├── JWT 발급 → 앱에 반환 (앱 인증용)
    ├── OAuth 토큰 DB 저장 (LLM API 호출용)
    └── LLM 프록시 호출 시 저장된 토큰 사용
```

**원칙**: 앱은 JWT만 보관, 프로바이더 토큰은 서버만 보관.

---

## 1. DB 스키마 (사용자 테이블)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 각 프로바이더별 고유 ID (하나만 있으면 됨)
    apple_user_id TEXT UNIQUE,
    google_user_id TEXT UNIQUE,
    openai_user_id TEXT UNIQUE,
    email TEXT UNIQUE,
    -- 프로바이더별 OAuth 토큰 (LLM API 호출용)
    google_refresh_token TEXT,        -- Gemini API용
    openai_access_token TEXT,         -- Codex API용
    openai_refresh_token TEXT,        -- Codex 토큰 갱신용
    created_at TEXT DEFAULT (datetime('now'))
);
```

### 왜 refresh_token을 서버에 저장하나?
- **access_token**은 수명이 짧음 (보통 1시간)
- **refresh_token**으로 서버가 자동 갱신 → 사용자가 매번 재로그인할 필요 없음
- 앱에 토큰을 두면 탈옥/리버싱으로 노출 위험

---

## 2. 인증 흐름별 상세

### 2-A. Apple Sign-In (가장 단순)

```
[iOS] ASAuthorizationController
  → identityToken (JWT) 획득
  → POST /auth/apple { identity_token: "xxx" }

[서버]
  → Apple 공개키로 identityToken 검증
  → apple_user_id 추출
  → users 테이블에서 찾거나 새로 생성
  → 자체 JWT (access + refresh) 발급
  → 앱에 반환
```

**서버 검증 코드 핵심 (Rust)**:
```rust
// Apple의 공개키 가져오기
let jwks = reqwest::get("https://appleid.apple.com/auth/keys").await?;
// identityToken을 공개키로 검증
let token_data = decode::<Claims>(identity_token, &jwks, &validation)?;
let apple_user_id = token_data.claims.sub; // Apple 고유 사용자 ID
```

**특징**: Apple은 refresh_token이 없음. 로그인 인증용으로만 사용.

---

### 2-B. Google OAuth (Gemini API 접근용)

```
[iOS] Google OAuth 시작 (ASWebAuthenticationSession)
  → authorization_code 획득
  → POST /auth/google { code: "xxx", redirect_uri: "..." }

[서버]
  → Google에 code 교환 요청
     POST https://oauth2.googleapis.com/token
     { code, client_id, client_secret, redirect_uri, grant_type: "authorization_code" }
  → access_token + refresh_token 수신
  → Google userinfo API로 사용자 정보 조회
     GET https://www.googleapis.com/oauth2/v2/userinfo
     Authorization: Bearer {access_token}
  → users.google_refresh_token에 저장
  → 자체 JWT 발급 → 앱 반환
```

**나중에 Gemini API 호출 시**:
```rust
// 저장된 refresh_token으로 새 access_token 획득
POST https://oauth2.googleapis.com/token
{ refresh_token, client_id, client_secret, grant_type: "refresh_token" }

// 받은 access_token으로 Gemini API 호출
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent
Authorization: Bearer {새_access_token}
```

---

### 2-C. ChatGPT OAuth + PKCE (Codex API 접근용)

```
[iOS] PKCE 준비
  → code_verifier (랜덤 43~128자) 생성
  → code_challenge = Base64URL(SHA256(code_verifier))
  → ASWebAuthenticationSession으로 OpenAI authorize URL 열기
     https://auth0.openai.com/authorize?
       response_type=code&
       client_id=xxx&
       redirect_uri=xxx&
       code_challenge=xxx&
       code_challenge_method=S256&
       scope=openid profile email
  → authorization_code 획득
  → POST /auth/chatgpt/connect { code, code_verifier, redirect_uri }

[서버]
  → OpenAI에 code + code_verifier 교환
     POST https://auth0.openai.com/oauth/token
     { code, code_verifier, client_id, redirect_uri, grant_type: "authorization_code" }
  → access_token + refresh_token 수신
  → users.openai_access_token, openai_refresh_token에 저장
  → 응답 반환
```

**PKCE가 필요한 이유**:
- 모바일 앱은 client_secret을 안전하게 보관할 수 없음
- PKCE는 code_verifier/challenge로 client_secret 없이 보안 보장
- code를 가로채도 code_verifier 없이는 토큰 교환 불가

---

## 3. 자체 JWT 발급/관리

### 토큰 구조
```rust
struct Claims {
    sub: String,        // user_id
    exp: usize,         // 만료 시간
    iat: usize,         // 발급 시간
    token_type: String, // "access" 또는 "refresh"
}

// access_token: 30분 수명
// refresh_token: 7일 수명
```

### 토큰 갱신 흐름
```
[iOS] API 호출 → 401 Unauthorized 수신
  → POST /auth/refresh { refresh_token: "xxx" }
  → 새 access_token + refresh_token 수신
  → Keychain 업데이트
  → 원래 API 호출 재시도
```

### iOS 측 자동 갱신 (APIClient)
```swift
func request<T: Decodable>(...) async throws -> T {
    var response = try await rawRequest(...)

    if response.statusCode == 401 {
        // 토큰 갱신 시도
        try await authManager.refreshToken()
        // 원래 요청 재시도
        response = try await rawRequest(...)
    }

    return try decode(response)
}
```

---

## 4. LLM 프록시 패턴

### 왜 프록시?
- API 키/토큰을 앱에 노출하지 않음
- 서버에서 사용량(quota) 제어 가능
- 프로바이더 전환이 서버 로직 변경만으로 가능

### 라우팅 로직
```rust
async fn chat(user: AuthUser, body: ChatRequest, db: &Pool) -> Result<Response> {
    // 1. 사용량 체크
    check_quota(&user, &db).await?;

    // 2. 프로바이더별 분기
    let response = match body.provider {
        "openai" => {
            // 서버 환경변수의 공용 API 키 사용
            call_openai(&body, &env::var("OPENAI_API_KEY")?).await?
        }
        "gemini" => {
            // DB에서 해당 유저의 google_refresh_token 조회
            let token = get_google_access_token(&user, &db).await?;
            call_gemini(&body, &token).await?
        }
        "codex" => {
            // DB에서 해당 유저의 openai_access_token 조회
            let token = get_openai_token(&user, &db).await?;
            call_openai(&body, &token).await?
        }
    };

    // 3. 사용량 기록
    increment_usage(&user, &db).await?;

    Ok(response)
}
```

---

## 5. 사용량(Quota) 관리

```sql
CREATE TABLE usage_records (
    user_id INTEGER,
    date TEXT,              -- "2024-01-15"
    request_count INTEGER DEFAULT 0,
    bonus_count INTEGER DEFAULT 0,      -- 리워드 광고로 획득
    reward_ads_watched INTEGER DEFAULT 0,
    UNIQUE(user_id, date)
);
```

```rust
// 무료: 20회/일, Pro: 200회/일
// 보너스: 광고 1회당 +10회, 최대 5회/일
fn check_quota(user, record) -> bool {
    let limit = if user.is_pro { 200 } else { 20 };
    let total = limit + record.bonus_count;
    record.request_count < total
}
```

---

## 6. 보안 체크리스트

- [ ] 프로바이더 토큰은 **서버 DB에만** 저장 (앱 Keychain에 저장 X)
- [ ] 앱은 **자체 JWT만** Keychain에 저장
- [ ] Google/OpenAI client_secret은 **서버 환경변수**에만 존재
- [ ] PKCE 사용 (모바일 앱에서 client_secret 불필요)
- [ ] JWT에 만료 시간 설정 + 자동 갱신 로직
- [ ] 401 응답 시 토큰 갱신 → 재시도 (최대 1회)
- [ ] HTTPS 강제 (Fly.io force_https: true)

---

## 7. 다른 프로젝트에 적용 시

### 필수 구현 순서
1. **users 테이블** — 프로바이더별 ID/토큰 컬럼
2. **Apple Sign-In** — 가장 단순, iOS 필수
3. **자체 JWT** — access/refresh 토큰 발급/갱신
4. **Google OAuth** — Gemini 등 Google API 접근 필요 시
5. **OpenAI OAuth + PKCE** — ChatGPT/Codex 접근 필요 시
6. **LLM 프록시** — 서버에서 토큰 관리 + API 호출
7. **Quota** — 사용량 제한 (수익화 연결)

### 스택 무관 핵심 원칙
- OAuth 코드 교환은 **항상 서버에서** (client_secret 보호)
- 모바일은 **PKCE** 사용 (client_secret 없이 보안 확보)
- LLM API 호출은 **서버 프록시** 경유 (토큰 노출 방지 + 사용량 제어)
- 앱은 자체 JWT만 보관, 프로바이더 토큰 직접 사용 X
