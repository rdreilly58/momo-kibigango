#!/usr/bin/env python3
"""
Rocket.Chat Auto-Responder
Polls #general, detects messages from bob_r, generates responses with Claude
Auto-posts responses back to #general
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
POLL_INTERVAL = 3

RC_HEADERS = {
    "X-User-Id": BOT_USER_ID,
    "X-Auth-Token": BOT_AUTH_TOKEN,
    "Content-Type": "application/json"
}

LAST_MESSAGE_ID = None
POSTING_SCRIPT = "/Users/rreilly/.openclaw/workspace/scripts/post-to-rocketchat.sh"

def log(msg):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)
    sys.stdout.flush()

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
    except Exception as e:
        log(f"❌ API error: {e}")
    return None

def post_to_rocketchat(message_text):
    """Post response to Rocket.Chat using script"""
    try:
        result = subprocess.run(
            [POSTING_SCRIPT, message_text],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            log(f"✅ Posted to #general")
            return True
        else:
            log(f"⚠️ Posting failed: {result.stderr}")
            return False
    except Exception as e:
        log(f"❌ Post error: {e}")
        return False

def generate_response(user_message):
    """Generate response using Claude (via oracle CLI if available, else default response)"""
    # Try to use oracle/Claude if available
    try:
        # Create a simple prompt for Claude
        prompt = f"The user asked in Rocket.Chat: {user_message}\n\nRespond conversationally and helpfully. Keep response concise (2-3 sentences)."
        
        # Try using oracle CLI
        result = subprocess.run(
            ["oracle", "--model", "claude-opus", "--print", user_message],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0 and result.stdout:
            return result.stdout.strip()
    except:
        pass
    
    # Fallback: Use gog or simple response
    # For now, return a simple acknowledgment
    return f"I received your message: '{user_message}'. (Auto-response - awaiting Claude connection)"

def check_and_respond():
    """Check for new messages and auto-respond"""
    global LAST_MESSAGE_ID
    
    try:
        msg = get_latest_message()
        if not msg:
            return False
        
        msg_id = msg.get('_id', '')
        username = msg.get('u', {}).get('username', '')
        text = msg.get('msg', '')
        
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
        log(f"🚀 NEW MESSAGE FROM bob_r: {text[:100]}")
        
        # Generate response
        log(f"🤖 Generating response...")
        response = generate_response(text)
        
        # Post response
        log(f"📤 Posting response to #general...")
        post_to_rocketchat(response)
        
        return True
    except Exception as e:
        log(f"❌ Error: {e}")
        return False

def main():
    """Main auto-responder loop"""
    log("=" * 60)
    log("🤖 Rocket.Chat Auto-Responder Started")
    log(f"📍 Polling #general every {POLL_INTERVAL} seconds")
    log(f"📍 Auto-responding to messages from bob_r")
    log("=" * 60)
    
    try:
        poll_count = 0
        while True:
            poll_count += 1
            check_and_respond()
            if poll_count % 20 == 0:
                log(f"Polling... ({poll_count} checks)")
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        log("✋ Auto-responder stopped")
    except Exception as e:
        log(f"❌ Fatal error: {e}")
        raise

if __name__ == '__main__':
    main()
