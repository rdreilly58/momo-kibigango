# ONIGASHIMA — FINAL DEVELOPMENT PLAN

**Date:** Wednesday, March 11, 2026, 2:51 PM EDT  
**Status:** ✅ LOCKED & READY TO BUILD  
**Your Decisions:**
1. ✅ 30 hours/week, 4 weeks
2. ✅ Build both backend + installer
3. ✅ Funding arrives Weeks 16-20
4. ✅ Weekly syncs Tuesday 10 AM EDT
5. ✅ MVP: Messaging + Backups + Updates

---

## FINAL TIMELINE

### Phase 1: Solo MVP Build (Weeks 1-6)

**Your commitment:** 30 hours/week  
**Goal:** Core features working (messaging, backups, updates)  
**Marketing parallel:** Survey + interviews

#### Week 1: Backend API (March 11-15)

**Focus:** 6 core API endpoints

**You'll build:**
- User registration + login (JWT)
- Device registration (Mac + iPhone)
- Message sending/receiving
- Version checking (for updates)
- Backup endpoint (basic)
- Support messaging (store requests)

**Code to start from:** `ONIGASHIMA_SOLO_BACKEND_STARTER.js`

**Tech:**
- Node.js + Express
- PostgreSQL (local or Heroku Postgres)
- JWT (jsonwebtoken)
- WebSocket (ws library)

**Effort:** 30 hours (full week)

**Deliverable:** 6 working API endpoints, deployed to Heroku

**Checklist:**
- [ ] Node.js project initialized
- [ ] PostgreSQL database created (local or cloud)
- [ ] Database schema set up (users, devices, messages, backups, versions)
- [ ] User registration endpoint works
- [ ] User login endpoint works
- [ ] Device registration endpoint works
- [ ] Message send endpoint works
- [ ] Message retrieve endpoint works
- [ ] Deployed to Heroku or Railway
- [ ] Tested with Postman or curl
- [ ] WebSocket server running

---

#### Week 2: macOS Installer (March 16-22)

**Focus:** SwiftUI installer, 4 screens

**You'll build:**
- Welcome screen
- Configuration screen (device name, API endpoint, install path)
- Progress screen (show installation in progress)
- Success screen (show QR code for pairing)
- Installation logic (copy files, setup launch agent)

**Design to follow:** `ONIGASHIMA_SOLO_INSTALLER_DESIGN.md`

**Tech:**
- SwiftUI (macOS target)
- QR code generation (CIFilter)
- File operations (FileManager)
- Process execution (for system commands)

**Effort:** 30 hours (full week)

**Deliverable:** Running installer app that creates `/Applications/Onigashima`, generates QR code

**Checklist:**
- [ ] Xcode project created (macOS target)
- [ ] WelcomeView built and styled
- [ ] ConfigView with TextFields for settings
- [ ] ProgressView with animation
- [ ] SuccessView with QR code display
- [ ] File copy logic (create app folder)
- [ ] Launch agent setup (auto-start on boot)
- [ ] QR code generation from pairing code
- [ ] Installer tested on local Mac
- [ ] App can be run multiple times safely
- [ ] Error handling for missing folders/permissions

---

#### Week 3: iPhone Pairing (March 23-29)

**Focus:** Add QR scanner + device pairing to Momotaro app

**You'll build:**
- QR code scanner (use camera)
- Parse scanned QR → get pairing code
- Register device with backend API
- Store JWT token securely (Keychain)
- Verify pairing succeeded

**Base:** Existing Momotaro-iOS app (extend, don't rebuild)

**Tech:**
- AVFoundation (camera + QR scanning)
- URLSession (API calls)
- Keychain (secure token storage)
- CodableKeys (JSON parsing)

**Effort:** 30 hours (full week)

**Deliverable:** iPhone can scan Mac's QR code → pair with backend

**Checklist:**
- [ ] QR scanner view created (camera access)
- [ ] QR parsing logic (extract pairing code)
- [ ] Device registration API call
- [ ] JWT token storage in Keychain
- [ ] Pairing verification (test connection)
- [ ] Error handling (invalid QR, network error, etc.)
- [ ] User feedback (success/failure messages)
- [ ] Tested end-to-end (scan real QR code)

---

#### Week 4: WebSocket & Real-Time Messaging (March 30-April 5)

**Focus:** Messages route in real-time (iPhone ↔ Backend ↔ Mac)

**You'll build:**
- WebSocket on backend (broadcast messages)
- WebSocket on macOS app (listen for messages)
- WebSocket on iPhone app (receive messages)
- Full message flow (send, receive, display)
- Connection state management

**Tech:**
- WebSocket (ws library on backend)
- URLSessionWebSocketTask (macOS + iPhone)
- Reconnection logic (exponential backoff)
- JSON message format

**Effort:** 30 hours (full week)

**Deliverable:** End-to-end messaging works (iPhone → Mac → iPhone)

**Checklist:**
- [ ] Backend WebSocket server implemented
- [ ] Device registration includes WebSocket token
- [ ] macOS app connects to WebSocket
- [ ] iPhone app connects to WebSocket
- [ ] Message send from iPhone → Backend receives
- [ ] Backend broadcasts to Mac → Mac receives
- [ ] Mac sends response → Backend receives
- [ ] Backend sends to iPhone → iPhone receives
- [ ] Connection recovery (auto-reconnect)
- [ ] Error handling (network drops)
- [ ] Tested full loop (message sends both ways)

---

#### Week 5: Backup System (April 6-12)

**Focus:** Store + restore encrypted backups to cloud

**You'll build:**
- Backup encryption (AES-256)
- Upload to S3 or similar
- Backup listing
- Restore functionality
- Automatic daily backups (scheduled)

**Tech:**
- Node.js crypto (encryption)
- AWS S3 or DigitalOcean Spaces (cheap storage)
- Cron jobs (schedule backups)
- Compression (zip before encrypting)

**Effort:** 30 hours (full week)

**Deliverable:** Backups work (create → upload → restore)

**Checklist:**
- [ ] S3 bucket created and configured
- [ ] Encryption key management (secure storage)
- [ ] Backup creation logic (tar + gzip + encrypt)
- [ ] Upload to S3 with progress
- [ ] Backup listing endpoint
- [ ] Restore endpoint (download + decrypt + extract)
- [ ] Scheduling (cron for daily backups)
- [ ] Tested: Create backup → Upload → Restore
- [ ] Size limits enforced
- [ ] Error handling (S3 failures, encryption errors)

---

#### Week 6: Auto-Updates System (April 13-19)

**Focus:** Distribute updates to Mac + iPhone

**You'll build:**
- Version checking endpoint
- Download endpoint (delta or full)
- Installation logic (macOS)
- Staged rollout (10% → 50% → 100%)
- Rollback if errors

**Tech:**
- Version comparison logic
- Delta updates (bsdiff) or full downloads
- Code signing (macOS, Apple)
- Rollout management (database)

**Effort:** 30 hours (full week)

**Deliverable:** Update system works (check → download → install)

**Checklist:**
- [ ] Version schema in database
- [ ] Latest version endpoint
- [ ] Download endpoint (full file)
- [ ] macOS updater logic (replace files, restart)
- [ ] iPhone auto-update (TestFlight or direct)
- [ ] Version mismatch handling
- [ ] Staged rollout logic (10% → 50% → 100%)
- [ ] Rollback procedure (if update fails)
- [ ] Tested: Update Mac → Verify works → Update iPhone
- [ ] Logs for troubleshooting

---

### Phase 2: Validation & Optimization (Weeks 7-8)

**Your focus:** Testing, market feedback, minor fixes

#### Week 7: Integration Testing (April 20-26)

- Test all flows end-to-end
- Load testing (100+ simultaneous devices)
- Security audit (basic)
- Database optimization
- Bug fixes from testing

**Deliverable:** MVP stable, ready for beta users

#### Week 8: Beta Launch (April 27 - May 3)

- Launch to 20-50 beta users
- Gather feedback
- Fix critical bugs
- Document known issues

**Deliverable:** Real user feedback, validated product

---

### Phase 3: Waiting for Contractors (Weeks 9-16)

**Timeline:** Weeks 9-16 (April-May)

**Your focus:**
- Collect 100+ survey responses
- Conduct 20+ user interviews
- Refine MVP based on feedback
- Plan Phase 2 features
- Prepare contractor handoff documentation

**Contractors:**
- When funding arrives (Weeks 16-20 estimate)
- They take over scaling, infrastructure, polish

**Deliverable by Week 16:**
- Validated product-market fit
- Clear Phase 2 feature list
- Production-ready code documentation
- Ready to scale

---

## WEEKLY SYNC SCHEDULE

**Time:** Tuesday 10:00 AM EDT  
**Attendees:** Bob + Momotaro  
**Duration:** 30 minutes  
**Format:** Progress update + blockers + decisions

### Schedule

| Date | Week | Focus | Agenda |
|------|------|-------|--------|
| Mar 18 | 1 | Backend API | API progress, database working? |
| Mar 25 | 2 | Installer | Installer building? QR code working? |
| Apr 1 | 3 | iPhone | QR scanner working? Pairing complete? |
| Apr 8 | 4 | WebSocket | End-to-end messaging working? |
| Apr 15 | 5 | Backups | Backup system working? S3 connected? |
| Apr 22 | 6 | Updates | Update system working? Staged rollout ready? |
| Apr 29 | 7 | Testing | Beta users recruited? Feedback gathered? |
| May 6 | 8 | Launch | Beta launch complete? Feedback collected? |

---

## PARALLEL: MARKETING TRACK

**Your time:** 5-10 hours/week (non-overlapping with development)

### Week 1-2 (March 11-22): Market Survey

- [ ] Create survey (15-20 questions)
- [ ] Post on Product Hunt, Reddit, Twitter, Hacker News
- [ ] Target: 50+ responses by March 22
- [ ] Questions cover: pricing, features, use cases, willingness to pay

### Week 3-4 (March 23-April 5): User Interviews

- [ ] Schedule 10+ interviews (30 min each)
- [ ] Interview questions prepared
- [ ] Conduct interviews async (email) or sync (Zoom)
- [ ] Collect feedback: problems, features, pricing

### Week 5-6 (April 6-19): Analysis & Refinement

- [ ] Analyze 50+ survey responses
- [ ] Summarize interview insights
- [ ] Identify top requested features
- [ ] Refine MVP based on feedback
- [ ] Update Phase 2 roadmap

### Week 7-8 (April 20 - May 3): Beta Recruitment

- [ ] Create beta signup page
- [ ] Email survey respondents (recruit 20-50 beta users)
- [ ] Prepare beta documentation
- [ ] Onboard beta testers
- [ ] Gather feedback from beta use

---

## DEVELOPMENT ENVIRONMENT SETUP (Before Week 1)

### Backend (by March 11)

- [ ] Node.js 18+ installed
- [ ] npm updated
- [ ] PostgreSQL installed locally (or Heroku Postgres account)
- [ ] Heroku CLI installed
- [ ] GitHub repo cloned
- [ ] .env file created with DB credentials
- [ ] npm dependencies installed (`express`, `pg`, `jsonwebtoken`, `bcrypt`, `ws`)

### Installer (by March 16)

- [ ] Xcode 14+ installed
- [ ] SwiftUI project created (macOS target)
- [ ] Code signing set up
- [ ] QR code library installed (if needed)

### iPhone (by March 23)

- [ ] Xcode iOS project open (Momotaro-iOS)
- [ ] Camera permissions configured
- [ ] QR scanning library installed (if needed)

---

## SUCCESS METRICS (By May 3)

### Technical (Week 8)
✅ 6 API endpoints working  
✅ Messaging end-to-end (iPhone ↔ Mac)  
✅ Backup system operational  
✅ Auto-update system working  
✅ 20-50 beta users testing  
✅ <5% critical bugs  
✅ API uptime >99%  
✅ Database stable  

### Business (Week 8)
✅ 50+ survey responses collected  
✅ 10+ user interviews conducted  
✅ Confirmed: Customers want this  
✅ Pricing validated ($99/year sweet spot)  
✅ 100+ people interested in beta  
✅ 20-50 beta users onboarded  
✅ Real user feedback documented  

### Product (Week 8)
✅ MVP works (rough UI acceptable)  
✅ Can demo to investors/customers  
✅ Clear understanding of Phase 2 needs  
✅ Phase 2 roadmap finalized  
✅ Production-ready code + documentation  

---

## CONTRACTOR HANDOFF (Weeks 16-20)

**When:** After funding arrives (estimate Weeks 16-20)

**Contractors will:**
1. **Polish installer** (2 weeks, $7K)
   - Professional UI/UX
   - Code signing + notarization
   - DMG installer package

2. **Scale infrastructure** (2 weeks, $8K)
   - AWS/DigitalOcean deployment
   - Database scaling
   - CDN + caching
   - Monitoring + alerting

3. **Add missing features** (2 weeks, $8K)
   - Tailscale integration
   - Hardware support (Mac mini)
   - Advanced settings

4. **QA + security** (1 week, $5K)
   - Load testing (1K+ devices)
   - Security audit
   - Bug fixes

**Total Phase 2 cost:** $28K (vs original $81K)

**Result:** Production-ready, ready to launch publicly

---

## WEEK 1 DETAILED BREAKDOWN (March 11-15)

### Daily Schedule

**Monday (March 11):**
- Setup: Node.js project structure
- Setup: PostgreSQL (local or cloud)
- Setup: Heroku account + CLI
- Setup: GitHub repo
- Create: Database schema (users, devices, messages, backups, versions)
- Start: User registration endpoint

**Tuesday (March 12):**
- Finish: User registration endpoint (test with Postman)
- Build: User login endpoint (JWT generation)
- Test: Both endpoints work
- Weekly sync: 10 AM (5 min update)

**Wednesday (March 13):**
- Build: Device registration endpoint
- Build: Device status endpoint
- Test: Both endpoints work
- Database: Verify data persists

**Thursday (March 14):**
- Build: Message send endpoint
- Build: Message retrieve endpoint
- Build: Version check endpoint
- Test: All endpoints work

**Friday (March 15):**
- Build: Backup endpoint (basic)
- Build: Support message endpoint
- Deploy: Push to Heroku
- Test: API works from external URL
- Document: API endpoints in README
- Success criteria: 6 endpoints live on Heroku

**Weekend (March 16):**
- Rest/review
- Prep for Week 2 (macOS installer)

---

## CRITICAL PATH

**Cannot start Week 2 without:**
- ✅ 6 API endpoints working + deployed

**Cannot start Week 3 without:**
- ✅ Installer building + showing QR code

**Cannot start Week 4 without:**
- ✅ iPhone pairing working

**Cannot ship MVP without:**
- ✅ End-to-end messaging working
- ✅ Backups functional
- ✅ Updates functional

---

## BLOCKERS & CONTINGENCY

### If Backend Takes Longer
**Plan:** Move WebSocket to Week 5, compress backup + update to Weeks 6-7

### If Installer Takes Longer
**Plan:** Simple command-line installer instead of GUI (can polish later)

### If iPhone Integration Fails
**Plan:** Use temporary QR code pairing (manual 6-digit code entry)

### If WebSocket Unreliable
**Plan:** Switch to polling (less elegant, but works)

**Key principle:** Rough > Perfect. Ship MVP, iterate with real users.

---

## RESOURCES

### Code Started From
- `ONIGASHIMA_SOLO_BACKEND_STARTER.js` (Week 1)
- `ONIGASHIMA_SOLO_INSTALLER_DESIGN.md` (Week 2)

### Learning (if you need refreshers)
- WebSocket: MDN docs
- SwiftUI: Apple docs + tutorials
- PostgreSQL: Official docs
- JWT: jwt.io

### Tools You'll Need
- Postman (API testing)
- Xcode (macOS/iOS development)
- VS Code (backend development)
- TablePlus or pgAdmin (database GUI)
- Heroku dashboard (deployment)

---

## SUMMARY

**Your commitment:**
- 30 hours/week, 6 weeks (not 4)
- Build backend + installer solo
- Parallel marketing validation
- Weekly syncs Tuesday 10 AM

**What you'll have by May 3:**
- Working MVP (messaging + backups + updates)
- 50+ survey responses + validated market
- 20-50 beta users
- Production-ready code + documentation
- Ready for contractors Week 16-20

**Cost:**
- $0 now (you building)
- $28K later (contractors polish + scale)
- vs $81K if hired day 1

**Timeline:**
- Week 1-6: You build + validate
- Week 7-16: Contractors join + scale
- Week 17+: Launch publicly

**Success criteria:**
- MVP works (rough UI fine)
- Market validated (50+ responses)
- Real users testing (20-50 beta)
- Product-market fit clear

---

## GO TIME

**Start:** Today, March 11, 2026  
**Week 1:** Backend API  
**Sync:** Tuesday 10 AM EDT  

**Ready to start?**

Let me know if you have any questions about Week 1 before you begin.

---

**Status:** ✅ LOCKED & FINAL  
**Owner:** Bob Reilly 🍑  
**Next:** Setup development environment, start Week 1 Monday
