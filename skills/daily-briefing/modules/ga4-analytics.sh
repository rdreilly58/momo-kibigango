#!/bin/bash
# GA4 Analytics Module for Morning Briefing
# Fetches and formats GA4 metrics for the briefing

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Fetch GA4 data
fetch_ga4_data() {
  local output_file=$1
  
  echo -e "${BLUE}📊 Fetching GA4 analytics...${NC}" >&2
  
  # Check if GA4 script exists
  if [ ! -f ~/.openclaw/workspace/scripts/ga4-query-simple.py ]; then
    echo "⚠️  GA4 script not found" >> "$output_file"
    return 1
  fi
  
  # Run GA4 query (7 day lookback)
  local ga4_output=$(python3 ~/.openclaw/workspace/scripts/ga4-query-simple.py --days=7 2>/dev/null)
  
  if [ -z "$ga4_output" ]; then
    echo "⚠️  GA4 query returned no data" >> "$output_file"
    return 1
  fi
  
  echo "$ga4_output" >> "$output_file"
  echo -e "${GREEN}✓ GA4 data retrieved${NC}" >&2
  return 0
}

# Format GA4 data for HTML briefing
format_ga4_html() {
  local ga4_data=$1
  
  cat << 'HTML_END'
<section style="margin: 20px 0; padding: 20px; background: #f0f8ff; border-left: 4px solid #0066cc;">
  <h2 style="color: #0066cc; margin-top: 0;">📊 Analytics (Last 7 Days)</h2>
  <pre style="background: #fff; padding: 15px; border-radius: 5px; overflow-x: auto;">
HTML_END
  
  echo "$ga4_data" | head -20  # Truncate for email
  
  cat << 'HTML_END'
  </pre>
  <p style="font-size: 12px; color: #666; margin-bottom: 0;">Data from Google Analytics 4</p>
</section>
HTML_END
}

# Main execution if called directly
if [ "$1" = "fetch" ]; then
  fetch_ga4_data "$2"
elif [ "$1" = "format-html" ]; then
  format_ga4_html "$2"
else
  echo "Usage: ga4-analytics.sh [fetch|format-html] <output_file>"
fi
