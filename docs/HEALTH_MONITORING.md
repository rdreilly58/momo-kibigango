# OpenClaw Health Monitoring System

**Date:** March 25, 2026  
**Status:** ✅ IMPLEMENTED  
**Scope:** System health, API quotas, critical services

---

## Overview

Automated health monitoring catches failures before they impact operations. Two-tier system:

1. **System Health Check** — Critical systems (Gateway, Git, Memory, Disk, Python, GPU)
2. **API Quota Monitor** — API usage & quota status (Brave, OpenAI, HF, Cloudflare, AWS)

---

## Components

### 1. System Health Check
**File:** `scripts/system-health-check.sh`

**Checks:**
- ✅ OpenClaw Gateway (port 8080 connectivity)
- ✅ Git repository (uncommitted changes)
- ✅ API keys (environment variables loaded)
- ✅ Memory files (SOUL.md, USER.md, MEMORY.CORE.md)
- ✅ Disk space (usage %, alerts at 75%/90%)
- ✅ Python environment (venv integrity)
- ✅ Cron jobs (active count)
- ✅ LaunchD services (active agents)
- ✅ GPU health (quick check if configured)

**Output:**
```
✅ OpenClaw Gateway: Running (port 8080)
✅ Git Repository: Clean
✅ API Keys: BRAVE_API_KEY loaded
✅ Memory Files: 47 daily logs
✅ Disk Space: 42% used
✅ Python Env: Python 3.10.0
✅ Cron Jobs: 8 active entries
✅ LaunchD Services: 12 agents, 3 active
✅ GPU Health: Quick check passed
```

**Usage:**
```bash
# Standard output to log
bash scripts/system-health-check.sh

# Verbose output to terminal
bash scripts/system-health-check.sh --verbose

# With Telegram alerts (if errors found)
bash scripts/system-health-check.sh --verbose --telegram
```

### 2. API Quota Monitor
**File:** `scripts/api-quota-monitor.sh`

**Checks:**
- ✅ Brave Search API (test query + status)
- ✅ OpenAI API (status: using local embeddings)
- ✅ Hugging Face (fallback availability)
- ✅ Local embeddings (unlimited local queries)
- ✅ Cloudflare API (unlimited for most endpoints)
- ✅ AWS quota (Mac instance request status)

**Output:**
```
✅ Brave Search API: Working (status)
ℹ️  OpenAI API: Using local embeddings (no quota needed)
✅ Hugging Face API: Free tier (Unlimited)
✅ Local Embeddings: Unlimited (queries)
✅ Cloudflare API: OK (Unlimited)
⏳ AWS Mac Instance Quota: PENDING (submitted 2026-03-20)
```

**Usage:**
```bash
# Standard check
bash scripts/api-quota-monitor.sh

# Verbose with alerts
bash scripts/api-quota-monitor.sh --verbose --alert
```

---

## Cron Integration

### Setup

Add to crontab:
```bash
crontab -e
```

```cron
# System health check - daily at 9 AM
0 9 * * * /Users/rreilly/.openclaw/workspace/scripts/system-health-check.sh --verbose --telegram

# API quota monitor - daily at 10 AM
0 10 * * * /Users/rreilly/.openclaw/workspace/scripts/api-quota-monitor.sh --verbose --alert

# GPU health (if configured) - every 4 hours
0 */4 * * * /Users/rreilly/.openclaw/workspace/scripts/gpu-health-check-full.sh

# Weekly summary - Sunday at 8 AM
0 8 * * 0 echo "Weekly OpenClaw Health Summary" && bash scripts/system-health-check.sh --verbose
```

### Log Files

- **System health:** `~/.openclaw/logs/health-check.log`
- **API quotas:** `~/.openclaw/logs/quota.log`
- **GPU health:** `~/.openclaw/logs/gpu-health.log`

---

## Alert Behavior

### Automatic Alerts (Telegram)

Sent when:
- ❌ Gateway not responding
- ❌ Memory files missing
- ❌ Disk usage >90%
- ❌ API quota exceeded
- ❌ Python environment broken
- ❌ GPU health check failed

**Format:**
```
⚠️ ALERT: [Service Name]
Status: [Critical/Error]
Issue: [What's wrong]
Action: [Next step]
Time: [HH:MM EDT]
```

### Silent Issues (Logged only)

- ⚠️ Uncommitted Git changes (warn, don't alert)
- ⚠️ Disk usage 75-90% (warn, don't alert)
- ⚠️ API keys not set (warn if optional)
- ⚠️ Optional services offline (log, don't alert)

---

## Manual Checks

Run anytime to verify system health:

```bash
# Full system check
bash ~/.openclaw/workspace/scripts/system-health-check.sh --verbose

# API quota check
bash ~/.openclaw/workspace/scripts/api-quota-monitor.sh --verbose

# GPU health (if configured)
bash ~/.openclaw/workspace/scripts/gpu-health-check-full.sh

# View recent logs
tail -50 ~/.openclaw/logs/health-check.log
tail -50 ~/.openclaw/logs/quota.log
```

---

## Integration with Heartbeat

Health checks can be run as part of periodic heartbeat:

**In HEARTBEAT.md:**
```bash
# During heartbeat (~every 30 min)
bash ~/.openclaw/workspace/scripts/api-quota-monitor.sh --alert

# Less frequently (daily)
bash ~/.openclaw/workspace/scripts/system-health-check.sh --verbose
```

---

## Troubleshooting

**"Gateway not responding on port 8080"**
- Check if OpenClaw is running: `openclaw status`
- Restart: `openclaw gateway restart`
- Check logs: `tail -50 ~/.openclaw/logs/gateway.log`

**"Memory files missing"**
- Ensure workspace is initialized: `cd ~/.openclaw/workspace && git status`
- Restore from git: `git checkout SOUL.md USER.md MEMORY.CORE.md`

**"Disk usage critical"**
- Clean old logs: `rm -rf ~/.openclaw/logs/*.log.* ~/.openclaw/logs/archive/*`
- Archive old memory: `mv memory/2026-01-*.md archive/`

**"API quota exceeded"**
- See ALERT_PROTOCOL.md for immediate actions
- Check which service is affected
- Activate fallback or reduce usage

---

## Future Improvements

- [ ] Slack/Discord integration for alerts
- [ ] Metrics dashboard (Prometheus + Grafana)
- [ ] Automated log rotation and archival
- [ ] Weekly health report email
- [ ] Predictive quota warnings (before limit)
- [ ] Service dependency checks (e.g., Gateway needs Redis)
- [ ] Performance regression detection
