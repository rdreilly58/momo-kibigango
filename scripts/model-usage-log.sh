#!/usr/bin/env bash
# model-usage-log.sh — Log per-session model usage to dated CSV files.
#
# Usage:
#   model-usage-log.sh --session-type telegram --message "What time is it?" --model anthropic/claude-haiku-4-6
#   model-usage-log.sh --session-type cron --message "Run memory decay" --model anthropic/claude-haiku-4-6
#
# Environment:
#   MODEL_USED       override for model (alternative to --model)
#   SESSION_TYPE     override for session_type (alternative to --session-type)
#
# Output CSV format:
#   timestamp,session_type,message_preview,tier_classified,model_used,tokens_est

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
LOG_DIR="${HOME}/.openclaw/logs/model-usage"
CLASSIFIER="${HOME}/.openclaw/workspace/scripts/task-classifier-v2.py"
DATE_STR=$(date +%Y-%m-%d)
LOG_FILE="${LOG_DIR}/${DATE_STR}.csv"

# ── Defaults ──────────────────────────────────────────────────────────────────
session_type="${SESSION_TYPE:-}"
message=""
model_used="${MODEL_USED:-}"

# ── Argument parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --session-type|-s) session_type="$2"; shift 2 ;;
    --message|-m)      message="$2";      shift 2 ;;
    --model)           model_used="$2";   shift 2 ;;
    --help|-h)
      echo "Usage: model-usage-log.sh --session-type <telegram|cron|subagent> --message <text> [--model <model>]"
      exit 0
      ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

# ── Validate ──────────────────────────────────────────────────────────────────
if [[ -z "$message" ]]; then
  echo "Error: --message is required" >&2
  exit 1
fi

if [[ -z "$session_type" ]]; then
  session_type="unknown"
fi

# ── Classify ──────────────────────────────────────────────────────────────────
tier_classified="unknown"
if [[ -f "$CLASSIFIER" ]]; then
  classifier_json=$(echo "$message" | python3 "$CLASSIFIER" 2>/dev/null || echo '{"tier":"unknown"}')
  tier_classified=$(echo "$classifier_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tier','unknown'))" 2>/dev/null || echo "unknown")
fi

# ── Derive model if not passed ────────────────────────────────────────────────
if [[ -z "$model_used" ]]; then
  case "$tier_classified" in
    simple)  model_used="anthropic/claude-haiku-4-6" ;;
    complex) model_used="anthropic/claude-opus-4-7" ;;
    *)       model_used="anthropic/claude-sonnet-4-6" ;;
  esac
fi

# ── Build CSV row ─────────────────────────────────────────────────────────────
timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Message preview: first 50 chars, strip commas/newlines for CSV safety
message_preview=$(echo "$message" | tr '\n' ' ' | cut -c1-50 | sed 's/,/;/g')

# Token estimate: word_count * 1.3
word_count=$(echo "$message" | wc -w | tr -d ' ')
tokens_est=$(python3 -c "print(round(${word_count} * 1.3))" 2>/dev/null || echo "$word_count")

csv_row="${timestamp},${session_type},${message_preview},${tier_classified},${model_used},${tokens_est}"

# ── Write to log ──────────────────────────────────────────────────────────────
mkdir -p "$LOG_DIR"

# Write header if file doesn't exist
if [[ ! -f "$LOG_FILE" ]]; then
  echo "timestamp,session_type,message_preview,tier_classified,model_used,tokens_est" > "$LOG_FILE"
fi

echo "$csv_row" >> "$LOG_FILE"

# ── Confirm ───────────────────────────────────────────────────────────────────
echo "Logged: $csv_row"
echo "File:   $LOG_FILE"
