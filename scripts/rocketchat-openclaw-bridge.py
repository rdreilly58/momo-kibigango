#!/usr/bin/env python3
"""
Rocket.Chat → Claude Bridge
Polls #general and DMs, responds via claude -p
"""

import requests
import json
import subprocess
import time
import sys
from datetime import datetime

# Track processed message IDs
PROCESSED_MESSAGES = set()
MAX_TRACKED = 500

# Config
ROCKETCHAT_URL = "http://localhost:3000"
BOT_USER_ID = "NyTi2Ktzzv4Q6hDoL"
BOT_AUTH_TOKEN = "oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ"
GENERAL_ROOM_ID = "GENERAL"
DM_ROOM_ID = "69c9017c2fa4cd8b432ac5ca"  # momotaro <-> bob-reilly
TARGET_USERNAME = "bob-reilly"

LOG_FILE = "/Users/rreilly/.openclaw/logs/rocketchat-responder.log"

RC_HEADERS = {
    "X-User-Id": BOT_USER_ID,
    "X-Auth-Token": BOT_AUTH_TOKEN,
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = (
    "You are Momo, Bob Reilly's personal AI assistant running inside Rocket.Chat. "
    "Be direct, concise, and genuinely helpful. Skip filler phrases. "
    "You have access to Bob's workspace and can help with coding, tasks, research, and more. "
    "Keep replies brief unless depth is needed."
)


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def get_messages(room_id, room_type="channel", limit=10):
    """Fetch recent messages from a channel or DM."""
    if room_type == "dm":
        url = f"{ROCKETCHAT_URL}/api/v1/im.messages?roomId={room_id}&count={limit}"
    else:
        url = f"{ROCKETCHAT_URL}/api/v1/channels.messages?roomId={room_id}&count={limit}"
    try:
        resp = requests.get(url, headers=RC_HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("messages", [])
    except Exception as e:
        log(f"❌ Error fetching messages from {room_id}: {e}")
    return []


def post_message(text, room_id):
    """Post a message to a Rocket.Chat room."""
    url = f"{ROCKETCHAT_URL}/api/v1/chat.postMessage"
    try:
        resp = requests.post(url, json={"roomId": room_id, "text": text},
                             headers=RC_HEADERS, timeout=10)
        if resp.status_code == 200 and resp.json().get("success"):
            log(f"✅ Posted to {room_id} ({len(text)} chars)")
            return True
        else:
            log(f"⚠️ Post failed {resp.status_code}: {resp.text[:100]}")
    except Exception as e:
        log(f"❌ Error posting: {e}")
    return False


def ask_claude(user_message):
    """Send a message to Claude via claude -p and return the response."""
    try:
        result = subprocess.run(
            ["/opt/homebrew/bin/claude", "-p", "--model", "haiku",
             "--append-system-prompt", SYSTEM_PROMPT,
             user_message],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        else:
            log(f"⚠️ Claude returned code {result.returncode}: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        log("⚠️ Claude timed out")
    except Exception as e:
        log(f"❌ Claude error: {e}")
    return None


def process_room(room_id, room_type="channel"):
    """Check a room for new messages and respond."""
    messages = get_messages(room_id, room_type=room_type)
    for msg in reversed(messages):  # oldest first
        msg_id = msg.get("_id", "")
        username = msg.get("u", {}).get("username", "")
        text = msg.get("msg", "").strip()

        if not text or msg_id in PROCESSED_MESSAGES:
            continue

        # Mark all seen messages as processed (including bot's own)
        PROCESSED_MESSAGES.add(msg_id)
        if len(PROCESSED_MESSAGES) > MAX_TRACKED:
            # Drop oldest 100
            old = list(PROCESSED_MESSAGES)[:100]
            for o in old:
                PROCESSED_MESSAGES.discard(o)

        if username != TARGET_USERNAME:
            continue

        log(f"📨 [{username}] ({room_type}): {text}")
        response = ask_claude(text)
        if response:
            log(f"🤖 Responding: {response[:80]}...")
            post_message(response, room_id)
        else:
            log("⚠️ No response generated")


def monitor_loop(interval=5):
    log("🚀 Rocket.Chat ↔ Claude Bridge started")
    log(f"   Polling #general + DMs every {interval}s")
    log(f"   Target user: {TARGET_USERNAME}")

    # Seed processed set with existing messages to avoid replying to old ones
    log("📋 Seeding processed messages (skipping history)...")
    for room_id, rtype in [(GENERAL_ROOM_ID, "channel"), (DM_ROOM_ID, "dm")]:
        msgs = get_messages(room_id, room_type=rtype, limit=20)
        for m in msgs:
            PROCESSED_MESSAGES.add(m.get("_id", ""))
    log(f"   Seeded {len(PROCESSED_MESSAGES)} existing message IDs")

    try:
        while True:
            process_room(GENERAL_ROOM_ID, "channel")
            process_room(DM_ROOM_ID, "dm")
            time.sleep(interval)
    except KeyboardInterrupt:
        log("⏹️  Bridge stopped")
        sys.exit(0)


if __name__ == "__main__":
    monitor_loop(interval=5)
