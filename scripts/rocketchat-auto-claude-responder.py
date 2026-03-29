#!/usr/bin/env python3
"""
Rocket.Chat Auto-Responder with Claude Integration
1. Listen for messages on #general
2. Send acknowledgment immediately
3. Call Claude API to generate response
4. Post full response to both Telegram and Rocket.Chat
All automated - no manual intervention
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
POLL_INTERVAL = 1

RC_HEADERS = {
    "X-User-Id": BOT_USER_ID,
    "X-Auth-Token": BOT_AUTH_TOKEN,
    "Content-Type": "application/json"
}

TELEGRAM_CHAT_ID = 8755120444
POSTING_SCRIPT = "/Users/rreilly/.openclaw/workspace/scripts/post-to-rocketchat.sh"

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
            return f.read().strip()
    except:
        return None

def send_to_telegram(message_text):
    """Send message to Telegram"""
    token = get_telegram_token()
    if not token:
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message_text,
            "parse_mode": "Markdown"
        }
        resp = requests.post(url, json=payload, timeout=5)
        return resp.status_code == 200
    except:
        return False

def post_to_rocketchat(message_text):
    """Post to Rocket.Chat"""
    try:
        result = subprocess.run(
            [POSTING_SCRIPT, message_text],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
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
    except:
        pass
    return None

def generate_response_with_claude(user_message):
    """
    Generate response using Claude
    Since we don't have direct API access, send to main Claude session via sessions_send
    For now, use a subprocess to call Claude via OpenClaw
    """
    try:
        # Use oracle CLI if available (Claude interface)
        # Otherwise fall back to a simple response
        result = subprocess.run(
            ["oracle", "--model", "claude-opus", "--print", "--permission-mode", "bypassPermissions", user_message],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            response = result.stdout.strip()
            # Limit response length for Rocket.Chat
            if len(response) > 500:
                response = response[:500] + "..."
            return response
    except Exception as e:
        log(f"⚠️ Claude API error: {e}")
    
    # Fallback: acknowledgment
    return f"Processing: {user_message}"

def process_message(msg):
    """Process a new message"""
    global LAST_MESSAGE_ID
    
    msg_id = msg.get('_id', '')
    username = msg.get('u', {}).get('username', '')
    text = msg.get('msg', '')
    
    if msg_id == LAST_MESSAGE_ID:
        return False
    
    LAST_MESSAGE_ID = msg_id
    
    # Skip momotaro's own responses
    if username == 'momotaro':
        return False
    
    if not text:
        return False
    
    # Step 1: Log
    log(f"📨 Message from {username}: {text[:80]}")
    
    # Step 2: Post acknowledgment immediately
    log(f"⚡ Posting acknowledgment...")
    post_to_rocketchat(f"Got it! Processing: {text}")
    
    # Step 3: Notify on Telegram
    log(f"📤 Telegram notification...")
    send_to_telegram(f"📨 *{username}*:\n\n{text}")
    
    # Step 4: Generate response (with Claude)
    log(f"🤖 Generating response with Claude...")
    response = generate_response_with_claude(text)
    
    # Step 5: Post full response
    log(f"📤 Posting response...")
    post_to_rocketchat(response)
    send_to_telegram(f"📤 *Response*:\n\n{response}")
    
    log(f"✅ Complete")
    return True

def main():
    """Main loop"""
    log("=" * 70)
    log("🚀 Rocket.Chat Auto-Responder with Claude (AUTOMATED)")
    log("📍 1-second polling + instant ACK + Claude response")
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
        log("✋ Stopped")
    except Exception as e:
        log(f"❌ Fatal error: {e}")
        raise

if __name__ == '__main__':
    main()
