#!/usr/bin/env python3
"""
Rocket.Chat Webhook Server - Receives messages from Rocket.Chat and forwards to Telegram
Runs on localhost:9999 (inside Docker, this is accessible at 172.17.0.1:9999)
"""

import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
import requests
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/.openclaw/logs/rocketchat-webhook.log')),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
ROCKETCHAT_URL = "http://localhost:3000"
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8755120444:AAHPuRzWMyLNPzSwkME8TmRQxUbj7Q1x1pE')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '8755120444')
WEBHOOK_TOKEN = os.getenv('ROCKETCHAT_WEBHOOK_TOKEN', 'rocketchat-webhook-secret')
BOT_USER_ID = "NyTi2Ktzzv4Q6hDoL"
BOT_AUTH_TOKEN = "oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ"

RC_HEADERS = {
    "X-User-Id": BOT_USER_ID,
    "X-Auth-Token": BOT_AUTH_TOKEN,
    "Content-Type": "application/json"
}

def forward_to_telegram(message_data):
    """Forward Rocket.Chat message to Telegram"""
    try:
        username = message_data.get('u', {}).get('username', 'Unknown')
        text = message_data.get('msg', '')
        channel = message_data.get('room_name', '#general')
        
        # Format message for Telegram
        telegram_message = f"💬 **{channel}** - {username}:\n{text}"
        
        # Send to Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": telegram_message,
            "parse_mode": "Markdown"
        }
        
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            logger.info(f"✅ Forwarded to Telegram: {username} in {channel}")
            return True
        else:
            logger.error(f"❌ Telegram error: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Error forwarding to Telegram: {e}")
        return False

def post_response_to_rocketchat(response_text, room_id):
    """Post response back to Rocket.Chat"""
    try:
        url = f"{ROCKETCHAT_URL}/api/v1/chat.postMessage"
        payload = {
            "roomId": room_id,
            "text": response_text
        }
        
        resp = requests.post(url, json=payload, headers=RC_HEADERS, timeout=10)
        if resp.status_code == 200 and resp.json().get("success"):
            logger.info(f"✅ Posted response to Rocket.Chat")
            return True
        else:
            logger.error(f"❌ Failed to post to Rocket.Chat: {resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Error posting to Rocket.Chat: {e}")
        return False

@app.route('/webhook/rocketchat-message', methods=['POST'])
def webhook_receiver():
    """Receive webhook from Rocket.Chat"""
    try:
        logger.info("📨 Webhook endpoint hit!")
        
        # Verify webhook token
        token = request.headers.get('X-Rocket-Chat-Webhook-Token', '')
        logger.info(f"Token received: {token}")
        if token != WEBHOOK_TOKEN:
            logger.warning(f"⚠️ Invalid webhook token: {token}")
            return jsonify({"error": "Unauthorized"}), 401
        
        # Get webhook payload
        data = request.json
        logger.info(f"📨 Received webhook: {json.dumps(data, indent=2)}")
        
        # Extract message info
        message_data = {
            'u': data.get('user_obj', {}) or {'username': data.get('user_name', 'unknown')},
            'msg': data.get('text', ''),
            'room_name': data.get('channel_name', '#general'),
            'room_id': data.get('room_id', 'GENERAL'),
            '_id': data.get('message_id', '')
        }
        
        # Skip bot messages
        if message_data['u'].get('username') == 'rocketchat.internal.admin.omnichannel':
            logger.info("⏭️  Skipping internal bot message")
            return jsonify({"success": True}), 200
        
        # Forward to Telegram
        forward_to_telegram(message_data)
        
        # Log receipt
        logger.info(f"✅ Webhook processed: {message_data['u'].get('username')} -> {message_data['msg'][:100]}")
        
        return jsonify({"success": True, "message": "Webhook received and processed"}), 200
    
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

@app.route('/', methods=['GET', 'POST'])
def index():
    """Index page"""
    logger.info("✅ Index endpoint hit")
    return jsonify({
        "service": "Rocket.Chat Webhook Server",
        "status": "running",
        "endpoints": {
            "webhook": "/webhook/rocketchat-message",
            "health": "/health"
        }
    }), 200

def main():
    logger.info("=" * 60)
    logger.info("🚀 Rocket.Chat Webhook Server Starting")
    logger.info("=" * 60)
    logger.info(f"📍 Listening on http://0.0.0.0:9999")
    logger.info(f"📨 Webhook endpoint: /webhook/rocketchat-message")
    logger.info(f"🤖 Telegram forwarding enabled")
    logger.info("=" * 60)
    
    # Run Flask app
    app.run(host='0.0.0.0', port=9999, debug=False, threaded=True)

if __name__ == '__main__':
    main()
