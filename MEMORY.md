# MEMORY.md - Long-Term Memory

## Latest Session (March 12, 2026 - 6:32-7:20 AM)

**WEEK 5 BACKUP SYSTEM: ✅ COMPLETE & DEPLOYED**

### Outcome
- ✅ 16 production-ready files (6,168 lines) created with Claude Code
- ✅ All files committed locally by subagents
- ✅ **All files pushed to GitHub by Momotaro (main session)**
- ✅ README.md with complete feature guide
- ✅ Process updated with GitHub verification requirements

### Key Deliverables
**Backend (4 files, 1,404 lines):**
- backup-service.js: AES-256-GCM encryption, gzip compression
- routes/backups.js: 6 REST API endpoints
- database-backup-schema.js: PostgreSQL schema + indexes
- backup-scheduler.js: 24-hour auto-backup scheduler

**macOS UI (4 files, 1,859 lines):**
- BackupListView.swift: Pagination, filtering, sorting
- BackupDetailView.swift: Details + restore/delete actions
- BackupSettingsView.swift: Auto-backup toggle, retention, storage
- BackupViewModel.swift: Async/await networking, caching

**iPhone UI (4 files, 1,284 lines):**
- BackupListView.swift: Mobile list with pull-to-refresh
- BackupDetailView.swift: Details + restore on touch
- BackupSettingsView.swift: Storage gauge + mobile settings
- BackupViewModel.swift: Same state management as macOS

**Tests + Docs (4 files, 1,621 lines):**
- backup-service.test.js (418 lines): Unit tests
- backup-routes.test.js (499 lines): API endpoint tests
- BackupViewModel.test.swift (368 lines): Integration tests
- WEEK_5_BACKUP_SYSTEM.md (336 lines): Complete guide

### Critical Process Update
**GitHub Push Issue Discovered:**
- Claude Code subagents claim files are "pushed to GitHub" but often only commit locally
- **Solution:** Subagents commit, Momotaro (main session) handles all GitHub pushes
- **Verification:** Always check GitHub after push before reporting complete
- **Process updated:** CLAUDE_CODE_PROCESS.md now includes GitHub verification steps

### GitHub Status
- ✅ Commit: 127ae32 (Add comprehensive README)
- ✅ All Week 5 files visible on GitHub
- ✅ README.md deployed with architecture, API reference, troubleshooting
- ✅ URL: https://github.com/rdreilly58/onigashima

---

## Previous Session (March 11, 2026 - 4:15-6:25 AM)

**Major Accomplishments:**
1. ✅ Fixed morning and evening briefing systems
   - Updated scripts to use proper GA4 reporting format
   - Added comprehensive analytics: 7-day trends, traffic sources, top pages
   - Fixed cron PATH issues (gog not found)
   
2. ✅ Himalaya CLI Setup & Optimization
   - Created persistent config file: `~/.config/himalaya/config.toml`
   - Upgraded from v1.1.0 to v1.2.0 (fixes IMAP codec warnings)
   - Created email-stats.sh helper script
   - Integrated email metrics into briefings (unread, total, today)
   
3. ✅ Comprehensive briefing emails
   - Morning: 6:00 AM with 7-day analytics
   - Evening: 5:00 PM with daily analytics
   - Both include: GA4 metrics, traffic sources, top pages, email status
   
4. ✅ Email workflow optimized
   - Inbound: Himalaya CLI for reading/searching
   - Outbound: gog CLI for sending
   - Unified config persistence

**Technical Improvements:**
- Himalaya config with IMAP/SMTP credentials configured
- Email statistics script for quick briefing metrics
- Cron jobs using full paths to avoid PATH issues
- v1.2.0 features: improved query syntax, better IMAP handling

---

## Previous Session (March 10, 2026 - 6:00-7:15 AM)

**Major Accomplishments:**
1. ✅ Fixed morning briefing delivery system
   - Moved from broken OpenClaw cron agents to system cron
   - Switched from isolated agents (timeouts) to direct gog CLI
   - Now sends via `gog gmail send` reliably

2. ✅ Created professional PDF briefing system
   - Morning briefing: 6:00 AM EDT (email, calendar, GA4, priorities)
   - Evening briefing: 5:00 PM EDT (completed work, blockers, tomorrow's focus)
   - Both as PDF attachments with professional formatting
   - Uses reportlab for clean PDF generation

3. ✅ Sent Stripe environment setup PDF to Gmail
   - All configuration steps and resources included
   - Ready for environment variable setup in AWS Amplify

4. ✅ Set up GA4 access reminder
   - 9 AM daily reminder to grant service account permissions
   - Will enable analytics in briefings once completed

**Technical Fixes:**
- Debugged isolated agent timeouts (fixed by switching to system cron)
- Struggled with HTML-to-PDF conversion, settled on reportlab native approach
- HTML formatting issues in PDFs resolved with content extraction + native PDF generation

---

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
- **GA4 Property ID:** 526836321 ✓
- **Property Name:** ReillyDesignStudio
- **Service Account:** momo2analytics@rds-analytics-489420.iam.gserviceaccount.com
- **GA4 Analytics Setup:** ✅ WORKING
  - Service account key: `~/.openclaw/workspace/secrets/ga4-service-account.json` ✓
  - Service account has Viewer role on property ✓
  - Briefings now pulling live GA4 data ✓

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

### Personal Gmail (rdreilly2010@gmail.com)
- **Email:** rdreilly2010@gmail.com
- **Tools:** 
  - ✅ Himalaya CLI (IMAP/SMTP) — fully configured with password saved
  - ✅ Python IMAP Reader (`gmail_reader.py`) — direct IMAP access
  - ✅ Google CLI (gog) — Gmail send/search
- **Credentials:** App password saved in Himalaya config
- **Config:** ~/.config/himalaya/config.toml
- **Status:** ✅ Fully authenticated and working
- **Usage:**
  - Himalaya: `himalaya envelope list`, `himalaya message read <id>`
  - Python: `python3 ~/.openclaw/workspace/scripts/gmail_reader.py rdreilly2010@gmail.com <password> <command>`

### ReillyDesignStudio Work Account
- **Email:** robert.reilly@reillydesignstudio.com
- **Tool:** Himalaya CLI (IMAP/SMTP)
- **Status:** ⏳ Not yet authenticated (can set up if needed)
- **Config:** ~/.config/himalaya/config.toml
- **Note:** Only rdreilly2010@gmail.com is currently set up

## Gmail Access Setup (March 10, 11:45 AM)

### Tools Configured
1. **Himalaya CLI** — Full IMAP/SMTP email client
   - Interactive setup completed with wizard
   - Credentials stored securely in config
   - Commands: `himalaya envelope list`, `himalaya message read <id>`, `himalaya message reply <id>`

2. **Python IMAP Reader** — Direct Gmail API via imaplib
   - Script: `~/.openclaw/workspace/scripts/gmail_reader.py`
   - Usage: `python3 gmail_reader.py <email> <password> <command>`
   - Commands: search, list, read, example
   - No external dependencies (uses Python stdlib)

3. **Google CLI (gog)** — Already configured
   - OAuth authenticated
   - Limited message viewing but full send capability

### App Password
- Gmail App Password obtained: `xssl wrzz vfhb ypft`
- 2-Step Verification enabled on rdreilly2010@gmail.com
- Password stored in Himalaya config (not in version control)

### What We Discovered
- **March 7 Briefing Email:** Found in inbox (message ID 133268)
- **Content:** Text-only email (no PDF attachment), showed old GA4 setup issues
  - Used wrong property ID (G-HY3PW3N3TW)
  - Had metric name error ('unique_visitors' → should be 'activeUsers')
  - Failed to pull analytics data
- **March 7 vs March 10 Comparison:**
  - Old: Text-only, GA4 failing, basic format
  - New: Professional PDF, GA4 working, correct property ID (526836321)

---

## Daily Briefing Schedule

### Morning Briefing ✅
- **Time:** 6:00 AM EDT
- **Script:** `/Users/rreilly/.openclaw/workspace/scripts/morning-briefing-pro.py`
- **Cron:** `0 6 * * * /Users/rreilly/.openclaw/workspace/scripts/morning-briefing-pro.py`
- **Contents:** Email status, calendar (48h), GA4 stats (24h), top 3 priorities
- **Format:** PDF attachment (professional HTML rendered)
- **Status:** ✅ Tested & working

### Evening Briefing ✅
- **Time:** 5:00 PM EDT
- **Script:** `/Users/rreilly/.openclaw/workspace/scripts/evening-briefing-pro.py`
- **Cron:** `0 17 * * * /Users/rreilly/.openclaw/workspace/scripts/evening-briefing-pro.py`
- **Contents:** Completed items, GA4 daily stats, blockers, tomorrow's preview
- **Format:** PDF attachment (professional HTML rendered)
- **Status:** ✅ Tested & working

### Email & PDF Setup
- **Recipient:** rdreilly2010@gmail.com (Gmail account)
- **Email Tool:** `gog` (Gmail CLI, authenticated with service account)
- **PDF Converter:** `/Users/rreilly/.openclaw/workspace/scripts/html_to_pdf.py` (uses reportlab or xhtml2pdf)
- **Attachments:** PDFs sent via gog gmail send with `--attach` flag

### Known Issue: GA4 Permissions
- **Status:** Service account lacks Viewer role on GA4 property (GA4 metrics show as unavailable)
- **Fix:** Grant `momo2analytics@rds-analytics-489420.iam.gserviceaccount.com` Viewer role on ReillyDesignStudio property
  - Steps: https://analytics.google.com → Admin → Property → Property Access Management
  - Reminder scheduled for 9:00 AM daily
- **Impact:** Briefings still work fine without GA4 data; analytics will populate once access is granted

### System Architecture
- Using **system cron** (macOS native) instead of OpenClaw cron:
  - System cron runs independently, no OpenClaw overhead
  - Direct CLI access via `gog` and Python scripts works reliably
  - No timeout issues like isolated agents had
- Scripts log to `/tmp/morning-briefing.log` and `/tmp/evening-briefing.log`

---

## Key Decisions

1. Use Tuist for iOS project management (cleaner than raw Xcode)
2. Deployed ReillyDesignStudio to Amplify (AWS managed, auto-scaling)
3. Create reusable skills instead of one-off scripts
4. Store secrets in ~/.openclaw/workspace/secrets/ (not committed to Git)
5. Daily briefing emails at 6 AM and 5 PM for proactive engagement
