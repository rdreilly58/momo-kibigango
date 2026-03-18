# Email Integration for Daily Briefing

**Date:** March 16, 2026, 10:45 PM  
**Status:** Ready for implementation  
**Tools:** gog (Gmail) + browser-use (digest generation)

---

## 🎯 INTEGRATION PLAN

### Email Section in Morning Briefing (6:00 AM)

Add this to your daily briefing cron job:

```bash
#!/bin/bash
# Email Section for Morning Briefing

echo "📧 EMAIL SUMMARY"
echo "================"
echo ""

# Get counts
UNREAD=$(gog gmail search "is:unread after:2026-03-16" --json 2>/dev/null | jq '.threads | length // 0')
TODAY=$(gog gmail search "after:2026-03-16" --json 2>/dev/null | jq '.threads | length // 0')

echo "📊 Stats:"
echo "  • Unread: $UNREAD"
echo "  • Today: $TODAY emails"
echo ""

# Get top senders today
echo "👤 Top senders today:"
gog gmail search "after:2026-03-16" --json 2>/dev/null | jq -r '.threads[0:5] | .[] | "\(.from)"' | sort | uniq -c | sort -rn | awk '{print "  • " $2 ": " $1}' || echo "  (no emails today)"
echo ""

# Urgent items (starred or marked important)
URGENT=$(gog gmail search "is:starred OR is:important after:2026-03-16" --json 2>/dev/null | jq '.threads | length // 0')
if [ "$URGENT" -gt 0 ]; then
  echo "⚡ URGENT ($URGENT):"
  gog gmail search "is:starred OR is:important after:2026-03-16" --json 2>/dev/null | jq -r '.threads[0:3] | .[] | "  • \(.subject)"' || true
else
  echo "✅ No urgent items"
fi
echo ""
```

---

## 📦 EMAIL-DAILY-SUMMARY: Automated Digest

### Option 1: Simple Gmail Digest (No Browser Automation)

Use gog to generate email summary manually:

```bash
#!/bin/bash
# Simple email summary from gog (no browser needed)

echo "📧 EMAIL DIGEST (Last 24h)"
echo "=========================="
echo ""

# Count emails by hour
gog gmail search "after:2026-03-15" --json 2>/dev/null | jq -r '.threads[] | "\(.date)"' | cut -d' ' -f2 | sort | uniq -c | sort -rn | while read count hour; do
  echo "  $hour: $count emails"
done

echo ""
echo "Top subjects today:"
gog gmail search "after:2026-03-16" --json 2>/dev/null | jq -r '.threads[0:10] | .[] | "\(.subject)"' | sed 's/^/  • /' || echo "  No emails"
echo ""
```

### Option 2: Full Browser-Based Digest (If You Set Up Pre-Login)

```bash
#!/bin/bash
# Browser-based digest using email-daily-summary

# Pre-requisite: You must have pre-logged in
# Run once: browser-use --browser real open https://mail.google.com

# Auto-extract emails with JavaScript
browser-use --browser real eval "
const emails = [];
document.querySelectorAll('tr[role=\"row\"]').forEach((row, i) => {
  if (i < 30) {
    const cells = row.querySelectorAll('td');
    if (cells.length > 3) {
      const sender = cells[2]?.innerText || '';
      const subject = cells[3]?.innerText || '';
      emails.push({ sender, subject });
    }
  }
});
console.log(JSON.stringify(emails, null, 2));
" 2>/dev/null | jq '.' > /tmp/emails.json

# Generate summary from JSON
echo "📧 EMAIL DIGEST"
echo "=============="
python3 << 'EOF'
import json

with open('/tmp/emails.json', 'r') as f:
    emails = json.load(f)

senders = {}
for email in emails:
    sender = email['sender'].split('<')[0].strip() or email['sender']
    if sender not in senders:
        senders[sender] = 0
    senders[sender] += 1

print(f"📊 Total: {len(emails)} emails")
print("\n👤 By sender:")
for sender, count in sorted(senders.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  • {sender}: {count}")
EOF
```

---

## 🔧 IMPLEMENTATION STEPS

### Step 1: Add gog Email Section to Briefing

**File to modify:** Your daily briefing script (location depends on your setup)

**Add this section (before or after other briefing sections):**

```bash
# ---- EMAIL SECTION ----
echo ""
echo "📧 EMAIL SUMMARY"
echo "================"

UNREAD=$(gog gmail search "is:unread after:2026-03-16" --json 2>/dev/null | jq '.threads | length // 0')
TODAY=$(gog gmail search "after:2026-03-16" --json 2>/dev/null | jq '.threads | length // 0')

echo "📊 $TODAY emails today | $UNREAD unread"

URGENT=$(gog gmail search "is:starred after:2026-03-16" --json 2>/dev/null | jq '.threads | length // 0')
[ "$URGENT" -gt 0 ] && echo "⚡ $URGENT starred/important items"
# ---- END EMAIL SECTION ----
```

### Step 2: Test the Email Integration

```bash
# Run the email section standalone first
UNREAD=$(gog gmail search "is:unread" --json | jq '.threads | length // 0')
TODAY=$(gog gmail search "after:2026-03-16" --json | jq '.threads | length // 0')
echo "📧 Emails: $TODAY today, $UNREAD unread"
```

### Step 3: Add to Daily Briefing Cron

**Your briefing cron job (location: ~/.openclaw/workspace/skills/daily-briefing/...)**

After implementing Step 1 & 2, the email section will automatically run each morning.

---

## 🎯 PRACTICAL WORKFLOW (TOMORROW)

### Morning (6:00 AM)
1. Daily briefing runs
2. **NEW:** Email summary displays:
   - 📧 Count of today's emails
   - 📊 Unread count
   - 👤 Top senders
   - ⚡ Urgent items (if any)
3. Briefing sent to your inbox/Telegram

### On-Demand (Anytime)
```bash
# Quick email check
gog gmail search "is:unread" --json | jq '.threads[0:3] | .[] | "\(.from): \(.subject)"'

# Check for VIPs
gog gmail search 'from:"bob@example.com"' --json

# Get attachment count
gog gmail search "has:attachment after:2026-03-16" --json | jq '.threads | length'
```

### Evening (5:00 PM - Optional)
Same as morning, but:
- Summarize last 24h
- Highlight follow-ups
- Preview tomorrow's items

---

## 📊 EMAIL QUERIES REFERENCE

**Common gog Gmail searches:**

```bash
# Unread
gog gmail search "is:unread" --json

# Today's emails
gog gmail search "after:2026-03-16" --json

# From specific person
gog gmail search 'from:rdreilly2010@gmail.com' --json

# With attachments
gog gmail search "has:attachment" --json

# Starred/important
gog gmail search "is:starred OR is:important" --json

# From domain
gog gmail search 'from:@google.com' --json

# Subject search
gog gmail search 'subject:"urgent"' --json

# Date range
gog gmail search 'after:2026-03-10 before:2026-03-16' --json

# All combined
gog gmail search 'is:unread AND has:attachment after:2026-03-16' --json
```

---

## ✅ IMPLEMENTATION CHECKLIST

- [ ] Identify your daily briefing cron job location
- [ ] Add gog email section to briefing script
- [ ] Test email section manually
- [ ] Deploy to production (update cron job)
- [ ] Run morning briefing and verify email section appears
- [ ] (Optional) Add evening briefing email section
- [ ] (Optional) Set up browser-based digest if needed

---

## 🚀 EXPECTED RESULT

**Morning briefing now includes:**

```
📧 EMAIL SUMMARY
================
📊 5 emails today | 2 unread

👤 Top senders:
  • LinkedIn: 2
  • Bob: 1
  • Newsletter: 1

⚡ 1 starred item
```

**Time saved per day:** 5-10 minutes (automated email check)

---

## 📞 TROUBLESHOOTING

### "gog: command not found"
```bash
# Verify gog is installed
which gog
# Should output: /opt/homebrew/bin/gog
```

### "jq: command not found"
```bash
# Install jq
brew install jq
```

### Email count always 0
```bash
# Check date format
gog gmail search "after:2026-03-16" --json

# Debug: verify auth
gog auth status
```

### Integration not showing in briefing
- Verify script has email section
- Check cron job logs
- Test section manually first

---

## 📝 NEXT STEPS

1. **Tomorrow morning (6:00-6:35 AM):**
   - After Phase 2 deployment completes
   - Identify your daily briefing script
   - Add email section
   - Deploy

2. **This week:**
   - Verify email appears in briefing
   - Add evening check (optional)
   - Configure VIP alerts (optional)

3. **Next week:**
   - Email analytics dashboard
   - Automated filtering rules
   - Enhanced digest with categorization

---

**Ready to integrate?** Let me know your briefing script location! 🍑
