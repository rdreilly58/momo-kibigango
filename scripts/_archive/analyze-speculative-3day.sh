#!/bin/bash
# Analyze 3-Day Speculative Decoding Test
# Processes metrics and generates comprehensive report

set -euo pipefail

METRICS_FILE=~/.openclaw/logs/speculative-metrics.jsonl
REPORT_FILE=~/.openclaw/logs/speculative-3day-analysis.txt
GRAPH_DATA=~/.openclaw/logs/speculative-3day-data.csv

echo "Analyzing 3-day speculative decoding test..." >&2

if [ ! -f "$METRICS_FILE" ]; then
    echo "❌ No metrics file found at $METRICS_FILE"
    exit 1
fi

# Initialize report
cat > "$REPORT_FILE" << 'EOF'
╔════════════════════════════════════════════════════════════════════════════╗
║          3-DAY SPECULATIVE DECODING TEST — ANALYSIS REPORT                ║
║                        March 27-30, 2026                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

Generated: $(date)

EOF

echo "Generating statistics..." >&2

# Use Python for analysis (faster than bash)
python3 << 'PYTHON'
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

metrics_file = Path.home() / ".openclaw/logs" / "speculative-metrics.jsonl"
report_file = Path.home() / ".openclaw/logs" / "speculative-3day-analysis.txt"

# Parse metrics
records = []
with open(metrics_file, 'r') as f:
    for line in f:
        try:
            records.append(json.loads(line))
        except:
            pass

# Categorize records
generations = [r for r in records if r['type'] == 'generation']
requests = [r for r in records if r['type'] == 'request']
errors = [r for r in records if r['type'] == 'error']
server_events = [r for r in records if r['type'] in ['server_start', 'server_stop']]

# Calculate statistics
report = []

report.append("\n" + "="*80)
report.append("SUMMARY")
report.append("="*80)
report.append("")

report.append(f"Total Records: {len(records)}")
report.append(f"Generations: {len(generations)}")
report.append(f"Requests: {len(requests)}")
report.append(f"Errors: {len(errors)}")
report.append(f"Server Events: {len(server_events)}")
report.append("")

if generations:
    tokens_list = [g['tokens'] for g in generations]
    time_list = [g['time_s'] for g in generations]
    speed_list = [g['tok_s'] for g in generations]
    memory_list = [g['mem_gb'] for g in generations]
    
    total_tokens = sum(tokens_list)
    total_time = sum(time_list)
    
    report.append("="*80)
    report.append("GENERATION STATISTICS")
    report.append("="*80)
    report.append("")
    
    report.append(f"Total Generations: {len(generations)}")
    report.append(f"Total Tokens Generated: {total_tokens:,}")
    report.append(f"Total Time: {total_time:.1f} seconds ({total_time/3600:.2f} hours)")
    report.append(f"Average Tokens/Generation: {sum(tokens_list)/len(tokens_list):.1f}")
    report.append(f"Average Generation Time: {sum(time_list)/len(time_list):.2f} seconds")
    report.append("")
    
    report.append("SPEED ANALYSIS")
    report.append("-" * 80)
    report.append(f"Average Speed: {sum(speed_list)/len(speed_list):.2f} tok/sec")
    report.append(f"Min Speed: {min(speed_list):.2f} tok/sec")
    report.append(f"Max Speed: {max(speed_list):.2f} tok/sec")
    report.append(f"Median Speed: {sorted(speed_list)[len(speed_list)//2]:.2f} tok/sec")
    
    # Speed quartiles
    sorted_speed = sorted(speed_list)
    q1_idx = len(sorted_speed) // 4
    q3_idx = (3 * len(sorted_speed)) // 4
    report.append(f"Speed Q1: {sorted_speed[q1_idx]:.2f} tok/sec")
    report.append(f"Speed Q3: {sorted_speed[q3_idx]:.2f} tok/sec")
    report.append("")
    
    report.append("MEMORY USAGE")
    report.append("-" * 80)
    report.append(f"Average Memory: {sum(memory_list)/len(memory_list):.3f} GB")
    report.append(f"Min Memory: {min(memory_list):.3f} GB")
    report.append(f"Max Memory: {max(memory_list):.3f} GB")
    report.append("")
    
    report.append("THROUGHPUT")
    report.append("-" * 80)
    report.append(f"Tokens/Hour: {(total_tokens / (total_time/3600)):.0f}")
    report.append(f"Generations/Hour: {(len(generations) / (total_time/3600)):.1f}")
    report.append("")

if errors:
    report.append("="*80)
    report.append("ERRORS ({} total)".format(len(errors)))
    report.append("="*80)
    report.append("")
    
    error_types = defaultdict(int)
    for e in errors:
        error_msg = e.get('error', 'unknown')[:50]
        error_types[error_msg] += 1
    
    for error, count in sorted(error_types.items(), key=lambda x: -x[1]):
        report.append(f"  {count}x: {error}")
    report.append("")

report.append("="*80)
report.append("UPTIME & STABILITY")
report.append("="*80)
report.append("")

if server_events:
    starts = [r for r in server_events if r['type'] == 'server_start']
    stops = [r for r in server_events if r['type'] == 'server_stop']
    restarts = len(starts) - 1
    
    report.append(f"Server Starts: {len(starts)}")
    report.append(f"Server Stops: {len(stops)}")
    report.append(f"Restarts: {restarts}")
    
    if restarts == 0:
        report.append("✅ STABLE: No unexpected restarts")
    else:
        report.append(f"⚠️ {restarts} restart(s) detected")
    report.append("")

# Time range
if records:
    start_ts = records[0]['ts']
    end_ts = records[-1]['ts']
    duration = end_ts - start_ts
    
    report.append("="*80)
    report.append("TEST DURATION")
    report.append("="*80)
    report.append("")
    report.append(f"Start: {datetime.fromtimestamp(start_ts)}")
    report.append(f"End: {datetime.fromtimestamp(end_ts)}")
    report.append(f"Duration: {duration/3600:.1f} hours ({duration/86400:.1f} days)")
    report.append("")

report.append("="*80)
report.append("RECOMMENDATIONS")
report.append("="*80)
report.append("")

if generations:
    avg_speed = sum(speed_list) / len(speed_list)
    
    report.append("Based on observed performance:")
    report.append("")
    
    if avg_speed >= 15:
        report.append("✅ Performance exceeds expectations (>15 tok/sec)")
        report.append("   → Ready for production deployment")
        report.append("   → Consider Phase 3 GPU deployment for 5-10x speedup")
    elif avg_speed >= 10:
        report.append("✅ Performance meets expectations (~10 tok/sec)")
        report.append("   → Suitable for production use")
        report.append("   → GPU deployment would be beneficial")
    else:
        report.append("⚠️ Performance lower than expected (<10 tok/sec)")
        report.append("   → Investigate for bottlenecks")
        report.append("   → Consider GPU deployment for improvement")
    
    report.append("")
    
    if len(errors) == 0:
        report.append("✅ Error Rate: 0% (perfect reliability)")
        report.append("   → System is production-ready")
    elif len(errors) / len(generations) < 0.01:
        report.append(f"✅ Error Rate: <1% (excellent reliability)")
        report.append("   → System is production-ready")
    else:
        error_rate = (len(errors) / len(generations)) * 100
        report.append(f"⚠️ Error Rate: {error_rate:.1f}%")
        report.append("   → Investigate and address errors")

report.append("")
report.append("="*80)

# Write report
with open(report_file, 'a') as f:
    for line in report:
        f.write(line + '\n')

# Print to stdout
for line in report:
    print(line)

PYTHON

echo "" >&2
echo "✅ Analysis complete:" >&2
echo "   Report: $REPORT_FILE" >&2
echo "   Metrics: $METRICS_FILE" >&2
