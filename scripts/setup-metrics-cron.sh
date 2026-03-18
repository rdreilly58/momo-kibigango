#!/bin/bash
# setup-metrics-cron.sh
# Add automatic metrics collection to crontab
# Run once to set up automatic daily and weekly metrics

set -e

SCRIPTS_DIR="$HOME/.openclaw/workspace/scripts"

echo "🔧 Setting up automatic metrics collection..."
echo ""

# Get current crontab (or empty string if none)
CURRENT_CRON=$(crontab -l 2>/dev/null || echo "")

# Check if metrics cron jobs already exist
if echo "$CURRENT_CRON" | grep -q "collect-daily-metrics"; then
  echo "⚠️  Metrics cron jobs already configured!"
  echo ""
  echo "Current entries:"
  crontab -l 2>/dev/null | grep metrics || true
  echo ""
  echo "To reconfigure, remove these entries and run this script again:"
  echo "  crontab -e"
  exit 0
fi

# Create new crontab with metrics jobs added
TEMP_CRON=$(mktemp)

# Write existing crontab to temp file
if [ -n "$CURRENT_CRON" ]; then
  echo "$CURRENT_CRON" > "$TEMP_CRON"
else
  touch "$TEMP_CRON"
fi

# Add new metrics jobs
cat >> "$TEMP_CRON" << 'EOF'

# GPU Metrics Collection (Daily at 10 PM)
0 22 * * * /Users/rreilly/.openclaw/workspace/scripts/collect-daily-metrics.sh >> ~/.openclaw/logs/metrics.cron.log 2>&1

# GPU Weekly Summary (Every Monday at 9 AM)
0 9 * * 1 /Users/rreilly/.openclaw/workspace/scripts/weekly-metrics-summary.sh >> ~/.openclaw/logs/metrics.cron.log 2>&1
EOF

# Install new crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo "✅ Cron jobs installed successfully!"
echo ""
echo "📅 Schedule:"
echo "  • Daily metrics:   10:00 PM EDT (every day)"
echo "  • Weekly summary:  9:00 AM EDT (every Monday)"
echo ""
echo "📊 Metrics will be saved to:"
echo "  • Daily JSON: ~/.openclaw/logs/metrics/[DATE]-summary.json"
echo "  • Daily Markdown: ~/.openclaw/workspace/memory/DAILY_METRICS_[DATE].md"
echo "  • Weekly JSON: ~/.openclaw/logs/metrics/week-[WK]-[YEAR]-summary.json"
echo "  • Weekly Markdown: ~/.openclaw/workspace/memory/WEEKLY_METRICS_W[WK]-[YEAR].md"
echo ""
echo "📋 View crontab:"
echo "  crontab -l | grep metrics"
echo ""
echo "📖 View logs:"
echo "  tail ~/.openclaw/logs/metrics.cron.log"
echo ""
echo "✅ Automation complete! Metrics will now be collected automatically."
