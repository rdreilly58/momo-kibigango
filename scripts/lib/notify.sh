#!/bin/bash
# scripts/lib/notify.sh — Centralized notification & healthcheck library
#
# Usage: source "$(dirname "$0")/lib/notify.sh"
#
# Requires env vars (set in config/briefing.env or ~/.openclaw/.env):
#   TELEGRAM_BOT_TOKEN  — Telegram bot token (optional)
#   TELEGRAM_CHAT_ID    — Telegram chat ID (optional)
#   NTFY_TOPIC_URL      — ntfy full topic URL, e.g. http://127.0.0.1:8085/<topic> (optional)
#   NTFY_USER           — ntfy basic-auth username (optional; required for self-hosted)
#   NTFY_PASS           — ntfy basic-auth password (optional; required for self-hosted)
#   SLACK_WEBHOOK_URL   — Slack incoming webhook URL (optional)
#   HEALTHCHECK_URL     — healthchecks.io ping URL (optional)
#
# All functions are no-ops if the relevant env vars are unset.

# ── Telegram ────────────────────────────────────────────────────────────────

notify_telegram() {
    local message="$1"
    local parse_mode="${2:-}"   # "", "HTML", or "MarkdownV2"
    local token="${TELEGRAM_BOT_TOKEN:-}"
    local chat="${TELEGRAM_CHAT_ID:-}"

    [[ -z "$token" || -z "$chat" ]] && return 0

    local body
    if command -v jq &>/dev/null; then
        body=$(jq -n \
            --arg text "$message" \
            --arg chat_id "$chat" \
            --arg parse_mode "$parse_mode" \
            'if $parse_mode == "" then
                {chat_id: $chat_id, text: $text}
             else
                {chat_id: $chat_id, text: $text, parse_mode: $parse_mode}
             end')
    else
        local escaped="${message//\"/\\\"}"
        if [[ -n "$parse_mode" ]]; then
            body="{\"chat_id\":\"${chat}\",\"text\":\"${escaped}\",\"parse_mode\":\"${parse_mode}\"}"
        else
            body="{\"chat_id\":\"${chat}\",\"text\":\"${escaped}\"}"
        fi
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

# ── ntfy ────────────────────────────────────────────────────────────────────
# Supports both public ntfy.sh (no auth) and self-hosted ntfy with basic auth.
# Set NTFY_USER + NTFY_PASS in ~/.openclaw/.env to enable auth.

notify_ntfy() {
    local message="$1"
    local title="${2:-OpenClaw}"
    local priority="${3:-default}"   # min, low, default, high, urgent
    local tags="${4:-}"              # comma-separated, e.g. "warning,robot"
    local url="${NTFY_TOPIC_URL:-}"

    [[ -z "$url" ]] && return 0

    local -a headers=(-H "Title: ${title}" -H "Priority: ${priority}")
    [[ -n "$tags" ]] && headers+=(-H "Tags: ${tags}")

    local -a auth_args=()
    if [[ -n "${NTFY_USER:-}" && -n "${NTFY_PASS:-}" ]]; then
        auth_args=(-u "${NTFY_USER}:${NTFY_PASS}")
    fi

    # ${auth_args[@]+"${auth_args[@]}"} is safe under `set -u` when empty.
    curl -fsS -m 30 --retry 3 \
        ${auth_args[@]+"${auth_args[@]}"} \
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

# ── Severity-tiered routing ─────────────────────────────────────────────────
#
# notify_severity <tier> "message" [title]
#
# Mirrors the Grafana notification policy in
# config/grafana/provisioning/alerting/openclaw-notification-policy.yaml so
# script-emitted alerts and Grafana-emitted alerts behave consistently.
#
# Tiers:
#   info     — ntfy only, low priority. No interrupt. For trend signals.
#   warning  — telegram + ntfy, default priority. Day-time noticeable.
#   critical — telegram + ntfy (high) + slack. Hour-scale response.
#   page     — telegram + ntfy (urgent) + slack. Wakes you up. rotating_light.
#
# Override per-call with NOTIFY_CHANNELS to scope (e.g. NOTIFY_CHANNELS=ntfy).

notify_severity() {
    local tier="$1"
    local message="$2"
    local title="${3:-OpenClaw}"

    case "$tier" in
        info)
            NOTIFY_CHANNELS="${NOTIFY_CHANNELS:-ntfy}" \
                notify_user "$message" "$title" "low" ""
            ;;
        warning|warn)
            NOTIFY_CHANNELS="${NOTIFY_CHANNELS:-telegram,ntfy}" \
                notify_user "⚠️  $message" "$title" "default" "warning"
            ;;
        critical|crit)
            NOTIFY_CHANNELS="${NOTIFY_CHANNELS:-all}" \
                notify_user "🚨 $message" "$title" "high" "rotating_light"
            ;;
        page)
            NOTIFY_CHANNELS="${NOTIFY_CHANNELS:-all}" \
                notify_user "📟 PAGE: $message" "$title" "urgent" "rotating_light,sos"
            ;;
        *)
            echo "notify_severity: unknown tier '$tier' — treating as warning" >&2
            NOTIFY_CHANNELS="${NOTIFY_CHANNELS:-telegram,ntfy}" \
                notify_user "$message" "$title" "default" ""
            ;;
    esac
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
