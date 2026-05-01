#!/usr/bin/env python3
"""
dreams-consolidation.py — Nightly memory consolidation (DREAMS system).

Reads memory/YYYY-MM-DD*.md files from the last 7 days, extracts key facts,
decisions, and lessons not yet in MEMORY.md, and appends them under a
"## Recent Additions (auto)" section.

Also writes/updates DREAMS.md with processing metadata.

Usage:
    python3 dreams-consolidation.py           # Process last 7 days
    python3 dreams-consolidation.py --dry-run # Show what would be added
    python3 dreams-consolidation.py --days 14 # Look back 14 days

Requirements:
    - ANTHROPIC_API_KEY env var OR key in macOS Keychain (label: ANTHROPIC_API_KEY)
    - anthropic Python SDK (in workspace venv)
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_MD = WORKSPACE / "MEMORY.md"
DREAMS_MD = WORKSPACE / "DREAMS.md"
MEMORY_DIR = WORKSPACE / "memory"

HAIKU_MODEL = "claude-haiku-4-5"  # fast, cheap
SECTION_HEADER = "## Recent Additions (auto)"
MAX_FILE_SIZE = 50_000  # bytes, skip huge files
LOOKBACK_DAYS = 7


def get_api_key() -> str | None:
    """Get Anthropic API key from env or macOS Keychain."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "ANTHROPIC_API_KEY", "-w"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def find_recent_files(days: int) -> list[Path]:
    """Find memory/*.md files modified in the last N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    files = []
    if not MEMORY_DIR.exists():
        return files
    for path in sorted(MEMORY_DIR.glob("*.md")):
        if path.stat().st_size < 100:
            continue  # skip truly empty files
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        if mtime >= cutoff:
            files.append(path)
    return files


def read_memory_md() -> str:
    """Read current MEMORY.md content."""
    if MEMORY_MD.exists():
        return MEMORY_MD.read_text(encoding="utf-8")
    return ""


def read_file(path: Path) -> str:
    """Read a file safely, truncating if too large."""
    try:
        content = path.read_text(encoding="utf-8")
        if len(content.encode()) > MAX_FILE_SIZE:
            content = content[:MAX_FILE_SIZE] + "\n[... truncated ...]"
        return content
    except (OSError, UnicodeDecodeError):
        return ""


def extract_additions(daily_contents: dict[str, str], existing_memory: str, api_key: str, dry_run: bool) -> str:
    """
    Call Haiku to extract key facts from daily logs not yet in MEMORY.md.
    Returns the text to append (may be empty if nothing new).
    """
    import anthropic

    if not daily_contents:
        return ""

    # Build input for LLM
    logs_text = ""
    for filename, content in daily_contents.items():
        logs_text += f"\n\n=== {filename} ===\n{content}"

    # Truncate existing MEMORY.md to ~4000 chars for context
    memory_excerpt = existing_memory[-4000:] if len(existing_memory) > 4000 else existing_memory

    prompt = f"""You are Momotaro, an AI assistant's memory consolidation system.

Below are recent daily session logs followed by the existing long-term memory file.
Extract 3-8 bullet points of KEY information from the logs that is NOT already captured in MEMORY.md.

Focus on:
- Technical decisions made (tools chosen, configs changed, approaches decided)
- Important facts discovered (bugs, fixes, system state)
- Lessons learned
- Project status changes
- New tool setups or configurations

Skip:
- Routine tasks already documented in MEMORY.md
- Redundant or trivial details
- Session housekeeping (context flushes, heartbeats, etc.)

Format each bullet as:
- [DATE if known] Fact/decision/lesson here

If there is truly nothing new worth adding, respond with exactly: NO_NEW_ADDITIONS

=== RECENT DAILY LOGS ===
{logs_text}

=== EXISTING MEMORY.md (last 4000 chars) ===
{memory_excerpt}

=== YOUR RESPONSE (bullet points only, or NO_NEW_ADDITIONS) ==="""

    if dry_run:
        print("\n[DRY RUN] Would call Claude Haiku with prompt:")
        print(f"  Daily files: {list(daily_contents.keys())}")
        print(f"  Total log content: {sum(len(c) for c in daily_contents.values())} chars")
        return ""

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=HAIKU_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text.strip()

    if text == "NO_NEW_ADDITIONS" or not text:
        return ""
    return text


def update_memory_md(new_content: str) -> None:
    """Append new content under SECTION_HEADER in MEMORY.md."""
    existing = read_memory_md()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    new_section = f"\n\n{SECTION_HEADER} — {now_str}\n\n{new_content}\n"

    # Remove old "Recent Additions (auto)" section if exists, to avoid growing forever
    if SECTION_HEADER in existing:
        # Replace old section
        pattern = re.compile(
            r'\n\n' + re.escape(SECTION_HEADER) + r'.*?(?=\n\n##|\Z)',
            re.DOTALL
        )
        existing = pattern.sub("", existing)

    updated = existing.rstrip() + new_section
    MEMORY_MD.write_text(updated, encoding="utf-8")


def update_dreams_log(files_processed: list[str], added: bool, dry_run: bool) -> None:
    """Write/update DREAMS.md with processing metadata."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    mode = "DRY RUN" if dry_run else "LIVE"

    entry = f"""## DREAMS Run — {now_str} [{mode}]

- Files processed: {len(files_processed)}
- Files: {', '.join(files_processed) if files_processed else 'none'}
- New content added to MEMORY.md: {'yes' if added else 'no (nothing new or dry run)'}

"""

    if DREAMS_MD.exists():
        existing = DREAMS_MD.read_text(encoding="utf-8")
        # Keep last 10 entries (rough cap)
        lines = existing.split("\n")
        if len(lines) > 200:
            # Trim to last 150 lines
            existing = "\n".join(lines[-150:])
        DREAMS_MD.write_text(entry + existing, encoding="utf-8")
    else:
        header = "# DREAMS.md — Nightly Memory Consolidation Log\n\n"
        DREAMS_MD.write_text(header + entry, encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description="DREAMS nightly memory consolidation")
    p.add_argument("--dry-run", action="store_true", help="Show what would be added without writing")
    p.add_argument("--days", type=int, default=LOOKBACK_DAYS, help=f"Days to look back (default {LOOKBACK_DAYS})")
    args = p.parse_args()

    print(f"🌙 DREAMS consolidation — lookback: {args.days} days {'[DRY RUN]' if args.dry_run else '[LIVE]'}")

    # Get API key
    api_key = get_api_key()
    if not api_key:
        print("❌ No ANTHROPIC_API_KEY found in env or Keychain. Cannot call Haiku.")
        sys.exit(1)

    # Find recent files
    recent_files = find_recent_files(args.days)
    if not recent_files:
        print(f"ℹ️  No memory files found in the last {args.days} days.")
        update_dreams_log([], False, args.dry_run)
        return

    print(f"📁 Found {len(recent_files)} recent file(s):")
    for f in recent_files:
        size = f.stat().st_size
        print(f"   {size:6d}B  {f.name}")

    # Read files
    daily_contents = {}
    for path in recent_files:
        content = read_file(path)
        if content.strip():
            daily_contents[path.name] = content

    # Read existing MEMORY.md
    existing_memory = read_memory_md()

    # Extract additions
    print(f"\n🤖 Calling Claude Haiku to extract key facts...")
    new_content = extract_additions(daily_contents, existing_memory, api_key, args.dry_run)

    if args.dry_run:
        print("\n✅ Dry run complete. To apply, run without --dry-run.")
        update_dreams_log([f.name for f in recent_files], False, dry_run=True)
        return

    if not new_content:
        print("ℹ️  No new content worth adding to MEMORY.md (Haiku found nothing new).")
        update_dreams_log([f.name for f in recent_files], False, dry_run=False)
        return

    print(f"\n📝 New content to add to MEMORY.md:")
    print("-" * 60)
    print(new_content)
    print("-" * 60)

    # Append to MEMORY.md
    update_memory_md(new_content)
    print(f"\n✅ Appended to MEMORY.md under '{SECTION_HEADER}'")

    # Update DREAMS.md
    update_dreams_log([f.name for f in recent_files], True, dry_run=False)
    print(f"📋 Updated DREAMS.md log")


if __name__ == "__main__":
    main()
