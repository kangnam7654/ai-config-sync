---
name: GitHub Copilot API Model IDs
description: Exact model ID strings available through api.githubcopilot.com as of March 2026, with premium request multipliers and deprecation status
type: reference
---

# GitHub Copilot API Models (as of 2026-03-20)

API endpoint: `https://api.githubcopilot.com/models` — returns `.data[].id` format
Naming convention: dot notation for versions (e.g., `claude-sonnet-4.5`, `gpt-5.2`)

## Active Claude Models (Anthropic)
| Model ID | Multiplier | Status | Notes |
|---|---|---|---|
| `claude-haiku-4.5` | 0.33x | GA | |
| `claude-sonnet-4` | 1x | GA | Minor version absent — no `.0` suffix |
| `claude-sonnet-4.5` | 1x | GA | CLI default model |
| `claude-sonnet-4.6` | 1x | GA | GA Feb 17 2026; 1M token context |
| `claude-opus-4.5` | 3x | GA | |
| `claude-opus-4.6` | 3x | GA | |
| `claude-opus-4-6-fast` | 30x | Preview | Uses hyphen not dot (exception to convention) |

## Active OpenAI Models
| Model ID | Multiplier | Status | Notes |
|---|---|---|---|
| `gpt-4.1` | 0x | GA | Free tier; no premium requests consumed |
| `gpt-5-mini` | 0x | GA | Free tier |
| `gpt-5.2` | 1x | GA | |
| `gpt-5.2-codex` | 1x | GA | |
| `gpt-5.3-codex` | 1x | GA | Replacement for gpt-5.1 family |
| `gpt-5.4` | 1x | GA | |
| `gpt-5.4-mini` | 0.33x | GA | |

## Deprecated/Removed OpenAI Models
- `gpt-4o` — removed Aug 6, 2025
- `o3-mini`, `o1`, `gpt-4.5` — removed mid-2025
- `gpt-5.1`, `gpt-5.1-codex`, `gpt-5.1-codex-mini`, `gpt-5.1-codex-max` — deprecating April 1, 2026

## Active Google Gemini Models
| Model ID | Multiplier | Status | Notes |
|---|---|---|---|
| `gemini-2.5-pro` | 1x | GA | ID format inferred — medium confidence |
| `gemini-3-flash` | 0.33x | Preview | |
| `gemini-3.1-pro` | 1x | Preview | Replacement for gemini-3-pro |

## Deprecated Google Models
- `gemini-3-pro` — deprecating March 26, 2026

## Other Models
| Model ID | Provider | Multiplier | Status |
|---|---|---|---|
| `grok-code-fast-1` | xAI | 0.25x | GA; free tier |
| `raptor-mini` | Microsoft (GPT-5 mini fine-tune) | 0x | GA; free tier |
| `goldeneye` | Microsoft (GPT-5.1-Codex fine-tune) | 0x | Preview; free only |

## Key Facts
- Copilot Free plan can use: `gpt-4.1`, `gpt-5-mini`, `grok-code-fast-1`, `raptor-mini`, `goldeneye`
- Pro/Pro+/Business/Enterprise unlock all other models
- `claude-opus-4-6-fast` at 30x is extremely expensive per request
- Sources: GitHub official docs + openclaw implementation code (issues #15014 and #20091)
