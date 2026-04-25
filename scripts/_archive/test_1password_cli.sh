#!/bin/bash
# 1Password CLI Test Script
# Run this after completing 1Password account setup

echo "Testing 1Password CLI Integration..."
echo "===================================="

# Check if op CLI is installed
if ! command -v op &> /dev/null; then
    echo "❌ 1Password CLI (op) not found!"
    echo "Install with: brew install 1password-cli"
    exit 1
fi

echo "✅ 1Password CLI found: $(op --version)"

# Test signin
echo -e "\n📝 Attempting to sign in..."
echo "Make sure 1Password desktop app is running and unlocked"

# Use tmux for persistent session as per skill requirements
SOCKET_DIR="${TMPDIR:-/tmp}/openclaw-tmux-sockets"
mkdir -p "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/openclaw-op.sock"
SESSION="op-test-$(date +%Y%m%d-%H%M%S)"

# Create tmux session and test op commands
tmux -S "$SOCKET" new -d -s "$SESSION" -n shell
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op signin" Enter
sleep 3
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op whoami" Enter
sleep 1
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op vault list" Enter
sleep 1

# Capture output
echo -e "\n📋 Output from 1Password CLI:"
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -200

# Clean up
tmux -S "$SOCKET" kill-session -t "$SESSION"

echo -e "\n✅ Test complete!"
echo "If successful, you should see your account info and vault list above."