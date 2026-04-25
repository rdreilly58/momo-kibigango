#!/bin/bash
# quarterly-lessons-review.sh — surface lessons-learned entries older than 90 days
# Runs quarterly (1st of Jan/Apr/Jul/Oct at 09:00).
# Outputs a summary to observations.md and logs for human review.

set -euo pipefail

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
LESSONS_FILE="$WORKSPACE/memory/lessons-learned.md"
OBS_FILE="$WORKSPACE/memory/observations.md"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)

if [ ! -f "$LESSONS_FILE" ]; then
    echo "[quarterly-review] lessons-learned.md not found — skipping"
    exit 0
fi

# Count total entries (lines starting with "### ")
TOTAL=$(grep -c "^### " "$LESSONS_FILE" 2>/dev/null || echo 0)

# Find entries under date sections older than 90 days
CUTOFF=$(date -v-90d +%Y-%m-%d 2>/dev/null || date -d "90 days ago" +%Y-%m-%d)

# Extract date headers (## YYYY-MM-DD) older than cutoff
OLD_SECTIONS=$(grep "^## [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}" "$LESSONS_FILE" \
  | awk -F'## ' '{print $2}' \
  | while read -r d; do
      [[ "$d" < "$CUTOFF" ]] && echo "$d"
    done || true)

OLD_COUNT=$(echo "$OLD_SECTIONS" | grep -c "." 2>/dev/null || echo 0)

echo "[quarterly-review] Lessons-learned review: $TOTAL total entries, $OLD_COUNT sections older than 90 days (cutoff: $CUTOFF)"

# Write observation entry
ENTRY="- 🔵 ${TIME} **Quarterly lessons-learned review** — ${TOTAL} total entries; ${OLD_COUNT} date section(s) older than ${CUTOFF} are candidates for promotion to MEMORY.md or archival. Review: memory/lessons-learned.md <!-- dc:type=reminder dc:importance=8.0 dc:date=${DATE} -->"
echo "$ENTRY" >> "$OBS_FILE"

if [ "$OLD_COUNT" -gt 0 ]; then
    echo ""
    echo "Sections older than $CUTOFF:"
    echo "$OLD_SECTIONS"
    echo ""
    echo "ACTION: Review these sections in memory/lessons-learned.md."
    echo "  - Promote generalisable lessons to MEMORY.md feedback entries"
    echo "  - Archive or delete entries that are no longer relevant"
    echo "  - Update 'Prevention' steps if system has changed"
fi

# Dead-man heartbeat
bash "$WORKSPACE/scripts/cron-heartbeat.sh" quarterly-lessons-review $? 2>/dev/null || true
