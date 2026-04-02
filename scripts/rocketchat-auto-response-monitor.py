#!/usr/bin/env python3
"""
Auto-Response Monitor
Watches responder logs for messages and automatically generates/posts responses
This runs continuously in the background
"""

import subprocess
import time
from datetime import datetime
import os

RESPONDER_LOG = os.path.expanduser("~/.openclaw/logs/responder.log")
POSTING_SCRIPT = os.path.expanduser("~/.openclaw/workspace/scripts/post-to-rocketchat.sh")
CHECK_INTERVAL = 1  # Check every 1 second

# Track processed messages
PROCESSED_MESSAGES = set()

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

def get_recent_logs(lines=30):
    """Get recent lines from responder log"""
    try:
        result = subprocess.run(
            ["tail", "-n", str(lines), RESPONDER_LOG],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip().split('\n') if result.stdout else []
    except:
        return []

def extract_message_from_logs():
    """Find latest message that needs response"""
    logs = get_recent_logs(20)
    
    for line in reversed(logs):
        # Look for "New message" followed by "Acknowledgment posted"
        if "📨 New message" in line:
            # Extract message details
            try:
                # Format: [HH:MM:SS] 📨 New message from bob-reilly: MESSAGE TEXT
                msg_part = line.split("📨 New message from ")[-1]
                username, message = msg_part.split(": ", 1)
                
                # Check if we already processed this
                msg_id = f"{username}:{message[:50]}"
                if msg_id in PROCESSED_MESSAGES:
                    return None
                
                # Check if acknowledgment was posted
                ack_found = any("✅ Acknowledgment posted" in l for l in logs)
                if ack_found:
                    PROCESSED_MESSAGES.add(msg_id)
                    return message
            except:
                pass
    
    return None

def generate_simple_response(message):
    """Generate a simple acknowledgment response"""
    # For now, just return the message back
    # This could be extended to call Claude
    return f"Got your message: {message}"

def post_response(response_text):
    """Post response to Rocket.Chat"""
    try:
        result = subprocess.run(
            [POSTING_SCRIPT, response_text],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        log(f"❌ Post error: {e}")
        return False

def main():
    log("=" * 60)
    log("🚀 Auto-Response Monitor Started")
    log("📍 Continuously monitoring responder logs")
    log("📍 Auto-posting responses within 1 second")
    log("=" * 60)
    
    try:
        check_count = 0
        while True:
            check_count += 1
            
            # Check for unanswered messages
            message = extract_message_from_logs()
            if message:
                log(f"🎯 Found unanswered message: {message[:60]}")
                log(f"📤 Auto-generating response...")
                
                # For now: just acknowledge
                # Later: integrate Claude for real responses
                response = f"Got your message: {message}"
                
                log(f"📤 Posting response...")
                if post_response(response):
                    log(f"✅ Response posted!")
                else:
                    log(f"⚠️ Failed to post response")
            
            if check_count % 100 == 0:
                log(f"Monitoring... ({check_count} checks)")
            
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        log("✋ Monitor stopped")
    except Exception as e:
        log(f"❌ Fatal error: {e}")
        raise

if __name__ == '__main__':
    main()
