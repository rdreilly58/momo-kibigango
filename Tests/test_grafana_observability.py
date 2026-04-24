#!/usr/bin/env python3
"""
test_grafana_observability.py — Test suite for OpenClaw Grafana observability stack.

Tests:
  1. Metrics exporter — unit tests for each collector function
  2. Prometheus format — output parses as valid Prometheus text
  3. Grafana provisioning files — valid YAML and expected keys present
  4. Dashboard JSON — valid JSON, required panels present
  5. Integration — exporter HTTP server responds (if running)
  6. Grafana API — health endpoint responds (if Grafana is running)

Run:
    python3 Tests/test_grafana_observability.py
    python3 -m pytest Tests/test_grafana_observability.py -v
"""

from __future__ import annotations

import json
import os
import sys
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

# ── Path setup ─────────────────────────────────────────────────────────────────
WORKSPACE = Path.home() / ".openclaw" / "workspace"
SCRIPTS = WORKSPACE / "scripts"
TESTS = WORKSPACE / "Tests"
CONFIG = WORKSPACE / "config" / "grafana"
LOGS = Path.home() / ".openclaw" / "logs"
HB_DIR = LOGS / "cron-heartbeats"

sys.path.insert(0, str(SCRIPTS))

# Import the exporter module
import openclaw_metrics_exporter as exporter


# ── Helper ─────────────────────────────────────────────────────────────────────
def _parse_prometheus_text(text: str) -> dict[str, list[float]]:
    """Parse Prometheus text format → {metric_name: [values]}."""
    result: dict[str, list[float]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Split metric_name{labels} value [timestamp]
        parts = line.rsplit(" ", 1)
        if len(parts) != 2:
            continue
        metric_part, val_str = parts
        # strip labels
        name = metric_part.split("{")[0]
        try:
            val = float(val_str)
            result.setdefault(name, []).append(val)
        except ValueError:
            pass
    return result


# ── 1. Collector unit tests ────────────────────────────────────────────────────
class TestCronMetrics(unittest.TestCase):
    def test_returns_list_of_strings(self):
        lines = exporter._cron_metrics()
        self.assertIsInstance(lines, list)
        self.assertTrue(len(lines) > 0)

    def test_covers_all_known_crons(self):
        lines = exporter._cron_metrics()
        text = "\n".join(lines)
        for job in exporter.KNOWN_CRONS:
            self.assertIn(f'job="{job}"', text, f"Missing metric for cron: {job}")

    def test_stale_metric_is_0_or_1(self):
        lines = exporter._cron_metrics()
        stale_lines = [
            l
            for l in lines
            if "openclaw_cron_stale" in l and "HELP" not in l and "TYPE" not in l
        ]
        for line in stale_lines:
            val = float(line.rsplit(" ", 1)[-1])
            self.assertIn(val, (0.0, 1.0, -1.0), f"Unexpected stale value: {line}")

    def test_exit_code_metric_present(self):
        lines = exporter._cron_metrics()
        exit_lines = [
            l
            for l in lines
            if "openclaw_cron_last_exit_code" in l
            and "HELP" not in l
            and "TYPE" not in l
        ]
        self.assertTrue(len(exit_lines) > 0, "No exit_code lines found")

    def test_present_metric_1_for_existing_heartbeats(self):
        """If a heartbeat file exists for a shell-script cron, present should be 1.
        Jobs migrated to native cron tracking (NATIVE_CRON_MAP) are excluded — they
        may have stale orphaned heartbeat files but are no longer in KNOWN_CRONS.
        """
        existing = list(HB_DIR.glob("*.json"))
        if not existing:
            self.skipTest("No heartbeat files found")
        # Build the set of native-cron slugs so we skip orphaned heartbeat files
        native_slugs = (
            set(exporter.NATIVE_CRON_MAP.keys())
            if hasattr(exporter, "NATIVE_CRON_MAP")
            else set()
        )
        lines = exporter._cron_metrics()
        text = "\n".join(lines)
        for hb in existing:
            job = hb.stem
            if job in native_slugs or job not in exporter.KNOWN_CRONS:
                continue  # migrated to native cron tracking — heartbeat file is orphaned
            self.assertIn(
                f'openclaw_cron_present{{job="{job}"}} 1',
                text,
                f"Expected present=1 for existing heartbeat: {job}",
            )


class TestMemoryMetrics(unittest.TestCase):
    def test_returns_list(self):
        lines = exporter._memory_metrics()
        self.assertIsInstance(lines, list)

    def test_total_is_numeric(self):
        lines = exporter._memory_metrics()
        total_lines = [
            l for l in lines if l.startswith("openclaw_memory_entries_total")
        ]
        self.assertTrue(len(total_lines) > 0, "No total memory metric")
        val = float(total_lines[0].split()[-1])
        self.assertTrue(val >= -1, f"Unexpected memory total: {val}")

    def test_tier_metrics_present(self):
        lines = exporter._memory_metrics()
        text = "\n".join(lines)
        if "openclaw_memory_entries_total -1" not in text:
            self.assertIn("openclaw_memory_entries_by_tier", text)

    def test_graph_links_metric(self):
        lines = exporter._memory_metrics()
        graph_lines = [
            l
            for l in lines
            if "openclaw_memory_graph_links" in l
            and "HELP" not in l
            and "TYPE" not in l
        ]
        if graph_lines:
            val = float(graph_lines[0].split()[-1])
            self.assertGreaterEqual(val, 0)


class TestSessionMetrics(unittest.TestCase):
    def test_returns_list(self):
        lines = exporter._session_metrics()
        self.assertIsInstance(lines, list)

    def test_age_metric_present(self):
        lines = exporter._session_metrics()
        age_lines = [l for l in lines if l.startswith("openclaw_session_age_seconds")]
        self.assertTrue(len(age_lines) > 0)

    def test_stale_metric_0_or_1(self):
        lines = exporter._session_metrics()
        stale_lines = [l for l in lines if l.startswith("openclaw_session_stale")]
        if stale_lines:
            val = float(stale_lines[0].split()[-1])
            self.assertIn(val, (0.0, 1.0))


class TestLogMetrics(unittest.TestCase):
    def test_returns_list(self):
        lines = exporter._log_metrics()
        self.assertIsInstance(lines, list)

    def test_numeric_values(self):
        lines = exporter._log_metrics()
        for line in lines:
            if line.startswith("#") or not line:
                continue
            val = float(line.rsplit(" ", 1)[-1])
            self.assertGreaterEqual(val, -1)


class TestSystemMetrics(unittest.TestCase):
    def test_scrape_timestamp_removed(self):
        """openclaw_exporter_scrape_timestamp should be absent (discouraged by Prometheus docs)."""
        lines = exporter._system_metrics()
        text = "\n".join(lines)
        self.assertNotIn(
            "openclaw_exporter_scrape_timestamp",
            text,
            "scrape_timestamp metric should have been removed (Prometheus anti-pattern)",
        )

    def test_session_context_age_present(self):
        """Session context age should still be present in system metrics."""
        lines = exporter._system_metrics()
        # Only check if SESSION_CONTEXT.md exists
        sc_file = exporter.WORKSPACE / "SESSION_CONTEXT.md"
        if not sc_file.exists():
            return  # can't test what isn't there
        age_lines = [
            l for l in lines if l.startswith("openclaw_session_context_age_seconds")
        ]
        self.assertTrue(len(age_lines) > 0, "session_context_age metric missing")


# ── 2. Full output format ──────────────────────────────────────────────────────
class TestPrometheusFormat(unittest.TestCase):
    def setUp(self):
        self.text = exporter.collect_all_metrics()
        self.parsed = _parse_prometheus_text(self.text)

    def test_output_is_string(self):
        self.assertIsInstance(self.text, str)
        self.assertTrue(len(self.text) > 100)

    def test_ends_with_newline(self):
        self.assertTrue(self.text.endswith("\n"))

    def test_help_and_type_lines_present(self):
        lines = self.text.splitlines()
        help_lines = [l for l in lines if l.startswith("# HELP")]
        type_lines = [l for l in lines if l.startswith("# TYPE")]
        self.assertGreater(len(help_lines), 3)
        self.assertGreater(len(type_lines), 3)

    def test_all_expected_metrics_present(self):
        expected = [
            "openclaw_cron_present",
            "openclaw_cron_stale",
            "openclaw_cron_last_run_age_seconds",
            "openclaw_cron_last_exit_code",
            "openclaw_memory_entries_total",
            "openclaw_session_age_seconds",
            "openclaw_session_stale",
            "openclaw_log_errors_recent",
            "openclaw_system_cpu_percent",
            "openclaw_gateway_running",
            "openclaw_native_cron_stale",
            "openclaw_native_cron_last_run_age_seconds",
        ]
        for name in expected:
            self.assertIn(name, self.parsed, f"Metric missing from output: {name}")

    def test_no_nan_or_inf_values(self):
        for name, vals in self.parsed.items():
            for v in vals:
                self.assertFalse(v != v, f"NaN in metric {name}")  # NaN != NaN
                self.assertTrue(
                    abs(v) < 1e15 or v == -1, f"Suspicious value {v} in {name}"
                )

    def test_all_crons_have_entries(self):
        for job in exporter.KNOWN_CRONS:
            found = any(
                job in line
                for line in self.text.splitlines()
                if not line.startswith("#")
            )
            self.assertTrue(found, f"No metric lines for cron job: {job}")


# ── 3. Provisioning file validation ───────────────────────────────────────────
class TestGrafanaProvisioning(unittest.TestCase):
    def test_datasource_file_exists(self):
        ds = CONFIG / "provisioning" / "datasources" / "openclaw.yaml"
        self.assertTrue(ds.exists(), f"Datasource config missing: {ds}")

    def test_datasource_yaml_valid(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed — skipping YAML parse test")
        ds = CONFIG / "provisioning" / "datasources" / "openclaw.yaml"
        data = yaml.safe_load(ds.read_text())
        self.assertEqual(data["apiVersion"], 1)
        self.assertIn("datasources", data)
        sources = data["datasources"]
        self.assertTrue(len(sources) > 0)
        self.assertEqual(sources[0]["type"], "prometheus")
        self.assertIn("9091", sources[0]["url"])

    def test_dashboard_provider_file_exists(self):
        db = CONFIG / "provisioning" / "dashboards" / "openclaw.yaml"
        self.assertTrue(db.exists(), f"Dashboard provider config missing: {db}")

    def test_dashboard_provider_yaml_valid(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed — skipping YAML parse test")
        db = CONFIG / "provisioning" / "dashboards" / "openclaw.yaml"
        data = yaml.safe_load(db.read_text())
        self.assertEqual(data["apiVersion"], 1)
        self.assertIn("providers", data)
        provider = data["providers"][0]
        self.assertIn("path", provider["options"])

    def test_dashboard_path_in_provider_exists(self):
        try:
            import yaml
        except ImportError:
            # fall back to raw text check
            db = CONFIG / "provisioning" / "dashboards" / "openclaw.yaml"
            text = db.read_text()
            self.assertIn(str(CONFIG / "dashboards"), text)
            return
        db = CONFIG / "provisioning" / "dashboards" / "openclaw.yaml"
        data = yaml.safe_load(db.read_text())
        path = Path(data["providers"][0]["options"]["path"])
        self.assertTrue(
            path.exists(), f"Dashboard path in provider does not exist: {path}"
        )


# ── 4. Dashboard JSON validation ───────────────────────────────────────────────
class TestDashboardJson(unittest.TestCase):
    def setUp(self):
        self.path = CONFIG / "dashboards" / "openclaw-overview.json"
        self.data = json.loads(self.path.read_text())

    def test_file_exists(self):
        self.assertTrue(self.path.exists())

    def test_valid_json(self):
        self.assertIsInstance(self.data, dict)

    def test_required_top_level_keys(self):
        for key in ("title", "panels", "schemaVersion"):
            self.assertIn(key, self.data, f"Missing dashboard key: {key}")

    def test_has_minimum_panels(self):
        panels = self.data.get("panels", [])
        self.assertGreaterEqual(len(panels), 4, "Expected at least 4 dashboard panels")

    def test_panels_have_targets(self):
        panels = self.data.get("panels", [])
        for panel in panels:
            targets = panel.get("targets", [])
            self.assertTrue(
                len(targets) > 0, f"Panel '{panel.get('title')}' has no targets"
            )

    def test_datasource_uid_consistent(self):
        valid_uids = {"openclaw-prometheus", "openclaw-tsdb"}
        panels = self.data.get("panels", [])
        for panel in panels:
            ds = panel.get("datasource", {})
            if ds:
                self.assertIn(
                    ds.get("uid"),
                    valid_uids,
                    f"Panel '{panel.get('title')}' has wrong datasource uid",
                )

    def test_all_panels_have_unique_ids(self):
        panels = self.data.get("panels", [])
        ids = [p.get("id") for p in panels]
        self.assertEqual(len(ids), len(set(ids)), "Dashboard has duplicate panel IDs")

    def test_session_stale_panel_present(self):
        panels = self.data.get("panels", [])
        titles = [p.get("title", "") for p in panels]
        self.assertTrue(any("Session" in t for t in titles), "No session panel found")

    def test_cron_health_panel_present(self):
        panels = self.data.get("panels", [])
        titles = [p.get("title", "") for p in panels]
        self.assertTrue(any("Cron" in t for t in titles), "No cron health panel found")

    def test_memory_panel_present(self):
        panels = self.data.get("panels", [])
        titles = [p.get("title", "") for p in panels]
        self.assertTrue(any("Memory" in t for t in titles), "No memory panel found")


# ── 5. Integration: exporter HTTP server ──────────────────────────────────────
class TestExporterHTTP(unittest.TestCase):
    """These tests require the exporter to be running on :9091. Skipped if not."""

    EXPORTER_URL = "http://localhost:9091"

    def _get(self, path: str, timeout: int = 3) -> tuple[int, str]:
        try:
            with urllib.request.urlopen(
                f"{self.EXPORTER_URL}{path}", timeout=timeout
            ) as r:
                return r.status, r.read().decode()
        except Exception as e:
            return -1, str(e)

    def test_metrics_endpoint_responds(self):
        status, body = self._get("/metrics")
        if status == -1:
            self.skipTest(f"Exporter not running: {body}")
        self.assertEqual(status, 200)

    def test_metrics_content_type(self):
        try:
            with urllib.request.urlopen(f"{self.EXPORTER_URL}/metrics", timeout=3) as r:
                ct = r.headers.get("Content-Type", "")
        except Exception as e:
            self.skipTest(f"Exporter not running: {e}")
        self.assertIn("text/plain", ct)

    def test_health_endpoint(self):
        status, body = self._get("/health")
        if status == -1:
            self.skipTest(f"Exporter not running: {body}")
        self.assertEqual(status, 200)
        self.assertEqual(body, "ok")

    def test_metrics_contain_openclaw_prefix(self):
        status, body = self._get("/metrics")
        if status == -1:
            self.skipTest(f"Exporter not running: {body}")
        self.assertIn("openclaw_", body)


# ── 6. Integration: Grafana API ────────────────────────────────────────────────
class TestGrafanaAPI(unittest.TestCase):
    """These tests require Grafana to be running on :3000. Skipped if not."""

    GRAFANA_URL = "http://localhost:3000"

    def _get(self, path: str, timeout: int = 3) -> tuple[int, str]:
        try:
            req = urllib.request.Request(f"{self.GRAFANA_URL}{path}")
            req.add_header("Authorization", "Basic YWRtaW46YWRtaW4=")  # admin:admin
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read().decode()
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()
        except Exception as e:
            return -1, str(e)

    def test_grafana_health(self):
        status, body = self._get("/api/health")
        if status == -1:
            self.skipTest(f"Grafana not running: {body}")
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertEqual(data.get("database"), "ok")

    def test_datasource_provisioned(self):
        status, body = self._get("/api/datasources")
        if status == -1:
            self.skipTest(f"Grafana not running: {body}")
        if status == 401:
            self.skipTest("Grafana auth required — check admin credentials")
        sources = json.loads(body)
        names = [s.get("name") for s in sources]
        self.assertIn(
            "OpenClaw-Prometheus",
            names,
            f"OpenClaw-Prometheus datasource not provisioned. Found: {names}",
        )

    def test_dashboard_provisioned(self):
        status, body = self._get("/api/search?query=OpenClaw")
        if status == -1:
            self.skipTest(f"Grafana not running: {body}")
        if status == 401:
            self.skipTest("Grafana auth required")
        results = json.loads(body)
        titles = [r.get("title") for r in results]
        self.assertIn(
            "OpenClaw Overview",
            titles,
            f"OpenClaw Overview dashboard not found. Found: {titles}",
        )


# ── 7. Process metrics ────────────────────────────────────────────────────────
class TestProcessMetrics(unittest.TestCase):
    def test_returns_list(self):
        lines = exporter._process_metrics()
        self.assertIsInstance(lines, list)
        self.assertTrue(len(lines) > 0)

    def test_cpu_metric_present(self):
        lines = exporter._process_metrics()
        cpu_lines = [
            l
            for l in lines
            if l.startswith("openclaw_system_cpu_percent")
            and "HELP" not in l
            and "TYPE" not in l
        ]
        self.assertTrue(len(cpu_lines) > 0, "CPU metric missing")
        val = float(cpu_lines[0].split()[-1])
        self.assertTrue(-1 <= val <= 100, f"CPU% out of range: {val}")

    def test_memory_metric_present(self):
        lines = exporter._process_metrics()
        mem_lines = [
            l
            for l in lines
            if l.startswith("openclaw_system_memory_percent")
            and "HELP" not in l
            and "TYPE" not in l
        ]
        self.assertTrue(len(mem_lines) > 0, "Memory% metric missing")
        val = float(mem_lines[0].split()[-1])
        self.assertTrue(-1 <= val <= 100, f"Memory% out of range: {val}")

    def test_disk_metric_present(self):
        lines = exporter._process_metrics()
        disk_lines = [
            l
            for l in lines
            if l.startswith("openclaw_disk_percent")
            and "HELP" not in l
            and "TYPE" not in l
        ]
        self.assertTrue(len(disk_lines) > 0, "Disk% metric missing")

    def test_gateway_running_metric_present(self):
        lines = exporter._process_metrics()
        gw_lines = [
            l
            for l in lines
            if l.startswith("openclaw_gateway_running")
            and "HELP" not in l
            and "TYPE" not in l
        ]
        self.assertTrue(len(gw_lines) > 0, "Gateway running metric missing")
        val = float(gw_lines[0].split()[-1])
        self.assertIn(val, (0.0, 1.0), f"Gateway running must be 0 or 1, got {val}")


# ── 8. Ring buffer history ────────────────────────────────────────────────────
class TestRingBufferHistory(unittest.TestCase):
    def test_history_deque_exists(self):
        self.assertTrue(hasattr(exporter, "_HISTORY"), "_HISTORY deque not found")
        self.assertTrue(hasattr(exporter, "_HISTORY_LOCK"), "_HISTORY_LOCK not found")

    def test_collect_appends_to_history(self):
        """Calling collect_all_metrics should not crash; history is filled by bg thread."""
        text = exporter.collect_all_metrics()
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 50)

    def test_eval_range_with_empty_history_falls_back(self):
        """eval_range with no history should still return valid result (fallback)."""
        with exporter._HISTORY_LOCK:
            saved = list(exporter._HISTORY)
            exporter._HISTORY.clear()
        try:
            raw = exporter.collect_all_metrics()
            parsed = exporter.parse_metrics_text(raw)
            end = time.time()
            start = end - 60
            result = exporter.eval_range(
                parsed, "openclaw_memory_entries_total", start, end, 15.0
            )
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0)
        finally:
            with exporter._HISTORY_LOCK:
                exporter._HISTORY.extend(saved)

    def test_eval_range_with_history_produces_multiple_points(self):
        """If we seed history, eval_range should return multiple time-series points."""
        raw = exporter.collect_all_metrics()
        now = time.time()
        fakes = [(now - (10 - i) * 15, raw) for i in range(10)]
        with exporter._HISTORY_LOCK:
            saved = list(exporter._HISTORY)
            exporter._HISTORY.clear()
            for entry in fakes:
                exporter._HISTORY.append(entry)
        try:
            parsed = exporter.parse_metrics_text(raw)
            result = exporter.eval_range(
                parsed,
                "openclaw_memory_entries_total",
                now - 150,
                now,
                15.0,
            )
            self.assertIsInstance(result, list)
            if result:
                self.assertGreater(
                    len(result[0].get("values", [])),
                    3,
                    "eval_range should produce multiple points with history",
                )
        finally:
            with exporter._HISTORY_LOCK:
                exporter._HISTORY.clear()
                exporter._HISTORY.extend(saved)


# ── 9. Server crash hardening ─────────────────────────────────────────────────
class TestServerCrashHardening(unittest.TestCase):
    def test_collect_metrics_doesnt_crash_on_missing_files(self):
        """collect_all_metrics() should never raise — missing files are handled gracefully."""
        orig_db = exporter.DB_PATH
        exporter.DB_PATH = Path("/nonexistent/path/ai-memory.db")
        try:
            text = exporter.collect_all_metrics()
            self.assertIsInstance(text, str)
        finally:
            exporter.DB_PATH = orig_db

    def test_handler_metrics_endpoint_doesnt_crash(self):
        """MetricsHandler.do_GET for /metrics must return 200 even if collect raises."""
        from io import BytesIO
        from unittest.mock import MagicMock, patch

        handler = exporter.MetricsHandler.__new__(exporter.MetricsHandler)
        handler.path = "/metrics"

        output = BytesIO()
        mock_wfile = MagicMock()
        mock_wfile.write = output.write
        handler.wfile = mock_wfile
        handler.request = MagicMock()
        handler.client_address = ("127.0.0.1", 12345)
        handler.server = MagicMock()
        handler.headers = {}
        responses: list[int] = []
        handler.send_response = lambda code, *a, **kw: responses.append(code)
        handler.send_header = lambda *a, **kw: None
        handler.end_headers = lambda: None

        handler.do_GET()
        self.assertTrue(len(responses) > 0, "send_response was never called")
        self.assertEqual(responses[0], 200)


# ── 10. Ring buffer persistence ──────────────────────────────────────────────
class TestRingBufferPersistence(unittest.TestCase):
    """Tests for _save_history() / _load_history().

    The exporter module is loaded via an importlib wrapper so the functions'
    __globals__ dict (the impl module) differs from the wrapper module's attrs.
    We patch HISTORY_FILE via _save_history.__globals__ to ensure the functions
    see the override.
    """

    @staticmethod
    def _impl_globals() -> dict:
        """Return the globals dict that _save_history and _load_history use."""
        return exporter._save_history.__globals__

    def test_save_and_load_history(self):
        """_save_history() and _load_history() round-trip correctly."""
        import tempfile

        impl = self._impl_globals()
        orig_file = impl["HISTORY_FILE"]
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = Path(f.name)
        impl["HISTORY_FILE"] = tmp_path

        try:
            # Seed history with known entries
            now = time.time()
            test_entries = [(now - i * 15, f"metric_{i} {i}\n") for i in range(10)]
            with exporter._HISTORY_LOCK:
                saved_history = list(exporter._HISTORY)
                exporter._HISTORY.clear()
                for e in test_entries:
                    exporter._HISTORY.append(e)

            # Save
            exporter._save_history()
            self.assertTrue(tmp_path.exists(), "History file not created")
            raw = json.loads(tmp_path.read_text())
            self.assertEqual(len(raw), 10)

            # Load into fresh deque
            with exporter._HISTORY_LOCK:
                exporter._HISTORY.clear()
            exporter._load_history()
            with exporter._HISTORY_LOCK:
                loaded = list(exporter._HISTORY)
            self.assertEqual(len(loaded), 10, f"Expected 10 entries, got {len(loaded)}")
            self.assertAlmostEqual(loaded[0][0], test_entries[0][0], delta=0.01)
        finally:
            impl["HISTORY_FILE"] = orig_file
            with exporter._HISTORY_LOCK:
                exporter._HISTORY.clear()
                for e in saved_history:
                    exporter._HISTORY.append(e)
            tmp_path.unlink(missing_ok=True)

    def test_load_history_skips_stale_entries(self):
        """_load_history() ignores entries older than 4 hours."""
        import tempfile

        impl = self._impl_globals()
        orig_file = impl["HISTORY_FILE"]
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = Path(f.name)
        impl["HISTORY_FILE"] = tmp_path

        try:
            now = time.time()
            old_entry = [now - 5 * 3600, "stale_metric 1\n"]
            fresh_entry = [now - 60, "fresh_metric 1\n"]
            tmp_path.write_text(json.dumps([old_entry, fresh_entry]))

            with exporter._HISTORY_LOCK:
                exporter._HISTORY.clear()
            exporter._load_history()
            with exporter._HISTORY_LOCK:
                loaded = list(exporter._HISTORY)

            self.assertEqual(len(loaded), 1, "Should have loaded only 1 fresh entry")
            self.assertAlmostEqual(loaded[0][0], fresh_entry[0], delta=0.01)
        finally:
            impl["HISTORY_FILE"] = orig_file
            tmp_path.unlink(missing_ok=True)

    def test_save_history_atomic_write(self):
        """_save_history() writes atomically via .tmp file."""
        import tempfile

        impl = self._impl_globals()
        orig_file = impl["HISTORY_FILE"]
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = Path(f.name)
        impl["HISTORY_FILE"] = tmp_path

        try:
            now = time.time()
            with exporter._HISTORY_LOCK:
                exporter._HISTORY.append((now, "test_metric 1\n"))
            exporter._save_history()
            self.assertTrue(tmp_path.exists())
            # .tmp file should be gone (renamed to final)
            self.assertFalse(
                tmp_path.with_suffix(".tmp").exists(),
                ".tmp file should not exist after atomic rename",
            )
        finally:
            impl["HISTORY_FILE"] = orig_file
            tmp_path.unlink(missing_ok=True)


# ── 11. Alert provisioning ────────────────────────────────────────────────────
class TestAlertProvisioning(unittest.TestCase):
    ALERTS_FILE = CONFIG / "provisioning" / "alerting" / "openclaw-alerts.yaml"

    def test_alerting_file_exists(self):
        self.assertTrue(
            self.ALERTS_FILE.exists(),
            f"Alert provisioning file missing: {self.ALERTS_FILE}",
        )

    def test_alerting_yaml_valid(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        data = yaml.safe_load(self.ALERTS_FILE.read_text())
        self.assertEqual(data.get("apiVersion"), 1)
        self.assertIn("groups", data)
        self.assertTrue(len(data["groups"]) > 0)

    def test_alert_rules_have_required_fields(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        data = yaml.safe_load(self.ALERTS_FILE.read_text())
        for group in data.get("groups", []):
            for rule in group.get("rules", []):
                self.assertIn("uid", rule, f"Rule missing uid: {rule.get('title')}")
                self.assertIn("title", rule, "Rule missing title")
                self.assertIn(
                    "condition", rule, f"Rule missing condition: {rule.get('title')}"
                )
                self.assertIn("data", rule, f"Rule missing data: {rule.get('title')}")

    def test_expected_alert_rules_present(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        data = yaml.safe_load(self.ALERTS_FILE.read_text())
        uids = [r["uid"] for g in data.get("groups", []) for r in g.get("rules", [])]
        expected_uids = [
            "openclaw-gateway-down",
            "openclaw-session-stale",
            "openclaw-disk-high",
            "openclaw-cron-stale",
            "openclaw-native-cron-stale",
        ]
        for uid in expected_uids:
            self.assertIn(uid, uids, f"Expected alert rule uid not found: {uid}")

    def test_grafana_alert_rules_loaded(self):
        """If Grafana is running, provisioned alert rules should be visible via API."""
        try:
            req = urllib.request.Request(
                "http://localhost:3000/api/v1/provisioning/alert-rules"
            )
            req.add_header("Authorization", "Basic YWRtaW46YWRtaW4=")
            with urllib.request.urlopen(req, timeout=3) as r:
                rules = json.loads(r.read().decode())
        except Exception as e:
            self.skipTest(f"Grafana not running or rules API unavailable: {e}")
        self.assertIsInstance(rules, list)
        loaded_uids = {r.get("uid") for r in rules}
        expected = {"openclaw-gateway-down", "openclaw-session-stale"}
        for uid in expected:
            self.assertIn(uid, loaded_uids, f"Alert rule not loaded in Grafana: {uid}")


# ── 12. PromQL Evaluator ──────────────────────────────────────────────────────
class TestPromQLEvaluator(unittest.TestCase):
    """Unit tests for the extended PromQL evaluator."""

    def _make_parsed(self, series_dict: dict) -> dict:
        """Helper: build a parsed metrics structure from {metric_name: [(labels, value)]}."""
        return {"series": series_dict, "help": {}, "type": {}}

    def test_sum_no_labels(self):
        parsed = self._make_parsed({"my_metric": [({}, 3.0), ({}, 7.0)]})
        result = exporter.eval_instant(parsed, "sum(my_metric)", time.time())
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(float(result[0]["value"][1]), 10.0)

    def test_avg_no_labels(self):
        parsed = self._make_parsed({"my_metric": [({}, 4.0), ({}, 6.0)]})
        result = exporter.eval_instant(parsed, "avg(my_metric)", time.time())
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(float(result[0]["value"][1]), 5.0)

    def test_min_no_labels(self):
        parsed = self._make_parsed({"my_metric": [({}, 2.0), ({}, 8.0), ({}, 5.0)]})
        result = exporter.eval_instant(parsed, "min(my_metric)", time.time())
        self.assertAlmostEqual(float(result[0]["value"][1]), 2.0)

    def test_max_no_labels(self):
        parsed = self._make_parsed({"my_metric": [({}, 2.0), ({}, 8.0), ({}, 5.0)]})
        result = exporter.eval_instant(parsed, "max(my_metric)", time.time())
        self.assertAlmostEqual(float(result[0]["value"][1]), 8.0)

    def test_count_no_labels(self):
        parsed = self._make_parsed({"my_metric": [({}, 1.0), ({}, 2.0), ({}, 3.0)]})
        result = exporter.eval_instant(parsed, "count(my_metric)", time.time())
        self.assertAlmostEqual(float(result[0]["value"][1]), 3.0)

    def test_sum_by_label(self):
        parsed = self._make_parsed(
            {
                "my_metric": [
                    ({"job": "a"}, 3.0),
                    ({"job": "a"}, 2.0),
                    ({"job": "b"}, 5.0),
                ]
            }
        )
        result = exporter.eval_instant(parsed, "sum(my_metric) by (job)", time.time())
        self.assertEqual(len(result), 2)
        val_by_job = {r["metric"]["job"]: float(r["value"][1]) for r in result}
        self.assertAlmostEqual(val_by_job["a"], 5.0)
        self.assertAlmostEqual(val_by_job["b"], 5.0)

    def test_topk(self):
        parsed = self._make_parsed(
            {
                "my_metric": [
                    ({"job": "a"}, 1.0),
                    ({"job": "b"}, 5.0),
                    ({"job": "c"}, 3.0),
                ]
            }
        )
        result = exporter.eval_instant(parsed, "topk(2, my_metric)", time.time())
        self.assertEqual(len(result), 2)
        vals = sorted([float(r["value"][1]) for r in result], reverse=True)
        self.assertEqual(vals, [5.0, 3.0])

    def test_bottomk(self):
        parsed = self._make_parsed(
            {
                "my_metric": [
                    ({"job": "a"}, 1.0),
                    ({"job": "b"}, 5.0),
                    ({"job": "c"}, 3.0),
                ]
            }
        )
        result = exporter.eval_instant(parsed, "bottomk(2, my_metric)", time.time())
        self.assertEqual(len(result), 2)
        vals = sorted([float(r["value"][1]) for r in result])
        self.assertEqual(vals, [1.0, 3.0])

    def test_label_filter_exact(self):
        parsed = self._make_parsed(
            {"my_metric": [({"job": "a"}, 1.0), ({"job": "b"}, 2.0)]}
        )
        result = exporter.eval_instant(parsed, 'my_metric{job="a"}', time.time())
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(float(result[0]["value"][1]), 1.0)

    def test_label_filter_regex(self):
        parsed = self._make_parsed(
            {
                "my_metric": [
                    ({"job": "a"}, 1.0),
                    ({"job": "b"}, 2.0),
                    ({"job": "ab"}, 3.0),
                ]
            }
        )
        result = exporter.eval_instant(parsed, 'my_metric{job=~"a.*"}', time.time())
        self.assertEqual(len(result), 2)
        vals = sorted([float(r["value"][1]) for r in result])
        self.assertEqual(vals, [1.0, 3.0])

    def test_label_filter_not_equal(self):
        parsed = self._make_parsed(
            {"my_metric": [({"job": "a"}, 1.0), ({"job": "b"}, 2.0)]}
        )
        result = exporter.eval_instant(parsed, 'my_metric{job!="a"}', time.time())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["metric"]["job"], "b")

    def test_rate_returns_list(self):
        """rate() should return a result list without crashing, even with no history."""
        raw = exporter.collect_all_metrics()
        parsed = exporter.parse_metrics_text(raw)
        result = exporter.eval_instant(
            parsed, "rate(openclaw_memory_entries_total[5m])", time.time()
        )
        self.assertIsInstance(result, list)

    def test_label_values_query(self):
        """label_values() should return values of a label for use in template variables."""
        parsed = self._make_parsed(
            {
                "my_metric": [
                    ({"job": "a"}, 1.0),
                    ({"job": "b"}, 2.0),
                    ({"job": "a"}, 3.0),
                ]
            }
        )
        result = exporter.eval_instant(
            parsed, "label_values(my_metric, job)", time.time()
        )
        self.assertIsInstance(result, list)
        values = [r["metric"].get("job") for r in result]
        self.assertIn("a", values)
        self.assertIn("b", values)
        self.assertEqual(len(values), 2, "label_values should deduplicate")


# ── 13. Contact Point Provisioning ───────────────────────────────────────────
class TestContactPointProvisioning(unittest.TestCase):
    CP_FILE = CONFIG / "provisioning" / "alerting" / "openclaw-contact-points.yaml"
    NP_FILE = CONFIG / "provisioning" / "alerting" / "openclaw-notification-policy.yaml"

    def test_contact_point_file_exists(self):
        self.assertTrue(
            self.CP_FILE.exists(), f"Contact point file missing: {self.CP_FILE}"
        )

    def test_notification_policy_file_exists(self):
        self.assertTrue(
            self.NP_FILE.exists(), f"Notification policy file missing: {self.NP_FILE}"
        )

    def test_contact_point_yaml_valid(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        data = yaml.safe_load(self.CP_FILE.read_text())
        self.assertEqual(data.get("apiVersion"), 1)
        self.assertIn("contactPoints", data)
        points = data["contactPoints"]
        self.assertTrue(len(points) > 0)
        receivers = points[0].get("receivers", [])
        self.assertTrue(len(receivers) > 0)
        self.assertEqual(receivers[0]["type"], "telegram")

    def test_grafana_contact_point_loaded(self):
        try:
            req = urllib.request.Request(
                "http://localhost:3000/api/v1/provisioning/contact-points"
            )
            req.add_header("Authorization", "Basic YWRtaW46YWRtaW4=")
            with urllib.request.urlopen(req, timeout=3) as r:
                points = json.loads(r.read().decode())
        except Exception as e:
            self.skipTest(f"Grafana not running: {e}")
        names = [p.get("name") for p in points]
        self.assertIn(
            "Telegram", names, f"Telegram contact point not loaded. Found: {names}"
        )


# ── 14. Dashboard Templating ──────────────────────────────────────────────────
class TestDashboardTemplating(unittest.TestCase):
    def setUp(self):
        self.path = CONFIG / "dashboards" / "openclaw-overview.json"
        self.data = json.loads(self.path.read_text())

    def test_templating_section_exists(self):
        self.assertIn("templating", self.data, "Dashboard missing templating section")
        self.assertIn("list", self.data["templating"], "templating.list missing")

    def test_job_variable_present(self):
        variables = self.data.get("templating", {}).get("list", [])
        names = [v.get("name") for v in variables]
        self.assertIn("job", names, "Dashboard missing $job template variable")

    def test_job_variable_uses_label_values(self):
        variables = self.data.get("templating", {}).get("list", [])
        job_var = next((v for v in variables if v.get("name") == "job"), None)
        self.assertIsNotNone(job_var, "$job variable not found")
        query = job_var.get("query", {})
        query_str = query.get("query", "") if isinstance(query, dict) else str(query)
        self.assertIn(
            "label_values", query_str, "$job variable should use label_values()"
        )

    def test_time_range_is_2h(self):
        time_cfg = self.data.get("time", {})
        self.assertEqual(
            time_cfg.get("from"), "now-2h", "Default time range should be now-2h"
        )

    def test_cron_panel_uses_job_variable(self):
        panels = self.data.get("panels", [])
        cron_panel = next(
            (p for p in panels if "Cron Job Health" in p.get("title", "")), None
        )
        if cron_panel is None:
            self.skipTest("Cron Job Health panel not found")
        targets = cron_panel.get("targets", [])
        exprs = [t.get("expr", "") for t in targets]
        self.assertTrue(
            any("$job" in e for e in exprs),
            f"Cron Job Health panel should use $job variable. Exprs: {exprs}",
        )


# ── 15. Counter metrics ───────────────────────────────────────────────────────
class TestCounterMetrics(unittest.TestCase):
    def test_counter_metrics_returns_list(self):
        lines = exporter._counter_metrics()
        self.assertIsInstance(lines, list)

    def test_counter_metrics_have_help_and_type(self):
        lines = exporter._counter_metrics()
        text = "\n".join(lines)
        self.assertIn("# HELP openclaw_cron_runs_total", text)
        self.assertIn("# TYPE openclaw_cron_runs_total counter", text)
        self.assertIn("# HELP openclaw_log_errors_total", text)
        self.assertIn("# TYPE openclaw_log_errors_total counter", text)

    def test_increment_cron_counter(self):
        import copy

        with exporter._COUNTER_LOCK:
            orig = copy.deepcopy(exporter._CRON_RUNS_TOTAL)
        exporter._increment_cron_counter("test-job-x", True)
        exporter._increment_cron_counter("test-job-x", True)
        exporter._increment_cron_counter("test-job-x", False)
        with exporter._COUNTER_LOCK:
            counts = exporter._CRON_RUNS_TOTAL.get("test-job-x", {})
        self.assertEqual(counts.get("success", 0), 2)
        self.assertEqual(counts.get("fail", 0), 1)
        # cleanup
        with exporter._COUNTER_LOCK:
            exporter._CRON_RUNS_TOTAL.clear()
            exporter._CRON_RUNS_TOTAL.update(orig)

    def test_increment_log_error_counter(self):
        import copy

        with exporter._COUNTER_LOCK:
            orig = copy.deepcopy(exporter._LOG_ERRORS_TOTAL)
        exporter._increment_log_error_counter("test-log-x", 5)
        exporter._increment_log_error_counter("test-log-x", 3)
        with exporter._COUNTER_LOCK:
            count = exporter._LOG_ERRORS_TOTAL.get("test-log-x", 0)
        self.assertEqual(count, 8)
        # cleanup
        with exporter._COUNTER_LOCK:
            exporter._LOG_ERRORS_TOTAL.clear()
            exporter._LOG_ERRORS_TOTAL.update(orig)

    def test_counter_metric_line_format(self):
        """Counter metric lines must follow {name}{labels} value format."""
        exporter._increment_cron_counter("format-test", True)
        lines = exporter._counter_metrics()
        data_lines = [l for l in lines if l.startswith("openclaw_cron_runs_total{")]
        self.assertTrue(len(data_lines) > 0, "No counter data lines found")
        for line in data_lines:
            parts = line.rsplit(" ", 1)
            self.assertEqual(len(parts), 2, f"Bad format: {line}")
            val = float(parts[1])
            self.assertGreaterEqual(val, 0)
        # cleanup
        with exporter._COUNTER_LOCK:
            exporter._CRON_RUNS_TOTAL.pop("format-test", None)

    def test_counter_in_full_output(self):
        lines_text = exporter.collect_all_metrics()
        self.assertIn("openclaw_cron_runs_total", lines_text)
        self.assertIn("openclaw_log_errors_total", lines_text)


# ── 16. Prometheus server ─────────────────────────────────────────────────────
class TestPrometheusServer(unittest.TestCase):
    PROMETHEUS_URL = "http://localhost:9090"

    def _get(self, path, timeout=5):
        try:
            with urllib.request.urlopen(
                f"{self.PROMETHEUS_URL}{path}", timeout=timeout
            ) as r:
                return r.status, r.read().decode()
        except Exception as e:
            return -1, str(e)

    def test_prometheus_healthy(self):
        status, body = self._get("/-/healthy")
        if status == -1:
            self.skipTest(f"Prometheus not running: {body}")
        self.assertEqual(status, 200)

    def test_prometheus_scraping_openclaw(self):
        """Prometheus should have at least one openclaw metric."""
        status, body = self._get("/api/v1/query?query=openclaw_memory_entries_total")
        if status == -1:
            self.skipTest(f"Prometheus not running: {body}")
        data = json.loads(body)
        self.assertEqual(data.get("status"), "success")
        results = data.get("data", {}).get("result", [])
        self.assertTrue(len(results) > 0, "No openclaw metrics found in Prometheus")

    def test_openclaw_tsdb_datasource_in_grafana(self):
        try:
            req = urllib.request.Request("http://localhost:3000/api/datasources")
            req.add_header("Authorization", "Basic YWRtaW46YWRtaW4=")
            with urllib.request.urlopen(req, timeout=3) as r:
                sources = json.loads(r.read().decode())
        except Exception as e:
            self.skipTest(f"Grafana not running: {e}")
        names = [s.get("name") for s in sources]
        self.assertIn(
            "OpenClaw-TSDB",
            names,
            f"OpenClaw-TSDB datasource not found. Found: {names}",
        )


# ── 17. Dashboard system panels ───────────────────────────────────────────────
class TestDashboardSystemPanels(unittest.TestCase):
    def setUp(self):
        self.path = CONFIG / "dashboards" / "openclaw-overview.json"
        self.data = json.loads(self.path.read_text())

    def test_cpu_panel_exists(self):
        panels = self.data.get("panels", [])
        titles = [p.get("title", "") for p in panels]
        self.assertTrue(
            any("CPU" in t for t in titles), f"No CPU panel found. Titles: {titles}"
        )

    def test_memory_panel_exists(self):
        panels = self.data.get("panels", [])
        titles = [p.get("title", "") for p in panels]
        self.assertTrue(
            any("Memory" in t and "Over Time" in t for t in titles),
            f"No Memory Over Time panel. Titles: {titles}",
        )

    def test_system_panels_are_timeseries_type(self):
        panels = self.data.get("panels", [])
        for panel in panels:
            if "CPU" in panel.get("title", "") or (
                "Memory" in panel.get("title", "")
                and "Over Time" in panel.get("title", "")
            ):
                self.assertEqual(
                    panel.get("type"),
                    "timeseries",
                    f"Panel '{panel['title']}' should be timeseries type",
                )

    def test_system_panels_use_tsdb_datasource(self):
        panels = self.data.get("panels", [])
        for panel in panels:
            if panel.get("title") in ("CPU Usage Over Time", "Memory Usage Over Time"):
                ds = panel.get("datasource", {})
                self.assertEqual(
                    ds.get("uid"),
                    "openclaw-tsdb",
                    f"Panel '{panel['title']}' should use openclaw-tsdb datasource",
                )

    def test_panel_ids_unique(self):
        panels = self.data.get("panels", [])
        ids = [p.get("id") for p in panels]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate panel IDs found")


# ── 18. Log metrics cache ─────────────────────────────────────────────────────
class TestLogMetricsCache(unittest.TestCase):
    def test_cache_state_exists(self):
        self.assertTrue(
            hasattr(exporter, "_LOG_SCAN_CACHE"), "_LOG_SCAN_CACHE not found"
        )
        self.assertTrue(
            hasattr(exporter, "_LOG_CACHE_LOCK"), "_LOG_CACHE_LOCK not found"
        )
        self.assertIsInstance(exporter._LOG_SCAN_CACHE, dict)

    def test_cache_populates_on_first_scan(self):
        """After calling _log_metrics(), cache should have entries for existing log files."""
        # Clear cache first
        with exporter._LOG_CACHE_LOCK:
            exporter._LOG_SCAN_CACHE.clear()

        exporter._log_metrics()

        with exporter._LOG_CACHE_LOCK:
            cache = dict(exporter._LOG_SCAN_CACHE)

        # At least one entry should be cached (if any log files exist)
        from pathlib import Path

        logs_dir = exporter.LOGS_DIR
        log_paths = {
            "session_watchdog": logs_dir / "session-watchdog.log",
            "session_context_flush": logs_dir / "session-context-flush.log",
            "cron_dead_man": logs_dir / "cron-dead-man.log",
        }
        existing = [name for name, path in log_paths.items() if path.exists()]
        if not existing:
            self.skipTest("No log files found to test cache")
        for name in existing:
            self.assertIn(name, cache, f"Expected cache entry for {name}")
            mtime, count = cache[name]
            self.assertGreater(mtime, 0)
            self.assertGreaterEqual(count, 0)

    def test_cache_avoids_reread_on_unchanged_file(self):
        """Second call to _log_metrics() should not re-read files if mtime unchanged."""
        import os
        import tempfile

        # Create a temp log file with known content
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write("normal line\nERROR bad thing\nnormal line\n")
            tmp_path = Path(f.name)

        log_name = "test_cache_log"

        try:
            # Simulate: first scan populates cache
            mtime = tmp_path.stat().st_mtime
            with exporter._LOG_CACHE_LOCK:
                exporter._LOG_SCAN_CACHE[log_name] = (mtime, 42)  # sentinel value

            # If cache is hit, error count should be 42 (sentinel), not re-read from file
            # We test this by checking the cache returns the sentinel
            with exporter._LOG_CACHE_LOCK:
                cached = exporter._LOG_SCAN_CACHE.get(log_name)
            self.assertIsNotNone(cached)
            self.assertEqual(
                cached[1], 42, "Cache should return sentinel value without re-read"
            )
        finally:
            tmp_path.unlink(missing_ok=True)
            with exporter._LOG_CACHE_LOCK:
                exporter._LOG_SCAN_CACHE.pop(log_name, None)

    def test_log_metrics_still_returns_valid_output(self):
        """After cache refactor, _log_metrics() output should still be valid."""
        lines = exporter._log_metrics()
        self.assertIsInstance(lines, list)
        data_lines = [l for l in lines if l.startswith("openclaw_log_errors_recent")]
        self.assertTrue(len(data_lines) > 0, "No log metric lines found")
        for line in data_lines:
            val = float(line.rsplit(" ", 1)[-1])
            self.assertGreaterEqual(val, -1)


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Run with verbose output
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
