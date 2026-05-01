#!/usr/bin/env python3
"""
memory-compress-daily.py — Summarize and compress old daily memory files.

Finds all memory/YYYY-MM-DD*.md files older than 7 days AND larger than 5KB.
For each file, calls Anthropic Haiku to summarize the content, then writes
a compressed version back to the same file with a header noting the compression.
Keeps a .md.orig backup of the original.

Runs in --dry-run mode by default. Use --apply to actually compress files.

Usage:
    python3 memory-compress-daily.py              # dry-run (default)
    python3 memory-compress-daily.py --dry-run    # explicit dry-run
    python3 memory-compress-daily.py --apply      # compress files
    python3 memory-compress-daily.py --apply --verbose
    python3 memory-compress-daily.py --min-age 14  # only files older than 14 days
    python3 memory-compress-daily.py --min-size 8192  # only files larger than 8KB

Environment:
    ANTHROPIC_API_KEY — required for compression (uses claude-haiku-4-5-20251001)

Notes:
    - Files already compressed (header: "# [COMPRESSED") are skipped.
    - .orig backups are kept; delete manually when satisfied.
    - Estimated token savings shown in dry-run mode.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ── Config ──────────────────────────────────────────────────────────────────

MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory"
MIN_AGE_DAYS = 7
MIN_SIZE_BYTES = 5 * 1024  # 5 KB
HAIKU_MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS_IN = 4000    # truncate input to avoid Haiku context limits
MAX_TOKENS_OUT = 1200   # max summary length

COMPRESSION_HEADER = "# [COMPRESSED {date}] Original: {orig_kb}KB → {new_kb}KB\n\n"

SUMMARY_PROMPT = """\
Summarize the key facts, decisions, and learnings from this session log.
Be concise. Preserve any specific values (URLs, commands, names, numbers, config values).
Output clean markdown with headers as appropriate.
Skip boilerplate, pleasantries, and repeated content.
Focus: what was done, what was decided, what was discovered, what to remember."""

DAILY_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}")


def _get_api_key() -> str:
    """Get ANTHROPIC_API_KEY from env or briefing.env."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    env_file = Path.home() / ".openclaw" / "workspace" / "config" / "briefing.env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError(
        "ANTHROPIC_API_KEY not set. Add to env or config/briefing.env."
    )


def _file_date(path: Path) -> Optional[datetime]:
    """Extract date from filename like 2026-04-24.md or 2026-04-24-1234.md."""
    m = DAILY_PATTERN.match(path.name)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(0), "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _age_days(path: Path) -> float:
    """Return age in days based on filename date."""
    file_date = _file_date(path)
    if not file_date:
        return 0.0
    delta = datetime.now(timezone.utc) - file_date
    return delta.total_seconds() / 86400


def _is_already_compressed(path: Path) -> bool:
    """Check if file already has a compression header."""
    try:
        first_line = path.read_text(encoding="utf-8", errors="replace")[:80]
        return first_line.startswith("# [COMPRESSED")
    except Exception:
        return False


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return len(text) // 4


def find_candidates(
    memory_dir: Path = MEMORY_DIR,
    min_age_days: int = MIN_AGE_DAYS,
    min_size_bytes: int = MIN_SIZE_BYTES,
) -> List[Dict]:
    """
    Find daily memory files that qualify for compression.

    Returns list of dicts: {path, age_days, size_bytes, tokens_est}.
    """
    candidates = []
    for f in sorted(memory_dir.glob("*.md")):
        if not DAILY_PATTERN.match(f.name):
            continue
        age = _age_days(f)
        if age <= min_age_days:
            continue
        size = f.stat().st_size
        if size <= min_size_bytes:
            continue
        if _is_already_compressed(f):
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        candidates.append({
            "path": f,
            "age_days": age,
            "size_bytes": size,
            "tokens_est": _estimate_tokens(content),
            "content": content,
        })
    return candidates


def _summarize_with_haiku(content: str, api_key: str) -> str:
    """Call Anthropic Haiku to summarize session log content."""
    try:
        import anthropic
    except ImportError:
        raise RuntimeError("anthropic package not installed. Run: pip install anthropic")

    # Truncate if too long
    if len(content) > MAX_TOKENS_IN * 4:
        content = content[:MAX_TOKENS_IN * 4] + "\n\n[... content truncated for compression ...]"

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model=HAIKU_MODEL,
        max_tokens=MAX_TOKENS_OUT,
        system=SUMMARY_PROMPT,
        messages=[
            {"role": "user", "content": f"Session log to summarize:\n\n{content}"}
        ],
    )
    return msg.content[0].text.strip()


def compress_file(
    candidate: Dict,
    api_key: str,
    dry_run: bool = True,
    verbose: bool = False,
) -> Dict:
    """
    Compress a single file. Returns result dict with stats.
    In dry-run mode, estimates savings without modifying any files.
    """
    path: Path = candidate["path"]
    content: str = candidate["content"]
    orig_size = candidate["size_bytes"]
    date_str = _file_date(path).strftime("%Y-%m-%d") if _file_date(path) else "unknown"

    result = {
        "path": str(path),
        "name": path.name,
        "orig_size_bytes": orig_size,
        "new_size_bytes": None,
        "compression_ratio": None,
        "dry_run": dry_run,
        "error": None,
    }

    if verbose:
        print(f"  {'[DRY]' if dry_run else '[APPLY]'} {path.name} ({orig_size//1024}KB, {candidate['age_days']:.0f}d old)")

    if dry_run:
        # Estimate: summaries are typically 10-20% of original
        est_summary_size = max(500, orig_size // 6)
        header_size = len(COMPRESSION_HEADER.format(date=date_str, orig_kb=orig_size//1024, new_kb=est_summary_size//1024))
        est_total = header_size + est_summary_size
        result["new_size_bytes"] = est_total
        result["compression_ratio"] = round(est_total / orig_size, 2)
        if verbose:
            print(f"    Est: {orig_size//1024}KB → {est_total//1024}KB ({result['compression_ratio']:.0%})")
        return result

    # Apply: backup + summarize + write
    backup_path = path.with_suffix(".md.orig")
    try:
        # 1. Write backup
        backup_path.write_text(content, encoding="utf-8")

        # 2. Summarize
        summary = _summarize_with_haiku(content, api_key)

        # 3. Build compressed content
        orig_kb = orig_size // 1024
        new_kb = len(summary) // 1024
        header = COMPRESSION_HEADER.format(date=date_str, orig_kb=orig_kb, new_kb=max(1, new_kb))
        compressed = header + summary

        # 4. Write back
        path.write_text(compressed, encoding="utf-8")

        new_size = len(compressed.encode("utf-8"))
        result["new_size_bytes"] = new_size
        result["compression_ratio"] = round(new_size / orig_size, 2)

        print(f"    ✓ {path.name}: {orig_size//1024}KB → {new_size//1024}KB "
              f"(backup: {backup_path.name})")

    except Exception as e:
        result["error"] = str(e)
        # Restore from backup if we made one
        if backup_path.exists() and not path.exists():
            backup_path.rename(path)
        print(f"    ✗ {path.name}: {e}", file=sys.stderr)

    return result


def run_compression(
    memory_dir: Path = MEMORY_DIR,
    min_age_days: int = MIN_AGE_DAYS,
    min_size_bytes: int = MIN_SIZE_BYTES,
    dry_run: bool = True,
    verbose: bool = False,
) -> Dict:
    """Main compression routine. Returns summary stats."""
    candidates = find_candidates(memory_dir, min_age_days, min_size_bytes)

    total_orig = sum(c["size_bytes"] for c in candidates)
    total_tokens = sum(c["tokens_est"] for c in candidates)

    print(f"[memory-compress] Found {len(candidates)} file(s) eligible for compression")
    if candidates:
        print(f"  Total size: {total_orig // 1024}KB | Est. tokens: {total_tokens:,}")
        print(f"  Threshold: >{min_age_days} days old AND >{min_size_bytes//1024}KB")
        print()

    if not candidates:
        print("[memory-compress] Nothing to compress.")
        return {"candidates": 0, "total_orig_kb": 0, "total_new_kb": 0, "errors": 0}

    api_key = None
    if not dry_run:
        try:
            api_key = _get_api_key()
        except RuntimeError as e:
            print(f"[memory-compress] ERROR: {e}", file=sys.stderr)
            sys.exit(1)

    results = []
    for c in candidates:
        r = compress_file(c, api_key=api_key or "", dry_run=dry_run, verbose=verbose)
        results.append(r)
        if not dry_run:
            time.sleep(0.5)  # rate limit Haiku calls

    ok = [r for r in results if not r.get("error")]
    errors = [r for r in results if r.get("error")]

    total_new = sum(r.get("new_size_bytes") or 0 for r in ok)
    savings_kb = (total_orig - total_new) // 1024

    print(f"\n[memory-compress] {'DRY RUN ' if dry_run else ''}Summary:")
    print(f"  Files processed: {len(ok)}/{len(candidates)}")
    print(f"  Original size:   {total_orig // 1024}KB")
    print(f"  New size (est):  {total_new // 1024}KB")
    print(f"  Savings (est):   {savings_kb}KB (~{round(total_new/total_orig*100) if total_orig else 0}% of original)")
    if errors:
        print(f"  Errors:          {len(errors)}")
    if dry_run:
        print("\n  Use --apply to actually compress files.")
        print("  Each file will be backed up as .md.orig before compression.")

    return {
        "candidates": len(candidates),
        "compressed": len(ok),
        "errors": len(errors),
        "total_orig_kb": total_orig // 1024,
        "total_new_kb": total_new // 1024,
        "savings_kb": savings_kb,
        "dry_run": dry_run,
        "files": [{"name": r["name"], "orig_kb": r["orig_size_bytes"]//1024,
                   "new_kb": (r["new_size_bytes"] or 0)//1024,
                   "error": r.get("error")} for r in results],
    }


def main():
    ap = argparse.ArgumentParser(
        description="Compress old daily memory files using Haiku summarization"
    )
    ap.add_argument("--dry-run", action="store_true", default=False,
                    help="Show what would be compressed (no writes)")
    ap.add_argument("--apply", action="store_true",
                    help="Actually compress files (writes .md.orig backup + new summary)")
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="Show per-file details")
    ap.add_argument("--min-age", type=int, default=MIN_AGE_DAYS,
                    help=f"Minimum file age in days (default: {MIN_AGE_DAYS})")
    ap.add_argument("--min-size", type=int, default=MIN_SIZE_BYTES,
                    help=f"Minimum file size in bytes (default: {MIN_SIZE_BYTES} = 5KB)")
    ap.add_argument("--memory-dir", default=str(MEMORY_DIR),
                    help=f"Memory directory (default: {MEMORY_DIR})")
    args = ap.parse_args()

    dry_run = not args.apply
    if dry_run:
        print("[memory-compress] Mode: DRY RUN (use --apply to actually compress)")
    else:
        print("[memory-compress] Mode: APPLY (will compress and backup files)")

    stats = run_compression(
        memory_dir=Path(args.memory_dir),
        min_age_days=args.min_age,
        min_size_bytes=args.min_size,
        dry_run=dry_run,
        verbose=args.verbose,
    )

    import json
    print("\n[stats]", json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
