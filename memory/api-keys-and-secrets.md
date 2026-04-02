# API Keys & Credentials Reference

## Storage Location
All keys stored in `~/.openclaw/.env` (primary) and macOS Keychain (backup).

## Active Keys
| Service | Env Variable | Status | Notes |
|---------|-------------|--------|-------|
| **Brave Search** | `BRAVE_API_KEY` | ✅ Active | In ~/.openclaw/.env |
| **Gemini API** | `GEMINI_API_KEY` | ✅ Active | In ~/.openclaw/.env, paid tier |
| **Cloudflare** | `CLOUDFLARE_TOKEN` | ✅ Active | DNS management for reillydesignstudio.com |
| **Hugging Face** | `HF_API_TOKEN` | ✅ Active | Fallback embeddings |
| **Anthropic** | Auth profile | ✅ Active | anthropic:default token |

## Credential Rules
- Store actual tokens ONLY in `~/.openclaw/.env` (never in TOOLS.md or git)
- Config references use `${VAR_NAME}` syntax
- Rotate keys if exposed to git (happened March 24, 2026)
