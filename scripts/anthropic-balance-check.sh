#!/bin/bash
# anthropic-balance-check.sh — Anthropic billing health monitor
#
# Two-pronged approach (Anthropic has no balance API):
#   1. Detect active billing failures in cron jobs → alert immediately
#   2. Check 7-day spend rate → estimate days remaining on typical $20 top-up
#
# Usage: bash anthropic-balance-check.sh
# Cron: every 4h via api-quota-monitor or standalone

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAMP_DIR="$HOME/.openclaw/state/billing"
TELEGRAM_CHAT_ID="8755120444"
ALERT_COOLDOWN=14400  # 4h between repeat alerts
SPEND_WARN_DAYS=2     # warn if < 2 days of credit remaining at current burn rate

mkdir -p "$STAMP_DIR"

# --- Utility Functions ---

log() { echo "[$(date '+%H:%M:%S')] $*"; }

fetch_telegram_token() {
  local BOT_TOKEN
  BOT_TOKEN=$(python3 -c "
import json
try:
    c = json.load(open('$HOME/.openclaw/config.json'))
    print(c.get('telegram', {}).get('botToken', ''))
except FileNotFoundError:
    print('')
" 2>/dev/null || true)
  echo "$BOT_TOKEN"
}

send_telegram() {
  local msg="$1"
  local BOT_TOKEN=$(fetch_telegram_token) # Corrected call
  [[ -z "$BOT_TOKEN" ]] && { log "Telegram token missing. Skipping send."; return; }
  curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d "chat_id=$TELEGRAM_CHAT_ID" \
    -d "text=$msg" > /dev/null 2>&1 || true
}

alert_with_cooldown() {
  local level="$1" msg="$2"
  local STAMP="$STAMP_DIR/balance-${level}.stamp"
  local NOW AGE LAST=0
  NOW=$(date +%s)
  [[ -f "$STAMP" ]] && LAST=$(cat "$STAMP" 2>/dev/null || echo 0)
  AGE=$(( NOW - LAST ))
  if [[ $AGE -gt $ALERT_COOLDOWN ]]; then
    log "ALERT [$level] sending..."
    send_telegram "$msg"
    echo "$NOW" > "$STAMP"
  else
    log "DEDUP [$level] — alerted ${AGE}s ago"
  fi
}

send_summary_alert() {
  local findings=()

  if [[ -n "$BILLING_ERRORS" ]]; then
    COUNT=$(echo "$BILLING_ERRORS" | wc -l | tr -d ' ')
    NAMES=$(echo "$BILLING_ERRORS" | tr '\n' ', ' | sed 's/, $//')
    findings+=("cron-billing: $COUNT cron(s) with billing errors: $NAMES")
  fi

  if [[ -n "$SPEND_7D" ]]; then
    DAILY_RATE=$(python3 -c "print(f'{float(\"$SPEND_7D\")/7:.2f}')")
    DAYS_PER_TOPUP=$(python3 -c "
rate = float('$DAILY_RATE')
topup = 20.0
print(f'{topup/rate:.1f}' if rate > 0 else '999')
" 2>/dev/null || echo "?")

    findings+=("spend-rate: \$$SPEND_7D (Daily rate: \$$DAILY_RATE/day, ~${DAYS_PER_TOPUP} days per \$20 top-up)")
  fi

  if [[ "$CLAUDE_DAILY_COST" != "unknown" ]]; then
    OVER_THRESHOLD=$(python3 -c "import sys; sys.exit(0 if float('$CLAUDE_DAILY_COST') >= $CLAUDE_DAILY_WARN_THRESHOLD else 1)" 2>/dev/null && echo "yes" || echo "no")
    findings+=("claude-cli-spend: \$$CLAUDE_DAILY_COST notional (threshold: \$${CLAUDE_DAILY_WARN_THRESHOLD})"$(if [[ "$OVER_THRESHOLD" == "yes" ]]; then echo ", HIGH"; fi))
  fi

  if [[ ${#findings[@]} -eq 0 ]]; then
    send_telegram "✅ All clear!"
  else
    local summary="Summary of Billing Health:\n"
    for alert in "${findings[@]}"; do
      summary+="$alert\n"
    done
    send_telegram "$summary"
  fi
}


# ── Check 1: Active billing failures in crons ───────────────────────────────────
log "🔍 Checking cron billing errors..."
BILLING_ERRORS=$(openclaw cron list --json 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    jobs = data.get('jobs', data) if isinstance(data, dict) else data
    bad = [j.get('name','?') for j in jobs
           if j.get('state',{}).get('lastErrorReason') == 'billing'
           or 'billing' in str(j.get('state',{}).get('lastError',''))]
    print('\n'.join(bad))
except: pass
" 2>/dev/null || true)

# --- Check 2: Spend rate → days remaining estimate ───────────────────────
log "📊 Checking 7-day spend rate..."
ADMIN_KEY=$(security find-generic-password -s "AnthropicAdminKey" -w 2>/dev/null || true)

if [[ -z "$ADMIN_KEY" ]]; then
  log "⚠️  AnthropicAdminKey not in keychain — skipping spend rate check"
  : # Skip check if key is missing
else
  TODAY=$(date +%Y-%m-%d)
  WEEK_AGO=$(date -v-7d +%Y-%m-%d 2>/dev/null || date -d "7 days ago" +%Y-%m-%d)

  # Get raw usage data JSON to capture potential total cost
  USAGE_JSON=$(curl -s \
    "https://api.anthropic.com/v1/organizations/usage_report/messages?starting_at=${WEEK_AGO}&ending_at=${TODAY}&group_by[]=model" \
    -H "x-api-key: $ADMIN_KEY" \
    -H "anthropic-version: 2023-06-01" 2>/dev/null)
  
  # Simplified cost extraction: try to find the total cost displayed in the response structure.
  # This parsing is inherently brittle based on external API structure.
  SPEND_7D=$(echo "$USAGE_JSON" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    # Attempt to find a summary total cost structure
    for item in data.get('data', []):
        if 'total' in item:
            print(item['total'])
            sys.exit(0)
    print('unknown')
except Exception as e:
    print('unknown')
" <<< "$USAGE_JSON" 2>/dev/null)

  if [[ "$SPEND_7D" =~ [\$.]?[0-9]+\.[0-9]+ ]]; then
    # If we successfully extracted a numeric cost (e.g., $123.45)
    log "💸 7-day spend captured: \$$SPEND_7D"
    
    # Calculate Daily Rate
    DAILY_RATE=$(python3 -c "
total_spend_str=\$(echo \"$SPEND_7D\" | sed 's/[[^0-9.]//g')
if [ -z \"\$total_spend_str\" ]; then echo \"0.00\"; else echo \"\$(echo \"\$total_spend_str\" | awk '{print \$1 / 7.0}')\"; fi
")
    
    # Calculate Days per Topup
    DAYS_PER_TOPUP=$(python3 -c "
rate = ${DAILY_RATE}
topup = 20.0
print(f'{topup/rate:.1f}' if rate > 0 else '999')
")
    
    log "📅 At current rate: ~${DAYS_PER_TOPUP} days per \$20 top-up"
  else
    log "⚠️  Could not determine spend rate from API response."
  fi
fi


# ── Check 3: Claude Code CLI daily notional spend (ccusage) ──────────
log "📊 Checking Claude Code CLI daily spend..."
CLAUDE_DAILY_COST=$(npx ccusage --json 2>/dev/null | python3 -c "
import json, sys, datetime
try:
    data = json.load(sys.stdin)
    today = datetime.date.today().isoformat()
    rows = data.get('daily', data) if isinstance(data, dict) else data
    for row in rows:
        if str(row.get('date','')).startswith(today):
            cost = row.get('cost', 0)
            print(f'{cost:.2f}')
            sys.exit(0)
    print('0.00')
except Exception as e:
    print('unknown')
" 2>/dev/null || echo "unknown")

CLAUDE_DAILY_WARN_THRESHOLD=30  # alert if notional spend > $30/day

# --- Heartbeat ---
bash "$SCRIPT_DIR/cron-heartbeat.sh" anthropic-balance-check 0
log "✅ Done"

# --- Final Summary ---
send_summary_alert