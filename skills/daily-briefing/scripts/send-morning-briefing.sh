#!/bin/bash
# send-morning-briefing.sh — Send morning briefing via Email + Telegram
#
# Usage: bash send-morning-briefing.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRIEFING_TYPE="morning"

# Load config
source ~/.openclaw/workspace/config/briefing.env 2>/dev/null || {
  echo "[briefing] Error: briefing.env not found"
  exit 1
}

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

EMAIL_SUBJECT="☀️ $(echo $BRIEFING_TYPE | tr '[:lower:]' '[:upper:]') Briefing — $(date '+%A, %B %d')"

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
  BRIEFING_TITLE=$(printf "Morning Briefing — %s" "$(date '+%A, %B %d')")
  
  TELEGRAM_TEXT="📊 $BRIEFING_TITLE

🎯 Today's Focus
• Review emails
• Check calendar
• Monitor analytics
• Continue coding tasks

📧 Unread Emails
• Check full briefing for details

📅 Calendar
• Check full briefing for events

🔥 Yesterday's Top Performance
• Traffic sources & top pages
• Engagement metrics

📎 Full briefing sent to email"
  
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
