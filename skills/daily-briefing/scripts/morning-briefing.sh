#!/bin/bash
# morning-briefing.sh — Generate and send morning briefing
#
# Usage: bash morning-briefing.sh [--send]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SEND_EMAIL="${1:-}"

# Load config
source ~/.openclaw/workspace/config/briefing.env 2>/dev/null || {
  echo "[briefing] Error: briefing.env not found"
  echo "Run: bash setup-briefing.sh first"
  exit 1
}

# Fetch live data
BRIEFING_DATA=$(python3 "$SCRIPT_DIR/scripts/populate-briefing.py" 2>/dev/null || echo '{"ga4":{"sessions":"--","users":"--","bounce":"--","html":"","sources_html":"","pages_html":""},"gmail":{"unread":"--","flagged":"--"}}')
GA4_SESSIONS=$(echo "$BRIEFING_DATA" | jq -r '.ga4.sessions // "--"')
GA4_USERS=$(echo "$BRIEFING_DATA" | jq -r '.ga4.users // "--"')
GA4_BOUNCE=$(echo "$BRIEFING_DATA" | jq -r '.ga4.bounce // "--"')
GA4_HTML=$(echo "$BRIEFING_DATA" | jq -r '.ga4.html // ""')
GA4_SOURCES_HTML=$(echo "$BRIEFING_DATA" | jq -r '.ga4.sources_html // ""')
GA4_PAGES_HTML=$(echo "$BRIEFING_DATA" | jq -r '.ga4.pages_html // ""')
GMAIL_UNREAD=$(echo "$BRIEFING_DATA" | jq -r '.gmail.unread // "--"')
GMAIL_FLAGGED=$(echo "$BRIEFING_DATA" | jq -r '.gmail.flagged // "--"')

# Create HTML content
cat > /tmp/morning-briefing.html << EOF
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; text-align: center; margin-bottom: 20px; }
        .section { background: #f9f9f9; padding: 15px; margin-bottom: 15px; border-left: 4px solid #667eea; border-radius: 4px; }
        .section h2 { margin-top: 0; color: #667eea; font-size: 18px; }
        .item { padding: 8px 0; border-bottom: 1px solid #eee; }
        .item:last-child { border-bottom: none; }
        .time { color: #999; font-size: 12px; }
        .stat { display: inline-block; background: white; padding: 10px 15px; margin: 5px 5px 5px 0; border-radius: 4px; font-weight: bold; }
        .priority { background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin-bottom: 15px; border-radius: 4px; }
        .metric-item { padding: 8px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
        .metric-item:last-child { border-bottom: none; }
        .metric-label { flex: 1; }
        .metric-value { font-weight: bold; color: #667eea; min-width: 60px; text-align: right; }
        .metric-change { color: #28a745; font-size: 12px; min-width: 80px; text-align: right; }
        .source-item { padding: 8px 0; border-bottom: 1px solid #eee; font-size: 13px; }
        .source-item:last-child { border-bottom: none; }
        .page-item { padding: 8px 0; border-bottom: 1px solid #eee; font-size: 13px; }
        .page-item:last-child { border-bottom: none; }
        .footer { text-align: center; color: #999; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>☀️ Good Morning</h1>
            <p>Daily Briefing — <span id="date"></span></p>
        </div>

        <div class="priority">
            <strong>📋 Today's Focus:</strong> Momotaro iOS development • ReillyDesignStudio optimization • GA4 integration
        </div>

        <div class="section">
            <h2>📅 Calendar (Next 48h)</h2>
            <div class="item">
                <strong>Gabe's Wedding Planning</strong>
                <br><span class="time">April 18, 2026 @ 2:00 PM</span>
                <br>📍 Saint Anne's Episcopal Church, Reston, VA
            </div>
        </div>

        <div class="section">
            <h2>📧 Email Activity</h2>
            <div class="stat">Unread: <strong>$GMAIL_UNREAD</strong></div>
            <div class="stat">Flagged: <strong>$GMAIL_FLAGGED</strong></div>
        </div>

        $GA4_HTML
        
        $GA4_SOURCES_HTML
        
        $GA4_PAGES_HTML

        <div class="section">
            <h2>🎯 Top Priorities</h2>
            <div class="item">1. Complete Momotaro iOS WebSocket integration</div>
            <div class="item">2. Resolve GA4 Cloud project linking issue</div>
            <div class="item">3. Review ReillyDesignStudio analytics</div>
        </div>

        <div class="footer">
            <p>🍑 Momotaro Daily Briefing System</p>
            <p><small>Generated at $(date +"%I:%M %p") EDT</small></p>
        </div>
    </div>
</body>
</html>
EOF

# Send email
if [[ "$SEND_EMAIL" == "--send" ]]; then
  gog gmail send \
    --to "$BRIEFING_EMAIL" \
    --subject "☀️ Morning Briefing — $(date +%A, %B %d)" \
    --body-html "$(cat /tmp/morning-briefing.html)" 2>&1 | head -3
  echo "[briefing] ✓ Morning briefing sent"
else
  cat /tmp/morning-briefing.html
  echo "[briefing] Morning briefing generated (use --send to email)"
fi
