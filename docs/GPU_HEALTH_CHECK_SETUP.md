# GPU Health Check Setup - Documentation

**Date:** March 17, 2026  
**Status:** ✅ COMPLETE  
**Instance:** 54.81.20.218 (g5.2xlarge, NVIDIA A10G)  

---

## Overview

Automatic health monitoring for GPU inference instance. Runs at Mac boot + periodic heartbeat monitoring.

**Quick Check (@reboot):** 5 seconds, verifies SSH + GPU + CUDA  
**Full Check (heartbeat):** 90 seconds, includes inference test + latency measurement  

---

## What Was Built

### 1. Health Check Scripts

**Location:** `~/.openclaw/workspace/scripts/`

| Script | Purpose | Runtime | Trigger |
|--------|---------|---------|---------|
| `gpu-health-check-quick.sh` | SSH + GPU + CUDA verification | ~5s | @reboot |
| `gpu-health-check-full.sh` | Full inference + latency test | ~90s | Heartbeat |
| `gpu-startup-notify.sh` | Wrapper for startup notification | ~5s | @reboot |

### 2. Cron Integration

**Cron Entry:** `@reboot` 
```bash
@reboot /Users/rreilly/.openclaw/workspace/scripts/gpu-startup-notify.sh 2>&1 | tee -a ~/.openclaw/logs/gpu-startup.log
```

**Runs:** When Mac boots  
**Execution:** Happens within ~5 seconds of OpenClaw startup  
**Output:** Logged to `~/.openclaw/logs/gpu-startup.log`

### 3. Heartbeat Monitoring

**Location:** `~/.openclaw/workspace/HEARTBEAT.md`

Full health check runs every heartbeat (~30 min). Provides ongoing visibility into GPU state.

### 4. Skill Documentation

**Location:** `~/.openclaw/workspace/skills/gpu-health-check/SKILL.md`

Comprehensive guide for troubleshooting, configuration, and understanding the system.

---

## How It Works

### On Mac Boot

```
Mac starts
  ↓
Cron @reboot fires
  ↓
gpu-startup-notify.sh runs
  ↓
Calls gpu-health-check-quick.sh
  ↓
Check 1: SSH connectivity (10s timeout)
  ↓
Check 2: GPU driver (nvidia-smi available?)
  ↓
Check 3: CUDA status (torch.cuda.is_available()?)
  ↓
Output: "✅ GPU offload startup OK" or "❌ GPU offload setup failed"
  ↓
Logged to ~/.openclaw/logs/gpu-startup.log
  ↓
Visible in system (cron output)
  ↓
Ready for use in ~5 seconds
```

### On Heartbeat (Every ~30 min)

```
Heartbeat fires
  ↓
HEARTBEAT.md trigger runs gpu-health-check-full.sh
  ↓
All quick checks +
  ↓
Model loading test
  ↓
Inference latency measurement
  ↓
Performance metrics recorded
  ↓
"✅ GPU offload startup OK" with stats
  OR
"❌ GPU offload setup failed" with reason
```

---

## Telegram Integration

Currently, status messages go to:
1. `~/.openclaw/logs/gpu-startup.log` (local file)
2. Cron output (visible in macOS Console app)

**To add Telegram:**
- Option A: Use OpenClaw heartbeat delivery with announcement mode
- Option B: Add `sessions_send` call in health check script
- Option C: Create separate cron job that reads log and sends via bot

### Recommended: Heartbeat Delivery

Edit `.openclaw/workspace/HEARTBEAT.md`:
```yaml
**GPU Offload Health Check**
Run: /Users/rreilly/.openclaw/workspace/scripts/gpu-health-check-full.sh
Delivery: announce to telegram (channel: 8755120444)
Frequency: every heartbeat
```

Then, when you get a Telegram message saying "Ready to accept complex tasks!" you know GPU is operational.

---

## Success Criteria

### Quick Check (✅ Pass)
- SSH connects within 10 seconds
- nvidia-smi shows A10G
- torch.cuda.is_available() returns True

### Full Check (✅ Pass)
- All quick checks pass
- Mistral-7B model loads successfully
- 10-token inference generates under 90 seconds
- Speed measured > 20 tok/s
- Memory stable (no swapping)

---

## Failure Scenarios & Fixes

### "SSH unreachable"
```bash
# Troubleshoot:
ssh -i ~/.ssh/vlm-deploy-key.pem ubuntu@54.81.20.218 "echo OK"

# Check instance:
aws ec2 describe-instances --instance-ids i-046d1154c0f4a9b2e --region us-east-1 | grep State
```

### "GPU driver issue"
```bash
# On GPU instance:
nvidia-smi
nvidia-smi --query-gpu=name --format=csv,noheader

# If missing, reinstall:
sudo apt-get install -y nvidia-driver-550
sudo reboot
```

### "CUDA initialization failed"
```bash
# On GPU instance:
/mnt/data/venv/bin/python3 -c "import torch; print(torch.cuda.is_available())"

# If False, check:
echo $CUDA_HOME
echo $LD_LIBRARY_PATH
/usr/bin/nvidia-smi
```

### "Inference test failed"
```bash
# Check model cache:
ls -lh /mnt/data/.cache/hf/models/mistralai/

# Check venv:
/mnt/data/venv/bin/python3 --version
/mnt/data/venv/bin/python3 -c "import transformers; print(transformers.__version__)"

# Check disk:
df -h /mnt/data/
```

---

## Logs & Monitoring

### Quick Check Log
```bash
tail -20 ~/.openclaw/logs/gpu-startup.log
```

Shows all startup checks with timestamps.

### Full Check Log
```bash
tail -50 ~/.openclaw/logs/gpu-health.log
```

Shows detailed health history including inference timings.

### Real-Time Monitoring
```bash
# Watch logs as they update:
tail -f ~/.openclaw/logs/gpu-health.log

# Watch startup:
tail -f ~/.openclaw/logs/gpu-startup.log
```

---

## Cost Impact

- **Quick check:** Negligible (~5 sec SSH, no compute)
- **Full check:** ~$0.02 (90 seconds GPU + model load)
- **Daily monitoring:** ~$0.60/month
- **Monthly surveillance:** < $20/month

Worth the cost for a $980/month instance.

---

## Three-Day Test Plan

**Days 1-3 (March 17-19, 2026):**

1. **Boot your Mac normally**
   - Cron @reboot fires automatically
   - Check logs: `tail ~/.openclaw/logs/gpu-startup.log`
   - Should see ✅ status within 5 seconds

2. **Use GPU for complex tasks**
   - Write articles, code, analysis
   - Note latency: ~2-3 minutes first request (includes model load), ~60 sec cached
   - 27.98 tok/s performance is expected

3. **Monitor daily**
   - Run heartbeat (or let it run automatically): `bash ~/.openclaw/workspace/scripts/gpu-health-check-full.sh`
   - Check logs for any warnings
   - Note any degradation or issues

4. **After 3 days, decide:**
   - **Keep always-on:** If using >3 times/day, worth the $980/month
   - **Switch to on-demand:** If < 3 times/day, save money by starting on-demand

---

## Files Created

```
~/.openclaw/workspace/
├── scripts/
│   ├── gpu-health-check-quick.sh       (5s quick check)
│   ├── gpu-health-check-full.sh        (90s full check)
│   └── gpu-startup-notify.sh           (startup wrapper)
├── skills/
│   └── gpu-health-check/
│       └── SKILL.md                    (documentation)
├── HEARTBEAT.md                        (updated with GPU check)
└── docs/
    └── GPU_HEALTH_CHECK_SETUP.md       (this file)

~/.openclaw/logs/
├── gpu-startup.log                     (cron @reboot output)
└── gpu-health.log                      (periodic check results)
```

---

## Quick Reference

### Test GPU Health Now
```bash
/Users/rreilly/.openclaw/workspace/scripts/gpu-health-check-quick.sh
```

### View Setup Log
```bash
tail ~/.openclaw/logs/gpu-startup.log
```

### SSH to Instance
```bash
ssh -i ~/.ssh/vlm-deploy-key.pem ubuntu@54.81.20.218
```

### Verify Setup
```bash
# On Mac
crontab -l | grep gpu

# Check logs
ls -lh ~/.openclaw/logs/gpu-*.log
```

---

## Next Steps (Optional)

1. **Enable Telegram notifications**
   - Modify health check to send message to Telegram
   - Or use OpenClaw heartbeat delivery system

2. **Add performance graphs**
   - Log tok/s measurements over time
   - Track GPU memory usage trends
   - Create dashboard (optional, nice-to-have)

3. **Implement auto-failover**
   - If GPU health check fails, automatically disable GPU feature
   - Fall back to local Claude Haiku
   - Alert user for manual intervention

4. **Monitor inference quality**
   - Log response quality metrics
   - Alert if coherence degrades
   - Compare against baseline

---

## Support

**Questions?** Check the logs and SKILL.md documentation.

**GPU Instance:** `54.81.20.218` (i-046d1154c0f4a9b2e)  
**Key:** `~/.ssh/vlm-deploy-key.pem`  
**Monthly cost:** $980  
**Performance:** 27.98 tok/s baseline (Mistral-7B)  
**Status:** ✅ Operational and monitored  

---

**Setup completed:** Tuesday, March 17, 2026 at 11:18 AM EDT  
**Next review:** March 20, 2026 (after 3-day test)
