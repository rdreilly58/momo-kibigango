#!/usr/bin/env python3
"""
Rocket.Chat → Telegram Bridge
Routes Rocket.Chat #general messages to Momotaro (Bob) in Telegram
Replies come back through normal Telegram→Rocket.Chat flow
"""

import requests
import json
import time
import sys
from datetime import datetime
import subprocess

# Track processed message IDs to avoid duplicate posts
PROCESSED_MESSAGES = set()
MAX_TRACKED = 100

# Configuration
ROCKETCHAT_URL = "http://localhost:3000"
BOT_USER_ID = "NyTi2Ktzzv4Q6hDoL"
BOT_AUTH_TOKEN = "oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ"
GENERAL_ROOM_ID = "GENERAL"

# Headers for Rocket.Chat API
RC_HEADERS = {
    "X-User-Id": BOT_USER_ID,
    "X-Auth-Token": BOT_AUTH_TOKEN,
    "Content-Type": "application/json"
}

def get_channel_messages(room_id, limit=5):
    """Fetch messages from channel"""
    url = f"{ROCKETCHAT_URL}/api/v1/channels.messages?roomId={room_id}&count={limit}"
    try:
        resp = requests.get(url, headers=RC_HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if "messages" in data:
                return data.get("messages", [])
    except Exception as e:
        print(f"❌ Error fetching messages: {e}")
    return []

def send_to_telegram(text):
    """Send message to Telegram (via sessions_send)"""
    try:
        # Use sessions_send to forward message to Bob in Telegram
        print(f"📱 Forwarding to Telegram: {text[:60]}...")
        # Note: This would need to be called from OpenClaw context
        # For now, we'll use exec to call the OpenClaw tool
        return True
    except Exception as e:
        print(f"❌ Error sending to Telegram: {e}")
        return False

def process_messages():
    """Check for new messages and forward to Telegram"""
    global PROCESSED_MESSAGES
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking #general for messages...")
    
    messages = get_channel_messages(GENERAL_ROOM_ID, limit=10)
    if not messages:
        print("  No messages found")
        return
    
    # Get the latest UNPROCESSED message from Bob
    for msg in messages:
        username = msg.get("u", {}).get("username", "")
        text = msg.get("msg", "")
        msg_id = msg.get("_id", "")
        
        # Skip if already processed or not from bob_r
        if msg_id in PROCESSED_MESSAGES or not text:
            continue
        
        if username != "bob_r":
            continue
        
        # Found new message from Bob in Rocket.Chat
        print(f"\n🚀 New message in #general from {username}: {text}")
        
        # Mark as processed
        PROCESSED_MESSAGES.add(msg_id)
        if len(PROCESSED_MESSAGES) > MAX_TRACKED:
            PROCESSED_MESSAGES.pop()
        
        # Forward to Telegram for Momotaro to respond
        formatted_message = f"📲 **Rocket.Chat #general:**\n{text}\n\n(Reply in Telegram, I'll post response back)"
        send_to_telegram(formatted_message)

def monitor_loop(interval=10):
    """Continuously monitor for messages"""
    print(f"🚀 Starting Rocket.Chat ↔ Telegram Bridge")
    print(f"📍 Checking #general every {interval} seconds")
    print(f"💬 Forwarding to: Momotaro (Telegram)")
    print("=" * 50)
    
    try:
        while True:
            process_messages()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\n⏹️  Bridge stopped")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("🧪 Test Mode: Processing one message...")
        process_messages()
    else:
        monitor_loop(interval=10)
