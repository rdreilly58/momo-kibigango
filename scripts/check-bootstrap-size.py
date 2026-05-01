#!/usr/bin/env python3
"""
check-bootstrap-size.py — Monitor workspace bootstrap file sizes
Alert if any file exceeds 70% of the 12K character limit, or if total exceeds 70% of 60K.

Weekly cron: runs Monday 09:00 America/New_York
Exit 1 if any threshold exceeded, 0 otherwise.
"""

import os
import sys

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")

# Files to check (relative to workspace)
FILES = [
    "AGENTS.md",
    "SOUL.md",
    "USER.md",
    "TOOLS.md",
    "MEMORY.md",
    "HEARTBEAT.md",
]

# Thresholds
PER_FILE_LIMIT = 12_000     # chars per file (system limit)
PER_FILE_WARN  = int(PER_FILE_LIMIT * 0.70)  # 8,400 chars = 70%
TOTAL_LIMIT    = 60_000     # total chars across all files
TOTAL_WARN     = int(TOTAL_LIMIT * 0.70)      # 42,000 chars = 70%

results = []
total_chars = 0
any_exceeded = False

print("Bootstrap File Size Report")
print("=" * 55)

for filename in FILES:
    path = os.path.join(WORKSPACE, filename)
    if not os.path.exists(path):
        results.append((filename, 0, "MISSING", False))
        print(f"  ⚠️  {filename:<20} MISSING")
        continue

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    chars = len(content)
    total_chars += chars
    pct = (chars / PER_FILE_LIMIT) * 100
    exceeded = chars > PER_FILE_WARN

    if exceeded:
        any_exceeded = True
        status = f"⚠️  {chars:,} chars ({pct:.0f}%) — OVER 70% THRESHOLD"
    else:
        status = f"✅  {chars:,} chars ({pct:.0f}%)"

    results.append((filename, chars, status, exceeded))
    print(f"  {filename:<20} {status}")

print()

# Total check
total_pct = (total_chars / TOTAL_LIMIT) * 100
if total_chars > TOTAL_WARN:
    any_exceeded = True
    print(f"  TOTAL: {total_chars:,} chars ({total_pct:.0f}%) — ⚠️  OVER 70% TOTAL THRESHOLD ({TOTAL_WARN:,})")
else:
    print(f"  TOTAL: {total_chars:,} chars ({total_pct:.0f}%) ✅")

print()

if any_exceeded:
    print("ACTION REQUIRED: One or more bootstrap files exceed 70% size threshold.")
    print("  → Trim MEMORY.md, TOOLS.md, or other large files.")
    print(f"  → Per-file limit: {PER_FILE_WARN:,} chars (warn) / {PER_FILE_LIMIT:,} chars (hard)")
    print(f"  → Total limit:    {TOTAL_WARN:,} chars (warn) / {TOTAL_LIMIT:,} chars (hard)")
    sys.exit(1)
else:
    print("All bootstrap files within safe size limits. No action needed.")
    sys.exit(0)
