#!/bin/bash
# cron-heartbeat.sh — Write a dead-man timestamp for a named cron job.
#
# Usage (add as last line of any cron script):
#   bash ~/.openclaw/workspace/scripts/cron-heartbeat.sh <job-name> [exit-code]
#
# Writes: ~/.openclaw/logs/cron-heartbeats/<job-name>.json
#   {"name":"...", "last_run":"<ISO>", "last_run_ts":<epoch>, "exit_code":<n>, "host":"..."}
#
# The dead-man monitor (cron-dead-man.sh) reads these files to detect missed jobs.

JOB_NAME="${1:-unknown}"
EXIT_CODE="${2:-0}"
HEARTBEAT_DIR="$HOME/.openclaw/logs/cron-heartbeats"

mkdir -p "$HEARTBEAT_DIR"

python3 - "$JOB_NAME" "$EXIT_CODE" "$HEARTBEAT_DIR" << 'EOF'
import sys, json, os, socket, time
from datetime import datetime, timezone

name, exit_code, hb_dir = sys.argv[1], int(sys.argv[2]), sys.argv[3]
now = datetime.now(timezone.utc)
payload = {
    "name": name,
    "last_run": now.isoformat(),
    "last_run_ts": int(time.time()),
    "exit_code": exit_code,
    "host": socket.gethostname(),
}
path = os.path.join(hb_dir, f"{name}.json")
with open(path, "w") as f:
    json.dump(payload, f, indent=2)
EOF
