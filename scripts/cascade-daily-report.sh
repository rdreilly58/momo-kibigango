#!/bin/bash
# Daily Cascade Decoder Performance Report
# Sends email with yesterday's (or today's) metrics to Bob
# Usage: cascade-daily-report.sh [YYYY-MM-DD]

set -e

DATE="${1:-$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d 'yesterday' +%Y-%m-%d)}"
METRICS_DIR="$HOME/.openclaw/logs/cascade-metrics"
LOG_FILE="$METRICS_DIR/${DATE}.jsonl"
REPORT_FILE="/tmp/cascade-report-${DATE}.html"
EMAIL="reillyrd58@gmail.com"

echo "[cascade-report] Generating report for $DATE"

if [ ! -f "$LOG_FILE" ]; then
    echo "[cascade-report] No metrics file for $DATE — no requests routed through cascade"
    # Still send a short report
    cat > "$REPORT_FILE" <<EOF
<html><body>
<h2>🍑 Momo-Kibidango Cascade Report — $DATE</h2>
<p><strong>No requests were routed through the cascade proxy today.</strong></p>
<p>The cascade service may not have been active, or all requests bypassed it.</p>
<p>Check: <code>launchctl list | grep cascade</code></p>
</body></html>
EOF
    gog gmail send -a reillyrd58@gmail.com \
        --to "$EMAIL" \
        --subject "🍑 Cascade Report — $DATE (no data)" \
        --body-file "$REPORT_FILE" 2>&1
    echo "[cascade-report] Sent (no data) report"
    exit 0
fi

# Count records
TOTAL=$(wc -l < "$LOG_FILE" | tr -d ' ')
ERRORS=$(grep -c '"tier_used": "error"' "$LOG_FILE" 2>/dev/null || echo 0)
SUCCESSFUL=$((TOTAL - ERRORS))

# Tier breakdown
HAIKU=$(grep -c '"tier_used": "haiku"' "$LOG_FILE" 2>/dev/null || echo 0)
SONNET=$(grep -c '"tier_used": "sonnet"' "$LOG_FILE" 2>/dev/null || echo 0)
OPUS=$(grep -c '"tier_used": "opus"' "$LOG_FILE" 2>/dev/null || echo 0)

# Cost analysis (using python for JSON parsing)
COST_DATA=$(python3 -c "
import json, sys
records = []
with open('$LOG_FILE') as f:
    for line in f:
        line = line.strip()
        if line:
            try: records.append(json.loads(line))
            except: pass

successful = [r for r in records if r.get('tier_used') != 'error']
total_cost = sum(r.get('cost_usd', 0) for r in successful)
total_input = sum(r.get('input_tokens', 0) for r in successful)
total_output = sum(r.get('output_tokens', 0) for r in successful)
opus_cost = (total_input * 15.0 + total_output * 75.0) / 1_000_000
savings = opus_cost - total_cost
savings_pct = (1 - total_cost / opus_cost) * 100 if opus_cost > 0 else 0
avg_latency = sum(r.get('latency_ms', 0) for r in successful) / len(successful) if successful else 0
avg_confidence = sum(r.get('confidence', 0) for r in successful) / len(successful) if successful else 0

print(f'{total_cost:.6f}')
print(f'{opus_cost:.6f}')
print(f'{savings:.6f}')
print(f'{savings_pct:.1f}')
print(f'{avg_latency:.0f}')
print(f'{avg_confidence:.2f}')
print(f'{total_input}')
print(f'{total_output}')
" 2>/dev/null)

TOTAL_COST=$(echo "$COST_DATA" | sed -n '1p')
OPUS_COST=$(echo "$COST_DATA" | sed -n '2p')
SAVINGS=$(echo "$COST_DATA" | sed -n '3p')
SAVINGS_PCT=$(echo "$COST_DATA" | sed -n '4p')
AVG_LATENCY=$(echo "$COST_DATA" | sed -n '5p')
AVG_CONFIDENCE=$(echo "$COST_DATA" | sed -n '6p')
TOTAL_INPUT=$(echo "$COST_DATA" | sed -n '7p')
TOTAL_OUTPUT=$(echo "$COST_DATA" | sed -n '8p')

# Generate HTML report
cat > "$REPORT_FILE" <<EOF
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
<h2 style="color: #333;">🍑 Momo-Kibidango Cascade Report</h2>
<h3 style="color: #666;">$DATE</h3>

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
<tr style="background: #f5f5f5;">
  <td style="padding: 10px; border: 1px solid #ddd;"><strong>Total Requests</strong></td>
  <td style="padding: 10px; border: 1px solid #ddd;">$TOTAL</td>
</tr>
<tr>
  <td style="padding: 10px; border: 1px solid #ddd;"><strong>Successful</strong></td>
  <td style="padding: 10px; border: 1px solid #ddd;">$SUCCESSFUL</td>
</tr>
<tr style="background: #f5f5f5;">
  <td style="padding: 10px; border: 1px solid #ddd;"><strong>Errors</strong></td>
  <td style="padding: 10px; border: 1px solid #ddd;">$ERRORS</td>
</tr>
</table>

<h3 style="color: #333;">Tier Breakdown</h3>
<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
<tr style="background: #e8f5e9;">
  <td style="padding: 10px; border: 1px solid #ddd;">⚡ <strong>Haiku</strong> (fast/cheap)</td>
  <td style="padding: 10px; border: 1px solid #ddd;">$HAIKU requests</td>
</tr>
<tr style="background: #fff3e0;">
  <td style="padding: 10px; border: 1px solid #ddd;">🔄 <strong>Sonnet</strong> (balanced)</td>
  <td style="padding: 10px; border: 1px solid #ddd;">$SONNET requests</td>
</tr>
<tr style="background: #fce4ec;">
  <td style="padding: 10px; border: 1px solid #ddd;">🧠 <strong>Opus</strong> (quality)</td>
  <td style="padding: 10px; border: 1px solid #ddd;">$OPUS requests</td>
</tr>
</table>

<h3 style="color: #333;">💰 Cost Analysis</h3>
<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
<tr style="background: #f5f5f5;">
  <td style="padding: 10px; border: 1px solid #ddd;"><strong>Actual Cost</strong></td>
  <td style="padding: 10px; border: 1px solid #ddd;">\$$TOTAL_COST</td>
</tr>
<tr>
  <td style="padding: 10px; border: 1px solid #ddd;"><strong>Opus-Only Cost</strong></td>
  <td style="padding: 10px; border: 1px solid #ddd;">\$$OPUS_COST</td>
</tr>
<tr style="background: #e8f5e9;">
  <td style="padding: 10px; border: 1px solid #ddd;"><strong>💰 Savings</strong></td>
  <td style="padding: 10px; border: 1px solid #ddd; color: green; font-weight: bold;">\$$SAVINGS (${SAVINGS_PCT}%)</td>
</tr>
</table>

<h3 style="color: #333;">📊 Performance</h3>
<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
<tr style="background: #f5f5f5;">
  <td style="padding: 10px; border: 1px solid #ddd;"><strong>Avg Latency</strong></td>
  <td style="padding: 10px; border: 1px solid #ddd;">${AVG_LATENCY}ms</td>
</tr>
<tr>
  <td style="padding: 10px; border: 1px solid #ddd;"><strong>Avg Confidence</strong></td>
  <td style="padding: 10px; border: 1px solid #ddd;">${AVG_CONFIDENCE}</td>
</tr>
<tr style="background: #f5f5f5;">
  <td style="padding: 10px; border: 1px solid #ddd;"><strong>Input Tokens</strong></td>
  <td style="padding: 10px; border: 1px solid #ddd;">${TOTAL_INPUT}</td>
</tr>
<tr>
  <td style="padding: 10px; border: 1px solid #ddd;"><strong>Output Tokens</strong></td>
  <td style="padding: 10px; border: 1px solid #ddd;">${TOTAL_OUTPUT}</td>
</tr>
</table>

<hr style="border: 1px solid #eee; margin: 20px 0;">
<p style="color: #999; font-size: 12px;">Generated by momo-kibidango v2.0.0 • 3-day trial (April 2-5, 2026)</p>
</body></html>
EOF

echo "[cascade-report] Report generated: $REPORT_FILE"

# Send email
gog gmail send -a reillyrd58@gmail.com \
    --to "$EMAIL" \
    --subject "🍑 Cascade Report — $DATE | ${SAVINGS_PCT}% savings | $TOTAL requests" \
    --body-file "$REPORT_FILE" 2>&1

echo "[cascade-report] ✅ Email sent to $EMAIL"
