#!/usr/bin/env python3
"""
Rocket.Chat → OpenClaw Gateway Bridge
Routes Rocket.Chat messages through OpenClaw Gateway to reach Claude AI
"""

import requests
import json
import time
import sys
from datetime import datetime

# Track processed message IDs to avoid duplicate responses
PROCESSED_MESSAGES = set()
MAX_TRACKED = 100

# Configuration
ROCKETCHAT_URL = "http://localhost:3000"
OPENCLAW_GATEWAY = "https://127.0.0.1:18789"  # Local loopback with TLS
BOT_USER_ID = "NyTi2Ktzzv4Q6hDoL"
BOT_AUTH_TOKEN = "oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ"
GENERAL_ROOM_ID = "GENERAL"

# Gateway auth token
GATEWAY_TOKEN = "7b8a244f4f9ba85d67f41de3ae835682e7c9ca25facc2fa4"

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
    """Send message to Rocket.Chat channel"""
    url = f"{ROCKETCHAT_URL}/api/v1/chat.postMessage"
    payload = {
        "roomId": room_id,
        "text": text
    }
    try:
        resp = requests.post(url, json=payload, headers=RC_HEADERS, timeout=10)
        if resp.status_code == 200 and resp.json().get("success"):
            print(f"✅ Message posted to #general: {text[:50]}...")
            return True
        else:
            print(f"⚠️ API error {resp.status_code}: {resp.text[:100]}")
    except Exception as e:
        print(f"❌ Error posting message: {e}")
    return False

def query_openclaw_gateway(question):
    """Send question to OpenClaw Gateway and get response from Claude"""
    url = f"{OPENCLAW_GATEWAY}/message"
    
    headers = {
        "Authorization": f"Bearer {GATEWAY_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": question,
        "context": "Rocket.Chat channel query"
    }
    
    try:
        print(f"🌐 Querying OpenClaw Gateway at {url}...")
        # Disable SSL verification for localhost (self-signed cert)
        resp = requests.post(url, json=payload, headers=headers, timeout=30, verify=False)
        
        if resp.status_code == 200:
            data = resp.json()
            response_text = data.get("response") or data.get("message") or data.get("text")
            if response_text:
                return response_text
        else:
            print(f"⚠️ Gateway returned {resp.status_code}")
            return None
    except Exception as e:
        print(f"❌ Gateway error: {e}")
        return None

def process_messages():
    """Check for new messages and route to OpenClaw Gateway"""
    global PROCESSED_MESSAGES
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking for messages...")
    
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
        
        # Found new message from Bob
        print(f"\n📨 New message from {username}: {text}")
        
        # Mark as processed
        PROCESSED_MESSAGES.add(msg_id)
        if len(PROCESSED_MESSAGES) > MAX_TRACKED:
            PROCESSED_MESSAGES.pop()
        
        # Query OpenClaw Gateway (routes to Claude)
        response = query_openclaw_gateway(text)
        
        if response:
            print(f"✨ Claude response: {response[:100]}...")
            # Post response back to #general
            send_message_to_channel(response, GENERAL_ROOM_ID)
            return
        else:
            print("⚠️ No response from OpenClaw Gateway")

def monitor_loop(interval=10):
    """Continuously monitor for messages"""
    print(f"🚀 Starting Rocket.Chat ↔ OpenClaw Gateway Bridge")
    print(f"📍 Checking every {interval} seconds")
    print(f"🌐 Gateway: {OPENCLAW_GATEWAY}")
    print(f"💬 Rocket.Chat: {ROCKETCHAT_URL}")
    print(f"🎯 Target: Claude AI via OpenClaw")
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
