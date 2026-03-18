#!/usr/bin/env python3
"""
Get today's project progress from git commits and recent work
"""

import subprocess
import json
import os
from datetime import datetime

def get_git_commits_today():
    """Fetch git commits from today across key repos"""
    today = datetime.now().strftime("%Y-%m-%d")
    repos = [
        os.path.expanduser("~/reillydesignstudio"),
        os.path.expanduser("~/Projects/reillydesignstudio"),
        os.path.expanduser("~/momotaro-ios"),
    ]
    
    commits = {}
    
    for repo in repos:
        if not os.path.isdir(repo):
            continue
        
        try:
            # Get commits since today
            cmd = f"cd '{repo}' && git log --since='{today}' --until='tomorrow' --oneline --pretty=format:'%s' 2>/dev/null"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                repo_name = os.path.basename(repo)
                commits[repo_name] = result.stdout.strip().split('\n')
        except Exception as e:
            pass
    
    return commits

def get_project_status():
    """Get current project status"""
    projects = {
        "ReillyDesignStudio": {
            "status": "Live",
            "url": "https://www.reillydesignstudio.com",
            "notes": "GA4 tracking active, DNS configured"
        },
        "Momotaro": {
            "status": "In Progress",
            "notes": "iOS app development"
        }
    }
    return projects

def format_progress_html(commits, projects):
    """Format project progress as HTML"""
    html = []
    
    # Add git commits
    if commits:
        for repo, commit_list in commits.items():
            html.append(f'<div class="item">')
            html.append(f'<strong>{repo}</strong><br>')
            for commit in commit_list:
                html.append(f'<em>• {commit}</em><br>')
            html.append(f'</div>')
    
    # Add project status
    for project_name, project_info in projects.items():
        status_color = "#28a745" if project_info["status"] == "Live" else "#0099cc"
        html.append(f'<div class="item">')
        html.append(f'<strong>{project_name}</strong><br>')
        html.append(f'Status: <span style="color: {status_color}; font-weight: bold;">{project_info["status"]}</span>')
        if "url" in project_info:
            html.append(f'<br>URL: <a href="{project_info["url"]}">{project_info["url"]}</a>')
        if "notes" in project_info:
            html.append(f'<br><em>{project_info["notes"]}</em>')
        html.append(f'</div>')
    
    if not html:
        html.append('<div class="item"><em>No project updates today</em></div>')
    
    return '\n            '.join(html)

if __name__ == "__main__":
    commits = get_git_commits_today()
    projects = get_project_status()
    html = format_progress_html(commits, projects)
    
    output = {
        "commits": commits,
        "projects": projects,
        "html": html
    }
    
    print(json.dumps(output))
