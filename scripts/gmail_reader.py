#!/usr/bin/env python3
"""
Gmail reader using Python's imaplib (no external dependencies)
Read, search, and download messages from Gmail IMAP
"""

import sys
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import json
from datetime import datetime
import os

class GmailReader:
    def __init__(self, email_addr, app_password):
        """
        Initialize Gmail IMAP connection
        email_addr: Gmail address
        app_password: Gmail App Password (not regular password)
        """
        self.email = email_addr
        self.app_password = app_password
        self.imap = None
        self.connect()
    
    def connect(self):
        """Connect to Gmail IMAP server"""
        try:
            self.imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
            self.imap.login(self.email, self.app_password)
            print(f"✓ Connected to Gmail: {self.email}")
        except Exception as e:
            print(f"✗ Connection failed: {e}", file=sys.stderr)
            raise
    
    def search(self, query):
        """Search emails using Gmail IMAP syntax"""
        try:
            self.imap.select('INBOX')
            status, message_ids = self.imap.search(None, query)
            if status == 'OK':
                return message_ids[0].split()
            return []
        except Exception as e:
            print(f"✗ Search failed: {e}", file=sys.stderr)
            return []
    
    def get_message(self, msg_id):
        """Fetch full message by ID"""
        try:
            status, msg_data = self.imap.fetch(msg_id, '(RFC822)')
            if status == 'OK':
                msg = email.message_from_bytes(msg_data[0][1])
                return msg
            return None
        except Exception as e:
            print(f"✗ Fetch failed: {e}", file=sys.stderr)
            return None
    
    def get_message_text(self, msg):
        """Extract text body from email message"""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        return part.get_payload(decode=True).decode('utf-8')
                    elif part.get_content_type() == 'text/html':
                        return part.get_payload(decode=True).decode('utf-8')
            else:
                return msg.get_payload(decode=True).decode('utf-8')
        except Exception as e:
            print(f"✗ Text extraction failed: {e}", file=sys.stderr)
            return None
    
    def list_messages(self, folder='INBOX', limit=10):
        """List recent messages"""
        try:
            self.imap.select(folder)
            status, message_ids = self.imap.search(None, 'ALL')
            if status == 'OK':
                ids = message_ids[0].split()[-limit:]  # Get last N
                messages = []
                for msg_id in reversed(ids):
                    msg = self.get_message(msg_id)
                    if msg:
                        messages.append({
                            'id': msg_id.decode() if isinstance(msg_id, bytes) else msg_id,
                            'subject': msg.get('Subject', ''),
                            'from': msg.get('From', ''),
                            'date': msg.get('Date', ''),
                        })
                return messages
            return []
        except Exception as e:
            print(f"✗ List failed: {e}", file=sys.stderr)
            return []
    
    def save_attachment(self, msg, filename, output_dir='.'):
        """Extract and save attachments"""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_disposition() == 'attachment':
                        fname = part.get_filename()
                        if fname:
                            filepath = os.path.join(output_dir, fname)
                            with open(filepath, 'wb') as f:
                                f.write(part.get_payload(decode=True))
                            return filepath
        except Exception as e:
            print(f"✗ Attachment save failed: {e}", file=sys.stderr)
        return None
    
    def close(self):
        """Close IMAP connection"""
        try:
            self.imap.close()
            self.imap.logout()
        except:
            pass

def main():
    if len(sys.argv) < 3:
        print("Usage: gmail_reader.py <email> <app_password> <command> [args]")
        print("\nCommands:")
        print("  search <query>     - Search emails")
        print("  list [folder]      - List recent emails")
        print("  read <msg_id>      - Read full message")
        print("  example            - Show example Gmail query syntax")
        sys.exit(1)
    
    email_addr = sys.argv[1]
    app_password = sys.argv[2]
    command = sys.argv[3] if len(sys.argv) > 3 else 'list'
    
    try:
        reader = GmailReader(email_addr, app_password)
        
        if command == 'search':
            query = ' '.join(sys.argv[4:]) if len(sys.argv) > 4 else 'ALL'
            msg_ids = reader.search(query)
            print(f"Found {len(msg_ids)} messages:")
            for msg_id in msg_ids[:10]:
                msg = reader.get_message(msg_id)
                if msg:
                    print(f"\n  ID: {msg_id.decode()}")
                    print(f"  Subject: {msg.get('Subject', '')}")
                    print(f"  From: {msg.get('From', '')}")
                    print(f"  Date: {msg.get('Date', '')}")
        
        elif command == 'list':
            folder = sys.argv[4] if len(sys.argv) > 4 else 'INBOX'
            messages = reader.list_messages(folder)
            print(f"\nLatest 10 messages from {folder}:")
            for msg_info in messages:
                print(f"\n  [{msg_info['id']}]")
                print(f"  Subject: {msg_info['subject']}")
                print(f"  From: {msg_info['from']}")
                print(f"  Date: {msg_info['date']}")
        
        elif command == 'read':
            msg_id = sys.argv[4].encode() if len(sys.argv) > 4 else None
            if msg_id:
                msg = reader.get_message(msg_id)
                if msg:
                    print(f"Subject: {msg.get('Subject', '')}")
                    print(f"From: {msg.get('From', '')}")
                    print(f"Date: {msg.get('Date', '')}")
                    print(f"\n--- Message Body ---\n")
                    text = reader.get_message_text(msg)
                    if text:
                        print(text[:2000])  # First 2000 chars
                    else:
                        print("(Could not extract text)")
        
        elif command == 'example':
            print("""
Gmail IMAP Search Query Examples:
  SUBJECT "text"      - Search subject line
  FROM "email"        - Search sender
  SINCE 1-Jan-2026    - After date
  BEFORE 1-Mar-2026   - Before date
  UNSEEN              - Unread messages
  ALL                 - All messages
  
Combined: SUBJECT "RDS Analytics" SINCE 7-Mar-2026 BEFORE 8-Mar-2026
""")
        
        reader.close()
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
