#!/usr/bin/env python3
"""
Simple Rocket.Chat Webhook Server - Uses only standard library
No Flask/external dependencies required
"""

import json
import logging
import requests
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import threading

# Configure logging
log_file = os.path.expanduser('~/.openclaw/logs/rocketchat-webhook.log')
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = '8755120444:AAHPuRzWMyLNPzSwkME8TmRQxUbj7Q1x1pE'
TELEGRAM_CHAT_ID = '8755120444'
WEBHOOK_TOKEN = 'rocketchat-webhook-secret'

def forward_to_telegram(username, text, channel):
    """Forward message to Telegram"""
    try:
        telegram_message = f"💬 **{channel}** - {username}:\n{text}"
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
            logger.error(f"❌ Telegram error: {resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Telegram error: {e}")
        return False

class WebhookHandler(BaseHTTPRequestHandler):
    """HTTP request handler for webhooks"""
    
    def log_message(self, format, *args):
        """Override to use logger"""
        logger.info(format % args)
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            # Check path
            if self.path != '/webhook/rocketchat-message':
                logger.warning(f"⚠️ Invalid path: {self.path}")
                self.send_response(404)
                self.end_headers()
                return
            
            # Check token
            token = self.headers.get('X-Rocket-Chat-Webhook-Token', '')
            if token != WEBHOOK_TOKEN:
                logger.warning(f"⚠️ Invalid webhook token")
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
                return
            
            # Read body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())
            
            logger.info(f"📨 Webhook received: {json.dumps(data, indent=2)}")
            
            # Extract message info
            username = data.get('user_name', 'unknown')
            text = data.get('text', '')
            channel = data.get('channel_name', '#general')
            
            # Skip internal messages
            if username == 'rocketchat.internal.admin.omnichannel':
                logger.info("⏭️  Skipping internal message")
            else:
                # Forward to Telegram
                forward_to_telegram(username, text, channel)
            
            # Return success
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = json.dumps({"success": True, "message": "Webhook processed"})
            self.wfile.write(response.encode())
            
            logger.info(f"✅ Webhook processed successfully")
        
        except Exception as e:
            logger.error(f"❌ Error processing webhook: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_GET(self):
        """Handle GET requests for health checks"""
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = json.dumps({
                "status": "healthy",
                "service": "Rocket.Chat Webhook Server",
                "timestamp": datetime.now().isoformat()
            })
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=9999):
    """Run the webhook server"""
    logger.info("=" * 60)
    logger.info("🚀 Rocket.Chat Webhook Server Starting")
    logger.info("=" * 60)
    logger.info(f"📍 Listening on http://0.0.0.0:{port}")
    logger.info(f"📨 Webhook endpoint: /webhook/rocketchat-message")
    logger.info(f"🤖 Telegram forwarding enabled")
    logger.info("=" * 60)
    
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, WebhookHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    try:
        run_server(9999)
    except KeyboardInterrupt:
        logger.info("⏹️  Server stopped")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)
