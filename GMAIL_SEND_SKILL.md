# gmail-send Skill - Complete Reference

**Status:** ✅ Created, Tested & Committed (March 18, 2026)  
**Location:** `~/.openclaw/workspace/skills/gmail-send/`  
**Purpose:** Send emails with attachments via Gmail SMTP

---

## Quick Start

### 1. Set Up Gmail App Password (One-time)

```bash
# Interactive setup (recommended)
bash ~/.openclaw/workspace/skills/gmail-send/scripts/setup-gmail.sh

# Or manual setup
echo "xxxx xxxx xxxx xxxx" > ~/.gmail_app_password
chmod 600 ~/.gmail_app_password
```

**To get Gmail app password:**
1. Go to https://myaccount.google.com/apppasswords
2. Enable 2-Step Verification if needed
3. Select "Mail" and "macOS"
4. Click "Generate"
5. Copy the 16-character password

### 2. Send Your First Email

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "rdreilly2010@gmail.com" \
  --subject "Test Email" \
  --body "Hello from Momotaro!" \
  --from "rdreilly2010@gmail.com"
```

### 3. Send Email with Attachments

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "rdreilly2010@gmail.com" \
  --subject "Drafts for Review" \
  --body "Please review the attached files" \
  --from "rdreilly2010@gmail.com" \
  --attach ~/.openclaw/workspace/drafts/momo-kiji-blog-post.md \
             ~/.openclaw/workspace/drafts/momo-kiji-linkedin-post.md
```

---

## Skill Files

### SKILL.md (7.3 KB)
Complete skill documentation including:
- Quick start guide
- Usage patterns
- Environment setup options
- Script reference
- Examples
- Troubleshooting
- Security notes

### scripts/send_email.py (9.9 KB)
Main Python script for sending emails:
- Robust error handling
- MIME message building
- Attachment support
- Multiple recipients
- HTML/plain text
- Verbose debugging
- Dry-run mode

**Key features:**
```python
✓ Gmail SMTP connection (smtp.gmail.com:587 + TLS)
✓ App password authentication
✓ Multiple attachment types (text, binary, images, audio)
✓ HTML or plain text body
✓ Multiple recipients
✓ Custom sender display name
✓ Verbose logging for debugging
✓ Dry-run mode to test without sending
```

### scripts/setup-gmail.sh (1.9 KB)
Interactive setup helper script:
- Prompts for Gmail app password
- Validates password format
- Creates secure password file
- Sets correct permissions
- Provides next steps

### SETUP.md (6 KB)
Detailed setup guide:
- Prerequisites
- Step-by-step setup
- Testing instructions
- Troubleshooting
- Usage examples
- Security notes

---

## Command Reference

### Basic Email

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "Subject Line" \
  --body "Email body text" \
  --from "rdreilly2010@gmail.com"
```

### With Attachments

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "Files Attached" \
  --body "See attached" \
  --from "rdreilly2010@gmail.com" \
  --attach /path/to/file1.pdf /path/to/file2.md
```

### HTML Email

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "HTML Email" \
  --body-html "<h1>Hello</h1><p>This is <b>HTML</b></p>" \
  --from "rdreilly2010@gmail.com"
```

### Multiple Recipients

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "alice@example.com,bob@example.com,charlie@example.com" \
  --subject "Team Update" \
  --body "Status update" \
  --from "rdreilly2010@gmail.com"
```

### Custom Display Name

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "From Momotaro" \
  --body "Hello!" \
  --from "rdreilly2010@gmail.com" \
  --from-name "Momotaro 🍑"
```

### Dry Run (Test Without Sending)

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "Test" \
  --body "Test message" \
  --from "rdreilly2010@gmail.com" \
  --dry-run --verbose
```

### Verbose Output (Debugging)

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  ... \
  --verbose
```

---

## Arguments Reference

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `--to` | string | Yes | Recipient email(s), comma-separated |
| `--subject` | string | Yes | Email subject line |
| `--body` | string | Optional | Plain text body (use either --body or --body-html) |
| `--body-html` | string | Optional | HTML body (overrides --body if both provided) |
| `--from` | string | Yes | Sender email address |
| `--from-name` | string | Optional | Sender display name (default: extracted from --from) |
| `--attach` | list | Optional | File paths to attach (space-separated) |
| `--password` | string | Optional | Gmail app password (reads from env/file if not provided) |
| `--verbose` | flag | Optional | Print detailed output |
| `--dry-run` | flag | Optional | Show what would be sent without sending |

---

## Environment Variables

### GMAIL_APP_PASSWORD

If set, the script uses this as the Gmail app password:

```bash
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py ...
```

### Automatic File Reading

The script automatically checks `~/.gmail_app_password` file if the environment variable is not set.

---

## Password Storage Methods (Priority Order)

1. **Command-line argument:** `--password "xxxx xxxx xxxx xxxx"`
2. **Environment variable:** `GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"`
3. **Secure file:** `~/.gmail_app_password` (mode 600)

**Recommended:** Use secure file (`~/.gmail_app_password`)

---

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Email sent |
| 1 | Invalid arguments | Check command syntax |
| 2 | Authentication failed | Check app password and 2-Step Verification |
| 3 | Email send failed | Check recipients and connection |
| 4 | File not found | Verify attachment file paths exist |

---

## Examples

### Send Drafts to Self

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "rdreilly2010@gmail.com" \
  --subject "momo-kiji Content Drafts - Ready for Review" \
  --body "Blog post and LinkedIn versions ready for your 6:30 AM review." \
  --from "rdreilly2010@gmail.com" \
  --attach ~/.openclaw/workspace/drafts/momo-kiji-blog-post.md \
             ~/.openclaw/workspace/drafts/momo-kiji-linkedin-post.md \
             ~/.openclaw/workspace/drafts/README-DRAFTS.md
```

### Send Project Report

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "bob@example.com" \
  --subject "Project Status Report - March 2026" \
  --body-html "
    <h2>Project Status</h2>
    <p>Progress: <strong>85%</strong></p>
    <ul>
      <li>Backend API: ✅ Complete</li>
      <li>Frontend UI: ⏳ In Progress</li>
      <li>Testing: ⏳ In Progress</li>
    </ul>
    <p>Detailed report and metrics attached.</p>
  " \
  --from "rdreilly2010@gmail.com" \
  --from-name "Project Manager" \
  --attach report.pdf metrics.csv
```

### Send Team Announcement

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "alice@example.com,bob@example.com,charlie@example.com" \
  --subject "Team Meeting - Friday at 2 PM" \
  --body "Hi team,

We have a team meeting scheduled for Friday at 2 PM EDT.

Agenda:
- Project updates
- Q2 planning
- Team feedback

Looking forward to seeing everyone there!

—Momotaro" \
  --from "rdreilly2010@gmail.com"
```

---

## Troubleshooting

### "Authentication failed"

**Cause:** Wrong password or 2-Step Verification not enabled

**Solution:**
1. Verify you're using an app password (not Gmail password)
2. Check 2-Step Verification is enabled: https://myaccount.google.com/security
3. Regenerate app password if needed
4. Update `~/.gmail_app_password` file

### "Connection refused"

**Cause:** Network issue or Gmail server unreachable

**Solution:**
```bash
# Test DNS
nslookup smtp.gmail.com

# Test connection
python3 << 'EOF'
import smtplib
try:
    s = smtplib.SMTP('smtp.gmail.com', 587, timeout=5)
    s.starttls()
    print("✓ Connection successful")
    s.quit()
except Exception as e:
    print(f"✗ Error: {e}")
EOF
```

### "File not found"

**Cause:** Attachment path doesn't exist

**Solution:**
```bash
# Verify file exists
ls -la /path/to/file

# Use absolute paths (not relative)
python3 ... --attach /Users/rreilly/.openclaw/workspace/drafts/file.md
```

### "Invalid recipients"

**Cause:** Invalid email format

**Solution:**
- Ensure email addresses are valid (user@example.com format)
- Separate multiple recipients with commas (no spaces)
- Check for typos in addresses

---

## Security Best Practices

✅ **Do:**
- Store app password in `~/.gmail_app_password` with `chmod 600`
- Use app passwords (not Gmail password)
- Never commit passwords to git
- Revoke app password if compromised

❌ **Don't:**
- Share app password with others
- Store password in plain text without file permissions
- Use actual Gmail password
- Include password in scripts

**Revoke Compromised Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Find Mail password
3. Click Delete icon
4. Generate new password

---

## Performance

- **Connection time:** ~2-3 seconds (first time)
- **Send time:** 1-5 seconds (depends on attachment size)
- **Typical email:** <2 seconds
- **With large attachments:** 5-30 seconds

---

## Supported File Types

All file types supported through MIME type detection:
- **Text:** .md, .txt, .csv, .json, .html, .py, .js, etc.
- **Documents:** .pdf, .docx, .xlsx, .pptx
- **Images:** .jpg, .png, .gif, .svg
- **Audio:** .mp3, .wav, .m4a
- **Archives:** .zip, .tar, .gz
- **Binary:** Any other file type

---

## Git History

**Commit:** 7eeee18  
**Date:** March 18, 2026  
**Message:** Add gmail-send skill - Send emails with Gmail SMTP + attachments  
**Files:** 5 changed, 858 insertions

---

## Created By

Momotaro 🍑  
Date: March 18, 2026  
Status: ✅ Production-ready & Tested
