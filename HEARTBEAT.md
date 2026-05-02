# HEARTBEAT.md - Periodic Tasks

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

**Current status:** ✅ Heartbeat re-enabled May 1, 2026. Isolation support confirmed working in v2026.4.29 (`isolatedSession: true`, `lightContext: true`, Haiku model). Fires every 30 min — cheap, isolated, non-disruptive.

Config: `agents.defaults.heartbeat = { enabled: true, every: "30m", isolatedSession: true, lightContext: true, model: "anthropic/claude-haiku-4-5" }`

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
