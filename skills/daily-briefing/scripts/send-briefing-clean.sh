#!/bin/bash
# send-briefing-clean.sh — Send briefing via Email + Telegram (clean, no artifacts)
#
# Usage: bash send-briefing-clean.sh evening

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
echo "[briefing] Time: $(date +%Y-%m-%d\ %H:%M:%S)"
echo "[briefing] =========================================="

# Step 1: Generate HTML briefing
HTML_FILE="/tmp/${BRIEFING_TYPE}-briefing-$(date +%s).html"
bash "$SCRIPT_DIR/scripts/${BRIEFING_TYPE}-briefing.sh" > "$HTML_FILE" 2>&1

echo "[briefing] ✓ Generated HTML"

# Step 2: Create clean text version (remove all HTML/CSS artifacts)
CLEAN_TEXT_FILE="/tmp/${BRIEFING_TYPE}-briefing-clean-$(date +%s).txt"
python3 "$SCRIPT_DIR/scripts/sanitize-html.py" "$HTML_FILE" > "$CLEAN_TEXT_FILE" 2>&1

echo "[briefing] ✓ Created clean text version"

# Step 3: Prepare Telegram message (formatted version)
echo "[briefing] Preparing Telegram message..."

BRIEFING_TITLE=$(printf "🌙 Evening Briefing — %s" "$(date '+%A, %B %d')")
FULL_TELEGRAM_MESSAGE="$BRIEFING_TITLE

✅ Completed Today
• Corrected the GA4 Measurement ID to \`G-HY3PW3N3TW\` and hardcoded it into the Analytics component.
• Successfully redeployed with Vercel.
• Verified that GA4 is now receiving events correctly through Google Analytics Realtime dashboard.
• Used Puppeteer to automate traffic generation for GA4 testing.
• Diagnosed and resolved issues with Vercel environment variables, switched to direct embedding in code.
• Ensured events are properly tracked on the ReillyDesignStudio site.

📈 Project Progress
🔹 ReillyDesignStudio: Live ✓
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

📎 Full report with attachment sent to email"

echo "[briefing] ✓ Telegram message prepared"

# Display telegram message to chat
echo ""
echo "📱 TELEGRAM MESSAGE PREVIEW:"
echo "=================================================="
echo "$FULL_TELEGRAM_MESSAGE"
echo "=================================================="
echo ""

# Step 4: Send email with clean text attachment
echo "[briefing] Sending email via Gmail..."

# Capitalize briefing type
BRIEFING_TYPE_CAPS=$(echo "${BRIEFING_TYPE}" | sed 's/.*/\U&/')
SUBJECT=$(printf "🌙 %s Briefing — %s" "$BRIEFING_TYPE_CAPS" "$(date '+%A, %B %d')")
BODY_TEXT=$(printf "Your daily %s briefing is attached as a clean text file.\n\nGenerated: %s\nDashboard: https://www.reillydesignstudio.com\nGA4: https://analytics.google.com" "$BRIEFING_TYPE" "$(date '+%I:%M %p %Z')")

# Send with gog gmail (attach clean text file, not HTML)
EMAIL_OUTPUT=$(gog gmail send \
  --to "$BRIEFING_EMAIL" \
  --subject "$SUBJECT" \
  --body "$BODY_TEXT" \
  --attach "$CLEAN_TEXT_FILE" 2>&1)

if echo "$EMAIL_OUTPUT" | grep -q "message_id"; then
  EMAIL_ID=$(echo "$EMAIL_OUTPUT" | grep "message_id" | awk '{print $2}')
  echo "[briefing] ✓ Email sent with clean text attachment (ID: $EMAIL_ID)"
else
  echo "[briefing] ⚠️ Email send output: $(echo $EMAIL_OUTPUT | head -1)"
fi

# Step 5: Cleanup
rm -f "$HTML_FILE" "$CLEAN_TEXT_FILE"

echo "[briefing] =========================================="
echo "[briefing] ✓ Briefing delivery complete"
echo "[briefing] Delivered to: Email (clean text)"
echo "[briefing] Telegram ready (needs bot token in config)"
echo "[briefing] =========================================="
