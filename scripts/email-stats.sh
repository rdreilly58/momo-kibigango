#!/bin/bash

# Email Statistics Helper
# Returns formatted email status for briefings
# Uses gog gmail (OAuth) instead of himalaya (IMAP broken)

ACCOUNT="rdreilly2010@gmail.com"
GOG="/opt/homebrew/bin/gog"

# Count unread emails
UNREAD=$($GOG gmail list "is:unread" --account "$ACCOUNT" --json 2>/dev/null | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('threads',[])))" 2>/dev/null || echo 0)

# Count total inbox
TOTAL=$($GOG gmail list "in:inbox" --account "$ACCOUNT" --json 2>/dev/null | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('threads',[])))" 2>/dev/null || echo 0)

# Count emails from last 24 hours
TODAY=$($GOG gmail list "newer_than:1d in:inbox" --account "$ACCOUNT" --json 2>/dev/null | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('threads',[])))" 2>/dev/null || echo 0)

# Output
if [ "$1" == "json" ]; then
    echo "{\"unread\": $UNREAD, \"total\": $TOTAL, \"today\": $TODAY}"
else
    printf "Unread: %8s | Total: %8s | Today: %8s\n" "$UNREAD" "$TOTAL" "$TODAY"
fi
