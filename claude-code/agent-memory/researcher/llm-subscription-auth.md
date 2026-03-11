# LLM Subscription-Based Authentication Research Notes
Last updated: 2026-03-11

## Provider Status Summary

| Provider | Subscription Auth | Status | Notes |
|---|---|---|---|
| Anthropic Claude Pro/Max | setup-token (sk-ant-oat01-) | BLOCKED (Feb 2026) | Anthropic legal blocked 3rd-party OAuth |
| OpenAI Codex / ChatGPT Plus | Browser OAuth | WORKING | Official in Cline, Codex CLI |
| GitHub Copilot | Device flow → gho_xxx token | WORKING (unofficial for 3rd-party) | VSCode client_id needed |
| Google Gemini CLI | Google OAuth (accounts.google.com) | WORKING | 60 rpm / 1000 rpd free |
| Google Antigravity | Google OAuth (same endpoints) | WORKING | Preview; includes Claude Opus 4.6 |

## Key Projects

- **opencode-ai/opencode**: Go TUI terminal agent. Supports /connect for all providers. Auth stored in ~/.local/share/opencode/auth.json
- **OpenClaw**: Desktop/web AI assistant. Supports API keys + subscription OAuth. Has setup-token for Anthropic (with caveats).
- **CLIProxyAPI** (router-for-me): Wraps Gemini CLI, Antigravity, Codex, Claude Code as OpenAI-compatible API. Multi-account round-robin.
- **NadirClaw** (doramirdor): LLM router + cost optimizer. nadirclaw auth <provider> login for OAuth; no API key needed.
- **copilot-api** (ericc-ch): Reverse-engineered Copilot proxy exposing OpenAI+Anthropic compatible endpoints.
- **llm-github-copilot**: PyPI plugin for Simon Willison's llm tool. Device flow auth.

## GitHub Copilot Auth Flow (2-step)
1. Device flow to github.com/login/device → get gho_xxx token
2. POST to api.github.com/copilot_internal with gho_xxx → get short-lived Copilot token (30 min TTL)
3. Use Copilot token for chat completions
Note: Uses VSCode's OAuth client_id. Simulates VSCode headers.

## Anthropic OAuth Blocked (critical)
- Anthropic issued legal request ~Feb 2026 blocking sk-ant-oat01- tokens for 3rd-party tools
- OpenCode removed Claude OAuth support per Anthropic legal
- Only claude setup-token approach remains (compatibility unclear)
- Claude Pro/Max subscription cannot be used via 3rd-party integrations anymore

## Gemini CLI OAuth Scopes
- cloud-platform, userinfo.email, userinfo.profile
- Antigravity adds: cclog, experimentsandconfigs
- Auth URL: https://accounts.google.com/o/oauth2/auth
- Token URL: https://oauth2.googleapis.com/token
- Spins up local server to capture callback
