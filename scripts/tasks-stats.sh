#!/bin/bash

# Google Tasks Statistics Helper
# Returns task counts and active tasks for briefings

# Get task list ID (ToDo list)
TASKLIST_ID="MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow"

# Count pending tasks (needsAction status)
PENDING=$(/opt/homebrew/bin/gog tasks list --account rdreilly2010@gmail.com "$TASKLIST_ID" --plain 2>/dev/null | tail -n +2 | grep "needsAction" | wc -l)

# Count completed tasks
COMPLETED=$(/opt/homebrew/bin/gog tasks list --account rdreilly2010@gmail.com "$TASKLIST_ID" --plain 2>/dev/null | tail -n +2 | grep "completed" | wc -l)

# Get top 5 pending tasks
TOP_TASKS=$(/opt/homebrew/bin/gog tasks list --account rdreilly2010@gmail.com "$TASKLIST_ID" --plain 2>/dev/null | tail -n +2 | grep "needsAction" | head -5 | cut -f2)

# Output for use in scripts
if [ "$1" == "json" ]; then
    echo "{\"pending\": $PENDING, \"completed\": $COMPLETED}"
elif [ "$1" == "top" ]; then
    echo "$TOP_TASKS"
else
    echo "Pending: $PENDING | Completed: $COMPLETED"
fi
