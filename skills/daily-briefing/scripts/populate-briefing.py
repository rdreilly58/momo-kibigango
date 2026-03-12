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

def get_ga4_data():
    """Fetch comprehensive GA4 analytics for last 7 days"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        property_id = "526836321"
        
        # Fetch comprehensive analytics
        cmd = f"python3 {script_dir}/ga4-query.py --property-id={property_id} --comprehensive 2>/dev/null"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                analytics_data = json.loads(result.stdout)
                
                # Format the HTML
                format_cmd = f"python3 {script_dir}/format-analytics.py"
                format_result = subprocess.run(
                    format_cmd, shell=True, input=json.dumps(analytics_data),
                    capture_output=True, text=True, timeout=5
                )
                
                if format_result.returncode == 0:
                    formatted = json.loads(format_result.stdout)
                    return {
                        "metrics_html": formatted.get("metrics_html", ""),
                        "sources_html": formatted.get("sources_html", ""),
                        "pages_html": formatted.get("pages_html", ""),
                        "raw": analytics_data
                    }
                
                # Fallback to raw data
                current = analytics_data.get("current_metrics", {})
                return {
                    "sessions": str(current.get("sessions", "—")),
                    "users": str(current.get("activeUsers", "—")),
                    "bounce": str(current.get("bounceRate", "—")),
                    "pages": []
                }
            except json.JSONDecodeError:
                pass
        
        # Fallback: return placeholder
        return {
            "sessions": "—",
            "users": "—", 
            "bounce": "—",
            "pages": []
        }
    except Exception as e:
        print(f"[GA4] Error: {e}", file=__import__('sys').stderr)
        return {"sessions": "—", "users": "—", "bounce": "—", "pages": []}

def get_gmail_data():
    """Fetch Gmail statistics"""
    try:
        # Get unread count
        cmd_unread = "gog gmail search 'is:unread' --json 2>/dev/null | jq '.threads | length'"
        result = subprocess.run(cmd_unread, shell=True, capture_output=True, text=True, timeout=10)
        unread = result.stdout.strip() if result.returncode == 0 else "--"
        
        # Get flagged count
        cmd_flagged = "gog gmail search 'is:starred' --json 2>/dev/null | jq '.threads | length'"
        result = subprocess.run(cmd_flagged, shell=True, capture_output=True, text=True, timeout=10)
        flagged = result.stdout.strip() if result.returncode == 0 else "--"
        
        return {"unread": unread, "flagged": flagged}
    except Exception as e:
        print(f"[Gmail] Error: {e}", file=__import__('sys').stderr)
        return {"unread": "--", "flagged": "--"}

def main():
    ga4 = get_ga4_data()
    gmail = get_gmail_data()
    
    # Extract summary metrics if we got HTML
    if "metrics_html" in ga4:
        ga4_summary = ga4.get("raw", {}).get("current_metrics", {})
        metrics = {
            "sessions": str(int(ga4_summary.get("sessions", 0))),
            "users": str(int(ga4_summary.get("activeUsers", 0))),
            "bounce": f"{float(ga4_summary.get('bounceRate', 0)):.1f}",
            "html": ga4.get("metrics_html", ""),
            "sources_html": ga4.get("sources_html", ""),
            "pages_html": ga4.get("pages_html", "")
        }
    else:
        metrics = ga4
    
    output = {
        "ga4": metrics,
        "gmail": gmail,
        "timestamp": datetime.now().isoformat()
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
