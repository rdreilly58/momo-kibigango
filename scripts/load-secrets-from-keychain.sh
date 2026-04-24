#!/bin/bash
# load-secrets-from-keychain.sh — Export API keys from macOS Keychain into environment
#
# Source this file (don't execute it) to populate env vars:
#   source ~/.openclaw/workspace/scripts/load-secrets-from-keychain.sh
#
# Or call it from session-startup to regenerate .env from Keychain:
#   bash ~/.openclaw/workspace/scripts/load-secrets-from-keychain.sh --write-env

_kc() {
  security find-generic-password -s "$1" -a "openclaw" -w 2>/dev/null || echo ""
}

WRITE_ENV=false
[[ "${1:-}" == "--write-env" ]] && WRITE_ENV=true

ANTHROPIC_API_KEY=$(_kc "OpenclawAnthropic")
OPENROUTER_API_KEY=$(_kc "OpenclawOpenRouter")
LLM_API_KEY="$OPENROUTER_API_KEY"
BRAVE_API_KEY=$(_kc "OpenclawBrave")
CLOUDFLARE_TOKEN=$(_kc "OpenclawCloudflare")
CLOUDFLARE_ACCOUNT_ID=$(_kc "OpenclawCloudflareAccount")
HF_TOKEN=$(_kc "OpenclawHuggingFace")
GEMINI_API_KEY=$(_kc "OpenclawGemini")

export ANTHROPIC_API_KEY OPENROUTER_API_KEY LLM_API_KEY BRAVE_API_KEY \
       CLOUDFLARE_TOKEN CLOUDFLARE_ACCOUNT_ID HF_TOKEN GEMINI_API_KEY

if $WRITE_ENV; then
  ENV_FILE="$HOME/.openclaw/.env"
  cat > "$ENV_FILE" << EOF
# Auto-generated from macOS Keychain by load-secrets-from-keychain.sh
# Do not edit manually — re-run with --write-env to refresh
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
LLM_API_KEY=${LLM_API_KEY}
BRAVE_API_KEY=${BRAVE_API_KEY}
CLOUDFLARE_TOKEN=${CLOUDFLARE_TOKEN}
CLOUDFLARE_ACCOUNT_ID=${CLOUDFLARE_ACCOUNT_ID}
HF_TOKEN=${HF_TOKEN}
GEMINI_API_KEY=${GEMINI_API_KEY}
EOF
  echo "✅ .env refreshed from Keychain"
fi

# Verify all keys loaded
MISSING=()
[ -z "$ANTHROPIC_API_KEY" ]   && MISSING+=("ANTHROPIC_API_KEY")
[ -z "$OPENROUTER_API_KEY" ]  && MISSING+=("OPENROUTER_API_KEY")
[ -z "$BRAVE_API_KEY" ]       && MISSING+=("BRAVE_API_KEY")
[ -z "$CLOUDFLARE_TOKEN" ]    && MISSING+=("CLOUDFLARE_TOKEN")
[ -z "$HF_TOKEN" ]            && MISSING+=("HF_TOKEN")

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "⚠️  Missing from Keychain: ${MISSING[*]}"
  echo "   Run: bash ~/.openclaw/workspace/scripts/migrate-secrets-to-keychain.sh"
  exit 1
else
  echo "✅ All secrets loaded from Keychain"
fi
