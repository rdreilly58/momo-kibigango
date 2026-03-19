#!/bin/bash
# morning-briefing.sh — Generate morning briefing with dynamic data
#
# Usage: bash morning-briefing.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load config
source ~/.openclaw/workspace/config/briefing.env 2>/dev/null || {
  echo "[briefing] Error: briefing.env not found"
  exit 1
}

# Fetch live data
BRIEFING_DATA=$(python3 "$SCRIPT_DIR/scripts/populate-briefing.py" 2>/dev/null || echo '{"ga4":{"sessions":"—","users":"—","bounce":"—","html":"","sources_html":"","pages_html":""},"gmail":{"unread":"—"}}')
GA4_SESSIONS=$(echo "$BRIEFING_DATA" | jq -r '.ga4.sessions // "—"')
GA4_USERS=$(echo "$BRIEFING_DATA" | jq -r '.ga4.users // "—"')
GA4_BOUNCE=$(echo "$BRIEFING_DATA" | jq -r '.ga4.bounce // "—"')
GA4_HTML=$(echo "$BRIEFING_DATA" | jq -r '.ga4.html // ""')
GA4_SOURCES_HTML=$(echo "$BRIEFING_DATA" | jq -r '.ga4.sources_html // ""')
GA4_PAGES_HTML=$(echo "$BRIEFING_DATA" | jq -r '.ga4.pages_html // ""')
GMAIL_UNREAD=$(echo "$BRIEFING_DATA" | jq -r '.gmail.unread // "—"')

# Fetch calendar events
CALENDAR_DATA=$(python3 "$SCRIPT_DIR/scripts/get-calendar-events.py" 2>/dev/null || echo '{"html":"<div class=\"item\"><em>Calendar unavailable</em></div>"}')
CALENDAR_HTML=$(echo "$CALENDAR_DATA" | jq -r '.html // ""')

# Fetch today's priorities
PRIORITIES_DATA=$(python3 "$SCRIPT_DIR/scripts/get-todays-priorities.py" 2>/dev/null || echo '{"html":"<div class=\"item\"><em>Set priorities in MEMORY.md</em></div>"}')
PRIORITIES_HTML=$(echo "$PRIORITIES_DATA" | jq -r '.html // ""')

# Fetch Google Tasks
TASKS_DATA=$(python3 "$SCRIPT_DIR/scripts/get-tasks.py" 2>/dev/null || echo '{"pending_count":0,"tasks":[]}')
TASKS_COUNT=$(echo "$TASKS_DATA" | jq -r '.pending_count // 0')
TASKS_LIST=$(echo "$TASKS_DATA" | jq -r '.tasks[] | "      <div class=\"item\">• \(.title)</div>"' | head -5 || echo '<div class="item"><em>No pending tasks</em></div>')

# Export for envsubst
export GMAIL_UNREAD
export CALENDAR_HTML
export PRIORITIES_HTML
export TASKS_COUNT
export TASKS_LIST
export GA4_HTML
export GA4_SOURCES_HTML
export GA4_PAGES_HTML

# Create HTML template and substitute variables
envsubst << 'HTMLEOF'
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
        .footer { text-align: center; color: #999; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>☀️ Good Morning</h1>
            <p>Daily Briefing — Wednesday, March 18</p>
        </div>

        <div class="section">
            <h2>📧 Email Status</h2>
            <div class="item"><strong>Unread:</strong> ${GMAIL_UNREAD}</div>
        </div>

        <div class="section">
            <h2>📅 Today's Calendar</h2>
            ${CALENDAR_HTML}
        </div>

        <div class="section">
            <h2>📋 Pending Tasks</h2>
            <div class="item"><strong>${TASKS_COUNT}</strong> pending tasks</div>
            ${TASKS_LIST}
        </div>

        <div class="section">
            <h2>🎯 Today's Priorities</h2>
            ${PRIORITIES_HTML}
        </div>

        ${GA4_HTML}
        
        ${GA4_SOURCES_HTML}
        
        ${GA4_PAGES_HTML}

        <div class="footer">
            <p>🍑 Momotaro Daily Briefing System</p>
            <p><small>Generated at 06:00 AM EDT</small></p>
        </div>
    </div>
</body>
</html>
HTMLEOF
