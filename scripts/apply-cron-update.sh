#!/bin/bash
# Apply cron job updates

CURRENT=$(crontab -l 2>/dev/null || echo "")

# Remove old AWS quota checks
FILTERED=$(echo "$CURRENT" | grep -v "AWS Mac Quota" || echo "$CURRENT")

# Add new cron jobs
NEW_CRONTAB="$FILTERED
# AWS Mac Quota Check (every 4 hours, work hours only)
0 6,10,14,18,22 * * * echo '⏳ AWS Mac Quota Status Check - Request ID: f385e0e9ebe248b1bbbc70b36755d34bU68btWJY' 2>&1

# System Health Check (every 2 hours, work hours)
0 8,10,12,14,16,18,20 * * * $HOME/.openclaw/workspace/scripts/system-health-check.sh >> $HOME/.openclaw/logs/health-check.log 2>&1

# Quota Monitoring (every 4 hours)
0 6,10,14,18,22 * * * $HOME/.openclaw/workspace/scripts/quota-monitoring-cron.sh >> $HOME/.openclaw/logs/quota-monitor.log 2>&1"

echo "$NEW_CRONTAB" | crontab -
echo "✅ Cron jobs updated successfully"
echo ""
crontab -l | grep -E "AWS|Health|Quota" || echo "(No entries found)"
