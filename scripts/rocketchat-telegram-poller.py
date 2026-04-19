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
import sys

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

def log(msg):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)
    sys.stdout.flush()

def get_telegram_token():
    """Load Telegram bot token from file"""
    try:
        with open(os.path.expanduser('~/.openclaw/telegram-bot-token'), 'r') as f:
            token = f.read().strip()
            if token:
                return token
    except Exception as e:
        log(f"⚠️ Error reading token: {e}")
    return None

def forward_to_telegram(message_text):
    """Send message to Telegram"""
    token = get_telegram_token()
    if not token:
        log("⚠️ No Telegram token configured")
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
            log(f"✅ Forwarded to Telegram")
            return True
        else:
            log(f"⚠️ Telegram error: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        log(f"❌ Forward failed: {e}")
        return False

def get_latest_message():
    """Get latest message from #general"""
    try:
        url = f"{ROCKETCHAT_URL}/api/v1/channels.messages?roomId={GENERAL_ROOM_ID}&count=1"
        resp = requests.get(url, headers=RC_HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            messages = data.get('messages', [])
            if messages:
                return messages[0]
        else:
            log(f"⚠️ API error: {resp.status_code}")
    except Exception as e:
        log(f"❌ API error: {e}")
    return None

def check_for_new_messages():
    """Check for new messages from bob_r"""
    global LAST_MESSAGE_ID
    
    try:
        msg = get_latest_message()
        if not msg:
            return False
        
        msg_id = msg.get('_id', '')
        username = msg.get('u', {}).get('username', '')
        text = msg.get('msg', '')
        timestamp = msg.get('ts', '')
        
        # Skip if same message
        if msg_id == LAST_MESSAGE_ID:
            return False
        
        # Update last message ID
        LAST_MESSAGE_ID = msg_id
        
        # Skip if not from bob_r
        if username != 'bob_r':
            return False
        
        # Skip if no text
        if not text:
            return False
        
        # New message from bob_r!
        try:
            time_str = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%H:%M:%S')
        except:
            time_str = "??:??:??"
        
        log(f"🚀 NEW MESSAGE FROM bob_r [{time_str}]")
        log(f"   Message: {text[:100]}")
        
        # Forward to Telegram
        forward_to_telegram(text)
        return True
    except Exception as e:
        log(f"❌ Error checking messages: {e}")
        return False

def main():
    """Main polling loop"""
    log("=" * 60)
    log("🚀 Rocket.Chat → Telegram Poller Started")
    log(f"📍 Polling #general every {POLL_INTERVAL} seconds")
    log(f"📍 Forwarding messages from bob_r to Telegram")
    log(f"📍 Telegram token: {('✅ Configured' if get_telegram_token() else '❌ Missing')}")
    log("=" * 60)
    
    try:
        poll_count = 0
        while True:
            poll_count += 1
            check_for_new_messages()
            if poll_count % 20 == 0:
                log(f"Polling... ({poll_count} checks)")
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        log("✋ Poller stopped")
    except Exception as e:
        log(f"❌ Fatal error: {e}")
        raise

if __name__ == '__main__':
    main()
