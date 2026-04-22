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

## Things 3 Task Check

Show pending tasks during periodic checks (Things 3 is the primary task tracker since April 16, 2026):

```bash
echo "📋 Today's Tasks:"
things today 2>/dev/null | head -10 | sed 's/^/  • /' || echo "  (Things unavailable)"

echo ""
echo "📥 Inbox:"
things inbox 2>/dev/null | head -5 | sed 's/^/  • /' || true
```

**What it shows:**
- Today's scheduled tasks
- Inbox items needing triage
- Quick overview of what needs attention

**Frequency:** Every heartbeat (~30 min)  
**Duration:** <2 seconds  
**Impact:** Lightweight, informational only

> Note: Google Tasks check was removed April 2026 — `jq` display was broken (escaping issue in `exec` call). Things 3 is now authoritative. Use `things today` or `things inbox` from CLI.

---

## Heartbeat Performance: Isolation Mode

**Current status:** ⏸️ Heartbeat disabled April 19, 2026. The built-in 30-min heartbeat was burning full main session context (no isolation support in v2026.4.15). Disabled until OpenClaw implements `isolatedSession` for built-in heartbeats.

Periodic tasks are now handled exclusively by explicit `agentTurn` crons (see sections above), which run in isolated sessions and are significantly cheaper.

> To re-enable: `openclaw config set agents.defaults.heartbeat.enabled true` once isolation is confirmed working. Target config when available:
> ```bash
> openclaw config set agents.defaults.heartbeat.isolatedSession true
> openclaw config set agents.defaults.heartbeat.lightContext true
> ```

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

## GPU / Compute Status

**Current compute hierarchy (as of April 22, 2026):**

| Tier | Resource | Status |
|------|----------|--------|
| 1 | Local M4 Max GPU (24GB) | ✅ Primary — torch/MLX, all local inference |
| 2 | Google Colab H100 | ✅ Available (manual) — large batch jobs only |
| ~~3~~ | ~~AWS EC2 `54.81.20.218`~~ | 🗑️ **Decommissioned April 22, 2026** |

**Decision:** EC2 instance was down since April 5 with no path to recovery. Standardised on M4 Max (local, always available) + Colab H100 (manual, for jobs needing >24GB VRAM). EC2 tier removed — no restart, no replacement.

**For GPU work:**
- Local inference → M4 Max via MLX or PyTorch (MPS backend)
- Large-scale batch / >24GB jobs → Google Colab H100 (manual launch)
- Do NOT attempt to ssh to `54.81.20.218` — instance terminated
