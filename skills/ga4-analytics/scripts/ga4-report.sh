#!/bin/bash
# ga4-report.sh — Generate GA4 analytics reports
#
# Usage:
#   ga4-report.sh [COMMAND] [OPTIONS]
#   ga4-report.sh overview [--days 7]
#   ga4-report.sh devices [--days 7]
#   ga4-report.sh pages [--days 7]
#   ga4-report.sh traffic [--days 7]
#   ga4-report.sh custom --dimensions DATE --metrics SESSIONS

set -euo pipefail

# Load GA4 config
if [[ -f ~/.openclaw/workspace/config/ga4.env ]]; then
  source ~/.openclaw/workspace/config/ga4.env
fi

PROPERTY_ID="${GA4_PROPERTY_ID:-}"
COMMAND="${1:-overview}"
DAYS="${2:-7}"

if [[ -z "$PROPERTY_ID" ]]; then
  echo "[ga4] Error: GA4_PROPERTY_ID not set"
  echo "Run: bash setup-ga4.sh <PROPERTY_ID>"
  exit 1
fi

# Calculate date range
if [[ "$DAYS" == "today" ]]; then
  DATE_RANGE="today"
elif [[ "$DAYS" == "all" ]]; then
  DATE_RANGE="365daysAgo,today"
else
  DATE_RANGE="${DAYS}daysAgo,today"
fi

case "$COMMAND" in
  overview)
    echo "[ga4] Traffic Overview (Last $DAYS days)"
    gog analytics report \
      --property-id="$PROPERTY_ID" \
      --date-ranges="$DATE_RANGE" \
      --dimensions="date" \
      --metrics="sessions,users,newUsers,bounceRate,sessionDuration" \
      --plain
    ;;
  
  devices)
    echo "[ga4] Traffic by Device (Last $DAYS days)"
    gog analytics report \
      --property-id="$PROPERTY_ID" \
      --date-ranges="$DATE_RANGE" \
      --dimensions="deviceCategory" \
      --metrics="sessions,users,bounceRate" \
      --plain
    ;;
  
  pages)
    echo "[ga4] Traffic by Page (Last $DAYS days)"
    gog analytics report \
      --property-id="$PROPERTY_ID" \
      --date-ranges="$DATE_RANGE" \
      --dimensions="pagePath" \
      --metrics="sessions,users,bounceRate,avgSessionDuration" \
      --plain
    ;;
  
  traffic)
    echo "[ga4] Traffic Sources (Last $DAYS days)"
    gog analytics report \
      --property-id="$PROPERTY_ID" \
      --date-ranges="$DATE_RANGE" \
      --dimensions="source,medium" \
      --metrics="sessions,users,conversionRate" \
      --plain
    ;;
  
  events)
    echo "[ga4] Events/Conversions (Last $DAYS days)"
    gog analytics report \
      --property-id="$PROPERTY_ID" \
      --date-ranges="$DATE_RANGE" \
      --dimensions="eventName" \
      --metrics="eventCount,eventValue" \
      --plain
    ;;
  
  geo)
    echo "[ga4] Traffic by Country (Last $DAYS days)"
    gog analytics report \
      --property-id="$PROPERTY_ID" \
      --date-ranges="$DATE_RANGE" \
      --dimensions="country" \
      --metrics="sessions,users" \
      --plain
    ;;
  
  help|*)
    echo "Usage: ga4-report.sh [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  overview      - Traffic overview (sessions, users, bounce rate)"
    echo "  devices       - Traffic by device type"
    echo "  pages         - Traffic by page"
    echo "  traffic       - Traffic by source/medium"
    echo "  events        - Events and conversions"
    echo "  geo           - Traffic by country"
    echo ""
    echo "Options:"
    echo "  --days N      - Number of days to report (default: 7)"
    echo "  --days today  - Today only"
    echo "  --days all    - Last 365 days"
    echo ""
    echo "Examples:"
    echo "  ga4-report.sh overview"
    echo "  ga4-report.sh devices --days 30"
    echo "  ga4-report.sh traffic --days all"
    exit 0
    ;;
esac
