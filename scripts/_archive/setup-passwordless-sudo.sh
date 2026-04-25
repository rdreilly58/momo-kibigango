#!/bin/bash
# Setup passwordless sudo for Momotaro (OpenClaw automation)
# Run once with: sudo bash setup-passwordless-sudo.sh

set -e

SUDOERS_FILE="/etc/sudoers.d/momotaro-nopasswd"

echo "🔧 Configuring passwordless sudo for rreilly..."

# Create the sudoers configuration
cat > /tmp/momotaro_sudoers << 'SUDOERS'
# Momotaro passwordless sudo for OpenClaw automation
# Non-TTY execution support (scripts, background processes)
# Generated: 2026-03-24

Defaults use_pty
Defaults lecture="never"
Defaults !requiretty

# File operations (remove, move, copy, change permissions)
rreilly ALL=(ALL) NOPASSWD: /usr/bin/rm, /usr/bin/rmdir, /bin/rm, /bin/rmdir
rreilly ALL=(ALL) NOPASSWD: /bin/cp, /usr/bin/cp, /bin/mv, /usr/bin/mv
rreilly ALL=(ALL) NOPASSWD: /usr/bin/chown, /usr/bin/chmod

# System services (launchctl, brew)
rreilly ALL=(ALL) NOPASSWD: /bin/launchctl, /usr/bin/launchctl
rreilly ALL=(ALL) NOPASSWD: /opt/homebrew/bin/brew, /usr/local/bin/brew

# System updates and tools
rreilly ALL=(ALL) NOPASSWD: /usr/sbin/softwareupdate
rreilly ALL=(ALL) NOPASSWD: /usr/sbin/systemctl, /usr/sbin/dscacheutil

# Search and discovery
rreilly ALL=(ALL) NOPASSWD: /usr/bin/find, /usr/bin/xargs, /usr/bin/grep
SUDOERS

# Validate syntax
if /usr/sbin/visudo -c -f /tmp/momotaro_sudoers; then
    echo "✅ Sudoers syntax valid"
    
    # Remove old entry if it exists
    if [ -f "$SUDOERS_FILE" ]; then
        rm -f "$SUDOERS_FILE"
        echo "Removed old sudoers entry"
    fi
    
    # Install new entry
    cp /tmp/momotaro_sudoers "$SUDOERS_FILE"
    chmod 440 "$SUDOERS_FILE"
    
    echo "✅ Sudoers installed: $SUDOERS_FILE"
    echo "✅ Passwordless sudo is now active for rreilly"
    
    # Cleanup
    rm -f /tmp/momotaro_sudoers
else
    echo "❌ Sudoers syntax validation failed"
    exit 1
fi

echo ""
echo "🎯 Next step: Test with:"
echo "   sudo -n /bin/echo 'Passwordless sudo works!'"
