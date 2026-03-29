#!/usr/bin/env python3
"""
Rocket.Chat → Mistral 7B Direct Bridge
Bypasses OpenClaw agent system to route messages directly to local Ollama Mistral model
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
ROCKETCHAT_URL = "http://localhost:3000"
OLLAMA_URL = "http://localhost:11434"
BOT_USER_ID = "NyTi2Ktzzv4Q6hDoL"
BOT_AUTH_TOKEN = "oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ"
DM_ROOM_ID = "69c9017c2fa4cd8b432ac5ca"  # Bob's DM with Momotaro

# Headers for Rocket.Chat API
RC_HEADERS = {
    "X-User-Id": BOT_USER_ID,
    "X-Auth-Token": BOT_AUTH_TOKEN,
    "Content-Type": "application/json"
}

def get_latest_messages(limit=5):
    """Fetch latest messages from DM room"""
    # Try direct message endpoint first
    url = f"{ROCKETCHAT_URL}/api/v1/dm.messages?roomId={DM_ROOM_ID}&count={limit}"
    try:
        resp = requests.get(url, headers=RC_HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if "messages" in data:
                return data.get("messages", [])
        
        # Fallback to channels endpoint
        url = f"{ROCKETCHAT_URL}/api/v1/channels.messages?roomId={DM_ROOM_ID}&count={limit}"
        resp = requests.get(url, headers=RC_HEADERS, timeout=5)
        if resp.status_code == 200:
            return resp.json().get("messages", [])
    except Exception as e:
        print(f"❌ Error fetching messages: {e}")
    return []

def send_message(text):
    """Send message via Rocket.Chat API"""
    # Use postMessage endpoint (works for both channels and DMs)
    url = f"{ROCKETCHAT_URL}/api/v1/chat.postMessage"
    payload = {
        "roomId": DM_ROOM_ID,
        "text": text
    }
    try:
        resp = requests.post(url, json=payload, headers=RC_HEADERS, timeout=10)
        if resp.status_code == 200 and resp.json().get("success"):
            print(f"✅ Message sent: {text[:50]}...")
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
    """Check for new messages and respond"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking for messages...")
    
    messages = get_latest_messages(limit=3)
    if not messages:
        print("No messages found")
        return
    
    # Get the latest message from Bob (not from Momotaro)
    for msg in messages:
        username = msg.get("u", {}).get("username", "")
        text = msg.get("msg", "")
        msg_id = msg.get("_id", "")
        
        if username == "bob-reilly" and text:
            print(f"\n📨 Message from {username}: {text}")
            
            # Generate response using Mistral
            response = generate_response(text)
            
            if response:
                print(f"✨ Mistral response: {response[:100]}...")
                # Send response back to Rocket.Chat
                send_message(response)
                return
    
    print("No new messages from bob-reilly")

def monitor_loop(interval=30):
    """Continuously monitor for messages"""
    print(f"🚀 Starting Rocket.Chat ↔ Mistral Bridge")
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
