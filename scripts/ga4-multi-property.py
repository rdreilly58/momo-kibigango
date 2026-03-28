#!/usr/bin/env python3
"""
GA4 Multi-Property Analytics Query
Fetches metrics across multiple GA4 properties in one report
Usage: python3 ga4-multi-property.py [--days N] [--json] [--format csv|json|text]
"""

import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import argparse

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        RunReportRequest,
        Dimension,
        Metric,
        DateRange,
    )
    GA4_AVAILABLE = True
except ImportError:
    GA4_AVAILABLE = False
    print("⚠️ Google Analytics client not installed. Install with:")
    print("   pip install google-analytics-data")

# GA4 Property Configuration
GA4_PROPERTIES = {
    "reillydesignstudio": {
        "property_id": "529199158",
        "domain": "reillydesignstudio.com",
        "description": "Robert Reilly Design Studio",
    },
    "momo-kij": {
        "property_id": "536826321",
        "domain": "momo-kij.vercel.app",
        "description": "Momotaro Kiji (Blog)",
    },
}

def get_credentials_path():
    """Get path to GCP credentials"""
    creds_path = os.path.expanduser("~/.gcp/credentials.json")
    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"Credentials not found at {creds_path}")
    return creds_path

def initialize_client():
    """Initialize GA4 Analytics client"""
    if not GA4_AVAILABLE:
        raise ImportError("Google Analytics client not available")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = get_credentials_path()
    return BetaAnalyticsDataClient()

def run_ga4_report(client, property_id, start_date, end_date):
    """Run GA4 report with key metrics"""
    
    try:
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
    except Exception as e:
        raise RuntimeError(f"GA4 API error: {e}")

def aggregate_metrics(responses):
    """Aggregate metrics from multiple properties"""
    
    aggregated = {
        "total_users": 0,
        "total_new_users": 0,
        "total_sessions": 0,
        "total_page_views": 0,
        "properties": {},
    }
    
    for prop_name, response in responses.items():
        prop_data = {
            "users": 0,
            "new_users": 0,
            "sessions": 0,
            "page_views": 0,
            "bounce_rate": 0,
            "avg_session_duration": 0,
        }
        
        row_count = 0
        total_duration = 0
        
        for row in response.rows:
            row_count += 1
            # Parse metrics
            metrics = row.metric_values
            if len(metrics) >= 6:
                users = int(metrics[0].value or 0)
                new_users = int(metrics[1].value or 0)
                sessions = int(metrics[2].value or 0)
                duration = float(metrics[3].value or 0)
                bounce = float(metrics[4].value or 0)
                page_views = int(metrics[5].value or 0)
                
                prop_data["users"] += users
                prop_data["new_users"] += new_users
                prop_data["sessions"] += sessions
                prop_data["page_views"] += page_views
                total_duration += duration
        
        if row_count > 0:
            prop_data["avg_session_duration"] = total_duration / row_count
        
        aggregated["properties"][prop_name] = prop_data
        aggregated["total_users"] += prop_data["users"]
        aggregated["total_new_users"] += prop_data["new_users"]
        aggregated["total_sessions"] += prop_data["sessions"]
        aggregated["total_page_views"] += prop_data["page_views"]
    
    return aggregated

def format_text_report(aggregated):
    """Format as human-readable text"""
    
    output = []
    output.append("=" * 80)
    output.append("GA4 ANALYTICS — MULTI-PROPERTY REPORT")
    output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("=" * 80)
    output.append("")
    
    output.append("AGGREGATE METRICS (All Properties)")
    output.append("-" * 80)
    output.append(f"Total Users:           {aggregated['total_users']:,}")
    output.append(f"Total New Users:       {aggregated['total_new_users']:,}")
    output.append(f"Total Sessions:        {aggregated['total_sessions']:,}")
    output.append(f"Total Page Views:      {aggregated['total_page_views']:,}")
    output.append("")
    
    output.append("PER-PROPERTY BREAKDOWN")
    output.append("-" * 80)
    
    for prop_name, config in GA4_PROPERTIES.items():
        if prop_name not in aggregated["properties"]:
            continue
        
        data = aggregated["properties"][prop_name]
        output.append(f"\n{config['description']} ({config['domain']})")
        output.append(f"  Users:        {data['users']:>6}")
        output.append(f"  New Users:    {data['new_users']:>6}")
        output.append(f"  Sessions:     {data['sessions']:>6}")
        output.append(f"  Page Views:   {data['page_views']:>6}")
        output.append(f"  Avg Duration: {data['avg_session_duration']:>6.1f}s")
    
    output.append("")
    output.append("=" * 80)
    
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description="GA4 Multi-Property Analytics")
    parser.add_argument("--days", type=int, default=7, help="Days to report (default: 7)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--format", choices=["text", "json", "csv"], default="text")
    args = parser.parse_args()
    
    # Calculate date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=args.days)
    
    try:
        if not GA4_AVAILABLE:
            print("⚠️ Google Analytics API not available (demo mode)")
            print("\nTo enable real data:")
            print("  1. Install: pip install google-analytics-data")
            print("  2. Verify credentials: ~/.gcp/credentials.json")
            print("  3. Update property IDs in this script")
            return
        
        print(f"Fetching GA4 data ({start_date} to {end_date})...", file=sys.stderr)
        
        client = initialize_client()
        responses = {}
        
        # Query each property
        for prop_name, config in GA4_PROPERTIES.items():
            try:
                print(f"  • {config['description']}...", file=sys.stderr)
                response = run_ga4_report(
                    client,
                    config["property_id"],
                    str(start_date),
                    str(end_date),
                )
                responses[prop_name] = response
            except Exception as e:
                print(f"  ✗ Error querying {prop_name}: {e}", file=sys.stderr)
        
        # Aggregate and format
        aggregated = aggregate_metrics(responses)
        
        if args.format == "json" or args.json:
            print(json.dumps(aggregated, indent=2))
        else:
            print(format_text_report(aggregated))
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
