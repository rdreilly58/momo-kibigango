#!/usr/bin/env python3
"""
Morning Briefing Generator
Sends a daily morning briefing email with calendar, unread emails, and priorities.
"""

import subprocess
import json
from datetime import datetime, timedelta
import sys

def run_command(cmd):
    """Run shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return None

def get_calendar_events():
    """Fetch calendar events for next 48h."""
    today = datetime.now()
    from_date = today.isoformat()
    to_date = (today + timedelta(days=2)).isoformat()
    
    cmd = f'gog calendar events primary --from {from_date} --to {to_date} --json 2>/dev/null'
    output = run_command(cmd)
    
    if not output:
        return "No calendar events"
    
    try:
        events = json.loads(output)
        if not events:
            return "No calendar events"
        
        event_list = []
        for event in events[:5]:  # Limit to 5 events
            title = event.get('summary', 'Untitled')
            start = event.get('start', {})
            start_time = start.get('dateTime', start.get('date', '')).split('T')[0]
            event_list.append(f"  • {title} ({start_time})")
        
        return "\n".join(event_list) if event_list else "No calendar events"
    except:
        return "Could not parse calendar events"

def get_unread_count():
    """Get unread email count."""
    cmd = "gog gmail search 'is:unread' --max 1 2>/dev/null | wc -l"
    output = run_command(cmd)
    return output if output else "0"

def generate_briefing():
    """Generate the morning briefing content."""
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%I:%M %p %Z")
    
    calendar = get_calendar_events()
    unread = get_unread_count()
    
    body = f"""Good morning! ☀️

📅 {date_str} at {time_str}

📬 Email: {unread} unread messages

🗓️ Next 48 hours:
{calendar}

⭐ Today's Priorities:
  1. iOS development (WebSocket integration)
  2. Stripe environment setup & testing
  3. ReillyDesignStudio deployment monitoring

Have a productive day! 🍑
"""
    return body

def send_email(body):
    """Send the briefing email."""
    subject = f"☀️ Morning Briefing - {datetime.now().strftime('%A, %B %d')}"
    email = "rdreilly2010@gmail.com"
    
    # Escape quotes for shell
    body_escaped = body.replace('"', '\\"').replace('\n', '\\n')
    
    cmd = f'gog gmail send --to {email} --subject "{subject}" --body "{body_escaped}" --account {email} 2>/dev/null'
    output = run_command(cmd)
    
    if output and 'message_id' in output:
        return True
    return False

if __name__ == "__main__":
    try:
        body = generate_briefing()
        if send_email(body):
            print("✅ Morning briefing sent successfully")
            sys.exit(0)
        else:
            print("⚠️ Failed to send briefing email")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
