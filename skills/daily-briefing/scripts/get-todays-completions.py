#!/usr/bin/env python3
"""
Extract today's completions from memory/YYYY-MM-DD.md
"""

import os
import json
from datetime import datetime

def get_todays_completions():
    """Pull completions from today's memory file"""
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = os.path.expanduser(f"~/.openclaw/workspace/memory/{today}.md")
    
    completions = []
    
    if os.path.exists(memory_file):
        try:
            with open(memory_file, 'r') as f:
                content = f.read()
                
            # Extract lines that start with "- " as bullet points
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('- '):
                    # Extract the completion text
                    completion = line[2:].strip()
                    if completion:
                        completions.append(completion)
        except Exception as e:
            print(f"Error reading {memory_file}: {e}", file=__import__('sys').stderr)
    
    # If no completions found, return empty list (will show "No items recorded yet")
    return completions

def format_completions_html(completions):
    """Format completions as HTML items"""
    if not completions:
        return '<div class="item"><em>No completions recorded yet. Start by updating memory/YYYY-MM-DD.md with your work!</em></div>'
    
    html_items = []
    for completion in completions:
        html_items.append(f'<div class="item"><span class="success">✓</span> {completion}</div>')
    
    return '\n            '.join(html_items)

if __name__ == "__main__":
    completions = get_todays_completions()
    
    # Output as JSON for shell script to parse
    output = {
        "completions": completions,
        "count": len(completions),
        "html": format_completions_html(completions)
    }
    
    print(json.dumps(output))
