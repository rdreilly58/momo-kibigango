# Weekly Leadership Plan System — Setup & Documentation

**Created:** March 22, 2026  
**Status:** ✅ PRODUCTION READY  
**First run:** Sunday, March 29, 2026, 3:00 AM EDT

---

## Overview

Automated system that generates **calendar-aware, strategy-aligned leadership plans** every Sunday at 3:00 AM EDT.

**Pipeline:** Google Calendar → Strategy Review → Generate Plan → PDF → Email → Archive

---

## Components

### 1. Template: `leidos/templates/plan-template.md`

Professional markdown template with:
- Strategic context (from last review)
- Next day (Monday) priorities and calendar
- Next week heatmap and strategic blocks
- Next 30 days week-by-week breakdown
- Key decisions, risks, success metrics

### 2. Script: `leidos/scripts/generate-leadership-plan.py`

Python script that generates markdown plan from:
1. Google Calendar JSON export (30 days)
2. Last week's strategy review
3. Leadership strategy framework

### 3. Automation: `leidos/scripts/weekly-plan-automation.sh`

Bash script orchestrating full pipeline:
1. Pull calendar (gog)
2. Find latest review
3. Generate plan (Python)
4. Convert to PDF (pandoc)
5. Archive (Git)
6. Email (gog gmail)

### 4. Cron Job: Sunday 3:00 AM EDT

**ID:** `8efa9471-3c9c-4a86-96fb-81779fff3e8a`  
**Status:** ✅ Enabled

---

## Weekly Cycle

### Sunday, 3:00 AM EDT — Plan Generation
- Cron fires → Full pipeline runs → PDF in inbox

### Sunday, 8:00 AM EDT — Strategy Review
- Review template: DORA metrics, people, delivery
- Identify adjustments needed

### Sunday, 9:00 AM EDT — Optional Refinement
- If major changes → Regenerate plan

---

## What You'll Receive

Every Sunday at 3:00 AM, PDF email with:

**📋 Next Day (Monday)**
- Calendar and priorities
- Decisions needed
- Success criteria

**📅 Next Week (Mon-Fri)**
- Calendar heatmap
- Strategic blocks
- 1:1 meetings
- Delivery targets
- Technical focus

**📅 Next 30 Days**
- Week-by-week breakdown
- Major initiatives
- Critical dates
- Risks and mitigations
- Success scorecard

---

## Files & Locations

```
leidos/
├── templates/plan-template.md
├── scripts/
│   ├── generate-leadership-plan.py
│   └── weekly-plan-automation.sh
├── plans/weekly/
│   ├── YYYY-MM-DD-plan.md
│   └── YYYY-MM-DD-plan.pdf
└── docs/PLAN_SYSTEM_SETUP.md (this file)
```

---

## Dependencies

✅ gog (calendar)  
✅ gog (gmail)  
✅ Python 3  
✅ Bash 4+  
✅ Git  
✅ pandoc (PDF conversion)

---

## Status

**Production Ready:**
✅ Scripts complete  
✅ Cron configured  
✅ Calendar access verified  
✅ Email configured  
✅ Error handling in place  
✅ Logging comprehensive  
✅ Git integration complete

**First run:** Sunday, March 29, 2026, 3:00 AM EDT

---

**Related:** LEADERSHIP_STRATEGY.md, WEEKLY_REVIEW_TEMPLATE.md, JOB_DESCRIPTION.md
