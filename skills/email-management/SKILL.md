---
name: email-management
description: "Manage email accounts: primary Gmail (reillyrd58@gmail.com) via gog CLI, and ReillyDesignStudio (robert@reillydesignstudio.com) via Himalaya CLI when app password is configured."
metadata:
  {
    "openclaw": { "emoji": "📧", "requires": { "bins": ["himalaya", "gog"] } },
  }
---

# Email Management

Manage multiple email accounts using CLI tools.

## Quick Reference

**Primary Gmail Account (reillyrd58@gmail.com):**
```bash
# Search inbox
gog gmail search -a reillyrd58@gmail.com "is:inbox"

# Send email
gog gmail send -a reillyrd58@gmail.com --to "recipient@example.com" --subject "Subject" --body-file <(cat message.txt)

# Search with filters
gog gmail search -a reillyrd58@gmail.com "from:sender@example.com subject:important"
```

**ReillyDesignStudio Account (robert@reillydesignstudio.com):**
- Status: Pending app password setup (see Setup section below)
- Provider: Google Workspace (Gmail)
- Method: Himalaya CLI (IMAP/SMTP)

---

## Setup

### 1. Configure Email Account

```bash
himalaya account configure
```

Follow the interactive wizard to:
- Set email: robert@reillydesignstudio.com
- Configure IMAP (ask your email provider for settings)
- Configure SMTP (for sending)
- Store password securely in system keyring

### 2. Verify Configuration

```bash
himalaya account list
himalaya envelope list  # Should show emails
```

## Common Tasks

### List Unread Emails

```bash
himalaya envelope list --output plain
```

### Search Emails

By sender:
```bash
himalaya envelope list from:client@example.com
```

By subject:
```bash
himalaya envelope list subject:"ReillyDesignStudio"
```

By date:
```bash
himalaya envelope list since:2026-03-01
```

### Read an Email

```bash
himalaya message read 42
```

### Reply to Email

```bash
himalaya message reply 42
```

### Send New Email

```bash
himalaya message write
```

Then compose in your editor and send.

### Move Email to Folder

```bash
himalaya message move 42 "Archive"
```

## Daily Email Scan

Run the automated scan:

```bash
bash ~/.openclaw/workspace/scripts/email-scan.sh
```

Or add to heartbeat for periodic checks:

```bash
# In HEARTBEAT.md, add:
- Check ReillyDesignStudio emails (run: bash ~/.openclaw/workspace/scripts/email-scan.sh)
```

## Email Accounts

```bash
# List all configured accounts
himalaya account list

# Use specific account
himalaya --account rds envelope list
```

## Tips

- Emails are referenced by ID (number)
- Search is case-insensitive
- Use `--output json` for parsing
- Passwords are stored securely in system keyring (macOS Keychain)
