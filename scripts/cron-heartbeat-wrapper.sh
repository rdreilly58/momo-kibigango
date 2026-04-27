#!/bin/bash
# cron-heartbeat-wrapper.sh — Capture cron job metrics and record heartbeat
# Usage: cron-heartbeat-wrapper.sh "job-name" "command to run"

set -euo pipefail

JOB_NAME="${1:?job-name required}"
shift
COMMAND="$@"

HB_DIR="$HOME/.openclaw/logs/cron-heartbeats"
mkdir -p "$HB_DIR"

START=$(date +%s%N)
STDERR_FILE=$(mktemp)
trap 'rm -f "$STDERR_FILE"' EXIT

# Run command and capture exit code + stderr
EXIT_CODE=0
eval "$COMMAND" 2>"$STDERR_FILE" || EXIT_CODE=$?

END=$(date +%s%N)
ELAPSED_MS=$(( (END - START) / 1000000 ))

# Get first 200 chars of stderr for diagnostics
STDERR_PREVIEW=$(head -c 200 "$STDERR_FILE" | tr '\n' ' ')

# Write heartbeat JSON
python3 << 'PYTHON_EOF'
import json
import sys
import os
from datetime import datetime, timezone

job_name = os.environ.get("JOB_NAME", "unknown")
exit_code = int(os.environ.get("EXIT_CODE", "1"))
elapsed_ms = int(os.environ.get("ELAPSED_MS", "0"))
stderr_preview = os.environ.get("STDERR_PREVIEW", "")
hb_dir = os.environ.get("HB_DIR", "")

heartbeat = {
    "name": job_name,
    "last_run": datetime.now(timezone.utc).isoformat(),
    "last_run_ts": int(datetime.now(timezone.utc).timestamp()),
    "exit_code": exit_code,
    "elapsed_ms": elapsed_ms,
    "stderr": stderr_preview[:200],
    "host": os.uname()[1],
}

hb_file = os.path.join(hb_dir, f"{job_name}.json")
with open(hb_file, "w") as f:
    json.dump(heartbeat, f)

print(f"[heartbeat] {job_name}: exit={exit_code}, elapsed={elapsed_ms}ms", file=sys.stderr)
PYTHON_EOF

exit "$EXIT_CODE"
