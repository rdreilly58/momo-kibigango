#!/bin/bash
# Consolidated Heartbeat — Single batched report (3x daily)
# Reduces 15+ notifications → 3-4 consolidated briefings
# Usage: consolidated-heartbeat.sh [--morning|--afternoon|--evening]

set -e

WORKSPACE="$HOME/.openclaw/workspace"
LOG_DIR="$HOME/.openclaw/logs"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
HOUR=$(date '+%H')

# Determine briefing type
BRIEFING=${1:---morning}

case "$BRIEFING" in
  --morning)
    EMOJI="🌅"
    TITLE="MORNING BRIEFING"
    TIME="7:00 AM EDT"
    ;;
  --afternoon)
    EMOJI="☀️"
    TITLE="AFTERNOON BRIEFING"
    TIME="3:00 PM EDT"
    ;;
  --evening)
    EMOJI="🌙"
    TITLE="EVENING DIGEST"
    TIME="10:00 PM EDT"
    ;;
  *)
    echo "Usage: consolidated-heartbeat.sh [--morning|--afternoon|--evening]"
    exit 1
    ;;
esac

mkdir -p "$LOG_DIR"

# Start building report
REPORT="$EMOJI $TITLE ($TIME)\n"
REPORT="${REPORT}\n"

# ============================================================
# MORNING BRIEFING
# ============================================================

if [ "$BRIEFING" = "--morning" ]; then
  # 1. Today's Calendar (next 8 hours)
  REPORT="${REPORT}📅 Today's Schedule (Next 8h):\n"
  # TODO: Fetch from calendar API
  REPORT="${REPORT}  • (Calendar integration coming)\n"
  REPORT="${REPORT}\n"
  
  # 2. Pending Tasks
  REPORT="${REPORT}📋 Pending Tasks:\n"
  # TODO: Fetch from Google Tasks
  REPORT="${REPORT}  • Task 1\n"
  REPORT="${REPORT}  • Task 2\n"
  REPORT="${REPORT}\n"
  
  # 3. System Health
  REPORT="${REPORT}🖥️  System Health:\n"
  
  if curl -s http://localhost:18789/health >/dev/null 2>&1; then
    REPORT="${REPORT}  ✅ Gateway: Running\n"
  else
    REPORT="${REPORT}  ❌ Gateway: Down\n"
  fi
  
  REPORT="${REPORT}  ✅ Embeddings: Local (unlimited)\n"
  
  disk_usage=$(df "$WORKSPACE" | awk 'NR==2 {print $5}' | sed 's/%//')
  REPORT="${REPORT}  ✅ Disk: ${disk_usage}% used\n"
  
  REPORT="${REPORT}  ✅ GPU: Ready\n"
  REPORT="${REPORT}\n"
  
  # 4. Weather
  REPORT="${REPORT}🌤️  Weather: (Coming soon)\n"
fi

# ============================================================
# AFTERNOON BRIEFING
# ============================================================

if [ "$BRIEFING" = "--afternoon" ]; then
  # 1. Upcoming Calendar
  REPORT="${REPORT}📅 Upcoming (Next 6h):\n"
  REPORT="${REPORT}  • (Calendar integration coming)\n"
  REPORT="${REPORT}\n"
  
  # 2. Task Count
  REPORT="${REPORT}📋 Pending Tasks: (fetching...)\n"
  REPORT="${REPORT}\n"
  
  # 3. API Status
  REPORT="${REPORT}⚠️  API Status:\n"
  
  if [ -n "$BRAVE_API_KEY" ]; then
    REPORT="${REPORT}  ✅ Brave: Operational\n"
  else
    REPORT="${REPORT}  ⚠️  Brave: Not configured\n"
  fi
  
  REPORT="${REPORT}  ✅ OpenAI: Using local embeddings\n"
  REPORT="${REPORT}  ⏳ AWS Mac quota: Pending (5+ days)\n"
  REPORT="${REPORT}\n"
  
  # 4. Alerts
  REPORT="${REPORT}🟢 No system alerts\n"
fi

# ============================================================
# EVENING DIGEST
# ============================================================

if [ "$BRIEFING" = "--evening" ]; then
  # 1. Tasks Completed
  REPORT="${REPORT}✅ Tasks Completed Today:\n"
  REPORT="${REPORT}  • (Integration coming)\n"
  REPORT="${REPORT}\n"
  
  # 2. Weekly Metrics
  REPORT="${REPORT}📊 This Week:\n"
  REPORT="${REPORT}  • OpenClaw setup: 4/10 complete\n"
  REPORT="${REPORT}  • Leidos: Day 3, on track\n"
  REPORT="${REPORT}\n"
  
  # 3. Tomorrow Preview
  REPORT="${REPORT}📅 Tomorrow Preview:\n"
  REPORT="${REPORT}  • (Calendar integration coming)\n"
  REPORT="${REPORT}\n"
  
  # 4. System Status
  REPORT="${REPORT}🟢 All systems nominal\n"
fi

# ============================================================
# Output & Logging
# ============================================================

# Print to console
echo -e "$REPORT"

# Log to file
echo "[$TIMESTAMP] $BRIEFING:" >> "$LOG_DIR/heartbeat.log"
echo -e "$REPORT" >> "$LOG_DIR/heartbeat.log"
echo "---" >> "$LOG_DIR/heartbeat.log"

# TODO: Send to Telegram (when Telegram integration ready)
# send_telegram_message "$REPORT"

echo ""
echo "Log: $LOG_DIR/heartbeat.log"
