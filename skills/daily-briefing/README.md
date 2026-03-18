# Daily Briefing System

Automated morning and evening briefings with real-time data.

## Quick Start

```bash
# Generate + Send Evening Briefing
bash scripts/send-briefing-clean.sh evening

# Generate + Send Morning Briefing  
bash scripts/send-briefing-clean.sh morning

# Preview only (no email)
bash scripts/evening-briefing.sh
```

## What's Included

- **Completions:** From `memory/YYYY-MM-DD.md`
- **Project Progress:** Git commits + project status
- **Blockers/Issues:** Memory + GitHub issues
- **Tomorrow's Prep:** From MEMORY.md
- **GA4 Analytics:** Real-time website metrics
- **Email:** Clean text attachment (no artifacts)
- **Telegram:** Ready (needs bot token)

## Configuration

Edit: `~/.openclaw/workspace/config/briefing.env`

## Scheduling (Cron)

```bash
0 17 * * * bash ~/.openclaw/workspace/skills/daily-briefing/scripts/send-briefing-clean.sh evening
0 6 * * * bash ~/.openclaw/workspace/skills/daily-briefing/scripts/send-briefing-clean.sh morning
```

## Files

- `send-briefing-clean.sh` - Main script (email + Telegram preview)
- `evening-briefing.sh` - Generate evening briefing HTML
- `morning-briefing.sh` - Generate morning briefing HTML
- `sanitize-html.py` - Clean HTML for email/PDF
- `populate-briefing.py` - Fetch GA4 data
- `get-*.py` - Data collection scripts

---

Last updated: March 18, 2026
