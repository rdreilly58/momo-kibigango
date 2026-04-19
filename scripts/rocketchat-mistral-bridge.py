#!/usr/bin/env python3
"""
Rocket.Chat → Mistral 7B Direct Bridge
Bypasses OpenClaw agent system to route messages directly to local Ollama Mistral model
Now monitors both DM and #general channel
"""

import requests
import json
import time
import sys
from datetime import datetime

# Track processed message IDs to avoid duplicate responses
PROCESSED_MESSAGES = set()
MAX_TRACKED = 100  # Keep last 100 message IDs to avoid memory leak

# Configuration
ROCKETCHAT_URL = "http://localhost:3000"
OLLAMA_URL = "http://localhost:11434"
BOT_USER_ID = "NyTi2Ktzzv4Q6hDoL"
BOT_AUTH_TOKEN = "oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ"
DM_ROOM_ID = "69c9017c2fa4cd8b432ac5ca"  # Bob's DM with Momotaro
GENERAL_ROOM_ID = "GENERAL"  # #general channel

# Headers for Rocket.Chat API
RC_HEADERS = {
    "X-User-Id": BOT_USER_ID,
    "X-Auth-Token": BOT_AUTH_TOKEN,
    "Content-Type": "application/json"
}

def get_channel_messages(room_id, limit=5):
    """Fetch messages from any channel or DM"""
    url = f"{ROCKETCHAT_URL}/api/v1/channels.messages?roomId={room_id}&count={limit}"
    try:
        resp = requests.get(url, headers=RC_HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if "messages" in data:
                return data.get("messages", [])
    except Exception as e:
        print(f"❌ Error fetching messages from {room_id}: {e}")
    return []

def send_channel_message(text, room_id):
    """Send message to any channel or DM"""
    url = f"{ROCKETCHAT_URL}/api/v1/chat.postMessage"
    payload = {
        "roomId": room_id,
        "text": text
    }
    try:
        resp = requests.post(url, json=payload, headers=RC_HEADERS, timeout=10)
        if resp.status_code == 200 and resp.json().get("success"):
            print(f"✅ Message sent to room {room_id}: {text[:50]}...")
            return True
        else:
            print(f"⚠️ API returned {resp.status_code}: {resp.text[:100]}")
    except Exception as e:
        print(f"❌ Error sending message: {e}")
    return False

def generate_response(prompt):
    """Generate response using local Mistral 7B via Ollama"""
    url = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }
    try:
        print(f"🤖 Generating response with Mistral 7B...")
        resp = requests.post(url, json=payload, timeout=60)
        if resp.status_code == 200:
            result = resp.json()
            return result.get("response", "").strip()
    except Exception as e:
        print(f"❌ Error generating response: {e}")
    return None

def process_messages():
    """Check for new messages in DM and #general and respond"""
    global PROCESSED_MESSAGES
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking for messages...")
    
    # Check #general channel only
    rooms_to_check = [
        (GENERAL_ROOM_ID, "#general")
    ]
    
    for room_id, room_name in rooms_to_check:
        messages = get_channel_messages(room_id, limit=10)
        if not messages:
            print(f"  No messages in {room_name}")
            continue
        
        # Get the latest UNPROCESSED message from Bob (not from Momotaro)
        for msg in messages:
            username = msg.get("u", {}).get("username", "")
            text = msg.get("msg", "")
            msg_id = msg.get("_id", "")
            
            # Skip if already processed or not from bob_r (username in channels) / bob-reilly (in DM)
            if msg_id in PROCESSED_MESSAGES or not text:
                continue
            
            # Match both bob-reilly (DM) and bob_r (channels)
            if username not in ["bob-reilly", "bob_r"]:
                continue
            
            # Found new message from Bob
            print(f"\n📨 New message in {room_name} from {username}: {text}")
            
            # Mark as processed immediately
            PROCESSED_MESSAGES.add(msg_id)
            if len(PROCESSED_MESSAGES) > MAX_TRACKED:
                PROCESSED_MESSAGES.pop()
            
            # Generate response using Mistral
            response = generate_response(text)
            
            if response:
                print(f"✨ Mistral response: {response[:100]}...")
                # Send response back to same room
                send_channel_message(response, room_id)
                return
    
    print("No new unprocessed messages from Bob")

def monitor_loop(interval=10):
    """Continuously monitor for messages"""
    print(f"🚀 Starting Rocket.Chat ↔ Mistral Bridge (#general only)")
    print(f"📍 Checking every {interval} seconds")
    print(f"🤖 Using Mistral 7B at {OLLAMA_URL}")
    print(f"💬 Rocket.Chat at {ROCKETCHAT_URL}")
    print("=" * 50)
    
    try:
        while True:
            process_messages()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\n⏹️  Bridge stopped")
        sys.exit(0)

if __name__ == "__main__":
    # Test mode: respond to one message and exit
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("🧪 Test Mode: Processing one message...")
        process_messages()
    else:
        # Run in monitoring mode
        monitor_loop(interval=10)
