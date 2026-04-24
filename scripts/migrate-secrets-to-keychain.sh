#!/bin/bash
# migrate-secrets-to-keychain.sh — One-time migration of .env secrets to macOS Keychain
#
# Run once: bash scripts/migrate-secrets-to-keychain.sh
# After migration, use scripts/load-secrets-from-keychain.sh to populate env at session start.

OPENCLAW_ENV="$HOME/.openclaw/.env"
WORKSPACE_ENV="$HOME/.openclaw/workspace/.env"

_lookup() {
  local key="$1"
  local val
  # Check ~/.openclaw/.env first, then workspace/.env
  val=$(grep "^${key}=" "$OPENCLAW_ENV" 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'" || true)
  if [ -z "$val" ]; then
    val=$(grep "^${key}=" "$WORKSPACE_ENV" 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'" || true)
  fi
  echo "$val"
}

_store() {
  local service="$1" key="$2"
  local value
  value=$(_lookup "$key")
  if [ -z "$value" ]; then
    echo "⚠️  $key not found in either .env — skipping"
    return
  fi
  security delete-generic-password -s "$service" -a "openclaw" 2>/dev/null || true
  security add-generic-password -s "$service" -a "openclaw" -w "$value" 2>/dev/null && \
    echo "✅ $key → Keychain ($service)" || \
    echo "❌ Failed to store $key (check Keychain access)"
}

echo "Migrating secrets to macOS Keychain..."
echo ""

_store "OpenclawAnthropic"         "ANTHROPIC_API_KEY"
_store "OpenclawOpenRouter"        "OPENROUTER_API_KEY"
_store "OpenclawBrave"             "BRAVE_API_KEY"
_store "OpenclawCloudflare"        "CLOUDFLARE_TOKEN"
_store "OpenclawCloudflareAccount" "CLOUDFLARE_ACCOUNT_ID"
_store "OpenclawHuggingFace"       "HF_TOKEN"
_store "OpenclawGemini"            "GEMINI_API_KEY"

echo ""
echo "Done. Run 'bash scripts/load-secrets-from-keychain.sh' to verify."
