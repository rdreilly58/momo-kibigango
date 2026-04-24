# ONIGASHIMA — BOOTSTRAP DEVELOPMENT PLAN

**Date:** Wednesday, March 11, 2026, 2:39 PM EDT  
**Status:** ✅ REVISED FOR SOLO DEVELOPMENT  
**Timeline:** 12 weeks solo → contractors join when funding arrives

---

## NEW APPROACH: Solo Bootstrap First

### Key Changes

**OLD PLAN:**
- Week 1: Hire contractors
- Week 2-10: Contractors build MVP
- Week 10: Launch

**NEW PLAN:**
- Week 1-4: You build MVP solo (lean & focused)
- Week 5-12: Contractors accelerate (when funding arrives)
- Week 12-16: Scale & polish
- Launch: Week 16-20 (more realistic, less pressure)

### Why This Works

1. **You own the architecture** — No miscommunication with contractors
2. **Learn the codebase** — Easy to manage contractors later
3. **Reduce scope** — Solo forces you to cut to essentials
4. **De-risk hiring** — You validate product before paying for team
5. **Real MVP** — Build what customers actually need, not what you imagined
6. **Control costs** — Spend $0 now, $20K-$30K later on contractors

---

## SOLO DEVELOPMENT TRACK (Weeks 1-4)

### Your Time Investment

**Realistic Weekly Commitment:**
- 20-30 hours/week on Onigashima development
- Parallel marketing continues (survey, user interviews)
- Keep ReillyDesignStudio operations running

**Focus:** Core MVP only (not Phase 1 features)

### What You'll Build Solo (Weeks 1-4)

#### Week 1: Backend Foundation (March 11-15)
**Goal:** Minimal working API (6 endpoints)

**What to build:**
1. **Auth endpoints (2):**
   - `/register` — email + password → JWT token
   - `/login` — email + password → JWT token

2. **Device endpoints (2):**
   - `/devices/register` — register Mac installation
   - `/devices/{id}/status` — report device health

3. **Support endpoint (1):**
   - `/support/messages` — store support requests (for you to read)

4. **Update endpoint (1):**
   - `/versions/latest` — return current version number

**Tech Stack:**
- Node.js + Express (you know this already)
- PostgreSQL (local dev database, cheap cloud later)
- JWT for auth (simple, stateless)
- Environment variables for config

**Deliverable:** 6 working endpoints, minimal error handling, deployed to local or $5 cloud server

**Effort:** 15-20 hours

#### Week 2: Installer Foundation (March 16-22)
**Goal:** Non-technical visual wizard (proof of concept)

**What to build:**
1. **Welcome screen** — explain what Onigashima is
2. **System check** — verify Mac meets requirements
3. **Installation path** — where to install files
4. **Configuration** — API endpoint URL + device name
5. **Installation** — copy files, setup permissions, create launch agent
6. **Success screen** — show QR code (phone scans this to pair)

**Tech Stack:**
- SwiftUI (you're familiar with this)
- macOS app bundle (not installer PKG yet)
- Launch agent for auto-start
- QR generation (simple library)

**Deliverable:** Working prototype (installs OpenClaw, starts on boot, shows QR code)

**Effort:** 15-20 hours

**Note:** Don't worry about fancy UI. Get it working. Polish later.

#### Week 3: iPhone Pairing (March 23-29)
**Goal:** iPhone can pair with Mac, send test messages

**What to build:**
1. **QR code scanner** — scan Mac's pairing QR code
2. **Device registration** — send device info to backend API
3. **JWT storage** — save token locally on iPhone
4. **Test message send** — send "hello world" to Mac

**Tech Stack:**
- Momotaro iOS (use existing app as base)
- Camera + AVFoundation for QR scanning
- URLSession for API calls
- Keychain for token storage (secure)

**Deliverable:** iPhone app can scan QR → register with backend → send messages to backend API

**Effort:** 10-15 hours

#### Week 4: Mac ↔ iPhone Communication (March 30-April 5)
**Goal:** Message routing works (iPhone → Mac → iPhone)

**What to build:**
1. **Mac WebSocket connection** — connects to backend, listens for messages
2. **Message routing** — backend receives message from iPhone, sends to Mac
3. **Mac response** — Mac processes message, sends response back
4. **iPhone receives response** — iPhone app shows message from Mac

**Tech Stack:**
- WebSocket on backend (Socket.io or ws library)
- WebSocket on Mac (URLSessionWebSocketTask)
- Simple message format (JSON with device_id, content)

**Deliverable:** Full loop works — iPhone → Backend → Mac → Backend → iPhone

**Effort:** 15-20 hours

### Summary: Week 1-4 Solo Build

| Week | Component | Goal | Effort | Deliverable |
|------|-----------|------|--------|-------------|
| 1 | Backend | 6 endpoints working | 15-20h | Minimal API |
| 2 | Installer | Visual wizard | 15-20h | macOS app |
| 3 | iPhone pairing | QR registration | 10-15h | Pairing works |
| 4 | Communication | Message routing | 15-20h | End-to-end working |

**Total Effort:** 55-75 hours (2-3 weeks for you)  
**Result:** Working MVP (rough, but functional)

---

## WHAT YOU'RE NOT BUILDING (YET)

❌ Fancy UI (basic is fine)  
❌ Backup system (manual for now)  
❌ Automatic updates (manual updates)  
❌ Cloud services (local only)  
❌ Hardware (Mac mini pre-configured)  
❌ Tailscale integration (direct IP for now, add Tailscale later)  
❌ Remote support tunnel (can do peer-to-peer SSH manually)  
❌ Production deployment (run on laptop, upgrade later)

**Why:** Solo, 4 weeks, focused on ONE thing: Does the core concept work?

---

## PHASE 1: CONTRACTOR ACCELERATION (Weeks 5-12)

**When:** After funding arrives (estimate: Week 5-12, but could be Week 16)

**What contractors do:**
1. **Polish installer** (2 weeks, $7K)
   - Professional UI/UX
   - Error handling
   - Code signing + notarization
   - Installer package (DMG)

2. **Build backup system** (2 weeks, $7K)
   - Encryption
   - Cloud storage (S3)
   - Restore functionality

3. **Add automatic updates** (1 week, $3.5K)
   - Update checking
   - Delta updates
   - Rollback safety

4. **Setup cloud infrastructure** (1 week, $3.5K)
   - AWS/DigitalOcean deployment
   - Database migration
   - Monitoring + logging
   - CDN for downloads

5. **Tailscale integration** (1 week, $3.5K)
   - VPN tunnel setup
   - Remote device access
   - Security hardening

6. **Testing + QA** (2 weeks, $7K)
   - Load testing
   - Security audit
   - Bug fixes

**Total Phase 1:** 9 weeks, $32K (much less than $81K for full build)

---

## PARALLEL TRACK: MARKETING (Weeks 1-12)

**Your weekly commitment:** 5-10 hours

**Week 1-4 (Concurrent with backend):**
- Launch market survey (Product Hunt, Reddit, Twitter)
- Collect 50+ responses
- Conduct 10+ user interviews
- Validate assumptions about customer needs

**Week 5-8:**
- Analyze survey data
- Create marketing website (or simple landing page)
- Build email list (100+ users interested)
- Plan Phase 1 launch strategy

**Week 9-12:**
- Prepare beta launch
- Create marketing materials
- Reach out to early adopters
- Setup support channel (Discord/Slack)

**Deliverable by Week 12:** 100+ beta signups, validated demand

---

## REALISTIC TIMELINE (REVISED)

### Solo Build Phase (Weeks 1-4)

| Date | Milestone | Status |
|------|-----------|--------|
| Mar 11 | Start development | ✅ Today |
| Mar 15 | Basic API working | ⏳ Week 1 |
| Mar 22 | Installer prototype | ⏳ Week 2 |
| Mar 29 | iPhone pairing | ⏳ Week 3 |
| Apr 5 | MVP working end-to-end | ⏳ Week 4 |

### Validation Phase (Weeks 5-8)

| Date | Milestone |
|------|-----------|
| Apr 12 | Market feedback (survey results) |
| Apr 19 | Pivot/refine based on feedback |
| Apr 26 | MVP refined with user feedback |
| May 3 | Ready for beta (20 users) |

### Acceleration Phase (Weeks 9-16)

| Date | Milestone |
|------|-----------|
| May 10 | Contractors onboarded (if funded) |
| May 24 | Installer polished, backups working |
| Jun 7 | Automatic updates, cloud infrastructure |
| Jun 21 | Full features, ready for scale |

### Launch Phase (Weeks 17+)

| Date | Milestone |
|------|-----------|
| Jun 28 | Public launch |
| Jul 5 | First 100 customers (if marketing works) |
| Aug | Evaluate if Phase 2 expansion needed |

---

## TECHNOLOGY CHOICES (Optimized for Solo)

### Backend
- **Framework:** Node.js + Express (simple, you know it)
- **Database:** PostgreSQL (powerful but not overkill)
- **Deployment:** Heroku or Railway ($50-$100/month, easy to manage solo)
- **Messaging:** Socket.io for WebSockets (battle-tested)

**Why:** You can manage this solo. Simple enough for contractors to extend later.

### Installer (macOS)
- **Technology:** SwiftUI (you're building Momotaro-iOS anyway)
- **Deployment:** DMG installer (sign + notarize later with contractor)
- **Approach:** Build as regular app first, wrap in installer later

**Why:** You know SwiftUI. Can build functional UI in 1-2 weeks.

### iPhone App
- **Use existing:** Momotaro iOS (don't rebuild, extend)
- **Add:** QR scanner, device pairing, API integration
- **Keep:** Most existing Momotaro features

**Why:** You already have working app. Just add pairing flow.

### Infrastructure
- **Dev:** Local Postgres + local Node server
- **Testing:** Docker (optional, can skip for now)
- **Production:** Heroku + AWS S3 (when contractors arrive)

**Why:** Minimal setup for solo. Easy to scale later.

---

## ARCHITECTURE CHANGES FOR SOLO BUILD

### Simplified Data Model

**Users Table:**
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Devices Table:**
```sql
CREATE TABLE devices (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id),
  device_name VARCHAR(255),
  pairing_code VARCHAR(6), -- simple 6-digit code (user enters manually)
  registered_at TIMESTAMP DEFAULT NOW(),
  last_seen TIMESTAMP
);
```

**Messages Table:**
```sql
CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  from_device_id INT NOT NULL REFERENCES devices(id),
  to_device_id INT NOT NULL REFERENCES devices(id),
  content TEXT,
  status VARCHAR(50), -- sent, delivered, read
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Note:** Drop `pairings`, `backups`, `support_messages` tables for now. Add them in Phase 1.

### Simplified API (6 endpoints, not 18)

**Auth:**
- `POST /register` — email, password → JWT
- `POST /login` — email, password → JWT

**Devices:**
- `POST /devices/register` — device_name, pairing_code → device_id
- `GET /devices/{id}` — get device info

**Messages:**
- `POST /messages/send` — from_device_id, to_device_id, content → message_id
- `GET /messages/{device_id}` — get messages for device

**That's it.** No backup endpoints, no update endpoints, no support endpoints. Add those in Phase 1.

### Simplified Installer (4 screens, not 7)

1. **Welcome** — "This installs Onigashima on your Mac"
2. **Settings** — Choose install location, device name
3. **Progress** — Show installation in progress
4. **Success** — Show QR code (user scans with iPhone)

**No error handling screens yet.** Keep it simple.

### Simplified iPhone Pairing (3 steps)

1. **Open Momotaro app** → new "Pair Device" button
2. **Scan QR code** → get pairing code
3. **Auto-register** → app registers with backend using pairing code

**Done.** User is paired.

---

## YOUR WEEKLY SCHEDULE (Weeks 1-4)

### Week 1 (March 11-15)
**Focus: Backend API**

Monday-Tuesday:
- Setup Node.js project structure
- Setup PostgreSQL (local or free tier)
- Implement JWT auth
- Deploy to Heroku ($50/month)

Wednesday-Friday:
- Implement 6 API endpoints
- Write basic tests
- Document API (README)

**Goal:** API accessible at `https://onigashima-api.herokuapp.com`, 6 endpoints working

### Week 2 (March 16-22)
**Focus: macOS Installer**

Monday-Wednesday:
- Create SwiftUI project (macOS target)
- Build 4 UI screens
- Connect to API

Thursday-Friday:
- Bundle as app
- Test installation flow
- Create QR code generator

**Goal:** Running app that installs files and shows QR code

### Week 3 (March 23-29)
**Focus: iPhone Pairing**

Monday-Tuesday:
- Add QR scanner to Momotaro
- Implement pairing flow
- Store auth token

Wednesday-Friday:
- Test pairing end-to-end
- Fix bugs
- Document flow

**Goal:** iPhone can scan QR → register with backend

### Week 4 (March 30-April 5)
**Focus: End-to-End Communication**

Monday-Wednesday:
- Implement WebSocket on backend
- Implement WebSocket on macOS
- Implement message sending on iPhone

Thursday-Friday:
- Test end-to-end
- Fix bugs
- Deploy updated API

**Goal:** Send message from iPhone → received by Mac

---

## SUCCESS METRICS (Week 4)

By April 5, you should have:

✅ **Technical:**
- Minimum 6 API endpoints working
- macOS installer builds and runs
- iPhone app pairs with Mac
- Messages route end-to-end
- Database stores data
- API deployed to $5-$50/month server

✅ **Business:**
- 50+ survey responses collected
- 10+ user interviews conducted
- Validated core assumption (do customers want this?)
- Email list of 100+ interested users

✅ **Product:**
- MVP works (rough UI acceptable)
- Can demonstrate to potential customers
- Have 20 beta testers ready
- Clear understanding of what Phase 1 needs

---

## WHEN CONTRACTORS JOIN (Week 5+)

### Handoff Process

1. **Code is clean but unpolished**
   - Documented
   - Tests written
   - Architecture clear
   - Contractors understand what works

2. **Contractors polish, don't rebuild**
   - Add professional UI
   - Add missing features (backups, updates)
   - Deploy to production
   - Handle scale

3. **You focus on marketing + product**
   - Gather user feedback
   - Plan Phase 1 features
   - Build community
   - Validate business model

---

## BUDGET COMPARISON

### Old Plan (Hire Day 1)
- Week 1-10: Full contractor team build MVP
- Cost: $81K upfront
- Risk: Miscommunication, scope creep
- Launch: Week 10
- Revenue: $0 (no time to validate)

### New Plan (Solo First)
- Week 1-4: You build MVP solo ($0)
- Week 5-12: Contractors accelerate ($20-$30K when funded)
- Week 12-20: Launch and scale
- Cost: $20-$30K total (vs $81K)
- Risk: Lower (you've proven it works)
- Revenue: Starts week 20, but with validated market

---

## CRITICAL SUCCESS FACTORS

1. **Scope discipline** — Build ONLY the 6 endpoints, 4 screens. Nothing more.
2. **Marketing parallel** — Survey + interviews must happen Week 1-4. Don't skip.
3. **Code quality** — Write clean code from day one. Contractors will extend it.
4. **Documentation** — Every decision, every API, every screen flow. Document it.
5. **Weekly syncs** — Momotaro + Bob every Tuesday 10 AM. Stay aligned.

---

## QUESTIONS TO ANSWER

1. **Can you commit 20-30 hours/week for 4 weeks?** (Or do you need to adjust timeline to 6-8 weeks?)
2. **Do you want to build backend, installer, or both?** (Could hire contractor for one piece early)
3. **What's your target funding timeline?** (Affects contractor start date)
4. **Should we aim for Week 4 MVP or Week 8 MVP?** (More time = more features, less risk)

---

## NEXT STEPS

1. **Review this plan** with Momotaro
2. **Decide scope** — what's MVP vs Phase 1?
3. **Set up environment** — Node.js, PostgreSQL, Heroku
4. **Start Week 1** — Backend foundation
5. **Weekly syncs** — Tuesday 10 AM, review progress

---

**Status:** Ready to pivot to solo bootstrap  
**Owner:** Bob Reilly + Momotaro 🍑  
**Timeline:** 4 weeks to MVP (rough), 12+ weeks to launch  
**Cost:** $0 now, $20-30K later (vs $81K upfront)

Let's build this lean. 🍑🏝️
