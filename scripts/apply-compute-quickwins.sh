#!/bin/bash
# apply-compute-quickwins.sh
# Run once to apply system-level compute optimizations for OpenClaw + Ollama
# Requires sudo for pmset and mdutil

set -e
echo "🚀 Applying compute quick wins..."

echo ""
echo "1/4 — Power management: disable sleep/nap (server mode)"
# Mac mini as a server: never sleep, never hibernate, never spin down disks
sudo pmset -a sleep 0           # disable system sleep
sudo pmset -a disksleep 0       # disable disk sleep
sudo pmset -a displaysleep 10   # displays can sleep (saves power, not perf)
sudo pmset -a autopoweroff 0    # disable auto power-off
sudo pmset -a standby 0         # disable standby
sudo pmset -a womp 1            # wake on network (keep responding)
sudo pmset -a ttyskeepawake 1   # stay awake while terminal/SSH active
echo "   ✅ pmset configured for server mode"

echo ""
echo "2/4 — Spotlight: exclude workspace from indexing"
# Workspace has lots of churn (logs, memory files, json) — indexing wastes I/O
sudo mdutil -i off /Users/rreilly/.openclaw 2>/dev/null || true
echo "   ✅ Spotlight indexing disabled for ~/.openclaw"

echo ""
echo "3/4 — Reload Ollama with new plist settings"
launchctl unload ~/Library/LaunchAgents/homebrew.mxcl.ollama.plist 2>/dev/null || true
sleep 2
launchctl load ~/Library/LaunchAgents/homebrew.mxcl.ollama.plist
sleep 3
echo "   ✅ Ollama reloaded (KEEP_ALIVE=-1, NUM_PARALLEL=2, Nice=-5)"

echo ""
echo "4/4 — File descriptor limits (for high-concurrency sessions)"
# Check current launchd limits
echo "   Current limits:"
launchctl limit maxfiles
# OpenClaw opens many file handles (sessions, logs, sqlite, sockets)
# macOS default is 256/unlimited — increase soft limit
sudo launchctl limit maxfiles 65536 200000
echo "   ✅ maxfiles limit raised to 65536/200000"

echo ""
echo "✅ All quick wins applied."
echo ""
echo "Current pmset profile:"
pmset -g | grep -E "sleep|nap|standby|autopoweroff|disksleep|womp|ttyskeep"
echo ""
echo "Ollama status:"
ollama ps 2>/dev/null || echo "(no models currently loaded)"
