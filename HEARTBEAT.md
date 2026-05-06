# HEARTBEAT.md - Periodic Tasks

Heartbeat runs every 30 min — isolated session, Haiku model, light context.

## Things 3 Task Check

```bash
echo "📋 Today's Tasks:"
things today 2>/dev/null | head -10 | sed 's/^/  • /' || echo "  (Things unavailable)"
echo ""
echo "📥 Inbox:"
things inbox 2>/dev/null | head -5 | sed 's/^/  • /' || true
```

Things 3 is the authoritative task tracker (since April 2026). Use `things today` / `things inbox` from CLI.

## Telegraph Status Report

Publish tasks, calendar, and system metrics to Telegraph:

```bash
python3 ~/.openclaw/workspace/scripts/telegraph_heartbeat.py
```

Skip if no pending tasks and no upcoming events.

## GPU / Compute

| Tier | Resource | Status |
|------|----------|--------|
| 1 | Local M4 Max (24GB) | ✅ Primary — MLX/PyTorch |
| 2 | Google Colab H100 | ✅ Manual — large batch / >24GB jobs |

Do NOT ssh to `54.81.20.218` — EC2 decommissioned April 22, 2026.
