#!/usr/bin/env python3
"""
Query GA4 Analytics API directly using service account credentials
Enhanced with traffic sources, top pages, and comparisons
"""

import json
import os
import sys

def query_ga4(property_id, start_date, end_date, dimensions=None, metrics=None, order_by=None, limit=None):
    """Query GA4 using REST API"""
    import requests
    from google.auth.transport.requests import Request
    from google.oauth2.service_account import Credentials
    
    creds_file = os.path.expanduser("~/.openclaw/workspace/secrets/ga4-service-account.json")
    
    if not os.path.exists(creds_file):
        print(f"Error: {creds_file} not found", file=sys.stderr)
        return None
    
    try:
        # Load and authenticate
        credentials = Credentials.from_service_account_file(
            creds_file,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"]
        )
        
        # Refresh token
        request = Request()
        credentials.refresh(request)
        token = credentials.token
        
        # Build request
        url = "https://analyticsdata.googleapis.com/v1beta/properties/" + property_id + ":runReport"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "dateRanges": [{"startDate": start_date, "endDate": end_date}],
            "dimensions": [{"name": d} for d in (dimensions or [])],
            "metrics": [{"name": m} for m in (metrics or [])]
        }
        
        if order_by:
            payload["orderBys"] = order_by
        
        if limit:
            payload["limit"] = str(limit)
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code != 200:
            error_detail = response.text
            print(f"GA4 Error ({response.status_code}): {error_detail}", file=sys.stderr)
            return None
        
        return response.json()
    
    except ImportError as e:
        print(f"Missing library: {e}. Install with: pip3 install --break-system-packages google-auth requests", 
              file=sys.stderr)
        return None
    except Exception as e:
        print(f"GA4 Error: {e}", file=sys.stderr)
        return None

def parse_simple_response(response):
    """Extract single row from GA4 response"""
    if not response or "rows" not in response:
        return None
    
    rows = response.get("rows", [])
    if not rows:
        return None
    
    result = {}
    metrics = response.get("metricHeaders", [])
    dimensions = response.get("dimensionHeaders", [])
    
    # Get first row
    row = rows[0]
    
    # Extract dimension values
    for i, dim in enumerate(dimensions):
        dim_name = dim.get("name", f"dim_{i}")
        result[dim_name] = row["dimensionValues"][i].get("value", "—")
    
    # Extract metric values
    for i, met in enumerate(metrics):
        met_name = met.get("name", f"metric_{i}")
        value = row["metricValues"][i].get("value", "—")
        try:
            if met_name in ["bounceRate", "conversionRate"]:
                result[met_name] = float(value)
            else:
                result[met_name] = int(value) if value != "—" else 0
        except:
            result[met_name] = value
    
    return result

def parse_multiple_rows(response):
    """Extract multiple rows from GA4 response"""
    if not response or "rows" not in response:
        return []
    
    rows = response.get("rows", [])
    metrics = response.get("metricHeaders", [])
    dimensions = response.get("dimensionHeaders", [])
    
    results = []
    for row in rows:
        result = {}
        
        # Extract dimensions
        for i, dim in enumerate(dimensions):
            dim_name = dim.get("name")
            result[dim_name] = row["dimensionValues"][i].get("value", "—")
        
        # Extract metrics
        for i, met in enumerate(metrics):
            met_name = met.get("name")
            value = row["metricValues"][i].get("value", "—")
            try:
                if met_name in ["bounceRate", "conversionRate"]:
                    result[met_name] = float(value)
                else:
                    result[met_name] = int(value) if value != "—" else 0
            except:
                result[met_name] = value
        
        results.append(result)
    
    return results

def get_comprehensive_analytics(property_id, period_days=7):
    """Fetch comprehensive GA4 analytics: key metrics, traffic sources, top pages, comparisons"""
    
    # Calculate dates
    end_date = "today"
    start_date = f"{period_days}daysAgo"
    compare_start = f"{period_days*2}daysAgo"
    compare_end = f"{period_days}daysAgo"
    
    # 1. Key metrics (current period vs previous)
    metrics_resp = query_ga4(
        property_id, start_date, end_date,
        dimensions=[],
        metrics=["activeUsers", "sessions", "bounceRate", "averageSessionDuration"]
    )
    
    compare_resp = query_ga4(
        property_id, compare_start, compare_end,
        dimensions=[],
        metrics=["activeUsers", "sessions"]
    )
    
    # 2. Traffic sources
    sources_resp = query_ga4(
        property_id, start_date, end_date,
        dimensions=["source"],
        metrics=["sessions", "activeUsers", "bounceRate"],
        limit=10
    )
    
    # 3. Top pages by pageviews
    pages_resp = query_ga4(
        property_id, start_date, end_date,
        dimensions=["pagePath"],
        metrics=["screenPageViews", "activeUsers", "averageSessionDuration"],
        limit=10
    )
    
    # Parse results
    current_metrics = parse_simple_response(metrics_resp) if metrics_resp else {}
    compare_metrics = parse_simple_response(compare_resp) if compare_resp else {}
    traffic_sources = parse_multiple_rows(sources_resp) if sources_resp else []
    top_pages = parse_multiple_rows(pages_resp) if pages_resp else []
    
    # Sort by metrics
    if traffic_sources:
        traffic_sources.sort(key=lambda x: x.get("sessions", 0), reverse=True)
    if top_pages:
        top_pages.sort(key=lambda x: x.get("screenPageViews", 0), reverse=True)
    
    # Calculate comparisons
    current_users = current_metrics.get("activeUsers", 0)
    compare_users = compare_metrics.get("activeUsers", 0)
    
    current_sessions = current_metrics.get("sessions", 0)
    compare_sessions = compare_metrics.get("sessions", 0)
    
    user_change = ((current_users - compare_users) / max(compare_users, 1)) * 100 if compare_users else 0
    session_change = ((current_sessions - compare_sessions) / max(compare_sessions, 1)) * 100 if compare_sessions else 0
    
    return {
        "period_days": period_days,
        "current_metrics": current_metrics,
        "compare_metrics": compare_metrics,
        "changes": {
            "user_change_percent": round(user_change, 1),
            "session_change_percent": round(session_change, 1)
        },
        "traffic_sources": traffic_sources,
        "top_pages": top_pages
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Query GA4 Analytics")
    parser.add_argument("--property-id", default="526836321", help="GA4 Property ID")
    parser.add_argument("--period", type=int, default=7, help="Period days for comparison (default 7)")
    parser.add_argument("--comprehensive", action="store_true", help="Fetch comprehensive analytics")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD or 'NdaysAgo')")
    parser.add_argument("--end-date", default="today", help="End date")
    parser.add_argument("--dimensions", help="Comma-separated dimensions")
    parser.add_argument("--metrics", help="Comma-separated metrics")
    
    args = parser.parse_args()
    
    if args.comprehensive:
        # Full analytics report
        data = get_comprehensive_analytics(args.property_id, args.period)
        print(json.dumps(data, indent=2))
    else:
        # Single query
        if not args.start_date:
            args.start_date = "yesterday"
        if not args.dimensions:
            args.dimensions = "date"
        if not args.metrics:
            args.metrics = "sessions,activeUsers,bounceRate"
        
        dimensions = [d.strip() for d in args.dimensions.split(",")]
        metrics = [m.strip() for m in args.metrics.split(",")]
        
        response = query_ga4(args.property_id, args.start_date, args.end_date, dimensions, metrics)
        
        if response:
            parsed = parse_simple_response(response)
            if parsed:
                print(json.dumps(parsed, indent=2))
