#!/usr/bin/env bash
# model-usage-report.sh — Weekly summary of model usage from CSV logs.
#
# Usage:
#   model-usage-report.sh              # last 7 days
#   model-usage-report.sh --days 14    # last N days
#   model-usage-report.sh --date 2026-05-08  # specific day
#
# Reports:
#   - Total messages by tier
#   - Token estimates by tier
#   - Tier with most messages
#   - Warning if >10% of simple-classified are long (>50 words) — likely misclassification

set -euo pipefail

LOG_DIR="${HOME}/.openclaw/logs/model-usage"
days=7
specific_date=""

# ── Argument parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --days|-d)   days="$2";          shift 2 ;;
    --date)      specific_date="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: model-usage-report.sh [--days N] [--date YYYY-MM-DD]"
      exit 0
      ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

# ── Gather CSV files ──────────────────────────────────────────────────────────
if [[ -n "$specific_date" ]]; then
  files=("${LOG_DIR}/${specific_date}.csv")
else
  files=()
  for i in $(seq 0 $((days - 1))); do
    d=$(date -v-${i}d +%Y-%m-%d 2>/dev/null || date -d "${i} days ago" +%Y-%m-%d 2>/dev/null || echo "")
    [[ -n "$d" && -f "${LOG_DIR}/${d}.csv" ]] && files+=("${LOG_DIR}/${d}.csv")
  done
fi

# Check if any files exist
existing_files=()
for f in "${files[@]}"; do
  [[ -f "$f" ]] && existing_files+=("$f")
done

if [[ ${#existing_files[@]} -eq 0 ]]; then
  echo "No usage logs found in ${LOG_DIR} for the requested period."
  exit 0
fi

echo "════════════════════════════════════════════════════"
echo " Model Usage Report — last ${days} days"
echo " Log dir: ${LOG_DIR}"
echo "════════════════════════════════════════════════════"
echo ""

# ── Python analysis ───────────────────────────────────────────────────────────
python3 - "${existing_files[@]}" <<'PYEOF'
import sys
import csv
from collections import defaultdict

files = sys.argv[1:]
rows = []

for path in files:
    try:
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    except Exception as e:
        print(f"  Warning: could not read {path}: {e}")

if not rows:
    print("No data rows found.")
    sys.exit(0)

# Aggregate by tier
tier_counts  = defaultdict(int)
tier_tokens  = defaultdict(int)
session_counts = defaultdict(int)
model_counts = defaultdict(int)

# Track simple-classified rows with long messages (>50 words)
simple_rows = []
simple_long = 0

for row in rows:
    tier = row.get("tier_classified", "unknown")
    tokens = int(row.get("tokens_est", 0) or 0)
    stype = row.get("session_type", "unknown")
    model = row.get("model_used", "unknown")
    preview = row.get("message_preview", "")

    tier_counts[tier] += 1
    tier_tokens[tier] += tokens
    session_counts[stype] += 1
    model_counts[model] += 1

    if tier == "simple":
        word_count = len(preview.split())
        if word_count > 50:
            simple_long += 1
        simple_rows.append(word_count)

total = len(rows)

print(f"Total messages logged: {total}")
print(f"Date range: {files[0].split('/')[-1].replace('.csv','')} — {files[-1].split('/')[-1].replace('.csv','')}")
print()

# ── By tier ──────────────────────────────────────────────────────────────────
print("Messages by tier:")
print(f"  {'Tier':<12} {'Count':<8} {'Tokens Est':<12} {'% of Total'}")
print(f"  {'─'*12} {'─'*8} {'─'*12} {'─'*10}")
for tier in ["simple", "medium", "complex", "unknown"]:
    count = tier_counts.get(tier, 0)
    tokens = tier_tokens.get(tier, 0)
    pct = (count / total * 100) if total > 0 else 0
    print(f"  {tier:<12} {count:<8} {tokens:<12} {pct:.1f}%")
print()

# ── Most common tier ─────────────────────────────────────────────────────────
if tier_counts:
    top_tier = max(tier_counts, key=tier_counts.get)
    print(f"Most active tier: {top_tier} ({tier_counts[top_tier]} messages)")

# ── By session type ──────────────────────────────────────────────────────────
print()
print("Messages by session type:")
for stype, count in sorted(session_counts.items(), key=lambda x: -x[1]):
    print(f"  {stype:<15} {count}")

# ── By model ─────────────────────────────────────────────────────────────────
print()
print("Messages by model:")
for model, count in sorted(model_counts.items(), key=lambda x: -x[1]):
    pct = (count / total * 100) if total > 0 else 0
    print(f"  {model:<45} {count:>5}  ({pct:.1f}%)")

# ── Misclassification warning ─────────────────────────────────────────────────
print()
simple_total = tier_counts.get("simple", 0)
if simple_total > 0 and simple_rows:
    long_rate = simple_long / simple_total
    if long_rate > 0.10:
        print(f"⚠️  MISCLASSIFICATION WARNING: {simple_long}/{simple_total} simple-classified messages")
        print(f"   have >50 words ({long_rate*100:.1f}%) — may indicate classifier is under-routing.")
    else:
        print(f"✅ Simple classifier quality: {simple_long}/{simple_total} long messages "
              f"({long_rate*100:.1f}%) — within threshold.")
else:
    print("ℹ️  No simple-classified messages to assess.")

PYEOF
