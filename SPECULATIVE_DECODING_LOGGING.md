# Speculative Decoding — Lightweight Logging System

**Purpose:** Track performance metrics during 3-day test with minimal overhead  
**Format:** JSONL (JSON Lines) — one record per line, instant writes, no parsing overhead  
**File:** `~/.openclaw/logs/speculative-metrics.jsonl`

## Design Principles

### Lightweight
- ✅ **Asynchronous writes** — Batch 10 records, then flush (non-blocking)
- ✅ **Minimal data** — Only essential metrics, no full request/response
- ✅ **No file locking** — Append-only, concurrent writes safe
- ✅ **Small records** — ~100 bytes per generation record

### Comprehensive
- ✅ **Request tracking** — Prompt length, max tokens, draft length
- ✅ **Generation metrics** — Tokens, time, speed, memory
- ✅ **Error logging** — Errors for reliability analysis
- ✅ **Server events** — Start/stop for uptime calculation

## Record Types

### generation (1 per request)
```json
{
  "type": "generation",
  "ts": 1711527600.123,
  "tokens": 98,
  "time_s": 8.5,
  "tok_s": 11.5,
  "mem_gb": 0.95
}
```

**Fields:**
- `type`: "generation"
- `ts`: Unix timestamp (float)
- `tokens`: Tokens generated
- `time_s`: Time taken (seconds, rounded to 3 decimals)
- `tok_s`: Throughput (tokens/sec, rounded to 2 decimals)
- `mem_gb`: Memory used (GB, rounded to 3 decimals)

### request (1 per API call)
```json
{
  "type": "request",
  "ts": 1711527600.123,
  "prompt_len": 145,
  "max_tokens": 150,
  "draft_len": 4
}
```

**Fields:**
- `type`: "request"
- `ts`: Unix timestamp
- `prompt_len`: Length of input prompt
- `max_tokens`: Maximum tokens requested
- `draft_len`: Draft model speculation length

### error (0+ per session)
```json
{
  "type": "error",
  "ts": 1711527600.123,
  "error": "CUDA out of memory"
}
```

**Fields:**
- `type`: "error"
- `ts`: Unix timestamp
- `error`: Error message (truncated to 200 chars)

### server_start / server_stop (once each)
```json
{
  "type": "server_start",
  "ts": 1711527600.123
}
```

## Performance Impact

**Overhead per generation:**
- Logging call: <1 microsecond
- Batch append: ~0.1 milliseconds (amortized, 1 per 10 generations)
- Total impact: **<0.1% of generation time**

**Storage:**
- ~100 bytes per generation
- ~1,000 bytes per request-generation pair
- Estimated 3-day test: ~10,000 generations = 1-2 MB

## How to Use

### View logs in real-time
```bash
tail -f ~/.openclaw/logs/speculative-metrics.jsonl
```

### Count records
```bash
wc -l ~/.openclaw/logs/speculative-metrics.jsonl
```

### Find errors
```bash
grep '"error"' ~/.openclaw/logs/speculative-metrics.jsonl
```

### Extract speed over time
```bash
grep '"generation"' ~/.openclaw/logs/speculative-metrics.jsonl | \
  jq -r '[.ts, .tok_s] | @csv' | \
  sort -n | \
  awk -F, '{print $1, $2}'
```

### Get generation count
```bash
grep -c '"generation"' ~/.openclaw/logs/speculative-metrics.jsonl
```

## Analysis (After 3 Days)

### Automatic Analysis
```bash
bash ~/.openclaw/workspace/scripts/analyze-speculative-3day.sh
```

This generates a comprehensive report with:
- Total generations and tokens
- Speed statistics (avg, min, max, quartiles)
- Memory usage analysis
- Error rate and types
- Uptime and stability metrics
- Recommendations

### Manual Analysis

**Python script to parse logs:**
```python
import json
from pathlib import Path

metrics_file = Path.home() / ".openclaw/logs" / "speculative-metrics.jsonl"

generations = []
with open(metrics_file, 'r') as f:
    for line in f:
        record = json.loads(line)
        if record['type'] == 'generation':
            generations.append(record)

# Calculate statistics
speeds = [g['tok_s'] for g in generations]
print(f"Average speed: {sum(speeds)/len(speeds):.2f} tok/sec")
print(f"Min speed: {min(speeds):.2f} tok/sec")
print(f"Max speed: {max(speeds):.2f} tok/sec")
```

## Log Files

### Main Metrics
- **File:** `~/.openclaw/logs/speculative-metrics.jsonl`
- **Format:** JSON Lines (one JSON object per line)
- **Size:** ~1-2 MB for 3-day test
- **Read mode:** Append-only, safe concurrent access

### Server Logs
- **File:** `~/.openclaw/logs/speculative-decoding.log`
- **Purpose:** Standard Python logging (errors, startup messages)
- **Size:** ~50-100 KB

### Launch Agent Logs
- **Stdout:** `~/.openclaw/logs/speculative-decoding-launchd.log`
- **Stderr:** `~/.openclaw/logs/speculative-decoding-launchd-error.log`
- **Purpose:** launchd service startup messages

## Integration with Flask

The logging is integrated directly into the Flask server:

```python
from speculative_logging import init_logger

# Initialize at startup
logger = init_logger()

# Log requests
logger.log_request(len(prompt), max_tokens, draft_len)

# Log generations
logger.log_generation(tokens, time_taken, throughput, memory_gb)

# Log errors
logger.log_error("Error message")

# Get stats for /status endpoint
stats = logger.get_stats()
```

## Implementation Details

### Thread Safety
- Uses `Lock` for batch access
- Safe for concurrent writes from Flask

### Batching Strategy
- Accumulates 10 records in memory
- Flushes automatically when batch is full
- Flushes on shutdown for clean termination

### Error Handling
- Silent failures (no exceptions thrown)
- Errors logged but don't impact generation
- Recovery: Next successful write flushes batch

## Example Output (First 5 Records)

```json
{"type": "server_start", "ts": 1711527600.123}
{"type": "request", "ts": 1711527600.124, "prompt_len": 45, "max_tokens": 100, "draft_len": 4}
{"type": "generation", "ts": 1711527608.624, "tokens": 98, "time_s": 8.5, "tok_s": 11.5, "mem_gb": 0.95}
{"type": "request", "ts": 1711527610.124, "prompt_len": 52, "max_tokens": 150, "draft_len": 4}
{"type": "generation", "ts": 1711527620.124, "tokens": 145, "time_s": 10.0, "tok_s": 14.5, "mem_gb": 0.98}
```

## Data Analysis Examples

### Generate CSV for plotting
```bash
grep '"generation"' ~/.openclaw/logs/speculative-metrics.jsonl | \
  jq -r '[.ts, .tok_s, .tokens, .time_s] | @csv' > ~/speed_analysis.csv
```

### Calculate percentiles
```bash
grep '"generation"' ~/.openclaw/logs/speculative-metrics.jsonl | \
  jq '.tok_s' | \
  sort -n | \
  awk 'NR==int(NR*0.25) {q1=$1} NR==int(NR*0.50) {q2=$1} NR==int(NR*0.75) {q3=$1} END {print "Q1: "q1 " Median: "q2 " Q3: "q3}'
```

## Expected Data Volume

**3-day test estimates:**

| Metric | Expected | Reality |
|--------|----------|---------|
| Generations/day | 100-200 | TBD |
| Requests/day | 100-200 | TBD |
| Log file size | 500 KB - 1 MB | TBD |
| Overhead | <0.1% | TBD |

## Cleanup

**To delete metrics (after analysis):**
```bash
rm ~/.openclaw/logs/speculative-metrics.jsonl
```

**To archive (for long-term storage):**
```bash
gzip ~/.openclaw/logs/speculative-metrics.jsonl
```

## References

- **Logger code:** `scripts/speculative-logging.py`
- **Analysis script:** `scripts/analyze-speculative-3day.sh`
- **Flask integration:** Updated launchd plist
- **Main metrics file:** `~/.openclaw/logs/speculative-metrics.jsonl`
