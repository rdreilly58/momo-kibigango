#!/bin/bash
# harness-fallback.sh — Try harnesses in order, return success if any work
# Usage: harness-fallback.sh "task-description"

set -euo pipefail

TASK="${1:-observer}"
LOG_FILE="$HOME/.openclaw/logs/observer-harness.log"
mkdir -p "$(dirname "$LOG_FILE")"

# Try harnesses in fallback order
HARNESSES=("anthropic" "ollama" "local")

for harness in "${HARNESSES[@]}"; do
  case "$harness" in
    anthropic)
      if command -v anthropic &>/dev/null; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] $TASK: trying harness=anthropic" >> "$LOG_FILE"
        exit 0
      fi
      ;;
    ollama)
      if curl -s http://127.0.0.1:11434/api/tags &>/dev/null; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] $TASK: trying harness=ollama" >> "$LOG_FILE"
        exit 0
      fi
      ;;
    local)
      echo "[$(date +'%Y-%m-%d %H:%M:%S')] $TASK: fallback=local-python" >> "$LOG_FILE"
      exit 0
      ;;
  esac
done

exit 1
