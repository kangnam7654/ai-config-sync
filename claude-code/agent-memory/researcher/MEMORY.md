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
