#!/usr/bin/env python3
"""
Rocket.Chat Auto-Responder
Monitors #general for new messages from bob_r and automatically generates
Claude responses using the local Mistral 7B model (instant responses)
"""

import requests
import json
import time
from datetime import datetime

ROCKETCHAT_URL = "http://localhost:3000"
OLLAMA_URL = "http://localhost:11434"
BOT_USER_ID = "NyTi2Ktzzv4Q6hDoL"
BOT_AUTH_TOKEN = "oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ"
GENERAL_ROOM_ID = "GENERAL"

RC_HEADERS = {
    "X-User-Id": BOT_USER_ID,
    "X-Auth-Token": BOT_AUTH_TOKEN,
    "Content-Type": "application/json"
}

# Track processed messages
PROCESSED_MESSAGE_IDS = set()

def get_latest_messages(limit=5):
    """Get latest messages from #general"""
    url = f"{ROCKETCHAT_URL}/api/v1/channels.messages?roomId={GENERAL_ROOM_ID}&count={limit}"
    try:
        resp = requests.get(url, headers=RC_HEADERS, timeout=5)
        if resp.status_code == 200:
            return resp.json().get('messages', [])
    except Exception as e:
        print(f"❌ Error fetching messages: {e}")
    return []

def generate_response_with_mistral(question):
    """Generate response using local Mistral 7B via Ollama"""
    url = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": "mistral",
        "prompt": question,
        "stream": False
    }
    try:
        print(f"🤖 Generating response with Mistral 7B...")
        resp = requests.post(url, json=payload, timeout=60)
        if resp.status_code == 200:
            result = resp.json()
            response_text = result.get("response", "").strip()
            if response_text:
                return response_text
    except Exception as e:
        print(f"❌ Error generating response: {e}")
    return None

def post_response_to_rocket_chat(text):
    """Post response to #general"""
    url = f"{ROCKETCHAT_URL}/api/v1/chat.postMessage"
    payload = {
        "roomId": GENERAL_ROOM_ID,
        "text": text
    }
    try:
        resp = requests.post(url, json=payload, headers=RC_HEADERS, timeout=10)
        if resp.status_code == 200 and resp.json().get("success"):
            print(f"✅ Posted to #general: {text[:50]}...")
            return True
    except Exception as e:
        print(f"❌ Error posting response: {e}")
    return False

def process_new_messages():
    """Check for new messages and respond automatically"""
    messages = get_latest_messages(limit=10)
    
    if not messages:
        return
    
    # Process messages in reverse order (oldest first)
    for msg in reversed(messages):
        msg_id = msg.get('_id', '')
        username = msg.get('u', {}).get('username', '')
        text = msg.get('msg', '')
        
        # Skip if already processed, or not from bob_r, or from momotaro
        if msg_id in PROCESSED_MESSAGE_IDS or username != 'bob_r' or not text:
            continue
        
        print(f"\n📨 New message from bob_r: {text}")
        
        # Mark as processed
        PROCESSED_MESSAGE_IDS.add(msg_id)
        
        # Limit processed messages to prevent memory leak
        if len(PROCESSED_MESSAGE_IDS) > 100:
            PROCESSED_MESSAGE_IDS.clear()
        
        # Generate response
        response = generate_response_with_mistral(text)
        
        if response:
            print(f"✨ Response: {response[:100]}...")
            # Post immediately
            post_response_to_rocket_chat(response)
        else:
            print("⚠️ No response generated")

def main():
    """Main loop"""
    print(f"🚀 Rocket.Chat Auto-Responder Started")
    print(f"📍 Monitoring #general for messages from bob_r")
    print(f"🤖 Using Mistral 7B for instant responses")
    print(f"⏱️  Checking every 2 seconds")
    print("=" * 50)
    
    try:
        while True:
            process_new_messages()
            time.sleep(2)  # Check every 2 seconds for instant responses
    except KeyboardInterrupt:
        print("\n⏹️  Auto-responder stopped")

if __name__ == '__main__':
    main()
