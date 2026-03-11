# ONIGASHIMA — REVISED BOOTSTRAP PLAN SUMMARY

**Date:** Wednesday, March 11, 2026, 2:39 PM EDT  
**Change:** Shifted to solo bootstrap development (funding delays)  
**Status:** Ready for your review

---

## THE CHANGE

### Original Plan
- Hire contractors immediately (Week 1)
- Contractors build everything (Weeks 2-10)
- Launch in 10 weeks
- Cost: $81K upfront
- Risk: Scope creep, miscommunication

### New Plan ✅
- **You build MVP solo (Weeks 1-4)** ← KEY CHANGE
- Contractors join when funding arrives (Weeks 5+)
- MVP validates concept (rough but working)
- Launch in 16-20 weeks (more realistic)
- Cost: $0 now, $20-30K later (when you have money)
- Risk: Lower (you've proven it works before hiring)

---

## YOUR ROLE (Weeks 1-4)

### What You'll Build

**Week 1: Backend (6 API endpoints)**
- User registration + login (JWT)
- Device registration (Mac + iPhone)
- Message sending between devices
- Total: ~300-400 lines of Node.js code

**Week 2: macOS Installer (4 screens)**
- Welcome → Config → Progress → Success
- Creates `/Applications/Onigashima` folder
- Generates QR code for pairing
- Total: ~200-300 lines of SwiftUI code

**Week 3: iPhone Pairing**
- Add QR scanner to Momotaro app
- Register device with backend
- Store JWT token
- Total: ~100-150 lines of Swift code

**Week 4: End-to-End Communication**
- WebSocket on backend (real-time messages)
- WebSocket on Mac (listen for messages)
- iPhone sends → Mac receives → iPhone responds
- Total: ~150-200 lines across all platforms

### Time Commitment

**20-30 hours/week for 4 weeks** (roughly 5-7 hours per week per task)

### Why This Works

1. **You own the code** — Understand every part
2. **Learn before scaling** — Easy to manage contractors later
3. **Real MVP** — Build what's actually needed, not what you imagined
4. **Validation** — Collect 50+ survey responses + 10+ interviews in parallel
5. **Lower cost** — $0 now vs $81K upfront
6. **Lower risk** — Contractors extend proven code, not build from scratch

---

## WHAT YOU GET THIS WEEK (Documents Created)

### 1. ONIGASHIMA_BOOTSTRAP_PLAN.md (15 KB)
**Your detailed roadmap for solo development:**
- Week 1-4 solo build breakdown
- Week 5-12 contractor acceleration plan
- Parallel marketing track
- Success metrics
- Timeline (MVP Week 4 → Launch Week 16-20)

### 2. ONIGASHIMA_SOLO_BACKEND_STARTER.js (12 KB)
**Your starting point for backend:**
- 6 API endpoints (complete, ready to code)
- User registration + login (JWT)
- Device registration (Mac + iPhone)
- Message sending + WebSocket real-time delivery
- ~350 lines, production pattern, well-commented
- Already uses bcrypt + JWT (security best practices)

### 3. ONIGASHIMA_SOLO_INSTALLER_DESIGN.md (12 KB)
**Your SwiftUI installer specification:**
- 4 screens (Welcome → Config → Progress → Success)
- ASCII mockups
- Complete SwiftUI code examples for each screen
- QR code generation
- Installation logic
- File structure
- 15-20 hours to build

---

## TIMELINE COMPARISON

### Old Plan (Hire Day 1)
```
Mar 11: Hire contractors
Mar 16: Contractors start
Apr 13: Alpha done
Apr 28: Beta done
May 5: LAUNCH
Risk: High (depends on contractors)
Cost: $81K
```

### New Plan (Solo + Contractors)
```
Mar 11: YOU start building
Mar 15: Basic API working
Mar 22: Installer done
Mar 29: iPhone pairing done
Apr 5: MVP working end-to-end ✅
Apr 12: Market feedback (50+ responses)
May 3: Contractors join (when funded)
Jun 21: Fully polished
Jun 28: LAUNCH
Risk: Lower (you've validated concept)
Cost: $0 now, $20-30K later
```

---

## WHAT'S THE SAME

✅ **Target Customer:** Non-technical person with iPhone + Mac  
✅ **MVP Goal:** 15-min installation, QR pairing, message routing  
✅ **Market Size:** 2-5M users  
✅ **Revenue Model:** 3 tiers (software, hardware, cloud)  
✅ **Success Metric:** 100 paying customers by end of year  
✅ **Marketing Track:** Parallel validation with surveys + interviews

---

## WHAT'S DIFFERENT

| Aspect | Old Plan | New Plan |
|--------|----------|----------|
| **Development** | Contractors (Week 1-10) | You solo (Week 1-4) |
| **Launch** | Week 10 | Week 16-20 |
| **Cost** | $81K upfront | $0 now, $20-30K later |
| **Risk** | Higher (depends on contractors) | Lower (you've proven it) |
| **Contractor Scope** | Build from zero | Accelerate + polish |
| **Your Learning** | Oversight only | Deep ownership |
| **MVP Features** | Full 18 endpoints | Lean 6 endpoints |
| **Validation** | Before contractors | Before scaling |

---

## WEEK-BY-WEEK BREAKDOWN

### Week 1 (March 11-15)
**Your Task:** Backend API (6 endpoints)

Files you need:
- ONIGASHIMA_SOLO_BACKEND_STARTER.js ← Use this
- ONIGASHIMA_BOOTSTRAP_PLAN.md (Week 1 section)

What you'll do:
- Setup Node.js project
- Connect to PostgreSQL
- Implement /register, /login, /devices/register, /devices/{id}, /messages/send, /messages/{device_id}
- Deploy to Heroku ($50/month)

Effort: 15-20 hours  
Deliverable: 6 working API endpoints

### Week 2 (March 16-22)
**Your Task:** macOS Installer (4 screens)

Files you need:
- ONIGASHIMA_SOLO_INSTALLER_DESIGN.md ← Use this

What you'll do:
- Create SwiftUI macOS project
- Build Welcome screen
- Build Config screen (device name, API endpoint, path)
- Build Progress screen (installation progress)
- Build Success screen (show QR code)
- Implement installation logic (copy files, setup launch agent)
- Test installation

Effort: 15-20 hours  
Deliverable: Running installer with QR code

### Week 3 (March 23-29)
**Your Task:** iPhone Pairing (QR scanner + registration)

Files you need:
- ONIGASHIMA_BOOTSTRAP_PLAN.md (Week 3 section)
- Existing Momotaro-iOS app

What you'll do:
- Add QR code scanner to iPhone app
- Implement pairing flow (scan → register → store JWT)
- Test end-to-end (scan Mac's QR → register with backend)

Effort: 10-15 hours  
Deliverable: iPhone can pair with Mac

### Week 4 (March 30-April 5)
**Your Task:** End-to-End Communication (WebSocket)

Files you need:
- ONIGASHIMA_BOOTSTRAP_PLAN.md (Week 4 section)
- ONIGASHIMA_SOLO_BACKEND_STARTER.js (WebSocket section)

What you'll do:
- Add WebSocket to backend (broadcast messages to connected devices)
- Add WebSocket to macOS app (listen for messages)
- Implement message sending from iPhone
- Test full loop (iPhone → Backend → Mac)

Effort: 15-20 hours  
Deliverable: Full message routing works

---

## PARALLEL: MARKETING (Weeks 1-4)

**Your time:** 5-10 hours/week (non-overlapping with development)

- Week 1: Launch survey (Product Hunt, Reddit, Twitter)
- Week 2: Conduct interviews (10+ users)
- Week 3: Analyze feedback
- Week 4: Refine MVP based on feedback

**Deliverable:** 50+ survey responses, validated assumptions

---

## SUCCESS METRICS (April 5)

By end of Week 4, you should have:

✅ **Technical:**
- 6 API endpoints working
- macOS installer builds + runs
- iPhone pairs via QR code
- Messages route end-to-end
- Database stores everything
- API deployed ($5-$50/month)

✅ **Business:**
- 50+ survey responses
- 10+ user interviews
- Validated core assumptions
- 100+ people interested in beta

✅ **Product:**
- MVP works (rough UI is fine)
- Can demo to potential customers
- Clear understanding of what Phase 1 needs
- Confident in business model

---

## WHEN CONTRACTORS JOIN (Week 5+)

### What They'll Do
1. **Polish installer** (2 weeks) — Professional UI, code signing, DMG
2. **Build backup system** (2 weeks) — Encryption, cloud storage, restore
3. **Add auto-updates** (1 week) — Version checking, delta updates
4. **Setup infrastructure** (1 week) — AWS deployment, monitoring
5. **Add Tailscale** (1 week) — VPN tunnel, remote access
6. **QA + testing** (2 weeks) — Load testing, security, bug fixes

Total: 9 weeks, $20-30K

Result: Production-ready product

---

## BUDGET COMPARISON

### Old Plan
```
Week 1-10: Full contractor team ($81K)
├── Backend: $28.8K
├── Installer: $28.8K
├── DevOps: $12K
├── QA: $9.6K
└── Infrastructure: $1.8K

Risk: High
Launch: Week 10
Revenue: Week 11
```

### New Plan
```
Week 1-4: You ($0)
├── Backend: DIY
├── Installer: DIY
├── Testing: DIY
└── Infrastructure: DIY

Week 5-13: Contractors when funded ($20-30K)
├── Polish: $7K
├── Features: $10K
├── Infrastructure: $3.5K
└── QA: $5K

Risk: Lower
Launch: Week 16-20
Revenue: Week 17-21
```

---

## QUESTIONS TO ANSWER (Review)

1. ✅ **Can you commit 20-30 hours/week for 4 weeks?**
   - Or do you need to extend to 6-8 weeks?

2. ✅ **Do you want to build backend, installer, or both?**
   - Or hire one specialist early (e.g., backend engineer)?

3. ✅ **What's your funding timeline?**
   - When will investment money arrive?
   - This determines when contractors join (Week 5 vs Week 12)

4. ✅ **What's your definition of MVP?**
   - Just messaging (what we have)?
   - Or messaging + backups (add 2 weeks)?

5. ✅ **Do you want weekly syncs with Momotaro?**
   - Yes, keep Tuesday 10 AM?
   - Or adjust based on your schedule?

---

## NEXT STEPS

### If You Agree to This Plan:

1. **Review all 3 new documents:**
   - ONIGASHIMA_BOOTSTRAP_PLAN.md (detailed roadmap)
   - ONIGASHIMA_SOLO_BACKEND_STARTER.js (code to build from)
   - ONIGASHIMA_SOLO_INSTALLER_DESIGN.md (design to follow)

2. **Set up development environment (before Week 1):**
   - Node.js + Express
   - PostgreSQL (local or free tier)
   - Heroku account (deploy backend)
   - SwiftUI project (macOS)

3. **Confirm timeline:**
   - Week 1 start: March 11 (today)
   - Week 4 MVP: April 5
   - Contractors: Week 5 or later (when funded)

4. **Schedule weekly syncs:**
   - Tuesday 10 AM EDT
   - Bob + Momotaro
   - 30-min check-ins to stay aligned

5. **Start marketing track in parallel:**
   - Survey design by March 15
   - Launch by March 18

---

## BOTTOM LINE

**Old approach:** Hire contractors, wait 10 weeks, hope it works  
**New approach:** Build MVP yourself in 4 weeks, validate with customers, then hire contractors to scale

**Why it's better:**
- You learn the code
- You validate the concept
- You save $81K upfront
- You reduce risk (lower stakes)
- You still launch in 16-20 weeks (realistic)
- You have paying customers and real feedback

**The trade-off:**
- Your time (20-30 hours/week for 4 weeks)
- Slightly longer timeline (6-10 extra weeks)
- But you own the product and the knowledge

---

## FILES & LOCATIONS

All files committed to GitHub + workspace:

**For this week's review:**
- `ONIGASHIMA_BOOTSTRAP_PLAN.md` — Full roadmap (read this first)
- `ONIGASHIMA_SOLO_BACKEND_STARTER.js` — Backend code to start from
- `ONIGASHIMA_SOLO_INSTALLER_DESIGN.md` — Installer design to follow

**Supporting docs:**
- `ONIGASHIMA_TECHNICAL_ARCHITECTURE.md` (updated with Phase 1/2 notes)
- `ONIGASHIMA_EXECUTION_TRACKS.md` (updated with timeline)

**GitHub:**
- https://github.com/rdreilly58/onigashima (PRIVATE)
- All files committed and pushed

---

## 🍑 RECOMMENDATION

**This is the right move.** Here's why:

1. **You're a capable engineer** — Can build this solo in 4 weeks
2. **Early validation is gold** — 50+ survey responses > no data
3. **Cost savings are real** — $81K later is a lot cheaper than $81K now
4. **Risk is lower** — You've proven concept before scaling
5. **Market timing is better** — More time to adjust based on feedback
6. **You maintain control** — Contractors extend your vision, not build it

**The path forward:**
- Week 1-4: Build MVP solo (validate concept + market)
- Week 5-12: Contractors accelerate (when funding arrives)
- Week 16-20: Launch with confidence

---

**Status:** Ready for your review  
**Owner:** Bob Reilly + Momotaro 🍑  
**Next:** Confirm plan and start Week 1 (March 11)

Questions? Concerns? Let me know what you'd like to adjust.
