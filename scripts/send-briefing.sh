#!/bin/bash

# Simple morning briefing sender
# Usage: ./send-briefing.sh

EMAIL="rdreilly2010@gmail.com"
SUBJECT="☀️ Morning Briefing - $(date '+%A, %B %d, %Y')"

BODY="Good morning! ☀️

Time: $(date '+%I:%M %p %Z')

Your priorities for today:
• Check calendar and upcoming meetings
• Review important emails
• Work on active projects

Have a great day! 🍑
"

# Send via mail command (requires local mail setup)
# For now, this is a placeholder - needs proper email config
echo "$BODY" | mail -s "$SUBJECT" "$EMAIL" 2>/dev/null

if [ $? -eq 0 ]; then
  echo "✅ Briefing sent to $EMAIL"
else
  echo "⚠️ Failed to send briefing - mail command not available"
  echo "Consider using: gog gmail send, himalaya send, or gmailctl"
fi
