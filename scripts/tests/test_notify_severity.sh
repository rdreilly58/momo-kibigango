#!/bin/bash
# Test notify_severity routing tiers without making real HTTP calls.

unset TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID NTFY_TOPIC_URL SLACK_WEBHOOK_URL NOTIFY_CHANNELS

export TELEGRAM_BOT_TOKEN="t"
export TELEGRAM_CHAT_ID="c"
export NTFY_TOPIC_URL="http://x/y"
export SLACK_WEBHOOK_URL="http://slack/x"

TRACE=$(mktemp)
export TRACE

curl() {
    local args="$*"
    if [[ "$args" == *"api.telegram.org"* ]]; then echo "telegram" >> "$TRACE"; fi
    if [[ "$args" == *"$NTFY_TOPIC_URL"* ]]; then echo "ntfy" >> "$TRACE"; fi
    if [[ "$args" == *"$SLACK_WEBHOOK_URL"* ]]; then echo "slack" >> "$TRACE"; fi
    return 0
}
export -f curl

source scripts/lib/notify.sh

run_case() {
    local label="$1"
    local cmd="$2"
    local expected="$3"
    : > "$TRACE"
    eval "$cmd"
    local actual
    actual=$(sort -u "$TRACE" | tr '\n' ' ' | sed 's/ $//')
    if [[ "$actual" == "$expected" ]]; then
        echo "  PASS  $label"
    else
        echo "  FAIL  $label"
        echo "    expected: '$expected'"
        echo "    actual  : '$actual'"
        FAILED=1
    fi
}

FAILED=0

run_case "info -> ntfy only" \
    'notify_severity info "trend signal"' \
    "ntfy"

run_case "warning -> telegram + ntfy" \
    'notify_severity warning "uh oh"' \
    "ntfy telegram"

run_case "critical -> all three" \
    'notify_severity critical "broke"' \
    "ntfy slack telegram"

run_case "page -> all three" \
    'notify_severity page "wake up"' \
    "ntfy slack telegram"

run_case "unknown tier -> fallback (telegram + ntfy)" \
    'notify_severity unknown_tier "bad"' \
    "ntfy telegram"

run_case "NOTIFY_CHANNELS=telegram scopes critical" \
    'NOTIFY_CHANNELS=telegram notify_severity critical "scoped"' \
    "telegram"

run_case "NOTIFY_CHANNELS=ntfy scopes warning" \
    'NOTIFY_CHANNELS=ntfy notify_severity warning "scoped"' \
    "ntfy"

if [[ $FAILED -eq 0 ]]; then
    echo ""
    echo "All notify_severity tests passed."
    exit 0
else
    echo ""
    echo "Some tests FAILED."
    exit 1
fi
