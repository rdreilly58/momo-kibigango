#!/usr/bin/env python3
"""
Rocket.Chat ↔ Claude Simple Webhook (no external dependencies)
Uses Python's built-in http.server instead of Flask
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests
import threading
from datetime import datetime
import sys

# Configuration
ROCKETCHAT_URL = "http://localhost:3000"
BOT_USER_ID = "NyTi2Ktzzv4Q6hDoL"
BOT_AUTH_TOKEN = "oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ"
GENERAL_ROOM_ID = "GENERAL"
WEBHOOK_PORT = 9999

RC_HEADERS = {
    "X-User-Id": BOT_USER_ID,
    "X-Auth-Token": BOT_AUTH_TOKEN,
    "Content-Type": "application/json"
}

def send_to_rocket_chat(text):
    """Post message to Rocket.Chat #general"""
    url = f"{ROCKETCHAT_URL}/api/v1/chat.postMessage"
    payload = {
        "roomId": GENERAL_ROOM_ID,
        "text": text
    }
    try:
        resp = requests.post(url, json=payload, headers=RC_HEADERS, timeout=10)
        if resp.status_code == 200 and resp.json().get("success"):
            print(f"✅ Posted to RC: {text[:50]}...")
            return True
    except Exception as e:
        print(f"❌ RC error: {e}")
    return False

class WebhookHandler(BaseHTTPRequestHandler):
    """Handle incoming webhooks"""
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode())
            
            if self.path == '/webhook/rocketchat-message':
                self.handle_rocket_chat_message(data)
            elif self.path == '/webhook/claude-response':
                self.handle_claude_response(data)
            else:
                self.send_error(404)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_error(500)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "running",
                "service": "Rocket.Chat ↔ Claude Webhook",
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404)
    
    def handle_rocket_chat_message(self, data):
        """Process message from Rocket.Chat"""
        try:
            message = data.get('data', {})
            text = message.get('msg', '')
            username = message.get('u', {}).get('username', '')
            room_id = message.get('rid', '')
            
            print(f"\n📨 RC Message from {username}: {text}")
            
            # Only process from bob_r in #general
            if username != "bob_r" or room_id != GENERAL_ROOM_ID:
                self.send_json({"status": "ignored"}, 200)
                return
            
            # Send acknowledgment
            send_to_rocket_chat(f"🤔 **Processing your question: {text}**")
            
            # Forward to Claude in background
            threading.Thread(
                target=self.forward_to_claude,
                args=(text,),
                daemon=True
            ).start()
            
            self.send_json({"status": "received"}, 200)
            
        except Exception as e:
            print(f"❌ Message error: {e}")
            self.send_error(500)
    
    def forward_to_claude(self, question):
        """Forward question to Claude"""
        try:
            # For now, post a message indicating it was forwarded
            response_msg = f"""✉️ **Message forwarded to Claude**
            
_Your question: "{question}"_

Claude will reply in this channel. Stand by...
"""
            send_to_rocket_chat(response_msg)
            
        except Exception as e:
            print(f"❌ Forward error: {e}")
    
    def handle_claude_response(self, data):
        """Post Claude response back to Rocket.Chat"""
        try:
            response_text = data.get('response') or data.get('text')
            
            if not response_text:
                self.send_error(400)
                return
            
            print(f"💬 Claude response: {response_text[:50]}...")
            
            # Format response with attribution
            formatted = f"""✅ **Claude's Response:**

{response_text}"""
            
            send_to_rocket_chat(formatted)
            self.send_json({"status": "posted"}, 200)
            
        except Exception as e:
            print(f"❌ Response error: {e}")
            self.send_error(500)
    
    def send_json(self, data, status_code):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def run_webhook_server():
    """Start webhook server"""
    server = HTTPServer(('127.0.0.1', WEBHOOK_PORT), WebhookHandler)
    print(f"🚀 Webhook server running on 127.0.0.1:{WEBHOOK_PORT}")
    print(f"📍 Endpoints:")
    print(f"   POST /webhook/rocketchat-message")
    print(f"   POST /webhook/claude-response")
    print(f"   GET  /status")
    print("=" * 50)
    server.serve_forever()

if __name__ == '__main__':
    run_webhook_server()
