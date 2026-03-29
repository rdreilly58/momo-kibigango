#!/usr/bin/env python3
"""
Rocket.Chat Unified Responder
1. Listen for ALL messages on #general
2. Print received message to Telegram
3. Act on message (generate response)
4. Post response to BOTH Telegram and Rocket.Chat
"""

import requests
import json
import time
from datetime import datetime
import os
import sys
import subprocess

# Configuration
ROCKETCHAT_URL = "http://localhost:3000"
BOT_USER_ID = "NyTi2Ktzzv4Q6hDoL"
BOT_AUTH_TOKEN = "oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ"
GENERAL_ROOM_ID = "GENERAL"
POLL_INTERVAL = 1  # Check every 1 second for faster response

RC_HEADERS = {
    "X-User-Id": BOT_USER_ID,
    "X-Auth-Token": BOT_AUTH_TOKEN,
    "Content-Type": "application/json"
}

TELEGRAM_CHAT_ID = 8755120444
POSTING_SCRIPT = "/Users/rreilly/.openclaw/workspace/scripts/post-to-rocketchat.sh"

# Track processed messages
LAST_MESSAGE_ID = None

def log(msg):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)
    sys.stdout.flush()

def get_telegram_token():
    """Load Telegram bot token"""
    try:
        with open(os.path.expanduser('~/.openclaw/telegram-bot-token'), 'r') as f:
            token = f.read().strip()
            return token if token else None
    except:
        return None

def send_to_telegram(message_text):
    """Send message to Telegram"""
    token = get_telegram_token()
    if not token:
        log("⚠️ No Telegram token")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message_text,
            "parse_mode": "Markdown"
        }
        resp = requests.post(url, json=payload, timeout=5)
        if resp.status_code == 200:
            return True
        else:
            log(f"⚠️ Telegram error: {resp.status_code}")
            return False
    except Exception as e:
        log(f"❌ Telegram error: {e}")
        return False

def post_to_rocketchat(message_text):
    """Post to Rocket.Chat using script"""
    try:
        result = subprocess.run(
            [POSTING_SCRIPT, message_text],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        log(f"❌ Post error: {e}")
        return False

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
        log(f"❌ API error: {e}")
    return None

def generate_response(user_message, username):
    """
    Generate INSTANT acknowledgment to show message was received
    Actual thoughtful response will be provided by Claude manually
    """
    # Instant acknowledgment shows user their message was received
    return f"Got it! Processing: {user_message}"

def process_message(msg):
    """Process a new message"""
    global LAST_MESSAGE_ID
    
    msg_id = msg.get('_id', '')
    username = msg.get('u', {}).get('username', '')
    text = msg.get('msg', '')
    
    # Skip if same message ID
    if msg_id == LAST_MESSAGE_ID:
        return False
    
    LAST_MESSAGE_ID = msg_id
    
    # Skip if from momotaro (our own response)
    if username == 'momotaro':
        return False
    
    # Skip if no text
    if not text:
        return False
    
    # Step 1: Log message received
    log(f"📨 New message from {username}: {text[:80]}")
    
    # Step 1a: IMMEDIATE acknowledgment to Rocket.Chat (fast response visible)
    log(f"⚡ Posting instant acknowledgment...")
    ack_response = generate_response(text, username)
    post_to_rocketchat(ack_response)
    
    # Step 2: Send message to Telegram for my awareness
    telegram_msg = f"🚀 *{username}* in #general:\n\n_{text}_\n\n(Acknowledgment posted to #general)"
    log(f"📤 Sending to Telegram...")
    send_to_telegram(telegram_msg)
    
    # Step 3: Await manual response from Claude
    log(f"⏳ Awaiting manual response...")
    
    log(f"✅ Acknowledgment posted (awaiting detailed response)")
    return True

def main():
    """Main loop"""
    log("=" * 70)
    log("🚀 Rocket.Chat Unified Responder Started")
    log("📍 Listening to ALL messages on #general")
    log("📍 Forwarding messages to Telegram")
    log("📍 Processing and responding to all messages")
    log("=" * 70)
    
    try:
        poll_count = 0
        while True:
            poll_count += 1
            msg = get_latest_message()
            if msg:
                process_message(msg)
            
            if poll_count % 20 == 0:
                log(f"Listening... ({poll_count} checks)")
            
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        log("✋ Responder stopped")
    except Exception as e:
        log(f"❌ Fatal error: {e}")
        raise

if __name__ == '__main__':
    main()
