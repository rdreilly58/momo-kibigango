#!/bin/bash
# Update Cron Jobs — Reduce noise, consolidate checks
# Reduces AWS quota checks from hourly to every 4 hours

CRON_BACKUP="/tmp/crontab-backup-$(date +%s).txt"

echo "📅 Updating Cron Jobs Configuration"
echo ""

# Backup existing crontab
echo "💾 Backing up crontab..."
crontab -l > "$CRON_BACKUP" 2>/dev/null || echo "No existing crontab"
echo "   Backup: $CRON_BACKUP"

echo ""
echo "📝 Cron Job Changes:"
echo ""

# Read current crontab
CURRENT=$(crontab -l 2>/dev/null || echo "")

# Remove old hourly AWS quota check (if exists)
echo "1. AWS Mac Quota Check: hourly → every 4 hours"
if echo "$CURRENT" | grep -q "AWS Mac Quota"; then
    echo "   - Removing old hourly check"
    echo "$CURRENT" | grep -v "AWS Mac Quota" > /tmp/crontab-filtered.txt
    CURRENT=$(cat /tmp/crontab-filtered.txt)
else
    echo "   - No existing check found"
fi

# Add new 4-hourly AWS quota check (only during work hours)
# Check at 6 AM, 10 AM, 2 PM, 6 PM, 10 PM (5 times/day)
echo "   - Adding new 4-hourly check (work hours)"
AWS_CHECK="0 6,10,14,18,22 * * * echo '⏳ AWS Mac Quota Status Check - Request ID: f385e0e9ebe248b1bbbc70b36755d34bU68btWJY' 2>&1"

echo ""
echo "2. Health Check Cron Job: NEW"
echo "   - Adding: system-health-check.sh every 2 hours during work"
HEALTH_CHECK="0 8,10,12,14,16,18,20 * * * $HOME/.openclaw/workspace/scripts/system-health-check.sh >> $HOME/.openclaw/logs/health-check.log 2>&1"

echo ""
echo "3. Quota Monitoring: NEW"
echo "   - Adding: quota-monitoring-cron.sh every 4 hours"
QUOTA_MONITOR="0 6,10,14,18,22 * * * $HOME/.openclaw/workspace/scripts/quota-monitoring-cron.sh >> $HOME/.openclaw/logs/quota-monitor.log 2>&1"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Summary of Changes:"
echo "═══════════════════════════════════════════════════════════"
echo "BEFORE: AWS quota check runs every hour (24 messages/day)"
echo "AFTER:  AWS quota check runs 5 times/day at set hours"
echo "        + Health check every 2 hours during work"
echo "        + Quota monitoring every 4 hours"
echo ""
echo "Expected notifications/day:"
echo "  - AWS quota: 5 messages (6 AM, 10 AM, 2 PM, 6 PM, 10 PM)"
echo "  - Briefings: 2 messages (6 AM, 5 PM)"
echo "  - Health checks: 7 messages (every 2 hours, work hours)"
echo "═══════════════════════════════════════════════════════════"

# Combine crontab entries
echo ""
echo "⚙️ Ready to apply. Use this command to activate:"
echo ""
echo "cat > /tmp/crontab-update.txt << 'CRON_EOF'"
echo "$CURRENT"
echo "$AWS_CHECK"
echo "$HEALTH_CHECK"
echo "$QUOTA_MONITOR"
echo "CRON_EOF"
echo "crontab /tmp/crontab-update.txt"
echo ""
echo "Or run: ~/.openclaw/workspace/scripts/apply-cron-update.sh"

cat > ~/.openclaw/workspace/scripts/apply-cron-update.sh << 'APPLY_EOF'
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
APPLY_EOF

chmod +x ~/.openclaw/workspace/scripts/apply-cron-update.sh
echo "✅ Created apply-cron-update.sh"
