#!/bin/bash
# evening-briefing.sh — Generate and send evening briefing
#
# Usage: bash evening-briefing.sh [--send]

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
BRIEFING_DATA=$(python3 "$SCRIPT_DIR/scripts/populate-briefing.py" 2>/dev/null || echo '{"ga4":{"sessions":"—","users":"—","bounce":"—","html":"","sources_html":"","pages_html":""},"gmail":{"unread":"—","flagged":"—"}}')
GA4_SESSIONS=$(echo "$BRIEFING_DATA" | jq -r '.ga4.sessions // "—"')
GA4_USERS=$(echo "$BRIEFING_DATA" | jq -r '.ga4.users // "—"')
GA4_BOUNCE=$(echo "$BRIEFING_DATA" | jq -r '.ga4.bounce // "—"')
GA4_HTML=$(echo "$BRIEFING_DATA" | jq -r '.ga4.html // ""')
GA4_SOURCES_HTML=$(echo "$BRIEFING_DATA" | jq -r '.ga4.sources_html // ""')
GA4_PAGES_HTML=$(echo "$BRIEFING_DATA" | jq -r '.ga4.pages_html // ""')
GMAIL_UNREAD=$(echo "$BRIEFING_DATA" | jq -r '.gmail.unread // "—"')

# Fetch today's completions from memory
COMPLETIONS_DATA=$(python3 "$SCRIPT_DIR/scripts/get-todays-completions.py" 2>/dev/null || echo '{"html":"<div class=\"item\"><em>Unable to load completions</em></div>"}')
COMPLETIONS_HTML=$(echo "$COMPLETIONS_DATA" | jq -r '.html // ""')

# Fetch project progress from git and projects
PROJECT_DATA=$(python3 "$SCRIPT_DIR/scripts/get-project-progress.py" 2>/dev/null || echo '{"html":"<div class=\"item\"><em>Unable to load projects</em></div>"}')
PROJECT_HTML=$(echo "$PROJECT_DATA" | jq -r '.html // ""')

# Fetch blockers from memory and GitHub
BLOCKERS_DATA=$(python3 "$SCRIPT_DIR/scripts/get-blockers.py" 2>/dev/null || echo '{"html":"<div class=\"item\"><em>No blockers</em></div>"}')
BLOCKERS_HTML=$(echo "$BLOCKERS_DATA" | jq -r '.html // ""')

# Fetch tomorrow's prep
PREP_DATA=$(python3 "$SCRIPT_DIR/scripts/get-tomorrow-prep.py" 2>/dev/null || echo '{"html":"<div class=\"item\"><em>Check MEMORY.md</em></div>"}')
PREP_HTML=$(echo "$PREP_DATA" | jq -r '.html // ""')

# Fetch Google Tasks (remaining tasks for tomorrow)
TASKS_DATA=$(python3 "$SCRIPT_DIR/scripts/get-tasks.py" 2>/dev/null || echo '{"pending_count":0,"total_count":0,"tasks":[]}')
TASKS_COUNT=$(echo "$TASKS_DATA" | jq -r '.pending_count // 0')
TASKS_LIST=$(echo "$TASKS_DATA" | jq -r '.tasks[] | "      <div class=\"item\">• \(.title)</div>"' | head -5 || echo '<div class="item"><em>All caught up!</em></div>')

# Create HTML content
cat > /tmp/evening-briefing.html << EOF
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; border-radius: 8px; text-align: center; margin-bottom: 20px; }
        .section { background: #f9f9f9; padding: 15px; margin-bottom: 15px; border-left: 4px solid #f5576c; border-radius: 4px; }
        .section h2 { margin-top: 0; color: #f5576c; font-size: 18px; }
        .item { padding: 8px 0; border-bottom: 1px solid #eee; }
        .item:last-child { border-bottom: none; }
        .time { color: #999; font-size: 12px; }
        .success { color: #28a745; font-weight: bold; }
        .warning { color: #dc3545; font-weight: bold; }
        .stat { display: inline-block; background: white; padding: 10px 15px; margin: 5px 5px 5px 0; border-radius: 4px; font-weight: bold; font-size: 14px; }
        .tomorrow { background: #e8f4f8; padding: 15px; border-left: 4px solid #0099cc; margin-bottom: 15px; border-radius: 4px; }
        .metric-item { padding: 8px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
        .metric-item:last-child { border-bottom: none; }
        .metric-label { flex: 1; }
        .metric-value { font-weight: bold; color: #f5576c; min-width: 60px; text-align: right; }
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
            <h1>🌙 Good Evening</h1>
            <p>Daily Summary — <span id="date"></span></p>
        </div>

        <div class="section">
            <h2>✅ Completed Today</h2>
            $COMPLETIONS_HTML
        </div>

        <div class="section">
            <h2>📈 Project Progress</h2>
            $PROJECT_HTML
        </div>

        $GA4_HTML
        
        $GA4_SOURCES_HTML
        
        $GA4_PAGES_HTML

        <div class="section">
            <h2>⚠️ Blockers / Issues</h2>
            $BLOCKERS_HTML
        </div>

        <div class="section">
            <h2>📋 Pending Tasks</h2>
            <div class="item"><strong>$TASKS_COUNT</strong> pending tasks to carry forward</div>
            $TASKS_LIST
        </div>

        <div class="tomorrow">
            <h2>📋 Tomorrow's Prep</h2>
            $PREP_HTML
        </div>

        <div class="section">
            <h2>🎯 Top 3 Actions for Tomorrow</h2>
            <div class="item"><strong>1.</strong> Continue Momotaro iOS (5:30 AM reminder set)</div>
            <div class="item"><strong>2.</strong> Resolve GA4 Cloud project issue</div>
            <div class="item"><strong>3.</strong> Configure ReillyDesignStudio environment</div>
        </div>

        <div class="footer">
            <p>🍑 Momotaro Daily Briefing System</p>
            <p><small>Generated at $(date +"%I:%M %p") EDT</small></p>
            <p><small>Tomorrow morning briefing: 6:00 AM EDT</small></p>
        </div>
    </div>
</body>
</html>
EOF

# Send email
if [[ "$SEND_EMAIL" == "--send" ]]; then
  gog gmail send \
    --to "$BRIEFING_EMAIL" \
    --subject "🌙 Evening Briefing — $(date +%A, %B %d)" \
    --body-html "$(cat /tmp/evening-briefing.html)" 2>&1 | head -3
  echo "[briefing] ✓ Evening briefing sent"
else
  cat /tmp/evening-briefing.html
  echo "[briefing] Evening briefing generated (use --send to email)"
fi
