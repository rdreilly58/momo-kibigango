# Heartbeat Optimization — Reduce Notification Noise

**Date:** March 25, 2026  
**Status:** ✅ IMPLEMENTED  
**Goal:** 15+ messages/day → 3-4 consolidated messages/day

---

## The Problem

Current heartbeat setup fires every ~30 minutes with multiple independent checks:
- GPU health check (separate Telegram message)
- Google Tasks update (separate message)
- Telegraph publish (separate message)
- Weather check (separate message)
- Calendar check (separate message)

**Result:** 15-20 notification messages per day, overwhelming and hard to parse.

---

## Solution: Batched Heartbeat

Group related checks into a single consolidated report sent 2-4 times daily:

### Morning Briefing (7:00 AM EDT)
**Duration:** ~30 seconds  
**Contains:**
- ✅ Today's calendar (next 8 hours)
- ✅ Pending tasks
- ✅ System health summary
- ✅ Weather forecast

```
🌅 MORNING BRIEFING (7:00 AM EDT)

📅 Today's Schedule (Next 8h):
  • 9:00-10:00: Team standup
  • 2:00-3:00: Project review

📋 Pending Tasks (4):
  • OpenClaw health monitoring
  • Auto-update implementation
  • Heartbeat optimization
  • Recovery playbook

🖥️  System Health:
  ✅ Gateway: Running
  ✅ Embeddings: Local (unlimited)
  ✅ Disk: 42% used
  ✅ GPU: Ready

🌤️  Weather: 52°F, Partly Cloudy | Rain tomorrow
```

### Afternoon Briefing (3:00 PM EDT)
**Duration:** ~30 seconds  
**Contains:**
- ✅ Upcoming calendar (next 6 hours)
- ✅ Updated task count
- ✅ API quota status
- ✅ Any warnings or alerts

```
☀️  AFTERNOON BRIEFING (3:00 PM EDT)

📅 Upcoming (Next 6h):
  • 4:00-5:00: 1:1 with Bob
  • 5:30: End of day wrap

📋 Pending Tasks: Still 4

⚠️  API Status:
  ✅ Brave: Operational
  ✅ OpenAI: Using local (quota reset tomorrow)
  ⏳ AWS Mac quota: Still pending (6 days)

🟢 No system alerts
```

### Evening Digest (10:00 PM EDT)
**Duration:** ~30 seconds  
**Contains:**
- ✅ Summary of the day's tasks completed
- ✅ Weekly metrics (if applicable)
- ✅ Tomorrow's preview
- ✅ System status for night

```
🌙 EVENING DIGEST (10:00 PM EDT)

✅ Tasks Completed Today: 8
  • Email consolidation
  • Task routing integration
  • Health monitoring

📊 This Week (Day 3 of 7):
  • OpenClaw setup: 3/10 complete
  • Leidos: Day 3, on track

📅 Tomorrow Preview:
  • Standups: 9:00-10:00
  • Reviews: 2:00-3:00
  • Work blocks: 10:30-2:00, 3:00-5:30

🟢 All systems nominal
```

---

## Implementation

### New Unified Heartbeat Script
**File:** `scripts/consolidated-heartbeat.sh`

**Runs 3x daily:**
- 7:00 AM → Morning Briefing
- 3:00 PM → Afternoon Briefing  
- 10:00 PM → Evening Digest

**Features:**
- Single Telegram message (batched)
- Runs ~30 seconds (all checks in parallel)
- Skip redundant checks
- Color-coded severity (green/yellow/red)
- Optional Telegraph publication (on request only)

### What Gets Batched

**Morning:**
- Calendar (today)
- Tasks (pending)
- System health
- Weather
- GPU status

**Afternoon:**
- Calendar (remaining)
- Tasks (updated count)
- API quotas
- Any alerts from past 4 hours

**Evening:**
- Tasks completed (summary)
- Weekly metrics
- Tomorrow preview
- System status

### What Gets Skipped (Reduce Noise)

- ❌ GPU health every heartbeat → check only 1x daily (in morning)
- ❌ Telegraph publish every time → publish on request only
- ❌ Weather every heartbeat → once per morning
- ❌ Individual task notifications → one consolidated count

---

## Benefits

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| **Notifications/day** | 15-20 | 3-4 | 85% reduction |
| **Spam score** | High | Low | ✅ Cleaner |
| **Read time/message** | 5-10s each | 30s total | ✅ Faster |
| **Actionable items** | Low (noise) | High (curated) | ✅ Better |
| **API calls/day** | 100+ | ~30 | ✅ Cost savings |

---

## Cron Setup

```bash
# Morning briefing
0 7 * * * bash ~/.openclaw/workspace/scripts/consolidated-heartbeat.sh --morning

# Afternoon briefing
0 15 * * * bash ~/.openclaw/workspace/scripts/consolidated-heartbeat.sh --afternoon

# Evening digest
0 22 * * * bash ~/.openclaw/workspace/scripts/consolidated-heartbeat.sh --evening
```

---

## Backward Compatibility

**Existing HEARTBEAT.md tasks still work:**
- GPU health check script unchanged
- Telegraph publishing still available (on-demand)
- Task checking unchanged
- Everything continues to log

**New behavior:**
- Batched into 3 daily reports instead of per-heartbeat
- Consolidated messaging
- Reduced notification frequency
- Same information, better presentation

---

## Future Improvements

- [ ] Machine learning: Predict which events are most important
- [ ] Adaptive frequency: More briefings on busy days
- [ ] Custom digest: Let Bob choose what goes in each briefing
- [ ] Trending: Show what changed most in past 24h
- [ ] Analytics: "You got X% of tasks done this week"
- [ ] Calendar integration: Pull from Leidos calendar directly
