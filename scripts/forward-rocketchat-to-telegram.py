#!/usr/bin/env python3
"""
Periodically check Rocket.Chat #general for new messages and forward to Telegram
"""

import requests
import json
import time
from datetime import datetime

ROCKETCHAT_URL = "http://localhost:3000"
BOT_USER_ID = "NyTi2Ktzzv4Q6hDoL"
BOT_AUTH_TOKEN = "oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ"
GENERAL_ROOM_ID = "GENERAL"

RC_HEADERS = {
    "X-User-Id": BOT_USER_ID,
    "X-Auth-Token": BOT_AUTH_TOKEN,
    "Content-Type": "application/json"
}

# Track last message we forwarded
LAST_MESSAGE_ID = None

def get_latest_message():
    """Get latest message from #general"""
    url = f"{ROCKETCHAT_URL}/api/v1/channels.messages?roomId={GENERAL_ROOM_ID}&count=1"
    try:
        resp = requests.get(url, headers=RC_HEADERS, timeout=5)
        if resp.status_code == 200:
            messages = resp.json().get('messages', [])
            if messages:
                return messages[0]
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def check_and_forward():
    """Check for new messages and forward"""
    global LAST_MESSAGE_ID
    
    msg = get_latest_message()
    if not msg:
        return
    
    msg_id = msg.get('_id', '')
    username = msg.get('u', {}).get('username', '')
    text = msg.get('msg', '')
    
    # Skip if same message or from bot
    if msg_id == LAST_MESSAGE_ID or username == 'momotaro':
        return
    
    LAST_MESSAGE_ID = msg_id
    
    # Format message for Telegram
    if username == 'bob_r':
        print(f"\n🚀 NEW MESSAGE FROM ROCKET.CHAT #general:")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📨 {username}: {text}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🤖 Waiting for your response...\n")

if __name__ == '__main__':
    print("🚀 Rocket.Chat → Telegram Forwarder Started")
    print("📍 Monitoring #general for new messages...")
    print("=" * 50)
    
    while True:
        check_and_forward()
        time.sleep(5)  # Check every 5 seconds
