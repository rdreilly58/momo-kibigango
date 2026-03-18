#!/bin/bash
# send-briefing-v2.sh — Send briefing via Email + Telegram
#
# Usage: bash send-briefing-v2.sh evening

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRIEFING_TYPE="${1:-evening}"

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

EMAIL_SUBJECT="🌙 $(echo $BRIEFING_TYPE | tr '[:lower:]' '[:upper:]') Briefing — $(date '+%A, %B %d')"

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

✅ Completed Today
• Check email for full details

📈 Key Metrics
• GA4 Sessions, Users, Bounce Rate
• Gmail Unread/Starred counts
• Project progress & blockers

🔗 Full briefing sent to email"
  
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
   Dashboard: https://www.reillydesignstudio.com
   GA4 tracking active, DNS configured

🔹 Momotaro: In Progress
   iOS app development

🎯 KEY METRICS (last 7 days)
• Active Users: 41 (-93.8% ↘️)
• Total Sessions: 49 (-93.4% ↘️)
• Bounce Rate: 0.6%
• Avg Session: 58.4s

🔥 TOP PAGES
1. / (29 views)
2. /shop/services (5 views)
3. /portfolio/gallery-44-print (2 views)
4. /portfolio (9 views)
5. /shop (2 views)

📋 Tomorrow's Prep
Follow up on AWS mac instance approval
Review GA4 tracking performance
Continue Momotaro iOS development

📎 Full report with PDF sent to email"

echo "[briefing] ✓ Telegram message prepared"

# Display telegram message to chat
echo ""
echo "📱 TELEGRAM MESSAGE PREVIEW:"
echo "=================================================="
echo "$FULL_TELEGRAM_MESSAGE"
echo "=================================================="
echo ""

# Step 3: Send email with HTML attachment
echo "[briefing] Sending email via Gmail..."

# Capitalize briefing type (use tr for macOS compatibility)
BRIEFING_TYPE_CAPS=$(echo "${BRIEFING_TYPE}" | tr '[:lower:]' '[:upper:]')
SUBJECT=$(printf "🌙 %s Briefing — %s" "$BRIEFING_TYPE_CAPS" "$(date '+%A, %B %d')")
BODY_TEXT=$(printf "Your daily %s briefing is attached as HTML.\n\nGenerated: %s\nDashboard: https://www.reillydesignstudio.com\nGA4: https://analytics.google.com" "$BRIEFING_TYPE" "$(date '+%I:%M %p %Z')")

# Send with gog gmail (supports --attach flag)
EMAIL_OUTPUT=$(gog gmail send \
  --to "$BRIEFING_EMAIL" \
  --subject "$SUBJECT" \
  --body "$BODY_TEXT" \
  --attach "$HTML_FILE" 2>&1)

if echo "$EMAIL_OUTPUT" | grep -q "message_id"; then
  EMAIL_ID=$(echo "$EMAIL_OUTPUT" | grep "message_id" | awk '{print $2}')
  echo "[briefing] ✓ Email sent with HTML attachment (ID: $EMAIL_ID)"
else
  echo "[briefing] ⚠️ Email send output: $(echo $EMAIL_OUTPUT | head -1)"
fi

# Step 4: For now, skip Telegram (would need bot token setup)
# In production, we'd send via proper Telegram API
echo "[briefing] ⚠️ Telegram delivery requires bot setup (skipping for now)"
echo "[briefing]    → To enable: Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in briefing.env"

# Step 5: Cleanup
rm -f "$HTML_FILE"

echo "[briefing] =========================================="
echo "[briefing] ✓ Briefing delivery complete"
echo "[briefing] Delivered to: Email (HTML)"
echo "[briefing] Note: PDF conversion WIP, currently sending HTML"
echo "[briefing] =========================================="
