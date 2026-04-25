#!/bin/bash
# scripts/notify.sh — Send a one-off message to one or more OpenClaw channels
#
# Usage:
#   notify.sh "Hello world"                                 # all configured channels
#   notify.sh --channel ntfy "Disk at 90%"                  # ntfy only
#   notify.sh --channel telegram,slack "Backup done"        # subset
#   notify.sh --title "Cost alert" --priority high \
#             --tags warning,money "Daily spend > $5"       # ntfy-specific extras
#
# Channels: telegram | ntfy | slack | all (default)
# Priorities (ntfy): min | low | default | high | urgent
# Tags (ntfy): comma-separated, see https://docs.ntfy.sh/emojis/
#
# Reads credentials from ~/.openclaw/.env. Silently no-ops on any channel
# whose credentials are missing.

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${HOME}/.openclaw/.env"

# Load env if present
if [[ -f "$ENV_FILE" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
fi

# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/notify.sh"

usage() {
    sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'
    exit "${1:-0}"
}

CHANNEL="all"
TITLE="OpenClaw"
PRIORITY="default"
TAGS=""
MESSAGE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --channel)  CHANNEL="$2";  shift 2 ;;
        --title)    TITLE="$2";    shift 2 ;;
        --priority) PRIORITY="$2"; shift 2 ;;
        --tags)     TAGS="$2";     shift 2 ;;
        -h|--help)  usage 0 ;;
        --)         shift; MESSAGE="$*"; break ;;
        -*)         echo "unknown flag: $1" >&2; usage 1 ;;
        *)          MESSAGE="$*"; break ;;
    esac
done

if [[ -z "$MESSAGE" ]]; then
    echo "error: message is required" >&2
    usage 1
fi

NOTIFY_CHANNELS="$CHANNEL" notify_user "$MESSAGE" "$TITLE" "$PRIORITY" "$TAGS"
echo "sent (channel=${CHANNEL})"
