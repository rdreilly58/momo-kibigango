# HEARTBEAT.md - Periodic Tasks

## GPU Offload Health Check

Run full GPU health test every heartbeat (detect issues early):

```bash
/Users/rreilly/.openclaw/workspace/scripts/gpu-health-check-full.sh
```

**What it does:**
- Tests SSH connectivity to GPU instance (54.81.20.218)
- Verifies GPU driver & CUDA availability
- Runs quick inference test (measures latency + speed)
- Sends success/failure message to Telegram
- Logs results to ~/.openclaw/logs/gpu-health.log

**Success:** "✅ GPU offload startup OK" with performance metrics  
**Failure:** "❌ GPU offload setup failed" with reason + disables GPU feature

**Frequency:** Every heartbeat (~30 min)  
**Duration:** ~90 seconds (includes model load if needed)  
**Skip if:** Bob explicitly disables GPU feature or is troubleshooting
