#!/bin/bash
# generate-status.sh — Unified STATUS.md generator
#
# Aggregates health data from heartbeats, git, disk, gateway, crons,
# and recent memory/observations into a single STATUS.md at workspace root.
#
# Run: manually, by observer-agent.sh, or by the "Generate STATUS.md" cron (every 30 min).
#
# TODO (Option C): Integrate with Grafana/Netdata for time-series dashboarding.
#   When implemented, this script or a sidecar should push metrics to a Prometheus
#   pushgateway so Grafana can render historical trends for gateway uptime, disk,
#   cron health, and memory growth over time.

set -euo pipefail

WORKSPACE="$HOME/.openclaw/workspace"
HB_DIR="$HOME/.openclaw/logs/cron-heartbeats"
STATUS_FILE="$WORKSPACE/STATUS.md"
NOW=$(date '+%Y-%m-%d %H:%M %Z')
NOW_EPOCH=$(date +%s)

# ── Helpers ──────────────────────────────────────────────────────────────────

icon_for_exit() {
  [ "${1:-0}" -eq 0 ] && echo "✅" || echo "❌"
}

age_label() {
  local ts="$1"
  local age=$(( NOW_EPOCH - ts ))
  if   [ $age -lt 120 ];   then echo "just now"
  elif [ $age -lt 3600 ];  then echo "$(( age / 60 ))m ago"
  elif [ $age -lt 86400 ]; then echo "$(( age / 3600 ))h ago"
  else                          echo "$(( age / 86400 ))d ago"
  fi
}

# ── Section: Cron Heartbeats ─────────────────────────────────────────────────

cron_section() {
  echo "## Cron Heartbeats"
  echo ""
  if [ ! -d "$HB_DIR" ] || [ -z "$(ls -A "$HB_DIR" 2>/dev/null)" ]; then
    echo "_No heartbeat files found._"
    echo ""
    return
  fi

  echo "| Job | Last Run | Status |"
  echo "|-----|----------|--------|"

  for f in "$HB_DIR"/*.json; do
    local name exit_code last_run_ts icon age
    name=$(python3 -c "import json,sys; d=json.load(open('$f')); print(d.get('name','?'))")
    exit_code=$(python3 -c "import json,sys; d=json.load(open('$f')); print(d.get('exit_code',1))")
    last_run_ts=$(python3 -c "import json,sys; d=json.load(open('$f')); print(d.get('last_run_ts',0))")
    icon=$(icon_for_exit "$exit_code")
    age=$(age_label "$last_run_ts")
    echo "| $name | $age | $icon |"
  done
  echo ""
}

# ── Section: Gateway ─────────────────────────────────────────────────────────

gateway_section() {
  echo "## Gateway"
  echo ""
  local port
  port=$(openclaw gateway status 2>/dev/null | grep -oE 'port [0-9]+' | grep -oE '[0-9]+' | head -1 || echo "18789")

  if curl -s --max-time 3 "http://localhost:${port}/health" >/dev/null 2>&1; then
    echo "✅ Running on port ${port}"
  else
    echo "❌ Not responding on port ${port}"
  fi
  echo ""
}

# ── Section: Disk ─────────────────────────────────────────────────────────────

disk_section() {
  echo "## Disk"
  echo ""
  local usage
  usage=$(df "$WORKSPACE" | awk 'NR==2 {print $5}' | sed 's/%//')
  if   [ "$usage" -gt 90 ]; then echo "❌ ${usage}% used — critical"
  elif [ "$usage" -gt 75 ]; then echo "⚠️  ${usage}% used — warning"
  else                            echo "✅ ${usage}% used"
  fi
  echo ""
}

# ── Section: Git ─────────────────────────────────────────────────────────────

git_section() {
  echo "## Git"
  echo ""
  local branch dirty_count last_commit
  branch=$(git -C "$WORKSPACE" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
  dirty_count=$(git -C "$WORKSPACE" status --short 2>/dev/null | wc -l | tr -d ' ')
  last_commit=$(git -C "$WORKSPACE" log -1 --format="%h %s" 2>/dev/null || echo "n/a")
  echo "- Branch: \`${branch}\`"
  echo "- Uncommitted changes: ${dirty_count} file(s)"
  echo "- Last commit: \`${last_commit}\`"
  echo ""
}

# ── Section: OpenClaw Crons ───────────────────────────────────────────────────

crons_section() {
  echo "## Scheduled Crons"
  echo ""
  local cron_output
  cron_output=$(openclaw cron list 2>/dev/null || echo "")
  if [ -z "$cron_output" ]; then
    echo "_No crons found or openclaw unavailable._"
    echo ""
    return
  fi

  echo "| Name | Next | Last | Status |"
  echo "|------|------|------|--------|"

  # Use python to parse fixed-width columns from the header row
  # (avoid heredoc/pipe stdin conflict by using -c with a variable)
  local pycode='
import sys, re
lines = sys.stdin.read().splitlines()
if len(lines) < 2:
    sys.exit(0)
header = lines[0]
# Find ALL column start positions from the header line
all_cols = [(m.group(), m.start()) for m in re.finditer(r"\S+", header)]
col_starts = {name: start for name, start in all_cols}
col_order = sorted(all_cols, key=lambda x: x[1])

def get_col(line, col_name):
    if col_name not in col_starts:
        return "?"
    start = col_starts[col_name]
    # Find this col in the ordered list, use next col start as end
    for i, (n, s) in enumerate(col_order):
        if n == col_name:
            end = col_order[i+1][1] if i+1 < len(col_order) else len(line)
            return line[start:end].strip()
    return "?"

for line in lines[1:]:
    if not line.strip():
        continue
    cron_name = get_col(line, "Name")
    next_run  = get_col(line, "Next")
    last_run  = get_col(line, "Last")
    status    = get_col(line, "Status")
    icon      = "\u2705" if status == "ok" else "\u26a0\ufe0f"
    print(f"| {cron_name} | {next_run} | {last_run} | {icon} {status} |")
'
  echo "$cron_output" | python3 -c "$pycode"
  echo ""
}

# ── Section: Recent Observations ─────────────────────────────────────────────

observations_section() {
  echo "## Recent Observations"
  echo ""
  local obs_file="$WORKSPACE/memory/observations.md"
  if [ -f "$obs_file" ]; then
    tail -5 "$obs_file"
  else
    echo "_No observations file found._"
  fi
  echo ""
}

# ── Section: Today's Tasks ────────────────────────────────────────────────────

tasks_section() {
  echo "## Today's Tasks (Things 3)"
  echo ""
  local raw
  raw=$(things today 2>/dev/null || echo "")
  if [ -z "$raw" ]; then
    echo "_No incomplete tasks today._"
    echo ""
    return
  fi

  # Fixed-width parse: TITLE column from header
  local pycode='
import sys
lines = sys.stdin.read().splitlines()
if len(lines) < 2:
    print("_No incomplete tasks today._")
    sys.exit(0)
header = lines[0]
title_start = header.find("TITLE")
status_start = header.find("STATUS")
if title_start < 0 or status_start < 0:
    print("_Could not parse tasks output._")
    sys.exit(0)
tasks = []
for line in lines[1:]:
    if not line.strip():
        continue
    title  = line[title_start:status_start].strip()
    status = line[status_start:].split()[0] if len(line) > status_start else ""
    if status == "incomplete" and title:
        tasks.append(f"- [ ] {title}")
if tasks:
    print("\n".join(tasks[:10]))
else:
    print("_No incomplete tasks today._")
'
  echo "$raw" | python3 -c "$pycode"
  echo ""
}

# ── Section: Memory & Context Health ─────────────────────────────────────────

memory_section() {
  echo "## Memory & Context"
  echo ""

  # LanceDB warm tier record count
  local warm_count
  warm_count=$("$WORKSPACE/venv/bin/python3" -c "
import sys; sys.path.insert(0, '$WORKSPACE/scripts')
try:
    from memory_tier_manager import TierManager
    mgr = TierManager()
    s = mgr.stats()
    print(s.get('tiers', {}).get('warm', {}).get('records', '?'))
except Exception as e:
    print('?')
" 2>/dev/null || echo "?")

  local flat_count
  flat_count=$(ls "$WORKSPACE/memory/"*.md 2>/dev/null | wc -l | tr -d ' ')

  echo "| Store | Count |"
  echo "|-------|-------|"
  echo "| LanceDB warm | ${warm_count} records |"
  echo "| Flat memory files | ${flat_count} files |"
  echo ""

  # Recent session depth (last 3 entries from metrics file)
  local metrics_file="$HOME/.openclaw/logs/session-depth-metrics.jsonl"
  if [ -f "$metrics_file" ]; then
    echo "**Recent session depths:**"
    echo ""
    tail -3 "$metrics_file" | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        d = json.loads(line)
        chars = d.get('transcript_chars', 0)
        turns = d.get('turn_estimate', 0)
        date  = d.get('date', '')
        pct   = min(int(chars / 200000 * 100), 100)
        bar   = '█' * (pct // 10) + '░' * (10 - pct // 10)
        print(f'- {date}: {chars:,} chars (~{turns} turns) [{bar}] {pct}%')
    except Exception:
        pass
" 2>/dev/null || echo "_No session metrics yet._"
    echo ""
  fi
}

# ── Assemble STATUS.md ────────────────────────────────────────────────────────

{
  echo "# STATUS.md"
  echo ""
  echo "> Auto-generated by \`scripts/generate-status.sh\` — last updated **${NOW}**"
  echo "> Refresh manually: \`bash scripts/generate-status.sh\`"
  echo ""
  echo "---"
  echo ""

  gateway_section
  disk_section
  git_section
  cron_section
  crons_section
  observations_section
  tasks_section
  memory_section

  echo "---"
  echo ""
  echo "<!-- TODO(Option C): Push metrics to Prometheus pushgateway for Grafana time-series dashboards."
  echo "     See: https://grafana.com/docs/grafana/latest/  |  Netdata alternative: https://netdata.cloud"
  echo "     Candidate metrics: gateway_up, disk_pct, cron_last_run_age_s, git_dirty_count, memory_file_count -->"
} > "$STATUS_FILE"

echo "[generate-status] STATUS.md written at ${NOW}"
