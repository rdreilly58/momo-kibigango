#!/bin/bash
# Loads selected secrets from ~/.openclaw/.env into the user's launchd domain
# so that brew services (Grafana, Prometheus, etc.) inherit them on login.
# Idempotent: safe to run repeatedly.

ENV_FILE="$HOME/.openclaw/.env"
[ -f "$ENV_FILE" ] || { echo "[load-launchctl-env] missing $ENV_FILE"; exit 1; }

# Whitelist — only these get exported to launchd (don't leak everything)
KEYS=(
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID
  NTFY_TOPIC_URL
  NTFY_TOPIC_URL_PUBLIC
  NTFY_USER
  NTFY_PASS
  SLACK_WEBHOOK_URL
  SLACK_BOT_TOKEN
  SLACK_APP_TOKEN
)

set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
set +a

for k in "${KEYS[@]}"; do
  v="${!k}"
  [ -z "$v" ] && continue
  /bin/launchctl setenv "$k" "$v"
done

echo "[load-launchctl-env] loaded ${#KEYS[@]} keys at $(date)"
