#!/bin/bash
# Setup Gmail App Password for gmail-send skill
# Author: Momotaro
# Date: March 18, 2026

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PASSWORD_FILE="$HOME/.gmail_app_password"

echo "📧 Gmail Send Skill - Setup Helper"
echo "=================================="
echo ""

# Check if password file already exists
if [ -f "$PASSWORD_FILE" ]; then
    echo "⚠️  Password file already exists: $PASSWORD_FILE"
    read -p "Do you want to replace it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing password file"
        exit 0
    fi
fi

# Get password from user
echo "📍 To get your Gmail app password:"
echo "   1. Go to https://myaccount.google.com/apppasswords"
echo "   2. Enable 2-Step Verification if needed"
echo "   3. Select 'Mail' and 'macOS'"
echo "   4. Click 'Generate'"
echo "   5. Copy the 16-character password (xxxx xxxx xxxx xxxx)"
echo ""
read -sp "Enter your Gmail app password: " APP_PASSWORD
echo ""

# Verify password format
if [[ ! "$APP_PASSWORD" =~ ^[a-z]{4}\ [a-z]{4}\ [a-z]{4}\ [a-z]{4}$ ]]; then
    echo "⚠️  Warning: Password doesn't match expected format (xxxx xxxx xxxx xxxx)"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled"
        exit 1
    fi
fi

# Write password file
echo "$APP_PASSWORD" > "$PASSWORD_FILE"
chmod 600 "$PASSWORD_FILE"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Password file created: $PASSWORD_FILE"
echo "Permissions: $(stat -f '%OLp' "$PASSWORD_FILE")"
echo ""
echo "📧 Test the setup:"
echo "   python3 $SCRIPT_DIR/send_email.py \\"
echo "     --to 'rdreilly2010@gmail.com' \\"
echo "     --subject 'Gmail Skill Test' \\"
echo "     --body 'Test message' \\"
echo "     --from 'rdreilly2010@gmail.com' \\"
echo "     --dry-run"
echo ""
