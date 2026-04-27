#!/bin/bash
# memory-maintenance-cron.sh — Run all memory maintenance tasks
# Schedule: Weekly (Sunday 2am) or adjust as needed

set -euo pipefail

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
SCRIPTS="$WORKSPACE/scripts"

echo "[maintenance] Starting memory system maintenance..."

# 1. Lifecycle: demote stale memories (>90 days inactive)
echo "[maintenance] Phase 1: Warm→Cold demotion..."
bash "$SCRIPTS/memory-lifecycle-manager.sh" 90 || echo "[maintenance:warn] Lifecycle demote failed"

# 2. Deduplication: find and merge high-confidence duplicates
echo "[maintenance] Phase 2: Deduplication (0.95 threshold)..."
python3 "$SCRIPTS/memory-deduplication.py" --threshold 0.95 2>&1 | head -20 || echo "[maintenance:warn] Dedup failed"

# 3. Query analytics: compute stats
echo "[maintenance] Phase 3: Query analytics..."
python3 "$SCRIPTS/memory-query-analytics.py" --stats --days 7 > /tmp/memory-analytics-report.json 2>/dev/null || echo "[maintenance:warn] Analytics failed"

echo "[maintenance] Done"
bash "$WORKSPACE/scripts/cron-heartbeat.sh" memory-maintenance $?
