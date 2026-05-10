#!/bin/bash
# boost-process-priority.sh — Boost OpenClaw and Ollama scheduling priority
# Prevents macOS from backgrounding these processes under memory pressure.
# Run after system startup. Safe to run repeatedly.

OPENCLAW_PID=$(pgrep -f "openclaw-node" 2>/dev/null | head -1 || true)
NODE_PID=$(pgrep -f "openclaw/dist/index.js" 2>/dev/null | head -1 || true)
OLLAMA_PID=$(pgrep -x "ollama" 2>/dev/null | head -1 || true)

echo "🚀 Boosting OpenClaw + Ollama process priority..."

for PID_LABEL in "$OPENCLAW_PID:openclaw-node" "$NODE_PID:node-gateway" "$OLLAMA_PID:ollama"; do
    PID="${PID_LABEL%%:*}"
    LABEL="${PID_LABEL##*:}"
    [[ -z "$PID" ]] && continue
    taskpolicy -B -j 200 -p "$PID" 2>/dev/null && echo "  ✅ $LABEL (PID $PID): not-background, jetsam 200" || \
    echo "  ⚠️  $LABEL (PID $PID): taskpolicy failed"
done

echo "✅ Done."
