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

log() { echo "[$(date '+%H:%M:%S')] $*"; }

send_telegram() {
  local msg="$1"
  local BOT_TOKEN
  BOT_TOKEN=$(python3 -c "
import json
c = json.load(open('$HOME/.openclaw/config.json'))
print(c.get('telegram', {}).get('botToken', ''))
" 2>/dev/null || true)
  [[ -z "$BOT_TOKEN" ]] && return
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

# ── Check 1: Active billing failures in crons ─────────────────────────────────
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

if [[ -n "$BILLING_ERRORS" ]]; then
  COUNT=$(echo "$BILLING_ERRORS" | wc -l | tr -d ' ')
  NAMES=$(echo "$BILLING_ERRORS" | tr '\n' ', ' | sed 's/, $//')
  log "❌ $COUNT cron(s) with billing errors: $NAMES"
  alert_with_cooldown "cron-billing" "⚠️ ALERT: Anthropic | Status: Critical | $COUNT cron(s) failing due to billing: $NAMES | Action: Top up at console.anthropic.com/settings/billing"
else
  log "✅ No active cron billing errors"
  rm -f "$STAMP_DIR/balance-cron-billing.stamp" 2>/dev/null || true
fi

# ── Check 2: Spend rate → days remaining estimate ─────────────────────────────
log "📊 Checking 7-day spend rate..."
ADMIN_KEY=$(security find-generic-password -s "AnthropicAdminKey" -w 2>/dev/null || true)

if [[ -z "$ADMIN_KEY" ]]; then
  log "⚠️  AnthropicAdminKey not in keychain — skipping spend rate check"
  bash "$SCRIPT_DIR/cron-heartbeat.sh" anthropic-balance-check 0
  exit 0
fi

TODAY=$(date +%Y-%m-%d)
WEEK_AGO=$(date -v-7d +%Y-%m-%d 2>/dev/null || date -d "7 days ago" +%Y-%m-%d)

SPEND_7D=$(curl -s \
  "https://api.anthropic.com/v1/organizations/usage_report/messages?starting_at=${WEEK_AGO}&ending_at=${TODAY}&group_by[]=model" \
  -H "x-api-key: $ADMIN_KEY" \
  -H "anthropic-version: 2023-06-01" 2>/dev/null \
  | python3 "$SCRIPT_DIR/anthropic-spend-check.py" 2>/dev/null \
  | grep "^TOTAL_7D:" | awk '{print $2}' || echo "unknown")

if [[ "$SPEND_7D" == "unknown" || -z "$SPEND_7D" ]]; then
  # Fallback: just get total cost line
  SPEND_7D=$(curl -s \
    "https://api.anthropic.com/v1/organizations/usage_report/messages?starting_at=${WEEK_AGO}&ending_at=${TODAY}&group_by[]=model" \
    -H "x-api-key: $ADMIN_KEY" \
    -H "anthropic-version: 2023-06-01" 2>/dev/null \
    | python3 "$SCRIPT_DIR/anthropic-spend-check.py" 2>/dev/null \
    | grep -i "total\|7.day\|week" | grep -oE '\$[0-9]+\.[0-9]+' | head -1 | tr -d '$' || echo "")
fi

if [[ -n "$SPEND_7D" ]] && python3 -c "float('$SPEND_7D')" 2>/dev/null; then
  DAILY_RATE=$(python3 -c "print(f'{float(\"$SPEND_7D\")/7:.2f}')")
  log "💸 7-day spend: \$$SPEND_7D | Daily rate: \$$DAILY_RATE/day"

  # Standard top-up is $20 — estimate days remaining (conservative: assume $5 buffer)
  # We can't know exact balance, but we can warn when burn rate is high
  DAYS_PER_TOPUP=$(python3 -c "
rate = float('$DAILY_RATE')
topup = 20.0
print(f'{topup/rate:.1f}' if rate > 0 else '999')
" 2>/dev/null || echo "?")

  log "📅 At current rate: ~${DAYS_PER_TOPUP} days per \$20 top-up"

  # Alert if burning faster than $7/day (< 3 days per $20)
  BURN_WARN=$(python3 -c "import sys; sys.exit(0 if float('$DAILY_RATE') >= 7.0 else 1)" 2>/dev/null && echo "yes" || echo "no")
  if [[ "$BURN_WARN" == "yes" ]]; then
    alert_with_cooldown "burn-rate" "⚠️ Anthropic spend rate HIGH: \$$DAILY_RATE/day (7d avg). At this rate a \$20 top-up lasts ~${DAYS_PER_TOPUP} days. Consider larger top-up."
  else
    rm -f "$STAMP_DIR/balance-burn-rate.stamp" 2>/dev/null || true
  fi
else
  log "⚠️  Could not determine spend rate"
fi

# ── Heartbeat ─────────────────────────────────────────────────────────────────
bash "$SCRIPT_DIR/cron-heartbeat.sh" anthropic-balance-check 0
log "✅ Done"
