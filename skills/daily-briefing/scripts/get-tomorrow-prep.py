#!/usr/bin/env python3
"""
Get tomorrow's prep from memory and Things 3 todos
"""

import os
import json
import subprocess
from datetime import datetime, timedelta

def get_memory_todos():
    """Extract TODO/Next Steps from memory"""
    todos = []
    
    memory_file = os.path.expanduser("~/.openclaw/workspace/MEMORY.md")
    
    if os.path.exists(memory_file):
        try:
            with open(memory_file, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            in_todo_section = False
            for line in lines:
                if 'TODO' in line or 'Next' in line:
                    in_todo_section = True
                elif in_todo_section and line.startswith('- '):
                    todo_text = line[2:].strip()
                    if todo_text and not todo_text.startswith('['):
                        todos.append(todo_text)
                        if len(todos) >= 5:
                            break
        except Exception as e:
            pass
    
    return todos

def get_things_todos():
    """Fetch tomorrow's todos from Things 3"""
    todos = []
    
    try:
        # Get upcoming todos (next 3 days)
        cmd = "things upcoming --json 2>/dev/null | jq '.tasks[0:5] | .[] | {title, due}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            # Parse the output
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'title' in line or 'due' in line:
                    todos.append(line)
    except Exception as e:
        pass
    
    return todos

def format_prep_html(memory_todos):
    """Format tomorrow's prep as HTML"""
    html = []
    
    if memory_todos:
        for todo in memory_todos:
            html.append(f'<div class="item">• {todo}</div>')
    else:
        html.append('<div class="item"><em>Check MEMORY.md for upcoming work</em></div>')
    
    return '\n            '.join(html)

if __name__ == "__main__":
    memory_todos = get_memory_todos()
    things_todos = get_things_todos()
    html = format_prep_html(memory_todos)
    
    output = {
        "memory_todos": memory_todos,
        "things_todos": things_todos,
        "html": html
    }
    
    print(json.dumps(output))
