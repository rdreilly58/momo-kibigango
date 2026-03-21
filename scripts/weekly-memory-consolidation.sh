#!/bin/bash
# Weekly Memory Consolidation Script (runs Sunday 4:00 AM)
# Purpose: Archive old files, consolidate MEMORY.md, clean orphaned sessions

set -e

WORKSPACE="$HOME/.openclaw/workspace"
ARCHIVE_DIR="$WORKSPACE/memory/archive"
MEMORY_FILE="$WORKSPACE/MEMORY.md"

echo "📦 Weekly Memory Consolidation ($(date))"
echo "=================================================="

# 1. Archive daily files older than 7 days
echo "🗂️  Archiving daily files (>7 days old)..."
find "$WORKSPACE/memory" -maxdepth 1 -name "*.md" -type f -mtime +7 -exec mv {} "$ARCHIVE_DIR/" \; 2>/dev/null || true

# 2. Check MEMORY.md size and sections
MEMORY_LINES=$(wc -l < "$MEMORY_FILE" 2>/dev/null || echo 0)
echo "   MEMORY.md: $MEMORY_LINES lines"

if [ "$MEMORY_LINES" -gt 1000 ]; then
    echo "⚠️  MEMORY.md exceeds 1000 lines ($MEMORY_LINES)"
    echo "   Action needed: Archive old sections manually"
    echo "   Structure: Move older entries to memory/archive/MEMORY-2026-Q1.md"
fi

# 3. Count files
DAILY_COUNT=$(ls -1 "$WORKSPACE/memory"/*.md 2>/dev/null | wc -l)
ARCHIVE_COUNT=$(ls -1 "$ARCHIVE_DIR"/*.md 2>/dev/null | wc -l)

echo ""
echo "📊 Memory Inventory:"
echo "   Active daily files: $DAILY_COUNT"
echo "   Archived files: $ARCHIVE_COUNT"
echo "   Total memory: $(du -sh $WORKSPACE/memory/ | cut -f1)"
echo ""

# 4. Git commit
cd "$WORKSPACE"
git add -A && git commit -m "chore: Weekly memory consolidation and archival ($(date +%Y-%m-%d))" || true

echo "✅ Weekly consolidation complete"
echo "=================================================="
