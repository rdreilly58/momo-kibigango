# Gmail Send Skill - Setup Guide

## Prerequisites

- Gmail account with 2-Step Verification enabled
- Python 3 (already available on your Mac)
- App-specific password from Google

## Step 1: Enable 2-Step Verification (If Needed)

1. Go to https://myaccount.google.com/security
2. Look for "2-Step Verification"
3. If not enabled, click "Enable 2-Step Verification" and follow prompts
4. You'll need a phone to verify

## Step 2: Generate App Password

Once 2-Step Verification is enabled:

1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" from first dropdown
3. Select "macOS" from second dropdown  
4. Click "Generate"
5. Google shows a 16-character password (with spaces): `xxxx xxxx xxxx xxxx`
6. Copy the entire password

## Step 3: Store App Password Securely

### Option A: Secure File (RECOMMENDED)

```bash
# Create file with restrictive permissions
echo "xxxx xxxx xxxx xxxx" > ~/.gmail_app_password
chmod 600 ~/.gmail_app_password

# Verify permissions (should show rw-------)
ls -la ~/.gmail_app_password
```

The script will automatically find and use this file.

### Option B: Environment Variable

```bash
# Temporary (current terminal session only)
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"

# Verify
echo $GMAIL_APP_PASSWORD
```

### Option C: Command-Line Argument

```bash
# Include in every command (not recommended - visible in history)
--password "xxxx xxxx xxxx xxxx"
```

## Step 4: Test the Setup

### Test 1: Dry Run (No Email Sent)

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "rdreilly2010@gmail.com" \
  --subject "Test Email" \
  --body "This is a test" \
  --from "rdreilly2010@gmail.com" \
  --dry-run \
  --verbose
```

You should see output showing the email details without sending.

### Test 2: Send Test Email

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "rdreilly2010@gmail.com" \
  --subject "Gmail Skill Test" \
  --body "If you see this, the Gmail skill is working!" \
  --from "rdreilly2010@gmail.com" \
  --verbose
```

Check your Gmail inbox for the test email.

### Test 3: Send with Attachments

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "rdreilly2010@gmail.com" \
  --subject "Test with Attachments" \
  --body "See attached files" \
  --from "rdreilly2010@gmail.com" \
  --attach ~/.openclaw/workspace/drafts/momo-kiji-blog-post.md
```

## Troubleshooting

### "Authentication failed"

**Check:**
1. Password is 16 characters (with spaces: `xxxx xxxx xxxx xxxx`)
2. It's an APP password, not your Gmail password
3. 2-Step Verification is enabled
4. Password file has correct permissions: `chmod 600 ~/.gmail_app_password`

**Test connection:**
```bash
python3 << 'EOF'
import smtplib
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    password = open(os.path.expanduser("~/.gmail_app_password")).read().strip()
    server.login("rdreilly2010@gmail.com", password)
    print("✓ Connection successful!")
    server.quit()
except Exception as e:
    print(f"✗ Error: {e}")
EOF
```

### "Connection refused"

**Check:**
1. Internet connection is working
2. Gmail SMTP server (smtp.gmail.com:587) is reachable

**Test connectivity:**
```bash
# Test DNS resolution
nslookup smtp.gmail.com

# Test port connectivity  
telnet smtp.gmail.com 587
```

### "File not found"

**Check:**
1. File paths exist: `ls -la /path/to/file`
2. File permissions allow reading: `ls -la file`
3. Use absolute paths, not relative paths

## Usage Examples

### Send to Yourself

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "rdreilly2010@gmail.com" \
  --subject "Draft for Review" \
  --body "Please review attached documents" \
  --from "rdreilly2010@gmail.com" \
  --attach ~/drafts/document1.md ~/drafts/document2.md
```

### Send to Multiple People

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "bob@example.com,alice@example.com,charlie@example.com" \
  --subject "Project Update" \
  --body "Latest changes and reports attached" \
  --from "rdreilly2010@gmail.com" \
  --attach report.pdf summary.md
```

### Send HTML Email

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "HTML Email" \
  --body-html "<h1>Hello</h1><p>This is <strong>formatted</strong> HTML</p>" \
  --from "rdreilly2010@gmail.com"
```

### With Custom Display Name

```bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "From Momotaro" \
  --body "Hello!" \
  --from "rdreilly2010@gmail.com" \
  --from-name "Momotaro 🍑"
```

## Security Notes

✅ **Do:**
- Store app password in `~/.gmail_app_password` with permissions `600`
- Use app passwords (not your Gmail password)
- Revoke app password if compromised (in Gmail security settings)
- Use this skill for automated emails only

❌ **Don't:**
- Share your app password
- Commit app password to Git
- Use your actual Gmail password
- Store password in plain text files without permissions

## Revoking App Password

If your app password is compromised:

1. Go to https://myaccount.google.com/apppasswords
2. Find the Mail app password
3. Click the Delete icon (trash can)
4. Generate a new password and update `~/.gmail_app_password`

## Advanced: Create Wrapper Script

For convenience, create a wrapper script `~/.local/bin/send-gmail`:

```bash
#!/bin/bash
python3 ~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py "$@"
```

Then use it directly:
```bash
send-gmail --to bob@example.com --subject "Test" --body "Hi" --from rdreilly2010@gmail.com
```

## Support

If you encounter issues:

1. Run with `--verbose` flag for detailed output
2. Check error message carefully (authentication vs connection vs file)
3. Review this setup guide
4. Test each step independently
5. Check SKILL.md for usage patterns
