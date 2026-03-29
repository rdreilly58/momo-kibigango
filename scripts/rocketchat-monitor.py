#!/usr/bin/env python3
"""
Rocket.Chat Monitor - Continuously monitor #general and alert for new messages
Runs in background and checks every 5 seconds
"""

import requests
import json
import time
import subprocess
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

LAST_MESSAGE_ID = None

def get_latest_message():
    """Get latest message from #general"""
    try:
        url = f"{ROCKETCHAT_URL}/api/v1/channels.messages?roomId={GENERAL_ROOM_ID}&count=1"
        resp = requests.get(url, headers=RC_HEADERS, timeout=5)
        if resp.status_code == 200:
            messages = resp.json().get('messages', [])
            if messages:
                return messages[0]
    except Exception as e:
        print(f"Error fetching messages: {e}")
    return None

def check_for_new_messages():
    """Check for new messages from bob_r"""
    global LAST_MESSAGE_ID
    
    msg = get_latest_message()
    if not msg:
        return
    
    msg_id = msg.get('_id', '')
    username = msg.get('u', {}).get('username', '')
    text = msg.get('msg', '')
    
    # Skip if same message, from bot, or not from bob_r
    if msg_id == LAST_MESSAGE_ID or username != 'bob_r' or not text:
        return
    
    LAST_MESSAGE_ID = msg_id
    
    # Found new message!
    print(f"\n🚀 NEW MESSAGE FROM ROCKET.CHAT:")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📨 {username}: {text}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Waiting for your response...")
    print()

def main():
    """Monitor loop"""
    global LAST_MESSAGE_ID
    
    print(f"🚀 Rocket.Chat Monitor Started")
    print(f"📍 Monitoring #general for new messages from bob_r")
    print(f"⏱️  Checking every 5 seconds")
    print(f"🤖 Ready for near-real-time responses")
    print("=" * 50)
    
    try:
        while True:
            check_for_new_messages()
            time.sleep(5)  # Check every 5 seconds
    except KeyboardInterrupt:
        print("\n⏹️  Monitor stopped")

if __name__ == '__main__':
    main()
