# Daily Briefing System — Setup & Configuration

## Overview

Automated daily briefings sent to **Email (Gmail)** and **Telegram** with:
- ✅ Real-time GA4 analytics
- ✅ Today's completions (from memory)
- ✅ Project progress (git commits)
- ✅ Blockers & issues
- ✅ Tomorrow's prep & priorities

## Delivery Channels

### Email (Gmail) ✅ ACTIVE
- **To:** robert.reilly@reillydesignstudio.com
- **Format:** HTML (HTML/PDF coming soon)
- **Schedule:** 5:00 PM EDT (evening), 6:00 AM EDT (morning)

### Telegram 🟡 AVAILABLE
- **Setup:** Requires `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
- **Format:** Plain text with emoji markers
- **How to enable:** Set tokens in `~/.openclaw/workspace/config/briefing.env`

## Manual Triggers

Generate and send briefing now:

```bash
# Generate only (preview)
bash ~/.openclaw/workspace/skills/daily-briefing/scripts/evening-briefing.sh

# Generate + Send via Email
bash ~/.openclaw/workspace/skills/daily-briefing/scripts/send-briefing-v2.sh evening

# Generate + Send via Email (morning)
bash ~/.openclaw/workspace/skills/daily-briefing/scripts/send-briefing-v2.sh morning
```

## Configuration

Edit: `~/.openclaw/workspace/config/briefing.env`

**Key settings:**
```bash
BRIEFING_EMAIL="robert.reilly@reillydesignstudio.com"
MORNING_TIME="06:00"
EVENING_TIME="17:00"
TIMEZONE="America/New_York"
INCLUDE_GA4="true"
```

## Data Sources

### Completed Today
- **Source:** `~/.openclaw/workspace/memory/YYYY-MM-DD.md`
- **Pulled:** Bullet points from today's memory file
- **Update method:** Add `- ` items to today's memory file

### Project Progress
- **Source:** Git commits in tracked repos
- **Repos:** ~/reillydesignstudio, ~/momotaro-ios
- **Pulled:** Commits since midnight today

### Blockers/Issues
- **Sources:**
  - Memory file (items with ⚠️ prefix)
  - GitHub issues assigned to you
- **Repos:** rdreilly58/reillydesignstudio, rdreilly58/momotaro-ios

### Tomorrow's Prep
- **Source:** `~/.openclaw/workspace/MEMORY.md`
- **Pulled:** Lines under "TODO" or "Next Steps" sections
- **Update method:** Edit MEMORY.md with upcoming work

### GA4 Analytics
- **Source:** Google Analytics 4 API
- **Property:** ReillyDesignStudio (526836321)
- **Data:** Last 7 days, with trend comparison
- **Auth:** Service account (~/secrets/ga4-service-account.json)

## Scheduling (Cron)

To schedule automatic delivery at 5:00 PM daily:

```bash
# Add to crontab
crontab -e

# Add these lines:
0 17 * * * bash ~/.openclaw/workspace/skills/daily-briefing/scripts/send-briefing-v2.sh evening
0 6 * * * bash ~/.openclaw/workspace/skills/daily-briefing/scripts/send-briefing-v2.sh morning
```

Or use OpenClaw's cron scheduler:

```bash
# Register evening briefing
cron add \
  --schedule "0 17 * * *" \
  --payload "systemEvent" \
  --text "bash ~/.openclaw/workspace/skills/daily-briefing/scripts/send-briefing-v2.sh evening"
```

## Troubleshooting

**Email not sending?**
- Check gog auth: `gog gmail search --json | head -1`
- Check email address: `echo $BRIEFING_EMAIL`
- Try manual send: `gog gmail send --to $BRIEFING_EMAIL --subject "Test" --body "Test"`

**Data not updating?**
- Check memory file exists: `ls ~/.openclaw/workspace/memory/$(date +%Y-%m-%d).md`
- Check git repos: `cd ~/reillydesignstudio && git log --since=today`
- Check GA4: `python3 ~/.openclaw/workspace/skills/daily-briefing/scripts/ga4-query.py`

**Missing sections?**
- Completions: Update `~/.openclaw/workspace/memory/YYYY-MM-DD.md`
- Projects: Commit to git repos
- Blockers: Add ⚠️ to memory or create GitHub issues
- Prep: Update `~/.openclaw/workspace/MEMORY.md`

## Files

- **Main script:** `~/.openclaw/workspace/skills/daily-briefing/scripts/send-briefing-v2.sh`
- **Config:** `~/.openclaw/workspace/config/briefing.env`
- **Data scripts:**
  - `get-todays-completions.py` — reads memory
  - `get-project-progress.py` — reads git commits
  - `get-blockers.py` — reads memory + GitHub
  - `get-tomorrow-prep.py` — reads MEMORY.md
  - `populate-briefing.py` — fetches GA4 data
- **Templates:** `~/.openclaw/workspace/skills/daily-briefing/scripts/{morning,evening}-briefing.sh`

## Roadmap

- ✅ Email delivery (HTML)
- 🟡 Telegram delivery (needs bot token)
- ⏳ PDF conversion (pandoc/wkhtmltopdf)
- ⏳ Slack integration
- ⏳ Scheduled cron automation

---

**Last updated:** March 18, 2026
