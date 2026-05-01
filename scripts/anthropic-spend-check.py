#!/usr/bin/env python3
"""
Anthropic spend check — reads usage_report JSON from stdin, computes
token-based cost, and prints a summary + ALERT: lines for any threshold breach.

Usage: curl ... | python3 anthropic-spend-check.py
       python3 anthropic-spend-check.py < usage.json

For model breakdown, use group_by[]=model query param:
  curl "https://api.anthropic.com/v1/organizations/usage_report/messages?starting_at=YYYY-MM-DD&ending_at=YYYY-MM-DD&group_by[]=model"

Admin API key (from keychain: AnthropicAdminKey) required — standard API key won't work.

Env vars (optional):
  ANTHROPIC_DAILY_ALERT_USD   — alert if today's cost >= this (default: 20)
  ANTHROPIC_WEEKLY_ALERT_USD  — alert if 7d cost >= this   (default: 100)
"""

import json, sys, os
from datetime import datetime, timezone

# Pricing per 1M tokens (USD) — update if Anthropic changes rates
PRICING = {
    "claude-opus-4":          dict(inp=15.00, out=75.00, cw=18.75, cr=1.50),
    "claude-opus-4-7":        dict(inp=15.00, out=75.00, cw=18.75, cr=1.50),
    "claude-sonnet-4":        dict(inp=3.00,  out=15.00, cw=3.75,  cr=0.30),
    "claude-sonnet-4-5":      dict(inp=3.00,  out=15.00, cw=3.75,  cr=0.30),
    "claude-sonnet-4-6":      dict(inp=3.00,  out=15.00, cw=3.75,  cr=0.30),
    "claude-haiku-4":         dict(inp=0.80,  out=4.00,  cw=1.00,  cr=0.08),
    "claude-haiku-4-5":       dict(inp=0.80,  out=4.00,  cw=1.00,  cr=0.08),
    "claude-haiku-3-5":       dict(inp=0.80,  out=4.00,  cw=1.00,  cr=0.08),
    "claude-sonnet-3-5":      dict(inp=3.00,  out=15.00, cw=3.75,  cr=0.30),
    "default":                dict(inp=3.00,  out=15.00, cw=3.75,  cr=0.30),
}

def price_for(model):
    if not model:
        return PRICING["default"]
    m = model.lower()
    # Longest match wins (more specific models first)
    for k in sorted(PRICING.keys(), key=len, reverse=True):
        if k != "default" and k in m:
            return PRICING[k]
    return PRICING["default"]

daily_alert  = float(os.environ.get("ANTHROPIC_DAILY_ALERT_USD",  "20"))
weekly_alert = float(os.environ.get("ANTHROPIC_WEEKLY_ALERT_USD", "100"))
today        = datetime.now(timezone.utc).strftime("%Y-%m-%d")

try:
    raw = json.load(sys.stdin)
except Exception as e:
    print(f"ERROR: failed to parse JSON — {e}", file=sys.stderr)
    sys.exit(1)

if "error" in raw:
    err = raw["error"]
    print(f"ERROR:{err.get('type','?')}: {err.get('message','?')}")
    sys.exit(1)

data = raw.get("data", [])
total_7d   = 0.0
today_cost = 0.0
high_days  = []
model_totals = {}

for bucket in data:
    day = bucket["starting_at"][:10]
    day_cost = 0.0
    for r in bucket.get("results", []):
        p   = price_for(r.get("model"))
        cw  = r.get("cache_creation") or {}
        inp  = r.get("uncached_input_tokens",   0)
        out  = r.get("output_tokens",            0)
        cw5m = cw.get("ephemeral_5m_input_tokens", 0)
        cw1h = cw.get("ephemeral_1h_input_tokens", 0)
        cr   = r.get("cache_read_input_tokens",  0)
        cost = (inp/1e6*p["inp"] + out/1e6*p["out"] +
                (cw5m+cw1h)/1e6*p["cw"] + cr/1e6*p["cr"])
        day_cost += cost
        mdl = r.get("model") or "unknown"
        # Trim date suffix for cleaner display (e.g. claude-sonnet-4-6-20250101 → claude-sonnet-4-6)
        mdl_display = "-".join(p for p in mdl.split("-") if not (len(p) == 8 and p.isdigit()))
        model_totals[mdl_display] = model_totals.get(mdl_display, 0.0) + cost

    total_7d += day_cost
    if day == today:
        today_cost = day_cost
    if day_cost >= daily_alert:
        high_days.append((day, day_cost))

avg = total_7d / 7 if data else 0

print(f"Anthropic spend (7d) — today: ${today_cost:.4f} | 7d: ${total_7d:.4f} | avg/day: ${avg:.4f}")

# Top models by spend
if model_totals:
    top = sorted(model_totals.items(), key=lambda x: -x[1])[:5]
    print("  Top models:")
    for m, c in top:
        if c > 0.001:
            print(f"    {m:<40} ${c:.4f}")

if high_days:
    print("  High-spend days: " + ", ".join(f"{d}=${c:.2f}" for d, c in high_days))

# Emit ALERT lines for the bash script to pick up
if today_cost >= daily_alert:
    print(f"ALERT:Anthropic daily spend ${today_cost:.2f} exceeds ${daily_alert:.0f} threshold")
if total_7d >= weekly_alert:
    print(f"ALERT:Anthropic 7-day spend ${total_7d:.2f} exceeds ${weekly_alert:.0f} threshold")
