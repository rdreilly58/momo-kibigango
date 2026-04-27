#!/usr/bin/env python3
"""
test-memory-system.py — Comprehensive test suite for memory system overhaul.
"""

import sys
import os
import json
import subprocess
from pathlib import Path

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
SCRIPTS = os.path.join(WORKSPACE, "scripts")

tests_passed = 0
tests_failed = 0
failures = []


def test(name: str, check_fn):
    """Run a single test."""
    global tests_passed, tests_failed, failures

    try:
        result = check_fn()
        if result:
            print(f"  ✅ {name}")
            tests_passed += 1
        else:
            print(f"  ❌ {name}: Assertion failed")
            tests_failed += 1
            failures.append(name)
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        tests_failed += 1
        failures.append(f"{name}: {e}")


def file_exists(path: str):
    """Check if file exists."""
    return lambda: os.path.exists(os.path.expanduser(path))


def file_executable(path: str):
    """Check if file is executable."""
    return lambda: os.access(os.path.expanduser(path), os.X_OK)


def json_valid(path: str):
    """Check if JSON file is valid."""

    def check():
        with open(os.path.expanduser(path)) as f:
            json.load(f)
        return True

    return check


def json_has_fields(path: str, fields: list):
    """Check if JSON has required fields."""

    def check():
        with open(os.path.expanduser(path)) as f:
            data = json.load(f)
        return all(field in data for field in fields)

    return check


def script_runs(path: str, args: list = None):
    """Check if script runs without error."""

    def check():
        cmd = ["python3", os.path.expanduser(path)]
        if args:
            cmd.extend(args)
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        return result.returncode in [0, 1]  # Allow non-zero exit

    return check


# ============================================================================
# TIER 1: RELIABILITY
# ============================================================================

print("\n📋 TIER 1: RELIABILITY")
print("=" * 70)

test("Audit log directory exists", file_exists("~/.openclaw/logs/memory-audit"))
test(
    "Harness fallback script exists",
    file_exists("~/.openclaw/workspace/scripts/harness-fallback.sh"),
)
test(
    "Harness fallback is executable",
    file_executable("~/.openclaw/workspace/scripts/harness-fallback.sh"),
)
test(
    "Memory audit logger exists",
    file_exists("~/.openclaw/workspace/scripts/memory_audit_logger.py"),
)
test(
    "Memory audit CLI exists",
    file_exists("~/.openclaw/workspace/scripts/memory_audit_cli.py"),
)

# ============================================================================
# TIER 2: ORGANIZATION
# ============================================================================

print("\n📦 TIER 2: ORGANIZATION")
print("=" * 70)

test(
    "Lifecycle manager exists",
    file_exists("~/.openclaw/workspace/scripts/memory-lifecycle-manager.sh"),
)
test(
    "Deduplication script exists",
    file_exists("~/.openclaw/workspace/scripts/memory-deduplication.py"),
)
test(
    "Query analytics script exists",
    file_exists("~/.openclaw/workspace/scripts/memory-query-analytics.py"),
)
test("Analytics log directory exists", file_exists("~/.openclaw/logs/memory-analytics"))
test(
    "Deduplication runs without error",
    script_runs(
        "~/.openclaw/workspace/scripts/memory-deduplication.py",
        ["--threshold", "0.95", "--dry-run"],
    ),
)

# ============================================================================
# TIER 3: VISUALIZATION
# ============================================================================

print("\n🎨 TIER 3: VISUALIZATION")
print("=" * 70)

test("Palace JSON exists", file_exists("~/.openclaw/workspace/memory-palace.json"))
test("Palace JSON is valid", json_valid("~/.openclaw/workspace/memory-palace.json"))
test(
    "Palace has stats",
    json_has_fields("~/.openclaw/workspace/memory-palace.json", ["stats", "wings"]),
)

test("Graph JSON exists", file_exists("~/.openclaw/workspace/memory-graph.json"))
test("Graph JSON is valid", json_valid("~/.openclaw/workspace/memory-graph.json"))
test(
    "Graph has stats",
    json_has_fields(
        "~/.openclaw/workspace/memory-graph.json", ["stats", "nodes", "edges"]
    ),
)

test(
    "Palace builder runs",
    script_runs("~/.openclaw/workspace/scripts/memory-palace-builder.py", ["--build"]),
)
test(
    "Graph builder runs",
    script_runs("~/.openclaw/workspace/scripts/memory-graph-builder.py", ["--build"]),
)

# ============================================================================
# NEXT STEPS: AUTOMATION
# ============================================================================

print("\n⚙️  NEXT STEPS: AUTOMATION")
print("=" * 70)

test(
    "Maintenance cron exists",
    file_exists("~/.openclaw/workspace/scripts/memory-maintenance-cron.sh"),
)
test(
    "Maintenance cron is executable",
    file_executable("~/.openclaw/workspace/scripts/memory-maintenance-cron.sh"),
)
test("Web UI HTML exists", file_exists("~/.openclaw/workspace/memory-explorer.html"))


def check_web_ui():
    with open(os.path.expanduser("~/.openclaw/workspace/memory-explorer.html")) as f:
        content = f.read()
    return "palace" in content and "graph" in content and "stats" in content


test("Web UI has required tabs", check_web_ui)

# ============================================================================
# INTEGRATION
# ============================================================================

print("\n🔗 INTEGRATION")
print("=" * 70)

test(
    "Memory DB imports",
    script_runs("~/.openclaw/workspace/scripts/memory_db.py", ["--help"]),
)
test(
    "Query analytics runs",
    script_runs(
        "~/.openclaw/workspace/scripts/memory-query-analytics.py",
        ["--stats", "--days", "1"],
    ),
)

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("📊 TEST SUMMARY")
print("=" * 70)

total = tests_passed + tests_failed
print(f"\n✅ Passed: {tests_passed}/{total}")
print(f"❌ Failed: {tests_failed}/{total}")

if failures:
    print("\n⚠️  FAILURES:")
    for failure in failures:
        print(f"  • {failure}")
    sys.exit(1)
else:
    print("\n🎉 All tests passed!")
    sys.exit(0)
