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

# Create HTML content
cat > /tmp/evening-briefing.html << 'EOF'
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
            <div class="item"><span class="success">✓</span> Created 7 new OpenClaw skills</div>
            <div class="item"><span class="success">✓</span> Deployed ReillyDesignStudio to AWS Amplify</div>
            <div class="item"><span class="success">✓</span> Built Momotaro iOS project (SwiftUI)</div>
            <div class="item"><span class="success">✓</span> Pushed momotaro-ios to GitHub</div>
            <div class="item"><span class="success">✓</span> Configured GA4 analytics</div>
        </div>

        <div class="section">
            <h2>📈 Project Progress</h2>
            <div class="item">
                <strong>ReillyDesignStudio</strong><br>
                Status: <span class="success">Deployed ✓</span><br>
                Live: https://dev.d24p2wkrfuex3c.amplifyapp.com
            </div>
            <div class="item">
                <strong>Momotaro iOS</strong><br>
                Status: <span class="success">Build Successful ✓</span><br>
                GitHub: rdreilly58/momotaro-ios
            </div>
        </div>

        <div class="section">
            <h2>📊 Today's Metrics</h2>
            <div class="stat">Skills Created: 7</div>
            <div class="stat">Commits: 8</div>
            <div class="stat">Deployments: 1</div>
        </div>

        <div class="section">
            <h2>⚠️ Blockers / Issues</h2>
            <div class="item">
                <span class="warning">GA4 Cloud Project Mismatch</span><br>
                Service account in rds-analytics-489420, but property may be linked to different project.<br>
                Action: Verify GA4 property Cloud project linking
            </div>
        </div>

        <div class="tomorrow">
            <h2>📋 Tomorrow's Prep</h2>
            <div class="item">
                <strong>Momotaro iOS:</strong> Add external dependencies (Starscream, Crypto, SQLite)
            </div>
            <div class="item">
                <strong>GA4 Fix:</strong> Check and resolve Cloud project linking
            </div>
            <div class="item">
                <strong>ReillyDesignStudio:</strong> Setup custom domain and environment variables
            </div>
        </div>

        <div class="section">
            <h2>🎯 Top 3 Actions for Tomorrow</h2>
            <div class="item"><strong>1.</strong> Continue Momotaro iOS (5:30 AM reminder set)</div>
            <div class="item"><strong>2.</strong> Resolve GA4 Cloud project issue</div>
            <div class="item"><strong>3.</strong> Configure ReillyDesignStudio environment</div>
        </div>

        <div class="footer">
            <p>🍑 Momotaro Daily Briefing System</p>
            <p><small>Generated at <span id="time"></span> EDT</small></p>
            <p><small>Tomorrow morning briefing: 6:00 AM EDT</small></p>
        </div>
    </div>

    <script>
        document.getElementById('date').textContent = new Date().toLocaleDateString('en-US', {weekday: 'long', month: 'long', day: 'numeric', year: 'numeric'});
        document.getElementById('time').textContent = new Date().toLocaleTimeString('en-US', {hour: 'numeric', minute: '2-digit'});
    </script>
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
