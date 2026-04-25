#!/bin/bash
# Monitor responder logs and alert when new messages are detected
# This will trigger a notification so I respond immediately

RESPONDER_LOG="$HOME/.openclaw/logs/responder.log"

echo "🔍 Rocket.Chat Message Watcher Started"
echo "Monitoring: $RESPONDER_LOG"
echo "Will alert on new messages from bob_r"
echo ""

# Track last seen line
LAST_LINE=0

while true; do
  # Count current lines
  CURRENT_LINES=$(wc -l < "$RESPONDER_LOG")
  
  # If new lines were added
  if [ "$CURRENT_LINES" -gt "$LAST_LINE" ]; then
    # Show new lines
    NEW_CONTENT=$(tail -n $((CURRENT_LINES - LAST_LINE)) "$RESPONDER_LOG")
    
    # Check if new message detected
    if echo "$NEW_CONTENT" | grep -q "📨 New message"; then
      # Extract message details
      MESSAGE=$(echo "$NEW_CONTENT" | grep "📨 New message" | head -1)
      
      # Send alert to Telegram
      TOKEN=$(cat ~/.openclaw/telegram-bot-token 2>/dev/null)
      if [ -n "$TOKEN" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" \
          -d "chat_id=8755120444" \
          -d "text=🚨 NEW MESSAGE DETECTED - RESPOND NOW!%0A$MESSAGE" \
          -d "parse_mode=Markdown" > /dev/null 2>&1
      fi
      
      echo "🚨 ALERT: $MESSAGE"
    fi
    
    LAST_LINE=$CURRENT_LINES
  fi
  
  sleep 1
done
