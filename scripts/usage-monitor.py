#!/usr/bin/env python3
"""
Anthropic Usage Monitor for OpenClaw
Real-time display of billed API token usage.

Data sources:
  1. Anthropic Admin API — authoritative billing totals, polled every 5 min
  2. ~/.claude/projects JSONL files — per-message real-time tracking

Usage:
  python3 usage-monitor.py
  python3 usage-monitor.py --free-allowance 20   # $20/month included
  python3 usage-monitor.py --billing-start 2026-05-01
  python3 usage-monitor.py --plain              # no rich UI, plain text
  python3 usage-monitor.py --once               # single snapshot, then exit
"""

import json
import os
import glob
import time
import sys
import argparse
import subprocess
from datetime import datetime, timezone, timedelta
from collections import defaultdict

try:
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.text import Text
    from rich.columns import Columns
    from rich import box
    from rich.rule import Rule
    from rich.align import Align

    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# ─── Pricing ($ per million tokens) ────────────────────────────────────────────
# Source: anthropic-spend-check.py — update both together
PRICING = {
    "claude-opus-4-7": dict(inp=15.00, out=75.00, cw=18.75, cr=1.50),
    "claude-opus-4-6": dict(inp=15.00, out=75.00, cw=18.75, cr=1.50),
    "claude-opus-4-5": dict(inp=15.00, out=75.00, cw=18.75, cr=1.50),
    "claude-opus-4": dict(inp=15.00, out=75.00, cw=18.75, cr=1.50),
    "claude-sonnet-4-6": dict(inp=3.00, out=15.00, cw=3.75, cr=0.30),
    "claude-sonnet-4-5": dict(inp=3.00, out=15.00, cw=3.75, cr=0.30),
    "claude-sonnet-4": dict(inp=3.00, out=15.00, cw=3.75, cr=0.30),
    "claude-haiku-4-5": dict(inp=0.80, out=4.00, cw=1.00, cr=0.08),
    "claude-haiku-4": dict(inp=0.80, out=4.00, cw=1.00, cr=0.08),
    "claude-haiku-3-5": dict(inp=0.80, out=4.00, cw=1.00, cr=0.08),
    "claude-sonnet-3-5": dict(inp=3.00, out=15.00, cw=3.75, cr=0.30),
    "default": dict(inp=3.00, out=15.00, cw=3.75, cr=0.30),
}

CLAUDE_PROJECTS_DIR = os.path.expanduser("~/.claude/projects")

# ─── Helpers ────────────────────────────────────────────────────────────────────


def price_for(model: str) -> dict:
    if not model:
        return PRICING["default"]
    m = model.lower()
    for k in sorted(PRICING.keys(), key=len, reverse=True):
        if k != "default" and k in m:
            return PRICING[k]
    return PRICING["default"]


def calc_cost(inp, out, cw, cr, model) -> float:
    p = price_for(model)
    return (
        inp / 1e6 * p["inp"]
        + out / 1e6 * p["out"]
        + cw / 1e6 * p["cw"]
        + cr / 1e6 * p["cr"]
    )


def get_admin_key() -> str:
    try:
        result = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-s",
                "AnthropicAdminKey",
                "-a",
                "openclaw",
                "-w",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return os.environ.get("ANTHROPIC_ADMIN_KEY", "")


def fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def fmt_cost(usd: float) -> str:
    if usd >= 1.0:
        return f"${usd:.2f}"
    if usd >= 0.001:
        return f"${usd:.4f}"
    return f"${usd:.6f}"


def short_model(model: str) -> str:
    parts = model.split("-")
    trimmed = [p for p in parts if not (len(p) == 8 and p.isdigit())]
    return "-".join(trimmed)


def billing_period_start() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


# ─── Admin API ──────────────────────────────────────────────────────────────────


def fetch_admin_usage(admin_key: str, start: datetime, end: datetime) -> dict | None:
    """Fetch usage from Anthropic Admin API. Returns per-model aggregate or None on error."""
    if not admin_key:
        return None

    import urllib.request
    import urllib.error

    url = (
        "https://api.anthropic.com/v1/organizations/usage_report/messages"
        f"?starting_at={start.strftime('%Y-%m-%d')}"
        f"&ending_at={end.strftime('%Y-%m-%d')}"
        "&group_by[]=model"
    )

    req = urllib.request.Request(
        url,
        headers={
            "x-api-key": admin_key,
            "anthropic-version": "2023-06-01",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = json.load(resp)
    except (urllib.error.URLError, json.JSONDecodeError):
        return None

    if "error" in raw:
        return None

    # Aggregate by model across all days
    by_model: dict[str, dict] = {}
    for bucket in raw.get("data", []):
        for r in bucket.get("results", []):
            model = r.get("model") or "unknown"
            mdl = short_model(model)
            if mdl not in by_model:
                by_model[mdl] = {"inp": 0, "out": 0, "cw": 0, "cr": 0, "cost": 0.0}
            s = by_model[mdl]
            cw_info = r.get("cache_creation") or {}
            inp = r.get("uncached_input_tokens", 0)
            out = r.get("output_tokens", 0)
            cw = cw_info.get("ephemeral_5m_input_tokens", 0) + cw_info.get(
                "ephemeral_1h_input_tokens", 0
            )
            cr = r.get("cache_read_input_tokens", 0)
            s["inp"] += inp
            s["out"] += out
            s["cw"] += cw
            s["cr"] += cr
            s["cost"] += calc_cost(inp, out, cw, cr, model)

    return by_model


# ─── JSONL Tracker ──────────────────────────────────────────────────────────────


class LiveTracker:
    """Watches JSONL files for new usage entries. Provides today's live delta."""

    def __init__(self, billing_start: datetime):
        self.billing_start = billing_start
        self.seen_uuids: set[str] = set()
        self.file_positions: dict[str, int] = {}
        # Stats keyed by model
        self.today: dict[str, dict] = defaultdict(
            lambda: {"inp": 0, "out": 0, "cw": 0, "cr": 0, "cost": 0.0, "msgs": 0}
        )
        self.period: dict[str, dict] = defaultdict(
            lambda: {"inp": 0, "out": 0, "cw": 0, "cr": 0, "cost": 0.0, "msgs": 0}
        )
        self.recent: list[dict] = []  # last 20 messages

    def _process(self, entry: dict) -> bool:
        if entry.get("type") != "assistant":
            return False
        msg = entry.get("message", {})
        model = msg.get("model", "")
        if not model or model == "<synthetic>":
            return False
        usage = msg.get("usage", {})
        uuid = entry.get("uuid")
        if not uuid or uuid in self.seen_uuids:
            return False

        inp = usage.get("input_tokens", 0)
        out = usage.get("output_tokens", 0)
        cw_info = usage.get("cache_creation", {}) or {}
        cw = (
            usage.get("cache_creation_input_tokens", 0)
            + cw_info.get("ephemeral_5m_input_tokens", 0)
            + cw_info.get("ephemeral_1h_input_tokens", 0)
        )
        cr = usage.get("cache_read_input_tokens", 0)

        if inp + out + cw + cr == 0:
            return False

        self.seen_uuids.add(uuid)
        cost = calc_cost(inp, out, cw, cr, model)
        mdl = short_model(model)

        try:
            ts_str = entry.get("timestamp", "")
            ts = datetime.fromisoformat(ts_str.rstrip("Z") + "+00:00")
        except Exception:
            ts = datetime.now(timezone.utc)

        today = datetime.now(timezone.utc).date()

        if ts >= self.billing_start:
            s = self.period[mdl]
            s["inp"] += inp
            s["out"] += out
            s["cw"] += cw
            s["cr"] += cr
            s["cost"] += cost
            s["msgs"] += 1

        if ts.date() == today:
            s = self.today[mdl]
            s["inp"] += inp
            s["out"] += out
            s["cw"] += cw
            s["cr"] += cr
            s["cost"] += cost
            s["msgs"] += 1
            self.recent.append(
                {
                    "ts": ts,
                    "model": mdl,
                    "cost": cost,
                    "inp": inp,
                    "out": out,
                    "cw": cw,
                    "cr": cr,
                }
            )
            self.recent = sorted(self.recent, key=lambda x: x["ts"])[-20:]

        return True

    def scan_file(self, path: str, incremental: bool = True) -> int:
        pos = self.file_positions.get(path, 0) if incremental else 0
        count = 0
        try:
            with open(path) as f:
                f.seek(pos)
                for line in f:
                    try:
                        if self._process(json.loads(line)):
                            count += 1
                    except (json.JSONDecodeError, KeyError):
                        pass
                self.file_positions[path] = f.tell()
        except (OSError, IOError):
            pass
        return count

    def scan_all(self, incremental: bool = True) -> int:
        total = 0
        pattern = os.path.join(CLAUDE_PROJECTS_DIR, "*", "*.jsonl")
        for path in glob.glob(pattern):
            total += self.scan_file(path, incremental)
        return total

    def total_cost(self, stats: dict) -> float:
        return sum(s["cost"] for s in stats.values())


# ─── Display ────────────────────────────────────────────────────────────────────


def make_layout(
    tracker: LiveTracker,
    api_data: dict | None,
    api_synced_at: datetime | None,
    free_allowance: float,
    billing_start: datetime,
) -> "Layout":
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box

    now = datetime.now(timezone.utc)
    today_str = now.strftime("%b %-d, %Y")
    period_str = f"{billing_start.strftime('%b %-d')}–{now.strftime('%-d, %Y')}"

    # Period = API confirmed (past days) + JSONL live (today)
    today_cost = tracker.total_cost(tracker.today)
    if api_data is not None:
        api_confirmed = sum(s["cost"] for s in api_data.values())
        period_cost = api_confirmed + today_cost
        source = "API+live"
    else:
        period_cost = tracker.total_cost(tracker.period)
        source = "est"

    extra_cost = max(0.0, period_cost - free_allowance)

    sync_str = ""
    if api_synced_at:
        age_s = int((now - api_synced_at).total_seconds())
        if age_s < 60:
            sync_str = f"synced {age_s}s ago"
        else:
            sync_str = f"synced {age_s // 60}m ago"

    # ── Header panel ────────────────────────────────────────────────────────
    header_text = Text()
    header_text.append("Anthropic Usage Monitor", style="bold white")
    header_text.append(f"  ·  Billing period: {period_str}", style="dim")
    if sync_str:
        header_text.append(
            f"  ·  {sync_str}", style="dim green" if age_s < 300 else "dim yellow"
        )

    # ── Summary row ─────────────────────────────────────────────────────────
    summary = Table.grid(padding=(0, 4))
    summary.add_column(justify="left")
    summary.add_column(justify="left")
    summary.add_column(justify="left")
    summary.add_column(justify="left")

    period_style = (
        "bold red"
        if period_cost > 50
        else ("bold yellow" if period_cost > 10 else "bold green")
    )
    extra_style = "bold red" if extra_cost > 0 else "dim green"

    summary.add_row(
        f"[bold]Period ({source})[/]  [{period_style}]{fmt_cost(period_cost)}[/]",
        f"[bold]Today (live)[/]  [white]{fmt_cost(today_cost)}[/]",
        f"[bold]Allowance[/]  [dim]{fmt_cost(free_allowance)}[/]",
        f"[{extra_style}]EXTRA BILLED  {fmt_cost(extra_cost)}[/]",
    )

    # ── Model breakdown ──────────────────────────────────────────────────────
    model_table = Table(box=box.SIMPLE_HEAD, padding=(0, 1), expand=True)
    model_table.add_column("Model", style="cyan", no_wrap=True)
    model_table.add_column("Input", justify="right", style="dim")
    model_table.add_column("Output", justify="right", style="dim")
    model_table.add_column("CacheW", justify="right", style="dim")
    model_table.add_column("CacheR", justify="right", style="dim")
    model_table.add_column("Cost", justify="right", style="bold")

    # Merge API confirmed data with today's live JSONL data
    if api_data is not None:
        merged: dict[str, dict] = {}
        for model, s in api_data.items():
            merged[model] = dict(s)
        for model, s in tracker.today.items():
            if model in merged:
                for k in ("inp", "out", "cw", "cr", "cost"):
                    merged[model][k] = merged[model].get(k, 0) + s.get(k, 0)
            else:
                merged[model] = dict(s)
        data_src = merged
    else:
        data_src = tracker.period
    rows = sorted(data_src.items(), key=lambda x: -x[1]["cost"])
    for model, s in rows:
        cost = s["cost"]
        model_table.add_row(
            model,
            fmt_tokens(s["inp"]),
            fmt_tokens(s["out"]),
            fmt_tokens(s["cw"]),
            fmt_tokens(s["cr"]),
            fmt_cost(cost),
        )
    if not rows:
        model_table.add_row("[dim]No data[/]", "", "", "", "", "")

    # ── Live activity ────────────────────────────────────────────────────────
    live_table = Table(box=box.SIMPLE_HEAD, padding=(0, 1), expand=True)
    live_table.add_column("Time", style="dim", no_wrap=True)
    live_table.add_column("Model", style="cyan", no_wrap=True)
    live_table.add_column("In", justify="right", style="dim")
    live_table.add_column("Out", justify="right", style="dim")
    live_table.add_column("CacheW", justify="right", style="dim")
    live_table.add_column("CacheR", justify="right", style="dim")
    live_table.add_column("Cost", justify="right", style="bold")

    recent_reversed = list(reversed(tracker.recent))[:12]
    for entry in recent_reversed:
        ts_local = entry["ts"].astimezone()
        live_table.add_row(
            ts_local.strftime("%H:%M:%S"),
            entry["model"],
            fmt_tokens(entry["inp"]),
            fmt_tokens(entry["out"]),
            fmt_tokens(entry["cw"]),
            fmt_tokens(entry["cr"]),
            fmt_cost(entry["cost"]),
        )
    if not recent_reversed:
        live_table.add_row("[dim]Watching for new activity…[/]", "", "", "", "", "", "")

    # ── Assemble layout ──────────────────────────────────────────────────────
    layout = Layout()
    layout.split_column(
        Layout(Panel(header_text, border_style="blue"), size=3),
        Layout(Panel(summary, title="[bold]SUMMARY[/]", border_style="blue"), size=5),
        Layout(
            Panel(
                model_table,
                title=f"[bold]MODEL BREAKDOWN[/] [dim](billing period{' — API' if api_data else ' — estimated'})[/]",
                border_style="blue",
            )
        ),
        Layout(
            Panel(
                live_table,
                title="[bold]LIVE ACTIVITY[/] [dim](today)[/]",
                border_style="green",
            )
        ),
        Layout(
            Text(
                f"  Refresh: JSONL every 5s  ·  Admin API every 5min  ·  Press Ctrl-C to exit",
                style="dim",
            ),
            size=1,
        ),
    )

    return layout


def plain_output(
    tracker: LiveTracker,
    api_data: dict | None,
    api_synced_at: datetime | None,
    free_allowance: float,
    billing_start: datetime,
) -> None:
    now = datetime.now(timezone.utc)
    print(f"=== Anthropic Usage Monitor — {now.strftime('%Y-%m-%d %H:%M:%S UTC')} ===")

    today_cost = tracker.total_cost(tracker.today)
    if api_data is not None:
        api_confirmed = sum(s["cost"] for s in api_data.values())
        period_cost = api_confirmed + today_cost
        print(
            f"Billing period ({billing_start.strftime('%Y-%m-%d')} → today): {fmt_cost(period_cost)}  [API + live]"
        )
        print(f"  API confirmed (past days): {fmt_cost(api_confirmed)}")
        print(f"  Live today (JSONL):        {fmt_cost(today_cost)}")
        all_models: dict[str, dict] = {}
        for model, s in api_data.items():
            all_models[model] = dict(s)
        for model, s in tracker.today.items():
            if model in all_models:
                all_models[model]["cost"] += s["cost"]
            else:
                all_models[model] = dict(s)
        print()
        for model, s in sorted(all_models.items(), key=lambda x: -x[1]["cost"]):
            print(f"  {model:<35} {fmt_cost(s['cost'])}")
    else:
        period_cost = tracker.total_cost(tracker.period)
        print(
            f"Billing period ({billing_start.strftime('%Y-%m-%d')} → today): {fmt_cost(period_cost)}  [estimated from JSONL]"
        )

    extra = max(0.0, period_cost - free_allowance)
    print(f"Today: {fmt_cost(today_cost)}")
    print(f"Free allowance: {fmt_cost(free_allowance)}")
    print(f"EXTRA BILLED: {fmt_cost(extra)}")

    if tracker.recent:
        print("\nRecent activity:")
        for e in reversed(tracker.recent[-10:]):
            ts_local = e["ts"].astimezone()
            print(
                f"  {ts_local.strftime('%H:%M:%S')}  {e['model']:<30}  {fmt_cost(e['cost'])}"
            )


# ─── Main ────────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Anthropic usage monitor for OpenClaw")
    parser.add_argument(
        "--free-allowance",
        type=float,
        default=0.0,
        help="Monthly included amount in USD (default: 0)",
    )
    parser.add_argument(
        "--billing-start",
        type=str,
        default=None,
        help="Billing period start date YYYY-MM-DD (default: 1st of current month)",
    )
    parser.add_argument(
        "--plain", action="store_true", help="Plain text output (no rich UI)"
    )
    parser.add_argument("--once", action="store_true", help="Single snapshot then exit")
    parser.add_argument(
        "--refresh-secs", type=int, default=5, help="JSONL poll interval in seconds"
    )
    parser.add_argument(
        "--api-refresh-secs",
        type=int,
        default=300,
        help="Admin API refresh interval in seconds",
    )
    args = parser.parse_args()

    if args.billing_start:
        billing_start = datetime.fromisoformat(args.billing_start).replace(
            tzinfo=timezone.utc
        )
    else:
        billing_start = billing_period_start()

    admin_key = get_admin_key()
    if not admin_key:
        print(
            "WARNING: AnthropicAdminKey not found in keychain — API data unavailable",
            file=sys.stderr,
        )

    tracker = LiveTracker(billing_start=billing_start)

    # Initial full scan (historical)
    print("Scanning historical JSONL files…", file=sys.stderr, end=" ", flush=True)
    n = tracker.scan_all(incremental=False)
    print(f"{n} entries loaded.", file=sys.stderr)

    # Initial Admin API fetch
    now = datetime.now(timezone.utc)
    api_data = (
        fetch_admin_usage(admin_key, billing_start, now + timedelta(days=1))
        if admin_key
        else None
    )
    api_synced_at = now if api_data is not None else None

    if args.once or args.plain:
        plain_output(
            tracker, api_data, api_synced_at, args.free_allowance, billing_start
        )
        return

    if not HAS_RICH:
        print("Install 'rich' for live UI: pip install rich", file=sys.stderr)
        plain_output(
            tracker, api_data, api_synced_at, args.free_allowance, billing_start
        )
        return

    console = Console()
    last_api_refresh = time.time()

    try:
        with Live(console=console, refresh_per_second=1, screen=True) as live:
            while True:
                # Incremental JSONL scan
                tracker.scan_all(incremental=True)

                # Periodic Admin API refresh
                if time.time() - last_api_refresh >= args.api_refresh_secs:
                    now = datetime.now(timezone.utc)
                    new_data = fetch_admin_usage(
                        admin_key, billing_start, now + timedelta(days=1)
                    )
                    if new_data is not None:
                        api_data = new_data
                        api_synced_at = now
                    last_api_refresh = time.time()

                now = datetime.now(timezone.utc)
                layout = make_layout(
                    tracker, api_data, api_synced_at, args.free_allowance, billing_start
                )
                live.update(layout)
                time.sleep(args.refresh_secs)

    except KeyboardInterrupt:
        console.print("\n[dim]Exiting.[/]")


if __name__ == "__main__":
    main()
