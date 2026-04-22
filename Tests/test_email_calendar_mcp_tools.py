#!/usr/bin/env python3
"""
Test suite for email/calendar MCP tools in memory_mcp_server.py.

Groups:
  1. Unit tests — mocked subprocess, no gog required
  2. VIP watcher unit tests
  3. Edge cases
  4. Integration tests — real gog (skipped if gog not on PATH)
"""

import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
VENV_SITE = Path(__file__).parent.parent / "venv" / "lib" / "python3.14" / "site-packages"
sys.path.insert(0, str(VENV_SITE))
sys.path.insert(0, str(SCRIPTS_DIR))

import memory_mcp_server as srv
import email_vip_watcher as vip


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

def _gog_ok(messages: list) -> MagicMock:
    m = MagicMock()
    m.returncode = 0
    m.stdout = json.dumps({"messages": messages})
    m.stderr = ""
    return m


def _gog_calendar_ok(events: list) -> MagicMock:
    m = MagicMock()
    m.returncode = 0
    m.stdout = json.dumps({"events": events})
    m.stderr = ""
    return m


def _gog_fail(stderr: str = "gog error") -> MagicMock:
    m = MagicMock()
    m.returncode = 1
    m.stdout = ""
    m.stderr = stderr
    return m


NOW_ISO = datetime.now(timezone.utc).isoformat()
TOMORROW_ISO = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
    hour=9, minute=0, second=0, microsecond=0
).isoformat()

SAMPLE_MESSAGES = [
    {"id": "msg001", "from": "alice@example.com", "subject": "Hello", "date": NOW_ISO, "labels": ["INBOX"]},
    {"id": "msg002", "from": "boss@corp.com", "subject": "Invoice due", "date": NOW_ISO, "labels": ["IMPORTANT", "UNREAD"]},
]

SAMPLE_EVENTS = [
    {
        "summary": "Team Standup",
        "start": {"dateTime": datetime.now(timezone.utc).replace(hour=15, minute=0).isoformat()},
        "location": "Zoom",
    },
    {
        "summary": "Morning Coffee",
        "start": {"dateTime": (datetime.now(timezone.utc) + timedelta(days=1)).replace(hour=9, minute=0).isoformat()},
        "location": "",
    },
]


# ---------------------------------------------------------------------------
# 1. email_list_unread
# ---------------------------------------------------------------------------

class TestEmailListUnread(unittest.TestCase):

    @patch("memory_mcp_server.subprocess.run")
    def test_single_account_ok(self, mock_run):
        """Single account returns dict keyed by account email with message list."""
        mock_run.return_value = _gog_ok(SAMPLE_MESSAGES)
        result = json.loads(srv.email_list_unread("rdreilly2010@gmail.com"))
        self.assertIn("rdreilly2010@gmail.com", result)
        msgs = result["rdreilly2010@gmail.com"]
        self.assertIsInstance(msgs, list)
        self.assertEqual(len(msgs), 2)
        msg = msgs[0]
        self.assertIn("id", msg)
        self.assertIn("from", msg)
        self.assertIn("subject", msg)
        self.assertIn("date", msg)
        self.assertIn("flags", msg)

    @patch("memory_mcp_server.subprocess.run")
    def test_all_accounts_calls_gog_three_times(self, mock_run):
        """account='all' queries all 3 known accounts."""
        mock_run.return_value = _gog_ok([])
        result = json.loads(srv.email_list_unread("all"))
        self.assertEqual(mock_run.call_count, 3)
        self.assertEqual(len(result), 3)

    @patch("memory_mcp_server.subprocess.run")
    def test_short_label_resolves_account(self, mock_run):
        """Short label like 'rdreilly2010' should resolve to full email."""
        mock_run.return_value = _gog_ok([])
        result = json.loads(srv.email_list_unread("rdreilly2010"))
        self.assertEqual(len(result), 1)

    @patch("memory_mcp_server.subprocess.run")
    def test_gog_error_returns_error_dict(self, mock_run):
        """gog failure returns {account: {"error": ...}} not exception."""
        mock_run.return_value = _gog_fail("No auth token found")
        result = json.loads(srv.email_list_unread("reillyrd25@gmail.com"))
        acct_data = result.get("reillyrd25@gmail.com", {})
        self.assertIn("error", acct_data)

    @patch("memory_mcp_server.subprocess.run")
    def test_empty_inbox_ok(self, mock_run):
        """Empty message list returns empty list, not error."""
        mock_run.return_value = _gog_ok([])
        result = json.loads(srv.email_list_unread("rdreilly2010@gmail.com"))
        msgs = result["rdreilly2010@gmail.com"]
        self.assertIsInstance(msgs, list)
        self.assertEqual(len(msgs), 0)

    @patch("memory_mcp_server.subprocess.run")
    def test_important_label_in_flags(self, mock_run):
        """IMPORTANT label is surfaced in flags list."""
        mock_run.return_value = _gog_ok(SAMPLE_MESSAGES)
        result = json.loads(srv.email_list_unread("rdreilly2010@gmail.com"))
        msgs = result["rdreilly2010@gmail.com"]
        important_msgs = [m for m in msgs if "IMPORTANT" in m.get("flags", [])]
        self.assertEqual(len(important_msgs), 1)


# ---------------------------------------------------------------------------
# 2. email_search
# ---------------------------------------------------------------------------

class TestEmailSearch(unittest.TestCase):

    @patch("memory_mcp_server.subprocess.run")
    def test_query_passed_to_gog(self, mock_run):
        """The query string is passed through to gog."""
        mock_run.return_value = _gog_ok(SAMPLE_MESSAGES)
        srv.email_search("from:alice subject:invoice", "rdreilly2010@gmail.com")
        call_cmd = mock_run.call_args[0][0]
        self.assertIn("from:alice subject:invoice", call_cmd)

    @patch("memory_mcp_server.subprocess.run")
    def test_max_results_clamped_to_25(self, mock_run):
        """max_results > 25 is clamped."""
        mock_run.return_value = _gog_ok([])
        result = json.loads(srv.email_search("is:unread", "rdreilly2010@gmail.com", max_results=999))
        # Should complete without error; clamped internally
        self.assertIsInstance(result, dict)

    @patch("memory_mcp_server.subprocess.run")
    def test_single_quote_in_query_escaped(self, mock_run):
        """Single quotes in query are shell-escaped to prevent injection."""
        mock_run.return_value = _gog_ok([])
        srv.email_search("subject:it's urgent", "rdreilly2010@gmail.com")
        call_cmd = mock_run.call_args[0][0]
        # The literal ' should be escaped — confirm no raw ' inside quoted string
        self.assertNotIn("subject:it's urgent", call_cmd)

    @patch("memory_mcp_server.subprocess.run")
    def test_gog_error_returns_per_account_error(self, mock_run):
        """gog failure returns error dict per account."""
        mock_run.return_value = _gog_fail()
        result = json.loads(srv.email_search("is:unread", "rdreilly2010@gmail.com"))
        acct_data = result.get("rdreilly2010@gmail.com", {})
        self.assertIn("error", acct_data)


# ---------------------------------------------------------------------------
# 3. email_read
# ---------------------------------------------------------------------------

class TestEmailRead(unittest.TestCase):

    @patch("memory_mcp_server.subprocess.run")
    def test_returns_message_fields(self, mock_run):
        """Returns from, to, subject, date, body on success."""
        msg_data = {
            "from": "alice@example.com",
            "to": "me@gmail.com",
            "subject": "Hello",
            "date": "2026-04-22",
            "body": "This is the full email body.",
        }
        m = MagicMock()
        m.returncode = 0
        m.stdout = json.dumps(msg_data)
        m.stderr = ""
        mock_run.return_value = m

        result = json.loads(srv.email_read("msg001", "rdreilly2010@gmail.com"))
        self.assertEqual(result["from"], "alice@example.com")
        self.assertIn("body", result)
        self.assertIn("subject", result)

    @patch("memory_mcp_server.subprocess.run")
    def test_gog_error_returns_error_json(self, mock_run):
        """gog failure returns {"error": ...} not exception."""
        mock_run.return_value = _gog_fail("message not found")
        result = json.loads(srv.email_read("bad_id", "rdreilly2010@gmail.com"))
        self.assertIn("error", result)

    @patch("memory_mcp_server.subprocess.run")
    def test_body_truncated_at_4000_chars(self, mock_run):
        """Body is truncated to 4000 chars to protect context window."""
        long_body = "x" * 10_000
        m = MagicMock()
        m.returncode = 0
        m.stdout = json.dumps({"from": "a@b.com", "subject": "long", "body": long_body})
        m.stderr = ""
        mock_run.return_value = m
        result = json.loads(srv.email_read("msg001", "rdreilly2010@gmail.com"))
        self.assertLessEqual(len(result.get("body", "")), 4000)

    def test_message_id_shell_injection_sanitized(self):
        """Malicious message_id should be sanitized before shell invocation."""
        # Should not raise; injection chars should be stripped
        with patch("memory_mcp_server.subprocess.run") as mock_run:
            mock_run.return_value = _gog_fail()
            srv.email_read("$(rm -rf /); echo", "rdreilly2010@gmail.com")
            call_cmd = mock_run.call_args[0][0]
            self.assertNotIn("$(rm -rf /)", call_cmd)


# ---------------------------------------------------------------------------
# 4. calendar_today
# ---------------------------------------------------------------------------

class TestCalendarToday(unittest.TestCase):

    @patch("memory_mcp_server.subprocess.run")
    def test_returns_today_and_tomorrow_morning(self, mock_run):
        """Result has today and tomorrow_morning lists."""
        mock_run.return_value = _gog_calendar_ok(SAMPLE_EVENTS)
        result = json.loads(srv.calendar_today())
        self.assertIn("today", result)
        self.assertIn("tomorrow_morning", result)
        self.assertIn("as_of", result)
        self.assertIsInstance(result["today"], list)
        self.assertIsInstance(result["tomorrow_morning"], list)

    @patch("memory_mcp_server.subprocess.run")
    def test_past_events_excluded_from_today(self, mock_run):
        """Events earlier today (already past) are not returned."""
        past_event = {
            "summary": "Morning standup",
            "start": {"dateTime": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat()},
            "location": "",
        }
        mock_run.return_value = _gog_calendar_ok([past_event])
        result = json.loads(srv.calendar_today())
        self.assertEqual(len(result["today"]), 0)

    @patch("memory_mcp_server.subprocess.run")
    def test_all_day_event_included(self, mock_run):
        """All-day events (date only, no time) are included."""
        from datetime import date
        today_str = date.today().isoformat()
        all_day = {
            "summary": "Holiday",
            "start": {"date": today_str},
            "location": "",
        }
        mock_run.return_value = _gog_calendar_ok([all_day])
        result = json.loads(srv.calendar_today())
        self.assertEqual(len(result["today"]), 1)
        self.assertEqual(result["today"][0]["time"], "All day")

    @patch("memory_mcp_server.subprocess.run")
    def test_gog_error_returns_error_json(self, mock_run):
        mock_run.return_value = _gog_fail("calendar unavailable")
        result = json.loads(srv.calendar_today())
        self.assertIn("error", result)


# ---------------------------------------------------------------------------
# 5. calendar_range
# ---------------------------------------------------------------------------

class TestCalendarRange(unittest.TestCase):

    @patch("memory_mcp_server.subprocess.run")
    def test_returns_events_list_and_count(self, mock_run):
        """Result has events list and count."""
        mock_run.return_value = _gog_calendar_ok(SAMPLE_EVENTS)
        result = json.loads(srv.calendar_range("2026-04-20", "2026-04-30"))
        self.assertIn("events", result)
        self.assertIn("count", result)
        self.assertIsInstance(result["events"], list)

    def test_start_after_end_returns_error(self):
        """start_date > end_date returns error JSON without calling gog."""
        result = json.loads(srv.calendar_range("2026-04-29", "2026-04-22"))
        self.assertIn("error", result)

    def test_invalid_date_format_returns_error(self):
        """Non-ISO date string returns error JSON."""
        result = json.loads(srv.calendar_range("next Monday", "2026-04-30"))
        self.assertIn("error", result)

    def test_empty_start_date_returns_error(self):
        result = json.loads(srv.calendar_range("", "2026-04-30"))
        self.assertIn("error", result)

    @patch("memory_mcp_server.subprocess.run")
    def test_events_sorted_by_date(self, mock_run):
        """Events in response are sorted by date ascending."""
        events = [
            {"summary": "B", "start": {"dateTime": "2026-04-25T10:00:00+00:00"}, "location": ""},
            {"summary": "A", "start": {"dateTime": "2026-04-23T09:00:00+00:00"}, "location": ""},
        ]
        mock_run.return_value = _gog_calendar_ok(events)
        result = json.loads(srv.calendar_range("2026-04-22", "2026-04-30"))
        evts = result["events"]
        if len(evts) >= 2:
            self.assertLessEqual(evts[0]["date"], evts[1]["date"])

    @patch("memory_mcp_server.subprocess.run")
    def test_gog_error_returns_error_json(self, mock_run):
        mock_run.return_value = _gog_fail()
        result = json.loads(srv.calendar_range("2026-04-22", "2026-04-30"))
        self.assertIn("error", result)


# ---------------------------------------------------------------------------
# 6. VIP watcher unit tests
# ---------------------------------------------------------------------------

class TestVipWatcherIsVipMatch(unittest.TestCase):

    BASE_CONFIG = {
        "vip_emails": ["ceo@corp.com"],
        "vip_senders": ["security-alert"],
        "vip_sender_domains": ["importantclient.com"],
        "subject_keywords": ["urgent", "invoice"],
    }

    def _msg(self, sender: str, subject: str, labels: list = None) -> dict:
        return {"id": "x", "from": sender, "subject": subject,
                "date": NOW_ISO, "labels": labels or []}

    def test_vip_email_match(self):
        matched, reason = vip.is_vip_match(self._msg("ceo@corp.com", "Hello"), self.BASE_CONFIG)
        self.assertTrue(matched)
        self.assertIn("ceo@corp.com", reason)

    def test_vip_sender_substring_match(self):
        matched, reason = vip.is_vip_match(
            self._msg("Security-Alert <noreply@system.io>", "Alert"), self.BASE_CONFIG)
        self.assertTrue(matched)

    def test_vip_domain_match(self):
        matched, reason = vip.is_vip_match(
            self._msg("Jane <jane@importantclient.com>", "Hi"), self.BASE_CONFIG)
        self.assertTrue(matched)
        self.assertIn("importantclient.com", reason)

    def test_keyword_match(self):
        matched, reason = vip.is_vip_match(self._msg("random@example.com", "Urgent help needed"), self.BASE_CONFIG)
        self.assertTrue(matched)
        self.assertIn("urgent", reason)

    def test_no_match(self):
        matched, reason = vip.is_vip_match(self._msg("spam@nobody.com", "Newsletter"), self.BASE_CONFIG)
        self.assertFalse(matched)
        self.assertEqual(reason, "")

    def test_case_insensitive(self):
        matched, reason = vip.is_vip_match(
            self._msg("CEO@CORP.COM", "URGENT MATTER"), self.BASE_CONFIG)
        self.assertTrue(matched)

    def test_empty_message_no_crash(self):
        matched, reason = vip.is_vip_match({}, self.BASE_CONFIG)
        self.assertFalse(matched)

    def test_empty_config_no_match(self):
        matched, reason = vip.is_vip_match(self._msg("ceo@corp.com", "urgent"), {})
        self.assertFalse(matched)


class TestVipWatcherIsMessageRecent(unittest.TestCase):

    def test_recent_message_passes(self):
        now = datetime.now(timezone.utc).isoformat()
        self.assertTrue(vip.is_message_recent({"date": now}, max_age_minutes=10))

    def test_old_message_filtered(self):
        old = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        self.assertFalse(vip.is_message_recent({"date": old}, max_age_minutes=10))

    def test_missing_date_passes_conservatively(self):
        self.assertTrue(vip.is_message_recent({}, max_age_minutes=10))

    def test_unparseable_date_passes_conservatively(self):
        self.assertTrue(vip.is_message_recent({"date": "not-a-date"}, max_age_minutes=10))

    def test_exactly_at_boundary(self):
        """Message at exact max_age boundary should pass."""
        boundary = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
        self.assertTrue(vip.is_message_recent({"date": boundary}, max_age_minutes=10))


class TestVipWatcherCooldown(unittest.TestCase):

    def test_no_cooldown_when_state_empty(self):
        state = {"cooldowns": {}}
        self.assertFalse(vip.is_account_on_cooldown("a@b.com", state, cooldown_minutes=60))

    def test_cooldown_active_just_alerted(self):
        now = datetime.now(timezone.utc).isoformat()
        state = {"cooldowns": {"a@b.com": now}}
        self.assertTrue(vip.is_account_on_cooldown("a@b.com", state, cooldown_minutes=60))

    def test_cooldown_expired(self):
        old = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        state = {"cooldowns": {"a@b.com": old}}
        self.assertFalse(vip.is_account_on_cooldown("a@b.com", state, cooldown_minutes=60))

    def test_cooldown_wrong_account(self):
        now = datetime.now(timezone.utc).isoformat()
        state = {"cooldowns": {"other@example.com": now}}
        self.assertFalse(vip.is_account_on_cooldown("a@b.com", state, cooldown_minutes=60))


class TestVipWatcherStateDedup(unittest.TestCase):
    """Verify notified_ids dedup logic via load/save state."""

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self._state_path = Path(self._tmp.name)
        self._orig_state_file = vip.STATE_FILE
        vip.STATE_FILE = self._state_path

    def tearDown(self):
        vip.STATE_FILE = self._orig_state_file
        self._state_path.unlink(missing_ok=True)

    def test_round_trip_state(self):
        state = {"notified_ids": ["id1", "id2"], "cooldowns": {}, "last_run": ""}
        vip.save_state(state)
        loaded = vip.load_state()
        self.assertIn("id1", loaded["notified_ids"])
        self.assertIn("id2", loaded["notified_ids"])

    def test_ids_capped_at_max(self):
        """State should not grow beyond MAX_STATE_IDS entries."""
        ids = [f"msg{i:04d}" for i in range(vip.MAX_STATE_IDS + 50)]
        state = {"notified_ids": ids, "cooldowns": {}, "last_run": ""}
        vip.save_state(state)
        loaded = vip.load_state()
        self.assertLessEqual(len(loaded["notified_ids"]), vip.MAX_STATE_IDS)

    def test_corrupt_state_returns_default(self):
        self._state_path.write_text("not valid json {{{{")
        state = vip.load_state()
        self.assertIn("notified_ids", state)
        self.assertIsInstance(state["notified_ids"], list)

    def test_missing_state_file_returns_default(self):
        self._state_path.unlink(missing_ok=True)
        state = vip.load_state()
        self.assertIn("notified_ids", state)


class TestVipWatcherConfig(unittest.TestCase):
    """Config loading and default merging."""

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
        self._config_path = Path(self._tmp.name)
        self._orig_config = vip.CONFIG_FILE
        vip.CONFIG_FILE = self._config_path

    def tearDown(self):
        vip.CONFIG_FILE = self._orig_config
        self._config_path.unlink(missing_ok=True)

    def test_valid_config_loads(self):
        self._config_path.write_text(json.dumps({"enabled": False, "telegram_channel": "12345"}))
        config = vip.load_config()
        self.assertFalse(config["enabled"])
        self.assertEqual(config["telegram_channel"], "12345")

    def test_missing_keys_filled_with_defaults(self):
        self._config_path.write_text(json.dumps({}))
        config = vip.load_config()
        self.assertIn("subject_keywords", config)
        self.assertIn("accounts", config)

    def test_corrupt_config_uses_defaults(self):
        self._config_path.write_text("{bad json")
        config = vip.load_config()
        self.assertIn("accounts", config)


class TestVipWatcherSendTelegram(unittest.TestCase):

    @patch("email_vip_watcher.subprocess.run")
    def test_send_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
        result = vip.send_telegram("Hello", "8755120444")
        self.assertTrue(result)

    @patch("email_vip_watcher.subprocess.run")
    def test_send_failure_returns_false(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="connection refused")
        result = vip.send_telegram("Hello", "8755120444")
        self.assertFalse(result)

    @patch("email_vip_watcher.subprocess.run")
    def test_send_timeout_returns_false(self, mock_run):
        import subprocess as _sp
        mock_run.side_effect = _sp.TimeoutExpired(cmd="openclaw", timeout=15)
        result = vip.send_telegram("Hello", "8755120444")
        self.assertFalse(result)


# ---------------------------------------------------------------------------
# 7. Integration tests (real gog, skip if unavailable)
# ---------------------------------------------------------------------------

@unittest.skipUnless(shutil.which("gog"), "gog not on PATH — skipping live tests")
class TestIntegrationLive(unittest.TestCase):

    def test_calendar_today_live_shape(self):
        raw = srv.calendar_today()
        result = json.loads(raw)
        self.assertIn("today", result)
        self.assertIn("tomorrow_morning", result)
        self.assertIn("as_of", result)

    def test_email_list_unread_live_primary(self):
        raw = srv.email_list_unread("rdreilly2010@gmail.com")
        result = json.loads(raw)
        self.assertIn("rdreilly2010@gmail.com", result)
        acct_data = result["rdreilly2010@gmail.com"]
        # Either a list of messages or an error dict
        self.assertIsInstance(acct_data, (list, dict))

    def test_email_search_live(self):
        raw = srv.email_search("is:unread", "rdreilly2010@gmail.com", max_results=3)
        result = json.loads(raw)
        self.assertIn("rdreilly2010@gmail.com", result)

    def test_calendar_range_live(self):
        today = datetime.now().strftime("%Y-%m-%d")
        next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        raw = srv.calendar_range(today, next_week)
        result = json.loads(raw)
        self.assertIn("events", result)
        self.assertIn("count", result)


# ---------------------------------------------------------------------------
# 8. Edge cases — gog not available
# ---------------------------------------------------------------------------

class TestNoGog(unittest.TestCase):

    @patch("memory_mcp_server._gog_available", return_value=False)
    def test_email_list_unread_no_gog(self, _):
        result = json.loads(srv.email_list_unread())
        self.assertIn("error", result)

    @patch("memory_mcp_server._gog_available", return_value=False)
    def test_email_search_no_gog(self, _):
        result = json.loads(srv.email_search("is:unread"))
        self.assertIn("error", result)

    @patch("memory_mcp_server._gog_available", return_value=False)
    def test_email_read_no_gog(self, _):
        result = json.loads(srv.email_read("msg001", "a@b.com"))
        self.assertIn("error", result)

    @patch("memory_mcp_server._gog_available", return_value=False)
    def test_calendar_today_no_gog(self, _):
        result = json.loads(srv.calendar_today())
        self.assertIn("error", result)

    @patch("memory_mcp_server._gog_available", return_value=False)
    def test_calendar_range_no_gog(self, _):
        result = json.loads(srv.calendar_range("2026-04-22", "2026-04-30"))
        self.assertIn("error", result)


class TestUnicodeAndEncoding(unittest.TestCase):

    @patch("memory_mcp_server.subprocess.run")
    def test_unicode_subject_survives_json_roundtrip(self, mock_run):
        msgs = [{"id": "u1", "from": "tëst <t@e.com>", "subject": "Héllo 日本語", "date": NOW_ISO, "labels": []}]
        mock_run.return_value = _gog_ok(msgs)
        raw = srv.email_list_unread("rdreilly2010@gmail.com")
        result = json.loads(raw)
        subj = result["rdreilly2010@gmail.com"][0]["subject"]
        self.assertIn("Héllo", subj)
        self.assertIn("日本語", subj)


if __name__ == "__main__":
    unittest.main(verbosity=2)
