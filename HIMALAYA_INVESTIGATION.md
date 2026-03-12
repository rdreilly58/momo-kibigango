# Himalaya Setup Investigation & Improvements

## Current Status: ✅ WORKING (with warnings)

Himalaya CLI is functional and connected to your Gmail account, but there are several areas for improvement.

---

## ✅ What's Working

1. **Version:** v1.1.0 with IMAP, SMTP, Wizard, and PGP support
2. **Account Connection:** Gmail account (`gmail`) is configured and default
3. **Email Reading:** Can list and read envelopes successfully
4. **Account Management:** Can list configured accounts
5. **Email Access:** Successfully accessed 185k+ messages in inbox

### Test Results:
- ✅ `himalaya envelope list` — Lists 10 recent emails (185631, 185630, etc.)
- ✅ `himalaya message read 185630` — Reads full message body
- ✅ `himalaya account list` — Shows Gmail account as default
- ✅ No authentication errors

---

## ⚠️ Issues & Warnings

### 1. **IMAP Codec Warnings (Non-Fatal)**
```
WARN imap_codec::response: Rectified missing `text` to "..."
WARN imap_client::tasks::resolver: received unsolicited [unsolicited=Status(...)]
WARN imap_client::tasks::select: missing required UNSEEN OK untagged response
```
**Impact:** Minor — these are handled gracefully by Himalaya but indicate server protocol quirks.

**Fix:** Update to latest Himalaya version (currently v1.1.0, check for v1.2+)

### 2. **No Config File**
- Location: `~/.config/himalaya/config.toml` is missing
- Status: Himalaya is using default in-memory config (works but fragile)
- Risk: Settings not persisted if cache is cleared

**Fix:** Create explicit config.toml file

### 3. **Message Send Command Complexity**
- `himalaya message send` requires raw RFC 822 format (headers + body)
- Not user-friendly for simple email composition
- Alternative: Use `gog` (Gmail CLI) which has simpler syntax

**Fix:** For sending, continue using `gog gmail send` (already optimal)

### 4. **No Compose/Reply Wizards in This Version**
- Can read and list emails, but composing requires raw format
- No interactive reply feature
- Limitations for email workflows

**Fix:** Use `gog` for outbound, Himalaya for inbound

---

## 📋 Current Capabilities

### Strong Points:
- ✅ Fast email listing (185k+ messages in seconds)
- ✅ Full message body retrieval
- ✅ Account management
- ✅ Thread support
- ✅ Low-level access to IMAP

### Limited Points:
- ⚠️ Message composition requires raw RFC 822 format
- ⚠️ No easy reply/compose interface
- ⚠️ Minimal search functionality
- ⚠️ No config persistence by default

---

## 🎯 Recommendations

### Priority 1: Create Config File
Create `~/.config/himalaya/config.toml` to persist settings:

```toml
[gmail]
default = true
backend = "imap"
imap-host = "imap.gmail.com"
imap-port = 993
imap-starttls = false
imap-login = "rdreilly2010@gmail.com"
imap-password-cmd = "op read op://personal/Gmail --fields password"
smtp-host = "smtp.gmail.com"
smtp-port = 587
smtp-starttls = true
smtp-login = "rdreilly2010@gmail.com"
smtp-password-cmd = "op read op://personal/Gmail --fields password"
```

**Benefits:**
- Persistent settings across sessions
- Can use 1Password integration for secure credentials
- Enables advanced features

### Priority 2: Update Himalaya
```bash
brew upgrade himalaya
```
Check for v1.2+ to fix IMAP codec warnings.

### Priority 3: Setup Reading Pipeline
Use Himalaya for **reading** emails:
```bash
# List unread emails
himalaya envelope list --query "flag:unseen"

# Read specific message
himalaya message read <ID>

# Thread view
himalaya envelope thread --query "from:sender@example.com"
```

### Priority 4: Keep using `gog` for Sending
Our current setup is optimal:
```bash
/opt/homebrew/bin/gog gmail send --to user@example.com --subject "Subject" --body "Message"
```

---

## 🚀 Advanced Use Cases (Future)

Once config is set up, can add:
1. **Email Search Integration:** `himalaya envelope list --query "complex search"`
2. **Automated Email Backups:** Export to Maildir format
3. **Email Parsing Pipeline:** Extract data and feed to scripts
4. **Integration with Tasks/Reminders:** Parse email for action items

---

## Summary

**Himalaya Status:** ✅ Functional but needs configuration
- Works perfectly for **reading** emails
- Send via `gog` (already optimal)
- Create config.toml for persistence
- Update to latest version to fix warnings

**Suggested Setup:**
- **Inbound:** Himalaya CLI for listing, reading, searching
- **Outbound:** `gog` CLI for sending (simpler, works great)
- **Config:** Create `.config/himalaya/config.toml` with credentials
- **Cron Tasks:** Use Himalaya in morning briefing to fetch unread count

---

## Next Steps

1. Create config file: `~/.config/himalaya/config.toml`
2. Add to briefing scripts: Show unread email count from Himalaya
3. Test email search workflows
4. Set up optional 1Password integration for passwords
