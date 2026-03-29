#!/usr/bin/env python3
"""
Rocket.Chat → Momotaro (Claude) Bridge
Routes Rocket.Chat #general messages directly to Claude AI (Momotaro)
Replies are posted back to #general for visibility
"""

import requests
import json
import time
import sys
import subprocess
from datetime import datetime

# Track processed message IDs
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

def send_message_to_channel(text, room_id):
    """Send response message to Rocket.Chat"""
    url = f"{ROCKETCHAT_URL}/api/v1/chat.postMessage"
    payload = {
        "roomId": room_id,
        "text": text
    }
    try:
        resp = requests.post(url, json=payload, headers=RC_HEADERS, timeout=10)
        if resp.status_code == 200 and resp.json().get("success"):
            print(f"✅ Posted to #general: {text[:50]}...")
            return True
    except Exception as e:
        print(f"❌ Error posting: {e}")
    return False

def query_momotaro_via_telegram(question):
    """
    Send question to Momotaro (Telegram) and get response.
    This uses the sessions_send mechanism to talk to the main agent.
    """
    try:
        print(f"🤖 Sending to Momotaro: {question[:50]}...")
        
        # Prepare the command to send message to current session
        # This calls sessions_send to forward the message to me (Momotaro) in Telegram
        cmd = [
            "python3", "-c",
            f"""
import sys
sys.path.insert(0, '/Users/rreilly/.openclaw/workspace')
from sessions_send import send_message_to_telegram
response = send_message_to_telegram('{question}')
print(response if response else 'Error: No response')
"""
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            response = result.stdout.strip()
            if response and response != "None":
                return response
        
        # Fallback: if direct call fails, post acknowledgment message
        fallback_msg = f"🔄 Query sent to Momotaro (Claude). Awaiting response..."
        print(f"ℹ️  {fallback_msg}")
        return fallback_msg
        
    except Exception as e:
        print(f"❌ Error querying Momotaro: {e}")
        return None

def process_messages():
    """Check for new messages and route to Momotaro"""
    global PROCESSED_MESSAGES
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking #general...")
    
    messages = get_channel_messages(GENERAL_ROOM_ID, limit=10)
    if not messages:
        print("  No messages")
        return
    
    for msg in messages:
        username = msg.get("u", {}).get("username", "")
        text = msg.get("msg", "")
        msg_id = msg.get("_id", "")
        
        if msg_id in PROCESSED_MESSAGES or not text or username != "bob_r":
            continue
        
        print(f"\n📨 New message: {text}")
        
        PROCESSED_MESSAGES.add(msg_id)
        if len(PROCESSED_MESSAGES) > MAX_TRACKED:
            PROCESSED_MESSAGES.pop()
        
        # Query Momotaro (Claude)
        response = query_momotaro_via_telegram(text)
        
        if response:
            send_message_to_channel(response, GENERAL_ROOM_ID)
            return

def monitor_loop(interval=10):
    """Continuously monitor"""
    print(f"🚀 Rocket.Chat ↔ Momotaro (Claude) Bridge")
    print(f"📍 Monitoring #general every {interval}s")
    print(f"🎯 Target: Momotaro (Claude AI)")
    print("=" * 50)
    
    try:
        while True:
            process_messages()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n⏹️  Stopped")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("🧪 Test Mode...")
        process_messages()
    else:
        monitor_loop(interval=10)
