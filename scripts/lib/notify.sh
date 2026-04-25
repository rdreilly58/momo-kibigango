#!/bin/bash
# scripts/lib/notify.sh — Centralized notification & healthcheck library
#
# Usage: source "$(dirname "$0")/lib/notify.sh"
#
# Requires env vars (set in config/briefing.env or ~/.openclaw/.env):
#   TELEGRAM_BOT_TOKEN  — Telegram bot token (optional)
#   TELEGRAM_CHAT_ID    — Telegram chat ID (optional)
#   NTFY_TOPIC_URL      — ntfy.sh full topic URL, e.g. https://ntfy.sh/<topic> (optional)
#   SLACK_WEBHOOK_URL   — Slack incoming webhook URL (optional)
#   HEALTHCHECK_URL     — healthchecks.io ping URL (optional)
#
# All functions are no-ops if the relevant env vars are unset.

# ── Telegram ────────────────────────────────────────────────────────────────

notify_telegram() {
    local message="$1"
    local token="${TELEGRAM_BOT_TOKEN:-}"
    local chat="${TELEGRAM_CHAT_ID:-}"

    [[ -z "$token" || -z "$chat" ]] && return 0

    local body
    if command -v jq &>/dev/null; then
        body=$(jq -n \
            --arg text "$message" \
            --arg chat_id "$chat" \
            '{chat_id: $chat_id, text: $text}')
    else
        # Fallback: escape double quotes only (sufficient for plain-text alerts)
        local escaped="${message//\"/\\\"}"
        body="{\"chat_id\":\"${chat}\",\"text\":\"${escaped}\"}"
    fi

    curl -fsS -m 30 --retry 3 \
        -H 'Content-Type: application/json' \
        -d "$body" \
        "https://api.telegram.org/bot${token}/sendMessage" \
        >/dev/null 2>&1 || true
}

notify_telegram_failure() {
    local script="${1:-$(basename "${BASH_SOURCE[1]:-unknown}")}"
    local line="${2:-?}"
    local cmd="${3:-}"
    local msg="❌ FAILED: ${script} line ${line}"
    [[ -n "$cmd" ]] && msg+=" — ${cmd}"
    msg+=" at $(date '+%H:%M %Z')"
    notify_telegram "$msg"
}

# ── ntfy.sh ─────────────────────────────────────────────────────────────────

notify_ntfy() {
    local message="$1"
    local title="${2:-OpenClaw}"
    local priority="${3:-default}"   # min, low, default, high, urgent
    local tags="${4:-}"              # comma-separated, e.g. "warning,robot"
    local url="${NTFY_TOPIC_URL:-}"

    [[ -z "$url" ]] && return 0

    local -a headers=(-H "Title: ${title}" -H "Priority: ${priority}")
    [[ -n "$tags" ]] && headers+=(-H "Tags: ${tags}")

    curl -fsS -m 30 --retry 3 \
        "${headers[@]}" \
        -d "$message" \
        "$url" \
        >/dev/null 2>&1 || true
}

notify_ntfy_failure() {
    local script="${1:-$(basename "${BASH_SOURCE[1]:-unknown}")}"
    local line="${2:-?}"
    local cmd="${3:-}"
    local msg="FAILED: ${script} line ${line}"
    [[ -n "$cmd" ]] && msg+=" — ${cmd}"
    msg+=" at $(date '+%H:%M %Z')"
    notify_ntfy "$msg" "OpenClaw error" "high" "rotating_light"
}

# ── Slack (incoming webhook) ────────────────────────────────────────────────

notify_slack() {
    local message="$1"
    local url="${SLACK_WEBHOOK_URL:-}"

    [[ -z "$url" ]] && return 0

    local body
    if command -v jq &>/dev/null; then
        body=$(jq -n --arg text "$message" '{text: $text}')
    else
        local escaped="${message//\"/\\\"}"
        body="{\"text\":\"${escaped}\"}"
    fi

    curl -fsS -m 30 --retry 3 \
        -H 'Content-Type: application/json' \
        -d "$body" \
        "$url" \
        >/dev/null 2>&1 || true
}

notify_slack_failure() {
    local script="${1:-$(basename "${BASH_SOURCE[1]:-unknown}")}"
    local line="${2:-?}"
    local cmd="${3:-}"
    local msg=":rotating_light: FAILED: \`${script}\` line ${line}"
    [[ -n "$cmd" ]] && msg+=" — \`${cmd}\`"
    msg+=" at $(date '+%H:%M %Z')"
    notify_slack "$msg"
}

# ── Multi-channel fan-out ───────────────────────────────────────────────────
#
# notify_user "message" [title] [priority] [tags]
#
# Broadcasts to every configured channel. Channel is "configured" when its
# env var is set and non-empty. Honors NOTIFY_CHANNELS to opt out:
#   NOTIFY_CHANNELS="telegram,ntfy"   # skip slack
#   NOTIFY_CHANNELS="all"             # default — every configured channel

notify_user() {
    local message="$1"
    local title="${2:-OpenClaw}"
    local priority="${3:-default}"
    local tags="${4:-}"
    local channels="${NOTIFY_CHANNELS:-all}"

    if [[ "$channels" == "all" || ",$channels," == *,telegram,* ]]; then
        notify_telegram "$message"
    fi
    if [[ "$channels" == "all" || ",$channels," == *,ntfy,* ]]; then
        notify_ntfy "$message" "$title" "$priority" "$tags"
    fi
    if [[ "$channels" == "all" || ",$channels," == *,slack,* ]]; then
        notify_slack "$message"
    fi
}

# ── healthchecks.io ─────────────────────────────────────────────────────────

hc_ping() {
    # hc_ping [suffix]  — suffix is "", "/start", or "/fail"
    local suffix="${1:-}"
    local url="${HEALTHCHECK_URL:-}"
    [[ -z "$url" ]] && return 0
    curl -fsS -m 10 --retry 5 -o /dev/null "${url}${suffix}" || true
}

hc_start()   { hc_ping "/start"; }
hc_success() { hc_ping ""; }
hc_fail()    { hc_ping "/fail"; }

# ── Combined ERR trap ────────────────────────────────────────────────────────
#
# Install with:
#   trap '_notify_err_handler $LINENO' ERR
#
# Requires the calling script to use: set -Eeuo pipefail

_notify_err_handler() {
    local exit_code=$?
    local line="${1:-?}"
    local script
    script="$(basename "${BASH_SOURCE[1]:-${0}}")"
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] ERROR in ${script} line ${line}: '${BASH_COMMAND}' (exit ${exit_code})"

    echo "$msg" >&2
    [[ -n "${LOG_FILE:-}" ]] && echo "$msg" >>"$LOG_FILE" 2>/dev/null || true

    hc_fail
    notify_telegram_failure "$script" "$line" "$BASH_COMMAND"
}

# ── Log rotation helper ──────────────────────────────────────────────────────

rotate_logs() {
    local dir="${1:-$HOME/.openclaw/logs}"
    local pattern="${2:-*.log}"
    local days="${3:-30}"
    find "$dir" -name "$pattern" -mtime "+${days}" -delete 2>/dev/null || true
}
