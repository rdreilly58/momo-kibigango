#!/usr/bin/env python3
"""
test_classification_improvements.py — Comprehensive test suite for task classification improvements.

Tests:
  Suite 1: P0 — Cron model verification (8 jobs)
  Suite 2: P1 — task-classifier-v2.py behavior (13 checks)
  Suite 3: P2 — classifier-config.json structure (7 checks)
  Suite 4: P3 — TASK_ROUTING.md content (6 checks)
  Suite 5: P4 — model-usage-log.sh + model-usage-report.sh (5 checks)
  Suite 6: P5 — cron-audit-2026-05-08.md content (5 checks)
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

# ─── Paths ──────────────────────────────────────────────────────────────────
WORKSPACE = "/Users/rreilly/.openclaw/workspace"
SCRIPTS   = os.path.join(WORKSPACE, "scripts")
CONFIG    = os.path.join(WORKSPACE, "config")
MEMORY    = os.path.join(WORKSPACE, "memory")

CLASSIFIER_V2 = os.path.join(SCRIPTS, "task-classifier-v2.py")
CLASSIFIER_CFG = os.path.join(CONFIG, "classifier-config.json")
TASK_ROUTING  = os.path.join(WORKSPACE, "TASK_ROUTING.md")
USAGE_LOG     = os.path.join(SCRIPTS, "model-usage-log.sh")
USAGE_REPORT  = os.path.join(SCRIPTS, "model-usage-report.sh")
CRON_AUDIT    = os.path.join(MEMORY, "cron-audit-2026-05-08.md")

PYTHON3 = sys.executable


# ─── Helpers ─────────────────────────────────────────────────────────────────

def get_cron_jobs():
    """Fetch cron jobs via `openclaw cron list --json`."""
    result = subprocess.run(
        ["/opt/homebrew/bin/openclaw", "cron", "list", "--json"],
        capture_output=True, text=True, timeout=30
    )
    # Strip any config warnings printed to stdout before the JSON
    stdout = result.stdout
    # Find first '{' or '[' to locate JSON start
    idx = stdout.find('{')
    if idx == -1:
        raise RuntimeError(f"No JSON in cron list output: {stdout!r}")
    return json.loads(stdout[idx:])


def classify(message: str) -> dict:
    """Run task-classifier-v2.py on a message and return parsed JSON."""
    result = subprocess.run(
        [PYTHON3, CLASSIFIER_V2, "--message", message],
        capture_output=True, text=True, timeout=15
    )
    return json.loads(result.stdout.strip())


# ════════════════════════════════════════════════════════════════════════════
# Suite 1: P0 — Cron model verification
# ════════════════════════════════════════════════════════════════════════════

class Suite1_CronModels(unittest.TestCase):
    """Verify that the 8 target cron jobs have the correct payload.model values."""

    @classmethod
    def setUpClass(cls):
        data = get_cron_jobs()
        cls.jobs = {job["id"]: job for job in data.get("jobs", [])}

    def _get_model(self, job_id: str) -> str:
        """Return payload.model for a job, or '' if not found."""
        job = self.jobs.get(job_id, {})
        return job.get("payload", {}).get("model", "")

    def test_total_recall_observer(self):
        model = self._get_model("838c7ec2-4d9a-42c4-b81e-c3d4ec8aa03b")
        self.assertEqual(model, "anthropic/claude-haiku-4-6",
            f"Total Recall Observer model is '{model}'")

    def test_daily_session_reset(self):
        model = self._get_model("ed61e164-566c-476b-a3b1-755eb9135140")
        self.assertEqual(model, "anthropic/claude-haiku-4-6",
            f"Daily Session Reset model is '{model}'")

    def test_api_quota_monitor_evening(self):
        model = self._get_model("856f36a1-9e18-4b21-b375-21b1cc54f702")
        self.assertEqual(model, "anthropic/claude-haiku-4-6",
            f"API Quota Monitor Evening model is '{model}'")

    def test_weekly_memory_consolidation(self):
        model = self._get_model("cbc07acf-5ece-4b7a-8d65-1b22ff964622")
        self.assertEqual(model, "anthropic/claude-sonnet-4-6",
            f"Weekly Memory Consolidation model is '{model}'")

    def test_weekly_memory_pruning(self):
        model = self._get_model("59e40727-129c-4c64-adcd-2d70d9cd93c4")
        self.assertEqual(model, "anthropic/claude-sonnet-4-6",
            f"Weekly Memory Pruning model is '{model}'")

    def test_api_quota_monitor_morning(self):
        model = self._get_model("10e52215-47a2-4a8a-983a-acaea67af050")
        self.assertEqual(model, "anthropic/claude-haiku-4-6",
            f"API Quota Monitor Morning model is '{model}'")

    def test_bootstrap_size_check(self):
        model = self._get_model("197d1cfc-c83a-469c-8557-86b18cca81a5")
        self.assertEqual(model, "anthropic/claude-haiku-4-6",
            f"Bootstrap Size Check model is '{model}'")

    def test_weekly_backup_verification(self):
        model = self._get_model("1dd98948-99d6-4a33-84b3-fa3478dd6039")
        self.assertEqual(model, "anthropic/claude-haiku-4-6",
            f"Weekly Backup Verification model is '{model}'")


# ════════════════════════════════════════════════════════════════════════════
# Suite 2: P1 — task-classifier-v2.py
# ════════════════════════════════════════════════════════════════════════════

class Suite2_ClassifierV2(unittest.TestCase):
    """Verify task-classifier-v2.py existence, output format, and classification logic."""

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(CLASSIFIER_V2),
            f"Classifier not found at {CLASSIFIER_V2}")

    def test_file_is_executable(self):
        self.assertTrue(os.access(CLASSIFIER_V2, os.X_OK),
            f"Classifier is not executable: {CLASSIFIER_V2}")

    def test_json_output_valid(self):
        result = subprocess.run(
            [PYTHON3, CLASSIFIER_V2, "--message", "ping"],
            capture_output=True, text=True, timeout=10
        )
        self.assertEqual(result.returncode, 0, f"Classifier exited non-zero: {result.stderr}")
        data = json.loads(result.stdout.strip())
        self.assertIsInstance(data, dict, "Output is not a JSON object")

    def test_builtin_tests_all_pass(self):
        result = subprocess.run(
            [PYTHON3, CLASSIFIER_V2, "--test"],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout + result.stderr
        # Look for "11/11 passed" or similar
        match = re.search(r"(\d+)/(\d+)\s+passed", output)
        self.assertIsNotNone(match, f"No pass/fail summary found in --test output:\n{output}")
        passed = int(match.group(1))
        total  = int(match.group(2))
        self.assertEqual(passed, total,
            f"Built-in tests: only {passed}/{total} passed:\n{output}")

    # Classification checks ──────────────────────────────────────────────────

    def test_simple_what_time(self):
        data = classify("what time is it")
        self.assertEqual(data["tier"], "simple",
            f"'what time is it' → expected simple, got {data['tier']}: {data.get('reason')}")

    def test_simple_weather(self):
        data = classify("weather")
        self.assertEqual(data["tier"], "simple",
            f"'weather' → expected simple, got {data['tier']}")

    def test_simple_hi(self):
        data = classify("hi")
        self.assertEqual(data["tier"], "simple",
            f"'hi' → expected simple, got {data['tier']}")

    def test_simple_heartbeat_check(self):
        data = classify("heartbeat check")
        self.assertEqual(data["tier"], "simple",
            f"'heartbeat check' → expected simple, got {data['tier']}")

    def test_complex_refactor(self):
        data = classify("Refactor the auth module to use JWT")
        self.assertEqual(data["tier"], "complex",
            f"Refactor message → expected complex, got {data['tier']}")

    def test_complex_audit(self):
        data = classify("Audit the security config")
        self.assertEqual(data["tier"], "complex",
            f"Audit message → expected complex, got {data['tier']}")

    def test_medium_write_email(self):
        data = classify("Write an email to the team")
        self.assertEqual(data["tier"], "medium",
            f"Write email → expected medium, got {data['tier']}")

    def test_medium_explain_oauth(self):
        data = classify("Explain how OAuth2 works")
        self.assertEqual(data["tier"], "medium",
            f"Explain OAuth2 → expected medium, got {data['tier']}")

    def test_medium_code_block(self):
        msg = "Can you help me debug this:\n```python\ndef foo(): pass\n```"
        data = classify(msg)
        self.assertEqual(data["tier"], "medium",
            f"Code block message → expected medium, got {data['tier']}")

    def test_medium_long_message(self):
        # 150 words
        msg = " ".join(["word"] * 150)
        data = classify(msg)
        self.assertEqual(data["tier"], "medium",
            f"150-word message → expected medium, got {data['tier']}")

    def test_simple_single_check(self):
        data = classify("check")
        self.assertEqual(data["tier"], "simple",
            f"'check' → expected simple, got {data['tier']}")

    def test_medium_good_morning(self):
        data = classify("good morning")
        self.assertEqual(data["tier"], "medium",
            f"'good morning' → expected medium (no simple keyword), got {data['tier']}")

    def test_output_keys(self):
        data = classify("hello world")
        for key in ("tier", "model", "reason", "confidence"):
            self.assertIn(key, data,
                f"Output JSON missing key '{key}': {data}")


# ════════════════════════════════════════════════════════════════════════════
# Suite 3: P2 — classifier-config.json
# ════════════════════════════════════════════════════════════════════════════

class Suite3_ClassifierConfig(unittest.TestCase):
    """Verify classifier-config.json structure and content."""

    @classmethod
    def setUpClass(cls):
        with open(CLASSIFIER_CFG) as f:
            cls.cfg = json.load(f)
        cls.classifier = cls.cfg.get("routing", {}).get("classifier", {})

    def test_valid_json(self):
        # If setUpClass didn't raise, the file is valid JSON
        self.assertIsInstance(self.cfg, dict)

    def test_has_routing_classifier_key(self):
        self.assertIn("routing", self.cfg, "Missing 'routing' key")
        self.assertIn("classifier", self.cfg["routing"], "Missing 'routing.classifier' key")

    def test_strategy_is_hybrid(self):
        strategy = self.classifier.get("strategy", "")
        self.assertEqual(strategy, "hybrid",
            f"strategy is '{strategy}', expected 'hybrid'")

    def test_complex_keywords_nonempty_and_contains_required(self):
        kws = self.classifier.get("complex_keywords", [])
        self.assertGreater(len(kws), 0, "complex_keywords is empty")
        for required in ("refactor", "architecture", "algorithm"):
            self.assertTrue(
                any(required in kw for kw in kws),
                f"complex_keywords missing '{required}': {kws}"
            )

    def test_simple_keywords_contains_required(self):
        kws = self.classifier.get("simple_keywords", [])
        self.assertGreater(len(kws), 0, "simple_keywords is empty")
        for required in ("weather", "status", "remind", "heartbeat"):
            self.assertTrue(
                any(required in kw for kw in kws),
                f"simple_keywords missing '{required}': {kws}"
            )

    def test_simple_model(self):
        model = self.classifier.get("simple_model", "")
        self.assertIn("haiku-4-6", model,
            f"simple_model '{model}' does not contain 'haiku-4-6'")

    def test_medium_model(self):
        model = self.classifier.get("medium_model", "")
        self.assertIn("sonnet-4-6", model,
            f"medium_model '{model}' does not contain 'sonnet-4-6'")

    def test_complex_model(self):
        model = self.classifier.get("complex_model", "")
        self.assertIn("opus", model,
            f"complex_model '{model}' does not contain 'opus'")


# ════════════════════════════════════════════════════════════════════════════
# Suite 4: P3 — TASK_ROUTING.md
# ════════════════════════════════════════════════════════════════════════════

class Suite4_TaskRoutingDoc(unittest.TestCase):
    """Verify TASK_ROUTING.md content and size."""

    @classmethod
    def setUpClass(cls):
        with open(TASK_ROUTING) as f:
            cls.content = f.read()

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(TASK_ROUTING),
            f"TASK_ROUTING.md not found at {TASK_ROUTING}")

    def test_has_status_section(self):
        self.assertIn("## Status", self.content,
            "TASK_ROUTING.md missing '## Status' section")

    def test_references_classifier_v2(self):
        self.assertIn("task-classifier-v2.py", self.content,
            "TASK_ROUTING.md missing reference to 'task-classifier-v2.py'")

    def test_has_known_limitations_section(self):
        self.assertIn("## Known Limitations", self.content,
            "TASK_ROUTING.md missing '## Known Limitations' section")

    def test_contains_haiku_4_6(self):
        self.assertIn("claude-haiku-4-6", self.content,
            "TASK_ROUTING.md missing 'claude-haiku-4-6' model name")

    def test_file_size_adequate(self):
        size = os.path.getsize(TASK_ROUTING)
        self.assertGreater(size, 3000,
            f"TASK_ROUTING.md is only {size} bytes — may have been truncated")


# ════════════════════════════════════════════════════════════════════════════
# Suite 5: P4 — model-usage-log.sh + model-usage-report.sh
# ════════════════════════════════════════════════════════════════════════════

class Suite5_ModelUsageScripts(unittest.TestCase):
    """Verify model-usage-log.sh and model-usage-report.sh."""

    _test_log_file = None   # set during log test, cleaned up in tearDownClass

    @classmethod
    def tearDownClass(cls):
        if cls._test_log_file and os.path.isfile(cls._test_log_file):
            os.remove(cls._test_log_file)

    def test_log_script_exists_and_executable(self):
        self.assertTrue(os.path.isfile(USAGE_LOG),
            f"model-usage-log.sh not found at {USAGE_LOG}")
        self.assertTrue(os.access(USAGE_LOG, os.X_OK),
            "model-usage-log.sh is not executable")

    def test_report_script_exists_and_executable(self):
        self.assertTrue(os.path.isfile(USAGE_REPORT),
            f"model-usage-report.sh not found at {USAGE_REPORT}")
        self.assertTrue(os.access(USAGE_REPORT, os.X_OK),
            "model-usage-report.sh is not executable")

    def test_log_creates_csv_with_correct_format(self):
        """Run log script and verify the CSV row has 6 fields."""
        log_dir = os.path.expanduser("~/.openclaw/logs/model-usage")
        import datetime
        date_str = datetime.date.today().isoformat()
        log_file = os.path.join(log_dir, f"{date_str}.csv")
        pre_exists = os.path.isfile(log_file)
        pre_size   = os.path.getsize(log_file) if pre_exists else 0

        result = subprocess.run(
            ["bash", USAGE_LOG,
             "--session-type", "test",
             "--message", "test message from unit test",
             "--model", "anthropic/claude-sonnet-4-6"],
            capture_output=True, text=True, timeout=30
        )
        self.assertEqual(result.returncode, 0,
            f"model-usage-log.sh exited {result.returncode}:\n{result.stderr}")

        # Record for cleanup
        Suite5_ModelUsageScripts._test_log_file = log_file

        # Verify CSV file was created/updated
        self.assertTrue(os.path.isfile(log_file),
            f"CSV log file not created at {log_file}")

    def test_csv_row_has_6_fields(self):
        """Verify the last data row in today's CSV has exactly 6 comma-separated fields."""
        import datetime
        log_dir = os.path.expanduser("~/.openclaw/logs/model-usage")
        date_str = datetime.date.today().isoformat()
        log_file = os.path.join(log_dir, f"{date_str}.csv")
        self.assertTrue(os.path.isfile(log_file),
            f"CSV file not found at {log_file} (run log test first)")

        with open(log_file) as f:
            lines = [l.strip() for l in f if l.strip()]

        # Must have header + at least one data row
        self.assertGreater(len(lines), 1,
            f"CSV has only {len(lines)} line(s) — expected header + data")

        # Check last data row
        last_row = lines[-1]
        fields = last_row.split(",")
        self.assertEqual(len(fields), 6,
            f"Last CSV row has {len(fields)} fields (expected 6): {last_row!r}")

    def test_report_exits_zero(self):
        """Run report script and expect exit code 0."""
        result = subprocess.run(
            ["bash", USAGE_REPORT, "--days", "1"],
            capture_output=True, text=True, timeout=30
        )
        self.assertEqual(result.returncode, 0,
            f"model-usage-report.sh exited {result.returncode}:\n{result.stderr}")


# ════════════════════════════════════════════════════════════════════════════
# Suite 6: P5 — cron-audit-2026-05-08.md
# ════════════════════════════════════════════════════════════════════════════

class Suite6_CronAuditFile(unittest.TestCase):
    """Verify cron-audit-2026-05-08.md existence and content."""

    @classmethod
    def setUpClass(cls):
        if os.path.isfile(CRON_AUDIT):
            with open(CRON_AUDIT) as f:
                cls.content = f.read()
        else:
            cls.content = None

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(CRON_AUDIT),
            f"cron-audit-2026-05-08.md not found at {CRON_AUDIT}")

    def test_file_size_adequate(self):
        size = os.path.getsize(CRON_AUDIT)
        self.assertGreater(size, 500,
            f"cron-audit-2026-05-08.md is only {size} bytes — suspiciously small")

    def test_contains_config_json_reference(self):
        self.assertIsNotNone(self.content, "File not readable")
        self.assertIn("config.json", self.content,
            "cron-audit-2026-05-08.md missing 'config.json' reference")

    def test_contains_gateway_reference(self):
        self.assertIsNotNone(self.content)
        self.assertIn("gateway", self.content,
            "cron-audit-2026-05-08.md missing 'gateway' reference")

    def test_contains_at_least_one_recommendation(self):
        self.assertIsNotNone(self.content)
        # Accept "Recommendation" or "recommendation" or a "## Recommendations" section
        found = (
            "Recommendation" in self.content or
            "recommendation" in self.content or
            re.search(r"##\s*Recommend", self.content) is not None
        )
        self.assertTrue(found,
            "cron-audit-2026-05-08.md contains no recommendations")


# ════════════════════════════════════════════════════════════════════════════
# Entry point
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main(verbosity=2)
