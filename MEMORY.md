# MEMORY.md - Long-Term Memory

## Current Status (March 12, 2026 - 10:27 AM)

**Session Focus:** Performance optimization - Archiving memory, upgrading model

---

## Active Projects

### Onigashima MVP
- **Status:** ✅ COMPLETE (10:16 AM March 12)
- **Delivery:** 27 files, ~10,000 lines across 6 sequential batches
- **Features:** Search, Multi-device sync, E2E encryption, Admin dashboard, Tests + Docs
- **GitHub:** https://github.com/rdreilly58/onigashima (main branch)
- **Archive:** See memory/archive/week-6-onigashima-mvp.md for details

### ReillyDesignStudio (Next.js + AWS Amplify)
- **Status:** Built & deployed to dev environment
- **URL:** https://dev.d24p2wkrfuex3c.amplifyapp.com
- **Pending:**
  - Stripe env vars (STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET)
  - Google OAuth setup
  - Email SMTP configuration
  - Custom domain setup
- **GitHub:** https://github.com/rdreilly58/reillydesignstudio
- **Guide:** STRIPE_ENV_GUIDE.md (in workspace)

### Momotaro-iOS (Swift/SwiftUI)
- **Status:** Xcode project ready, build successful
- **Tech:** SwiftUI, Xcode 26.3, Tuist
- **Next:** WebSocket integration with Onigashima backend
- **GitHub:** https://github.com/rdreilly58/momotaro-ios

### Daily Briefings (Morning + Evening)
- **Status:** ✅ WORKING (GA4 access granted)
- **Schedule:** 6:00 AM & 5:00 PM EDT
- **Features:** Email status, calendar, GA4 analytics, priorities
- **Delivery:** PDF emails via Gmail
- **Tech:** Python scripts + system cron

---

## Accounts & Credentials

### AWS
- **Account ID:** 053677584823
- **Amplify App ID:** d24p2wkrfuex3c
- **Console:** https://console.aws.amazon.com/amplifyui

### GitHub
- **Username:** rdreilly58
- **Status:** Fully authenticated

### Google Cloud / GA4
- **GA4 Property ID:** 526836321
- **Service Account:** momo2analytics@rds-analytics-489420.iam.gserviceaccount.com
- **Status:** ✅ Viewer access granted

### Email (Gmail)
- **Personal:** rdreilly2010@gmail.com
- **Work:** robert.reilly@reillydesignstudio.com
- **Tools:** Himalaya CLI, gog (Google CLI)
- **Status:** ✅ Fully configured

---

## Key Decisions & Process Notes

1. **Sequential Batch Building:** Spawn → Complete → Push → Next (proven 4-6 min per batch)
2. **GitHub Verification:** Always push from main session after subagent completes
3. **Memory Management:** Archive completed projects, keep active context < 1000 lines
4. **Model Selection:** Use GPT-4o for long sessions, Haiku for quick tasks

---

## Bob's Preferences

- **Name:** Bob
- **Timezone:** America/New_York (EDT)
- **Email:** robert.reilly@reillydesignstudio.com
- **Called me:** Momotaro 🍑
- **Working style:** Sequential, documented, GitHub-verified

---

## Next Steps

1. **Week 7:** Integration testing + staging deployment (Onigashima)
2. **Week 8:** iOS client integration (connect momotaro-ios to Onigashima backend)
3. **Week 9:** Production deployment + monitoring
4. **ReillyDesignStudio:** Complete Stripe + OAuth configuration
5. **Momotaro iOS:** WebSocket real-time messaging integration

---

## Performance Improvements Applied (March 12, 10:27 AM)

- ✅ Archived Week 6 details to memory/archive/
- ✅ Trimmed MEMORY.md from 2000+ to ~400 lines
- ✅ Upgrading model from Haiku to GPT-4o (in progress)
- Expected improvement: 10-20x faster response on simple commands
