#!/bin/bash
# weekly-memory-smart-prune.sh — Smart weekly memory pruning
#
# Two-phase pruning:
#   Phase 1: Remove noise lines from current daily files (cron alerts, repeated warnings)
#   Phase 2: Archive daily files older than 30 days (delegates to memory-prune.sh)
#   Phase 3: Rebuild LanceDB warm index from cleaned files
#
# Cron: 0 9 * * 3 (Wednesday 9am — avoids Monday metrics run)
# Log: ~/.openclaw/logs/memory-smart-prune.log

set -euo pipefail

WORKSPACE="${HOME}/.openclaw/workspace"
MEMORY_DIR="${WORKSPACE}/memory"
LOG_DIR="${HOME}/.openclaw/logs"
LOG_FILE="${LOG_DIR}/memory-smart-prune.log"
PYTHON="${WORKSPACE}/venv/bin/python3"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        *) echo "Unknown: $1"; exit 1 ;;
    esac
done

mkdir -p "$LOG_DIR"
NOW=$(date '+%Y-%m-%d %H:%M:%S')

_log() { echo "[${NOW}] [smart-prune] $*" | tee -a "$LOG_FILE"; }

_log "Starting weekly smart prune (dry-run=${DRY_RUN})"

# ── Phase 1: Remove noise lines from daily memory files ──────────────────────
# Patterns that are pure operational noise — not useful for future retrieval

NOISE_PATTERNS=(
    '^\s*- \[[0-9][0-9]:[0-9][0-9]\] ⚠️ Cron missed'
    '^\s*- \[[0-9][0-9]:[0-9][0-9]\] ℹ️ Cron'
    '^\s*- \[[0-9][0-9]:[0-9][0-9]\] ✅ Cron'
    '^\s*- \[[0-9][0-9]:[0-9][0-9]\] 🟢 Cron'
    'still working\|still waiting\|⏳ Still'
    'Auto-flushed before daily reset'
)

NOISE_REGEX=$(IFS='|'; echo "${NOISE_PATTERNS[*]}")

CLEANED=0
LINES_REMOVED=0

for f in "${MEMORY_DIR}"/2026-*.md; do
    [ -f "$f" ] || continue
    basename=$(basename "$f")

    before=$(wc -l < "$f")
    if $DRY_RUN; then
        removed=$(grep -cE "$NOISE_REGEX" "$f" 2>/dev/null || echo 0)
        if [ "$removed" -gt 0 ]; then
            _log "WOULD clean ${basename}: ${removed} noise lines"
            ((CLEANED++)) || true
            ((LINES_REMOVED += removed)) || true
        fi
    else
        # Write cleaned version atomically via temp file
        tmp=$(mktemp)
        grep -vE "$NOISE_REGEX" "$f" > "$tmp" 2>/dev/null || cp "$f" "$tmp"
        after=$(wc -l < "$tmp")
        removed=$(( before - after ))
        if [ "$removed" -gt 0 ]; then
            mv "$tmp" "$f"
            _log "Cleaned ${basename}: removed ${removed} noise lines"
            ((CLEANED++)) || true
            ((LINES_REMOVED += removed)) || true
        else
            rm -f "$tmp"
        fi
    fi
done

_log "Phase 1 done: ${CLEANED} files cleaned, ${LINES_REMOVED} lines removed"

# ── Phase 2: Archive daily files older than 30 days ──────────────────────────
_log "Phase 2: Archiving files older than 30 days..."

PRUNE_ARGS="--days 30 --no-reindex"
$DRY_RUN && PRUNE_ARGS="${PRUNE_ARGS} --dry-run"

bash "${WORKSPACE}/scripts/memory-prune.sh" $PRUNE_ARGS 2>&1 | \
    grep -E "ARCHIVED|KEEP|Summary" | \
    while IFS= read -r line; do _log "$line"; done

# ── Phase 3: Rebuild LanceDB warm index ───────────────────────────────────────
if ! $DRY_RUN; then
    _log "Phase 3: Rebuilding LanceDB warm index..."
    REBUILD_RESULT=$(
        "$PYTHON" - <<'PYEOF' 2>&1
import sys, json
sys.path.insert(0, '/Users/rreilly/.openclaw/workspace/scripts')
from memory_tier_manager import TierManager
mgr = TierManager()
n = mgr.rebuild_warm_index()
print(json.dumps({"synced": n, "status": "ok"}))
PYEOF
    )
    _log "Rebuild result: ${REBUILD_RESULT}"
fi

_log "Smart prune complete"
