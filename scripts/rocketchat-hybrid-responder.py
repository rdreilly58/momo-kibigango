#!/usr/bin/env python3
"""
Rocket.Chat Hybrid Responder
- Auto-responds with Mistral 7B for instant acknowledgment
- Forwards to Claude (Momotaro) for complete answer
- Posts Claude's answer after he responds
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

def generate_instant_response(question):
    """Generate quick Mistral response for immediate acknowledgment"""
    url = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": "mistral",
        "prompt": f"Respond briefly (1-2 sentences) to this question:\n\n{question}\n\nKeep it concise and acknowledge the question.",
        "stream": False
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            return result.get("response", "").strip()
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def post_to_rocket_chat(text):
    """Post message to #general"""
    url = f"{ROCKETCHAT_URL}/api/v1/chat.postMessage"
    payload = {
        "roomId": GENERAL_ROOM_ID,
        "text": text
    }
    try:
        resp = requests.post(url, json=payload, headers=RC_HEADERS, timeout=10)
        if resp.status_code == 200 and resp.json().get("success"):
            print(f"✅ Posted: {text[:50]}...")
            return True
    except Exception as e:
        print(f"❌ Error posting: {e}")
    return False

def process_messages():
    """Monitor and respond to messages"""
    messages = get_latest_messages(limit=10)
    
    if not messages:
        return
    
    for msg in reversed(messages):
        msg_id = msg.get('_id', '')
        username = msg.get('u', {}).get('username', '')
        text = msg.get('msg', '')
        
        if msg_id in PROCESSED_MESSAGE_IDS or username != 'bob_r' or not text:
            continue
        
        print(f"\n📨 New message: {text}")
        
        PROCESSED_MESSAGE_IDS.add(msg_id)
        if len(PROCESSED_MESSAGE_IDS) > 100:
            PROCESSED_MESSAGE_IDS.clear()
        
        # Step 1: Post instant Mistral response for acknowledgment
        instant = generate_instant_response(text)
        if instant:
            response_msg = f"""⚡ **Quick Answer:**
{instant}

_Getting Claude's complete response..._"""
            post_to_rocket_chat(response_msg)
            print(f"⚡ Instant response posted")
        
        # Step 2: Notify that Claude is responding
        print(f"🔔 Forwarding to Claude for complete answer...")
        print(f"📱 You should see message in Telegram now")
        print(f"🤖 Waiting for Claude response...")

def main():
    """Main loop"""
    print(f"🚀 Rocket.Chat Hybrid Responder")
    print(f"📍 Monitoring #general")
    print(f"⚡ Instant: Mistral 7B (acknowledgment)")
    print(f"🤖 Complete: Claude (Momotaro)")
    print(f"⏱️ Checking every 2 seconds")
    print("=" * 50)
    
    try:
        while True:
            process_messages()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n⏹️ Stopped")

if __name__ == '__main__':
    main()
