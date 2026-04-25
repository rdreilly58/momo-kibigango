#!/bin/bash
# spending-cap-check.sh — Per-agent spending cap monitor.
#
# Reads ~/.openclaw/logs/subagent-costs/*.log, sums cost per agent
# (mapped from model name via the same heuristic used by the metrics
# exporter), compares against caps in config/spending-caps.json, and
# fires notify_user when a cap is breached at warn (80%) or alert (100%).
#
# Designed for hourly cron. Idempotent — uses a stamp file under
# ~/.openclaw/state/ to dedupe alerts within a 6h window per (agent, tier).
#
# Usage:
#   bash spending-cap-check.sh [--dry-run] [--verbose]

set -uo pipefail

set -a; source "$HOME/.openclaw/.env" 2>/dev/null || true; set +a
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/notify.sh
source "$SCRIPT_DIR/lib/notify.sh"

WORKSPACE="$HOME/.openclaw/workspace"
COST_DIR="$HOME/.openclaw/logs/subagent-costs"
CAPS_FILE="$WORKSPACE/config/spending-caps.json"
STATE_DIR="$HOME/.openclaw/state/spending-caps"
LOG_FILE="$HOME/.openclaw/logs/spending-cap-check.log"

DRY_RUN=0
VERBOSE=0
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=1 ;;
    --verbose) VERBOSE=1 ;;
  esac
  shift
done

mkdir -p "$STATE_DIR" "$(dirname "$LOG_FILE")"

_log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
_vlog() { [ $VERBOSE -eq 1 ] && _log "$*" || true; }

if [ ! -f "$CAPS_FILE" ]; then
  _log "ERROR: caps file not found at $CAPS_FILE — exiting"
  exit 1
fi

if [ ! -d "$COST_DIR" ]; then
  _vlog "No cost log directory yet ($COST_DIR) — nothing to check"
  exit 0
fi

# ── Compute per-agent totals (daily + rolling 30d) and breach status ────────
RESULTS=$(python3 - "$COST_DIR" "$CAPS_FILE" <<'PYEOF'
import json, os, re, sys, datetime as dt
cost_dir, caps_path = sys.argv[1], sys.argv[2]
caps = json.load(open(caps_path))
warn_pct  = caps.get("warn_at_pct", 80)
alert_pct = caps.get("alert_at_pct", 100)

def model_to_agent(model: str) -> str:
    m = model.lower()
    if "haiku"  in m: return "research"
    if "sonnet" in m: return "code"
    if "opus"   in m: return "ops"
    return "unknown"

now    = dt.datetime.utcnow()
today  = now.strftime("%Y-%m-%d")
day_30 = now - dt.timedelta(days=30)

daily, rolling = {}, {}
TS_RE   = re.compile(r"^\[(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s+UTC\]")
MOD_RE  = re.compile(r"Model:\s*(\S+)")
COST_RE = re.compile(r"Est\.\s*Cost:\s*\$([0-9.]+)")

for fname in sorted(os.listdir(cost_dir)):
    if not fname.endswith(".log"): continue
    path = os.path.join(cost_dir, fname)
    try:
        text = open(path).read()
    except Exception:
        continue
    for block in text.split("─" * 36):
        ts_m, mod_m, cost_m = TS_RE.search(block), MOD_RE.search(block), COST_RE.search(block)
        if not (ts_m and mod_m and cost_m): continue
        try:
            stamp = dt.datetime.strptime(ts_m.group(1) + " " + ts_m.group(2), "%Y-%m-%d %H:%M:%S")
            cost  = float(cost_m.group(1))
        except Exception:
            continue
        agent = model_to_agent(mod_m.group(1))
        if stamp.strftime("%Y-%m-%d") == today:
            daily[agent]   = daily.get(agent,   0.0) + cost
            daily["overall"] = daily.get("overall", 0.0) + cost
        if stamp >= day_30:
            rolling[agent]   = rolling.get(agent,   0.0) + cost
            rolling["overall"] = rolling.get("overall", 0.0) + cost

def check(actual: dict, caps_for_tier: dict, tier_name: str):
    out = []
    for agent, cap in caps_for_tier.items():
        if cap <= 0: continue
        amt = round(actual.get(agent, 0.0), 4)
        pct = (amt / cap) * 100 if cap else 0
        level = "alert" if pct >= alert_pct else ("warn" if pct >= warn_pct else "ok")
        out.append({"tier": tier_name, "agent": agent, "amount": amt, "cap": cap, "pct": round(pct,1), "level": level})
    return out

results = check(daily,   caps.get("daily_usd",       {}), "daily")
results += check(rolling, caps.get("rolling_30d_usd", {}), "rolling_30d")
print(json.dumps(results))
PYEOF
)

if [ -z "$RESULTS" ]; then
  _log "ERROR: python computation produced no output"
  exit 1
fi

_log "Computed cap status for $(echo "$RESULTS" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))') (tier, agent) pairs"

# ── Alert on breaches (with 6h dedup per agent+tier+level) ──────────────────
breaches=0
echo "$RESULTS" | python3 -c '
import json, sys
for r in json.load(sys.stdin):
    print("\t".join(str(r[k]) for k in ("tier","agent","amount","cap","pct","level")))
' | while IFS=$'\t' read -r tier agent amount cap pct level; do
  case "$level" in
    ok)
      _vlog "OK    $tier/$agent — \$$amount of \$$cap ($pct%)"
      ;;
    warn|alert)
      stamp_file="$STATE_DIR/${tier}-${agent}-${level}.stamp"
      if [ -f "$stamp_file" ]; then
        age=$(python3 -c "import os,time; print(int(time.time()-os.path.getmtime('$stamp_file')))" 2>/dev/null || echo 0)
        if [ "$age" -lt 21600 ]; then
          _log "DEDUP $tier/$agent $level — alerted ${age}s ago"
          continue
        fi
      fi
      icon="⚠️"; priority="default"; tags="warning"
      if [ "$level" = "alert" ]; then
        icon="🚨"; priority="high"; tags="rotating_light,money_with_wings"
      fi
      msg="${icon} OpenClaw spending cap ${level}: ${agent} (${tier})
\$${amount} of \$${cap} cap (${pct}%)
$(date '+%Y-%m-%d %H:%M %Z')"
      _log "ALERT $tier/$agent $level — \$$amount / \$$cap ($pct%)"
      if [ $DRY_RUN -eq 0 ]; then
        notify_user "$msg" "OpenClaw spending ${level}" "$priority" "$tags"
        touch "$stamp_file"
      fi
      breaches=$((breaches + 1))
      ;;
  esac
done

# Heartbeat for cron-dead-man.sh
HB_DIR="$HOME/.openclaw/logs/cron-heartbeats"
mkdir -p "$HB_DIR"
python3 -c "
import json, time, datetime as dt
json.dump({
    'last_run': dt.datetime.utcnow().isoformat() + 'Z',
    'last_run_ts': int(time.time()),
    'exit_code': 0,
}, open('$HB_DIR/spending-cap-check.json', 'w'))
" 2>/dev/null || true

_log "Done"
exit 0
