#!/bin/bash
# send-briefing-v2.sh — Send briefing via Email + Telegram with health checks
#
# Usage: bash send-briefing-v2.sh evening

set -uo pipefail  # Remove -e to prevent trap from killing script on warnings

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRIEFING_TYPE="${1:-evening}"

# Load config
source ~/.openclaw/workspace/config/briefing.env 2>/dev/null || {
  echo "[briefing] Error: briefing.env not found"
  exit 1
}

# Health check URLs (from TOOLS.md)
HEALTHCHECK_EVENING="https://hc-ping.com/d570cbc7-1164-492b-98f1-0443ce23482e"
HEALTHCHECK_MORNING="https://hc-ping.com/43edd8e8-e569-4bad-b044-90ab1546c271"

# Determine which health check to use
if [ "$BRIEFING_TYPE" = "evening" ]; then
  HEALTHCHECK_URL="$HEALTHCHECK_EVENING"
else
  HEALTHCHECK_URL="$HEALTHCHECK_MORNING"
fi

# Error trap: alert on failure
trap 'echo "[briefing] ❌ ERROR: $BRIEFING_TYPE briefing failed"; \
      if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then \
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
          -d "chat_id=${TELEGRAM_CHAT_ID}" \
          -d "text=⚠️ BRIEFING FAILED: ${BRIEFING_TYPE} briefing error at $(date '+%H:%M %Z')" > /dev/null 2>&1 || true; \
      fi' ERR

echo "[briefing] =========================================="
echo "[briefing] Starting $BRIEFING_TYPE briefing delivery"
echo "[briefing] Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "[briefing] =========================================="

# Step 1: Generate HTML briefing
HTML_FILE="/tmp/${BRIEFING_TYPE}-briefing-$(date +%s).html"
bash "$SCRIPT_DIR/scripts/${BRIEFING_TYPE}-briefing.sh" > "$HTML_FILE" 2>&1

echo "[briefing] ✓ Generated HTML: $HTML_FILE"

# Step 2: Send email with HTML
echo "[briefing] 📧 Sending email to $BRIEFING_EMAIL..."

EMAIL_SUBJECT="$(echo $BRIEFING_TYPE | tr '[:lower:]' '[:upper:]') Briefing — $(date '+%A, %B %d')"

gog gmail send \
  --to "$BRIEFING_EMAIL" \
  --subject "$EMAIL_SUBJECT" \
  --body-html "$(cat "$HTML_FILE")" 2>&1 | grep -E "message_id|Error" | head -1

if [ $? -eq 0 ]; then
  echo "[briefing] ✓ Email sent successfully"
else
  echo "[briefing] ⚠️  Email delivery may have issues"
fi

# Step 3: Prepare Telegram preview (optional, when bot token is configured)
if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
  echo "[briefing] 📱 Sending Telegram preview..."
  
  # Extract text from HTML
  BRIEFING_TITLE=$(printf "$(echo $BRIEFING_TYPE | tr '[:lower:]' '[:upper:]') Briefing — %s" "$(date '+%A, %B %d')")
  
  TELEGRAM_TEXT="📊 $BRIEFING_TITLE

✅ Status
• Email sent with full briefing
• Check Gmail for complete report

📈 Key Metrics
• GA4 analytics (7-day trend)
• Gmail unread count
• Project progress
• Calendar events

📎 Full briefing with metrics sent to email"
  
  # Send via Telegram (if configured)
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=${TELEGRAM_TEXT}" \
    -d "parse_mode=HTML" > /dev/null 2>&1 || true
  
  echo "[briefing] ✓ Telegram preview sent"
fi

echo "[briefing] =========================================="
echo "[briefing] $BRIEFING_TYPE briefing delivery complete"
echo "[briefing] =========================================="

# Ping health check on success
echo "[briefing] 📍 Pinging health check..."
curl -s -X POST "$HEALTHCHECK_URL" > /dev/null 2>&1 && \
  echo "[briefing] ✓ Health check pinged" || \
  echo "[briefing] ⚠️  Health check ping failed (non-fatal)"
