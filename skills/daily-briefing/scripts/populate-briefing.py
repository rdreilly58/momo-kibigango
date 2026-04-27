#!/usr/bin/env python3
"""
Populate briefing data from GA4 and Gmail
Fetches:
- GA4 sessions, users, bounce rate, top pages
- Gmail unread count, flagged count
"""

import subprocess
import json
import os
from datetime import datetime, timedelta

# GA4 Property IDs for all sites
GA4_SITES = {
    "reillydesignstudio.com": "526836321",
    "momo-kiji.dev": "531031250",
    "momo-kibidango.org": "531033893",
}

def get_ga4_data_for_site(site_name, property_id):
    """Fetch GA4 analytics for a single site (last 7 days)"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Fetch comprehensive analytics
        cmd = f"python3 {script_dir}/ga4-query.py --property-id={property_id} --comprehensive 2>/dev/null"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                analytics_data = json.loads(result.stdout)
                current = analytics_data.get("current_metrics", {})
                return {
                    "site": site_name,
                    "sessions": str(int(current.get("sessions", 0))),
                    "users": str(int(current.get("activeUsers", 0))),
                    "bounce": f"{float(current.get('bounceRate', 0)):.1f}",
                    "raw": analytics_data
                }
            except (json.JSONDecodeError, ValueError):
                pass
        
        return {"site": site_name, "sessions": "0", "users": "0", "bounce": "—"}
    except Exception as e:
        print(f"[GA4:{site_name}] Error: {e}", file=__import__('sys').stderr)
        return {"site": site_name, "sessions": "0", "users": "0", "bounce": "—"}

def get_ga4_data():
    """Fetch GA4 analytics for ALL sites (last 7 days)"""
    all_sites = []
    total_sessions = 0
    total_users = 0
    
    for site_name, prop_id in GA4_SITES.items():
        data = get_ga4_data_for_site(site_name, prop_id)
        all_sites.append(data)
        try:
            total_sessions += int(data.get("sessions", 0))
            total_users += int(data.get("users", 0))
        except ValueError:
            pass
    
    # Build combined HTML for briefing
    sites_html = ""
    for s in all_sites:
        sites_html += f'<div class="item"><strong>{s["site"]}</strong>: {s["sessions"]} sessions, {s["users"]} users</div>\n'
    
    return {
        "sessions": str(total_sessions),
        "users": str(total_users),
        "bounce": "—",
        "html": sites_html,
        "sources_html": "",
        "pages_html": "",
        "sites": all_sites
    }

def get_gmail_data():
    """Fetch Gmail statistics"""
    try:
        # Get unread count
        cmd_unread = "gog gmail search -a rdreilly2010@gmail.com 'is:unread' --json 2>/dev/null | jq '.threads | length'"
        result = subprocess.run(cmd_unread, shell=True, capture_output=True, text=True, timeout=10)
        unread = result.stdout.strip() if result.returncode == 0 else "--"
        
        # Get flagged/starred count
        cmd_starred = "gog gmail search -a rdreilly2010@gmail.com 'is:starred' --json 2>/dev/null | jq '.threads | length'"
        result = subprocess.run(cmd_starred, shell=True, capture_output=True, text=True, timeout=10)
        starred = result.stdout.strip() if result.returncode == 0 else "--"
        
        # Get today's email count
        cmd_today = "gog gmail search -a rdreilly2010@gmail.com 'after:" + datetime.now().strftime('%Y-%m-%d') + "' --json 2>/dev/null | jq '.threads | length'"
        result = subprocess.run(cmd_today, shell=True, capture_output=True, text=True, timeout=10)
        today = result.stdout.strip() if result.returncode == 0 else "--"
        
        # Get urgent/important count
        cmd_urgent = "gog gmail search -a rdreilly2010@gmail.com 'is:important OR is:starred after:" + datetime.now().strftime('%Y-%m-%d') + "' --json 2>/dev/null | jq '.threads | length'"
        result = subprocess.run(cmd_urgent, shell=True, capture_output=True, text=True, timeout=10)
        urgent = result.stdout.strip() if result.returncode == 0 else "--"
        
        return {
            "unread": unread,
            "starred": starred,
            "today": today,
            "urgent": urgent
        }
    except Exception as e:
        print(f"[Gmail] Error: {e}", file=__import__('sys').stderr)
        return {"unread": "--", "starred": "--", "today": "--", "urgent": "--"}

def main():
    ga4 = get_ga4_data()
    gmail = get_gmail_data()
    
    output = {
        "ga4": ga4,
        "gmail": gmail,
        "timestamp": datetime.now().isoformat()
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
