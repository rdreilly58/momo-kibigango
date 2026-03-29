#!/usr/bin/env python3
"""
Rocket.Chat ↔ Claude Webhook Integration
- Receives messages from Rocket.Chat #general
- Forwards to Claude via sessions_send
- Posts Claude responses back to Rocket.Chat
"""

from flask import Flask, request, jsonify
import requests
import json
import time
from datetime import datetime
from threading import Thread

app = Flask(__name__)

# Configuration
ROCKETCHAT_URL = "http://localhost:3000"
BOT_USER_ID = "NyTi2Ktzzv4Q6hDoL"
BOT_AUTH_TOKEN = "oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ"
GENERAL_ROOM_ID = "GENERAL"
WEBHOOK_PORT = 9999

# Headers for Rocket.Chat API
RC_HEADERS = {
    "X-User-Id": BOT_USER_ID,
    "X-Auth-Token": BOT_AUTH_TOKEN,
    "Content-Type": "application/json"
}

# Store pending messages awaiting Claude responses
PENDING_MESSAGES = {}

def send_to_rocket_chat(text, room_id):
    """Post message to Rocket.Chat"""
    url = f"{ROCKETCHAT_URL}/api/v1/chat.postMessage"
    payload = {
        "roomId": room_id,
        "text": text
    }
    try:
        resp = requests.post(url, json=payload, headers=RC_HEADERS, timeout=10)
        if resp.status_code == 200 and resp.json().get("success"):
            print(f"✅ Posted to Rocket.Chat: {text[:50]}...")
            return True
    except Exception as e:
        print(f"❌ Error posting to Rocket.Chat: {e}")
    return False

def send_to_momotaro(question, message_id):
    """
    Send message to Momotaro (Claude) via sessions_send.
    This runs in a background thread to not block the webhook response.
    """
    try:
        print(f"🤖 Forwarding to Claude: {question[:50]}...")
        
        # Call sessions_send to forward to main session (Momotaro/me in Telegram)
        # The response will come back as a separate message in Telegram
        # For now, we'll post a "thinking" message to Rocket.Chat
        
        send_to_rocket_chat(
            f"🤔 **Momotaro is thinking...**\n\n_Processing your question: {question[:50]}..._",
            GENERAL_ROOM_ID
        )
        
        # Store message ID for later response matching
        PENDING_MESSAGES[message_id] = {
            "question": question,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
    except Exception as e:
        print(f"❌ Error sending to Momotaro: {e}")
        send_to_rocket_chat(
            f"❌ Error: Could not reach Claude. {str(e)}",
            GENERAL_ROOM_ID
        )

@app.route('/webhook/rocketchat-message', methods=['POST'])
def handle_rocket_chat_webhook():
    """
    Webhook endpoint for Rocket.Chat messages.
    Rocket.Chat posts message events here.
    """
    try:
        data = request.json
        
        # Extract message details
        message = data.get('data', {})
        text = message.get('msg', '')
        username = message.get('u', {}).get('username', '')
        msg_id = message.get('_id', '')
        room_id = message.get('rid', '')
        
        print(f"\n📨 Webhook received from {username}: {text}")
        
        # Only process messages from bob_r in #general
        if username != "bob_r" or room_id != GENERAL_ROOM_ID:
            return jsonify({"status": "ignored"}), 200
        
        # Forward to Claude in background
        thread = Thread(target=send_to_momotaro, args=(text, msg_id))
        thread.daemon = True
        thread.start()
        
        return jsonify({"status": "received"}), 200
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/webhook/claude-response', methods=['POST'])
def handle_claude_response():
    """
    Endpoint for Claude responses.
    Can be called from Telegram or main agent to post response back to Rocket.Chat.
    """
    try:
        data = request.json
        response_text = data.get('response') or data.get('text')
        original_msg_id = data.get('original_message_id')
        
        if not response_text:
            return jsonify({"error": "No response text"}), 400
        
        print(f"💬 Claude response: {response_text[:50]}...")
        
        # Post to Rocket.Chat
        send_to_rocket_chat(response_text, GENERAL_ROOM_ID)
        
        # Mark as processed
        if original_msg_id in PENDING_MESSAGES:
            PENDING_MESSAGES[original_msg_id]["status"] = "completed"
        
        return jsonify({"status": "posted"}), 200
        
    except Exception as e:
        print(f"❌ Response error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "service": "Rocket.Chat ↔ Claude Webhook",
        "pending_messages": len(PENDING_MESSAGES),
        "timestamp": datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    print(f"🚀 Starting Rocket.Chat ↔ Claude Webhook Bridge")
    print(f"📍 Listening on 127.0.0.1:{WEBHOOK_PORT}")
    print(f"🎯 Endpoints:")
    print(f"   POST /webhook/rocketchat-message - Receives RC messages")
    print(f"   POST /webhook/claude-response    - Posts Claude responses")
    print(f"   GET  /status                     - Health check")
    print("=" * 50)
    
    app.run(host='127.0.0.1', port=WEBHOOK_PORT, debug=False)
