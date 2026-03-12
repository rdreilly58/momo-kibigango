#!/bin/bash
# Setup Gmail access via both Python IMAP and Himalaya

set -e

EMAIL="rdreilly2010@gmail.com"
WORKSPACE="$HOME/.openclaw/workspace"

echo "=== Gmail Access Setup ==="
echo "Email: $EMAIL"
echo ""

# Part 1: Python IMAP Setup
echo "1️⃣  Setting up Python Gmail Reader (IMAP)..."
if [ -f "$WORKSPACE/scripts/gmail_reader.py" ]; then
    chmod +x "$WORKSPACE/scripts/gmail_reader.py"
    echo "   ✓ gmail_reader.py ready"
    echo "   Usage: python3 gmail_reader.py <email> <app_password> <command>"
else
    echo "   ✗ gmail_reader.py not found"
    exit 1
fi

# Part 2: Himalaya Setup
echo ""
echo "2️⃣  Setting up Himalaya CLI (IMAP/SMTP)..."

if ! command -v himalaya &> /dev/null; then
    echo "   ✗ Himalaya not installed. Installing..."
    brew install himalaya
fi

echo "   ✓ Himalaya installed"
echo ""
echo "   Next, run: himalaya account configure $EMAIL"
echo "   This will prompt for IMAP settings (Gmail will provide app password option)"
echo ""

echo ""
echo "=== NEXT STEPS ==="
echo ""
echo "1. Get your Gmail App Password:"
echo "   → https://myaccount.google.com/security"
echo "   → App passwords (select Gmail + your device)"
echo "   → Copy the 16-character password"
echo ""
echo "2. Set up Python Gmail Reader:"
echo "   python3 $WORKSPACE/scripts/gmail_reader.py <email> <app_password> list"
echo ""
echo "3. Set up Himalaya (interactive):"
echo "   himalaya account configure $EMAIL"
echo "   (Use app password when prompted for password)"
echo ""
echo "4. After setup, test:"
echo "   himalaya message list"
echo "   himalaya message search 'RDS Analytics'"
echo ""
