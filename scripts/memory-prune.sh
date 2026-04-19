#!/bin/bash
# Memory Pruning Automation
# Archives daily memory files older than N days
# Keeps reference files (non-dated) in place
# Reindexes after pruning
#
# Usage: memory-prune.sh [--days 30] [--dry-run] [--reindex]

set -e

MEMORY_DIR="$HOME/.openclaw/workspace/memory"
ARCHIVE_DIR="$MEMORY_DIR/archive"
DAYS=30
DRY_RUN=false
REINDEX=true
LOG_FILE="$HOME/.openclaw/logs/memory-prune.log"

while [[ $# -gt 0 ]]; do
    case $1 in
        --days) DAYS="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        --no-reindex) REINDEX=false; shift ;;
        *) echo "Unknown: $1"; exit 1 ;;
    esac
done

mkdir -p "$ARCHIVE_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

CUTOFF=$(date -v-${DAYS}d +%Y-%m-%d 2>/dev/null || date -d "${DAYS} days ago" +%Y-%m-%d)
NOW=$(date '+%Y-%m-%d %H:%M:%S')
ARCHIVED=0
SKIPPED=0
KEPT=0

echo "[$NOW] Memory Pruning — archiving daily files older than $DAYS days (before $CUTOFF)"
echo "[$NOW] Memory Pruning — cutoff: $CUTOFF, dry-run: $DRY_RUN" >> "$LOG_FILE"

# Only process dated daily files (YYYY-MM-DD*.md pattern)
for f in "$MEMORY_DIR"/2026-*.md; do
    [ -f "$f" ] || continue
    
    basename=$(basename "$f")
    
    # Extract date from filename (first 10 chars: YYYY-MM-DD)
    file_date="${basename:0:10}"
    
    # Validate it's a real date
    if ! [[ "$file_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        echo "  SKIP (not a date): $basename"
        ((SKIPPED++))
        continue
    fi
    
    # Compare dates (string comparison works for YYYY-MM-DD)
    if [[ "$file_date" < "$CUTOFF" ]]; then
        size=$(wc -c < "$f" | tr -d ' ')
        
        if $DRY_RUN; then
            echo "  WOULD ARCHIVE: $basename ($size bytes, date: $file_date)"
        else
            # Move to archive
            mv "$f" "$ARCHIVE_DIR/$basename"
            echo "  ARCHIVED: $basename ($size bytes)"
            echo "[$NOW] Archived: $basename ($size bytes)" >> "$LOG_FILE"
        fi
        ((ARCHIVED++))
    else
        echo "  KEEP: $basename (date: $file_date, within ${DAYS}d window)"
        ((KEPT++))
    fi
done

echo ""
echo "Summary:"
echo "  Archived: $ARCHIVED files"
echo "  Kept: $KEPT files"
echo "  Skipped: $SKIPPED files"
echo "  Cutoff: $CUTOFF ($DAYS days ago)"

if $DRY_RUN; then
    echo "  Mode: DRY RUN (no files moved)"
else
    echo "[$NOW] Pruned: $ARCHIVED archived, $KEPT kept, $SKIPPED skipped" >> "$LOG_FILE"
fi

# Reindex if files were actually moved
if ! $DRY_RUN && [ $ARCHIVED -gt 0 ] && $REINDEX; then
    echo ""
    echo "Reindexing memory search..."
    rm -f ~/.openclaw/memory/main.sqlite 2>/dev/null
    openclaw memory index 2>&1 | tail -1
    echo "[$NOW] Reindexed after pruning" >> "$LOG_FILE"
fi

# Report large archive files that could be compressed
LARGE_THRESHOLD=20000
echo ""
echo "Large archive files (>${LARGE_THRESHOLD} bytes):"
for f in "$ARCHIVE_DIR"/*.md; do
    [ -f "$f" ] || continue
    size=$(wc -c < "$f" | tr -d ' ')
    if [ "$size" -gt "$LARGE_THRESHOLD" ]; then
        echo "  $(basename "$f"): ${size} bytes"
    fi
done
