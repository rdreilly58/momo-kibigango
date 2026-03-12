# MEMORY.md - Long-Term Memory

## Active Projects (Now)

### ReillyDesignStudio (Next.js + AWS Amplify)
- **Status:** Built & deployed to dev
- **URL:** https://dev.d24p2wkrfuex3c.amplifyapp.com
- **GitHub:** https://github.com/rdreilly58/reillydesignstudio
- **Pending:** Stripe env vars, Google OAuth, SMTP, custom domain

### Momotaro-iOS (Swift/SwiftUI)
- **Status:** Xcode project ready, build successful
- **GitHub:** https://github.com/rdreilly58/momotaro-ios
- **Next:** WebSocket integration with Onigashima backend

### Daily Briefings (✅ Just Completed)
- **Status:** LIVE with comprehensive GA4 analytics
- **Schedule:** 6:00 AM & 5:00 PM EDT
- **Features:** GA4 metrics + traffic sources + top pages + email count
- **GA4 Property ID:** 526836321

## Key Credentials

| Service | ID/Email | Status |
|---------|----------|--------|
| AWS | Account: 053677584823 | ✅ Active |
| GitHub | rdreilly58 | ✅ Authenticated |
| GA4 | Property: 526836321 | ✅ Viewer access |
| Gmail | robert.reilly@reillydesignstudio.com | ✅ Configured |

## Bob's Preferences

- **Name:** Bob
- **Timezone:** America/New_York (EDT)
- **Working style:** Sequential, documented, GitHub-verified
- **Called me:** Momotaro 🍑

## Performance Optimizations (March 12, 1:00 PM)

- ✅ Archived memory/2026-03-09 through 2026-03-10 to memory/archive/
- ✅ Trimmed MEMORY.md from 400 → 150 lines
- ✅ Model: Haiku for simple requests, GPT-4o for complex work
- Expected: 46% → 20% context usage

## Cron Jobs Active

1. **Morning Briefing** — 6:00 AM EDT (with GA4 analytics) ✅ FIXED Mar 12, 19:13
2. **Evening Briefing** — 5:00 PM EDT (with GA4 analytics) ✅ FIXED Mar 12, 19:13
3. **Momotaro iOS Dev Reminder** — 9:00 AM EDT
4. **Stripe Setup Reminder** — 9:00 AM EDT

## Email Configuration

**Status:** ✅ RESOLVED (Mar 12, 19:13)

**What was fixed:**
- gog authenticated to rdreilly2010@gmail.com (personal), not robert.reilly@reillydesignstudio.com (business)
- Emails ARE being sent successfully to robert.reilly@reillydesignstudio.com
- Both morning (6 AM) and evening (5 PM) briefings now configured with:
  - Detailed GA4 analytics (7-day metrics: active users, page views, bounce rate, avg session)
  - Traffic sources (Google CPC, direct, LinkedIn)
  - Top pages with view counts
  - Tomorrow's calendar events
  - Unread email count

**GA4 Setup:**
- Created Python script: `/tmp/ga4_briefing.py` (pulls live GA4 data)
- GA4 Property ID: 526836321 (reillydesignstudio.com)
- Service account: `~/.openclaw/workspace/secrets/ga4-service-account.json`
- Script calculates 7-day trends vs previous week

**Testing Complete:**
- Evening briefing: Sent successfully Mar 12 @ 19:06 & 19:04
- Morning briefing: Sent successfully Mar 12 @ 19:11
- Both arrived at robert.reilly@reillydesignstudio.com
