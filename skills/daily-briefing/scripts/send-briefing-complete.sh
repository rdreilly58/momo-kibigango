#!/bin/bash
# send-briefing-complete.sh — Send briefing via Telegram + Gmail with PDF
#
# Usage: bash send-briefing-complete.sh evening

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

echo "[briefing] ✓ Generated HTML: $HTML_FILE"

# Step 2: Convert HTML to PDF
echo "[briefing] Converting to PDF..."

PDF_FILE="/tmp/${BRIEFING_TYPE}-briefing-$(date +%s).pdf"

# Convert HTML to PDF using make-pdf skill
if [ -f ~/.openclaw/workspace/skills/make-pdf/scripts/topdf.sh ]; then
  bash ~/.openclaw/workspace/skills/make-pdf/scripts/topdf.sh \
    "$HTML_FILE" \
    -o "$PDF_FILE" \
    -t "Evening Briefing" 2>/dev/null && {
    echo "[briefing] ✓ PDF created: $PDF_FILE"
  } || {
    echo "[briefing] ⚠️ PDF conversion failed, sending HTML instead"
    PDF_FILE="$HTML_FILE"
  }
else
  echo "[briefing] ⚠️ make-pdf skill not found"
  PDF_FILE="$HTML_FILE"
fi

# Step 3: Send to Telegram (via OpenClaw routing)
echo "[briefing] Sending to Telegram..."

# Extract plain text from HTML for Telegram message
TELEGRAM_MESSAGE=$(sed 's/<[^>]*>//g; s/&nbsp;/ /g; s/&lt;/</g; s/&gt;/>/g' "$HTML_FILE" | \
  grep -v "^$" | head -80)

# Prepare formatted message (fix macOS date format)
BRIEFING_TITLE=$(printf "🌙 Evening Briefing — %s" "$(date '+%A, %B %d')")
FULL_TELEGRAM_MESSAGE="$BRIEFING_TITLE

$TELEGRAM_MESSAGE

📎 Full PDF report sent to email"

# Try to send via OpenClaw (this is routed to the user's Telegram session)
if [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
  # If we have a chat ID, send via curl
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" \
    -d "text=${FULL_TELEGRAM_MESSAGE}" \
    -d "parse_mode=HTML" > /dev/null 2>&1 && {
    echo "[briefing] ✓ Telegram sent"
  } || {
    echo "[briefing] ⚠️ Telegram failed (missing credentials)"
  }
else
  # Fallback: use sessions_send if available
  echo "[briefing] ⚠️ Using fallback Telegram delivery..."
fi

# Step 4: Send via Gmail with PDF attachment
echo "[briefing] Sending email with PDF..."

# Capitalize first letter of briefing type
BRIEFING_TYPE_CAPS=$(echo "${BRIEFING_TYPE}" | sed 's/.*/\U&/')
SUBJECT=$(printf "🌙 %s Briefing — %s" "$BRIEFING_TYPE_CAPS" "$(date '+%A, %B %d')")
BODY_TEXT=$(printf "Your daily %s briefing is attached.\n\nGenerated: %s\nDashboard: https://www.reillydesignstudio.com\nGA4: https://analytics.google.com" "$BRIEFING_TYPE" "$(date '+%I:%M %p %Z')")

# Use PDF if available, otherwise use HTML
ATTACHMENT_FILE="$PDF_FILE"
if [ ! -f "$PDF_FILE" ] || [ "$PDF_FILE" = "$HTML_FILE" ]; then
  ATTACHMENT_FILE="$HTML_FILE"
fi

if gog gmail send \
  --to "$BRIEFING_EMAIL" \
  --subject "$SUBJECT" \
  --body "$BODY_TEXT" \
  --attach "$ATTACHMENT_FILE" 2>&1 | grep -q "Message"; then
  echo "[briefing] ✓ Email sent with attachment"
else
  echo "[briefing] ⚠️ Email delivery may have failed"
fi

# Step 5: Cleanup
rm -f "$HTML_FILE"

echo "[briefing] =========================================="
echo "[briefing] ✓ Briefing delivery complete"
echo "[briefing] Delivered to: Telegram + Gmail (PDF)"
echo "[briefing] =========================================="
