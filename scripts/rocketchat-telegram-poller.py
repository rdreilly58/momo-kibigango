#!/usr/bin/env python3
"""
Rocket.Chat → Telegram Poller
Continuously polls #general for new messages from bob_r
Forwards to Telegram instantly when detected
"""

import requests
import json
import time
from datetime import datetime
import os

# Configuration
ROCKETCHAT_URL = "http://localhost:3000"
BOT_USER_ID = "NyTi2Ktzzv4Q6hDoL"
BOT_AUTH_TOKEN = "oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ"
GENERAL_ROOM_ID = "GENERAL"
POLL_INTERVAL = 3  # Check every 3 seconds

RC_HEADERS = {
    "X-User-Id": BOT_USER_ID,
    "X-Auth-Token": BOT_AUTH_TOKEN,
    "Content-Type": "application/json"
}

TELEGRAM_CHAT_ID = 8755120444

# Track processed messages to avoid duplicates
LAST_MESSAGE_ID = None

def get_telegram_token():
    """Load Telegram bot token from file"""
    try:
        with open(os.path.expanduser('~/.openclaw/telegram-bot-token'), 'r') as f:
            return f.read().strip()
    except:
        return None

def forward_to_telegram(message_text):
    """Send message to Telegram"""
    token = get_telegram_token()
    if not token:
        print("⚠️ No Telegram token, skipping forward")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": f"🚀 *Rocket.Chat #general*\n\n{message_text}",
            "parse_mode": "Markdown"
        }
        
        resp = requests.post(url, json=payload, timeout=5)
        if resp.status_code == 200:
            print(f"✅ Forwarded to Telegram")
            return True
        else:
            print(f"⚠️ Telegram error: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Forward failed: {e}")
        return False

def get_latest_message():
    """Get latest message from #general"""
    try:
        url = f"{ROCKETCHAT_URL}/api/v1/channels.messages?roomId={GENERAL_ROOM_ID}&count=1&sort={{'ts': -1}}"
        resp = requests.get(url, headers=RC_HEADERS, timeout=5)
        if resp.status_code == 200:
            messages = resp.json().get('messages', [])
            if messages:
                return messages[0]
    except Exception as e:
        print(f"❌ API error: {e}")
    return None

def check_for_new_messages():
    """Check for new messages from bob_r"""
    global LAST_MESSAGE_ID
    
    msg = get_latest_message()
    if not msg:
        return False
    
    msg_id = msg.get('_id', '')
    username = msg.get('u', {}).get('username', '')
    text = msg.get('msg', '')
    timestamp = msg.get('ts', '')
    
    # Skip if same message, from bot, or not from bob_r
    if msg_id == LAST_MESSAGE_ID:
        return False
    
    if username != 'bob_r':
        LAST_MESSAGE_ID = msg_id
        return False
    
    if not text:
        LAST_MESSAGE_ID = msg_id
        return False
    
    # New message from bob_r!
    LAST_MESSAGE_ID = msg_id
    
    time_str = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%H:%M:%S')
    print(f"\n🚀 NEW MESSAGE FROM bob_r [{time_str}]")
    print(f"   Message: {text}")
    
    # Forward to Telegram
    forward_to_telegram(text)
    return True

def main():
    """Main polling loop"""
    print(f"🚀 Rocket.Chat → Telegram Poller Started")
    print(f"📍 Polling #general every {POLL_INTERVAL} seconds")
    print(f"📍 Forwarding messages from bob_r to Telegram")
    print("=" * 60)
    
    try:
        while True:
            check_for_new_messages()
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\n✋ Poller stopped")

if __name__ == '__main__':
    main()
