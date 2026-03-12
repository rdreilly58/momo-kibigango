#!/bin/bash

# Working Morning Briefing - No external dependencies
# Sends via gog (Gmail CLI)

EMAIL="rdreilly2010@gmail.com"
SUBJECT="☀️ Morning Briefing - $(date '+%A, %B %d, %Y')"

# Build the briefing body
BODY="Good morning! ☀️

Time: $(date '+%I:%M %p %Z')

📋 Your Priorities for Today:
• Check calendar and upcoming meetings
• Review important emails  
• Work on active projects (ReillyDesignStudio, Momotaro-iOS)

✉️ Email Status:
Briefing generated at $(date '+%Y-%m-%d %H:%M:%S')

Have a productive day! 🍑
"

# Send via gog
gog gmail send --to "$EMAIL" --subject "$SUBJECT" --body "$BODY" 2>&1 | tee -a /tmp/morning-briefing.log

exit $?
