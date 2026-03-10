#!/bin/bash
set -e

# Source shell environment
source ~/.zprofile 2>/dev/null || true

STATUS=$(/opt/homebrew/bin/openclaw gateway status 2>&1)

if echo "$STATUS" | grep -q "running"; then
    osascript << 'APPLE'
    set choice to button returned of (display dialog "OpenClaw Gateway is running." buttons {"Stop Gateway", "Open Dashboard", "Cancel"} default button "Open Dashboard" with title "OpenClaw Gateway" with icon note)
    if choice is "Stop Gateway" then
        delay 0.5
        tell application "Terminal"
            activate
            do script "/opt/homebrew/bin/openclaw gateway stop"
        end tell
    else if choice is "Open Dashboard" then
        open location "http://127.0.0.1:18789/"
    end if
APPLE
else
    osascript << 'APPLE'
    set choice to button returned of (display dialog "OpenClaw Gateway is not running." buttons {"Start Gateway", "Cancel"} default button "Start Gateway" with title "OpenClaw Gateway" with icon caution)
    if choice is "Start Gateway" then
        delay 0.5
        tell application "Terminal"
            activate
            do script "/opt/homebrew/bin/openclaw gateway start"
        end tell
    end if
APPLE
fi
