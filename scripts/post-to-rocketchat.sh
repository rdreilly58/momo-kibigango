#!/bin/bash
# Simple script to post message to Rocket.Chat #general
# Usage: ./post-to-rocketchat.sh "Your message here"

ROCKETCHAT_URL="http://localhost:3000"
BOT_USER_ID="NyTi2Ktzzv4Q6hDoL"
BOT_AUTH_TOKEN="oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ"
GENERAL_ROOM_ID="GENERAL"

MESSAGE="$1"

if [ -z "$MESSAGE" ]; then
    echo "Usage: $0 \"Your message here\""
    exit 1
fi

curl -s -X POST "http://localhost:3000/api/v1/chat.postMessage" \
  -H "X-User-Id: ${BOT_USER_ID}" \
  -H "X-Auth-Token: ${BOT_AUTH_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"roomId\": \"${GENERAL_ROOM_ID}\", \"text\": \"${MESSAGE}\"}" | \
  grep -q "success" && echo "✅ Posted to #general" || echo "❌ Error posting"
