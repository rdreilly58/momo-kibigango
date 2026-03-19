#!/usr/bin/env python3
"""
Get Google Tasks for daily briefing.
Returns pending task count and top 5 task titles.
"""

import subprocess
import json
import sys

TASKLIST_ID = "MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow"
ACCOUNT = "rdreilly2010@gmail.com"

def get_tasks():
    """Fetch tasks from Google Tasks via gog CLI."""
    try:
        result = subprocess.run(
            ["gog", "tasks", "list", TASKLIST_ID, "-a", ACCOUNT, "--json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print(json.dumps({
                "error": f"gog command failed: {result.stderr}",
                "pending_count": 0,
                "tasks": []
            }))
            return
        
        data = json.loads(result.stdout)
        
        # Filter pending tasks
        pending_tasks = [
            task for task in data.get("tasks", [])
            if task.get("status") == "needsAction"
        ]
        
        # Format output
        output = {
            "pending_count": len(pending_tasks),
            "total_count": len(data.get("tasks", [])),
            "tasks": [
                {
                    "title": task.get("title", "Untitled").strip(),
                    "id": task.get("id"),
                    "due": task.get("due")
                }
                for task in pending_tasks[:5]  # Top 5
            ]
        }
        
        print(json.dumps(output, indent=2))
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            "error": f"JSON parse error: {e}",
            "pending_count": 0,
            "tasks": []
        }))
    except subprocess.TimeoutExpired:
        print(json.dumps({
            "error": "Command timeout",
            "pending_count": 0,
            "tasks": []
        }))
    except Exception as e:
        print(json.dumps({
            "error": f"Unexpected error: {e}",
            "pending_count": 0,
            "tasks": []
        }))

if __name__ == "__main__":
    get_tasks()
