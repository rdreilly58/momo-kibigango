# Implementation Roadmap - 4 Hours/Week

**Start Date:** March 16, 2026  
**Time Allocation:** 4 hours/week  
**Total Duration:** 12-14 weeks to full implementation

---

## 📅 WEEK-BY-WEEK BREAKDOWN

### WEEK 1 (Mar 16-22) - TIER 1 QUICK WINS - 3 hours

#### Session 1a: Healthchecks.io Setup (45 min)
- [ ] Create Healthchecks.io account (free)
- [ ] Create 3 checks: Morning Briefing, Evening Briefing, Gas Prices
- [ ] Get check URLs (hc-ping.com/YOUR_UUID)
- [ ] Document URLs in TOOLS.md

#### Session 1b: Swift-Expert Installation (30 min)
- [ ] Complete clawhub install swift-expert
- [ ] Verify installation: `which swift-expert`
- [ ] Create iOS workspace: `~/momotaro-ios` (if not exists)
- [ ] Document skill details in TOOLS.md

#### Session 1c: Next.js Audit (90 min)
- [x] Analyze app architecture (DONE ✓)
- [x] Cost comparison (DONE ✓)
- [x] Create audit report (DONE ✓)
- [ ] **Action:** Review AWS bill to validate cost estimates
- [ ] Document findings in TOOLS.md under "Projects > ReillyDesignStudio"

---

### WEEK 2 (Mar 23-29) - CONFIG AUDIT - 3.5 hours

#### Session 2a: System Config Audit (90 min)
- [ ] Find all API keys in ~/.openclaw/config.json
- [ ] Document each in TOOLS.md:
  - [ ] Brave API key (done ✓)
  - [ ] Other keys (audit)
- [ ] Check for Stripe keys, AWS credentials
- [ ] Add validation dates

#### Session 2b: Skill Version Audit (60 min)
- [ ] Run: `clawhub list --installed`
- [ ] Pin versions in TOOLS.md
- [ ] Check for outdated skills
- [ ] Create quarterly update reminder

#### Session 2c: iOS Dev Kickoff (90 min)
- [ ] Spawn Claude Code agent for iOS setup
- [ ] Create Momotaro iOS project scaffold
- [ ] Set up WebSocket dependencies (Starscream)
- [ ] First commit to ~/momotaro-ios

---

### WEEK 3-4 (Mar 30-Apr 12) - CRON & MONITORING - 4 hours/week

#### Session 3a: Add Healthchecks.io to Crons (120 min)
- [ ] Update Morning Briefing cron:
  - [ ] Add healthcheck ping on completion
  - [ ] Set grace time: 5 minutes
  - [ ] Set alert: Telegram
- [ ] Update Evening Briefing cron
- [ ] Update Gas Prices cron
- [ ] Test: Manually trigger one, verify ping

#### Session 3b: GA4 BigQuery Prep (120 min)
- [ ] Link GA4 to BigQuery (if not done)
- [ ] Verify data is streaming
- [ ] Test query: Recent events (last 24h)
- [ ] Document connection in TOOLS.md

---

### WEEK 4-5 (Apr 13-26) - GA4 AUTOMATION - 4 hours/week

#### Session 4a: BigQuery Scheduled Queries (150 min)
- [ ] Create scheduled query: Daily summary (6:00 AM)
- [ ] Create scheduled query: Weekly trends (Mon 6:00 AM)
- [ ] Export to GCS bucket
- [ ] Test email delivery

#### Session 4b: Briefing Enhancement (90 min)
- [ ] Update cron jobs to attach GA4 exports
- [ ] Add cost metrics (AWS Cost Explorer)
- [ ] Add uptime metrics (Route53 health)
- [ ] Test full briefing flow

---

### WEEK 6-8 (Apr 27-May 10) - iOS DEVELOPMENT - 4 hours/week

#### Session 5-7: Momotaro iOS Milestones
**Spawn Claude Code (iOS) agent for:**
- [ ] WebSocket connection to OpenClaw gateway
- [ ] Authentication flow (OAuth/token)
- [ ] Message relay UI
- [ ] Real-time status indicators
- [ ] Error handling & reconnection logic

**Iterate on:**
- [ ] UI/UX review
- [ ] Performance profiling
- [ ] Beta testing on simulator

---

### WEEK 9-10 (May 11-24) - ROUTE53 COMPLETION - 4 hours/week

#### Session 8a: Domain Transfer Completion (120 min)
- [ ] Get authorization code from Cloudflare
- [ ] Complete Route53 domain transfer
- [ ] Verify nameserver propagation
- [ ] Update DNS records in Route53

#### Session 8b: CloudFront Setup (150 min)
- [ ] Create CloudFront distribution
- [ ] Point to Amplify app as origin
- [ ] Enable caching rules
- [ ] Update Route53 to CloudFront alias
- [ ] Test SSL/TLS

---

### WEEK 11-12 (May 25-Jun 7) - EMAIL & SCALING - 4 hours/week

#### Session 9a: Email Infrastructure Review (120 min)
- [ ] Evaluate: Keep Gmail vs. Resend/SendGrid
- [ ] Document decision in TOOLS.md
- [ ] If switching: Migrate one cron job to test
- [ ] Monitor deliverability

#### Session 9b: Documentation & Cleanup (120 min)
- [ ] Update TOOLS.md with all findings
- [ ] Create runbooks for each automation
- [ ] Document API limits & quotas
- [ ] Archive old deployment docs

---

## 🎯 QUICK REFERENCE - WHAT TO DO RIGHT NOW

**TODAY (This session):**

1. ✅ Read audit report (you're doing this now)
2. **Go here:** https://healthchecks.io
   - Sign up (free account)
   - Create 3 checks for your cron jobs
   - Copy the URLs (hc-ping.com/...)
   - **Come back** and give me the URLs
3. Next 2-3 hours: Implementation sessions follow

---

## 📊 PROGRESS TRACKER

| Task | Status | Owner | Due |
|------|--------|-------|-----|
| Healthchecks.io setup | ⏳ Pending | Bob | TODAY |
| Swift-expert install | 🔄 Running | Momotaro | TODAY |
| Next.js audit | ✅ DONE | Momotaro | TODAY |
| Config audit | ⏳ Pending | Momotaro | Mar 23 |
| Cron monitoring | ⏳ Pending | Momotaro | Apr 5 |
| GA4 automation | ⏳ Pending | Momotaro | Apr 26 |
| iOS development | ⏳ Pending | Claude Code | May 10 |
| Route53 migration | ⏳ Pending | Bob + Momotaro | May 24 |

---

## 📝 HOW TO USE THIS ROADMAP

**Weekly check-in:**
1. Review this file Monday morning
2. Complete 4 hours of tasks
3. Update status above
4. Add notes in MEMORY.md or memory/2026-XX-XX.md

**If tasks slip:**
- Push to next week (don't skip)
- Document blocker in MEMORY.md
- Adjust timeline if needed

**Session ownership:**
- **Bob:** Manual steps (Healthchecks, auth codes, approvals)
- **Momotaro:** Automation, scripting, configuration
- **Claude Code:** iOS development

---

## 🚀 SUCCESS CRITERIA

**By June 7, 2026:**
- ✅ All cron jobs monitored + alerted
- ✅ GA4 automation integrated into briefings
- ✅ iOS development progressing (MVP ready)
- ✅ Domain migrated to Route53
- ✅ CloudFront caching active
- ✅ Email infrastructure documented

**Estimated savings/improvements:**
- 🔴 Risk reduction: 90% (cron job visibility)
- ⚡ Development speed: +30% (iOS tooling)
- 💰 Infrastructure: 15-25% savings potential (CloudFront)
- 📊 Analytics: +50% deeper insights (GA4 automation)

---

**Questions? Ask. Blockers? Note them. Let's ship! 🍑**
