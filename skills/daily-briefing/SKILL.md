---
name: daily-briefing
description: Generate and send daily morning and evening briefings with calendar, tasks, GA4 analytics, and project status.
---

# Daily Briefing System

Automated morning and evening briefings delivered via email with calendar, tasks, analytics, and project updates.

## Schedule

- **Morning:** 6:00 AM EDT (daily)
- **Evening:** 5:00 PM EDT (daily)

## Morning Briefing (6:00 AM)

**Contents:**
- 📊 Daily Goals & Focus Areas
- 📅 Calendar Events (next 48 hours)
- 📧 Email Summary (unread count, flagged)
- 📋 **Pending Tasks** (Google Tasks count & highlights)
- 🔔 Active Reminders
- 📈 GA4 Traffic (last 24h, last 7d comparison)
- 🎯 Top Priorities

**Recipients:** robert.reilly@reillydesignstudio.com

---

## Evening Briefing (5:00 PM)

**Contents:**
- ✅ Completed Today
- 📝 Work Summary
- 📈 Project Progress
- 📋 **Pending Tasks** (remaining count, due soon, high priority)
- ⚠️ Blockers/Issues
- 💾 GitHub Commits
- 🚀 Deployments
- 📋 Tomorrow's Prep
- 🎯 Next 3 Actions

**Recipients:** robert.reilly@reillydesignstudio.com

---

## GA4 Analytics in Briefing

**Morning includes (24h snapshot):**
- Sessions, Users, New Users
- Bounce Rate
- Device breakdown
- Top pages

**Evening includes:**
- Daily summary
- Comparison vs. 7-day average
- Traffic sources
- Geographic breakdown

---

## Configuration

Email settings saved in:
```
~/.openclaw/workspace/config/briefing.env
```

GA4 credentials:
```
~/.openclaw/workspace/secrets/ga4-service-account.json
~/.openclaw/workspace/config/ga4.env
```

---

## Manual Briefing Generation

```bash
# Generate morning briefing now
bash ~/.openclaw/workspace/skills/daily-briefing/scripts/morning-briefing.sh

# Generate evening briefing now
bash ~/.openclaw/workspace/skills/daily-briefing/scripts/evening-briefing.sh

# Send immediately
bash ~/.openclaw/workspace/skills/daily-briefing/scripts/morning-briefing.sh --send
bash ~/.openclaw/workspace/skills/daily-briefing/scripts/evening-briefing.sh --send
```

---

## Customization

Edit briefing templates:
```
~/.openclaw/workspace/skills/daily-briefing/templates/morning.html
~/.openclaw/workspace/skills/daily-briefing/templates/evening.html
```

Edit schedule in cron jobs or via:
```bash
cron list  # View scheduled jobs
cron update <jobId> --patch '{"schedule": {"kind": "cron", "expr": "0 6 * * *"}}'
```

---

## Troubleshooting

**Briefing not received:**
1. Check cron job status: `cron list`
2. Verify email address: `cat ~/.openclaw/workspace/config/briefing.env | grep EMAIL`
3. Check GA4 connection: `python3 /tmp/test_ga4.py`
4. Review logs: `cat ~/.openclaw/workspace/logs/briefing.log`

**GA4 data missing:**
- Confirm analytics API enabled
- Verify service account has Viewer access
- Check property ID: `cat ~/.openclaw/workspace/config/ga4.env | grep PROPERTY_ID`

---

## What's Tracked

**Morning:**
- Google Calendar events (next 48h)
- Gmail (unread count, labels)
- GitHub (open PRs, issues assigned)
- GA4 analytics (traffic, devices, pages)
- OpenClaw projects status

**Evening:**
- GitHub commits (all repos)
- Deployments (AWS Amplify, etc.)
- Calendar summary (completed events)
- Email activity
- Open blockers/issues
- Next-day preview

