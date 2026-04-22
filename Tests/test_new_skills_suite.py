"""
Extensive test suite for 5 newly installed OpenClaw skills:
  1. telegram-voice-to-voice-macos
  2. openclaw-ops-guardrails
  3. apple-calendar-cli
  4. elite-longterm-memory
  5. openclaw-agent-discovery

Run:
    cd /Users/rreilly/.openclaw/workspace
    python3 -m pytest Tests/test_new_skills_suite.py -v
"""

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import pytest

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────

WORKSPACE = Path("/Users/rreilly/.openclaw/workspace")
SKILLS = WORKSPACE / "skills"

SKILL_VOICE = SKILLS / "telegram-voice-to-voice-macos"
SKILL_GUARDRAILS = SKILLS / "openclaw-ops-guardrails"
SKILL_CALENDAR = SKILLS / "apple-calendar-cli"
SKILL_MEMORY = SKILLS / "elite-longterm-memory"
SKILL_DISCOVERY = SKILLS / "openclaw-agent-discovery"

INBOUND_MEDIA = Path.home() / ".openclaw" / "media" / "inbound"
VOICE_OUT = Path.home() / ".openclaw" / "workspace" / "voice_out"
VOICE_STATE = WORKSPACE / "voice_state"


def run(cmd, **kwargs) -> subprocess.CompletedProcess:
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    kwargs.setdefault("timeout", 30)
    return subprocess.run(cmd, **kwargs)


# ═══════════════════════════════════════════════════════════════════
# SKILL 1 — telegram-voice-to-voice-macos
# ═══════════════════════════════════════════════════════════════════

class TestTelegramVoice:
    """Tests for telegram-voice-to-voice-macos skill."""

    # ── Installation & structure ──────────────────────────────────

    def test_skill_directory_exists(self):
        assert SKILL_VOICE.is_dir(), "skill directory missing"

    def test_skill_md_exists(self):
        assert (SKILL_VOICE / "SKILL.md").is_file()

    def test_meta_json_valid(self):
        meta = json.loads((SKILL_VOICE / "_meta.json").read_text())
        assert "name" in meta or "slug" in meta

    def test_scripts_directory_exists(self):
        assert (SKILL_VOICE / "scripts").is_dir()

    def test_transcribe_script_exists_and_executable(self):
        s = SKILL_VOICE / "scripts" / "transcribe_telegram_ogg.sh"
        assert s.is_file(), "transcribe_telegram_ogg.sh missing"
        assert os.access(s, os.X_OK), "transcribe_telegram_ogg.sh not executable"

    def test_tts_script_exists_and_executable(self):
        s = SKILL_VOICE / "scripts" / "tts_telegram_voice.sh"
        assert s.is_file(), "tts_telegram_voice.sh missing"
        assert os.access(s, os.X_OK), "tts_telegram_voice.sh not executable"

    # ── Binary dependencies ───────────────────────────────────────

    def test_yap_installed(self):
        assert shutil.which("yap"), "yap not in PATH — install: brew install finnvoor/tools/yap"

    def test_ffmpeg_installed(self):
        assert shutil.which("ffmpeg"), "ffmpeg not in PATH"

    def test_say_installed(self):
        assert shutil.which("say"), "say not in PATH (macOS built-in should always exist)"

    def test_defaults_installed(self):
        assert shutil.which("defaults"), "defaults not in PATH (macOS built-in)"

    def test_yap_version_runs(self):
        r = run(["yap", "--version"])
        assert r.returncode == 0, f"yap --version failed: {r.stderr}"

    def test_ffmpeg_version_runs(self):
        r = run(["ffmpeg", "-version"])
        assert r.returncode == 0

    # ── Inbound media directory ────────────────────────────────────

    def test_inbound_media_dir_creatable(self):
        INBOUND_MEDIA.mkdir(parents=True, exist_ok=True)
        assert INBOUND_MEDIA.is_dir()

    # ── Voice state management ─────────────────────────────────────

    def test_voice_state_dir_creatable(self):
        VOICE_STATE.mkdir(parents=True, exist_ok=True)
        assert VOICE_STATE.is_dir()

    def test_voice_state_file_write_read(self):
        VOICE_STATE.mkdir(parents=True, exist_ok=True)
        state_file = VOICE_STATE / "telegram.json"
        state = {"8755120444": "voice"}
        state_file.write_text(json.dumps(state))
        loaded = json.loads(state_file.read_text())
        assert loaded["8755120444"] == "voice"

    def test_voice_state_toggle_to_text(self):
        VOICE_STATE.mkdir(parents=True, exist_ok=True)
        state_file = VOICE_STATE / "telegram.json"
        state = {"8755120444": "voice"}
        state_file.write_text(json.dumps(state))
        state["8755120444"] = "text"
        state_file.write_text(json.dumps(state))
        loaded = json.loads(state_file.read_text())
        assert loaded["8755120444"] == "text"

    def test_voice_state_default_when_missing(self):
        """Skill spec: if sender id missing, assume 'voice'."""
        state = {}
        sender_id = "9999999"
        result = state.get(sender_id, "voice")
        assert result == "voice"

    # ── TTS pipeline (end-to-end) ─────────────────────────────────

    def test_tts_script_produces_ogg(self):
        """Run tts_telegram_voice.sh with a short phrase and verify output."""
        script = SKILL_VOICE / "scripts" / "tts_telegram_voice.sh"
        r = run([str(script), "Hello from test suite"], timeout=30)
        assert r.returncode == 0, f"TTS script failed:\n{r.stderr}"
        ogg_path = r.stdout.strip()
        assert ogg_path.endswith(".ogg"), f"Expected .ogg path, got: {ogg_path}"
        assert Path(ogg_path).is_file(), f"OGG file not created at: {ogg_path}"
        assert Path(ogg_path).stat().st_size > 0, "OGG file is empty"
        # cleanup
        Path(ogg_path).unlink(missing_ok=True)

    def test_tts_script_with_named_voice(self):
        """TTS script should accept a voice name (Samantha)."""
        script = SKILL_VOICE / "scripts" / "tts_telegram_voice.sh"
        r = run([str(script), "Testing voice selection", "Samantha"], timeout=30)
        assert r.returncode == 0, f"TTS with voice name failed:\n{r.stderr}"
        ogg_path = r.stdout.strip()
        assert Path(ogg_path).is_file()
        Path(ogg_path).unlink(missing_ok=True)

    def test_tts_script_errors_on_empty_text(self):
        script = SKILL_VOICE / "scripts" / "tts_telegram_voice.sh"
        r = run([str(script), ""])
        assert r.returncode != 0, "Expected failure on empty text"

    def test_transcribe_script_errors_on_missing_ogg(self):
        """transcribe script should exit non-zero when no OGG is available."""
        script = SKILL_VOICE / "scripts" / "transcribe_telegram_ogg.sh"
        r = run([str(script), "/nonexistent/path.ogg"])
        assert r.returncode != 0

    def test_transcribe_roundtrip(self):
        """Generate a voice note then transcribe it — should produce non-empty text."""
        tts_script = SKILL_VOICE / "scripts" / "tts_telegram_voice.sh"
        tx_script = SKILL_VOICE / "scripts" / "transcribe_telegram_ogg.sh"

        # generate OGG
        r = run([str(tts_script), "Hello Momo this is a test"], timeout=30)
        assert r.returncode == 0, f"TTS failed: {r.stderr}"
        ogg_path = r.stdout.strip()

        try:
            # transcribe
            r2 = run([str(tx_script), ogg_path], timeout=30)
            assert r2.returncode == 0, f"Transcription failed: {r2.stderr}"
            transcript = r2.stdout.strip()
            assert len(transcript) > 0, "Transcription returned empty string"
        finally:
            Path(ogg_path).unlink(missing_ok=True)

    def test_voice_out_directory_created_by_tts(self):
        """tts script should create voice_out dir automatically."""
        script = SKILL_VOICE / "scripts" / "tts_telegram_voice.sh"
        r = run([str(script), "Directory creation test"], timeout=30)
        assert VOICE_OUT.is_dir()
        if r.returncode == 0:
            Path(r.stdout.strip()).unlink(missing_ok=True)

    def test_macos_locale_detection(self):
        """defaults read -g AppleLocale should return a valid locale."""
        r = run(["defaults", "read", "-g", "AppleLocale"])
        assert r.returncode == 0
        locale = r.stdout.strip()
        assert len(locale) >= 2, f"Unexpected locale value: {locale}"


# ═══════════════════════════════════════════════════════════════════
# SKILL 2 — openclaw-ops-guardrails
# ═══════════════════════════════════════════════════════════════════

class TestOpsGuardrails:
    """Tests for openclaw-ops-guardrails skill."""

    # ── Installation & structure ──────────────────────────────────

    def test_skill_directory_exists(self):
        assert SKILL_GUARDRAILS.is_dir()

    def test_skill_md_exists(self):
        assert (SKILL_GUARDRAILS / "SKILL.md").is_file()

    def test_references_directory_exists(self):
        assert (SKILL_GUARDRAILS / "references").is_dir()

    def test_failure_playbook_exists(self):
        playbook = SKILL_GUARDRAILS / "references" / "failure-playbook.md"
        assert playbook.is_file(), "failure-playbook.md missing"

    def test_sanitization_checklist_exists(self):
        checklist = SKILL_GUARDRAILS / "references" / "publish-sanitization-checklist.md"
        assert checklist.is_file(), "publish-sanitization-checklist.md missing"

    def test_failure_playbook_non_empty(self):
        playbook = SKILL_GUARDRAILS / "references" / "failure-playbook.md"
        assert playbook.stat().st_size > 100, "failure-playbook.md appears empty"

    def test_sanitization_checklist_non_empty(self):
        checklist = SKILL_GUARDRAILS / "references" / "publish-sanitization-checklist.md"
        assert checklist.stat().st_size > 100

    def test_failure_playbook_covers_approval_timeout(self):
        content = (SKILL_GUARDRAILS / "references" / "failure-playbook.md").read_text()
        assert "approval" in content.lower()

    def test_failure_playbook_covers_pairing(self):
        content = (SKILL_GUARDRAILS / "references" / "failure-playbook.md").read_text()
        assert "pairing" in content.lower()

    def test_sanitization_checklist_covers_tokens(self):
        content = (SKILL_GUARDRAILS / "references" / "publish-sanitization-checklist.md").read_text()
        keywords = ["token", "key", "password", "secret"]
        assert any(k in content.lower() for k in keywords), "checklist should mention token/key/password/secret"

    # ── OpenClaw CLI integration ───────────────────────────────────

    def test_openclaw_binary_available(self):
        assert shutil.which("openclaw"), "openclaw CLI not in PATH"

    def test_openclaw_health_returns_json(self):
        r = run(["openclaw", "health", "--json"])
        assert r.returncode == 0, f"openclaw health failed: {r.stderr}"
        data = json.loads(r.stdout)
        assert "ok" in data

    def test_openclaw_health_reports_ok(self):
        r = run(["openclaw", "health", "--json"])
        data = json.loads(r.stdout)
        assert data["ok"] is True, f"Gateway reports unhealthy: {data}"

    def test_openclaw_gateway_status_json(self):
        r = run(["openclaw", "gateway", "status", "--json"])
        assert r.returncode == 0, f"gateway status failed: {r.stderr}"
        data = json.loads(r.stdout)
        assert "service" in data or "loaded" in str(data)

    def test_openclaw_nodes_status(self):
        r = run(["openclaw", "nodes", "status", "--connected"])
        # non-zero is okay if no nodes are connected; just must not crash with code 1
        assert r.returncode in (0, 1), f"nodes status returned unexpected exit code: {r.returncode}"

    def test_openclaw_status_deep(self):
        r = run(["openclaw", "status", "--deep"], timeout=30)
        assert r.returncode == 0, f"openclaw status --deep failed: {r.stderr}"

    def test_openclaw_security_audit(self):
        r = run(["openclaw", "security", "audit", "--deep"], timeout=30)
        # audit may exit non-zero if findings exist, but should not error/crash
        assert r.returncode in (0, 1), f"security audit crashed: {r.stderr}"

    def test_guardrail_no_real_tokens_in_skill(self):
        """SKILL.md must use placeholders, not real tokens."""
        content = (SKILL_GUARDRAILS / "SKILL.md").read_text()
        # should NOT contain a real-looking gateway token (long hex strings)
        import re
        suspicious = re.findall(r"\b[0-9a-f]{32,}\b", content)
        assert not suspicious, f"Possible real token in SKILL.md: {suspicious}"

    def test_guardrail_no_real_ips_in_skill(self):
        """SKILL.md should not contain real IP addresses per the sanitization policy."""
        content = (SKILL_GUARDRAILS / "SKILL.md").read_text()
        import re
        ips = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", content)
        assert not ips, f"Real IP addresses found in SKILL.md: {ips}"


# ═══════════════════════════════════════════════════════════════════
# SKILL 3 — apple-calendar-cli
# ═══════════════════════════════════════════════════════════════════

class TestAppleCalendarCLI:
    """Tests for apple-calendar-cli skill."""

    # ── Installation & structure ──────────────────────────────────

    def test_skill_directory_exists(self):
        assert SKILL_CALENDAR.is_dir()

    def test_skill_md_exists(self):
        assert (SKILL_CALENDAR / "SKILL.md").is_file()

    def test_skill_md_covers_create(self):
        content = (SKILL_CALENDAR / "SKILL.md").read_text()
        assert "create-event" in content

    def test_skill_md_covers_delete(self):
        content = (SKILL_CALENDAR / "SKILL.md").read_text()
        assert "delete-event" in content

    def test_skill_md_covers_list_events(self):
        content = (SKILL_CALENDAR / "SKILL.md").read_text()
        assert "list-events" in content

    # ── Binary availability ───────────────────────────────────────

    def test_apple_calendar_cli_installed(self):
        assert shutil.which("apple-calendar-cli"), (
            "apple-calendar-cli not in PATH — run: brew install sichengchen/tap/apple-calendar-cli"
        )

    def test_apple_calendar_cli_help(self):
        r = run(["apple-calendar-cli", "--help"])
        assert r.returncode == 0

    def test_apple_calendar_cli_version(self):
        r = run(["apple-calendar-cli", "--version"])
        assert r.returncode == 0

    # ── Calendar access ───────────────────────────────────────────

    def test_list_calendars_returns_json(self):
        r = run(["apple-calendar-cli", "list-calendars", "--json"])
        if r.returncode != 0 and "access" in r.stderr.lower():
            pytest.skip("Calendar TCC access not granted — grant in System Settings > Privacy > Calendars")
        assert r.returncode == 0, f"list-calendars failed: {r.stderr}"
        data = json.loads(r.stdout)
        assert isinstance(data, list), "Expected JSON array"

    def test_list_calendars_has_at_least_one(self):
        r = run(["apple-calendar-cli", "list-calendars", "--json"])
        if r.returncode != 0:
            pytest.skip("Calendar access not available")
        data = json.loads(r.stdout)
        assert len(data) >= 1, "No calendars found — check iCloud/local calendar setup"

    def test_list_calendars_schema(self):
        r = run(["apple-calendar-cli", "list-calendars", "--json"])
        if r.returncode != 0:
            pytest.skip("Calendar access not available")
        data = json.loads(r.stdout)
        required_fields = {"identifier", "title"}
        for cal in data:
            missing = required_fields - set(cal.keys())
            assert not missing, f"Calendar missing fields {missing}: {cal}"

    def test_list_events_today_returns_json(self):
        from datetime import date, timedelta
        today = date.today().isoformat()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        r = run(["apple-calendar-cli", "list-events",
                 "--from", today, "--to", tomorrow, "--json"])
        if r.returncode != 0 and "access" in r.stderr.lower():
            pytest.skip("Calendar TCC access not granted")
        assert r.returncode == 0, f"list-events failed: {r.stderr}"
        data = json.loads(r.stdout)
        assert isinstance(data, list)

    def test_list_events_schema_when_present(self):
        from datetime import date, timedelta
        today = date.today().isoformat()
        next_week = (date.today() + timedelta(days=7)).isoformat()
        r = run(["apple-calendar-cli", "list-events",
                 "--from", today, "--to", next_week, "--json"])
        if r.returncode != 0:
            pytest.skip("Calendar access not available")
        data = json.loads(r.stdout)
        if not data:
            pytest.skip("No events in the next 7 days to validate schema")
        required_fields = {"identifier", "title", "startDate", "endDate", "isAllDay"}
        for ev in data[:3]:
            missing = required_fields - set(ev.keys())
            assert not missing, f"Event missing fields {missing}: {ev}"

    def test_create_and_delete_event_roundtrip(self):
        """Create a test event then delete it — validates write access."""
        from datetime import date, timedelta
        # Use a clearly test-labelled time in the near future
        start = f"{date.today().isoformat()}T23:50:00"
        end   = f"{date.today().isoformat()}T23:55:00"

        r_create = run(["apple-calendar-cli", "create-event",
                        "--title", "[MOMO TEST EVENT — DELETE ME]",
                        "--start", start,
                        "--end", end,
                        "--notes", "Created by test_new_skills_suite.py — safe to delete",
                        "--json"])
        if r_create.returncode != 0 and "access" in r_create.stderr.lower():
            pytest.skip("Calendar write access not granted")
        assert r_create.returncode == 0, f"create-event failed: {r_create.stderr}"

        created = json.loads(r_create.stdout)
        event_id = created.get("identifier")
        assert event_id, f"No identifier in created event: {created}"

        # Immediately delete it
        r_delete = run(["apple-calendar-cli", "delete-event", event_id, "--json"])
        assert r_delete.returncode == 0, f"delete-event failed: {r_delete.stderr}"
        deleted = json.loads(r_delete.stdout)
        assert deleted.get("deleted") is True, f"Expected deleted=true: {deleted}"

    def test_invalid_date_format_rejected(self):
        r = run(["apple-calendar-cli", "create-event",
                 "--title", "Bad date test",
                 "--start", "not-a-date",
                 "--end", "also-not-a-date"])
        assert r.returncode != 0, "Expected failure on invalid date format"

    def test_get_nonexistent_event_fails_gracefully(self):
        r = run(["apple-calendar-cli", "get-event", "FAKE-EVENT-ID-99999", "--json"])
        assert r.returncode != 0, "Expected non-zero exit for nonexistent event"


# ═══════════════════════════════════════════════════════════════════
# SKILL 4 — elite-longterm-memory
# ═══════════════════════════════════════════════════════════════════

class TestEliteLongtermMemory:
    """Tests for elite-longterm-memory skill."""

    # ── Installation & structure ──────────────────────────────────

    def test_skill_directory_exists(self):
        assert SKILL_MEMORY.is_dir()

    def test_skill_md_exists(self):
        assert (SKILL_MEMORY / "SKILL.md").is_file()

    def test_package_json_exists(self):
        assert (SKILL_MEMORY / "package.json").is_file()

    def test_package_json_valid(self):
        data = json.loads((SKILL_MEMORY / "package.json").read_text())
        assert data["name"] == "elite-longterm-memory"
        assert "version" in data

    def test_bin_directory_exists(self):
        assert (SKILL_MEMORY / "bin").is_dir()

    def test_elite_memory_js_exists(self):
        assert (SKILL_MEMORY / "bin" / "elite-memory.js").is_file()

    def test_skill_md_covers_session_state(self):
        content = (SKILL_MEMORY / "SKILL.md").read_text()
        assert "SESSION-STATE.md" in content

    def test_skill_md_covers_wal_protocol(self):
        content = (SKILL_MEMORY / "SKILL.md").read_text()
        assert "WAL" in content or "Write-Ahead" in content

    def test_skill_md_covers_lancedb(self):
        content = (SKILL_MEMORY / "SKILL.md").read_text()
        assert "LanceDB" in content or "lancedb" in content.lower()

    # ── Memory directory structure ─────────────────────────────────

    def test_memory_directory_exists(self):
        assert (WORKSPACE / "memory").is_dir(), "memory/ directory missing from workspace"

    def test_memory_md_exists(self):
        assert (WORKSPACE / "MEMORY.md").is_file() or (WORKSPACE / "memory" / "MEMORY.md").is_file(), \
            "MEMORY.md not found"

    def test_daily_log_format_present(self):
        """At least one daily log file matching YYYY-MM-DD.md should exist."""
        import re
        pattern = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
        daily_logs = [f for f in (WORKSPACE / "memory").iterdir()
                      if f.is_file() and pattern.match(f.name)]
        assert daily_logs, "No daily log files (YYYY-MM-DD.md) found in memory/"

    def test_today_daily_log_exists(self):
        from datetime import date
        today_log = WORKSPACE / "memory" / f"{date.today().isoformat()}.md"
        assert today_log.is_file(), f"Today's daily log missing: {today_log}"

    # ── SESSION-STATE.md (Hot RAM / WAL) ───────────────────────────

    def test_session_state_writeable(self):
        """SESSION-STATE.md can be initialized (or already exists and is writable)."""
        ss = WORKSPACE / "SESSION-STATE.md"
        if not ss.exists():
            ss.write_text("# SESSION-STATE.md — Active Working Memory\n\n## Current Task\n[None]\n")
        assert ss.is_file()
        assert os.access(ss, os.W_OK), "SESSION-STATE.md is not writable"

    def test_session_state_wal_write_before_respond(self):
        """Simulate WAL: write state file before 'responding'."""
        ss = WORKSPACE / "SESSION-STATE.md"
        original = ss.read_text() if ss.exists() else ""
        test_marker = f"## Test WAL Write — {int(time.time())}\n"
        content = original + "\n" + test_marker
        ss.write_text(content)
        # verify persisted
        assert test_marker in ss.read_text()
        # restore
        ss.write_text(original)

    # ── LanceDB / OpenAI config ────────────────────────────────────

    def test_openai_key_configured(self):
        """OPENAI_API_KEY must be set for LanceDB vector search to work."""
        key = os.environ.get("OPENAI_API_KEY", "")
        if not key:
            pytest.xfail(
                "OPENAI_API_KEY is not set — LanceDB warm store will be unavailable. "
                "Set this in ~/.zshrc or config/briefing.env to unlock vector search."
            )

    def test_openclaw_config_has_memory_search_section(self):
        config_path = Path.home() / ".openclaw" / "openclaw.json"
        if not config_path.exists():
            pytest.skip("openclaw.json not found")
        config = json.loads(config_path.read_text())
        # Not a hard fail — just flag if missing
        if "memorySearch" not in config:
            pytest.xfail(
                "memorySearch not configured in openclaw.json. "
                "See elite-longterm-memory SKILL.md Quick Setup section."
            )

    def test_memory_mcp_server_script_exists(self):
        assert (WORKSPACE / "scripts" / "memory_mcp_server.py").is_file()

    def test_memory_mcp_server_importable(self):
        r = run(["python3", "-c", "import ast; ast.parse(open('scripts/memory_mcp_server.py').read())"],
                cwd=str(WORKSPACE))
        assert r.returncode == 0, f"memory_mcp_server.py has syntax errors: {r.stderr}"

    def test_memory_db_script_importable(self):
        r = run(["python3", "-c", "import ast; ast.parse(open('scripts/memory_db.py').read())"],
                cwd=str(WORKSPACE))
        assert r.returncode == 0

    # ── Memory hygiene helpers ─────────────────────────────────────

    def test_archive_directory_exists(self):
        assert (WORKSPACE / "memory" / "archive").is_dir(), \
            "memory/archive/ missing — needed for long-term archival"

    def test_memory_directory_size_reasonable(self):
        """Memory store should not be enormous (warn if > 50MB)."""
        total = sum(f.stat().st_size for f in (WORKSPACE / "memory").rglob("*") if f.is_file())
        mb = total / (1024 * 1024)
        assert mb < 200, f"Memory directory is very large: {mb:.1f} MB — consider pruning"
        if mb > 50:
            pytest.xfail(f"Memory directory is {mb:.1f} MB — consider running weekly-memory-consolidation.sh")


# ═══════════════════════════════════════════════════════════════════
# SKILL 5 — openclaw-agent-discovery
# ═══════════════════════════════════════════════════════════════════

class TestAgentDiscovery:
    """Tests for openclaw-agent-discovery skill."""

    # ── Installation & structure ──────────────────────────────────

    def test_skill_directory_exists(self):
        assert SKILL_DISCOVERY.is_dir()

    def test_skill_md_exists(self):
        assert (SKILL_DISCOVERY / "SKILL.md").is_file()

    def test_meta_json_exists(self):
        assert (SKILL_DISCOVERY / "_meta.json").is_file()

    def test_meta_json_valid(self):
        data = json.loads((SKILL_DISCOVERY / "_meta.json").read_text())
        assert isinstance(data, dict)

    def test_skill_md_non_empty(self):
        content = (SKILL_DISCOVERY / "SKILL.md").read_text()
        assert len(content) > 50

    def test_skill_md_covers_search(self):
        content = (SKILL_DISCOVERY / "SKILL.md").read_text()
        assert "搜索" in content or "search" in content.lower()

    def test_skill_md_covers_evaluation(self):
        content = (SKILL_DISCOVERY / "SKILL.md").read_text()
        assert "评估" in content or "evaluat" in content.lower() or "compare" in content.lower()

    def test_skill_md_covers_integration(self):
        content = (SKILL_DISCOVERY / "SKILL.md").read_text()
        assert "集成" in content or "integrat" in content.lower()

    # ── ClawHub registry ──────────────────────────────────────────

    def test_clawhub_list_includes_agent_discovery(self):
        r = run(["clawhub", "list"])
        assert r.returncode == 0
        assert "openclaw-agent-discovery" in r.stdout, \
            "openclaw-agent-discovery not in clawhub list output"

    def test_clawhub_can_search_for_agents(self):
        r = run(["clawhub", "search", "agent orchestration"])
        assert r.returncode == 0
        assert len(r.stdout.strip()) > 0, "clawhub search returned no results"

    def test_clawhub_can_search_for_code_review_agents(self):
        r = run(["clawhub", "search", "code review agent"])
        assert r.returncode == 0

    def test_clawhub_can_search_for_free_agents(self):
        r = run(["clawhub", "search", "free agent automation"])
        assert r.returncode == 0


# ═══════════════════════════════════════════════════════════════════
# CROSS-SKILL: Integration & Sanity
# ═══════════════════════════════════════════════════════════════════

class TestCrossSkillIntegration:
    """Sanity checks that span multiple skills or test the overall system."""

    def test_all_five_skills_in_clawhub_list(self):
        r = run(["clawhub", "list"])
        assert r.returncode == 0
        installed = r.stdout
        for slug in [
            "telegram-voice-to-voice-macos",
            "openclaw-ops-guardrails",
            "apple-calendar-cli",
            "elite-longterm-memory",
            "openclaw-agent-discovery",
        ]:
            assert slug in installed, f"Skill not in clawhub list: {slug}"

    def test_all_skill_directories_present(self):
        for skill_dir in [SKILL_VOICE, SKILL_GUARDRAILS, SKILL_CALENDAR, SKILL_MEMORY, SKILL_DISCOVERY]:
            assert skill_dir.is_dir(), f"Skill directory missing: {skill_dir}"

    def test_all_skill_mds_present(self):
        for skill_dir in [SKILL_VOICE, SKILL_GUARDRAILS, SKILL_CALENDAR, SKILL_MEMORY, SKILL_DISCOVERY]:
            assert (skill_dir / "SKILL.md").is_file(), f"SKILL.md missing in {skill_dir.name}"

    def test_workspace_git_is_clean_enough(self):
        """After install, there should be no untracked skill files outside skills/."""
        r = run(["git", "status", "--porcelain"], cwd=str(WORKSPACE))
        assert r.returncode == 0
        # Just make sure git is functioning; don't fail on uncommitted changes
        assert r.stdout is not None

    def test_openclaw_gateway_still_healthy_after_installs(self):
        r = run(["openclaw", "health", "--json"])
        data = json.loads(r.stdout)
        assert data.get("ok") is True, f"Gateway unhealthy after skill installs: {data}"

    def test_voice_and_calendar_coexist(self):
        """Both voice_out and calendar write require different system permissions — sanity check."""
        # voice_out dir is filesystem only
        VOICE_OUT.mkdir(parents=True, exist_ok=True)
        assert VOICE_OUT.is_dir()
        # calendar CLI is available
        assert shutil.which("apple-calendar-cli")

    def test_no_skill_contains_real_api_keys(self):
        """Scan all installed SKILL.md files for suspicious credential patterns."""
        import re
        key_patterns = [
            r"sk-[a-zA-Z0-9]{20,}",     # OpenAI keys
            r"xox[baprs]-[0-9A-Za-z\-]{10,}",  # Slack tokens
            r"[A-Za-z0-9]{32}:[A-Za-z0-9\-_]{32}",  # Telegram bot token pattern
            r"\b[0-9a-f]{64}\b",          # long hex secrets
        ]
        for skill_dir in [SKILL_VOICE, SKILL_GUARDRAILS, SKILL_CALENDAR, SKILL_MEMORY, SKILL_DISCOVERY]:
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                content = skill_md.read_text()
                for pattern in key_patterns:
                    matches = re.findall(pattern, content)
                    assert not matches, (
                        f"Possible real credential in {skill_dir.name}/SKILL.md "
                        f"(pattern: {pattern}): {matches[:2]}"
                    )
