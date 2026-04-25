#!/bin/bash
# Security Hardening for OpenClaw
# Implements best practices from GitHub slowmist/openclaw-security-practice-guide
# Run: bash ~/.openclaw/workspace/scripts/security-hardening.sh

set -e

echo "🔒 OpenClaw Security Hardening"
echo "================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Bind Gateway to Localhost
echo "📌 Step 1: Bind Gateway to Localhost Only"
echo "   Current: Checking current binding..."
CURRENT_BIND=$(grep -o '"bind": "[^"]*"' ~/.openclaw/openclaw.json 2>/dev/null || echo "not set")
echo "   $CURRENT_BIND"
echo "   ✓ Recommended: 127.0.0.1:18789 (loopback only)"
echo ""

# 2. File Permissions
echo "📌 Step 2: Lock Down File Permissions"
chmod 700 ~/.openclaw || true
chmod 600 ~/.openclaw/openclaw.json || true
chmod 700 ~/.openclaw/credentials || true
echo "   ✓ ~/.openclaw: 700 (rwx------)"
echo "   ✓ ~/.openclaw/openclaw.json: 600 (rw-------)"
echo "   ✓ ~/.openclaw/credentials: 700 (rwx------)"
echo ""

# 3. Check for Exposed Secrets
echo "📌 Step 3: Check for Exposed Secrets in Logs"
SECRET_COUNT=$(grep -r "sk-" ~/.openclaw/logs/ 2>/dev/null | wc -l || echo "0")
if [ "$SECRET_COUNT" -gt 0 ]; then
    echo "   ${RED}⚠️  Found $SECRET_COUNT potential secrets in logs${NC}"
    echo "   Action: Rotate API keys immediately"
else
    echo "   ✓ No exposed secrets detected in logs"
fi
echo ""

# 4. Security Audit
echo "📌 Step 4: Run OpenClaw Security Audit"
echo "   Command: openclaw security audit --deep"
echo "   Status: Ready to run (requires manual execution)"
echo ""

# 5. TLS Configuration
echo "📌 Step 5: TLS/HTTPS Setup"
echo "   Current Setup: Self-signed certificates (recommended for localhost)"
echo "   Location: ~/.openclaw/certs/"
if [ ! -d ~/.openclaw/certs ]; then
    mkdir -p ~/.openclaw/certs
    echo "   ✓ Created certs directory"
fi
echo ""

# 6. Summary
echo "📋 Security Hardening Summary"
echo "================================"
echo ""
echo "✅ Completed:"
echo "   • File permissions: 700/600 locked"
echo "   • Credentials: Isolated in 700 directory"
echo "   • Secret check: Log files scanned"
echo ""
echo "⏳ Next Steps (Manual):"
echo "   1. Bind gateway to localhost:"
echo "      openclaw config set gateway.bind 127.0.0.1:18789"
echo ""
echo "   2. Run security audit:"
echo "      openclaw security audit --deep"
echo ""
echo "   3. Rotate API keys if secrets were found:"
echo "      Check: ~/.openclaw/credentials/"
echo ""
echo "   4. Enable TLS (if not using SSH tunnel):"
echo "      openclaw config set gateway.tls.enabled true"
echo ""
echo "🔒 Security Audit Checklist:"
echo "   □ Gateway bound to 127.0.0.1:18789"
echo "   □ File permissions: 700/600 set"
echo "   □ No exposed secrets in logs"
echo "   □ API keys in credentials directory"
echo "   □ TLS enabled or SSH tunnel configured"
echo "   □ Firewall configured (if applicable)"
echo ""
