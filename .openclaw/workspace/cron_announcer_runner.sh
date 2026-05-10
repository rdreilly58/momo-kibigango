#!/bin/bash

# cron_announcer_runner.sh
# Usage: ./cron_announcer_runner.sh <target_script_path> <announcement_message>

TARGET_SCRIPT="$1"
ANN_MESSAGE="$2"

if [ -z "$TARGET_SCRIPT" ]; then
    echo "Error: Target script path must be provided as the first argument."
    exit 1
fi

# 1. Announce the event
if [ -z "$ANN_MESSAGE" ]; then
    echo "Hello! I see that a scheduled reminder has been triggered for you."
    echo "It looks like you have a reminder to run the following script:"
    echo "bash $TARGET_SCRIPT"
    echo ""
    echo "This will run at $(date +'%Y-%m-%d %H:%M:%S %Z') on the system time."
else
    echo "$ANN_MESSAGE"
fi

# 2. Execute the actual script and send output
echo "--- Executing Script Output ---"
bash "$TARGET_SCRIPT"
echo "------------------------------"