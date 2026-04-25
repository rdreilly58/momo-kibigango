#!/bin/bash
# submodule-drift-check.sh — Detect submodule drift in the workspace.
#
# Three drift modes are flagged:
#
#   1. orphan-index     — gitlink (mode 160000) exists in the index but
#                         the path has no .gitmodules entry. `git submodule
#                         update` can't help; cloning is manual.
#   2. orphan-gitmodule — .gitmodules entry exists but no gitlink in the
#                         index. Stale config; should be removed.
#   3. sha-drift        — Working-tree submodule HEAD doesn't match the
#                         SHA recorded in the parent's index. Either
#                         someone forgot to commit the bump, or the parent
#                         repo moved past the submodule.
#
# Output: a summary table to stdout plus a JSON sidecar at
# ~/.openclaw/state/submodule-drift.json (consumed by Grafana / cron alerts).
#
# Exit codes:
#   0 = no drift
#   1 = drift detected (caller can fan out to notify_severity)
#
# Usage:
#   bash submodule-drift-check.sh [--quiet] [--alert]
#     --quiet   suppress stdout table
#     --alert   send notify_severity warning when drift detected

set -uo pipefail

set -a; source "$HOME/.openclaw/.env" 2>/dev/null || true; set +a
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/notify.sh
source "$SCRIPT_DIR/lib/notify.sh"

WORKSPACE="$HOME/.openclaw/workspace"
STATE_DIR="$HOME/.openclaw/state"
LOG_FILE="$HOME/.openclaw/logs/submodule-drift.log"
HB_DIR="$HOME/.openclaw/logs/cron-heartbeats"
STATE_FILE="$STATE_DIR/submodule-drift.json"

mkdir -p "$STATE_DIR" "$HB_DIR" "$(dirname "$LOG_FILE")"

QUIET=0
ALERT=0
while [[ $# -gt 0 ]]; do
  case $1 in
    --quiet) QUIET=1 ;;
    --alert) ALERT=1 ;;
  esac
  shift
done

_log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }
_say() { [ $QUIET -eq 0 ] && echo "$*" || true; }

cd "$WORKSPACE"

# ── Gather: paths in the index that are gitlinks (mode 160000) ──────────────
INDEX_PATHS=$(git ls-files --stage 2>/dev/null | awk '$1 == "160000" { print $4 }')

# ── Gather: paths declared in .gitmodules ───────────────────────────────────
GITMODULES_PATHS=""
if [ -f .gitmodules ]; then
  GITMODULES_PATHS=$(git config --file .gitmodules --get-regexp 'submodule\..*\.path' 2>/dev/null \
    | awk '{ print $2 }')
fi

# macOS bash 3.2 has no associative arrays, so we use sorted newline-delimited
# lists + `grep -Fx` for set membership. Cheap enough at our scale (<50 paths).

INDEX_LIST=$(printf '%s\n' "$INDEX_PATHS" | sort -u | sed '/^$/d')
GITMOD_LIST=$(printf '%s\n' "$GITMODULES_PATHS" | sort -u | sed '/^$/d')
TOTAL_GITLINKS=$(printf '%s' "$INDEX_LIST" | grep -c . 2>/dev/null || echo 0)

contains() {
  # contains "needle" "haystack-newline-delimited"
  printf '%s\n' "$2" | grep -Fxq -- "$1"
}

# ── Pass 1: orphan-index — in index but not in .gitmodules ──────────────────
orphan_index=()
while IFS= read -r path; do
  [ -z "$path" ] && continue
  if ! contains "$path" "$GITMOD_LIST"; then
    orphan_index+=("$path")
  fi
done <<< "$INDEX_LIST"

# ── Pass 2: orphan-gitmodule — in .gitmodules but not in index ──────────────
orphan_gitmodule=()
while IFS= read -r path; do
  [ -z "$path" ] && continue
  if ! contains "$path" "$INDEX_LIST"; then
    orphan_gitmodule+=("$path")
  fi
done <<< "$GITMOD_LIST"

# ── Pass 3: sha-drift — recorded SHA != working tree HEAD ───────────────────
sha_drift=()
while IFS= read -r path; do
  [ -z "$path" ] && continue
  recorded=$(git ls-files --stage -- "$path" 2>/dev/null | awk '$1 == "160000" { print $2 }')
  [ -z "$recorded" ] && continue
  # Working-tree HEAD: only checkable when path has its own git dir
  if [ -d "$path/.git" ] || [ -f "$path/.git" ]; then
    actual=$(git -C "$path" rev-parse HEAD 2>/dev/null || echo "")
    if [ -n "$actual" ] && [ "$actual" != "$recorded" ]; then
      sha_drift+=("$path|$recorded|$actual")
    fi
  fi
done <<< "$INDEX_LIST"

# ── Render summary ──────────────────────────────────────────────────────────
total=$(( ${#orphan_index[@]} + ${#orphan_gitmodule[@]} + ${#sha_drift[@]} ))

if [ $total -eq 0 ]; then
  _say "✓ No submodule drift. ${TOTAL_GITLINKS} gitlinks, all aligned with .gitmodules."
  _log "OK — no drift across ${TOTAL_GITLINKS} gitlinks"
else
  _say "⚠️  Submodule drift detected (${total} issues across ${TOTAL_GITLINKS} gitlinks)"
  if [ ${#orphan_index[@]} -gt 0 ]; then
    _say ""
    _say "  orphan-index (gitlink without .gitmodules entry):"
    for p in "${orphan_index[@]}"; do _say "    • $p"; done
  fi
  if [ ${#orphan_gitmodule[@]} -gt 0 ]; then
    _say ""
    _say "  orphan-gitmodule (.gitmodules entry without gitlink):"
    for p in "${orphan_gitmodule[@]}"; do _say "    • $p"; done
  fi
  if [ ${#sha_drift[@]} -gt 0 ]; then
    _say ""
    _say "  sha-drift (working tree != recorded SHA):"
    for entry in "${sha_drift[@]}"; do
      IFS='|' read -r path recorded actual <<< "$entry"
      _say "    • $path"
      _say "        recorded:    $recorded"
      _say "        working HEAD: $actual"
    done
  fi
  _log "DRIFT total=$total orphan_index=${#orphan_index[@]} orphan_gitmodule=${#orphan_gitmodule[@]} sha_drift=${#sha_drift[@]}"
fi

# ── Write JSON sidecar (always, for Grafana scraping) ───────────────────────
{
  printf '{\n'
  printf '  "checked_at": "%sZ",\n' "$(date -u '+%Y-%m-%dT%H:%M:%S')"
  printf '  "total_gitlinks": %d,\n' "${TOTAL_GITLINKS}"
  printf '  "drift_count": %d,\n' "$total"
  printf '  "orphan_index": ['
  first=1
  for p in "${orphan_index[@]:-}"; do
    [ -z "$p" ] && continue
    [ $first -eq 1 ] && first=0 || printf ', '
    printf '"%s"' "$p"
  done
  printf '],\n'
  printf '  "orphan_gitmodule": ['
  first=1
  for p in "${orphan_gitmodule[@]:-}"; do
    [ -z "$p" ] && continue
    [ $first -eq 1 ] && first=0 || printf ', '
    printf '"%s"' "$p"
  done
  printf '],\n'
  printf '  "sha_drift": ['
  first=1
  for entry in "${sha_drift[@]:-}"; do
    [ -z "$entry" ] && continue
    IFS='|' read -r path recorded actual <<< "$entry"
    [ -z "$path" ] && continue
    [ $first -eq 1 ] && first=0 || printf ', '
    printf '{"path":"%s","recorded":"%s","actual":"%s"}' "$path" "$recorded" "$actual"
  done
  printf ']\n'
  printf '}\n'
} > "$STATE_FILE"

# ── Heartbeat for cron-dead-man ─────────────────────────────────────────────
python3 -c "
import json, time, datetime as dt
json.dump({
    'last_run': dt.datetime.utcnow().isoformat() + 'Z',
    'last_run_ts': int(time.time()),
    'exit_code': 0,
    'drift_count': $total,
}, open('$HB_DIR/submodule-drift-check.json', 'w'))
" 2>/dev/null || true

# ── Optional alert ──────────────────────────────────────────────────────────
if [ $total -gt 0 ] && [ $ALERT -eq 1 ]; then
  msg="Submodule drift: ${total} issue(s) (${#orphan_index[@]} orphan-index, ${#orphan_gitmodule[@]} orphan-gitmodule, ${#sha_drift[@]} sha-drift). See $STATE_FILE."
  notify_severity warning "$msg" "OpenClaw submodule drift"
fi

[ $total -gt 0 ] && exit 1
exit 0
