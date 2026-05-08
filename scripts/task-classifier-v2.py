#!/usr/bin/env python3
"""
task-classifier-v2.py — Hybrid task classifier for OpenClaw routing.

Classifies a message into simple/medium/complex and maps to an appropriate model.
Uses a hybrid of length signals, code detection, keyword matching, and override rules.

Usage:
  echo "what time is it" | python3 task-classifier-v2.py
  python3 task-classifier-v2.py --message "Refactor the authentication module"
  python3 task-classifier-v2.py --test
"""

import sys
import json
import re
import argparse

# ─────────────────────────────────────────────
# Model mappings
# ─────────────────────────────────────────────
MODELS = {
    "simple":  "anthropic/claude-haiku-4-6",
    "medium":  "anthropic/claude-sonnet-4-6",
    "complex": "anthropic/claude-opus-4-7",
}

# ─────────────────────────────────────────────
# Keyword lists
# ─────────────────────────────────────────────
SIMPLE_KEYWORDS = [
    r"\bweather\b",
    r"\btime\b",
    r"\bdate\b",
    r"\bcalendar\b",
    r"\bschedule\b",
    r"\breminder\b",
    r"\bremind\b",
    r"\bstatus\b",
    r"\bcheck\b",
    r"\bheartbeat\b",
    r"\blist\b",
    r"\btoday\b",
    r"\btomorrow\b",
    r"\bthis week\b",
    r"\bnext week\b",
    r"\bcurrent\b",
    r"\blatest\b",
    r"\bwhat is\b",
    r"\bwhat's\b",
    r"\bwhat are\b",
    r"\bis there\b",
    r"\bhow many\b",
    r"\bhow much\b",
    r"\bping\b",
    r"\bhi\b",
    r"\bhello\b",
    r"\bsup\b",
    r"\bstatus check\b",
]

COMPLEX_KEYWORDS = [
    r"\brefactor\b",
    r"\barchitecture\b",
    r"\balgorithm\b",
    r"\bmigrat\b",          # migrate / migration
    r"\bbenchmark\b",
    r"\bdeploy\b",
    r"\baudit\b",
    r"\bredesign\b",
    r"\boverhaul\b",
    r"\bsecurity review\b",
    r"\bdata migration\b",
    r"\bscale\b",
    r"\binfrastructure\b",
    r"\bsystem design\b",
    r"\bdesign system\b",
    r"\bperformance analysis\b",
]

# Code indicators — trigger medium minimum
CODE_PATTERNS = [
    r"```",
    r"\bdef \b",
    r"\bclass \b",
    r"\bfunction\b",
    r"\bimport \b",
    r"\brequire\(",
    r"\bconst \b",
    r"\bvar \b",
    r"\blet \b",
    r"\breturn \b",
    r"=>",
]


# ─────────────────────────────────────────────
# Classification logic
# ─────────────────────────────────────────────
def count_words(text: str) -> int:
    return len(text.split())


def has_code(text: str) -> bool:
    for pat in CODE_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def matches_any(text: str, patterns: list) -> tuple[bool, str]:
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return True, m.group(0)
    return False, ""


def classify(message: str) -> dict:
    text = message.strip()
    word_count = count_words(text)
    line_count = len([l for l in text.splitlines() if l.strip()])
    code_detected = has_code(text)

    # ── Override signals (minimum tier upgrades) ──────────────────────────
    # Multi-line → medium minimum
    # Code blocks → medium minimum
    # >100 words → medium minimum
    min_medium = code_detected or line_count > 2 or word_count > 100

    # ── Complex keywords → complex regardless ────────────────────────────
    is_complex, complex_match = matches_any(text, COMPLEX_KEYWORDS)
    if is_complex:
        return {
            "tier": "complex",
            "model": MODELS["complex"],
            "reason": f"Complex keyword matched: '{complex_match}'",
            "confidence": 0.92,
            "word_count": word_count,
            "code_detected": code_detected,
        }

    # ── Length check: ≤10 words AND no code → check simple patterns ───────
    if word_count <= 10 and not code_detected:
        is_simple, simple_match = matches_any(text, SIMPLE_KEYWORDS)
        if is_simple:
            return {
                "tier": "simple",
                "model": MODELS["simple"],
                "reason": f"Short message with simple keyword: '{simple_match}'",
                "confidence": 0.88,
                "word_count": word_count,
                "code_detected": code_detected,
            }

    # ── If override signals require medium ────────────────────────────────
    if min_medium:
        reason_parts = []
        if code_detected:
            reason_parts.append("code detected")
        if line_count > 2:
            reason_parts.append(f"multi-line ({line_count} lines)")
        if word_count > 100:
            reason_parts.append(f"long message ({word_count} words)")
        return {
            "tier": "medium",
            "model": MODELS["medium"],
            "reason": "Override signals: " + ", ".join(reason_parts),
            "confidence": 0.85,
            "word_count": word_count,
            "code_detected": code_detected,
        }

    # ── Simple keyword present even in longer message ─────────────────────
    is_simple, simple_match = matches_any(text, SIMPLE_KEYWORDS)
    if is_simple and word_count <= 50:
        return {
            "tier": "simple",
            "model": MODELS["simple"],
            "reason": f"Simple keyword matched in short-ish message: '{simple_match}'",
            "confidence": 0.78,
            "word_count": word_count,
            "code_detected": code_detected,
        }

    # ── Default: medium ───────────────────────────────────────────────────
    return {
        "tier": "medium",
        "model": MODELS["medium"],
        "reason": "Default classification — no strong simple or complex signals",
        "confidence": 0.75,
        "word_count": word_count,
        "code_detected": code_detected,
    }


# ─────────────────────────────────────────────
# Test suite
# ─────────────────────────────────────────────
TEST_CASES = [
    ("What time is it?",                                     "simple"),
    ("weather today",                                        "simple"),
    ("hi",                                                   "simple"),
    ("heartbeat check",                                      "simple"),
    ("Refactor the authentication module to use JWT tokens", "complex"),
    ("Audit the security configuration of the API gateway",  "complex"),
    ("Design a new system architecture for the microservices platform", "complex"),
    ("Write an email to the team about the sprint review",   "medium"),
    ("Explain how OAuth2 works",                             "medium"),
    ("Can you help me debug this:\n```python\ndef foo(): pass\n```", "medium"),
    # long message
    ("I need you to analyze the following situation carefully. We have a production system "
     "that is experiencing intermittent failures and I need you to review the logs and "
     "suggest what might be causing the issue based on the patterns you observe.",         "medium"),
]


def run_tests():
    print(f"{'Message':<65} {'Expected':<10} {'Got':<10} {'Conf':<6} {'Pass'}")
    print("─" * 110)
    passed = 0
    for msg, expected in TEST_CASES:
        preview = (msg[:60] + "…") if len(msg) > 60 else msg
        result = classify(msg)
        got = result["tier"]
        ok = "✅" if got == expected else "❌"
        if got == expected:
            passed += 1
        print(f"{preview:<65} {expected:<10} {got:<10} {result['confidence']:<6.2f} {ok}")
    print(f"\n{passed}/{len(TEST_CASES)} passed")


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Hybrid task classifier for OpenClaw routing")
    parser.add_argument("--message", "-m", type=str, help="Message to classify")
    parser.add_argument("--test", action="store_true", help="Run test suite")
    args = parser.parse_args()

    if args.test:
        run_tests()
        return

    if args.message:
        message = args.message
    elif not sys.stdin.isatty():
        message = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)

    result = classify(message)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
