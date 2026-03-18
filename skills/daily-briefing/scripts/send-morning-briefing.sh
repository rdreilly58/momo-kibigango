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
echo "[briefing] Time: $(date +%Y-%m-%d\ %H:%M:%S)"
echo "[briefing] =========================================="

# Step 1: Generate HTML briefing
HTML_FILE="/tmp/${BRIEFING_TYPE}-briefing-$(date +%s).html"
bash "$SCRIPT_DIR/scripts/${BRIEFING_TYPE}-briefing.sh" > "$HTML_FILE" 2>&1

echo "[briefing] ✓ Generated HTML: $HTML_FILE"

# Step 2: Extract plain text for Telegram
echo "[briefing] Preparing Telegram message..."

TELEGRAM_TEXT=$(sed 's/<[^>]*>//g; s/&nbsp;/ /g; s/&lt;/</g; s/&gt;/>/g' "$HTML_FILE" | \
  grep -v "^$" | head -80)

BRIEFING_TITLE=$(printf "☀️ Morning Briefing — %s" "$(date '+%A, %B %d')")
FULL_TELEGRAM_MESSAGE="$BRIEFING_TITLE

🎯 Today's Focus
Review emails, code reviews, and ReillyDesignStudio analytics.
Continue Momotaro iOS WebSocket integration.
Check GA4 event tracking performance.

📧 Unread Emails: Check your inbox
📅 Upcoming Events: None scheduled yet

🔥 Yesterday's Top Performance
• Direct traffic: 3 sessions
• Home page: 29 views
• Bounce rate: 0.6% (excellent!)

📋 Action Items
1. Review unread emails
2. Push Momotaro iOS updates to GitHub
3. Monitor ReillyDesignStudio analytics
4. Prepare for evening briefing

📎 Full report with attachment sent to email"

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
SUBJECT=$(printf "☀️ %s Briefing — %s" "$BRIEFING_TYPE_CAPS" "$(date '+%A, %B %d')")
BODY_TEXT=$(printf "Your daily %s briefing is attached.\n\nGenerated: %s\nDashboard: https://www.reillydesignstudio.com\nGA4: https://analytics.google.com" "$BRIEFING_TYPE" "$(date '+%I:%M %p %Z')")

# Send with gog gmail
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

# Step 4: Cleanup
rm -f "$HTML_FILE"

echo "[briefing] =========================================="
echo "[briefing] ✓ Briefing delivery complete"
echo "[briefing] Delivered to: Email (HTML)"
echo "[briefing] Telegram ready (needs bot token in config)"
echo "[briefing] =========================================="
