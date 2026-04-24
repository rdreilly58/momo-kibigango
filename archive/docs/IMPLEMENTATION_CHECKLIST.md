# Implementation Checklist — OpenClaw Optimization
*Track your progress on recommendations from RECOMMENDATIONS_2026-03-18.md*

## 🔴 WEEK 1: Cron Job Monitoring (Priority)

### Task 1.1: Add Healthchecks.io Pings
- [ ] Update `send-briefing-v2.sh` (evening)
  - [ ] Add curl ping on success
  - [ ] Add error trap for failures
  - [ ] Test: `bash send-briefing-v2.sh evening`
  - [ ] Verify message sent to email
  - [ ] Check Healthchecks.io dashboard shows ping

- [ ] Update `send-morning-briefing.sh` (morning)
  - [ ] Same changes as evening
  - [ ] Test both scripts

**Status:** ⬜ Not started  
**Estimated time:** 10 minutes  
**Docs:** RECOMMENDATIONS_2026-03-18.md Section 1

---

### Task 1.2: Add Telegram Error Alerts
- [ ] Verify `TELEGRAM_BOT_TOKEN` in `~/.openclaw/workspace/config/briefing.env`
- [ ] Verify `TELEGRAM_CHAT_ID` in config
- [ ] Add error trap to both briefing scripts:
  ```bash
  trap 'curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
    -d "chat_id=$TELEGRAM_CHAT_ID" \
    -d "text=⚠️ Briefing FAILED: $1" > /dev/null' ERR
  ```
- [ ] Test: Manually break script to verify alert fires
- [ ] Document bot token setup (if not yet done)

**Status:** ⬜ Not started  
**Estimated time:** 15 minutes  
**Docs:** Check `config/briefing.env`

---

### Task 1.3: Verify Cron Jobs
- [ ] Run: `openclaw cron list` to confirm both jobs exist
- [ ] Job IDs should be:
  - Morning: `9b5b78c9-1982-4411-ae80-f6d3a9c74ca0`
  - Evening: `35ba6ee2-19d1-48c2-b7b6-37bb0274998c`
- [ ] Check next run times
- [ ] Verify both jobs are enabled (`enabled: true`)

**Status:** ⬜ Not started  
**Estimated time:** 5 minutes

---

## 🟡 WEEK 2: Skill Consolidation (Medium Priority)

### Task 2.1: Audit Current Skills
- [ ] Count installed skills:
  ```bash
  ls -1 ~/.openclaw/workspace/skills/ | wc -l
  ```
  Current: ~30 skills, Target: ~10 core + install on-demand

- [ ] Document which skills you actually use:
  - [ ] `gog` — Weekly (Gmail, Calendar)
  - [ ] `ga4-analytics` — Daily (briefing)
  - [ ] `ios-dev` — 2x/week (Momotaro)
  - [ ] `aws-deploy` — 1x/week (ReillyDesignStudio)
  - [ ] `agent-browser` — Rarely (web automation)
  - [ ] Others: _______________

**Status:** ⬜ Not started  
**Estimated time:** 10 minutes

---

### Task 2.2: Archive Unused Skills
- [ ] Create archive directory:
  ```bash
  mkdir -p ~/.openclaw/workspace/skills-archived
  ```

- [ ] Move redundant/unused skills:
  ```bash
  # Email consolidation
  mv ~/.openclaw/workspace/skills/browser-automation skills-archived/
  mv ~/.openclaw/workspace/skills/email-best-practices skills-archived/
  mv ~/.openclaw/workspace/skills/email-daily-summary skills-archived/
  mv ~/.openclaw/workspace/skills/porteden-email skills-archived/
  mv ~/.openclaw/workspace/skills/himalaya skills-archived/
  
  # In-progress/unused
  mv ~/.openclaw/workspace/skills/mbse skills-archived/
  mv ~/.openclaw/workspace/skills/speculative-decoding skills-archived/
  mv ~/.openclaw/workspace/skills/security-monitor skills-archived/
  ```

- [ ] Verify remaining skills (should be ~10-12):
  ```bash
  ls -1 ~/.openclaw/workspace/skills/ | wc -l
  ```

- [ ] Commit cleanup:
  ```bash
  cd ~/.openclaw/workspace && \
  git add -A && \
  git commit -m "Archive unused skills - consolidate to core 10"
  ```

**Status:** ⬜ Not started  
**Estimated time:** 20 minutes

---

### Task 2.3: Document Core Skill Stack
- [ ] Create `SKILL_STACK.md`:
  ```markdown
  # Core Skill Stack (10 skills)
  
  ## Always Available
  - gog (Gmail/Calendar/Drive)
  - ga4-analytics (Analytics queries)
  - ios-dev (iPhone builds)
  - aws-deploy (Amplify)
  - agent-browser (Web automation)
  
  ## Install on Demand via Clawhub
  - swift-expert: Advanced iOS patterns
  - code-review-automation: PR reviews
  - make-pdf: PDF generation
  - slack: Slack integration
  - linkedin-automation: LinkedIn posting
  
  Last updated: [DATE]
  ```

- [ ] Add to MEMORY.md for future reference

**Status:** ⬜ Not started  
**Estimated time:** 10 minutes

---

## 🟡 WEEK 2: Data Pipeline Optimization (Medium Priority)

### Task 3.1: Consolidate populate-briefing.py

This is a nice-to-have but worth doing for 50% speed improvement.

- [ ] Create new consolidated script: `populate-briefing-batch.py`
- [ ] Combine 4 separate calls into 1:
  - GA4 data
  - Gmail queries (unread, starred, today, urgent)
  - Calendar events
  - Git stats
- [ ] Return single JSON with all data
- [ ] Test on evening briefing:
  ```bash
  python3 ~/.openclaw/workspace/skills/daily-briefing/scripts/populate-briefing-batch.py
  ```
- [ ] Compare latency: before vs. after
- [ ] Swap in send-briefing-v2.sh
- [ ] Verify email still sends correctly
- [ ] Apply same change to send-morning-briefing.sh

**Status:** ⬜ Not started  
**Estimated time:** 45 minutes  
**Docs:** RECOMMENDATIONS_2026-03-18.md Section 3B

---

## 🟢 WEEK 3: Model Optimization & Enhancements

### Task 4.1: Update SOUL.md with Sub-Agent Model Tiering
- [ ] Open `~/.openclaw/workspace/SOUL.md`
- [ ] Add section "Sub-Agent Model Selection"
- [ ] Include hierarchy:
  ```
  Haiku: Simple fixes (1 file, <100 lines)
  Opus: Medium tasks (4-8 files)
  GPT-4: Large builds (16+ files)
  ```
- [ ] Add cost expectations
- [ ] Commit update

**Status:** ⬜ Not started  
**Estimated time:** 15 minutes

---

### Task 4.2: Install Recommended Clawhub Skills
- [ ] Install `swift-expert` for iOS work:
  ```bash
  clawhub install swift-expert
  ```
  - [ ] Verify installation: `ls ~/.openclaw/workspace/skills/swift-expert`
  - [ ] Read SKILL.md

- [ ] Optional: Install `code-review-automation`:
  ```bash
  clawhub install code-review-automation
  ```

**Status:** ⬜ Not started  
**Estimated time:** 10 minutes

---

## 🟢 DOCUMENTATION & TRACKING

### Task 5.1: Document This Roadmap
- [ ] Save this checklist to: `~/.openclaw/workspace/IMPLEMENTATION_CHECKLIST.md`
- [ ] Update status as you complete each task
- [ ] Add dates when completed

**Status:** ⬜ Not started  
**Estimated time:** 2 minutes

---

### Task 5.2: Add to MEMORY.md
- [ ] Open `~/.openclaw/workspace/MEMORY.md`
- [ ] Add entry:
  ```markdown
  ## March 18, 2026 — Optimization Roadmap Created
  - Generated RECOMMENDATIONS_2026-03-18.md with 7 sections
  - Key focus: Cron monitoring (critical), skill consolidation (medium), cost optimization
  - Sources: Clawhub (13k+ skills), OpenClaw docs, GitHub issues, community guides
  - 20-hour total effort → ~2-3 hours of implementation
  ```

**Status:** ⬜ Not started  
**Estimated time:** 5 minutes

---

## 📊 Summary & Tracking

| Week | Priority | Tasks | Status | Time |
|------|----------|-------|--------|------|
| 1 | 🔴 HIGH | Healthchecks + alerts + verify | ⬜ | 30 min |
| 2 | 🟡 MED | Archive skills + audit stack | ⬜ | 40 min |
| 2 | 🟡 MED | Batch populate-briefing.py | ⬜ | 45 min |
| 3 | 🟢 LOW | Model tiering + new skills | ⬜ | 25 min |
| 3 | 🟢 LOW | Documentation | ⬜ | 10 min |
| **TOTAL** | — | **10 tasks** | **⬜** | **~2.5 hours** |

---

## Next Steps

1. **Today:** Read RECOMMENDATIONS_2026-03-18.md in full
2. **Tomorrow:** Start with Week 1 (Cron monitoring) — highest ROI
3. **This week:** Complete skill cleanup (Week 2)
4. **Next week:** Optional optimizations (Week 3)

---

*Last updated: March 18, 2026 at 6:35 PM EDT*  
*Checklist owner: Bob Reilly*  
*Reference: RECOMMENDATIONS_2026-03-18.md*
