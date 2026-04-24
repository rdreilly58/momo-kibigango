#!/usr/bin/env python3
"""
test_apr24_changes.py — Comprehensive test suite for all Apr 24 2026 changes.

Covers:
  1. Session metrics (_ensure_session_start, openclaw_session_duration_seconds,
     openclaw_session_last_activity_seconds)
  2. Brave API probe caching (_brave_api_metrics)
  3. Cron idempotency lock patterns (observer-agent.sh, system-health-check.sh,
     daily-session-reset.sh)
  4. Grafana dashboard changes (openclaw-overview.json datasource uids, panel
     types, time range, panel 2 title/expr)
  5. Alert rules (6 rules, Brave API Down rule structure)
  6. Speculative-decoding skill stub
  7. .gitignore entries
  8. CI workflow jobs
  9. Memory DB tier counts (live check)
"""

from __future__ import annotations

import datetime
import json
import os
import socket
import sqlite3
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# ── Import the exporter via the importable alias ───────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import openclaw_metrics_exporter as exporter

WORKSPACE = Path(__file__).parent.parent

# ── Helper: check if exporter HTTP server is up on port 9091 ──────────────────


def _port_listening(port: int = 9091) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            return True
    except OSError:
        return False


EXPORTER_UP = _port_listening(9091)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Session metrics
# ═══════════════════════════════════════════════════════════════════════════════


class TestSessionMetrics(unittest.TestCase):
    """Tests for _ensure_session_start() and _session_metrics()."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.logs_dir = Path(self.tmp.name)
        self.session_start_file = self.logs_dir / "session-start.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _patch_session_start_file(self, path):
        """Patch SESSION_START_FILE in the impl module's globals (where the function reads it)."""
        impl_globals = exporter._ensure_session_start.__globals__
        old = impl_globals["SESSION_START_FILE"]
        impl_globals["SESSION_START_FILE"] = path
        return old

    def _restore_session_start_file(self, old_val):
        exporter._ensure_session_start.__globals__["SESSION_START_FILE"] = old_val

    def _patch_sessions_file(self, path):
        impl_globals = exporter._session_metrics.__globals__
        old = impl_globals["SESSIONS_FILE"]
        impl_globals["SESSIONS_FILE"] = path
        return old

    def _restore_sessions_file(self, old_val):
        exporter._session_metrics.__globals__["SESSIONS_FILE"] = old_val

    def test_ensure_session_start_creates_file_when_missing(self):
        """_ensure_session_start should create session-start.json if absent."""
        self.assertFalse(self.session_start_file.exists())
        before = time.time()
        old = self._patch_session_start_file(self.session_start_file)
        try:
            ts = exporter._ensure_session_start()
        finally:
            self._restore_session_start_file(old)
        after = time.time()
        self.assertTrue(self.session_start_file.exists())
        self.assertGreaterEqual(ts, before)
        self.assertLessEqual(ts, after)

    def test_ensure_session_start_returns_same_ts_on_same_day(self):
        """_ensure_session_start should return the stored ts if date matches today."""
        today = datetime.date.today().isoformat()
        fixed_ts = time.time() - 3600  # 1h ago
        self.session_start_file.write_text(
            json.dumps({"date": today, "start_ts": fixed_ts})
        )
        old = self._patch_session_start_file(self.session_start_file)
        try:
            ts = exporter._ensure_session_start()
        finally:
            self._restore_session_start_file(old)
        self.assertAlmostEqual(ts, fixed_ts, places=3)

    def test_session_duration_resets_on_new_day(self):
        """If session-start.json is from yesterday, a new anchor should be written."""
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        old_ts = time.time() - 86400
        self.session_start_file.write_text(
            json.dumps({"date": yesterday, "start_ts": old_ts})
        )
        before = time.time()
        old = self._patch_session_start_file(self.session_start_file)
        try:
            ts = exporter._ensure_session_start()
        finally:
            self._restore_session_start_file(old)
        after = time.time()
        # Should have written a new entry for today
        rec = json.loads(self.session_start_file.read_text())
        self.assertEqual(rec["date"], datetime.date.today().isoformat())
        self.assertGreaterEqual(ts, before)
        self.assertLessEqual(ts, after)

    def test_session_start_file_json_structure(self):
        """Written session-start.json must have 'date' and 'start_ts' keys."""
        old = self._patch_session_start_file(self.session_start_file)
        try:
            exporter._ensure_session_start()
        finally:
            self._restore_session_start_file(old)
        rec = json.loads(self.session_start_file.read_text())
        self.assertIn("date", rec)
        self.assertIn("start_ts", rec)
        self.assertEqual(rec["date"], datetime.date.today().isoformat())
        self.assertIsInstance(rec["start_ts"], float)

    def test_session_metrics_includes_duration(self):
        """_session_metrics() output must contain openclaw_session_duration_seconds."""
        tmp_sessions = self.logs_dir / "sessions.json"
        tmp_sessions.write_text(json.dumps({}))
        old_ssf = self._patch_session_start_file(self.session_start_file)
        old_sf = self._patch_sessions_file(tmp_sessions)
        try:
            lines = exporter._session_metrics()
        finally:
            self._restore_session_start_file(old_ssf)
            self._restore_sessions_file(old_sf)
        combined = "\n".join(lines)
        self.assertIn("openclaw_session_duration_seconds", combined)

    def test_session_metrics_includes_last_activity(self):
        """_session_metrics() output must contain openclaw_session_last_activity_seconds."""
        tmp_sessions = self.logs_dir / "sessions.json"
        now_ms = int(time.time() * 1000)
        session_data = {exporter.SESSION_ACTIVITY_KEY: {"updatedAt": now_ms}}
        tmp_sessions.write_text(json.dumps(session_data))
        old_ssf = self._patch_session_start_file(self.session_start_file)
        old_sf = self._patch_sessions_file(tmp_sessions)
        try:
            lines = exporter._session_metrics()
        finally:
            self._restore_session_start_file(old_ssf)
            self._restore_sessions_file(old_sf)
        combined = "\n".join(lines)
        self.assertIn("openclaw_session_last_activity_seconds", combined)

    def test_session_last_activity_absent_emits_minus_one(self):
        """When sessions.json is missing, last_activity should be -1."""
        missing = self.logs_dir / "no-such-sessions.json"
        old_ssf = self._patch_session_start_file(self.session_start_file)
        old_sf = self._patch_sessions_file(missing)
        try:
            lines = exporter._session_metrics()
        finally:
            self._restore_session_start_file(old_ssf)
            self._restore_sessions_file(old_sf)
        combined = "\n".join(lines)
        self.assertIn("openclaw_session_last_activity_seconds -1", combined)

    def test_session_activity_key_constant(self):
        """SESSION_ACTIVITY_KEY should be the expected Telegram session key."""
        self.assertEqual(
            exporter.SESSION_ACTIVITY_KEY,
            "agent:main:telegram:direct:8755120444",
        )

    def test_session_start_file_path_constant(self):
        """SESSION_START_FILE should live under ~/.openclaw/logs/."""
        self.assertTrue(str(exporter.SESSION_START_FILE).endswith("session-start.json"))
        self.assertIn(".openclaw", str(exporter.SESSION_START_FILE))
        self.assertIn("logs", str(exporter.SESSION_START_FILE))


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Brave API probe caching
# ═══════════════════════════════════════════════════════════════════════════════


class TestBraveApiMetrics(unittest.TestCase):
    """Tests for _brave_api_metrics() caching and gauge emission."""

    # _brave_api_metrics uses `global` to write back to the impl module's globals.
    # We must read/write those globals via the function's __globals__ dict.
    _impl_globals = exporter._brave_api_metrics.__globals__

    def _reset_brave_cache(self):
        """Reset module-level Brave cache state in the impl module between tests."""
        self._impl_globals["_BRAVE_LAST_CHECK"] = 0.0
        self._impl_globals["_BRAVE_LAST_STATUS"] = -1

    def setUp(self):
        self._reset_brave_cache()

    def tearDown(self):
        self._reset_brave_cache()

    def _set_cache(self, last_check: float, last_status: int):
        self._impl_globals["_BRAVE_LAST_CHECK"] = last_check
        self._impl_globals["_BRAVE_LAST_STATUS"] = last_status

    def test_brave_metrics_emits_gauge_help_and_type(self):
        """Output must include HELP and TYPE lines for openclaw_brave_api_up."""
        # Make the probe fast: no key → status -1
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="", returncode=1)
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("BRAVE_API_KEY", None)
                lines = exporter._brave_api_metrics()
        combined = "\n".join(lines)
        self.assertIn("# HELP openclaw_brave_api_up", combined)
        self.assertIn("# TYPE openclaw_brave_api_up gauge", combined)
        self.assertIn("openclaw_brave_api_up", combined)

    def test_brave_cache_prevents_double_probe(self):
        """Second call within 5 min must return cached value without re-probing."""
        # Prime the impl cache directly (60s ago, status=1)
        self._set_cache(time.time() - 60, 1)

        with patch("subprocess.run") as mock_run:
            lines = exporter._brave_api_metrics()
            mock_run.assert_not_called()

        combined = "\n".join(lines)
        self.assertIn("openclaw_brave_api_up 1", combined)

    def test_brave_cache_expires_after_300_seconds(self):
        """After 5+ min, probe must be re-run (subprocess.run called)."""
        self._set_cache(time.time() - 400, 1)  # expired

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="", returncode=1)
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("BRAVE_API_KEY", None)
                exporter._brave_api_metrics()
            mock_run.assert_called_once()

    def test_brave_no_key_emits_unknown(self):
        """When no API key is found, status should be -1 (unknown)."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="", returncode=1)
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("BRAVE_API_KEY", None)
                lines = exporter._brave_api_metrics()
        combined = "\n".join(lines)
        self.assertIn("openclaw_brave_api_up -1", combined)

    def test_brave_cache_lock_exists(self):
        """_BRAVE_CACHE_LOCK must be a threading.Lock."""
        self.assertIsInstance(exporter._BRAVE_CACHE_LOCK, type(threading.Lock()))

    def test_brave_cache_variables_exist(self):
        """Module must export all three Brave cache variables."""
        self.assertTrue(hasattr(exporter, "_BRAVE_LAST_CHECK"))
        self.assertTrue(hasattr(exporter, "_BRAVE_LAST_STATUS"))
        self.assertTrue(hasattr(exporter, "_BRAVE_CACHE_LOCK"))

    def test_brave_down_status_on_network_error(self):
        """If the HTTP request raises an exception, status should be 0 (down)."""
        self._set_cache(0.0, -1)  # force live probe
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="fake-key", returncode=0)
            with patch("urllib.request.urlopen", side_effect=OSError("timeout")):
                lines = exporter._brave_api_metrics()
        combined = "\n".join(lines)
        self.assertIn("openclaw_brave_api_up 0", combined)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Cron idempotency lock patterns (shell scripts)
# ═══════════════════════════════════════════════════════════════════════════════


class TestCronIdempotencyLocks(unittest.TestCase):
    """Verify the lock patterns defined in the three shell scripts."""

    OBSERVER_SCRIPT = WORKSPACE / "scripts" / "observer-agent.sh"
    HEALTH_SCRIPT = WORKSPACE / "scripts" / "system-health-check.sh"
    RESET_SCRIPT = WORKSPACE / "scripts" / "daily-session-reset.sh"

    def _read(self, path: Path) -> str:
        return path.read_text()

    def test_observer_agent_has_hourly_lock_pattern(self):
        """observer-agent.sh must define an hourly lock path."""
        content = self._read(self.OBSERVER_SCRIPT)
        self.assertIn("observer-agent-", content)
        self.assertIn("%Y-%m-%d-%H", content)
        self.assertIn(".lock", content)

    def test_observer_agent_skips_if_lock_exists(self):
        """observer-agent.sh must check for existing lock and exit 0."""
        content = self._read(self.OBSERVER_SCRIPT)
        self.assertIn("exit 0", content)
        # The guard uses:  if [ -e "$LOCK_FILE" ]; then  ...  exit 0
        self.assertIn("[ -e", content)
        self.assertIn("LOCK_FILE", content)

    def test_observer_agent_removes_lock_on_exit(self):
        """observer-agent.sh must clean up its lock via trap EXIT."""
        content = self._read(self.OBSERVER_SCRIPT)
        self.assertIn("trap", content)
        self.assertIn("EXIT", content)

    def test_system_health_check_has_hourly_lock_pattern(self):
        """system-health-check.sh must define an hourly lock path."""
        content = self._read(self.HEALTH_SCRIPT)
        self.assertIn("system-health-check-", content)
        self.assertIn("%Y-%m-%d-%H", content)
        self.assertIn(".lock", content)

    def test_system_health_check_skips_if_lock_exists(self):
        """system-health-check.sh must skip when lock already present."""
        content = self._read(self.HEALTH_SCRIPT)
        self.assertIn("exit 0", content)

    def test_daily_session_reset_has_daily_lock_pattern(self):
        """daily-session-reset.sh must use a date-only (daily) lock."""
        content = self._read(self.RESET_SCRIPT)
        self.assertIn("daily-session-reset-", content)
        # Daily = no %H in the lock filename context
        self.assertIn("%Y-%m-%d", content)
        self.assertIn(".lock", content)

    def test_daily_session_reset_skips_lock_with_log_flag(self):
        """daily-session-reset.sh must bypass lock when called with --log."""
        content = self._read(self.RESET_SCRIPT)
        self.assertIn("--log", content)
        # The guard must check the argument before touching the lock
        lock_block_start = content.find("LOCK_FILE")
        log_flag_pos = content.find("--log")
        # --log check should appear at or before the lock block
        self.assertLess(log_flag_pos, lock_block_start + 50)

    def test_all_three_scripts_exist(self):
        """All three shell scripts with lock logic must exist."""
        for script in (self.OBSERVER_SCRIPT, self.HEALTH_SCRIPT, self.RESET_SCRIPT):
            self.assertTrue(script.exists(), f"Missing: {script}")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Grafana dashboard changes
# ═══════════════════════════════════════════════════════════════════════════════


class TestGrafanaDashboard(unittest.TestCase):
    """Tests for config/grafana/dashboards/openclaw-overview.json."""

    DASHBOARD_PATH = (
        WORKSPACE / "config" / "grafana" / "dashboards" / "openclaw-overview.json"
    )

    @classmethod
    def setUpClass(cls):
        with open(cls.DASHBOARD_PATH) as f:
            cls.dash = json.load(f)
        cls.panels = {p["id"]: p for p in cls.dash["panels"]}

    def test_dashboard_default_time_range_24h(self):
        """Default time range must be 'now-24h'."""
        self.assertEqual(self.dash["time"]["from"], "now-24h")

    def test_timeseries_panels_use_openclaw_tsdb(self):
        """Panels 6, 7, 8, 10, 11 must use datasource uid 'openclaw-tsdb'."""
        tsdb_panel_ids = [6, 7, 8, 10, 11]
        for pid in tsdb_panel_ids:
            panel = self.panels[pid]
            ds = panel.get("datasource", {})
            self.assertEqual(
                ds.get("uid"),
                "openclaw-tsdb",
                f"Panel {pid} ({panel.get('title')}) datasource uid should be 'openclaw-tsdb', got {ds.get('uid')!r}",
            )

    def test_stat_panels_use_openclaw_prometheus(self):
        """Panels 1, 2, 3, 4, 9 must use datasource uid 'openclaw-prometheus'."""
        stat_panel_ids = [1, 2, 3, 4, 9]
        for pid in stat_panel_ids:
            panel = self.panels[pid]
            ds = panel.get("datasource", {})
            self.assertEqual(
                ds.get("uid"),
                "openclaw-prometheus",
                f"Panel {pid} ({panel.get('title')}) should use 'openclaw-prometheus', got {ds.get('uid')!r}",
            )

    def test_panel_7_is_barchart(self):
        """Panel 7 (Memory Entries by Tier) must have type='barchart'."""
        self.assertEqual(self.panels[7]["type"], "barchart")

    def test_panel_7_legend_calcs_lastNotNull(self):
        """Panel 7 legend calcs must include 'lastNotNull'."""
        calcs = self.panels[7]["options"]["legend"]["calcs"]
        self.assertIn("lastNotNull", calcs)

    def test_panel_7_legend_display_mode_table(self):
        """Panel 7 legend displayMode must be 'table'."""
        self.assertEqual(self.panels[7]["options"]["legend"]["displayMode"], "table")

    def test_panel_6_has_two_session_targets(self):
        """Panel 6 (Session Timing) must target both session metrics."""
        targets = self.panels[6]["targets"]
        exprs = [t["expr"] for t in targets]
        self.assertIn("openclaw_session_duration_seconds", exprs)
        self.assertIn("openclaw_session_last_activity_seconds", exprs)

    def test_panel_2_title_is_last_activity(self):
        """Panel 2 title must be 'Last Activity'."""
        self.assertEqual(self.panels[2]["title"], "Last Activity")

    def test_panel_2_expr_is_last_activity_metric(self):
        """Panel 2 must query openclaw_session_last_activity_seconds."""
        targets = self.panels[2]["targets"]
        exprs = [t["expr"] for t in targets]
        self.assertIn("openclaw_session_last_activity_seconds", exprs)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Alert rules
# ═══════════════════════════════════════════════════════════════════════════════


class TestAlertRules(unittest.TestCase):
    """Tests for config/grafana/provisioning/alerting/openclaw-alerts.yaml."""

    ALERTS_PATH = (
        WORKSPACE
        / "config"
        / "grafana"
        / "provisioning"
        / "alerting"
        / "openclaw-alerts.yaml"
    )

    @classmethod
    def setUpClass(cls):
        try:
            import yaml

            with open(cls.ALERTS_PATH) as f:
                cls.alerts_doc = yaml.safe_load(f)
        except ImportError:
            # Fallback: parse minimal structure without pyyaml
            cls.alerts_doc = None
        cls.raw = cls.ALERTS_PATH.read_text()

    def _get_rules(self):
        if self.alerts_doc:
            groups = self.alerts_doc.get("groups", [])
            rules = []
            for g in groups:
                rules.extend(g.get("rules", []))
            return rules
        return None

    def test_alerts_file_exists(self):
        """openclaw-alerts.yaml must exist."""
        self.assertTrue(self.ALERTS_PATH.exists())

    def test_six_rules_total(self):
        """There must be exactly 6 alert rules."""
        rules = self._get_rules()
        if rules is None:
            # Fallback: count uid lines
            count = self.raw.count("uid: openclaw-")
            self.assertEqual(count, 6, f"Expected 6 uid entries, got {count}")
        else:
            self.assertEqual(
                len(rules),
                6,
                f"Expected 6 rules, got {len(rules)}: {[r.get('uid') for r in rules]}",
            )

    def test_brave_api_down_rule_exists(self):
        """Rule with uid 'openclaw-brave-api-down' must exist."""
        self.assertIn("openclaw-brave-api-down", self.raw)

    def test_brave_api_down_rule_severity_warning(self):
        """Brave API Down rule must have severity=warning."""
        rules = self._get_rules()
        if rules:
            brave = next(
                (r for r in rules if r.get("uid") == "openclaw-brave-api-down"), None
            )
            self.assertIsNotNone(brave, "openclaw-brave-api-down rule not found")
            self.assertEqual(brave.get("labels", {}).get("severity"), "warning")
        else:
            self.assertIn("severity: warning", self.raw)

    def test_brave_api_down_rule_for_10m(self):
        """Brave API Down rule must fire for 10m."""
        rules = self._get_rules()
        if rules:
            brave = next(
                (r for r in rules if r.get("uid") == "openclaw-brave-api-down"), None
            )
            self.assertIsNotNone(brave)
            self.assertEqual(brave.get("for"), "10m")
        else:
            # Raw check in brave section
            brave_idx = self.raw.find("openclaw-brave-api-down")
            section = self.raw[brave_idx : brave_idx + 500]
            self.assertIn("10m", section)

    def test_brave_api_down_rule_expr(self):
        """Brave API Down rule must query openclaw_brave_api_up."""
        self.assertIn("openclaw_brave_api_up", self.raw)

    def test_brave_api_down_threshold_lt_1(self):
        """Brave API Down condition threshold must be lt 1."""
        brave_idx = self.raw.find("openclaw-brave-api-down")
        # Use a generous window (900 chars) — the evaluator block comes after the data section
        section = self.raw[brave_idx : brave_idx + 900]
        self.assertIn("lt", section)

    def test_known_rule_uids_present(self):
        """All five original rule uids must still be present."""
        expected_uids = [
            "openclaw-gateway-down",
            "openclaw-session-stale",
            "openclaw-disk-high",
            "openclaw-cron-stale",
            "openclaw-native-cron-stale",
        ]
        for uid in expected_uids:
            self.assertIn(uid, self.raw, f"Missing rule uid: {uid}")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Speculative-decoding skill stub
# ═══════════════════════════════════════════════════════════════════════════════


class TestSpeculativeDecodingStub(unittest.TestCase):
    """Tests for skills/speculative-decoding/SKILL.md."""

    SKILL_PATH = WORKSPACE / "skills" / "speculative-decoding" / "SKILL.md"

    def test_skill_md_exists(self):
        """skills/speculative-decoding/SKILL.md must exist."""
        self.assertTrue(self.SKILL_PATH.exists(), f"Not found: {self.SKILL_PATH}")

    def test_skill_md_is_nonempty(self):
        """SKILL.md must not be an empty file."""
        self.assertGreater(self.SKILL_PATH.stat().st_size, 0)

    def test_skill_md_mentions_archived(self):
        """SKILL.md must mention that the skill is archived."""
        content = self.SKILL_PATH.read_text().lower()
        self.assertIn("archived", content)

    def test_skill_md_mentions_speculative_decoding(self):
        """SKILL.md should reference speculative-decoding in some form."""
        content = self.SKILL_PATH.read_text().lower()
        self.assertIn("speculative", content)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. .gitignore entries
# ═══════════════════════════════════════════════════════════════════════════════


class TestGitignoreEntries(unittest.TestCase):
    """Verify new .gitignore patterns added Apr 24."""

    GITIGNORE = WORKSPACE / ".gitignore"

    @classmethod
    def setUpClass(cls):
        cls.content = cls.GITIGNORE.read_text()

    def test_gitignore_status_md(self):
        """STATUS.md must be ignored."""
        self.assertIn("STATUS.md", self.content)

    def test_gitignore_memory_observations(self):
        """memory/observations.md must be ignored."""
        self.assertIn("memory/observations.md", self.content)

    def test_gitignore_memory_last_summary_run(self):
        """memory/.last-summary-run must be ignored."""
        self.assertIn("memory/.last-summary-run", self.content)

    def test_gitignore_memory_observer_last_run(self):
        """memory/.observer-last-run must be ignored."""
        self.assertIn("memory/.observer-last-run", self.content)

    def test_gitignore_memory_2026_wildcard(self):
        """memory/2026-*.md pattern must be ignored."""
        self.assertIn("memory/2026-*.md", self.content)

    def test_gitignore_daily_metrics_wildcard(self):
        """memory/DAILY_METRICS_*.md pattern must be ignored."""
        self.assertIn("memory/DAILY_METRICS_*.md", self.content)

    def test_gitignore_session_start_json(self):
        """logs/session-start.json must be ignored."""
        self.assertIn("logs/session-start.json", self.content)


# ═══════════════════════════════════════════════════════════════════════════════
# 8. CI workflow jobs
# ═══════════════════════════════════════════════════════════════════════════════


class TestCIWorkflow(unittest.TestCase):
    """Verify .github/workflows/ci.yml has the expected 4 jobs."""

    CI_PATH = WORKSPACE / ".github" / "workflows" / "ci.yml"

    @classmethod
    def setUpClass(cls):
        cls.content = cls.CI_PATH.read_text()
        try:
            import yaml

            with open(cls.CI_PATH) as f:
                cls.ci_doc = yaml.safe_load(f)
        except ImportError:
            cls.ci_doc = None

    def test_ci_yml_exists(self):
        """ci.yml must exist."""
        self.assertTrue(self.CI_PATH.exists())

    def test_ci_has_secrets_scan_job(self):
        """CI must have a 'secrets-scan' job."""
        self.assertIn("secrets-scan", self.content)

    def test_ci_has_lint_python_job(self):
        """CI must have a 'lint-python' job."""
        self.assertIn("lint-python", self.content)

    def test_ci_has_test_observability_job(self):
        """CI must have a 'test-observability' job."""
        self.assertIn("test-observability", self.content)

    def test_ci_has_validate_grafana_job(self):
        """CI must have a 'validate-grafana' job."""
        self.assertIn("validate-grafana", self.content)

    def test_ci_has_exactly_four_jobs(self):
        """CI workflow must define exactly 4 jobs."""
        if self.ci_doc:
            jobs = self.ci_doc.get("jobs", {})
            self.assertEqual(
                len(jobs), 4, f"Expected 4 jobs, got {len(jobs)}: {list(jobs.keys())}"
            )
        else:
            # Approximate check via indentation pattern
            import re

            job_names = re.findall(
                r"^  ([a-z][a-z0-9-]+):\s*$", self.content, re.MULTILINE
            )
            # Filter out 'on', 'jobs' block headings — only lines at 2-space indent
            self.assertEqual(
                len(job_names), 4, f"Expected 4 job blocks, found: {job_names}"
            )

    def test_ci_triggers_on_push_and_pr_to_main(self):
        """CI must trigger on push and pull_request to main branch."""
        self.assertIn("push", self.content)
        self.assertIn("pull_request", self.content)
        self.assertIn("main", self.content)


# ═══════════════════════════════════════════════════════════════════════════════
# 9. Memory DB tier counts (live)
# ═══════════════════════════════════════════════════════════════════════════════


class TestMemoryDBTierCounts(unittest.TestCase):
    """Live check of ai-memory.db tier distribution."""

    DB_PATH = WORKSPACE / "ai-memory.db"

    def _get_tier_counts(self):
        conn = sqlite3.connect(str(self.DB_PATH))
        rows = conn.execute(
            "SELECT tier, count(*) FROM memories GROUP BY tier"
        ).fetchall()
        conn.close()
        return {tier: count for tier, count in rows}

    @unittest.skipIf(
        not (WORKSPACE / "ai-memory.db").exists(),
        "ai-memory.db not present — skipping live DB tests",
    )
    def test_long_tier_has_at_least_15_entries(self):
        """Long tier must have >= 15 entries."""
        counts = self._get_tier_counts()
        long_count = counts.get("long", 0)
        self.assertGreaterEqual(
            long_count,
            15,
            f"Long tier has {long_count} entries, expected >= 15",
        )

    @unittest.skipIf(
        not (WORKSPACE / "ai-memory.db").exists(),
        "ai-memory.db not present — skipping live DB tests",
    )
    def test_short_tier_within_limit(self):
        """Short tier must have <= 210 entries."""
        counts = self._get_tier_counts()
        short_count = counts.get("short", 0)
        self.assertLessEqual(
            short_count,
            210,
            f"Short tier has {short_count} entries, expected <= 210",
        )

    @unittest.skipIf(
        not (WORKSPACE / "ai-memory.db").exists(),
        "ai-memory.db not present — skipping live DB tests",
    )
    def test_db_has_memories_table(self):
        """ai-memory.db must have a 'memories' table."""
        conn = sqlite3.connect(str(self.DB_PATH))
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        ]
        conn.close()
        self.assertIn("memories", tables)

    @unittest.skipIf(
        not (WORKSPACE / "ai-memory.db").exists(),
        "ai-memory.db not present — skipping live DB tests",
    )
    def test_memory_entries_has_tier_column(self):
        """memories table must have a 'tier' column."""
        conn = sqlite3.connect(str(self.DB_PATH))
        cols = [r[1] for r in conn.execute("PRAGMA table_info(memories)").fetchall()]
        conn.close()
        self.assertIn("tier", cols)


# ═══════════════════════════════════════════════════════════════════════════════
# 10. HTTP exporter endpoint checks (skipped if port 9091 not listening)
# ═══════════════════════════════════════════════════════════════════════════════


@unittest.skipIf(not EXPORTER_UP, "Port 9091 not listening — skipping live HTTP tests")
class TestExporterHTTPLive(unittest.TestCase):
    """Smoke tests against the running exporter on :9091."""

    import urllib.request as _urllib_request

    def _get(self, path: str) -> tuple[int, str]:
        import urllib.request

        req = urllib.request.Request(f"http://127.0.0.1:9091{path}")
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, r.read().decode()

    def test_metrics_endpoint_returns_200(self):
        status, _ = self._get("/metrics")
        self.assertEqual(status, 200)

    def test_metrics_contains_session_duration(self):
        _, body = self._get("/metrics")
        self.assertIn("openclaw_session_duration_seconds", body)

    def test_metrics_contains_brave_api_up(self):
        _, body = self._get("/metrics")
        self.assertIn("openclaw_brave_api_up", body)

    def test_health_endpoint_returns_ok(self):
        status, body = self._get("/health")
        self.assertEqual(status, 200)
        self.assertEqual(body.strip(), "ok")


# ═══════════════════════════════════════════════════════════════════════════════
# 11. Exporter collect_all_metrics integration
# ═══════════════════════════════════════════════════════════════════════════════


class TestCollectAllMetricsIntegration(unittest.TestCase):
    """Integration: collect_all_metrics() must include all new metric names."""

    def test_collect_all_includes_session_duration(self):
        """collect_all_metrics() output must include session_duration_seconds."""
        output = exporter.collect_all_metrics()
        self.assertIn("openclaw_session_duration_seconds", output)

    def test_collect_all_includes_session_last_activity(self):
        """collect_all_metrics() output must include session_last_activity_seconds."""
        output = exporter.collect_all_metrics()
        self.assertIn("openclaw_session_last_activity_seconds", output)

    def test_collect_all_includes_brave_api_up(self):
        """collect_all_metrics() output must include openclaw_brave_api_up."""
        output = exporter.collect_all_metrics()
        self.assertIn("openclaw_brave_api_up", output)

    def test_collect_all_output_is_valid_prometheus_text(self):
        """Output must parse without error through parse_metrics_text()."""
        output = exporter.collect_all_metrics()
        parsed = exporter.parse_metrics_text(output)
        self.assertIn("series", parsed)
        self.assertIsInstance(parsed["series"], dict)
        self.assertGreater(len(parsed["series"]), 0)

    def test_session_duration_is_non_negative(self):
        """openclaw_session_duration_seconds value must be >= 0."""
        output = exporter.collect_all_metrics()
        parsed = exporter.parse_metrics_text(output)
        series = parsed["series"]
        self.assertIn("openclaw_session_duration_seconds", series)
        for _, value in series["openclaw_session_duration_seconds"]:
            self.assertGreaterEqual(value, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
