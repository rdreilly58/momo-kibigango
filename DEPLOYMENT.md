# Quick Wins Deployment Guide

**Status:** All 5 quick-win scripts created and committed ✅  
**Deployment Status:** Ready for activation ⏳

## Scripts Deployed

| Script | Location | Purpose | Status |
|--------|----------|---------|--------|
| system-health-check.sh | `scripts/system-health-check.sh` | Monitor APIs, disk, memory, git | ✅ Ready |
| quota-monitoring-cron.sh | `scripts/quota-monitoring-cron.sh` | Check API quotas hourly | ✅ Ready |
| session-startup-check.sh | `scripts/session-startup-check.sh` | Validate startup (10/13 ✅) | ✅ Ready |
| memory-search-config.md | `scripts/memory-search-config.md` | Local embeddings guide | ✅ Ready |
| update-cron-jobs.sh | `scripts/update-cron-jobs.sh` | Cron config generator | ✅ Ready |
| apply-cron-update.sh | `scripts/apply-cron-update.sh` | Apply cron updates | ⏳ Ready |

## Deployment Steps

### Step 1: Test Individual Scripts

```bash
# Test system health check
~/.openclaw/workspace/scripts/system-health-check.sh

# Test startup check
~/.openclaw/workspace/scripts/session-startup-check.sh

# View quota monitoring (dry-run, no actual changes)
cat ~/.openclaw/workspace/scripts/quota-monitoring-cron.sh
```

### Step 2: Manual Crontab Update (Alternative to apply-cron-update.sh)

If the automated script hangs, use this manual approach:

**Option A: Open crontab editor directly**
```bash
crontab -e
```

Add these lines at the end:
```cron
# AWS Mac Quota Check (every 4 hours, work hours)
0 6,10,14,18,22 * * * echo '⏳ AWS Mac Quota Status Check' >> ~/.openclaw/logs/quota-check.log 2>&1

# System Health Check (every 2 hours, work hours)
0 8,10,12,14,16,18,20 * * * /Users/rreilly/.openclaw/workspace/scripts/system-health-check.sh >> /Users/rreilly/.openclaw/logs/health-check.log 2>&1

# Quota Monitoring (every 4 hours)
0 6,10,14,18,22 * * * /Users/rreilly/.openclaw/workspace/scripts/quota-monitoring-cron.sh >> /Users/rreilly/.openclaw/logs/quota-monitor.log 2>&1
```

Save and exit (in vim: `:wq`)

**Option B: Using launchd (macOS native, preferred)**

Create `~/Library/LaunchAgents/com.momotaro.health-checks.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.momotaro.health-checks</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/rreilly/.openclaw/workspace/scripts/system-health-check.sh</string>
  </array>
  <key>StartInterval</key>
  <integer>7200</integer> <!-- 2 hours in seconds -->
  <key>StandardOutPath</key>
  <string>/Users/rreilly/.openclaw/logs/health-check.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/rreilly/.openclaw/logs/health-check.error.log</string>
</dict>
</plist>
```

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/com.momotaro.health-checks.plist
```

### Step 3: Verify Deployment

**Check crontab installation:**
```bash
crontab -l | grep -E "AWS|Health|Quota"
```

Expected output:
```
0 6,10,14,18,22 * * * echo '⏳ AWS Mac Quota Status Check' >> ~/.openclaw/logs/quota-check.log 2>&1
0 8,10,12,14,16,18,20 * * * /Users/rreilly/.openclaw/workspace/scripts/system-health-check.sh >> /Users/rreilly/.openclaw/logs/health-check.log 2>&1
0 6,10,14,18,22 * * * /Users/rreilly/.openclaw/workspace/scripts/quota-monitoring-cron.sh >> /Users/rreilly/.openclaw/logs/quota-monitor.log 2>&1
```

**Check launchd installation (if using launchd):**
```bash
launchctl list | grep momotaro
```

**Test individual scripts immediately:**
```bash
# Run quota monitoring now
/Users/rreilly/.openclaw/workspace/scripts/quota-monitoring-cron.sh

# Check logs
tail -f ~/.openclaw/logs/quota-monitor.log
```

### Step 4: Monitor Deployment

**Check cron logs:**
```bash
# View last 20 lines of health check logs
tail -20 ~/.openclaw/logs/health-check.log

# View quota monitor logs
tail -20 ~/.openclaw/logs/quota-monitor.log

# Watch for new entries
watch tail ~/.openclaw/logs/health-check.log
```

## Expected Behavior After Deployment

### Timing

**6:00 AM:** AWS quota check + quota monitoring  
**8:00 AM:** System health check  
**10:00 AM:** Health check + quota monitoring + AWS quota check  
**12:00 PM:** System health check  
**2:00 PM:** Health check + quota monitoring + AWS quota check  
**4:00 PM:** System health check  
**6:00 PM:** Health check + quota monitoring + AWS quota check  
**8:00 PM:** System health check  
**10:00 PM:** Quota monitoring + AWS quota check  

### Log Files Created

```
~/.openclaw/logs/health-check.log       — System health check results
~/.openclaw/logs/quota-monitor.log      — API quota monitoring logs
~/.openclaw/logs/quota-check.log        — AWS quota reminder logs
```

## Troubleshooting

### Issue: Crontab command hangs

**Solution:** Use launchd (macOS native) instead of cron
```bash
# Create the plist file shown in Step 2, Option B
# Then load it: launchctl load ~/Library/LaunchAgents/com.momotaro.health-checks.plist
```

### Issue: Scripts not running at scheduled time

**Check:**
```bash
# Verify scripts are executable
ls -l ~/.openclaw/workspace/scripts/*.sh

# Check system cron logs
log stream --predicate 'process == "cron"' --level debug

# For launchd:
log stream --predicate 'process == "launchd"' --level debug
```

### Issue: Logs not being created

**Solution:** Create log directory if missing
```bash
mkdir -p ~/.openclaw/logs
chmod 755 ~/.openclaw/logs
```

## Rollback (If Issues Arise)

**To remove all quick-win cron jobs:**
```bash
crontab -e
# Remove the three lines added above (AWS, Health, Quota)
# Save and exit
```

**Or restore from backup:**
```bash
# If we backed up crontab earlier
crontab /tmp/crontab-backup-*.txt
```

## Summary

| Component | Status | Action Required |
|-----------|--------|-----------------|
| Scripts created | ✅ Done | None |
| Scripts tested | ✅ Done | None |
| Committed to git | ✅ Done | None |
| Crontab updated | ⏳ Pending | Manual setup OR use launchd |
| Logs configured | ✅ Ready | Create ~/.openclaw/logs if missing |
| Deployment verified | ⏳ Pending | Run verification commands above |

**Next:** Use Option A (crontab -e) or Option B (launchd) from Step 2 to complete activation.

---

*Generated: March 25, 2026 00:53 AM EDT*
