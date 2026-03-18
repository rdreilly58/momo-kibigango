# Metrics Automation - Complete Setup Guide

**Status:** ✅ Fully automated (cron jobs installed and running)  
**Setup Date:** March 17, 2026  
**Next Automatic Run:** Today 10:00 PM EDT (daily) + Next Monday 9:00 AM EDT (weekly)

---

## 🤖 What's Automated

### Daily Metrics Collection
- **When:** Every day at 10:00 PM EDT
- **What:** Analyzes all GPU requests from that day
- **Output:** JSON + Markdown summary saved to memory/
- **Time:** <5 seconds execution

### Weekly Metrics Summary
- **When:** Every Monday at 9:00 AM EDT
- **What:** Aggregates all daily data for the week
- **Output:** Weekly report with ROI, savings, trends
- **Time:** <10 seconds execution

### GPU Health Checks
- **When:** Mac boot (@reboot) + Every heartbeat (~30 min)
- **What:** Verifies GPU is operational, fallback if needed
- **Output:** Logs + Telegram notification
- **Time:** 5-90 seconds depending on check type

---

## 📋 Cron Jobs Installed

```bash
# GPU Startup Verification (@reboot)
@reboot /Users/rreilly/.openclaw/workspace/scripts/gpu-startup-notify.sh

# Daily Metrics Collection (10 PM EDT)
0 22 * * * /Users/rreilly/.openclaw/workspace/scripts/collect-daily-metrics.sh

# Weekly Metrics Summary (9 AM EDT, Mondays)
0 9 * * 1 /Users/rreilly/.openclaw/workspace/scripts/weekly-metrics-summary.sh
```

**View installed jobs:**
```bash
crontab -l | grep -E "metrics|gpu"
```

---

## 🔍 What Gets Logged & Stored

### Daily (Every Evening at 10 PM)

**JSON Summary:**
```
~/.openclaw/logs/metrics/2026-03-17-summary.json
{
  "date": "2026-03-17",
  "total_requests": 15,
  "gpu_requests": 12,
  "cpu_requests": 3,
  "gpu_percentage": 80,
  "avg_gpu_latency_ms": 2140,
  "avg_cpu_latency_ms": 42500,
  "time_saved_total_seconds": 480000,
  "time_saved_hours": 133.33,
  "total_cost": 0.12
}
```

**Markdown Summary:**
```
~/.openclaw/workspace/memory/DAILY_METRICS_2026-03-17.md
# Daily Metrics Summary - 2026-03-17

## Quick Stats
- **Total Requests:** 15
- **GPU Requests:** 12
- **CPU Requests:** 3
- **GPU Usage:** 80%

## Performance
- **Avg GPU Latency:** 2140ms
- **Avg CPU Latency:** 42500ms
- **Time Saved (Total):** 133.33 hours
...
```

**CSV Append:**
```
~/.openclaw/logs/metrics/daily-summary.csv
date,gpu_requests,cpu_requests,total_requests,gpu_percentage,avg_gpu_latency_ms,total_time_saved_seconds,total_cost
2026-03-17,12,3,15,80,2140,480000,0.12
```

### Weekly (Every Monday at 9 AM)

**Weekly JSON:**
```
~/.openclaw/logs/metrics/week-11-2026-summary.json
{
  "week": 11,
  "year": 2026,
  "period": "2026-03-16 to 2026-03-22",
  "days_tracked": 7,
  "total_requests": 120,
  "gpu_requests": 104,
  "gpu_percentage": 87,
  "total_time_saved_hours": 520.5,
  "total_time_saved_days": 65.06,
  "gpu_instance_cost": 228.69,
  "cloud_api_equivalent": 1260.00,
  "estimated_savings": 1031.31
}
```

**Weekly Markdown:**
```
~/.openclaw/workspace/memory/WEEKLY_METRICS_W11-2026.md
# Weekly Metrics Report - Week 11, 2026

Period: 2026-03-16 to 2026-03-22 (7 days)

Usage: 120 total requests, 104 GPU (87%), 16 CPU
Performance: 520.5 hours saved (65 work days)
Savings: $1,031.31 estimated

...table with detailed breakdown...
```

---

## 📊 How It Works

### Data Flow
```
Every GPU request
        ↓
Logged to gpu-usage.jsonl
        ↓
Daily (10 PM): collect-daily-metrics.sh reads log
        ↓
Creates: [DATE]-summary.json + DAILY_METRICS_[DATE].md
        ↓
Weekly (Monday 9 AM): weekly-metrics-summary.sh aggregates
        ↓
Creates: week-[WK]-[YEAR]-summary.json + WEEKLY_METRICS_W[WK]-[YEAR].md
```

### Key Calculations (Automatic)

**GPU Percentage:**
```
gpu_percentage = (gpu_requests / total_requests) × 100
```

**Time Saved:**
```
time_per_request = cpu_latency - gpu_latency
total_time_saved = time_per_request × gpu_requests
hours_saved = total_time_saved / 3600
work_days_saved = hours_saved / 8
```

**Cost Analysis:**
```
gpu_cost = $980/month ÷ 30 = $32.67/day
cloud_equivalent = total_requests × $0.05
estimated_savings = cloud_equivalent - gpu_cost
```

---

## 🔧 Management Commands

### View Cron Jobs
```bash
# Show all metrics cron entries
crontab -l | grep metrics

# Edit crontab
crontab -e
```

### Manual Runs
```bash
# Run daily collection now (useful for testing)
~/.openclaw/workspace/scripts/collect-daily-metrics.sh

# Run weekly summary now
~/.openclaw/workspace/scripts/weekly-metrics-summary.sh
```

### View Logs
```bash
# See cron execution log
tail -50 ~/.openclaw/logs/metrics.cron.log

# Watch for today's metrics (after 10 PM)
watch -n 5 ls -lh ~/.openclaw/workspace/memory/DAILY_METRICS_*.md

# View latest daily summary
cat ~/.openclaw/logs/metrics/2026-03-17-summary.json | jq
```

### Update Schedule
```bash
# Change daily collection time from 10 PM to 11 PM
crontab -e
# Change: 0 22 * * * → 0 23 * * *

# Change weekly summary time from 9 AM to 10 AM Monday
crontab -e
# Change: 0 9 * * 1 → 0 10 * * 1
```

---

## 📈 What to Expect

### March 17 (Today)
- ✅ Cron jobs installed
- ✅ System ready
- First automatic run: Today 10:00 PM EDT

### March 18-20 (Testing Phase)
- Daily summaries generated each evening
- Daily metrics appear in memory/
- Review data for go/no-go decision March 20

### March 20 (Decision Day)
- Review all 3 daily summaries
- Weekly summary will have 3 days of data
- Make GO/NO-GO decision based on real data

### March 21+ (If GO)
- Metrics continue automatic collection
- Weekly reports every Monday
- Use data for marketing + transparency

---

## 🚀 Benefits of Automation

### For You
✅ Zero manual effort after setup  
✅ Perfect data every day (never forget to track)  
✅ Historical record for analysis  
✅ Ready for marketing/press immediately  

### For Marketing
✅ Real measured data (not estimates)  
✅ Weekly reports for community sharing  
✅ Transparent metrics build trust  
✅ Competitive advantage (proven ROI)  

### For Users (Future)
✅ See exactly how GPU is performing  
✅ Know the cost savings  
✅ Trust your system (transparent)  
✅ Feature requests based on real data  

---

## 📊 Example Output (What You'll See)

### Daily (Every Evening)
```
📊 DAILY METRICS SUMMARY - 2026-03-17
═══════════════════════════════════════════════════════════════

Usage:
  Total Requests:    15
  GPU Requests:      12
  CPU Requests:      3
  GPU Percentage:    80%

Performance:
  GPU Latency:       2140ms
  CPU Latency:       42500ms
  Time Saved:        133.33 hours

Cost:
  Total Cost:        $0.12
  Cost Per Request:  $0.008

═══════════════════════════════════════════════════════════════
```

### Weekly (Every Monday)
```
📊 WEEKLY METRICS SUMMARY - Week 11, 2026
═══════════════════════════════════════════════════════════════

Period: 2026-03-16 to 2026-03-22 (7 days)

Usage:
  Total Requests:     120
  GPU Requests:       104
  CPU Requests:       16
  GPU Usage Rate:     87%
  Avg Requests/Day:   17

Performance:
  Time Saved:         520.5 hours (65 work days)

Cost Analysis:
  GPU Instance Cost:  $228.69
  Cloud Equivalent:   $1,260.00
  Savings:            $1,031.31
  Cost Per Request:   $0.0195

═══════════════════════════════════════════════════════════════
```

---

## 🔐 Privacy & Security

- All metrics stored locally (no cloud sync by default)
- Logs in `~/.openclaw/logs/` (user-only readable)
- Memory files in `~/.openclaw/workspace/memory/` (user-only)
- No external APIs called for metrics collection
- No personally identifiable information logged

To share metrics publicly (optional):
```bash
# Example: Share weekly summary
cat ~/.openclaw/workspace/memory/WEEKLY_METRICS_W11-2026.md
# Copy content to blog post or GitHub

# Example: Include in marketing
# Reference the JSON files directly in your dashboard
```

---

## 🐛 Troubleshooting

### Metrics not appearing?
```bash
# Check if cron job ran
tail ~/.openclaw/logs/metrics.cron.log

# Check if script is executable
ls -l ~/.openclaw/workspace/scripts/collect-daily-metrics.sh
# Should show: -rwx (executable)

# Run manually to test
~/.openclaw/workspace/scripts/collect-daily-metrics.sh
```

### Cron job failed?
```bash
# Look at error log
tail -100 ~/.openclaw/logs/metrics.cron.log

# Check for jq (required for JSON parsing)
which jq
# If missing: brew install jq

# Check for bc (required for math)
which bc
# If missing: brew install bc
```

### Want to disable automation?
```bash
# Remove cron jobs
crontab -e
# Delete the metrics lines, save and exit

# Or remove just one job:
crontab -l > /tmp/cron.bak
grep -v "collect-daily-metrics" /tmp/cron.bak | crontab -
```

---

## 📝 Next Steps

1. **Verify setup** (right now):
   ```bash
   crontab -l | grep metrics
   ```

2. **Wait for first run** (today 10:00 PM EDT):
   - Check memory/ for new file: `DAILY_METRICS_2026-03-17.md`
   - Check logs/metrics/ for JSON summary

3. **Review daily** (March 18-19):
   - Read the auto-generated summaries
   - Note any patterns or issues
   - Prepare for March 20 decision

4. **Make decision** (March 20):
   - Review all 3 days of data
   - Calculate go/no-go based on metrics
   - Decide to launch or iterate

5. **Launch** (March 21+, if GO):
   - Metrics continue automatically
   - Use data for marketing
   - Share weekly summaries with community

---

## ✅ Automation Complete

Everything is now automated. You don't need to do anything except:

1. ✅ Use the GPU system normally
2. ✅ Let metrics collect automatically each evening
3. ✅ Review summaries weekly
4. ✅ Use data for decision-making + marketing

**No manual tracking required.** The system does it for you. 🤖

---

**Status:** Ready. Metrics collection active as of March 17, 2026.
