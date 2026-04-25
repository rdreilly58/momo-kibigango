#!/usr/bin/env python3
"""
Google Analytics Reporting API (v4) Query Script
Simpler alternative for fetching GA4 metrics
Usage: python3 ga4-query-simple.py [--days N]
"""

import os
import sys
import json
from datetime import datetime, timedelta

def get_sample_data():
    """Return sample GA4 data (until auth is fully set up)"""
    return {
        "timestamp": datetime.now().isoformat(),
        "period": "Last 7 days",
        "summary": {
            "users": 1250,
            "new_users": 340,
            "sessions": 2100,
            "bounce_rate": 32.5,
            "avg_session_duration": 245,
            "page_views": 8950,
        },
        "top_pages": [
            {"page": "/", "views": 2100, "users": 850},
            {"page": "/blog", "views": 1200, "users": 450},
            {"page": "/pricing", "views": 980, "users": 380},
            {"page": "/contact", "views": 450, "users": 200},
        ],
        "devices": [
            {"device": "mobile", "sessions": 1200, "percentage": 57.1},
            {"device": "desktop", "sessions": 750, "percentage": 35.7},
            {"device": "tablet", "sessions": 150, "percentage": 7.1},
        ],
        "countries": [
            {"country": "United States", "users": 650, "percentage": 52.0},
            {"country": "United Kingdom", "users": 180, "percentage": 14.4},
            {"country": "Canada", "users": 120, "percentage": 9.6},
            {"country": "Australia", "users": 90, "percentage": 7.2},
            {"country": "Other", "users": 210, "percentage": 16.8},
        ],
        "status": "demo_data",
        "note": "This is sample data. Full integration will populate real metrics once GA4 API access is configured."
    }

def format_report(data):
    """Format GA4 data for display"""
    
    output = []
    output.append("=" * 70)
    output.append("Google Analytics Report — " + data["period"])
    output.append("=" * 70)
    output.append("")
    
    # Summary metrics
    output.append("KEY METRICS")
    output.append("-" * 70)
    output.append(f"  Users:                 {data['summary']['users']:,}")
    output.append(f"  New Users:             {data['summary']['new_users']:,}")
    output.append(f"  Sessions:              {data['summary']['sessions']:,}")
    output.append(f"  Page Views:            {data['summary']['page_views']:,}")
    output.append(f"  Bounce Rate:           {data['summary']['bounce_rate']:.1f}%")
    output.append(f"  Avg Session Duration:  {data['summary']['avg_session_duration']} seconds")
    output.append("")
    
    # Top pages
    output.append("TOP PAGES")
    output.append("-" * 70)
    for page in data["top_pages"]:
        output.append(f"  {page['page']:30} {page['views']:5} views  {page['users']:4} users")
    output.append("")
    
    # Device breakdown
    output.append("DEVICES")
    output.append("-" * 70)
    for device in data["devices"]:
        output.append(f"  {device['device']:15} {device['sessions']:5} sessions ({device['percentage']:5.1f}%)")
    output.append("")
    
    # Top countries
    output.append("TOP COUNTRIES")
    output.append("-" * 70)
    for country in data["countries"]:
        output.append(f"  {country['country']:20} {country['users']:4} users ({country['percentage']:5.1f}%)")
    output.append("")
    
    # Status
    if data["status"] == "demo_data":
        output.append("📊 STATUS: Demo Data (awaiting full GA4 API configuration)")
        output.append("")
        output.append("To activate real GA4 data:")
        output.append("  1. Grant service account Editor access in GA4 property settings")
        output.append("  2. Enable Google Analytics Reporting API in GCP")
        output.append("  3. Verify credentials are installed (~/.gcp/credentials.json)")
    
    return "\n".join(output)

def main():
    """Main execution"""
    
    # Parse arguments
    days = 7
    json_mode = False
    for arg in sys.argv[1:]:
        if arg == "--json":
            json_mode = True
        elif arg.startswith("--days"):
            days = int(arg.split("=")[1])
    
    try:
        # Get data (sample for now)
        data = get_sample_data()
        
        if json_mode:
            print(json.dumps(data, indent=2))
        else:
            print(format_report(data))
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
