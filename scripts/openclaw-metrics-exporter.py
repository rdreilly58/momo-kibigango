#!/usr/bin/env python3
"""
openclaw-metrics-exporter.py — Prometheus metrics exporter for OpenClaw.

Reads cron heartbeat JSON files, memory DB stats, session health, and log
activity, then exposes them as Prometheus text format on :9091/metrics.

Also implements the Prometheus HTTP API (/api/v1/query, /api/v1/query_range,
/api/v1/labels, /api/v1/metadata) so Grafana's Prometheus datasource plugin
works without a full Prometheus server.

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
import re
import signal
import socket
import sqlite3
import sys
import time
import traceback
from collections import deque
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Iterator
from urllib.parse import urlparse, parse_qs
import threading

# ── Ring buffer for time-series history ───────────────────────────────────────
# Keeps last 4 hours at 15s resolution = ~960 entries, ~500KB max
_HISTORY_LOCK = threading.Lock()
_HISTORY: deque[tuple[float, str]] = deque(maxlen=960)
_LAST_SCRAPE_TS: float = 0.0
_SCRAPE_INTERVAL: float = 15.0  # seconds between background scrapes

# ── In-process counters (reset on restart) ───────────────────────────────────
_COUNTER_LOCK = threading.Lock()
_CRON_RUNS_TOTAL: dict[str, dict[str, int]] = {}  # job → {status → count}
_LOG_ERRORS_TOTAL: dict[str, int] = {}  # log_name → total_errors_seen

# ── Log scan cache (keyed by log name) ────────────────────────────────────────
_LOG_CACHE_LOCK = threading.Lock()
_LOG_SCAN_CACHE: dict[str, tuple[float, int]] = {}  # log_name → (mtime, error_count)

# ── Paths ──────────────────────────────────────────────────────────────────────
WORKSPACE = Path.home() / ".openclaw" / "workspace"
LOGS_DIR = Path.home() / ".openclaw" / "logs"
HB_DIR = LOGS_DIR / "cron-heartbeats"
DB_PATH = WORKSPACE / "ai-memory.db"
SESSIONS_FILE = (
    Path.home() / ".openclaw" / "agents" / "main" / "sessions" / "sessions.json"
)
CRON_JOBS_FILE = Path.home() / ".openclaw" / "cron" / "jobs.json"
CRON_STATE_FILE = Path.home() / ".openclaw" / "cron" / "jobs-state.json"
HISTORY_FILE = LOGS_DIR / "metrics-exporter-history.json"

# Shell-script crons that write heartbeat files to HB_DIR
# (OpenClaw-native agent-turn crons are tracked separately via jobs-state.json)
KNOWN_CRONS = [
    "observer-agent",
    "session-watchdog",
    "system-health-check",
]

# Cron max-age thresholds in seconds (matches cron-dead-man.sh)
CRON_MAX_AGE: dict[str, int] = {
    "session-watchdog": 3 * 3600,
    "system-health-check": 4 * 3600,
    "observer-agent": 3 * 3600,
}

# OpenClaw-native cron jobs tracked via jobs-state.json.
# Maps display slug → (OpenClaw cron job name, max_age_seconds)
NATIVE_CRON_MAP: dict[str, tuple[str, int]] = {
    "morning-briefing": ("Morning Briefing", 26 * 3600),
    "evening-briefing": ("Evening Briefing", 26 * 3600),
    "daily-session-reset": ("Daily Session Reset", 26 * 3600),
    "quota-monitoring-morning": ("API Quota Monitor (Morning)", 26 * 3600),
    "quota-monitoring-evening": ("API Quota Monitor (Evening)", 26 * 3600),
    "auto-update-system": ("Auto-Update System (Daily 2:00 AM EDT)", 26 * 3600),
}

SESSION_KEYS = [
    "agent:main:main",
    "agent:main:main:heartbeat",
    "agent:main:telegram:direct:8755120444",
]

# Key that resets per-message — used for "last activity" metric only
SESSION_ACTIVITY_KEY = "agent:main:telegram:direct:8755120444"

# File that anchors today's session start time (written once per calendar day)
SESSION_START_FILE = LOGS_DIR / "session-start.json"


# ── Metric helpers ─────────────────────────────────────────────────────────────


def _gauge(
    name: str, value: float, labels: dict[str, str] | None = None, help_text: str = ""
) -> Iterator[str]:
    """Yield Prometheus text lines for a gauge."""
    label_str = ""
    if labels:
        parts = ",".join(f'{k}="{v}"' for k, v in labels.items())
        label_str = f"{{{parts}}}"
    if help_text:
        yield f"# HELP {name} {help_text}"
        yield f"# TYPE {name} gauge"
    yield f"{name}{label_str} {value}"


def _increment_cron_counter(job: str, success: bool) -> None:
    status = "success" if success else "fail"
    with _COUNTER_LOCK:
        if job not in _CRON_RUNS_TOTAL:
            _CRON_RUNS_TOTAL[job] = {"success": 0, "fail": 0}
        _CRON_RUNS_TOTAL[job][status] += 1


def _increment_log_error_counter(log_name: str, delta: int) -> None:
    with _COUNTER_LOCK:
        _LOG_ERRORS_TOTAL[log_name] = _LOG_ERRORS_TOTAL.get(log_name, 0) + max(0, delta)


def _counter_metrics() -> list[str]:
    """Emit Prometheus counter metrics for cron runs and log errors."""
    lines: list[str] = []
    lines += ["# HELP openclaw_cron_runs_total Total cron runs since exporter start"]
    lines += ["# TYPE openclaw_cron_runs_total counter"]
    with _COUNTER_LOCK:
        cron_snap = {k: dict(v) for k, v in _CRON_RUNS_TOTAL.items()}
        log_snap = dict(_LOG_ERRORS_TOTAL)

    for job, counts in sorted(cron_snap.items()):
        for status, count in sorted(counts.items()):
            lines.append(
                f'openclaw_cron_runs_total{{job="{job}",status="{status}"}} {count}'
            )

    lines += [
        "# HELP openclaw_log_errors_total Total log errors seen since exporter start"
    ]
    lines += ["# TYPE openclaw_log_errors_total counter"]
    for log_name, count in sorted(log_snap.items()):
        lines.append(f'openclaw_log_errors_total{{log="{log_name}"}} {count}')

    return lines


def _cron_metrics() -> list[str]:
    lines: list[str] = []
    lines += ["# HELP openclaw_cron_last_run_age_seconds Seconds since cron last ran"]
    lines += ["# TYPE openclaw_cron_last_run_age_seconds gauge"]
    lines += ["# HELP openclaw_cron_last_exit_code Exit code of last run (0=success)"]
    lines += ["# TYPE openclaw_cron_last_exit_code gauge"]
    lines += [
        "# HELP openclaw_cron_stale Whether cron is past its max-age threshold (1=stale)"
    ]
    lines += ["# TYPE openclaw_cron_stale gauge"]
    lines += ["# HELP openclaw_cron_present Whether heartbeat file exists (1=yes)"]
    lines += ["# TYPE openclaw_cron_present gauge"]

    now = time.time()
    for job in KNOWN_CRONS:
        hb_file = HB_DIR / f"{job}.json"
        lbl = f'job="{job}"'
        if not hb_file.exists():
            lines.append(f"openclaw_cron_present{{{lbl}}} 0")
            lines.append(f"openclaw_cron_last_run_age_seconds{{{lbl}}} -1")
            lines.append(f"openclaw_cron_last_exit_code{{{lbl}}} -1")
            lines.append(f"openclaw_cron_stale{{{lbl}}} 1")
            continue

        try:
            data = json.loads(hb_file.read_text())
            ts = float(data.get("last_run_ts", 0))
            exit_code = int(data.get("exit_code", -1))
            age = now - ts if ts > 0 else -1
            max_age = CRON_MAX_AGE.get(job, 26 * 3600)
            stale = 1 if (age < 0 or age > max_age) else 0

            lines.append(f"openclaw_cron_present{{{lbl}}} 1")
            lines.append(f"openclaw_cron_last_run_age_seconds{{{lbl}}} {age:.0f}")
            lines.append(f"openclaw_cron_last_exit_code{{{lbl}}} {exit_code}")
            lines.append(f"openclaw_cron_stale{{{lbl}}} {stale}")
            _increment_cron_counter(job, success=(exit_code == 0))
        except Exception as e:
            lines.append(f"openclaw_cron_present{{{lbl}}} 0")
            lines.append(f"openclaw_cron_last_run_age_seconds{{{lbl}}} -1")
            lines.append(f"openclaw_cron_last_exit_code{{{lbl}}} -1")
            lines.append(f"openclaw_cron_stale{{{lbl}}} 1")

    return lines


def _native_cron_metrics() -> list[str]:
    """Collect metrics for OpenClaw-native agent-turn crons via jobs-state.json.

    These crons fire as agent turns and never write heartbeat files, so we read
    their last-run timestamps directly from the OpenClaw cron state database.
    """
    lines: list[str] = []
    lines += [
        "# HELP openclaw_native_cron_last_run_age_seconds Seconds since OpenClaw native cron last ran"
    ]
    lines += ["# TYPE openclaw_native_cron_last_run_age_seconds gauge"]
    lines += [
        "# HELP openclaw_native_cron_stale Whether native cron is past its max-age threshold (1=stale)"
    ]
    lines += ["# TYPE openclaw_native_cron_stale gauge"]
    lines += [
        "# HELP openclaw_native_cron_present Whether cron job exists in OpenClaw (1=yes)"
    ]
    lines += ["# TYPE openclaw_native_cron_present gauge"]

    now = time.time()

    # Build name → job_id map from jobs.json
    name_to_id: dict[str, str] = {}
    try:
        jobs_data = json.loads(CRON_JOBS_FILE.read_text())
        raw_jobs = jobs_data.get("jobs", [])
        job_iter = raw_jobs.values() if isinstance(raw_jobs, dict) else raw_jobs
        for job in job_iter:
            name_to_id[job.get("name", "")] = job.get("id", "")
    except Exception:
        pass

    # Load state map: job_id → updatedAtMs
    id_to_updated_ms: dict[str, int] = {}
    try:
        state_data = json.loads(CRON_STATE_FILE.read_text())
        for job_id, state in state_data.get("jobs", {}).items():
            ms = state.get("updatedAtMs", 0)
            if ms:
                id_to_updated_ms[job_id] = ms
    except Exception:
        pass

    for slug, (cron_name, max_age) in NATIVE_CRON_MAP.items():
        lbl = f'job="{slug}"'
        job_id = name_to_id.get(cron_name, "")
        updated_ms = id_to_updated_ms.get(job_id, 0) if job_id else 0

        if not job_id:
            # Job not found in OpenClaw config
            lines.append(f"openclaw_native_cron_present{{{lbl}}} 0")
            lines.append(f"openclaw_native_cron_last_run_age_seconds{{{lbl}}} -1")
            lines.append(f"openclaw_native_cron_stale{{{lbl}}} 1")
            continue

        lines.append(f"openclaw_native_cron_present{{{lbl}}} 1")

        if updated_ms == 0:
            lines.append(f"openclaw_native_cron_last_run_age_seconds{{{lbl}}} -1")
            lines.append(f"openclaw_native_cron_stale{{{lbl}}} 1")
        else:
            age = now - (updated_ms / 1000.0)
            stale = 1 if age > max_age else 0
            lines.append(
                f"openclaw_native_cron_last_run_age_seconds{{{lbl}}} {age:.0f}"
            )
            lines.append(f"openclaw_native_cron_stale{{{lbl}}} {stale}")
            _increment_cron_counter(slug, success=(stale == 0))

    return lines


def _memory_metrics() -> list[str]:
    lines: list[str] = []
    lines += [
        "# HELP openclaw_memory_entries_total Total memory entries in ai-memory.db"
    ]
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


def _ensure_session_start() -> float:
    """Return today's session start timestamp, creating the anchor file if needed."""
    import datetime

    today = datetime.date.today().isoformat()
    try:
        if SESSION_START_FILE.exists():
            rec = json.loads(SESSION_START_FILE.read_text())
            if rec.get("date") == today:
                return float(rec["start_ts"])
        # New day (or file missing) — write anchor now
        start_ts = time.time()
        SESSION_START_FILE.write_text(json.dumps({"date": today, "start_ts": start_ts}))
        return start_ts
    except Exception:
        return time.time()


def _session_metrics() -> list[str]:
    lines: list[str] = []
    lines += [
        "# HELP openclaw_session_last_activity_seconds Seconds since last Telegram message",
        "# TYPE openclaw_session_last_activity_seconds gauge",
        "# HELP openclaw_session_duration_seconds Seconds since today's session started",
        "# TYPE openclaw_session_duration_seconds gauge",
        "# HELP openclaw_session_stale Whether session is considered stale (>3600s, 1=stale)",
        "# TYPE openclaw_session_stale gauge",
    ]

    now_ms = time.time() * 1000
    now = time.time()

    # ── Session duration (monotonically rising, resets at midnight) ───────────
    session_start = _ensure_session_start()
    duration_sec = now - session_start
    lines.append(f"openclaw_session_duration_seconds {duration_sec:.0f}")

    # ── Last activity (time since last Telegram message) ─────────────────────
    if not SESSIONS_FILE.exists():
        lines.append("openclaw_session_last_activity_seconds -1")
        lines.append("openclaw_session_stale 1")
        return lines

    try:
        data = json.loads(SESSIONS_FILE.read_text())
        ts = int(data.get(SESSION_ACTIVITY_KEY, {}).get("updatedAt", 0))
        if ts == 0:
            lines.append("openclaw_session_last_activity_seconds -1")
            lines.append("openclaw_session_stale 1")
        else:
            activity_age = (now_ms - ts) / 1000
            stale = 1 if activity_age > 3600 else 0
            lines.append(f"openclaw_session_last_activity_seconds {activity_age:.0f}")
            lines.append(f"openclaw_session_stale {stale}")
    except Exception as e:
        lines.append(f"# ERROR reading sessions: {e}")
        lines.append("openclaw_session_last_activity_seconds -1")
        lines.append("openclaw_session_stale 1")

    return lines


def _log_metrics() -> list[str]:
    """Count recent error/warning lines in key log files.

    Results are cached by mtime — the file is only re-read when it changes.
    """
    lines: list[str] = []
    lines += [
        "# HELP openclaw_log_errors_recent Error/WARNING lines in last 200 log lines"
    ]
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
            current_mtime = log_path.stat().st_mtime

            # Check cache
            with _LOG_CACHE_LOCK:
                cached = _LOG_SCAN_CACHE.get(log_name)

            if cached is not None and cached[0] == current_mtime:
                # File unchanged — use cached count
                errors = cached[1]
            else:
                # File changed or not yet cached — rescan
                with open(log_path) as f:
                    tail = f.readlines()[-200:]
                errors = sum(
                    1
                    for l in tail
                    if any(w in l for w in ["ERROR", "STALE", "FAILED", "❌"])
                )
                with _LOG_CACHE_LOCK:
                    _LOG_SCAN_CACHE[log_name] = (current_mtime, errors)
                _increment_log_error_counter(log_name, errors)

            lines.append(f'openclaw_log_errors_recent{{log="{log_name}"}} {errors}')
        except Exception:
            lines.append(f'openclaw_log_errors_recent{{log="{log_name}"}} -1')

    return lines


def _system_metrics() -> list[str]:
    lines: list[str] = []

    # Session context file age
    sc_file = WORKSPACE / "SESSION_CONTEXT.md"
    if sc_file.exists():
        age = time.time() - sc_file.stat().st_mtime
        lines += [
            "# HELP openclaw_session_context_age_seconds Age of SESSION_CONTEXT.md"
        ]
        lines += ["# TYPE openclaw_session_context_age_seconds gauge"]
        lines.append(f"openclaw_session_context_age_seconds {age:.0f}")

    return lines


def _process_metrics() -> list[str]:
    """Collect CPU, memory, disk, and gateway process metrics."""
    lines: list[str] = []

    # Try psutil first (rich metrics), fall back to basic /proc-style
    try:
        import psutil

        # CPU
        cpu_pct = psutil.cpu_percent(interval=None)
        lines += ["# HELP openclaw_system_cpu_percent System CPU usage percent"]
        lines += ["# TYPE openclaw_system_cpu_percent gauge"]
        lines.append(f"openclaw_system_cpu_percent {cpu_pct:.1f}")

        # Memory
        mem = psutil.virtual_memory()
        lines += ["# HELP openclaw_system_memory_used_bytes System RAM used bytes"]
        lines += ["# TYPE openclaw_system_memory_used_bytes gauge"]
        lines.append(f"openclaw_system_memory_used_bytes {mem.used}")
        lines += ["# HELP openclaw_system_memory_total_bytes System RAM total bytes"]
        lines += ["# TYPE openclaw_system_memory_total_bytes gauge"]
        lines.append(f"openclaw_system_memory_total_bytes {mem.total}")
        lines += ["# HELP openclaw_system_memory_percent System RAM usage percent"]
        lines += ["# TYPE openclaw_system_memory_percent gauge"]
        lines.append(f"openclaw_system_memory_percent {mem.percent:.1f}")

        # Disk
        disk = psutil.disk_usage(str(Path.home()))
        lines += ["# HELP openclaw_disk_used_bytes Home disk used bytes"]
        lines += ["# TYPE openclaw_disk_used_bytes gauge"]
        lines.append(f"openclaw_disk_used_bytes {disk.used}")
        lines += ["# HELP openclaw_disk_free_bytes Home disk free bytes"]
        lines += ["# TYPE openclaw_disk_free_bytes gauge"]
        lines.append(f"openclaw_disk_free_bytes {disk.free}")
        lines += ["# HELP openclaw_disk_percent Home disk usage percent"]
        lines += ["# TYPE openclaw_disk_percent gauge"]
        lines.append(f"openclaw_disk_percent {disk.percent:.1f}")

        # This exporter's own process
        proc = psutil.Process(os.getpid())
        lines += [
            "# HELP openclaw_exporter_memory_rss_bytes Exporter process RSS bytes"
        ]
        lines += ["# TYPE openclaw_exporter_memory_rss_bytes gauge"]
        lines.append(f"openclaw_exporter_memory_rss_bytes {proc.memory_info().rss}")
        lines += [
            "# HELP openclaw_exporter_uptime_seconds Exporter process uptime seconds"
        ]
        lines += ["# TYPE openclaw_exporter_uptime_seconds gauge"]
        lines.append(
            f"openclaw_exporter_uptime_seconds {time.time() - proc.create_time():.0f}"
        )

        # Gateway process detection
        gateway_running = 0
        gateway_pid = -1
        for p in psutil.process_iter(["name", "cmdline", "pid"]):
            try:
                cmdline = " ".join(p.info.get("cmdline") or [])
                if "openclaw" in cmdline.lower() and "gateway" in cmdline.lower():
                    gateway_running = 1
                    gateway_pid = p.info["pid"]
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        lines += [
            "# HELP openclaw_gateway_running Whether the OpenClaw gateway process is running (1=yes)"
        ]
        lines += ["# TYPE openclaw_gateway_running gauge"]
        lines.append(f"openclaw_gateway_running {gateway_running}")

    except ImportError:
        # psutil not available — emit a stub so dashboards don't break
        lines += [
            "# HELP openclaw_system_cpu_percent System CPU usage percent (psutil unavailable)"
        ]
        lines += ["# TYPE openclaw_system_cpu_percent gauge"]
        lines.append("openclaw_system_cpu_percent -1")

    return lines


def collect_all_metrics() -> str:
    """Collect all metrics and return as Prometheus text."""
    sections = [
        _cron_metrics(),
        _native_cron_metrics(),
        _memory_metrics(),
        _session_metrics(),
        _log_metrics(),
        _system_metrics(),
        _process_metrics(),
        _counter_metrics(),
    ]
    all_lines: list[str] = []
    for section in sections:
        all_lines.extend(section)
        all_lines.append("")  # blank line between groups
    return "\n".join(all_lines) + "\n"


# ── Ring buffer persistence ────────────────────────────────────────────────────


def _save_history() -> None:
    """Persist ring buffer to disk for restart recovery."""
    global HISTORY_FILE
    try:
        with _HISTORY_LOCK:
            entries = list(_HISTORY)
        # Store as list of [timestamp, metrics_text] pairs
        # Limit to last 480 entries (~2h) to keep file size reasonable
        to_save = entries[-480:] if len(entries) > 480 else entries
        hf = HISTORY_FILE
        hf.parent.mkdir(parents=True, exist_ok=True)
        tmp = hf.with_suffix(".tmp")
        tmp.write_text(json.dumps([[ts, text] for ts, text in to_save]))
        tmp.rename(hf)
    except Exception:
        import traceback

        traceback.print_exc()


def _load_history() -> None:
    """Load persisted ring buffer from disk at startup."""
    global HISTORY_FILE
    hf = HISTORY_FILE
    if not hf.exists():
        return
    try:
        raw = json.loads(hf.read_text())
        entries = [(float(ts), text) for ts, text in raw if isinstance(text, str)]
        # Only load entries from the last 4 hours
        cutoff = time.time() - 4 * 3600
        fresh = [(ts, text) for ts, text in entries if ts >= cutoff]
        with _HISTORY_LOCK:
            for entry in fresh:
                _HISTORY.append(entry)
        if fresh:
            print(
                f"[openclaw-metrics] Loaded {len(fresh)} history entries from disk ({fresh[0][0]:.0f}–{fresh[-1][0]:.0f})",
                flush=True,
            )
    except Exception:
        import traceback

        traceback.print_exc()


def _handle_shutdown(signum, frame):
    print(
        f"[openclaw-metrics] Shutting down (signal {signum}), saving history...",
        flush=True,
    )
    _save_history()
    sys.exit(0)


# ── Background scraper thread ──────────────────────────────────────────────────


def _background_scraper():
    """Collect metrics every SCRAPE_INTERVAL seconds and store in ring buffer."""
    global _LAST_SCRAPE_TS
    scrape_count = 0
    while True:
        try:
            ts = time.time()
            text = collect_all_metrics()
            with _HISTORY_LOCK:
                _HISTORY.append((ts, text))
                _LAST_SCRAPE_TS = ts
            scrape_count += 1
            if scrape_count % 60 == 0:
                _save_history()
        except Exception:
            traceback.print_exc()
        time.sleep(_SCRAPE_INTERVAL)


def _start_background_scraper():
    t = threading.Thread(
        target=_background_scraper, daemon=True, name="metrics-scraper"
    )
    t.start()


# ── Prometheus text parser ─────────────────────────────────────────────────────

_SAMPLE_RE = re.compile(
    r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(\{([^}]*)\})?\s+([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?|-?Inf|NaN)"
)
_LABEL_RE = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)="([^"]*)"')


def parse_metrics_text(text: str) -> dict:
    """Parse Prometheus text format into {metric_name: [(labels_dict, float_value)]}."""
    result: dict[str, list[tuple[dict, float]]] = {}
    help_map: dict[str, str] = {}
    type_map: dict[str, str] = {}
    current_name = None

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("# HELP "):
            parts = line[7:].split(" ", 1)
            if len(parts) == 2:
                help_map[parts[0]] = parts[1]
            continue
        if line.startswith("# TYPE "):
            parts = line[7:].split(" ", 1)
            if len(parts) == 2:
                type_map[parts[0]] = parts[1]
            continue
        if line.startswith("#"):
            continue
        m = _SAMPLE_RE.match(line)
        if not m:
            continue
        name = m.group(1)
        labels_str = m.group(3) or ""
        val_str = m.group(4)
        try:
            value = float(val_str)
        except ValueError:
            continue
        labels: dict[str, str] = {}
        for lm in _LABEL_RE.finditer(labels_str):
            labels[lm.group(1)] = lm.group(2)
        result.setdefault(name, []).append((labels, value))

    return {"series": result, "help": help_map, "type": type_map}


# ── PromQL mini-evaluator ──────────────────────────────────────────────────────

_SELECTOR_RE = re.compile(r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(\{([^}]*)\})?$")


def _match_labels(labels: dict, filter_str: str) -> bool:
    """Check if a labels dict matches a PromQL label filter string.
    Supports =, =~, !=, !~ operators.
    """
    # Match label matchers: key op "value"
    for m in re.finditer(r'([a-zA-Z_][a-zA-Z0-9_]*)(=~|!=|!~|=)"([^"]*)"', filter_str):
        k, op, v = m.group(1), m.group(2), m.group(3)
        actual = labels.get(k, "")
        if op == "=":
            if actual != v:
                return False
        elif op == "!=":
            if actual == v:
                return False
        elif op == "=~":
            if not re.fullmatch(v, actual):
                return False
        elif op == "!~":
            if re.fullmatch(v, actual):
                return False
    return True


def eval_instant(parsed: dict, query: str, ts: float) -> list[dict]:
    """Evaluate a simplified PromQL query and return Prometheus vector result."""
    series = parsed["series"]
    query = query.strip()

    # ── Aggregation operators: sum/avg/min/max/count ──────────────────────────
    # Matches: func(inner) or func(inner) by (labels) or func(inner) without (labels)
    agg_m = re.match(
        r"^(sum|avg|min|max|count)\s*\((.+?)\)(?:\s+(?:by|without)\s*\(([^)]*)\))?$",
        query,
        re.IGNORECASE,
    )
    if agg_m:
        func = agg_m.group(1).lower()
        inner = agg_m.group(2).strip()
        by_labels_str = agg_m.group(3) or ""
        by_labels = [l.strip() for l in by_labels_str.split(",") if l.strip()]
        inner_results = eval_instant(parsed, inner, ts)
        if not inner_results:
            return []
        if not by_labels:
            vals = [float(r["value"][1]) for r in inner_results]
            if func == "sum":
                result_val = sum(vals)
            elif func == "avg":
                result_val = sum(vals) / len(vals)
            elif func == "min":
                result_val = min(vals)
            elif func == "max":
                result_val = max(vals)
            elif func == "count":
                result_val = float(len(vals))
            else:
                result_val = sum(vals)
            return [{"metric": {}, "value": [ts, str(result_val)]}]
        # grouped by labels
        groups: dict[tuple, list[float]] = {}
        group_labels: dict[tuple, dict] = {}
        for r in inner_results:
            key = tuple(r["metric"].get(l, "") for l in by_labels)
            groups.setdefault(key, []).append(float(r["value"][1]))
            group_labels[key] = {l: r["metric"].get(l, "") for l in by_labels}
        results = []
        for key, vals in groups.items():
            if func == "sum":
                v = sum(vals)
            elif func == "avg":
                v = sum(vals) / len(vals)
            elif func == "min":
                v = min(vals)
            elif func == "max":
                v = max(vals)
            elif func == "count":
                v = float(len(vals))
            else:
                v = sum(vals)
            results.append({"metric": group_labels[key], "value": [ts, str(v)]})
        return results

    # ── topk / bottomk ────────────────────────────────────────────────────────
    topk_m = re.match(
        r"^(topk|bottomk)\s*\(\s*(\d+)\s*,\s*(.+?)\s*\)$", query, re.IGNORECASE
    )
    if topk_m:
        func = topk_m.group(1).lower()
        k = int(topk_m.group(2))
        inner = topk_m.group(3).strip()
        inner_results = eval_instant(parsed, inner, ts)
        sorted_results = sorted(
            inner_results,
            key=lambda r: float(r["value"][1]),
            reverse=(func == "topk"),
        )
        return sorted_results[:k]

    # ── rate() / irate() / increase() ────────────────────────────────────────
    # These are range-vector functions in real PromQL but our metrics are gauges,
    # not counters, so we approximate: compute per-second change using ring buffer.
    rate_m = re.match(
        r"^(rate|irate|increase)\s*\((.+?)\[([^\]]+)\]\s*\)$", query, re.IGNORECASE
    )
    if rate_m:
        func = rate_m.group(1).lower()
        metric_expr = rate_m.group(2).strip()
        # For instant eval, we approximate using the most-recent two history snapshots
        with _HISTORY_LOCK:
            hist = list(_HISTORY)
        if len(hist) < 2:
            # No history — return zeros for each series
            base = eval_instant(parsed, metric_expr, ts)
            return [{"metric": r["metric"], "value": [ts, "0"]} for r in base]
        # Use the two most recent snapshots
        ts2, text2 = hist[-1]
        ts1, text1 = hist[-2]
        dt = ts2 - ts1
        if dt <= 0:
            base = eval_instant(parsed, metric_expr, ts)
            return [{"metric": r["metric"], "value": [ts, "0"]} for r in base]
        p1 = parse_metrics_text(text1)
        p2 = parse_metrics_text(text2)
        r1 = {
            json.dumps(r["metric"], sort_keys=True): float(r["value"][1])
            for r in eval_instant(p1, metric_expr, ts1)
        }
        r2_list = eval_instant(p2, metric_expr, ts2)
        results = []
        for r in r2_list:
            key = json.dumps(r["metric"], sort_keys=True)
            v2 = float(r["value"][1])
            v1 = r1.get(key, v2)
            delta = v2 - v1
            if func == "increase":
                rate_val = delta
            else:  # rate or irate: per-second
                rate_val = delta / dt if dt > 0 else 0.0
            results.append(
                {"metric": r["metric"], "value": [ts, str(max(0.0, rate_val))]}
            )
        return results

    # ── label_values() — used by Grafana template variables ──────────────────
    lv_m = re.match(
        r"^label_values\s*\(\s*(.+?)\s*,\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)$",
        query,
        re.IGNORECASE,
    )
    if lv_m:
        metric_expr = lv_m.group(1).strip()
        label_name = lv_m.group(2).strip()
        base = eval_instant(parsed, metric_expr, ts)
        values = sorted(
            {r["metric"].get(label_name, "") for r in base if label_name in r["metric"]}
        )
        return [
            {"metric": {"__name__": label_name, label_name: v}, "value": [ts, "1"]}
            for v in values
        ]

    # ── Simple selector ───────────────────────────────────────────────────────
    m = _SELECTOR_RE.match(query)
    if m:
        name = m.group(1)
        filter_str = m.group(3) or ""
        if name not in series:
            return []
        results = []
        for labels, value in series[name]:
            if filter_str and not _match_labels(labels, filter_str):
                continue
            metric = {"__name__": name, **labels}
            results.append({"metric": metric, "value": [ts, str(value)]})
        return results

    return []


def eval_range(
    parsed: dict, query: str, start: float, end: float, step: float
) -> list[dict]:
    """Return a matrix result using historical ring buffer data when available."""
    # Build a map of timestamp → parsed snapshot from history
    with _HISTORY_LOCK:
        history_snap = list(_HISTORY)  # [(ts, text), ...]

    # Filter history to the requested range
    in_range = [(ts, text) for ts, text in history_snap if start <= ts <= end + step]

    if len(in_range) < 2:
        # Fall back to current-instant duplication (original behavior)
        instant = eval_instant(parsed, query, end)
        timestamps = []
        t = start
        while t <= end + 0.001:
            timestamps.append(t)
            t += step
        if not timestamps or timestamps[-1] < end:
            timestamps.append(end)
        results = []
        for r in instant:
            val = r["value"][1]
            results.append(
                {"metric": r["metric"], "values": [[t, val] for t in timestamps]}
            )
        return results

    # Build a time-bucketed map: for each step bucket, use the nearest historical sample
    timestamps = []
    t = start
    while t <= end + 0.001:
        timestamps.append(t)
        t += step
    if not timestamps or timestamps[-1] < end:
        timestamps.append(end)

    # For each timestamp bucket, find the closest historical sample
    def _find_nearest(ts: float) -> tuple | None:
        best = None
        best_diff = float("inf")
        for h_ts, h_text in in_range:
            diff = abs(h_ts - ts)
            if diff < best_diff:
                best_diff = diff
                best = (h_ts, h_text)
        return best

    # Group results by metric identity
    metric_series: dict[str, dict] = {}  # key → {"metric": {}, "values": []}

    for bucket_ts in timestamps:
        nearest = _find_nearest(bucket_ts)
        if nearest is None:
            continue
        _, h_text = nearest
        h_parsed = parse_metrics_text(h_text)
        instant = eval_instant(h_parsed, query, bucket_ts)
        for r in instant:
            # Build a stable key from metric labels
            key = json.dumps(r["metric"], sort_keys=True)
            if key not in metric_series:
                metric_series[key] = {"metric": r["metric"], "values": []}
            metric_series[key]["values"].append([bucket_ts, r["value"][1]])

    return list(metric_series.values()) if metric_series else []


# ── HTTP server ────────────────────────────────────────────────────────────────


class ReusePortHTTPServer(HTTPServer):
    """HTTPServer subclass that sets SO_REUSEADDR and SO_REUSEPORT before bind."""

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            try:
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except OSError:
                pass
        super().server_bind()


class MetricsHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        params = parse_qs(parsed_url.query)

        if path in ("/metrics", "/"):
            try:
                body = collect_all_metrics().encode()
            except Exception:
                print("[openclaw-metrics] ERROR in collect_all_metrics:", flush=True)
                traceback.print_exc()
                error_body = b"# ERROR collecting metrics\n"
                self.send_response(500)
                self.send_header(
                    "Content-Type", "text/plain; version=0.0.4; charset=utf-8"
                )
                self.send_header("Content-Length", str(len(error_body)))
                self.end_headers()
                self.wfile.write(error_body)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        elif path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")

        elif path == "/api/v1/metadata":
            raw = collect_all_metrics()
            p = parse_metrics_text(raw)
            data = {
                name: [
                    {
                        "type": p["type"].get(name, "gauge"),
                        "help": p["help"].get(name, ""),
                    }
                ]
                for name in p["series"]
            }
            self._send_json({"status": "success", "data": data})

        elif path == "/api/v1/labels":
            raw = collect_all_metrics()
            p = parse_metrics_text(raw)
            label_names: set[str] = {"__name__"}
            for series_list in p["series"].values():
                for labels, _ in series_list:
                    label_names.update(labels.keys())
            self._send_json({"status": "success", "data": sorted(label_names)})

        elif re.match(r"^/api/v1/label/([^/]+)/values$", path):
            label_name = re.match(r"^/api/v1/label/([^/]+)/values$", path).group(1)
            raw = collect_all_metrics()
            p = parse_metrics_text(raw)
            if label_name == "__name__":
                values = sorted(p["series"].keys())
            else:
                vals: set[str] = set()
                for series_list in p["series"].values():
                    for labels, _ in series_list:
                        if label_name in labels:
                            vals.add(labels[label_name])
                values = sorted(vals)
            self._send_json({"status": "success", "data": values})

        elif path == "/api/v1/query":
            query = params.get("query", [""])[0]
            ts_str = params.get("time", [str(time.time())])[0]
            try:
                ts = float(ts_str)
            except ValueError:
                ts = time.time()
            raw = collect_all_metrics()
            p = parse_metrics_text(raw)
            result = eval_instant(p, query, ts)
            self._send_json(
                {
                    "status": "success",
                    "data": {"resultType": "vector", "result": result},
                }
            )

        elif path == "/api/v1/query_range":
            query = params.get("query", [""])[0]
            try:
                start = float(params.get("start", [str(time.time() - 3600)])[0])
                end = float(params.get("end", [str(time.time())])[0])
                step = float(params.get("step", ["60"])[0])
            except ValueError:
                start, end, step = time.time() - 3600, time.time(), 60.0
            raw = collect_all_metrics()
            p = parse_metrics_text(raw)
            result = eval_range(p, query, start, end, step)
            self._send_json(
                {
                    "status": "success",
                    "data": {"resultType": "matrix", "result": result},
                }
            )

        elif path == "/api/v1/series":
            raw = collect_all_metrics()
            p = parse_metrics_text(raw)
            result = []
            for name, series_list in p["series"].items():
                for labels, _ in series_list:
                    result.append({"__name__": name, **labels})
            self._send_json({"status": "success", "data": result})

        elif path == "/api/v1/status/buildinfo":
            # Grafana probes this to detect Prometheus version; return a stub.
            self._send_json(
                {
                    "status": "success",
                    "data": {
                        "version": "2.99.0",
                        "revision": "openclaw-exporter",
                        "branch": "main",
                        "buildUser": "openclaw",
                        "buildDate": "2026-04-24",
                        "goVersion": "go1.21.0",
                    },
                }
            )

        elif path in ("/api/v1/rules", "/api/v1/alerts"):
            # No alerting rules configured; return empty list.
            self._send_json({"status": "success", "data": {"groups": []}})

        elif path == "/api/v1/query_exemplars":
            # No exemplars; return empty list.
            self._send_json({"status": "success", "data": []})

        else:
            self._send_json({"status": "error", "error": "not found"}, status=404)

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

    # Register shutdown handlers
    signal.signal(signal.SIGTERM, _handle_shutdown)
    # SIGINT already handled by KeyboardInterrupt in serve_forever

    # Load persisted history before starting background scraper
    _load_history()

    server = ReusePortHTTPServer(("0.0.0.0", args.port), MetricsHandler)
    print(
        f"[openclaw-metrics] PID={os.getpid()} Serving on http://0.0.0.0:{args.port}/metrics",
        flush=True,
    )

    _start_background_scraper()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[openclaw-metrics] Stopped.", flush=True)
    except Exception:
        print("[openclaw-metrics] FATAL: unhandled exception:", flush=True)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
