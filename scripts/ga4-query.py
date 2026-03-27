#!/usr/bin/env python3
"""
GA4 Analytics Query Script
Fetches traffic metrics, user behavior, and conversions from Google Analytics 4
Usage: python3 ga4-query.py [--days N] [--json]
"""

import os
import json
import sys
from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    Dimension,
    Metric,
    DateRange,
)

def get_credentials_path():
    """Get path to GCP credentials"""
    creds_path = os.path.expanduser("~/.gcp/credentials.json")
    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"Credentials not found at {creds_path}")
    return creds_path

def initialize_client():
    """Initialize GA4 Analytics client"""
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = get_credentials_path()
    return BetaAnalyticsDataClient()

def run_ga4_report(client, property_id, start_date, end_date):
    """Run GA4 report with key metrics"""
    
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[
            Dimension(name="date"),
            Dimension(name="country"),
            Dimension(name="deviceCategory"),
        ],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="newUsers"),
            Metric(name="sessions"),
            Metric(name="sessionDuration"),
            Metric(name="bounceRate"),
            Metric(name="screenPageViews"),
        ],
    )
    
    response = client.run_report(request)
    return response

def parse_report(response):
    """Parse GA4 report response into readable format"""
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_active_users": 0,
            "total_new_users": 0,
            "total_sessions": 0,
            "avg_session_duration": 0,
            "avg_bounce_rate": 0,
            "total_page_views": 0,
        },
        "by_country": {},
        "by_device": {},
        "daily": []
    }
    
    # Process each row
    for row in response.rows:
        dimensions = row.dimensions
        metrics = row.metric_values
        
        date_str = dimensions[0].value
        country = dimensions[1].value
        device = dimensions[2].value
        
        active_users = int(metrics[0].value or 0)
        new_users = int(metrics[1].value or 0)
        sessions = int(metrics[2].value or 0)
        session_duration = float(metrics[3].value or 0)
        bounce_rate = float(metrics[4].value or 0)
        page_views = int(metrics[5].value or 0)
        
        # Aggregate totals
        data["summary"]["total_active_users"] += active_users
        data["summary"]["total_new_users"] += new_users
        data["summary"]["total_sessions"] += sessions
        data["summary"]["total_page_views"] += page_views
        
        # By country
        if country not in data["by_country"]:
            data["by_country"][country] = {
                "users": 0,
                "sessions": 0,
                "views": 0
            }
        data["by_country"][country]["users"] += active_users
        data["by_country"][country]["sessions"] += sessions
        data["by_country"][country]["views"] += page_views
        
        # By device
        if device not in data["by_device"]:
            data["by_device"][device] = {
                "users": 0,
                "sessions": 0,
                "bounce_rate": 0
            }
        data["by_device"][device]["users"] += active_users
        data["by_device"][device]["sessions"] += sessions
        data["by_device"][device]["bounce_rate"] = bounce_rate
        
        # Daily
        data["daily"].append({
            "date": date_str,
            "users": active_users,
            "new_users": new_users,
            "sessions": sessions,
            "bounce_rate": bounce_rate,
            "page_views": page_views
        })
    
    # Calculate averages
    if len(response.rows) > 0:
        data["summary"]["avg_bounce_rate"] = sum(
            float(row.metric_values[4].value or 0) for row in response.rows
        ) / len(response.rows)
        data["summary"]["avg_session_duration"] = sum(
            float(row.metric_values[3].value or 0) for row in response.rows
        ) / len(response.rows)
    
    return data

def format_report(data):
    """Format GA4 data for display"""
    
    output = []
    output.append("=" * 60)
    output.append("GA4 Analytics Report")
    output.append("=" * 60)
    output.append("")
    
    # Summary
    output.append("SUMMARY")
    output.append("-" * 60)
    output.append(f"Active Users:        {data['summary']['total_active_users']}")
    output.append(f"New Users:           {data['summary']['total_new_users']}")
    output.append(f"Sessions:            {data['summary']['total_sessions']}")
    output.append(f"Page Views:          {data['summary']['total_page_views']}")
    output.append(f"Avg Session Duration: {data['summary']['avg_session_duration']:.0f}s")
    output.append(f"Avg Bounce Rate:     {data['summary']['avg_bounce_rate']:.1f}%")
    output.append("")
    
    # By country (top 5)
    output.append("TOP COUNTRIES")
    output.append("-" * 60)
    sorted_countries = sorted(
        data["by_country"].items(),
        key=lambda x: x[1]["users"],
        reverse=True
    )[:5]
    for country, stats in sorted_countries:
        output.append(f"{country:20} {stats['users']:6} users  {stats['sessions']:6} sessions")
    output.append("")
    
    # By device
    output.append("BY DEVICE")
    output.append("-" * 60)
    for device, stats in data["by_device"].items():
        output.append(f"{device:15} {stats['users']:6} users  {stats['bounce_rate']:.1f}% bounce")
    output.append("")
    
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
    
    # GA4 Property ID
    property_id = "526836321"
    
    # Date range
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    try:
        # Initialize client and run report
        print("📊 Fetching GA4 data...", file=sys.stderr)
        client = initialize_client()
        response = run_ga4_report(client, property_id, start_date, end_date)
        
        # Parse and format
        data = parse_report(response)
        
        if json_mode:
            print(json.dumps(data, indent=2))
        else:
            print(format_report(data))
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ GA4 query failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
