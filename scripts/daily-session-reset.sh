#!/bin/bash
# Daily Session Reset Script (runs at 4:00 AM)
# Purpose: Reset main session, flush memory, prepare for new day
#
# Also provides log_session_entry() helper — source this file or call:
#   bash daily-session-reset.sh --log "Summary text here"

set -e

WORKSPACE="$HOME/.openclaw/workspace"
ARCHIVE_DIR="$WORKSPACE/memory/archive"
DAILY_LOG="$WORKSPACE/memory/$(date +%Y-%m-%d).md"

# ── Helper: append a timestamped entry to today's daily log ──────────────────
# Usage: log_session_entry "Tasks" "- Did X\n- Did Y"
#        or called via:  bash daily-session-reset.sh --log "summary text"
log_session_entry() {
    local section="${1:-End of Day Summary}"
    local content="$2"
    local file="$WORKSPACE/memory/$(date +%Y-%m-%d).md"
    local ts
    ts=$(date '+%H:%M')

    # Create file if missing
    if [ ! -f "$file" ]; then
        cat > "$file" << TMPL
# Daily Notes - Session Log

## Session Start
- Time: $(date)
- Status: Fresh session reset

## Tasks

## Learnings

## Issues Encountered

## End of Day Summary
TMPL
    fi

    # Append under the right section header (or at end if not found)
    if grep -q "^## ${section}" "$file" 2>/dev/null; then
        # Insert after the section header line
        local escaped
        escaped=$(printf '%s\n' "$content" | sed 's/[[\.*^$()+?{|]/\\&/g')
        sed -i '' "/^## ${section}/a\\
${content}
" "$file" 2>/dev/null || printf '\n%s\n' "$content" >> "$file"
    else
        printf '\n## %s\n%s\n' "$section" "$content" >> "$file"
    fi

    echo "[$ts] Logged to $file (section: $section)"
}

# If called with --log, append a summary entry and exit
if [[ "${1:-}" == "--log" ]]; then
    log_session_entry "End of Day Summary" "${2:-}"
    exit 0
fi

echo "🔄 Daily Session Reset ($(date))"
echo "=================================================="

# 1. Create daily memory file if not exists
if [ ! -f "$DAILY_LOG" ]; then
    echo "📝 Creating daily log: $DAILY_LOG"
    cat > "$DAILY_LOG" << EOF
# Daily Notes - Session Log

## Session Start
- Time: $(date)
- Status: Fresh session reset

## Tasks

## Learnings

## Issues Encountered

## End of Day Summary
EOF
fi

# 2. Archive yesterday's memory if it exists
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "1 day ago" +%Y-%m-%d)
YESTERDAY_FILE="$WORKSPACE/memory/$YESTERDAY.md"
if [ -f "$YESTERDAY_FILE" ]; then
    echo "📦 Archiving yesterday's memory: $YESTERDAY.md"
    cp "$YESTERDAY_FILE" "$ARCHIVE_DIR/$YESTERDAY.md"
fi

# 3. Memory consolidation (extract key items to MEMORY.md)
echo "🧠 Consolidating key learnings to MEMORY.md"
# This is a placeholder - actual consolidation happens via heartbeat

# 4. Check MEMORY.md size (keep under 1000 lines)
MEMORY_LINES=$(wc -l < "$WORKSPACE/MEMORY.md" 2>/dev/null || echo 0)
if [ "$MEMORY_LINES" -gt 1500 ]; then
    echo "⚠️  MEMORY.md is $MEMORY_LINES lines (>1000 recommended)"
    echo "   Consider archiving older sections to memory/archive/"
fi

# 5. Log reset event
echo "✅ Session reset complete"
echo ""
echo "📊 Memory Statistics:"
echo "   MEMORY.md: $MEMORY_LINES lines"
echo "   Daily files: $(ls -1 $WORKSPACE/memory/*.md 2>/dev/null | wc -l)"
echo "   Archived files: $(ls -1 $ARCHIVE_DIR/*.md 2>/dev/null | wc -l)"
echo ""
echo "=================================================="
