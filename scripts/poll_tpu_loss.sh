#!/bin/bash
# Poll TPU training log for new loss lines and print them
# State file tracks last seen line count

STATE_FILE="/tmp/tpu_loss_last_line"
LAST_LINE=0
if [ -f "$STATE_FILE" ]; then
  LAST_LINE=$(cat "$STATE_FILE")
fi

# Fetch log from TPU
LOG=$(gcloud compute tpus tpu-vm ssh momo-akira-tpu \
  --zone=us-east5-a \
  --command="cat ~/training.log" 2>/dev/null)

# Extract loss lines
LOSS_LINES=$(echo "$LOG" | grep -n "step=" | awk -F: '{if ($1 > '"$LAST_LINE"') print $0}')

if [ -n "$LOSS_LINES" ]; then
  echo "$LOSS_LINES"
  # Update last seen line
  NEW_LAST=$(echo "$LOG" | wc -l | tr -d ' ')
  echo "$NEW_LAST" > "$STATE_FILE"
else
  echo "NO_NEW_LOSS"
fi
