#!/usr/bin/env python3
"""
Rocket.Chat Webhook → Telegram Forwarder
Receives incoming webhooks from Rocket.Chat #general
Forwards messages to Telegram chat
Enables near real-time responses
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests
from datetime import datetime
import sys
import os

# Configuration
WEBHOOK_PORT = 9998
ROCKETCHAT_URL = "http://localhost:3000"
BOT_USER_ID = "NyTi2Ktzzv4Q6hDoL"
BOT_AUTH_TOKEN = "oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ"
GENERAL_ROOM_ID = "GENERAL"

# Telegram config (you'll provide these)
TELEGRAM_BOT_TOKEN = None  # Will be set from environment/file
TELEGRAM_CHAT_ID = 8755120444

RC_HEADERS = {
    "X-User-Id": BOT_USER_ID,
    "X-Auth-Token": BOT_AUTH_TOKEN,
    "Content-Type": "application/json"
}

class WebhookHandler(BaseHTTPRequestHandler):
    """Handle incoming Rocket.Chat webhooks"""
    
    def do_POST(self):
        """Handle POST requests from Rocket.Chat"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode())
            
            if self.path == '/rocket-chat':
                self.handle_rocketchat_webhook(data)
            else:
                self.send_error(404)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_error(500)
    
    def do_GET(self):
        """Health check"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_error(404)
    
    def handle_rocketchat_webhook(self, data):
        """Process webhook from Rocket.Chat"""
        try:
            # Extract message info
            text = data.get('text', '')
            username = data.get('user_name', '')
            channel = data.get('channel_name', '')
            
            print(f"\n📨 Webhook received from {username} in {channel}: {text}")
            
            # Only forward messages from bob_r in #general
            if username != 'bob_r' or channel != 'general':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ignored"}).encode())
                return
            
            # Forward to Telegram
            telegram_msg = f"""🚀 **Rocket.Chat #general**

{text}

_Waiting for response..._"""
            
            forward_to_telegram(telegram_msg)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "forwarded"}).encode())
            
        except Exception as e:
            print(f"❌ Webhook error: {e}")
            self.send_error(500)
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def forward_to_telegram(message):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ Telegram token not configured, skipping forward")
        return
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        resp = requests.post(url, json=payload, timeout=5)
        if resp.status_code == 200:
            print(f"✅ Forwarded to Telegram")
        else:
            print(f"⚠️ Telegram error: {resp.status_code}")
    except Exception as e:
        print(f"❌ Telegram forward failed: {e}")

def run_server():
    """Start webhook server"""
    server = HTTPServer(('127.0.0.1', WEBHOOK_PORT), WebhookHandler)
    print(f"🚀 Rocket.Chat Webhook Server Started")
    print(f"📍 Listening on 127.0.0.1:{WEBHOOK_PORT}")
    print(f"📍 Endpoint: POST /rocket-chat")
    print(f"📍 Health check: GET /health")
    print("=" * 50)
    print("\nNOTE: Configure Rocket.Chat webhook:")
    print("Admin → Integrations → Incoming Webhooks")
    print("Create webhook for #general with:")
    print("  URL: http://localhost:9998/rocket-chat")
    print("=" * 50)
    
    server.serve_forever()

if __name__ == '__main__':
    import os
    
    # Get Telegram token from environment or config file
    telegram_token = None
    
    # Try to read from file first
    try:
        with open(os.path.expanduser('~/.openclaw/telegram-bot-token'), 'r') as f:
            telegram_token = f.read().strip()
            print(f"✅ Telegram token loaded from file")
            TELEGRAM_BOT_TOKEN = telegram_token
    except:
        # Try environment variable
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if telegram_token:
            print(f"✅ Telegram token loaded from environment")
            TELEGRAM_BOT_TOKEN = telegram_token
        else:
            print(f"⚠️ Warning: No Telegram token configured")
            print(f"   Set TELEGRAM_BOT_TOKEN environment variable or")
            print(f"   Create ~/.openclaw/telegram-bot-token file")
    
    run_server()
