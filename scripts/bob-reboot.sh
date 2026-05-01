#!/bin/bash
# bob-reboot.sh — Graceful reboot wrapper.
# Quits known shutdown-blocking apps, then triggers reboot.
#
# Usage:  bob-reboot
#         bob-reboot --shutdown  (power off instead of restart)
#
# What it does:
#   1. Run pre-reboot-quit-apps.sh (Mail, Music, Photos, Safari)
#   2. Wait 3 s for things to settle
#   3. Call sudo shutdown -r now (or -h now for full shutdown)
#
# Why: macOS 26.3 Mail.app's WebKit children refuse graceful termination,
# causing 60-90 s shutdown hangs. Pre-quitting them avoids this.

set -uo pipefail

MODE="reboot"
if [ "${1:-}" = "--shutdown" ] || [ "${1:-}" = "-s" ]; then
    MODE="shutdown"
fi

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"

echo "🍑 Pre-reboot cleanup starting..."

# Step 1: Run app-quit script directly (more reliable than the launchd watch path)
bash "$WORKSPACE/scripts/pre-reboot-quit-apps.sh"

# Step 2: Brief pause
echo ""
echo "⏳ Settling for 3 s before shutdown..."
sleep 3

# Step 3: Initiate the reboot
if [ "$MODE" = "shutdown" ]; then
    echo "⏻  Shutting down now..."
    sudo shutdown -h now
else
    echo "🔄 Rebooting now..."
    sudo shutdown -r now
fi
