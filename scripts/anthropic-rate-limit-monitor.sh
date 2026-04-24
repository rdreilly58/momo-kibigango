#!/bin/bash
# anthropic-rate-limit-monitor.sh — Check Anthropic API rate limit headers
#
# Makes a minimal API call and logs the rate limit headers.
# Alerts via cron-heartbeat if within 20% of limits.
#
# Usage: bash scripts/anthropic-rate-limit-monitor.sh [--log-only]
# Cron: add to quota-monitoring or run hourly alongside api-quota-monitor.sh

set -euo pipefail

WORKSPACE="${HOME}/.openclaw/workspace"
LOG_FILE="${HOME}/.openclaw/logs/rate-limit-monitor.log"
METRICS_FILE="${HOME}/.openclaw/logs/rate-limit-metrics.jsonl"
ALERT_THRESHOLD=0.80  # alert when > 80% of limit consumed

LOG_ONLY=false
[[ "${1:-}" == "--log-only" ]] && LOG_ONLY=true

mkdir -p "$(dirname "$LOG_FILE")"

_log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [rate-limit] $*" | tee -a "$LOG_FILE"; }

# Load API key from Keychain (preferred) or env
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"
if [ -z "$ANTHROPIC_API_KEY" ]; then
    ANTHROPIC_API_KEY=$(security find-generic-password -s "OpenclawAnthropic" -a "openclaw" -w 2>/dev/null || true)
fi
if [ -z "$ANTHROPIC_API_KEY" ]; then
    _log "ERROR: ANTHROPIC_API_KEY not found in env or Keychain"
    exit 1
fi

# Make a minimal API call and capture response headers
RESPONSE=$(curl -s -i \
    -X POST "https://api.anthropic.com/v1/messages" \
    -H "x-api-key: ${ANTHROPIC_API_KEY}" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{"model":"claude-haiku-4-5-20251001","max_tokens":1,"messages":[{"role":"user","content":"hi"}]}' \
    2>/dev/null)

# Parse rate limit headers
extract_header() {
    echo "$RESPONSE" | grep -i "^${1}:" | head -1 | awk '{print $2}' | tr -d '\r'
}

RL_REQUESTS_LIMIT=$(extract_header "anthropic-ratelimit-requests-limit")
RL_REQUESTS_REMAINING=$(extract_header "anthropic-ratelimit-requests-remaining")
RL_REQUESTS_RESET=$(extract_header "anthropic-ratelimit-requests-reset")
RL_TOKENS_LIMIT=$(extract_header "anthropic-ratelimit-tokens-limit")
RL_TOKENS_REMAINING=$(extract_header "anthropic-ratelimit-tokens-remaining")
RL_TOKENS_RESET=$(extract_header "anthropic-ratelimit-tokens-reset")
RL_INPUT_TOKENS_LIMIT=$(extract_header "anthropic-ratelimit-input-tokens-limit")
RL_INPUT_TOKENS_REMAINING=$(extract_header "anthropic-ratelimit-input-tokens-remaining")

_log "Requests: ${RL_REQUESTS_REMAINING:-?}/${RL_REQUESTS_LIMIT:-?} (reset: ${RL_REQUESTS_RESET:-?})"
_log "Tokens:   ${RL_TOKENS_REMAINING:-?}/${RL_TOKENS_LIMIT:-?} (reset: ${RL_TOKENS_RESET:-?})"
_log "Input:    ${RL_INPUT_TOKENS_REMAINING:-?}/${RL_INPUT_TOKENS_LIMIT:-?}"

# Write JSON metrics
NOW_TS=$(date +%s)
NOW_ISO=$(date '+%Y-%m-%d %H:%M')
python3 - <<PYEOF 2>/dev/null || true
import json
entry = {
    "ts": ${NOW_TS},
    "date": "${NOW_ISO}",
    "requests_limit": "${RL_REQUESTS_LIMIT}",
    "requests_remaining": "${RL_REQUESTS_REMAINING}",
    "requests_reset": "${RL_REQUESTS_RESET}",
    "tokens_limit": "${RL_TOKENS_LIMIT}",
    "tokens_remaining": "${RL_TOKENS_REMAINING}",
    "tokens_reset": "${RL_TOKENS_RESET}",
    "input_tokens_limit": "${RL_INPUT_TOKENS_LIMIT}",
    "input_tokens_remaining": "${RL_INPUT_TOKENS_REMAINING}",
}
with open("${METRICS_FILE}", "a") as f:
    f.write(json.dumps(entry) + "\n")
# Keep last 48 entries (~2 days at hourly)
with open("${METRICS_FILE}") as f:
    lines = f.readlines()
if len(lines) > 48:
    with open("${METRICS_FILE}", "w") as f:
        f.writelines(lines[-48:])
PYEOF

# Alert if approaching limits
if [ "${LOG_ONLY}" = "true" ]; then exit 0; fi

ALERT=false
ALERT_MSG=""

check_threshold() {
    local remaining="$1" limit="$2" label="$3"
    if [ -n "$remaining" ] && [ -n "$limit" ] && [ "$limit" -gt 0 ] 2>/dev/null; then
        used=$(( limit - remaining ))
        pct_used=$(( used * 100 / limit ))
        if [ "$pct_used" -ge 80 ]; then
            ALERT=true
            ALERT_MSG="${ALERT_MSG}⚠️ ${label}: ${pct_used}% consumed (${remaining}/${limit} remaining)\n"
        fi
    fi
}

check_threshold "${RL_REQUESTS_REMAINING:-}" "${RL_REQUESTS_LIMIT:-}" "Requests"
check_threshold "${RL_TOKENS_REMAINING:-}" "${RL_TOKENS_LIMIT:-}" "Tokens"

if $ALERT; then
    _log "ALERT: Rate limits approaching threshold"
    # Fire cron heartbeat with failure to surface alert
    bash "${WORKSPACE}/scripts/cron-heartbeat.sh" "anthropic-rate-limit" "1" || true
    echo -e "⚠️ ALERT: Anthropic | Rate Limit | ${ALERT_MSG}| Action: Reduce request rate or wait for reset"
fi
