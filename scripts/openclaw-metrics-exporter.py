#!/usr/bin/env python3
"""
openclaw-metrics-exporter.py — Prometheus metrics exporter for OpenClaw.

Reads cron heartbeat JSON files, memory DB stats, session health, and log
activity, then exposes them as Prometheus text format on :9091/metrics.

Usage:
    python3 scripts/openclaw-metrics-exporter.py           # start server
    python3 scripts/openclaw-metrics-exporter.py --once    # print once to stdout
    python3 scripts/openclaw-metrics-exporter.py --port 9091

Grafana datasource: Prometheus → http://localhost:9091
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Iterator

# ── Paths ──────────────────────────────────────────────────────────────────────
WORKSPACE = Path.home() / ".openclaw" / "workspace"
LOGS_DIR  = Path.home() / ".openclaw" / "logs"
HB_DIR    = LOGS_DIR / "cron-heartbeats"
DB_PATH   = WORKSPACE / "ai-memory.db"
SESSIONS_FILE = Path.home() / ".openclaw" / "agents" / "main" / "sessions" / "sessions.json"

# Expected cron jobs — alert if missing heartbeat
KNOWN_CRONS = [
    "auto-flush-session-context",
    "daily-session-reset",
    "evening-briefing",
    "morning-briefing",
    "observer-agent",
    "quota-monitoring",
    "session-watchdog",
    "system-health-check",
]

# Cron max-age thresholds in seconds (matches cron-dead-man.sh)
CRON_MAX_AGE: dict[str, int] = {
    "session-watchdog":          3 * 3600,
    "auto-flush-session-context": 4 * 3600,
    "system-health-check":       4 * 3600,
    "daily-session-reset":       26 * 3600,
    "observer-agent":            3 * 3600,
    "morning-briefing":          26 * 3600,
    "evening-briefing":          26 * 3600,
    "quota-monitoring":          26 * 3600,
}

SESSION_KEYS = [
    "agent:main:main",
    "agent:main:main:heartbeat",
    "agent:main:telegram:direct:8755120444",
]


# ── Metric helpers ─────────────────────────────────────────────────────────────

def _gauge(name: str, value: float, labels: dict[str, str] | None = None, help_text: str = "") -> Iterator[str]:
    """Yield Prometheus text lines for a gauge."""
    label_str = ""
    if labels:
        parts = ','.join(f'{k}="{v}"' for k, v in labels.items())
        label_str = f"{{{parts}}}"
    if help_text:
        yield f"# HELP {name} {help_text}"
        yield f"# TYPE {name} gauge"
    yield f"{name}{label_str} {value}"


def _cron_metrics() -> list[str]:
    lines: list[str] = []
    lines += ["# HELP openclaw_cron_last_run_age_seconds Seconds since cron last ran"]
    lines += ["# TYPE openclaw_cron_last_run_age_seconds gauge"]
    lines += ["# HELP openclaw_cron_last_exit_code Exit code of last run (0=success)"]
    lines += ["# TYPE openclaw_cron_last_exit_code gauge"]
    lines += ["# HELP openclaw_cron_stale Whether cron is past its max-age threshold (1=stale)"]
    lines += ["# TYPE openclaw_cron_stale gauge"]
    lines += ["# HELP openclaw_cron_present Whether heartbeat file exists (1=yes)"]
    lines += ["# TYPE openclaw_cron_present gauge"]

    now = time.time()
    for job in KNOWN_CRONS:
        hb_file = HB_DIR / f"{job}.json"
        lbl = f'job="{job}"'
        if not hb_file.exists():
            lines.append(f'openclaw_cron_present{{{lbl}}} 0')
            lines.append(f'openclaw_cron_last_run_age_seconds{{{lbl}}} -1')
            lines.append(f'openclaw_cron_last_exit_code{{{lbl}}} -1')
            lines.append(f'openclaw_cron_stale{{{lbl}}} 1')
            continue

        try:
            data = json.loads(hb_file.read_text())
            ts = float(data.get("last_run_ts", 0))
            exit_code = int(data.get("exit_code", -1))
            age = now - ts if ts > 0 else -1
            max_age = CRON_MAX_AGE.get(job, 26 * 3600)
            stale = 1 if (age < 0 or age > max_age) else 0

            lines.append(f'openclaw_cron_present{{{lbl}}} 1')
            lines.append(f'openclaw_cron_last_run_age_seconds{{{lbl}}} {age:.0f}')
            lines.append(f'openclaw_cron_last_exit_code{{{lbl}}} {exit_code}')
            lines.append(f'openclaw_cron_stale{{{lbl}}} {stale}')
        except Exception as e:
            lines.append(f'openclaw_cron_present{{{lbl}}} 0')
            lines.append(f'openclaw_cron_last_run_age_seconds{{{lbl}}} -1')
            lines.append(f'openclaw_cron_last_exit_code{{{lbl}}} -1')
            lines.append(f'openclaw_cron_stale{{{lbl}}} 1')

    return lines


def _memory_metrics() -> list[str]:
    lines: list[str] = []
    lines += ["# HELP openclaw_memory_entries_total Total memory entries in ai-memory.db"]
    lines += ["# TYPE openclaw_memory_entries_total gauge"]
    lines += ["# HELP openclaw_memory_entries_by_tier Memory entries grouped by tier"]
    lines += ["# TYPE openclaw_memory_entries_by_tier gauge"]

    if not DB_PATH.exists():
        lines.append("openclaw_memory_entries_total -1")
        return lines

    try:
        conn = sqlite3.connect(str(DB_PATH))
        total = conn.execute("SELECT count(*) FROM memories").fetchone()[0]
        lines.append(f"openclaw_memory_entries_total {total}")

        by_tier = conn.execute(
            "SELECT tier, count(*) FROM memories GROUP BY tier"
        ).fetchall()
        for tier, count in by_tier:
            lines.append(f'openclaw_memory_entries_by_tier{{tier="{tier}"}} {count}')

        # Graph link count
        try:
            link_count = conn.execute("SELECT count(*) FROM memory_links").fetchone()[0]
            lines += ["# HELP openclaw_memory_graph_links Total graph links in memory"]
            lines += ["# TYPE openclaw_memory_graph_links gauge"]
            lines.append(f"openclaw_memory_graph_links {link_count}")
        except Exception:
            pass

        conn.close()
    except Exception as e:
        lines.append(f"# ERROR reading memory db: {e}")
        lines.append("openclaw_memory_entries_total -1")

    return lines


def _session_metrics() -> list[str]:
    lines: list[str] = []
    lines += ["# HELP openclaw_session_age_seconds Age of most recent session activity in seconds"]
    lines += ["# TYPE openclaw_session_age_seconds gauge"]
    lines += ["# HELP openclaw_session_stale Whether session is considered stale (>3600s, 1=stale)"]
    lines += ["# TYPE openclaw_session_stale gauge"]

    if not SESSIONS_FILE.exists():
        lines.append("openclaw_session_age_seconds -1")
        lines.append("openclaw_session_stale 1")
        return lines

    try:
        data = json.loads(SESSIONS_FILE.read_text())
        now_ms = time.time() * 1000
        best_ts = 0
        for key in SESSION_KEYS:
            ts = int(data.get(key, {}).get("updatedAt", 0))
            if ts > best_ts:
                best_ts = ts

        if best_ts == 0:
            lines.append("openclaw_session_age_seconds -1")
            lines.append("openclaw_session_stale 1")
        else:
            age_sec = (now_ms - best_ts) / 1000
            stale = 1 if age_sec > 3600 else 0
            lines.append(f"openclaw_session_age_seconds {age_sec:.0f}")
            lines.append(f"openclaw_session_stale {stale}")
    except Exception as e:
        lines.append(f"# ERROR reading sessions: {e}")
        lines.append("openclaw_session_age_seconds -1")
        lines.append("openclaw_session_stale 1")

    return lines


def _log_metrics() -> list[str]:
    """Count recent error/warning lines in key log files."""
    lines: list[str] = []
    lines += ["# HELP openclaw_log_errors_recent Error/WARNING lines in last 200 log lines"]
    lines += ["# TYPE openclaw_log_errors_recent gauge"]

    key_logs = {
        "session_watchdog": LOGS_DIR / "session-watchdog.log",
        "session_context_flush": LOGS_DIR / "session-context-flush.log",
        "cron_dead_man": LOGS_DIR / "cron-dead-man.log",
    }

    for log_name, log_path in key_logs.items():
        if not log_path.exists():
            lines.append(f'openclaw_log_errors_recent{{log="{log_name}"}} 0')
            continue
        try:
            with open(log_path) as f:
                tail = f.readlines()[-200:]
            errors = sum(1 for l in tail if any(w in l for w in ["ERROR", "STALE", "FAILED", "❌"]))
            lines.append(f'openclaw_log_errors_recent{{log="{log_name}"}} {errors}')
        except Exception:
            lines.append(f'openclaw_log_errors_recent{{log="{log_name}"}} -1')

    return lines


def _system_metrics() -> list[str]:
    lines: list[str] = []
    lines += ["# HELP openclaw_exporter_scrape_timestamp Unix timestamp of this scrape"]
    lines += ["# TYPE openclaw_exporter_scrape_timestamp gauge"]
    lines.append(f"openclaw_exporter_scrape_timestamp {time.time():.0f}")

    # Session context file age
    sc_file = WORKSPACE / "SESSION_CONTEXT.md"
    if sc_file.exists():
        age = time.time() - sc_file.stat().st_mtime
        lines += ["# HELP openclaw_session_context_age_seconds Age of SESSION_CONTEXT.md"]
        lines += ["# TYPE openclaw_session_context_age_seconds gauge"]
        lines.append(f"openclaw_session_context_age_seconds {age:.0f}")

    return lines


def collect_all_metrics() -> str:
    """Collect all metrics and return as Prometheus text."""
    sections = [
        _cron_metrics(),
        _memory_metrics(),
        _session_metrics(),
        _log_metrics(),
        _system_metrics(),
    ]
    all_lines: list[str] = []
    for section in sections:
        all_lines.extend(section)
        all_lines.append("")  # blank line between groups
    return "\n".join(all_lines) + "\n"


# ── HTTP server ────────────────────────────────────────────────────────────────

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/metrics", "/"):
            body = collect_all_metrics().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        # Suppress access log spam; write to stderr on errors only
        if int(args[1]) >= 400:
            super().log_message(fmt, *args)


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="OpenClaw Prometheus metrics exporter")
    p.add_argument("--port", type=int, default=9091)
    p.add_argument("--once", action="store_true", help="Print metrics once and exit")
    args = p.parse_args()

    if args.once:
        print(collect_all_metrics(), end="")
        return

    server = HTTPServer(("0.0.0.0", args.port), MetricsHandler)
    print(f"[openclaw-metrics] Serving on http://0.0.0.0:{args.port}/metrics", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[openclaw-metrics] Stopped.")


if __name__ == "__main__":
    main()
