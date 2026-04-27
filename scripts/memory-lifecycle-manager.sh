#!/bin/bash
# memory-lifecycle-manager.sh — Auto-promote memories from warm to cold
# Run daily or weekly to keep warm store lean

set -euo pipefail

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
DB_PATH="$WORKSPACE/ai-memory.db"
DAYS_INACTIVE="${1:-90}"

echo "[lifecycle] Starting warm→cold demotion (inactive > ${DAYS_INACTIVE}d)"

python3 << 'PYTHON_EOF'
import sys
import os
sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/scripts"))

from memory_tier_manager import TierManager
from memory_audit_logger import log_operation

try:
    db_path = os.environ.get("DB_PATH")
    days_inactive = int(os.environ.get("DAYS_INACTIVE", "90"))

    tm = TierManager(db_path=db_path)
    demoted_count = tm.demote_cold_candidates(days_inactive=days_inactive)

    if demoted_count > 0:
        print(f"[lifecycle] Demoted {demoted_count} memories to cold tier")
        # Log this maintenance operation
        log_operation(
            op="demote",
            source="auto:lifecycle",
            memory_id="batch",
            namespace="workspace",
            title=f"Demoted {demoted_count} stale memories",
            content=f"Memories inactive > {days_inactive} days moved to cold storage",
            tags=["lifecycle", "maintenance"],
        )
    else:
        print("[lifecycle] No memories to demote")

except Exception as e:
    print(f"[lifecycle:error] {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_EOF

echo "[lifecycle] Done"
