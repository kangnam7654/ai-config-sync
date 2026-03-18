---
name: ToS Compliance for Subscription OAuth in Third-Party LLM Clients
description: Per-provider ToS analysis for using subscription OAuth tokens in third-party desktop LLM clients (Codex/OpenAI, Gemini, Antigravity, GitHub Copilot, Claude/Anthropic). Includes enforcement history as of Feb-Mar 2026.
type: project
---

Researched 2026-03-18. Context: Kangnam Client desktop app uses subscription-based OAuth to access LLM providers.

**Why:** The OpenClaw mass-ban wave (Feb 2026) made this a critical risk area. Both Anthropic and Google executed sweeping account bans for this exact usage pattern.

**How to apply:** Treat Anthropic Claude (OAT tokens) and Google Gemini/Antigravity as CLEAR VIOLATIONS with active enforcement. Codex and Copilot are likely violations but no active enforcement yet. API keys remain the only safe path for commercial third-party tools.

---

## 1. Codex (ChatGPT/OpenAI)

**ToS violations:**
- OpenAI Terms of Use Section 2 (Prohibited): "access the Services through automated or non-human means, whether through a bot, script, or otherwise" (applies without API key)
- Cannot "buy, sell, or transfer API keys from, to, or with a third party" (Services Agreement)
- Consumer ToS Section 3: "may not share your Account login information... or Account credentials with anyone else"

**Internal API usage:** `chatgpt.com/backend-api/codex/responses` is an undocumented internal endpoint. No explicit prohibition found, but reverse engineering / unauthorized access clauses apply.

**Identity spoofing:** Using Codex CLI client_id `app_EMoamEEZ73f0CkXaXp7hrann` in a different app is a gray area. OpenAI has not explicitly prohibited it. Community discussion confirms no official policy exists.

**Enforcement precedent:** OpenAI notably did NOT ban OpenClaw users (unlike Anthropic/Google). The OpenClaw creator joined OpenAI as an employee. OpenAI's stance is currently more permissive.

**Risk:** GRAY AREA to LIKELY VIOLATION. No active enforcement as of Mar 2026. The legal text prohibits the pattern but OpenAI is not enforcing it. Could change anytime.

---

## 2. Gemini CLI (Google)

**ToS violations (confirmed):**
- Gemini CLI ToS: "Directly accessing the services powering Gemini CLI using third-party software, tools, or services is a violation of applicable terms and policies."
- Gemini CLI ToS additional terms Section 6: "You must not... use the Service in connection with products not provided by us."

**Internal API usage:** `cloudcode-pa.googleapis.com/v1internal` is documented internally as a Code Assist endpoint. Google explicitly prohibits third-party access to this endpoint.

**Enforcement precedent:** ACTIVE ENFORCEMENT. Feb 12-14, 2026: Google banned accounts for using OpenClaw with Gemini/Antigravity OAuth. Paid Ultra ($249/mo) subscribers were banned without warning. Google confirmed bans then offered reinstatement to users "unaware of ToS violations." Second offense = permanent ban.

**Risk:** CLEAR VIOLATION with documented enforcement. Do not use.

---

## 3. Antigravity (Google)

Same analysis as Gemini CLI above. Antigravity is Google's agentic platform on the same infrastructure. The Feb 2026 ban wave was specifically triggered by Antigravity OAuth usage with OpenClaw. The extra scopes (cclog, experimentsandconfigs) make the violation more obvious.

**Risk:** CLEAR VIOLATION with documented enforcement.

---

## 4. GitHub Copilot

**ToS state:**
- GitHub Terms for Additional Products (Copilot section): "To use GitHub Copilot in your code editor, you need to install the GitHub Copilot extension to that editor." Implies usage is intended only through official IDE extensions.
- GitHub Acceptable Use Policy: Prohibits "unauthorized access" to any account or network.
- Community consensus from GitHub discussion #178117: using `copilot_internal` endpoint outside officially supported clients "violates GitHub's Terms of Service and the Copilot license agreement" — but this is not an official GitHub statement.
- GitHub Generative AI Services Terms (effective Mar 5, 2026) replace old product-specific terms but no specific third-party client prohibition found in accessible text.

**Identity spoofing:** Sending `Editor-Version: vscode/1.85.1` and `Editor-Plugin-Version: copilot/1.155.0` while not being VS Code is header impersonation. Multiple third-party tools (LiteLLM, Continue, Goose) do this. GitHub has not enforcement-acted on this as of Mar 2026.

**Enforcement precedent:** No active enforcement found as of Mar 2026. Multiple open-source projects (LiteLLM, Continue, opencode Copilot plugin) use device flow + header spoofing openly with no bans reported.

**Risk:** LIKELY VIOLATION (header spoofing + unauthorized endpoint) but NO current enforcement. The absence of enforcement is not a green light — it may be because Copilot's volume-based pricing model tolerates it better than flat-rate subscription models.

---

## 5. Claude (Anthropic) - OAT tokens

**ToS violations (confirmed, with active enforcement):**
- Consumer Terms Section 3.7 (since Feb 2024): "Except when you are accessing our Services via an Anthropic API Key or where we otherwise explicitly permit it, to access the Services through automated or non-human means, whether through a bot, script, or otherwise."
- Claude Code Legal/Compliance (updated Feb 19, 2026): "Using OAuth tokens obtained through Claude Free, Pro, or Max accounts in any other product, tool, or service — including the Agent SDK — is not permitted and constitutes a violation of the Consumer Terms of Service."
- "Anthropic does not permit third-party developers to offer Claude.ai login or to route requests through Free, Pro, or Max plan credentials on behalf of their users."

**Enforcement timeline:**
- Jan 9, 2026: Server-side block deployed. OAT tokens return 401 "This credential is only authorized for use with Claude Code and cannot be used for other API requests."
- Feb 20, 2026: Documentation updated to explicitly state the prohibition.

**Reading from macOS Keychain:** No explicit ToS clause prohibits this at the OS level, but the resulting usage of those credentials in a third-party app is explicitly prohibited. The credential reading mechanism is irrelevant — the usage is what's banned.

**API keys:** EXPLICITLY PERMITTED. The ToS carveout "except when accessing via an Anthropic API Key" means standard API keys through Console remain the only legal path for third-party tools.

**Risk:** CLEAR VIOLATION with active server-side enforcement since Jan 9, 2026. OAT tokens are hard-blocked. The keychain-reading approach doesn't circumvent the server-side check.

---

## Summary Table

| Provider | Auth Method | ToS Clause | Enforcement | Risk Level |
|---|---|---|---|---|
| Codex/OpenAI | OAuth (Codex client_id) | ToU §2, implicit prohibition | None as of Mar 2026 | Gray Area |
| Gemini CLI | OAuth (Gemini CLI client_id) | Explicit ToS prohibition, §6 | Active (Feb 2026 ban wave) | Clear Violation |
| Antigravity | OAuth (Antigravity client_id) | Same as Gemini CLI | Active (Feb 2026 ban wave) | Clear Violation |
| GitHub Copilot | Device flow + header spoof | Implied via AUP; header impersonation | None as of Mar 2026 | Likely Violation |
| Claude OAT | Keychain token reading | Consumer ToS §3.7, explicit policy | Active (server-blocked Jan 9, 2026) | Clear Violation (blocked) |
| Claude API key | User-provided key | Explicitly PERMITTED | N/A | Safe |
