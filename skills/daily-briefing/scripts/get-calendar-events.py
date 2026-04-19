#!/usr/bin/env python3
"""
Get today's and tomorrow's calendar events
"""

import subprocess
import json
from datetime import datetime, timedelta

def get_calendar_events():
    """Fetch calendar events for next 48 hours"""
    events = []
    
    try:
        # Get calendar events
        cmd = 'gog calendar list -a rdreilly2010@gmail.com --json 2>/dev/null'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                if 'events' in data:
                    for event in data['events'][:5]:  # Next 5 events
                        events.append({
                            'title': event.get('summary', 'Untitled'),
                            'start': event.get('start', ''),
                            'location': event.get('location', '')
                        })
            except json.JSONDecodeError:
                pass
    except Exception as e:
        pass
    
    return events

def format_events_html(events):
    """Format calendar events as HTML"""
    if not events:
        return '<div class="item"><em>No events scheduled for today</em></div>'
    
    html = []
    for event in events:
        html.append(f'<div class="item">')
        html.append(f'<strong>{event["title"]}</strong>')
        
        # Format the start time nicely
        start = event.get('start', '')
        if isinstance(start, dict) and 'date' in start:
            # All-day event
            html.append(f'<br><span class="time">All day — {start["date"]}</span>')
        elif isinstance(start, dict) and 'dateTime' in start:
            # Timed event
            dt_str = start['dateTime']
            # Extract just the date and time part
            try:
                dt_part = dt_str.split('T')[0] + ' ' + dt_str.split('T')[1][:5]
                html.append(f'<br><span class="time">{dt_part}</span>')
            except:
                html.append(f'<br><span class="time">{start}</span>')
        elif start:
            html.append(f'<br><span class="time">{start}</span>')
        
        if event.get('location'):
            html.append(f'<br>📍 {event["location"]}')
        html.append(f'</div>')
    
    return '\n            '.join(html)

if __name__ == "__main__":
    events = get_calendar_events()
    html = format_events_html(events)
    
    output = {
        "events": events,
        "html": html
    }
    
    print(json.dumps(output))
