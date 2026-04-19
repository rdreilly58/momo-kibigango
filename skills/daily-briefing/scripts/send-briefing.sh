#!/bin/bash
# send-briefing.sh — Send evening briefing via Telegram and Gmail (with PDF)
#
# Usage: bash send-briefing.sh [evening|morning]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRIEFING_TYPE="${1:-evening}"

# Load config
source ~/.openclaw/workspace/config/briefing.env 2>/dev/null || {
  echo "[briefing] Error: briefing.env not found"
  exit 1
}

# Generate briefing HTML
HTML_FILE="/tmp/${BRIEFING_TYPE}-briefing.html"
bash "$SCRIPT_DIR/scripts/${BRIEFING_TYPE}-briefing.sh" > "$HTML_FILE" 2>&1

echo "[briefing] Generated $BRIEFING_TYPE briefing: $HTML_FILE"

# 1. TELEGRAM DELIVERY
echo "[briefing] Sending to Telegram..."

# Extract text content from HTML for Telegram (simple strip of tags)
TELEGRAM_TEXT=$(sed 's/<[^>]*>//g; s/&nbsp;/ /g; s/&lt;/</g; s/&gt;/>/g' "$HTML_FILE" | \
  grep -v "^$" | head -100)

# Send to Telegram
if command -v telegram-send &> /dev/null; then
  echo "$TELEGRAM_TEXT" | telegram-send --stdin
  echo "[briefing] ✓ Telegram sent"
else
  echo "[briefing] ⚠️ telegram-send not found, skipping Telegram"
fi

# 2. EMAIL DELIVERY (as PDF)
echo "[briefing] Converting to PDF and sending via email..."

PDF_FILE="/tmp/${BRIEFING_TYPE}-briefing.pdf"

# Convert HTML to PDF using pandoc
if command -v pandoc &> /dev/null; then
  pandoc "$HTML_FILE" -o "$PDF_FILE" --pdf-engine=wkhtmltopdf 2>/dev/null || {
    # Fallback: try simpler conversion
    wkhtmltopdf "$HTML_FILE" "$PDF_FILE" 2>/dev/null || {
      echo "[briefing] ⚠️ PDF conversion failed, sending HTML instead"
      PDF_FILE="$HTML_FILE"
    }
  }
  echo "[briefing] ✓ PDF created: $PDF_FILE"
else
  echo "[briefing] ⚠️ pandoc not found, trying wkhtmltopdf..."
  if command -v wkhtmltopdf &> /dev/null; then
    wkhtmltopdf "$HTML_FILE" "$PDF_FILE" 2>/dev/null || {
      echo "[briefing] ⚠️ wkhtmltopdf failed"
      PDF_FILE="$HTML_FILE"
    }
  fi
fi

# Send via Gmail with attachment
SUBJECT="🌙 ${BRIEFING_TYPE^} Briefing — $(date +%A, %B %d)"
BODY="Your daily ${BRIEFING_TYPE} briefing is attached as PDF.

Generated at $(date +"%I:%M %p %Z")"

gog gmail send \
  --to "$BRIEFING_EMAIL" \
  --subject "$SUBJECT" \
  --body "$BODY" \
  --attach "$PDF_FILE" 2>&1 | head -5

echo "[briefing] ✓ Email sent with PDF attachment"

# Cleanup
rm -f "$HTML_FILE"

echo "[briefing] ✓ ${BRIEFING_TYPE^} briefing delivered (Telegram + Email with PDF)"
