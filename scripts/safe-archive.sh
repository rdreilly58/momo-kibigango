#!/usr/bin/env bash
# safe-archive.sh — Check for active callers before archiving a script/file
# Usage: bash safe-archive.sh <file-to-archive>
# Returns non-zero if active references found (blocks archive)

set -euo pipefail

WORKSPACE="${HOME}/.openclaw/workspace"
CRON_DIR="${HOME}/.openclaw/cron"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <file-to-archive>"
  exit 1
fi

TARGET="$1"
BASENAME="$(basename "$TARGET")"
FOUND=0

echo "🔍 Checking for active references to: $BASENAME"
echo ""

# Search in workspace scripts
echo "=== Workspace scripts ==="
RESULTS=$(grep -rl "$BASENAME" "$WORKSPACE/scripts/" 2>/dev/null || true)
if [[ -n "$RESULTS" ]]; then
  echo "⚠️  Found in scripts:"
  echo "$RESULTS" | sed 's/^/   /'
  FOUND=1
else
  echo "   ✅ Clean"
fi

# Search in cron jobs
echo ""
echo "=== Cron jobs ==="
RESULTS=$(grep -rl "$BASENAME" "$CRON_DIR/" 2>/dev/null || true)
if [[ -n "$RESULTS" ]]; then
  echo "⚠️  Found in cron:"
  echo "$RESULTS" | sed 's/^/   /'
  FOUND=1
else
  echo "   ✅ Clean"
fi

# Search in agent configs
echo ""
echo "=== Agent configs / HEARTBEAT / AGENTS.md ==="
RESULTS=$(grep -rl "$BASENAME" "$WORKSPACE" --include="*.md" --include="*.json" --include="*.sh" \
  --exclude-dir=".git" --exclude-dir="_archive" 2>/dev/null | grep -v "$TARGET" || true)
if [[ -n "$RESULTS" ]]; then
  echo "⚠️  Found in workspace files:"
  echo "$RESULTS" | sed 's/^/   /'
  FOUND=1
else
  echo "   ✅ Clean"
fi

# Search in LaunchAgents
echo ""
echo "=== LaunchAgents ==="
RESULTS=$(grep -rl "$BASENAME" ~/Library/LaunchAgents/ 2>/dev/null || true)
if [[ -n "$RESULTS" ]]; then
  echo "⚠️  Found in LaunchAgents:"
  echo "$RESULTS" | sed 's/^/   /'
  FOUND=1
else
  echo "   ✅ Clean"
fi

echo ""
if [[ $FOUND -eq 1 ]]; then
  echo "❌ BLOCKED: '$BASENAME' has active references. Resolve them before archiving."
  exit 1
else
  echo "✅ SAFE TO ARCHIVE: No active references found for '$BASENAME'."
  exit 0
fi
