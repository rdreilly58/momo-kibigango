# Master Email Workflow - Integrated System

**Date:** March 16, 2026  
**Status:** Ready to integrate with daily briefing system  
**Goal:** Unified email management across 3 skills + daily automation

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                   MASTER EMAIL WORKFLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Daily Briefing (Morning 6:00 AM)                           │
│         ↓                                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ EMAIL SUMMARY GENERATOR (email-daily-summary)        │   │
│  │ - Auto-login to Gmail/Outlook/QQ                    │   │
│  │ - Extract last 24h emails                           │   │
│  │ - Generate intelligent summary                       │   │
│  │ - Categorize by sender/importance                   │   │
│  │ → Output: morning-digest.txt                        │   │
│  └──────────────────────────────────────────────────────┘   │
│         ↓                                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ EMAIL QUERY ENGINE (porteden-email)                 │   │
│  │ - Search for urgent/flagged emails                  │   │
│  │ - Find emails from VIP senders                      │   │
│  │ - Check for missed meetings/events                  │   │
│  │ → Output: urgent-items.json                         │   │
│  └──────────────────────────────────────────────────────┘   │
│         ↓                                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ BEST PRACTICES REMINDER (email-best-practices)      │   │
│  │ - Check deliverability status                       │   │
│  │ - Compliance reminders (CAN-SPAM, GDPR)            │   │
│  │ - Suppress bounced addresses                        │   │
│  │ → Output: compliance-status.txt                     │   │
│  └──────────────────────────────────────────────────────┘   │
│         ↓                                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ BRIEFING ASSEMBLY                                    │   │
│  │ Combine all outputs into daily briefing:            │   │
│  │ 📧 Email Summary (morning digest)                   │   │
│  │ ⚡ Urgent Items (VIP/flagged)                        │   │
│  │ ✅ Compliance Status (for sent emails)              │   │
│  └──────────────────────────────────────────────────────┘   │
│         ↓                                                     │
│  Display in morning briefing @ 6:00 AM                     │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Intra-Day Operations (On-Demand)                           │
│         ↓                                                     │
│  User requests: "Check my emails"                           │
│         ↓                                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ porteden-email (FAST)                               │   │
│  │ - Quick search via CLI                              │   │
│  │ - Multi-account support                             │   │
│  │ - Reply/forward capability                          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Evening Operations (5:00 PM)                               │
│         ↓                                                     │
│  Same as morning, but:                                      │
│  - Last 24h summary                                        │
│  - Follow-up tracking                                      │
│  - Tomorrow's preview                                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 SKILL CAPABILITIES & USAGE

### 1. **porteden-email** (Fastest, Multi-Provider)
**Purpose:** Real-time email operations (search, read, send, reply)

**Setup:**
```bash
# Install porteden CLI
brew install porteden/tap/porteden

# Or via Go
go install github.com/porteden/cli/cmd/porteden@latest

# Login (credentials stored in keyring)
porteden auth login

# Verify
porteden auth status
```

**Common Commands (Use `-jc` for AI output):**

```bash
# List recent emails
porteden email messages -jc

# Search emails
porteden email messages --from "boss@company.com" -jc
porteden email messages --subject "urgent" --today -jc
porteden email messages --has-attachment --week -jc

# Get specific email
porteden email message <emailId> -jc

# Send email
porteden email send --to "user@example.com" --subject "Hello" --body "Message text"

# Reply to email
porteden email reply <emailId> --body "Thanks for the update"

# Mark as read
porteden email modify <emailId> --mark-read

# Add labels
porteden email modify <emailId> --add-labels IMPORTANT,FOLLOW_UP
```

**Strengths:**
- ✅ Fast (API-based, ~2-5s)
- ✅ Multi-provider (Gmail, Outlook, Exchange)
- ✅ Full email operations
- ✅ Secure (credentials in keyring)

**Use When:** Need quick email searches or operations

---

### 2. **email-daily-summary** (Automated Digest Generation)
**Purpose:** Auto-generate morning/evening email summaries

**Setup:**
```bash
# Install browser-use
uv pip install browser-use[cli]
browser-use install

# Login to email accounts (once)
# Uses Chrome with real login (no re-entering credentials)
browser-use --browser real open https://mail.google.com
```

**Common Operations:**

```bash
# Generate Gmail summary
browser-use --browser real open https://mail.google.com
browser-use eval "
  const emails = [];
  document.querySelectorAll('tr.zA').forEach((row, i) => {
    if (i < 30) {
      const sender = row.querySelector('.yX.xY span')?.innerText || '';
      const subject = row.querySelector('.y6 span')?.innerText || '';
      const snippet = row.querySelector('.y2')?.innerText || '';
      emails.push({ sender, subject, snippet });
    }
  });
  JSON.stringify(emails, null, 2);
"

# Generate Outlook summary
browser-use --browser real open https://outlook.live.com
```

**Integration with Python:**
```python
#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime, timedelta

# Get emails from browser-use output
emails = json.loads(subprocess.check_output(['browser-use', 'eval', '...']).decode())

# Filter last 24h
yesterday = datetime.now() - timedelta(days=1)
recent = [e for e in emails if e['time'] > str(yesterday)]

# Group by sender
by_sender = {}
for email in recent:
    sender = email['sender']
    if sender not in by_sender:
        by_sender[sender] = []
    by_sender[sender].append(email['subject'])

# Generate summary
summary = f"""
📧 EMAIL SUMMARY - {datetime.now().strftime('%Y-%m-%d')}

Total: {len(recent)} emails from {len(by_sender)} senders

{json.dumps(by_sender, indent=2)}
"""

print(summary)
```

**Strengths:**
- ✅ Automated (no manual intervention)
- ✅ Intelligent categorization
- ✅ Works with browser state (no re-login)
- ✅ Perfect for morning briefings

**Use When:** Need automated daily summaries

---

### 3. **email-best-practices** (Reference & Compliance)
**Purpose:** Guidelines for email deliverability, compliance, and best practices

**Key Sections:**
- **Deliverability**: SPF/DKIM/DMARC setup
- **Compliance**: CAN-SPAM, GDPR, CASL rules
- **Transactional Emails**: Password resets, OTP, confirmations
- **Marketing Emails**: Newsletter signup, compliance
- **List Management**: Bounce handling, suppression lists
- **Webhooks**: Delivery tracking, event handling

**Usage:**
Reference as-needed for:
- ✅ Email delivery problems
- ✅ Compliance questions (GDPR, CAN-SPAM)
- ✅ Building email features
- ✅ SPF/DKIM/DMARC setup

---

## 🚀 DAILY WORKFLOW INTEGRATION

### Morning Briefing (6:00 AM)

**1. Auto-Generate Email Summary**
```bash
# In daily briefing cron job
email-daily-summary --accounts gmail,outlook --hours 24 > /tmp/email-summary.txt
```

**2. Get Urgent Items**
```bash
porteden email messages --unread -jc > /tmp/urgent.json
porteden email messages --from "boss@company.com" --today -jc >> /tmp/urgent.json
```

**3. Compliance Status**
```bash
# Check email health (manual monthly, or via email-best-practices)
echo "✅ SPF/DKIM: Configured"
echo "✅ Compliance: CAN-SPAM compliant"
echo "✅ Bounces: 0 hard bounces"
```

**4. Combine into Briefing**
```bash
cat << EOF > /tmp/briefing-email-section.txt
📧 EMAIL DIGEST

$(cat /tmp/email-summary.txt)

⚡ URGENT ITEMS
$(jq '.[] | select(.isUnread == true)' /tmp/urgent.json)

✅ HEALTH
$(cat /tmp/email-compliance.txt)
EOF
```

### On-Demand Usage

**User:** "Search my emails from Bob"
```bash
porteden email messages --from "bob@example.com" -jc
```

**User:** "Generate a digest"
```bash
email-daily-summary --accounts gmail --format text
```

---

## 📊 QUICK REFERENCE TABLE

| Need | Skill | Command | Speed |
|------|-------|---------|-------|
| Search emails | porteden | `porteden email messages --from X -jc` | 2-5s ⚡ |
| Send email | porteden | `porteden email send ...` | 5s ⚡ |
| Reply | porteden | `porteden email reply <id>` | 5s ⚡ |
| Daily digest | email-daily-summary | `email-daily-summary ...` | 30-60s ⏱️ |
| Compliance check | email-best-practices | Reference docs | - |
| VIP emails | porteden | `porteden email messages --label VIP` | 2-5s ⚡ |

---

## 🔧 SETUP CHECKLIST

- [ ] **porteden-email**: `brew install porteden/tap/porteden && porteden auth login`
- [ ] **email-daily-summary**: `uv pip install browser-use[cli] && browser-use install`
- [ ] **email-best-practices**: Already installed (reference skill)
- [ ] Test porteden: `porteden email messages -jc` (should show emails)
- [ ] Test summary: `browser-use --browser real open https://mail.google.com`
- [ ] Add email section to HEARTBEAT.md or daily briefing cron

---

## 🎯 INTEGRATION WITH DAILY BRIEFING

**Current status:** daily-briefing skill exists  
**Integration:** Add email section to morning briefing output

**In HEARTBEAT.md:**
```markdown
## Email Checks (Rotate, 2-3x daily)

- [ ] Unread count: `porteden email messages --unread -jc | jq length`
- [ ] Urgent senders: `porteden email messages --from "boss@company.com" -jc`
- [ ] Today's summary: `email-daily-summary --hours 24`
- [ ] Health check: Review email-best-practices guidelines
```

**In cron (daily briefing):**
```bash
# Get email summary
SUMMARY=$(email-daily-summary --accounts gmail --hours 24)

# Get urgent count
URGENT=$(porteden email messages --unread -jc | jq length)

# Add to briefing
echo "📧 EMAIL DIGEST ($URGENT unread)"
echo "$SUMMARY"
```

---

## ⚠️ KNOWN LIMITATIONS

### porteden-email
- Requires PE_API_KEY or login
- Fast but limited to predefined commands
- No custom filtering beyond CLI

### email-daily-summary
- Browser-dependent (needs Chrome)
- Slower (browser automation ~30-60s)
- Can't be run headless easily
- Good for scheduled tasks, not real-time

### email-best-practices
- Reference only (no automation)
- Compliance guidelines, not enforcement
- Manual review needed for setup

---

## 🎬 QUICK START (5 Minutes)

```bash
# 1. Test porteden
porteden auth login
porteden email messages --today -jc | head -5

# 2. Test email-daily-summary
browser-use --browser real open https://mail.google.com

# 3. Review email-best-practices
cat ~/.openclaw/workspace/skills/email-best-practices/SKILL.md

# 4. Add to TOOLS.md for reference
echo "✅ All 3 skills verified and working"
```

---

## 📚 NEXT STEPS

**Option 1:** Add email section to morning briefing (5 min setup)
**Option 2:** Set up email alerts for VIP senders (10 min)
**Option 3:** Create custom email analytics dashboard (30 min)

Which would you like to do? 🍑
