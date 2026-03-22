# HEARTBEAT.md - Periodic Tasks

## Leidos Strategy Check (ACTIVE)

**Weekly: Every Sunday 8:00 AM EDT**

This is managed by cron job: `Leidos Leadership Strategy Weekly Review`

The cron will automatically prompt you on Sunday mornings. Response flow:
1. Review the checklist that fires (DORA metrics, people, delivery, etc.)
2. I'll guide you through the template (we have `WEEKLY_REVIEW_TEMPLATE.md` ready)
3. Discuss adjustments needed
4. Save results to `leidos/knowledge/weekly-reviews/YYYY-MM-DD-review.md`

**What you need for each review:**
- DORA metrics (deployment frequency, lead time, failure rate, recovery time)
- Sprint completion data (% on-time)
- Team health observations (1:1s, morale, growth)
- Blocker list (what's slowing things down?)
- Any strategic adjustments from the week

---

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
