#!/usr/bin/env python3
"""
Extract today's priorities from MEMORY.md
"""

import os
import json

def get_todays_priorities():
    """Extract priority items from MEMORY.md"""
    priorities = []
    
    memory_file = os.path.expanduser("~/.openclaw/workspace/MEMORY.md")
    
    if os.path.exists(memory_file):
        try:
            with open(memory_file, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            in_priority_section = False
            for line in lines:
                # Look for priority sections
                if 'Priority' in line or 'Focus' in line or 'Goals' in line:
                    in_priority_section = True
                elif in_priority_section and line.startswith('- '):
                    priority_text = line[2:].strip()
                    if priority_text:
                        priorities.append(priority_text)
                        if len(priorities) >= 5:
                            break
                elif in_priority_section and not line.startswith('- '):
                    in_priority_section = False
        except Exception as e:
            pass
    
    # Fallback priorities if none found
    if not priorities:
        priorities = [
            "Review email and urgent messages",
            "Continue Momotaro iOS development",
            "Check ReillyDesignStudio analytics",
            "Follow up on pending tasks"
        ]
    
    return priorities

def format_priorities_html(priorities):
    """Format priorities as HTML"""
    if not priorities:
        return '<div class="item"><em>No priorities set. Update MEMORY.md to define daily goals.</em></div>'
    
    html = []
    for i, priority in enumerate(priorities, 1):
        html.append(f'<div class="item">{i}. {priority}</div>')
    
    return '\n            '.join(html)

if __name__ == "__main__":
    priorities = get_todays_priorities()
    html = format_priorities_html(priorities)
    
    output = {
        "priorities": priorities,
        "html": html
    }
    
    print(json.dumps(output))
