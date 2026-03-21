# HEARTBEAT.md - Periodic Tasks

## Google Tasks Check

Show pending tasks during periodic checks:

```bash
TASKLIST_ID="MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow"
PENDING=$(gog tasks list $TASKLIST_ID -a rdreilly2010@gmail.com --json 2>/dev/null | \
  jq '[.tasks[] | select(.status == "needsAction")] | length')

echo "📋 Pending Tasks: $PENDING"
gog tasks list $TASKLIST_ID -a rdreilly2010@gmail.com --json 2>/dev/null | \
  jq -r '.tasks[] | select(.status == "needsAction") | "  • \(.title)"' | head -5
```

**What it shows:**
- Count of pending tasks
- Top 5 task titles
- Quick overview of what needs attention

**Frequency:** Every heartbeat (~30 min)  
**Duration:** <5 seconds  
**Impact:** Lightweight, informational only

---

## Telegraph Heartbeat Publishing

Publish OpenClaw status report (tasks, calendar, metrics) to Telegraph:

```bash
python3 ~/.openclaw/workspace/scripts/telegraph_heartbeat.py
```

**What it does:**
- Fetches pending tasks from Google Tasks
- Retrieves next 24h calendar events
- Gets current system status (uptime)
- Formats as rich Telegraph article with headings
- Publishes to Telegraph.ph
- Sends Telegram notification with published link

**Output:** Telegraph article with sections for Tasks, Calendar, and System Status  
**Telegram notification:** "📄 OpenClaw Heartbeat Report - [timestamp]" with link

**Frequency:** Optional, every heartbeat (~30 min)  
**Duration:** ~5 seconds (API calls only)  
**Skip if:** No pending tasks + no upcoming events (can batch with other checks)

---

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
