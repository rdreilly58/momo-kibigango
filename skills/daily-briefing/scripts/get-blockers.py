#!/usr/bin/env python3
"""
Extract blockers from memory and GitHub issues
"""

import os
import json
import subprocess
from datetime import datetime

def get_memory_blockers():
    """Extract blocker items from memory files"""
    blockers = []
    
    # Check today's memory file for "⚠️" or "Blocker" sections
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = os.path.expanduser(f"~/.openclaw/workspace/memory/{today}.md")
    
    if os.path.exists(memory_file):
        try:
            with open(memory_file, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '⚠️' in line or 'Blocker' in line or 'Issue' in line:
                    blocker_text = line.strip().lstrip('- ⚠️ ')
                    if blocker_text:
                        blockers.append(blocker_text)
        except Exception as e:
            pass
    
    return blockers

def get_github_issues():
    """Fetch open GitHub issues (limited to assigned to user)"""
    issues = []
    repos = [
        "rdreilly58/reillydesignstudio",
        "rdreilly58/momotaro-ios"
    ]
    
    for repo in repos:
        try:
            cmd = f"gh issue list --repo {repo} --assignee @me --state open --limit 3 --json title,url,labels 2>/dev/null"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                issue_data = json.loads(result.stdout)
                for issue in issue_data:
                    issues.append({
                        "repo": repo,
                        "title": issue.get("title", ""),
                        "url": issue.get("url", "")
                    })
        except Exception as e:
            pass
    
    return issues

def format_blockers_html(memory_blockers, github_issues):
    """Format blockers as HTML"""
    html = []
    
    if memory_blockers:
        for blocker in memory_blockers:
            html.append(f'<div class="item"><span class="warning">⚠️</span> {blocker}</div>')
    
    if github_issues:
        html.append('<div class="item"><span class="warning">GitHub Issues:</span></div>')
        for issue in github_issues:
            html.append(f'<div class="item" style="padding-left: 20px;"><a href="{issue["url"]}">{issue["title"]}</a> ({issue["repo"]})</div>')
    
    if not html:
        html.append('<div class="item"><em>No active blockers</em></div>')
    
    return '\n            '.join(html)

if __name__ == "__main__":
    memory_blockers = get_memory_blockers()
    github_issues = get_github_issues()
    html = format_blockers_html(memory_blockers, github_issues)
    
    output = {
        "memory_blockers": memory_blockers,
        "github_issues": github_issues,
        "html": html
    }
    
    print(json.dumps(output))
