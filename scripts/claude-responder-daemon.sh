#!/bin/bash
# Simple daemon that monitors #general and alerts me to respond
# Runs in background and checks every 30 seconds

ROCKETCHAT_URL="http://localhost:3000"
BOT_USER_ID="NyTi2Ktzzv4Q6hDoL"
BOT_AUTH_TOKEN="oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ"
GENERAL_ROOM_ID="GENERAL"

echo "🚀 Claude Responder Daemon Started"
echo "📍 Monitoring for messages requiring Claude response"
echo "=" > /tmp/claude-responder-state

while true; do
    # Get latest messages
    MESSAGES=$(curl -s -X GET "${ROCKETCHAT_URL}/api/v1/channels.messages?roomId=${GENERAL_ROOM_ID}&count=20" \
      -H "X-User-Id: ${BOT_USER_ID}" \
      -H "X-Auth-Token: ${BOT_AUTH_TOKEN}" 2>/dev/null)
    
    # Check for "Getting Claude's complete response..." without a following Claude response
    NEEDS_RESPONSE=$(echo "$MESSAGES" | jq -r '.messages[] | 
      select(.msg | contains("Getting Claude")) |
      .ts' | head -1)
    
    if [ ! -z "$NEEDS_RESPONSE" ]; then
        echo "📨 $(date '+%H:%M:%S') - Found message needing Claude response"
        echo "🔔 Message: $NEEDS_RESPONSE"
        
        # Save state so we know we've handled this
        echo "$NEEDS_RESPONSE" > /tmp/claude-last-response-time
    fi
    
    sleep 30
done
