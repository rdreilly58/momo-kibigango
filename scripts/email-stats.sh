#!/bin/bash

# Email Statistics Helper
# Returns formatted email status for briefings

# Count unread emails
UNREAD=$(/opt/homebrew/bin/himalaya envelope list "flag unseen" 2>/dev/null | tail -n +2 | wc -l)

# Count all emails
TOTAL=$(/opt/homebrew/bin/himalaya envelope list 2>/dev/null | tail -n +2 | wc -l)

# Count emails from last 24 hours
TODAY=$(/opt/homebrew/bin/himalaya envelope list "after $(date -v-1d +%Y-%m-%d)" 2>/dev/null | tail -n +2 | wc -l)

# Output for use in scripts
if [ "$1" == "json" ]; then
    echo "{\"unread\": $UNREAD, \"total\": $TOTAL, \"today\": $TODAY}"
else
    echo "Unread: $UNREAD | Total: $TOTAL | Today: $TODAY"
fi
