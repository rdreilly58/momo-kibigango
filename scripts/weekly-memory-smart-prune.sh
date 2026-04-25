#!/bin/bash
# weekly-memory-smart-prune.sh — Smart weekly memory pruning
#
# Two-phase pruning:
#   Phase 1: Remove noise lines from current daily files (cron alerts, repeated warnings)
#   Phase 2: Archive daily files older than 30 days (delegates to memory-prune.sh)
#   Phase 3: Rebuild LanceDB warm index from cleaned files
#
# Cron: 0 9 * * 3 (Wednesday 9am — avoids Monday metrics run)
# Agent: memory (if manual consolidation needed, delegate to memory agent)
# Log: ~/.openclaw/logs/memory-smart-prune.log

set -euo pipefail

WORKSPACE="${HOME}/.openclaw/workspace"
MEMORY_DIR="${TEST_MEMORY_DIR:-${WORKSPACE}/memory}"
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

# ── Phase 1.5: Deduplicate consecutive auto-summary blocks ───────────────────
# Collapses runs of identical auto-summary blocks (same commits + same
# uncommitted files list) that accumulate when the stop hook fires every 10-15
# minutes with no new activity. Replaces the run with the first block plus a
# "[N repetitions HH:MM–HH:MM]" annotation.

DEDUP_CLEANED=0
DEDUP_LINES_SAVED=0

for f in "${MEMORY_DIR}"/2026-*.md; do
    [ -f "$f" ] || continue
    before=$(wc -l < "$f")
    tmp=$(mktemp)
    if $DRY_RUN; then
        saved=$(python3 - "$f" <<'PYEOF'
import sys, re
text = open(sys.argv[1]).read()
pattern = re.compile(r'(### Auto-summary \[(\d{2}:\d{2})\][^\n]*\n(?:(?!### Auto-summary).+\n?)*)', re.MULTILINE)
blocks = list(pattern.finditer(text))
count = 0
i = 0
while i < len(blocks) - 1:
    body_i = re.sub(r'\[\d{2}:\d{2}\]', '[XX:XX]', blocks[i].group(1))
    run = [blocks[i].group(2)]
    j = i + 1
    while j < len(blocks):
        body_j = re.sub(r'\[\d{2}:\d{2}\]', '[XX:XX]', blocks[j].group(1))
        if body_i == body_j:
            run.append(blocks[j].group(2))
            j += 1
        else:
            break
    if len(run) > 1:
        count += len(run) - 1
    i = j if j > i + 1 else i + 1
print(count)
PYEOF
        )
        [ "${saved:-0}" -gt 0 ] && _log "WOULD dedup $(basename "$f"): ~${saved} duplicate blocks"
    else
        python3 - "$f" "$tmp" <<'PYEOF'
import sys, re
src, dst = sys.argv[1], sys.argv[2]
text = open(src).read()
pattern = re.compile(r'(### Auto-summary \[(\d{2}:\d{2})\][^\n]*\n(?:(?!### Auto-summary).+\n?)*)', re.MULTILINE)
blocks = list(pattern.finditer(text))
if not blocks:
    open(dst, 'w').write(text)
    sys.exit(0)

replacements = []
i = 0
while i < len(blocks):
    body_i = re.sub(r'\[\d{2}:\d{2}\]', '[XX:XX]', blocks[i].group(1))
    run = [blocks[i]]
    j = i + 1
    while j < len(blocks):
        body_j = re.sub(r'\[\d{2}:\d{2}\]', '[XX:XX]', blocks[j].group(1))
        if body_i == body_j:
            run.append(blocks[j])
            j += 1
        else:
            break
    if len(run) > 1:
        first_time = run[0].group(2)
        last_time = run[-1].group(2)
        note = f'\n> _{len(run)-1} identical repetition(s) collapsed [{first_time}–{last_time}]_\n'
        # Replace all but first with empty; append note after first
        for b in run[1:]:
            replacements.append((b.start(), b.end(), ''))
        replacements.append((run[0].end(), run[0].end(), note))
    i = j if j > i + 1 else i + 1

# Apply replacements in reverse order to preserve offsets
for start, end, rep in sorted(replacements, key=lambda x: x[0], reverse=True):
    text = text[:start] + rep + text[end:]
open(dst, 'w').write(text)
PYEOF
        after=$(wc -l < "$tmp")
        saved=$(( before - after ))
        if [ "$saved" -gt 0 ]; then
            mv "$tmp" "$f"
            _log "Deduped $(basename "$f"): collapsed ~${saved} lines of repeated auto-summaries"
            ((DEDUP_CLEANED++)) || true
            ((DEDUP_LINES_SAVED += saved)) || true
        else
            rm -f "$tmp"
        fi
    fi
done

_log "Phase 1.5 done: ${DEDUP_CLEANED} files deduped, ~${DEDUP_LINES_SAVED} lines saved"

# ── Phase 1.6: Cross-file daily note deduplication ──────────────────────────
# Removes bullet-point lines from later daily files that already appeared
# verbatim in an earlier daily file. Prevents observer/cron lines from
# accumulating across multiple days with identical content.

CROSS_DEDUP_CLEANED=0
CROSS_DEDUP_LINES_SAVED=0

declare -A SEEN_LINES

if ! $DRY_RUN; then
    # Build corpus of lines seen in earlier files (chronological order)
    for f in $(ls "${MEMORY_DIR}"/2026-*.md 2>/dev/null | sort); do
        [ -f "$f" ] || continue
        basename=$(basename "$f")
        before=$(wc -l < "$f")
        tmp=$(mktemp)
        KEPT=0
        DROPPED=0
        while IFS= read -r line; do
            # Only deduplicate non-empty bullet lines
            trimmed="${line#"${line%%[![:space:]]*}"}"
            if [[ "$trimmed" =~ ^[-*•] ]] && [ ${#trimmed} -gt 20 ]; then
                key="${trimmed}"
                if [[ -n "${SEEN_LINES[$key]+x}" ]]; then
                    ((DROPPED++)) || true
                    continue
                else
                    SEEN_LINES[$key]=1
                fi
            fi
            echo "$line" >> "$tmp"
            ((KEPT++)) || true
        done < "$f"
        if [ "$DROPPED" -gt 0 ]; then
            mv "$tmp" "$f"
            _log "Cross-deduped ${basename}: removed ${DROPPED} duplicate bullet(s)"
            ((CROSS_DEDUP_CLEANED++)) || true
            ((CROSS_DEDUP_LINES_SAVED += DROPPED)) || true
        else
            rm -f "$tmp"
        fi
    done
fi

_log "Phase 1.6 done: ${CROSS_DEDUP_CLEANED} files cleaned, ${CROSS_DEDUP_LINES_SAVED} duplicate lines removed"

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
