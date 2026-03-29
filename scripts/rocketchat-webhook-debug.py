#!/usr/bin/env python3
"""
Debug webhook to see if Rocket.Chat is calling it
Logs all incoming requests with full details
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

class DebugHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Log all POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"\n[{timestamp}] 🎯 WEBHOOK RECEIVED!")
        print(f"Path: {self.path}")
        print(f"Headers: {dict(self.headers)}")
        print(f"Body: {body}")
        
        try:
            data = json.loads(body)
            print(f"Parsed JSON: {json.dumps(data, indent=2)}")
        except:
            print("(Not JSON)")
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "received"}).encode())
    
    def do_GET(self):
        """Health check"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Debug webhook is running\n")
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 9999), DebugHandler)
    print("🔍 DEBUG WEBHOOK RUNNING ON PORT 9999")
    print("Waiting for Rocket.Chat to call: http://localhost:9999/rocket-chat")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ Stopped")
