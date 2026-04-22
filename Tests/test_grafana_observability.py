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
        stale_lines = [l for l in lines if "openclaw_cron_stale" in l and "HELP" not in l and "TYPE" not in l]
        for line in stale_lines:
            val = float(line.rsplit(" ", 1)[-1])
            self.assertIn(val, (0.0, 1.0, -1.0), f"Unexpected stale value: {line}")

    def test_exit_code_metric_present(self):
        lines = exporter._cron_metrics()
        exit_lines = [l for l in lines if "openclaw_cron_last_exit_code" in l and "HELP" not in l and "TYPE" not in l]
        self.assertTrue(len(exit_lines) > 0, "No exit_code lines found")

    def test_present_metric_1_for_existing_heartbeats(self):
        """If a heartbeat file exists, present should be 1."""
        existing = list(HB_DIR.glob("*.json"))
        if not existing:
            self.skipTest("No heartbeat files found")
        lines = exporter._cron_metrics()
        text = "\n".join(lines)
        for hb in existing:
            job = hb.stem
            self.assertIn(f'openclaw_cron_present{{job="{job}"}} 1', text,
                          f"Expected present=1 for existing heartbeat: {job}")


class TestMemoryMetrics(unittest.TestCase):
    def test_returns_list(self):
        lines = exporter._memory_metrics()
        self.assertIsInstance(lines, list)

    def test_total_is_numeric(self):
        lines = exporter._memory_metrics()
        total_lines = [l for l in lines if l.startswith("openclaw_memory_entries_total")]
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
        graph_lines = [l for l in lines if "openclaw_memory_graph_links" in l and "HELP" not in l and "TYPE" not in l]
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
    def test_scrape_timestamp_present(self):
        lines = exporter._system_metrics()
        ts_lines = [l for l in lines if l.startswith("openclaw_exporter_scrape_timestamp")]
        self.assertTrue(len(ts_lines) > 0)
        val = float(ts_lines[0].split()[-1])
        # Should be within 10 seconds of now
        self.assertAlmostEqual(val, time.time(), delta=10)


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
            "openclaw_exporter_scrape_timestamp",
        ]
        for name in expected:
            self.assertIn(name, self.parsed, f"Metric missing from output: {name}")

    def test_no_nan_or_inf_values(self):
        for name, vals in self.parsed.items():
            for v in vals:
                self.assertFalse(v != v, f"NaN in metric {name}")  # NaN != NaN
                self.assertTrue(abs(v) < 1e15 or v == -1, f"Suspicious value {v} in {name}")

    def test_all_crons_have_entries(self):
        for job in exporter.KNOWN_CRONS:
            found = any(job in line for line in self.text.splitlines() if not line.startswith("#"))
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
        self.assertTrue(path.exists(), f"Dashboard path in provider does not exist: {path}")


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
            self.assertTrue(len(targets) > 0, f"Panel '{panel.get('title')}' has no targets")

    def test_datasource_uid_consistent(self):
        panels = self.data.get("panels", [])
        for panel in panels:
            ds = panel.get("datasource", {})
            if ds:
                self.assertEqual(ds.get("uid"), "openclaw-prometheus",
                                 f"Panel '{panel.get('title')}' has wrong datasource uid")

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
            with urllib.request.urlopen(f"{self.EXPORTER_URL}{path}", timeout=timeout) as r:
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
        self.assertIn("OpenClaw-Prometheus", names,
                      f"OpenClaw-Prometheus datasource not provisioned. Found: {names}")

    def test_dashboard_provisioned(self):
        status, body = self._get("/api/search?query=OpenClaw")
        if status == -1:
            self.skipTest(f"Grafana not running: {body}")
        if status == 401:
            self.skipTest("Grafana auth required")
        results = json.loads(body)
        titles = [r.get("title") for r in results]
        self.assertIn("OpenClaw Overview", titles,
                      f"OpenClaw Overview dashboard not found. Found: {titles}")


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Run with verbose output
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
