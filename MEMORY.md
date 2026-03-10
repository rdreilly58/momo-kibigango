# MEMORY.md - Long-Term Memory

## Active Projects

### ReillyDesignStudio (Next.js + AWS Amplify)
- **Status:** ✅ Rebuilt & deployed (March 10, 5:45 AM)
- **URL:** https://dev.d24p2wkrfuex3c.amplifyapp.com
- **Tech Stack:** Next.js, AWS Amplify, Stripe, NextAuth, Google Analytics
- **Build Status:** ✅ Successful (static + dynamic pages)
- **Stripe Integration:** Ready (env vars pending)
- **Features:** Invoice payment, shop checkout, portfolio, blog
- **TODO:**
  - Set Stripe environment variables (STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET)
  - Configure OAuth (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
  - Set analytics IDs
  - Configure SMTP for email
  - Custom domain setup
  - Monitor webhook logs
- **GitHub:** https://github.com/rdreilly58/reillydesignstudio
- **Setup Guide:** STRIPE_ENV_GUIDE.md

### Momotaro-iOS (Swift/SwiftUI)
- **Status:** ✓ Build successful, Xcode project ready
- **Tech Stack:** SwiftUI, Xcode 26.3, Tuist
- **GitHub:** https://github.com/rdreilly58/momotaro-ios
- **Next Steps:** 
  - Add external dependencies (Starscream, Crypto, SQLite)
  - Implement OpenClaw WebSocket connection
  - Test on simulator and device
- **Reminder Set:** 5:30 AM Mar 10 to continue development

## Skills Created

1. **ios-dev** — Xcode iPhone/iPad development (build, test, archive, simulator)
2. **ga4-analytics** — Google Analytics 4 reporting and data access
3. **address-lookup** — OpenStreetMap Nominatim geocoding (free, no API key)
4. **office-docs** — Word (.docx) and Excel (.xlsx) manipulation
5. **aws-deploy** — AWS Amplify build and deployment
6. **make-pdf** — Markdown to PDF conversion
7. **print-local** — Print to Brother printers

## Account & Credentials

### AWS
- **Account ID:** 053677584823
- **Amplify App ID:** d24p2wkrfuex3c
- **Amplify Console:** https://console.aws.amazon.com/amplifyui

### GitHub
- **Username:** rdreilly58
- **Authenticated:** Full repo/workflow permissions

### Google Cloud / GA4
- **GA4 Property ID:** 386311627
- **Property Name:** ReillyDesignStudio
- **Service Account:** momo2analytics@rds-analytics-489420.iam.gserviceaccount.com
- **GA4 Analytics Setup:** Key saved, need permission grant
  - Service account key: `~/.openclaw/workspace/secrets/ga4-service-account.json` ✓
  - **TODO:** Grant service account "Editor" or "Viewer" role on GA4 property
    - Go to https://analytics.google.com → Admin → Property → Property Access Management
    - Add email: momo2analytics@rds-analytics-489420.iam.gserviceaccount.com → Viewer role

### Xcode
- **Version:** 26.3, Build 17C519
- **iOS Target:** iOS 17+
- **Development Path:** ~/momotaro-ios

## Calendar Events

- **Gabe's Wedding:** Saturday, April 18, 2026 @ 2:00-10:00 PM
  - **Venue:** Saint Anne's Episcopal Church, 1700 Wainwright Drive, Lake Anne Village, Reston, VA 20190

## Bob's Preferences

- **Personal Email:** robert.reilly@reillydesignstudio.com (work account)
- **Timezone:** America/New_York (EDT)
- **Name Preference:** Bob
- **Called me:** Momotaro (peach emoji 🍑)

## Email Accounts

### ReillyDesignStudio Work Account
- **Email:** robert.reilly@reillydesignstudio.com
- **Tool:** Himalaya CLI (IMAP/SMTP)
- **Status:** ✅ Configured (awaiting authentication)
- **Config:** ~/.config/himalaya/config.toml
- **Email Scan:** bash ~/.openclaw/workspace/scripts/email-scan.sh
- **Next:** Run `himalaya account configure` to authenticate & store password in keyring

## Daily Briefing Schedule

- **Morning:** 6:00 AM EDT (includes GA4 24h snapshot, calendar, email, top priorities)
- **Evening:** 5:00 PM EDT (includes completed work, progress, blockers, tomorrow's prep)
- **Recipients:** robert.reilly@reillydesignstudio.com
- **Format:** Rich HTML email
- **Frequency:** Every day
- **Cron Jobs:** Scheduled and active

### Briefing Contents
- Morning: Calendar (48h), Email summary, GA4 stats (24h), Top 3 priorities
- Evening: Completed items, Project progress, GitHub commits, Blockers, Tomorrow's actions

---

## Key Decisions

1. Use Tuist for iOS project management (cleaner than raw Xcode)
2. Deployed ReillyDesignStudio to Amplify (AWS managed, auto-scaling)
3. Create reusable skills instead of one-off scripts
4. Store secrets in ~/.openclaw/workspace/secrets/ (not committed to Git)
5. Daily briefing emails at 6 AM and 5 PM for proactive engagement
