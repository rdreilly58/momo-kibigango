#!/usr/bin/env python3
"""
Rocket.Chat Auto-Responder v2
- Polls #general every 1 second
- Detects new messages from bob_r (or any non-bot user)
- Generates response via Claude CLI (--print mode)
- Posts response back to #general
- Forwards to Telegram for visibility

Target: <15 second end-to-end response time
"""

import requests
import json
import time
import subprocess
import os
import sys
import threading
from datetime import datetime

# ── Configuration ──────────────────────────────────────────────────

ROCKETCHAT_URL = "http://localhost:3000"
BOT_USER_ID = "NyTi2Ktzzv4Q6hDoL"
BOT_AUTH_TOKEN = "oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ"
GENERAL_ROOM_ID = "GENERAL"
POLL_INTERVAL = 1  # seconds

RC_HEADERS = {
    "X-User-Id": BOT_USER_ID,
    "X-Auth-Token": BOT_AUTH_TOKEN,
    "Content-Type": "application/json"
}

TELEGRAM_CHAT_ID = 8755120444
BOT_USERNAME = "momotaro"

# System prompt for Rocket.Chat responses
SYSTEM_PROMPT = """You are Momotaro 🍑, Bob's AI assistant. You're responding via Rocket.Chat on his home Mac.
Keep responses concise and helpful. You have access to Bob's home systems.
Be direct, skip filler phrases. If you don't know something, say so briefly.
Bob is a Principal Software Engineer at Leidos. His timezone is America/New_York."""

# ── State ──────────────────────────────────────────────────────────

LAST_MESSAGE_ID = None
PROCESSING = False  # Prevent overlapping responses
LOG_FILE = os.path.expanduser("~/.openclaw/logs/rocketchat-responder.log")

# ── Logging ────────────────────────────────────────────────────────

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass

# ── Rocket.Chat API ───────────────────────────────────────────────

def get_latest_messages(count=5):
    """Get latest messages from #general"""
    try:
        url = f"{ROCKETCHAT_URL}/api/v1/channels.messages"
        params = {"roomId": GENERAL_ROOM_ID, "count": count}
        resp = requests.get(url, headers=RC_HEADERS, params=params, timeout=5)
        if resp.status_code == 200:
            return resp.json().get("messages", [])
    except Exception as e:
        log(f"❌ API error: {e}")
    return []

def post_message(text):
    """Post message to #general"""
    try:
        url = f"{ROCKETCHAT_URL}/api/v1/chat.postMessage"
        payload = {"roomId": GENERAL_ROOM_ID, "text": text}
        resp = requests.post(url, headers=RC_HEADERS, json=payload, timeout=10)
        if resp.status_code == 200 and resp.json().get("success"):
            log(f"✅ Posted to #general ({len(text)} chars)")
            return True
        else:
            log(f"⚠️ Post failed: {resp.status_code} {resp.text[:100]}")
    except Exception as e:
        log(f"❌ Post error: {e}")
    return False

# ── Telegram ──────────────────────────────────────────────────────

def get_telegram_token():
    try:
        with open(os.path.expanduser("~/.openclaw/telegram-bot-token"), "r") as f:
            return f.read().strip()
    except:
        return None

def send_to_telegram(text):
    token = get_telegram_token()
    if not token:
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "Markdown"
        }, timeout=5)
    except Exception as e:
        log(f"⚠️ Telegram send error: {e}")

# ── Response Generation ───────────────────────────────────────────

def build_context(messages):
    """Build recent conversation context from last few messages"""
    context_lines = []
    # Messages come newest-first, reverse for chronological order
    for msg in reversed(messages):
        username = msg.get("u", {}).get("username", "unknown")
        text = msg.get("msg", "")
        if text:
            context_lines.append(f"{username}: {text}")
    return "\n".join(context_lines[-10:])  # Last 10 messages max

def generate_response(user_message, username, recent_messages=None):
    """Generate response using Claude CLI in --print mode"""
    log(f"🧠 Generating response for: {user_message[:80]}...")
    
    # Build prompt with context
    context = ""
    if recent_messages:
        context = build_context(recent_messages)
        prompt = f"""Recent conversation in Rocket.Chat #general:
{context}

Respond to the latest message from {username}. Be concise and helpful."""
    else:
        prompt = f"""{username} says: {user_message}

Respond concisely and helpfully."""

    try:
        start = time.time()
        result = subprocess.run(
            [
                "claude", "--print",
                "--model", "claude-haiku-4-5",
                "-s", SYSTEM_PROMPT,
                prompt
            ],
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "CLAUDE_CODE_DISABLE_NONINTERACTIVE_HINT": "1"}
        )
        elapsed = time.time() - start
        
        if result.returncode == 0 and result.stdout.strip():
            response = result.stdout.strip()
            log(f"✅ Response generated in {elapsed:.1f}s ({len(response)} chars)")
            return response
        else:
            log(f"⚠️ Claude CLI failed (code {result.returncode}): {result.stderr[:200]}")
            return None
    except subprocess.TimeoutExpired:
        log(f"⚠️ Claude CLI timed out (30s)")
        return None
    except Exception as e:
        log(f"❌ Generation error: {e}")
        return None

# ── Message Processing ────────────────────────────────────────────

def handle_message(msg, all_messages):
    """Process a new message end-to-end"""
    global PROCESSING
    
    if PROCESSING:
        log("⏳ Already processing a message, skipping")
        return
    
    PROCESSING = True
    try:
        username = msg.get("u", {}).get("username", "unknown")
        text = msg.get("msg", "")
        msg_id = msg.get("_id", "")
        
        log(f"📨 [{username}]: {text[:100]}")
        start_time = time.time()
        
        # Generate real response
        response = generate_response(text, username, all_messages)
        
        if response:
            # Post to Rocket.Chat
            post_message(response)
            
            elapsed = time.time() - start_time
            log(f"⏱️ Total response time: {elapsed:.1f}s")
            
            # Notify Telegram (for visibility)
            send_to_telegram(
                f"🚀 *RC #{BOT_USERNAME}* responded to *{username}*:\n"
                f"Q: _{text[:100]}_\n"
                f"A: {response[:200]}\n"
                f"⏱️ {elapsed:.1f}s"
            )
        else:
            # Fallback: post acknowledgment
            post_message(f"Hey {username}, I received your message but had trouble generating a response. Let me try again or reach me on Telegram.")
            send_to_telegram(
                f"⚠️ *RC response failed* for *{username}*:\n_{text[:100]}_\n\nPlease respond manually."
            )
    finally:
        PROCESSING = False

# ── Main Loop ─────────────────────────────────────────────────────

def main():
    global LAST_MESSAGE_ID
    
    log("=" * 60)
    log("🚀 Rocket.Chat Auto-Responder v2 Started")
    log(f"📍 Polling #{GENERAL_ROOM_ID} every {POLL_INTERVAL}s")
    log(f"🧠 Using Claude Haiku for fast responses")
    log(f"📝 Logging to {LOG_FILE}")
    log("=" * 60)
    
    # Initialize: get current latest message ID so we don't respond to old messages
    messages = get_latest_messages(1)
    if messages:
        LAST_MESSAGE_ID = messages[0].get("_id")
        log(f"📌 Initialized at message ID: {LAST_MESSAGE_ID}")
    
    poll_count = 0
    while True:
        try:
            poll_count += 1
            messages = get_latest_messages(5)
            
            if messages:
                latest = messages[0]
                latest_id = latest.get("_id", "")
                username = latest.get("u", {}).get("username", "")
                
                # New message from a non-bot user?
                if latest_id != LAST_MESSAGE_ID and username != BOT_USERNAME:
                    LAST_MESSAGE_ID = latest_id
                    handle_message(latest, messages)
                elif latest_id != LAST_MESSAGE_ID:
                    # Our own message or system message — just update tracker
                    LAST_MESSAGE_ID = latest_id
            
            # Periodic status log (every 5 minutes)
            if poll_count % 300 == 0:
                log(f"💓 Listening... ({poll_count} polls, {poll_count * POLL_INTERVAL}s uptime)")
            
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            log("✋ Responder stopped by user")
            break
        except Exception as e:
            log(f"❌ Loop error: {e}")
            time.sleep(5)  # Back off on errors

if __name__ == "__main__":
    main()
