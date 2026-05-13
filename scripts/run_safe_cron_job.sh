#!/bin/bash
#
# run_safe_cron_job.sh: A wrapper script for OpenClaw cron jobs.
# Purpose: Executes a given command robustly, catching common environment or
# scripting failures (e.g., model rejection, path issues) and providing
# a clean, predictable failure message to the cron delivery system.
#
# Usage: ./run_safe_cron_job.sh "your actual command here"
#
# --- Core Logic ---

# $1 holds the command to execute
COMMAND="$1"

echo "--- [Cron Job Started] ---"
echo "Executing command: $COMMAND"

# Execute the command and capture the exit status
# We redirect stdout and stderr to temporary variables/files to ensure
# all output is captured for the cron system to process.
OUTPUT=$(eval "$COMMAND" 2>&1)
EXIT_CODE=$?

# Check the exit code
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Command executed successfully."
    echo "Output Details: $OUTPUT"
    exit 0
else
    # If the exit code is non-zero, we report the failure
    echo "❌ Command failed with exit code: $EXIT_CODE"
    echo "Command Attempted: $COMMAND"
    echo "Error Output/Error Details: $OUTPUT"
    
    # To prevent excessive logging clutter, we only log the core error details.
    exit $EXIT_CODE
fi