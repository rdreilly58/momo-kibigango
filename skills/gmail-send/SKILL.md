---
name: gmail-send
description: "Send emails via Gmail SMTP with attachments. Use when you need to send documents, files, or messages to Gmail addresses. Supports single/multiple recipients, HTML/text content, file attachments, and Gmail authentication via app password."
---

# Gmail Send Email Skill

Send emails via Gmail SMTP with full support for attachments, HTML content, and multiple recipients.

## Quick Start

### 1. Set Up Gmail App Password (One-time)

Gmail requires an app-specific password for SMTP access (not your regular Gmail password).

```bash
# Set the app password as an environment variable
export GMAIL_APP_PASSWORD="your-16-character-app-password"

# Or store in ~/.openclaw/workspace/TOOLS.md for reference
```

**How to get an app password:**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification (if not already enabled)
3. Go to "App passwords" 
4. Select "Mail" and "macOS"
5. Copy the 16-character password
6. Store it safely in your environment or TOOLS.md

### 2. Send an Email

```bash
# Simple email
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "Test Email" \
  --body "Hello from Momotaro!" \
  --from "rdreilly2010@gmail.com"

# With attachment
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "bob@example.com" \
  --subject "Your Documents" \
  --body "Here are your files" \
  --from "rdreilly2010@gmail.com" \
  --attach "/path/to/file.pdf" "/path/to/file.md"

# HTML email
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "user@example.com" \
  --subject "HTML Email" \
  --body-html "<h1>Hello</h1><p>This is HTML</p>" \
  --from "rdreilly2010@gmail.com"
```

## Usage Patterns

### Send to Self

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "rdreilly2010@gmail.com" \
  --subject "Draft Review" \
  --body "Files attached for review" \
  --from "rdreilly2010@gmail.com" \
  --attach ~/.openclaw/workspace/drafts/momo-kiji-blog-post.md \
             ~/.openclaw/workspace/drafts/momo-kiji-linkedin-post.md
```

### Send with Multiple Recipients

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "bob@example.com,alice@example.com,charlie@example.com" \
  --subject "Project Update" \
  --body "Latest changes attached" \
  --from "rdreilly2010@gmail.com" \
  --attach draft.md results.pdf
```

### Send with Custom From Name

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "Message" \
  --body "Content" \
  --from "rdreilly2010@gmail.com" \
  --from-name "Momotaro 🍑"
```

## Environment Setup

### Option 1: Environment Variable (Temporary)

```bash
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py ...
```

### Option 2: Source from File (Recommended)

Create `~/.gmail_app_password` (mode 600):

```bash
echo "xxxx xxxx xxxx xxxx" > ~/.gmail_app_password
chmod 600 ~/.gmail_app_password
```

The script will automatically read it.

### Option 3: Command-line Argument

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  ... \
  --password "xxxx xxxx xxxx xxxx"
```

## Script Reference

**File:** `scripts/send_email.py`

**Arguments:**
- `--to` *(required)*: Recipient email(s), comma-separated
- `--subject` *(required)*: Email subject line
- `--body` *(optional)*: Plain text body (use either `--body` or `--body-html`)
- `--body-html` *(optional)*: HTML body (overrides `--body` if both provided)
- `--from` *(required)*: Sender email address
- `--from-name` *(optional)*: Display name (default: extracted from --from)
- `--attach` *(optional)*: One or more file paths to attach
- `--password` *(optional)*: Gmail app password (reads from env/file if not provided)
- `--verbose` *(optional)*: Print detailed output
- `--dry-run` *(optional)*: Show what would be sent without actually sending

**Exit codes:**
- `0`: Success
- `1`: Invalid arguments
- `2`: Authentication failed
- `3`: Email send failed
- `4`: File not found

## Examples

### Send Draft Documents for Review

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "rdreilly2010@gmail.com" \
  --subject "momo-kiji Content Drafts - Ready for Review" \
  --body "Blog post and LinkedIn versions attached for your 6:30 AM review." \
  --from "rdreilly2010@gmail.com" \
  --attach ~/.openclaw/workspace/drafts/momo-kiji-blog-post.md \
             ~/.openclaw/workspace/drafts/momo-kiji-linkedin-post.md \
             ~/.openclaw/workspace/drafts/README-DRAFTS.md
```

### Send with HTML Formatting

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "Project Status" \
  --body-html "
    <h2>Status Update</h2>
    <p>Project completion: <strong>85%</strong></p>
    <ul>
      <li>Task 1: Complete</li>
      <li>Task 2: In Progress</li>
      <li>Task 3: Pending</li>
    </ul>
    <p>Files attached for review.</p>
  " \
  --from "rdreilly2010@gmail.com" \
  --attach report.pdf summary.md
```

### Test Email (Dry Run)

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "test@example.com" \
  --subject "Test" \
  --body "Test message" \
  --from "rdreilly2010@gmail.com" \
  --dry-run \
  --verbose
```

## Troubleshooting

### "Authentication failed"
- Verify Gmail app password is correct (16 characters)
- Check it's an app password, not your regular Gmail password
- Ensure 2-Step Verification is enabled on Gmail account
- Try with `--verbose` flag to see detailed errors

### "Connection refused"
- Check internet connection
- Gmail SMTP server: `smtp.gmail.com:587`
- Try running: `telnet smtp.gmail.com 587`

### "File not found"
- Verify file paths are absolute or relative to current directory
- Use `ls -la` to confirm files exist
- Check file permissions (script needs read access)

### "Email send failed"
- Check recipient email addresses are valid
- Verify no special characters in subject/body causing encoding issues
- Try `--verbose` for detailed error output

## Security Notes

- **Never commit passwords** to git
- **Use environment variables** or secure files (mode 600)
- **App passwords** are single-use tokens for this app only (not your Gmail password)
- If password is compromised, revoke it immediately in Gmail security settings
- The script connects via TLS to `smtp.gmail.com:587` (secure)

## Advanced

### Debug Mode

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  ... \
  --verbose
```

Shows detailed SMTP conversation and debugging info.

### Test Connection

```bash
python3 << 'EOF'
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
print("✓ Connection successful")
server.quit()
EOF
```

### List Available Encodings

```bash
python3 -c "import encodings; print([x for x in dir(encodings) if not x.startswith('_')][:10])"
```

## Files

- `scripts/send_email.py` - Main email sending script
- `SKILL.md` - This file (documentation)

## Version

- Created: March 18, 2026
- Version: 1.0
- Last Updated: March 18, 2026 (Debugged & Tested)
