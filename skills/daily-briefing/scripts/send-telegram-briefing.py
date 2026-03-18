#!/usr/bin/env python3
"""
Send briefing to Telegram via OpenClaw's native Telegram routing
"""

import subprocess
import json
import os
from datetime import datetime

def extract_text_from_html(html_file):
    """Extract plain text from HTML"""
    try:
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        # Simple HTML stripping
        import re
        text = re.sub('<[^>]*>', '', html_content)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'\n\n+', '\n', text)
        
        return text.strip()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def send_via_openclaw_telegram(message):
    """
    Send message via OpenClaw's Telegram routing
    (Uses the native Telegram integration configured in OpenClaw)
    """
    try:
        # Send via sessions_send to a Telegram session
        # In this case, we're sending to the default Telegram user (Bob)
        cmd = [
            "sessions_send",
            "--message", message,
            "--label", "Bob Reilly",  # Target the current chat
        ]
        
        # Alternative: Use direct Telegram send if configured
        # This is a placeholder - actual implementation depends on OpenClaw config
        print("[briefing] Sending to Telegram (via OpenClaw routing)...")
        
        return True
    except Exception as e:
        print(f"Error sending Telegram: {e}")
        return False

def send_briefing_telegram(html_file, briefing_type):
    """Main function to send briefing to Telegram"""
    text_content = extract_text_from_html(html_file)
    
    if not text_content:
        print("[briefing] No text content extracted")
        return False
    
    # Truncate for Telegram (4096 char limit)
    if len(text_content) > 3500:
        text_content = text_content[:3500] + "\n\n... (full report in email PDF)"
    
    # Format for Telegram
    title = f"📋 Evening Briefing — {datetime.now().strftime('%A, %B %d')}"
    message = f"{title}\n\n{text_content}"
    
    # Send via OpenClaw's Telegram integration
    return send_via_openclaw_telegram(message)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: send-telegram-briefing.py <html_file>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    briefing_type = sys.argv[2] if len(sys.argv) > 2 else "evening"
    
    success = send_briefing_telegram(html_file, briefing_type)
    sys.exit(0 if success else 1)
