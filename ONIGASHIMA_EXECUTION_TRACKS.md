# ONIGASHIMA — EXECUTION TRACKS

**Date:** Wednesday, March 11, 2026, 2:24 PM EDT  
**Decision:** Approve parallel tracks (marketing + technical development)  
**Status:** Both tracks live and active

---

## 🎯 TWO PARALLEL TRACKS

### Track A: MARKETING & BUSINESS (Phase 0)
**Timeline:** Weeks 1-3 (March 11-29)  
**Owner:** Bob Reilly  
**Goal:** Validate market, hire contractors, create design mockups, finalize architecture

**Week 1 Tasks (March 11-15):**
- [ ] Launch market survey (50+ target)
- [ ] Post contractor jobs (designer, engineers)
- [ ] Create Figma design project
- [ ] Schedule weekly sync (Tuesdays 10 AM)
- [ ] Create team communication channel

**Week 2 Tasks (March 16-22):**
- [ ] Collect 50+ survey responses
- [ ] Conduct 10+ user interviews
- [ ] Hire design contractors
- [ ] Hire engineering contractors
- [ ] Approve installer mockups

**Week 3 Tasks (March 23-29):**
- [ ] Analyze market data
- [ ] Finalize Phase 1 budget
- [ ] Make GO decision for Phase 1
- [ ] Onboard contractors
- [ ] Plan launch strategy

**Deliverable:** Validated market, contractor team ready, Phase 1 budget approved

---

### Track B: MVP TECHNICAL DEVELOPMENT
**Timeline:** Weeks 1-9 (March 11-April 27)  
**Owner:** Momotaro (Product) + Claude Code (Architecture)  
**Goal:** Build working MVP for iPhone + Mac, 100 users, live by April 28

**Week 1: Technical Design (March 11-15) — IN PROGRESS**
- [ ] Architecture design (Claude Code)
- [ ] API specification (OpenAPI)
- [ ] Database schema (PostgreSQL)
- [ ] Installer design (SwiftUI mockups)
- [ ] Backend starter code (Node.js)
- **Deliverable:** Ready for development

**Week 2-3: Backend Development (March 16-29)**
- [ ] Setup AWS/DigitalOcean infrastructure
- [ ] Database setup + migrations
- [ ] Auth endpoints (register, login)
- [ ] Device registration API
- [ ] Pairing verification endpoint
- [ ] Backup endpoints
- [ ] Update check endpoint
- [ ] Support message endpoint
- **Deliverable:** Working backend API

**Week 4-6: Installer + App (March 30 - April 13)**
- [ ] macOS installer (SwiftUI)
- [ ] iPhone app updates (QR pairing, support)
- [ ] Tailscale integration (both sides)
- [ ] Testing + refinement
- **Deliverable:** Alpha MVP (internal testing)

**Week 7-9: Polish + Beta (April 14-27)**
- [ ] Bug fixes
- [ ] Documentation
- [ ] Beta testing (20-50 users)
- [ ] Support infrastructure
- [ ] Marketing materials
- **Deliverable:** Beta MVP ready for launch

**Week 10: Launch (April 28)**
- [ ] Public launch to first 100 customers
- [ ] Monitor + iterate
- [ ] Gather feedback
- **Deliverable:** MVP live, 100 users, revenue flowing

---

## 📊 RESOURCE ALLOCATION

### Track A (Marketing)
- **Bob Reilly:** 20-30 hours/week
- **Momotaro:** 5-10 hours/week (guidance only)
- **Contractors:** Design lead (to be hired)

### Track B (Technical)
- **Backend Engineer:** 40 hours/week (weeks 2-3)
- **Frontend (Installer):** 40 hours/week (weeks 4-6)
- **DevOps:** 10-20 hours/week (weeks 1-2)
- **QA/Testing:** 10-20 hours/week (weeks 4-9)
- **Momotaro:** 20-30 hours/week (architecture, integration, testing)

### Total Team
- **Bob:** 20-30 hours/week
- **Momotaro:** 30-40 hours/week
- **Contractors (Dev):** 100-160 hours/week
- **Contractors (Design):** 40-80 hours/week (overlaps with Track A)

---

## 💰 INVESTMENT TIMELINE

### Week 1 (March 11-15)
- Claude Code: Architecture design ($50-100)
- Design contractor posting: Free
- Engineering contractor posting: Free
- **Cost:** ~$100

### Week 2-3 (March 16-29)
- Backend engineer: 2-3 weeks @ $120/hr = $9,600-$14,400
- DevOps engineer: 1 week @ $150/hr = $6,000
- Infrastructure setup: $500
- **Cost:** ~$16,100-$20,900

### Week 4-6 (March 30 - April 13)
- Installer engineer: 3 weeks @ $120/hr = $14,400
- App integration: 2 weeks @ $120/hr = $9,600
- QA/Testing: 2 weeks @ $80/hr = $6,400
- Infrastructure: $1,500
- **Cost:** ~$31,900

### Week 7-9 (April 14-27)
- QA/Testing: 3 weeks @ $80/hr = $9,600
- Bug fixes: 2 weeks @ $100/hr = $8,000
- Support infrastructure: $1,000
- **Cost:** ~$18,600

### Week 10 (April 28+)
- Monitoring + support: Ongoing
- Marketing rollout: TBD

### **Total MVP Investment:** ~$67K-$77K

(Note: Design costs come from Track A Phase 0 budget)

---

## 🎯 DEPENDENCIES & RISKS

### Dependencies
1. **Track A informs Track B:** Market feedback → product features
2. **Track B validates Track A:** MVP feedback → market assumptions
3. **Both need Bob:** Decisions, approvals, strategy

### Risk Mitigation
1. **Backend behind schedule?** Use existing OpenClaw services as interim
2. **Installer complexity?** Start with simple version, add features
3. **Market says "no"?** Pivot features based on feedback
4. **Budget overrun?** Cut features, extend timeline

### Success Path
1. Weeks 1-3: Both tracks parallel (design + market)
2. Weeks 4-6: MVP development (incorporate market feedback)
3. Weeks 7-9: Polish (iterate based on beta feedback)
4. Week 10: Launch with confidence (both tracks validated)

---

## 📈 EXPECTED OUTCOMES

### By March 29 (End of Week 3)
**Track A:**
- ✓ 50+ survey responses (pricing, features, personas)
- ✓ Design mockups approved
- ✓ Phase 1 budget approved ($84K-$106K)
- ✓ Contractors hired and starting

**Track B:**
- ✓ Technical architecture finalized
- ✓ Backend API design complete
- ✓ Database schema ready
- ✓ Development ready to start

### By April 27 (End of Week 9)
**Track A:**
- ✓ Marketing website live
- ✓ Launch strategy finalized
- ✓ Press outreach list ready
- ✓ 100 beta signups target

**Track B:**
- ✓ MVP ready (installer + app + backend)
- ✓ Alpha tested internally
- ✓ Beta tested with 20-50 users
- ✓ Issues resolved
- ✓ Documentation complete

### By April 28+ (Week 10)
**Combined Outcome:**
- ✓ MVP live to 100 customers
- ✓ Market validated
- ✓ Revenue flowing ($0-$10K)
- ✓ Clear path to Phase 1 features
- ✓ Excited early adopters
- ✓ Real product feedback

---

## 📞 COORDINATION

### Weekly Sync (Every Tuesday, 10 AM EDT)
- Bob + Momotaro
- Review progress on both tracks
- Discuss any blockers
- Make quick decisions
- Plan next week

### Daily Standup (Async, in team chat)
- Morning: What you're doing today
- Evening: What you accomplished
- Blockers: What needs help

### Decision Log
- All major decisions documented
- In: `ONIGASHIMA_GO_DECISION.md`
- Update weekly

---

## 🍑 BOTTOM LINE

**Two Parallel Tracks:**
1. **Marketing Track:** Market validation, design, team building (Weeks 1-3+)
2. **MVP Technical Track:** Build working product (Weeks 1-10)

**Timeline:**
- Week 1: Design both tracks
- Weeks 2-9: Build MVP while validating market
- Week 10: Launch with confidence

**Investment:**
- Track A (Phase 0): ~$40K-$60K (design, contractors)
- Track B (MVP): ~$67K-$77K (development)
- **Total Year 1:** ~$125K-$180K

**Expected Outcome (May 2026):**
- 100+ customers
- Real revenue ($10K-$50K)
- Clear product-market fit
- Ready for Phase 1 scaling

**Philosophy:**
Don't wait for perfect. Build, learn, iterate, ship.

---

**Created:** March 11, 2026, 2:24 PM EDT  
**Status:** Both tracks approved and starting  
**Owner:** Bob Reilly + Momotaro 🍑
