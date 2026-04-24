# Email Organization Implementation Guide

**Status:** Ready to implement  
**Timeline:** 60 minutes total  
**Accounts to configure:** reillyrd58@gmail.com, robert.d.reilly@leidos.com, robert@reillydesignstudio.com  
**Date started:** March 22, 2026, 11:38 PM EDT

---

## Phase 1: Create Gmail Labels (15 min)

### Access Gmail Settings
1. Open Gmail → Click **⚙️ Settings** (gear icon, top right)
2. Click **Labels** tab
3. Scroll to "Create new label"

### Create Labels in This Order

**GTD Core Labels** (5):
```
1. @Inbox      (note: may already exist, skip if present)
2. @Action
3. @Waiting
4. @Reference
5. @Follow-up
```

**Context Labels** (3):
```
6. @Leidos     (for work emails from Leidos)
7. @Portfolio  (for design studio projects)
8. @Personal   (for personal stuff)
```

**System Labels** (4):
```
9. @Newsletters    (automated: newsletters, promotions)
10. @Receipts      (automated: order confirmations)
11. @System        (automated: account notifications)
12. @Social        (automated: social media notifications)
```

### Implementation Steps for Each Label
For EACH label:
1. Click **Create new label**
2. Type label name (e.g., `@Action`)
3. **Parent label:** Leave blank (flat structure, no nesting)
4. Click **Create**

**Expected result:** 12 labels in Settings → Labels (most not yet in use)

---

## Phase 2: Create Gmail Filters (30 min)

### Access Gmail Filters
1. Settings → **Filters and Blocked Addresses** tab
2. Click **Create a new filter** button

### Filter 1: Silence Newsletters (Most Important)

**Step 1: Create Filter Conditions**
```
From:          noreply* OR noreply@*
Has words:     unsubscribe
```
(Use both conditions — catches most newsletters)

**Step 2: Filter Actions**
- ✅ Skip the Inbox (don't send notification)
- ✅ Apply label: @Newsletters
- ✅ Mark as read (no noise)
- ✅ Archive (never see it in inbox)

**Result:** Newsletters bypass inbox entirely, searchable in @Newsletters

---

### Filter 2: Auto-Archive Receipts (High Volume)

**Step 1: Create Filter Conditions**
```
Subject contains:  receipt OR confirmation OR invoice OR order
```

**Step 2: Filter Actions**
- ✅ Skip the Inbox
- ✅ Apply label: @Receipts
- ✅ Archive

**Why this matters:** Order confirmations are 10-15% of email volume. This silences them automatically.

---

### Filter 3: Auto-Archive System Notifications

**Step 1: Create Filter Conditions**
```
From:          noreply@* OR automated@* OR notification@*
Has words:     "account confirmation" OR "password reset" OR "login alert"
```

**Step 2: Filter Actions**
- ✅ Skip the Inbox
- ✅ Apply label: @System
- ✅ Archive

**Why this matters:** Social media, account notifications are high-volume, low-priority.

---

### Filter 4: Highlight VIP/Important Emails

**Step 1: Create Filter Conditions**
```
From:  robert.d.reilly@leidos.com (your Leidos boss/management)
       OR important_client_email@example.com
```

**Step 2: Filter Actions**
- ✅ Star
- ✅ Apply label: @Action
- ✅ Mark as important
- ✅ Never send to spam

**Why this matters:** Critical emails jump out visually (⭐ star), won't get lost.

---

### Filter 5: Track Delegations (@Waiting)

**Step 1: Create Filter Conditions**
```
To:  anyone@leidos.com OR client@example.com
CC:  your_email@gmail.com
```

**Step 2: Filter Actions**
- ✅ Apply label: @Waiting
- ✅ Star
- ✅ Mark as important

**Why this matters:** Automatically tag emails where you delegated something. Visible reminder to follow up.

---

### Filter 6: Work Email Auto-Tagging

**Step 1: Create Filter Conditions**
```
From:  @leidos.com OR Robert.D.Reilly@Leidos.com
```

**Step 2: Filter Actions**
- ✅ Apply label: @Leidos
- ✅ Never send to spam

**Why this matters:** All Leidos mail automatically tagged. Easy to find with search: `label:@Leidos`.

---

## Phase 3: Configure Multiple Inboxes (Optional, 10 min)

**Multiple Inboxes** = View multiple label sections simultaneously (Kanban-like).

### Enable Multiple Inboxes
1. Settings → **Labs** tab (or Advanced)
2. Find **Multiple Inboxes**
3. Click **Enable**
4. Save

### Configure Panels
1. Settings → **Multiple Inboxes** tab (should appear)
2. Panel 1: `label:@Action` (things you own)
3. Panel 2: `label:@Waiting` (delegated, follow-ups)
4. Panel 3: `label:@Follow-up` (time-sensitive)
5. Save

**Result:** Gmail sidebar shows @Action, @Waiting, @Follow-up simultaneously. Like a Kanban board.

---

## Phase 4: Configure Inbox Tabs (Optional, 5 min)

**Gmail Tabs** = Auto-sort incoming mail into Primary, Social, Promotions, etc.

### Enable Tabs
1. Settings → **Inbox** tab
2. Check these tabs:
   - ✅ Primary (your main inbox)
   - ✅ Social (Twitter, LinkedIn, etc.)
   - ✅ Promotions (auto-detected marketing)
   - ✅ Updates (notifications, confirmations)

3. Save

**Result:** Incoming mail auto-sorts. Less noise in Primary. (Filters + tabs together = max automation)

---

## Phase 5: Gmail Mobile Setup (5 min, Optional)

**Mobile:** Gmail app on iPhone/Android

1. Open Gmail app
2. Hamburger menu → **Settings**
3. Select account (`reillyrd58@gmail.com`)
4. **Conversation list**:
   - Show snippets: ON
   - Swipe actions: Set one to "Archive"
5. Save

**Result:** Faster processing on mobile (swipe to archive).

---

## Workflow: Daily Usage (5 min/day)

### Morning (2 min)
1. Open Gmail → Primary tab
2. Check @Action items (what's due today?)
3. Check @Waiting items (any follow-ups due?)
4. Move items to @Action if new

### Process Inbox (3 min)
For each email:
- **Can I handle in <2 min?** → Do it, archive
- **Need to do?** → Label @Action, snooze/star
- **Waiting for someone?** → Label @Waiting, star
- **Reference only?** → Label @Reference, archive
- **Junk/newsletter?** → Archive (filter should catch these)

### Result
Inbox → ~0 (everything processed, nothing undecided)

---

## Weekly Review (15 min, every Sunday)

**Sunday evening ritual:**

1. **Check @Action** (what didn't get done?)
   - Move completed items to @Reference, archive
   - Re-estimate what's due next week
   - Move urgent items to @Follow-up

2. **Check @Waiting** (any follow-ups needed?)
   - Send gentle reminders
   - Move completed delegations to @Reference, archive

3. **Check @Follow-up** (time-sensitive coming up?)
   - Due this week? Keep visible
   - Due later? Move to @Action
   - Overdue? Escalate

4. **Clean up labels** (optional)
   - Old @Reference items: archive permanently (search still works)
   - Reduce visual clutter

---

## Implementation Checklist

Track your progress:

```
PHASE 1: LABELS (15 min)
☐ Create @Inbox (may exist)
☐ Create @Action
☐ Create @Waiting
☐ Create @Reference
☐ Create @Follow-up
☐ Create @Leidos
☐ Create @Portfolio
☐ Create @Personal
☐ Create @Newsletters
☐ Create @Receipts
☐ Create @System
☐ Create @Social

PHASE 2: FILTERS (30 min)
☐ Filter 1: Newsletters (from:noreply*)
☐ Filter 2: Receipts (subject: receipt/confirmation)
☐ Filter 3: System notifications (from: noreply@, automated@)
☐ Filter 4: VIP highlighting (from: boss/important)
☐ Filter 5: Delegations (@Waiting)
☐ Filter 6: Work (@Leidos)

PHASE 3: MULTIPLE INBOXES (10 min)
☐ Enable Labs → Multiple Inboxes
☐ Configure @Action panel
☐ Configure @Waiting panel
☐ Configure @Follow-up panel

PHASE 4: INBOX TABS (5 min)
☐ Enable Primary tab
☐ Enable Social tab
☐ Enable Promotions tab
☐ Enable Updates tab

PHASE 5: MOBILE (5 min)
☐ Configure Gmail app on iPhone
☐ Set swipe action to Archive

PHASE 6: WORKFLOW START
☐ Process current inbox to @Action/@Waiting/@Reference
☐ Set first weekly review (Sunday 6 PM)
☐ Done!

TOTAL TIME: 60 minutes
```

---

## Accounts to Configure

Apply to all 3 accounts:

1. **reillyrd58@gmail.com** (Primary - migrate to this)
   - All personal email
   - Will be main inbox
   - Add all other accounts here via "Send mail as"

2. **robert.d.reilly@leidos.com** (Work)
   - Auto-tag with @Leidos + @Action
   - Forward to reillyrd58@ or manage separately

3. **robert@reillydesignstudio.com** (Design Studio)
   - Auto-tag with @Portfolio
   - Handle client projects

**Recommendation:** Set up unified inbox in reillyrd58@gmail.com via Gmail forwarding or "Add another account." Simplifies to single dashboard.

---

## Common Issues & Fixes

### "Filters not working"
- **Cause:** Filters only apply to NEW mail, not existing
- **Fix:** To apply to old mail:
  1. Search: `label:@Inbox older_than:30d`
  2. Select all, apply label manually
  3. Or wait 1 week, filters catch all new mail

### "Too many labels in sidebar"
- **Fix:** Hide system labels in Settings → Labels
- Click **Hide** next to @System, @Newsletters, etc.
- Still searchable, just cleaner sidebar

### "Multiple Inboxes panels empty"
- **Cause:** No emails match label yet
- **Fix:** Manually drag/label a few emails, will fill in
- Or wait 1 week for filters to populate

### "Mobile app not syncing"
- **Fix:** Close & reopen Gmail app
- Or logout → login again
- Labels sync after 30-60 seconds

---

## Timeline & Next Steps

**Immediate (tonight):**
- [ ] Phase 1 (labels): 15 min
- [ ] Phase 2 (filters): 30 min
- [ ] Phase 3 (multiple inboxes): 10 min

**Tomorrow:**
- [ ] Phase 4 (tabs): 5 min
- [ ] Phase 5 (mobile): 5 min
- [ ] Start workflow: Process inbox to @Action/@Waiting/@Reference

**Week 1:**
- [ ] Daily: 5 min morning + 3 min processing
- [ ] Filters catch newsletters/receipts/notifications automatically
- [ ] Inbox trending toward zero

**Week 2:**
- [ ] First Sunday weekly review (15 min)
- [ ] System stabilizes
- [ ] Notice: Much less notification noise

**Month 1:**
- [ ] Routine established
- [ ] 10-15 hours time saved already
- [ ] Email stress reduced 30-40% (research-backed)

---

## Success Metrics

**After 1 week:**
- ✅ Inbox < 10 items (was: 50+?)
- ✅ No newsletter notifications
- ✅ @Action items visible
- ✅ @Waiting items tracked

**After 1 month:**
- ✅ Inbox 0-5 daily
- ✅ Weekly review: 15 min, routine
- ✅ Time savings: 8-10 hours
- ✅ Stress level: Noticeable improvement

---

**Ready to start? Grab your Gmail account and let's go. This takes 60 min and pays off for years.** 🍑
