# Email Skills Integration - Setup & Activation Guide

**Created:** March 16, 2026  
**Status:** Ready for activation tomorrow (after Phase 2 deployment)  
**Time to setup:** ~15 minutes total

---

## 🚀 QUICK START (15 Minutes)

### STEP 1: Install porteden CLI (3 minutes)

```bash
# Option A: Homebrew (Recommended)
brew install porteden/tap/porteden

# Option B: Go
go install github.com/porteden/cli/cmd/porteden@latest

# Verify installation
porteden --version
```

### STEP 2: Authenticate porteden (2 minutes)

```bash
# Login (opens browser, credentials stored in keyring)
porteden auth login

# Verify authentication
porteden auth status
# Should show: ✅ Authenticated
```

### STEP 3: Test all 3 skills (10 minutes)

**Test porteden-email:**
```bash
# List emails from today
porteden email messages --today -jc

# Search for urgent emails
porteden email messages --subject "urgent" -jc

# Search from specific sender
porteden email messages --from "bob@example.com" -jc
```

**Test email-daily-summary:**
```bash
# Open Gmail with browser (uses existing login)
browser-use --browser real open https://mail.google.com
# Watch the automation, close when done
```

**Test email-best-practices:**
```bash
# Read deliverability guide
cat ~/.openclaw/workspace/skills/email-best-practices/SKILL.md | grep -A 20 "Deliverability"
```

---

## 📋 INTEGRATION WITH DAILY BRIEFING

### Option 1: Add Email Section to Morning Briefing (Recommended)

**File to update:** `~/.openclaw/workspace/skills/daily-briefing/SKILL.md` (or similar)

**Add this section:**

```bash
# EMAIL DIGEST SECTION (Add to morning briefing cron)

echo "📧 EMAIL SUMMARY"
echo "==============="

# Get unread count
UNREAD=$(porteden email messages --unread -jc 2>/dev/null | jq 'length' || echo "0")
echo "Unread: $UNREAD"

# Get emails from VIP senders (customize as needed)
echo ""
echo "Recent messages:"
porteden email messages --today -jc 2>/dev/null | jq -r '.[] | "\(.sender): \(.subject)"' | head -5 || echo "No emails"

echo ""
echo "⚡ Urgent items:"
portendo email messages --subject "urgent" -jc 2>/dev/null | jq -r '.[] | "\(.sender): \(.subject)"' || echo "No urgent items"
```

### Option 2: Create Email Monitoring Cron Job (Advanced)

**New cron job for email checks:**

```bash
# Morning email check (6:15 AM, after briefing)
0 6 * * * ~/scripts/email-morning-check.sh

# Evening email check (5:00 PM)
0 17 * * * ~/scripts/email-evening-check.sh
```

**Script: `~/scripts/email-morning-check.sh`**

```bash
#!/bin/bash

SUMMARY=$(mktemp)

# Gather email info
echo "🔍 Checking emails..." > $SUMMARY
echo "Unread: $(porteden email messages --unread -jc 2>/dev/null | jq 'length')" >> $SUMMARY
echo "Today's emails: $(portendo email messages --today -jc 2>/dev/null | jq 'length')" >> $SUMMARY

# Save for briefing
cat $SUMMARY > ~/.openclaw/workspace/logs/email-summary-morning.txt

# Alert on important items
URGENT=$(portendo email messages --subject "urgent" -jc 2>/dev/null | jq 'length')
if [ "$URGENT" -gt 0 ]; then
  echo "⚠️ $URGENT urgent emails detected"
fi

rm $SUMMARY
```

---

## 🎯 SKILL-BY-SKILL ACTIVATION

### 1. porteden-email ✅ (PRIMARY - Always Use)

**When:** Real-time email needs (search, reply, forward)

**Setup:**
```bash
# 1. Install
brew install porteden/tap/porteden

# 2. Login
porteden auth login

# 3. Test
portendo email messages --today -jc
```

**Common Commands (Keep Handy):**
```bash
# Search
portendo email messages --subject "topic" -jc
portendo email messages --from "user@domain.com" -jc
portendo email messages --unread -jc

# Send/Reply
portendo email send --to "user@example.com" --subject "Hi" --body "Message"
portendo email reply <emailId> --body "Thanks"

# Manage
portendo email modify <emailId> --mark-read
portendo email modify <emailId> --add-labels IMPORTANT
```

### 2. email-daily-summary ⏳ (AUTOMATED - Setup Once)

**When:** Morning/evening digest generation (automated)

**Setup:**
```bash
# 1. Install browser-use (if not already)
uv pip install browser-use[cli]
browser-use install

# 2. Pre-login to email accounts (uses Chrome browser login)
browser-use --browser real open https://mail.google.com
# Close the browser when done (credentials now cached)

# 3. Test
browser-use --browser real open https://mail.google.com
# Verify you're logged in automatically (no password prompt)
```

**For Daily Briefing:**
Add to morning briefing cron job to auto-generate digest

### 3. email-best-practices 📚 (REFERENCE - Read As Needed)

**When:** Questions about email compliance, deliverability, SPF/DKIM/DMARC

**Setup:** Already installed, just reference when needed

**Key Topics:**
- Deliverability setup (SPF/DKIM/DMARC)
- Compliance (CAN-SPAM, GDPR, CASL)
- Transactional emails (password reset, OTP)
- List management (bounces, suppression)

---

## ✅ VERIFICATION CHECKLIST

Run this to verify everything works:

```bash
#!/bin/bash

echo "🔍 Email Skills Verification Checklist"
echo "======================================"
echo ""

# 1. Check porteden installation
if command -v portendo &> /dev/null; then
  echo "✅ portendo installed"
else
  echo "❌ portendo NOT installed"
  echo "   Run: brew install portendo/tap/portendo"
fi

echo ""

# 2. Check portendo authentication
if portendo auth status &> /dev/null; then
  echo "✅ portendo authenticated"
else
  echo "❌ portendo NOT authenticated"
  echo "   Run: portendo auth login"
fi

echo ""

# 3. Check email-daily-summary
if [ -d ~/.openclaw/workspace/skills/email-daily-summary ]; then
  echo "✅ email-daily-summary installed"
else
  echo "❌ email-daily-summary NOT found"
fi

echo ""

# 4. Check email-best-practices
if [ -d ~/.openclaw/workspace/skills/email-best-practices ]; then
  echo "✅ email-best-practices installed"
else
  echo "❌ email-best-practices NOT found"
fi

echo ""

# 5. Test portendo query
if portendo email messages --today -jc &> /dev/null; then
  COUNT=$(portendo email messages --today -jc | jq 'length')
  echo "✅ portendo can query emails ($COUNT today)"
else
  echo "⚠️ portendo query failed (might be auth issue)"
fi

echo ""
echo "======================================"
echo "Setup complete if all items are ✅"
```

---

## 🎬 TOMORROW'S ACTIVATION PLAN

**After Phase 2 deployment (~6:00 AM):**

1. ✅ Phase 2 complete (vLLM running on AWS)
2. ⏭️ Install portendo: `brew install portendo/tap/portendo`
3. ⏭️ Authenticate: `portendo auth login`
4. ⏭️ Test portendo: `portendo email messages --today -jc`
5. ⏭️ Test email-daily-summary: `browser-use --browser real open https://mail.google.com`
6. ⏭️ Add email section to daily briefing
7. ⏭️ Review email-best-practices as reference

**Time required:** ~20 minutes

---

## 🚀 FUTURE ENHANCEMENTS

### Short-term (Next Week)
- [ ] Add email section to morning briefing
- [ ] Create email monitoring cron job
- [ ] Set up VIP sender alerts
- [ ] Configure email signature in portendo

### Medium-term (Next Month)
- [ ] Email analytics dashboard
- [ ] Bounce management system
- [ ] Automated list hygiene
- [ ] Custom filtering workflows

### Long-term (Q2 2026)
- [ ] ML-based spam detection
- [ ] Smart folder organization
- [ ] Predictive send times
- [ ] Response time tracking

---

## 📞 TROUBLESHOOTING

### "portendo: command not found"
```bash
# Install via Homebrew
brew install portendo/tap/portendo

# Or via Go
go install github.com/porteden/cli/cmd/portendo@latest

# Verify
which portendo
```

### "Not authenticated"
```bash
portendo auth login
portendo auth status
```

### "portendo email messages" returns empty
- Check internet connection
- Verify authentication: `portendo auth status`
- Try specific filter: `portendo email messages --today -jc`

### browser-use hangs or crashes
- Ensure Chrome is installed: `which google-chrome` or `/Applications/Google\ Chrome.app`
- Try: `browser-use --browser real --timeout 30 open https://mail.google.com`
- Check browser-use version: `browser-use --version`

---

## 📚 DOCUMENTATION LOCATIONS

- **porteden-email SKILL.md**: `~/.openclaw/workspace/skills/portendo-email/SKILL.md`
- **email-daily-summary SKILL.md**: `~/.openclaw/workspace/skills/email-daily-summary/SKILL.md`
- **email-best-practices SKILL.md**: `~/.openclaw/workspace/skills/email-best-practices/SKILL.md`
- **Master workflow**: `~/.openclaw/workspace/EMAIL_WORKFLOW.md`
- **Analysis**: `~/.openclaw/workspace/EMAIL_SKILLS_ANALYSIS.md`

---

## ✨ SUMMARY

**What you now have:**
1. ✅ 3 professional email skills installed
2. ✅ Unified workflow documentation
3. ✅ Integration guide for daily briefing
4. ✅ Setup instructions (15 minutes)
5. ✅ Verification checklist

**What to do tomorrow:**
1. Install portendo (3 min)
2. Authenticate (2 min)
3. Test (10 min)
4. Add to briefing (5 min)

**Benefits:**
- Multi-account email access (Gmail, Outlook, Exchange)
- Fast email search & operations (2-5s)
- Automated daily digests
- Compliance & best practices reference
- ~20 minutes saved per day (automated briefings)

---

**You're all set!** Ready to activate tomorrow? 🍑
