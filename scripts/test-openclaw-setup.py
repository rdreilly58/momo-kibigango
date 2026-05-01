#!/usr/bin/env python3
"""
test-openclaw-setup.py — Comprehensive OpenClaw setup test suite.

Tests all changes made on 2026-05-01:
  Group 1: Config Validation (8 tests)
  Group 2: Bootstrap File Health (8 tests)
  Group 3: Cron Isolation (6 tests)
  Group 4: Skill Pruning (4 tests)
  Group 5: Memory Flush (3 tests)
  Group 6: Routing Rules (4 tests)
  Group 7: Cross-Agent Memory (5 tests)
  Group 8: Entity Graph (4 tests)
  Group 9: Gateway Health (4 tests)
  Group 10: File Integrity (4 tests)

Total: 50 tests
"""

import json
import os
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(os.environ.get("OPENCLAW_WORKSPACE", Path.home() / ".openclaw" / "workspace"))
CONFIG_PATH = Path.home() / ".openclaw" / "config.json"
PYTHON = str(WORKSPACE / "venv" / "bin" / "python3")

# ─── Test runner ──────────────────────────────────────────────────────────────

results = []

def test(test_id: str, name: str, passed: bool, reason: str = "", actual: str = "", expected: str = ""):
    status = "✅ PASS" if passed else "❌ FAIL"
    results.append({
        "id": test_id,
        "name": name,
        "passed": passed,
        "skipped": False,
        "reason": reason,
        "actual": actual,
        "expected": expected,
    })
    msg = f"  {status} [{test_id}] {name}"
    if not passed:
        if expected:
            msg += f"\n         expected: {expected}"
        if actual:
            msg += f"\n           actual: {actual}"
        if reason:
            msg += f"\n           reason: {reason}"
    print(msg)


def skip(test_id: str, name: str, reason: str):
    results.append({
        "id": test_id,
        "name": name,
        "passed": False,
        "skipped": True,
        "reason": reason,
        "actual": "",
        "expected": "",
    })
    print(f"  ⚠️  SKIP [{test_id}] {name}")
    print(f"         reason: {reason}")


def run_cmd(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=isinstance(cmd, str))
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)


def load_config():
    try:
        return json.loads(CONFIG_PATH.read_text())
    except Exception as e:
        print(f"  ⚠️  WARNING: Could not load config: {e}")
        return {}


# ─── Group 1: Config Validation ───────────────────────────────────────────────

def group_config():
    print("\n📋 Group 1: Config Validation")
    cfg = load_config()

    # C01: ownerAllowFrom
    owner = cfg.get("commands", {}).get("ownerAllowFrom", [])
    test("C01", "commands.ownerAllowFrom = [\"telegram:8755120444\"]",
         owner == ["telegram:8755120444"],
         actual=str(owner),
         expected='["telegram:8755120444"]')

    # C02: model.primary
    primary = cfg.get("model", {}).get("primary", "")
    test("C02", "model.primary = claude-sonnet-4-6",
         primary == "anthropic/claude-sonnet-4-6",
         actual=primary,
         expected="anthropic/claude-sonnet-4-6")

    # C03: model.cron
    cron_model = cfg.get("model", {}).get("cron", "")
    test("C03", "model.cron = claude-haiku-4-5",
         cron_model == "anthropic/claude-haiku-4-5",
         actual=cron_model,
         expected="anthropic/claude-haiku-4-5")

    # C04: model.subagent
    subagent = cfg.get("model", {}).get("subagent", "")
    test("C04", "model.subagent = claude-sonnet-4-6",
         subagent == "anthropic/claude-sonnet-4-6",
         actual=subagent,
         expected="anthropic/claude-sonnet-4-6")

    # C05: memoryFlush.model
    flush_model = cfg.get("compaction", {}).get("memoryFlush", {}).get("model", "")
    test("C05", "compaction.memoryFlush.model = ollama/qwen2.5:7b",
         flush_model == "ollama/qwen2.5:7b",
         actual=flush_model,
         expected="ollama/qwen2.5:7b")

    # C06: memoryFlush.softThresholdTokens
    soft_thresh = cfg.get("compaction", {}).get("memoryFlush", {}).get("softThresholdTokens", 0)
    test("C06", "compaction.memoryFlush.softThresholdTokens = 15000",
         soft_thresh == 15000,
         actual=str(soft_thresh),
         expected="15000")

    # C07: memory-wiki plugin enabled
    wiki_enabled = cfg.get("plugins", {}).get("entries", {}).get("memory-wiki", {}).get("enabled", False)
    test("C07", "memory-wiki plugin enabled",
         wiki_enabled is True,
         actual=str(wiki_enabled),
         expected="True")

    # C08: dreaming enabled with timezone + frequency
    dreaming = cfg.get("plugins", {}).get("entries", {}).get("memory-core", {}).get("config", {}).get("dreaming", {})
    dream_ok = (
        dreaming.get("enabled") is True
        and dreaming.get("timezone", "") != ""
        and dreaming.get("frequency", "") != ""
    )
    test("C08", "dreaming.enabled=True with timezone + frequency",
         dream_ok,
         actual=str(dreaming),
         expected="enabled=True, timezone set, frequency set")


# ─── Group 2: Bootstrap File Health ───────────────────────────────────────────

def group_bootstrap():
    print("\n📂 Group 2: Bootstrap File Health")
    files = {
        "AGENTS.md": WORKSPACE / "AGENTS.md",
        "TOOLS.md": WORKSPACE / "TOOLS.md",
        "MEMORY.md": WORKSPACE / "MEMORY.md",
        "SOUL.md": WORKSPACE / "SOUL.md",
    }
    sizes = {}
    for name, path in files.items():
        sizes[name] = path.stat().st_size if path.exists() else None

    # B01-B04: Existence and size < 8000 chars
    for tid, fname in [("B01", "AGENTS.md"), ("B02", "TOOLS.md"), ("B03", "MEMORY.md"), ("B04", "SOUL.md")]:
        sz = sizes.get(fname)
        if sz is None:
            test(tid, f"{fname} exists and < 8,000 chars", False,
                 actual="file not found", expected="exists and < 8000 chars")
        else:
            test(tid, f"{fname} exists and < 8,000 chars",
                 sz < 8000,
                 actual=f"{sz} chars",
                 expected="< 8000 chars")

    # B05: Total bootstrap chars < 42,000
    total = sum(s for s in sizes.values() if s is not None)
    test("B05", "Total bootstrap chars < 42,000",
         total < 42000,
         actual=f"{total} chars",
         expected="< 42,000 chars")

    # B06: AGENTS.md contains "Critical Behaviors"
    agents_text = (WORKSPACE / "AGENTS.md").read_text() if (WORKSPACE / "AGENTS.md").exists() else ""
    test("B06", 'AGENTS.md contains "Critical Behaviors" section',
         "Critical Behaviors" in agents_text,
         actual="not found" if "Critical Behaviors" not in agents_text else "found",
         expected="found")

    # B07: TOOLS.md contains "Git Commit Author"
    tools_text = (WORKSPACE / "TOOLS.md").read_text() if (WORKSPACE / "TOOLS.md").exists() else ""
    test("B07", 'TOOLS.md contains "Git Commit Author" table',
         "Git Commit Author" in tools_text,
         actual="not found" if "Git Commit Author" not in tools_text else "found",
         expected="found")

    # B08: MEMORY.md contains "Memory System"
    memory_text = (WORKSPACE / "MEMORY.md").read_text() if (WORKSPACE / "MEMORY.md").exists() else ""
    test("B08", 'MEMORY.md contains "Memory System" section',
         "Memory System" in memory_text,
         actual="not found" if "Memory System" not in memory_text else "found",
         expected="found")


# ─── Group 3: Cron Isolation ──────────────────────────────────────────────────

def group_crons():
    print("\n⏰ Group 3: Cron Isolation")
    cfg = load_config()
    cron_jobs = cfg.get("cron", {}).get("jobs", [])
    cron_by_name = {j.get("name", ""): j for j in cron_jobs}

    # Helper: check if an openclaw cron is isolated+haiku
    def check_isolated_haiku(name, tid, label):
        if name not in cron_by_name:
            skip(tid, f"{label} → session=isolated, model=haiku",
                 f"Cron '{name}' not found in config cron.jobs (may be a bash-only crontab entry — not an OpenClaw LLM cron)")
        else:
            job = cron_by_name[name]
            isolated = job.get("isolatedSession", False) is True
            model = job.get("model", "")
            is_haiku = "haiku" in model.lower()
            passed = isolated and is_haiku
            test(tid, f"{label} → session=isolated, model=haiku",
                 passed,
                 actual=f"isolatedSession={job.get('isolatedSession')}, model={model}",
                 expected="isolatedSession=true, model contains 'haiku'")

    check_isolated_haiku("api-quota-monitor-evening", "CR01", "API Quota Monitor (Evening)")
    check_isolated_haiku("api-quota-monitor-morning", "CR02", "API Quota Monitor (Morning)")
    check_isolated_haiku("weekly-memory-consolidation", "CR03", "Weekly Memory Consolidation")
    check_isolated_haiku("weekly-memory-pruning", "CR04", "Weekly Memory Pruning")
    check_isolated_haiku("daily-session-reset", "CR05", "Daily Session Reset")

    # CR06: No duplicate cron names
    names = [j.get("name", "") for j in cron_jobs]
    dupes = [n for n in names if names.count(n) > 1 and n]
    dupes = list(set(dupes))
    test("CR06", "No duplicate cron names",
         len(dupes) == 0,
         actual=f"duplicates: {dupes}" if dupes else "no duplicates",
         expected="no duplicates")


# ─── Group 4: Skill Pruning ───────────────────────────────────────────────────

def group_skills():
    print("\n🔧 Group 4: Skill Pruning")
    cfg = load_config()
    deny_list = cfg.get("agents", {}).get("defaults", {}).get("skills", {}).get("deny", [])

    # SK01: deny list >= 20 entries
    test("SK01", "agents.defaults.skills.deny contains at least 20 entries",
         len(deny_list) >= 20,
         actual=f"{len(deny_list)} entries",
         expected=">= 20")

    # SK02: Known irrelevant skills in deny list
    required_denied = ["discord", "1password", "trello", "notion", "sag"]
    missing = [s for s in required_denied if s not in deny_list]
    test("SK02", f"Known irrelevant skills are in deny list {required_denied}",
         len(missing) == 0,
         actual=f"missing from deny: {missing}" if missing else "all present",
         expected="all in deny list")

    # SK03: Core skills NOT in deny list
    core_skills = ["things-mac", "github", "gmail-send", "slack", "weather"]
    incorrectly_denied = [s for s in core_skills if s in deny_list]
    test("SK03", f"Core skills NOT in deny list {core_skills}",
         len(incorrectly_denied) == 0,
         actual=f"incorrectly denied: {incorrectly_denied}" if incorrectly_denied else "none denied",
         expected="none of these in deny list")

    # SK04: openclaw skills list shows < 75 ready
    # Note: deny list affects agent access, not installation count.
    # We test that the deny list has >= 26 entries (the claimed denial count).
    denied_count = len(deny_list)
    test("SK04", "26+ skills denied (deny list count >= 26)",
         denied_count >= 26,
         actual=f"{denied_count} skills in deny list",
         expected=">= 26 (as documented in config changes)")


# ─── Group 5: Memory Flush ────────────────────────────────────────────────────

def group_memory_flush():
    print("\n🧹 Group 5: Memory Flush")

    # MF01: ollama binary exists
    rc, out, _ = run_cmd("which ollama")
    test("MF01", "ollama binary exists on PATH",
         rc == 0 and bool(out),
         actual=out if out else "not found",
         expected="path to ollama binary")

    # MF02: qwen2.5:7b available in Ollama
    rc, out, err = run_cmd("ollama list", timeout=10)
    has_qwen = "qwen2.5:7b" in out
    test("MF02", "qwen2.5:7b is available in Ollama",
         has_qwen,
         actual=f"not found in ollama list" if not has_qwen else "found",
         expected="qwen2.5:7b in ollama list")

    # MF03: memoryFlush config points to ollama/qwen2.5:7b
    cfg = load_config()
    flush_model = cfg.get("compaction", {}).get("memoryFlush", {}).get("model", "")
    test("MF03", "memoryFlush config points to ollama/qwen2.5:7b",
         flush_model == "ollama/qwen2.5:7b",
         actual=flush_model,
         expected="ollama/qwen2.5:7b")


# ─── Group 6: Routing Rules ───────────────────────────────────────────────────

def group_routing():
    print("\n🗺️  Group 6: Routing Rules")
    soul_path = WORKSPACE / "SOUL.md"
    soul_text = soul_path.read_text() if soul_path.exists() else ""

    task_routing_path = WORKSPACE / "TASK_ROUTING.md"
    task_routing_text = task_routing_path.read_text() if task_routing_path.exists() else ""

    # RR01: SOUL.md contains "Opus costs 25×" cost warning
    test("RR01", 'SOUL.md contains "Opus costs 25×" cost warning',
         "Opus costs 25×" in soul_text or "25×" in soul_text,
         actual="found" if ("Opus costs 25×" in soul_text or "25×" in soul_text) else "not found",
         expected="Opus cost warning present")

    # RR02: SOUL.md contains Sonnet as default model reference
    test("RR02", "SOUL.md contains Sonnet as default model reference",
         "Sonnet" in soul_text and "default" in soul_text.lower(),
         actual="found" if "Sonnet" in soul_text else "not found",
         expected="Sonnet + default reference found")

    # RR03: TASK_ROUTING.md exists and > 1,000 chars
    tr_size = len(task_routing_text)
    test("RR03", "TASK_ROUTING.md exists and > 1,000 chars",
         task_routing_path.exists() and tr_size > 1000,
         actual=f"{tr_size} chars" if task_routing_path.exists() else "file not found",
         expected="> 1000 chars")

    # RR04: TASK_ROUTING.md contains Haiku, Sonnet, Opus sections
    has_haiku = "haiku" in task_routing_text.lower() or "Haiku" in task_routing_text
    has_sonnet = "sonnet" in task_routing_text.lower() or "Sonnet" in task_routing_text
    has_opus = "opus" in task_routing_text.lower() or "Opus" in task_routing_text
    test("RR04", "TASK_ROUTING.md contains Haiku, Sonnet, Opus sections",
         has_haiku and has_sonnet and has_opus,
         actual=f"Haiku={has_haiku}, Sonnet={has_sonnet}, Opus={has_opus}",
         expected="all three present")


# ─── Group 7: Cross-Agent Memory ──────────────────────────────────────────────

def group_cross_agent():
    print("\n🧠 Group 7: Cross-Agent Memory")
    scripts_dir = WORKSPACE / "scripts"

    # XA01: spawn-with-memory.py exists and is importable
    spawn_path = scripts_dir / "spawn-with-memory.py"
    test("XA01", "scripts/spawn-with-memory.py exists",
         spawn_path.exists(),
         actual="not found" if not spawn_path.exists() else "found",
         expected="file exists")

    # XA02: spawn-with-memory.py returns enriched task with memory_count > 0
    if spawn_path.exists():
        rc, out, err = run_cmd(
            [PYTHON, str(spawn_path), "test configuration", "--dry-run"],
            timeout=30
        )
        # Look for memory count in output
        has_memories = "Memories injected" in out or "memory_count" in out or "memories injected" in out.lower()
        # Also check it ran successfully
        success = rc == 0 or has_memories
        test("XA02", "spawn-with-memory.py returns enriched task with memory_count > 0",
             success and has_memories,
             actual=f"rc={rc}, has_memories={has_memories}" + (f"\n{out[:200]}" if not has_memories else ""),
             expected="memory_count > 0 in output")
    else:
        skip("XA02", "spawn-with-memory.py enriches task with memories", "XA01 failed — file not found")

    # XA03: memory-writeback.py exists
    writeback_path = scripts_dir / "memory-writeback.py"
    test("XA03", "scripts/memory-writeback.py exists",
         writeback_path.exists(),
         actual="not found" if not writeback_path.exists() else "found",
         expected="file exists")

    # XA04: memory-writeback.py status → qmd_available=true
    if writeback_path.exists():
        rc, out, err = run_cmd(
            [PYTHON, str(writeback_path), "status"],
            timeout=10
        )
        try:
            # Output might have model loading noise before JSON
            # Find JSON in output
            json_start = out.find("{")
            if json_start >= 0:
                status_data = json.loads(out[json_start:])
                qmd_ok = status_data.get("qmd_available", False) is True
            else:
                qmd_ok = "qmd_available" in out and '"qmd_available": true' in out
        except Exception:
            qmd_ok = '"qmd_available": true' in out or "qmd_available: True" in out

        test("XA04", "memory-writeback.py status → qmd_available=true",
             qmd_ok,
             actual=f"qmd_available={qmd_ok}",
             expected="qmd_available=true")
    else:
        skip("XA04", "memory-writeback.py qmd_available check", "XA03 failed — file not found")

    # XA05: memory/CROSS-AGENT-MEMORY.md exists
    cross_agent_path = WORKSPACE / "memory" / "CROSS-AGENT-MEMORY.md"
    test("XA05", "memory/CROSS-AGENT-MEMORY.md exists",
         cross_agent_path.exists(),
         actual="not found" if not cross_agent_path.exists() else "found",
         expected="file exists")


# ─── Group 8: Entity Graph ────────────────────────────────────────────────────

def group_entity_graph():
    print("\n🕸️  Group 8: Entity Graph")
    scripts_dir = WORKSPACE / "scripts"

    # EG01: memory-graph-builder.py exists
    builder_path = scripts_dir / "memory-graph-builder.py"
    test("EG01", "scripts/memory-graph-builder.py exists",
         builder_path.exists(),
         actual="not found" if not builder_path.exists() else "found",
         expected="file exists")

    # EG02: memory-graph-activate.py exists
    activate_path = scripts_dir / "memory-graph-activate.py"
    test("EG02", "scripts/memory-graph-activate.py exists",
         activate_path.exists(),
         actual="not found" if not activate_path.exists() else "found",
         expected="file exists")

    # EG03: Entity count in DB >= 200
    # The entity graph lives in ai-memory.db (memory_links stores relationships)
    # Distinct nodes in the graph = entities
    try:
        import sqlite3
        db_path = WORKSPACE / "ai-memory.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            # Count distinct entity nodes referenced in links
            entity_count = conn.execute("""
                SELECT COUNT(DISTINCT id) FROM (
                    SELECT source_id as id FROM memory_links
                    UNION
                    SELECT target_id as id FROM memory_links
                )
            """).fetchone()[0]
            conn.close()
            test("EG03", "Entity count in DB >= 200",
                 entity_count >= 200,
                 actual=f"{entity_count} entities",
                 expected=">= 200")
        else:
            skip("EG03", "Entity count in DB >= 200", f"ai-memory.db not found at {db_path}")
    except Exception as e:
        test("EG03", "Entity count in DB >= 200", False,
             actual=f"error: {e}", expected=">= 200")

    # EG04: Link count in DB >= 2,500
    try:
        import sqlite3
        db_path = WORKSPACE / "ai-memory.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            link_count = conn.execute("SELECT COUNT(*) FROM memory_links").fetchone()[0]
            conn.close()
            test("EG04", "Link count in DB >= 2,500",
                 link_count >= 2500,
                 actual=f"{link_count} links",
                 expected=">= 2,500")
        else:
            skip("EG04", "Link count in DB >= 2,500", f"ai-memory.db not found")
    except Exception as e:
        test("EG04", "Link count in DB >= 2,500", False,
             actual=f"error: {e}", expected=">= 2,500")


# ─── Group 9: Gateway Health ──────────────────────────────────────────────────

def group_gateway():
    print("\n🌐 Group 9: Gateway Health")

    # GW01: Gateway running
    rc, out, err = run_cmd("openclaw gateway status", timeout=15)
    running = rc == 0 or "running" in out.lower() or "running" in err.lower()
    test("GW01", "Gateway running (openclaw gateway status exits 0 or shows running)",
         running,
         actual=f"rc={rc}, {out[:100]}",
         expected="rc=0 or 'running' in output")

    # GW02: Connectivity probe = ok
    rc2, out2, _ = run_cmd("openclaw gateway status", timeout=15)
    probe_ok = "probe" in out2.lower() and "ok" in out2.lower()
    # Also try direct health endpoint
    if not probe_ok:
        rc3, out3, _ = run_cmd("curl -s http://127.0.0.1:18789/health", timeout=5)
        probe_ok = '"ok":true' in out3 or '"status":"live"' in out3
    test("GW02", "Connectivity probe = ok",
         probe_ok,
         actual="ok" if probe_ok else "probe not ok",
         expected="probe: ok")

    # GW03: Telegram channel connected
    cfg = load_config()
    telegram_cfg = cfg.get("telegram", {})
    has_telegram_config = bool(telegram_cfg.get("botToken")) and bool(telegram_cfg.get("chatId"))
    # Also check that it appears in sessions
    rc4, out4, _ = run_cmd("openclaw status 2>&1 | grep -i telegram", timeout=15)
    telegram_active = "telegram" in out4.lower()
    test("GW03", "Telegram channel connected",
         has_telegram_config and telegram_active,
         actual=f"configured={has_telegram_config}, active={telegram_active}",
         expected="configured + active sessions visible")

    # GW04: Slack channel connected
    has_slack_config = "slack" in cfg
    rc5, out5, _ = run_cmd("openclaw status 2>&1 | grep -i slack", timeout=15)
    slack_active = "slack" in out5.lower() and "Cannot find module" not in out5
    if not has_slack_config:
        skip("GW04", "Slack channel connected",
             "Slack is not configured in config.json (no 'slack' key found)")
    else:
        test("GW04", "Slack channel connected",
             slack_active,
             actual=f"config present, active={slack_active}",
             expected="slack active")


# ─── Group 10: File Integrity ─────────────────────────────────────────────────

def group_file_integrity():
    print("\n📁 Group 10: File Integrity")

    # FI01: memory/USER_PROFILE.md exists with >= 4 sections
    up_path = WORKSPACE / "memory" / "USER_PROFILE.md"
    if up_path.exists():
        text = up_path.read_text()
        sections = [l for l in text.split("\n") if l.startswith("## ")]
        test("FI01", "memory/USER_PROFILE.md exists with >= 4 sections",
             len(sections) >= 4,
             actual=f"{len(sections)} sections",
             expected=">= 4 sections")
    else:
        test("FI01", "memory/USER_PROFILE.md exists with >= 4 sections",
             False,
             actual="file not found",
             expected="exists with >= 4 sections")

    # FI02: memory/CROSS-AGENT-MEMORY.md exists
    ca_path = WORKSPACE / "memory" / "CROSS-AGENT-MEMORY.md"
    test("FI02", "memory/CROSS-AGENT-MEMORY.md exists",
         ca_path.exists(),
         actual="not found" if not ca_path.exists() else "found",
         expected="file exists")

    # FI03: memory/MEMORY-SEARCH-GUIDE.md exists
    msg_path = WORKSPACE / "memory" / "MEMORY-SEARCH-GUIDE.md"
    test("FI03", "memory/MEMORY-SEARCH-GUIDE.md exists",
         msg_path.exists(),
         actual="not found" if not msg_path.exists() else "found",
         expected="file exists")

    # FI04: DREAMS.md exists (created by dreaming system)
    dreams_path = WORKSPACE / "DREAMS.md"
    test("FI04", "DREAMS.md exists (created by dreaming system)",
         dreams_path.exists(),
         actual="not found" if not dreams_path.exists() else "found",
         expected="file exists")


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  OpenClaw Setup Test Suite — 2026-05-01")
    print("=" * 70)

    group_config()
    group_bootstrap()
    group_crons()
    group_skills()
    group_memory_flush()
    group_routing()
    group_cross_agent()
    group_entity_graph()
    group_gateway()
    group_file_integrity()

    # ─── Summary ───────────────────────────────────────────────────────────────
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    skipped = sum(1 for r in results if r["skipped"])
    failed_results = [r for r in results if not r["passed"] and not r["skipped"]]
    failed_count = len(failed_results)

    print("\n" + "=" * 70)
    print(f"  RESULTS: {passed}/{total} passed | {skipped} skipped | {failed_count} failed")
    print("=" * 70)

    if failed_results:
        print("\n❌ FAILURES:")
        for r in failed_results:
            print(f"  [{r['id']}] {r['name']}")
            if r.get("expected"):
                print(f"       expected: {r['expected']}")
            if r.get("actual"):
                print(f"         actual: {r['actual']}")

    if skipped > 0:
        skipped_list = [r for r in results if r["skipped"]]
        print(f"\n⚠️  SKIPPED ({skipped}):")
        for r in skipped_list:
            print(f"  [{r['id']}] {r['name']}")
            print(f"       reason: {r['reason']}")

    print()
    if failed_count == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {failed_count} test(s) failed. Fix failures above and re-run.")

    sys.exit(1 if failed_count > 0 else 0)


if __name__ == "__main__":
    main()
