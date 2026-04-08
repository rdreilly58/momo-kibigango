#!/bin/zsh

# Daily OpenClaw Config Backup Script
# Location: ~/.openclaw/workspace/scripts/backup-openclaw-config.sh

set -e

# Source and destination
CONFIG_FILE="$HOME/.openclaw/openclaw.json"
BACKUP_DIR="$HOME/.openclaw/backups"
TIMESTAMP=$(date +"%Y-%m-%d")
BACKUP_FILE="$BACKUP_DIR/openclaw-config-$TIMESTAMP.json"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Config file not found at $CONFIG_FILE" >&2
    exit 1
fi

# Create the daily backup
cp "$CONFIG_FILE" "$BACKUP_FILE"

# Clean up backups older than 7 days
# Use find to locate files older than 7 days and delete them.
find "$BACKUP_DIR" -name "openclaw-config-*.json" -mtime +7 -delete

# Success is silent, errors will be logged by cron.
exit 0
