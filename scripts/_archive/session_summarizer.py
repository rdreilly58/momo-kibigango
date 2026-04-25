#!/usr/bin/env python3
"""
session_summarizer.py — Two-tier session memory core engine

Accepts conversation text, calls Claude Haiku to compress it,
then writes structured summaries to:
  1. memory/YYYY-MM-DD.md (daily notes)
  2. SESSION_CONTEXT.md (prepend, keep last 5, max 150 lines)
  3. ai-memory.db (via MemoryDB)

Exit codes:
  0 = success
  1 = skipped (input too short)
  2 = skipped (duplicate)
  3 = error

Usage:
  python3 session_summarizer.py --text "conversation text"
  python3 session_summarizer.py --file /path/to/transcript.txt
  python3 session_summarizer.py --dry-run --text "..."
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_WORKSPACE = Path.home() / ".openclaw" / "workspace"
DEFAULT_MIN_CHARS = 200
DEFAULT_DEDUP_THRESHOLD = 0.60
HAIKU_MODEL = "claude-haiku-4-5-20251001"
MAX_CONTEXT_LINES = 150
MAX_CONTEXT_SESSIONS = 5
LOG_FILE = Path.home() / ".openclaw" / "logs" / "session-summarizer.log"

SYSTEM_PROMPT = """You are a session memory compressor. Given a conversation transcript, extract a structured summary in valid JSON only. No commentary, no markdown fences — raw JSON.

Schema:
{
  "one_liner": "1-sentence summary of what happened (max 120 chars)",
  "topics": ["list", "of", "topics", "discussed"],
  "completed": ["tasks or problems resolved"],
  "learned": ["facts, decisions, or insights discovered"],
  "issues": ["problems hit, errors, things that didn't work"],
  "next_steps": ["open items or follow-ups if any"]
}

Rules:
- Be factual and specific (include file names, script names, error messages)
- completed/learned/issues/next_steps: 0-5 items each, bullet-point style
- If nothing significant happened, return {"one_liner": "Routine session, nothing notable", "topics": [], "completed": [], "learned": [], "issues": [], "next_steps": []}
- Never hallucinate — only include what is explicitly in the transcript

Examples of good output:
{"one_liner": "Fixed session hook regression and added 25-test suite", "topics": ["session-memory", "testing", "bash"], "completed": ["fix(memory): agent-written summaries replace broken hook", "test suite for daily-session-reset.sh all passing"], "learned": ["OpenClaw v2026.4.15 hook writes only 171 bytes, not transcripts"], "issues": [], "next_steps": ["two-tier memory system"]}"""


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def _setup_logging() -> logging.Logger:
    logger = logging.getLogger("session_summarizer")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        # File handler
        try:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            fh = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
            fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
            logger.addHandler(fh)
        except Exception:
            pass
        # Stderr handler
        sh = logging.StreamHandler(sys.stderr)
        sh.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        logger.addHandler(sh)
    return logger


log = _setup_logging()


# ---------------------------------------------------------------------------
# Text preprocessing
# ---------------------------------------------------------------------------

# Patterns to strip from transcripts
_SYSTEM_RE = re.compile(
    r"(?m)^(?:<\|system\|>|<system>|SYSTEM:|Human:|Assistant:|<\|user\|>|<\|assistant\|>).*$"
)
_METADATA_RE = re.compile(
    r"(?m)^\s*(?:session_id|hook_event_name|stop_hook_active|transcript):\s*.*$"
)


def strip_boilerplate(text: str) -> str:
    """Remove system messages and metadata lines."""
    text = _SYSTEM_RE.sub("", text)
    text = _METADATA_RE.sub("", text)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Jaccard deduplication
# ---------------------------------------------------------------------------

_STOP_WORDS = frozenset(
    "the a an and or but in on at to for of with is was are were be been "
    "have has had do does did will would could should may might shall can "
    "it its it's that this these those i you he she we they them us our "
    "your their what how when where why which who whom".split()
)


def _significant_words(text: str) -> frozenset[str]:
    words = re.findall(r"[a-z0-9_\-/]{3,}", text.lower())
    return frozenset(w for w in words if w not in _STOP_WORDS)


def jaccard_similarity(a: str, b: str) -> float:
    sa, sb = _significant_words(a), _significant_words(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    intersection = len(sa & sb)
    union = len(sa | sb)
    return intersection / union if union > 0 else 0.0


# ---------------------------------------------------------------------------
# Daily notes helpers
# ---------------------------------------------------------------------------

DAILY_SECTIONS = {
    "tasks": "## Tasks",
    "learnings": "## Learnings",
    "issues": "## Issues Encountered",
    "summary": "## End of Day Summary",
}


def _ensure_daily_sections(content: str) -> str:
    """Make sure all four sections exist in the daily notes content."""
    for header in DAILY_SECTIONS.values():
        if header not in content:
            content = content.rstrip() + f"\n\n{header}\n"
    return content


def _append_to_section(content: str, section_header: str, items: list[str], timestamp: str) -> str:
    """Append timestamped items under a section header."""
    if not items:
        return content
    new_lines = "\n".join(f"- [{timestamp}] {item}" for item in items)
    # Insert after the section header line
    pattern = re.compile(rf"(^{re.escape(section_header)}\s*$)", re.MULTILINE)
    replacement = rf"\1\n{new_lines}"
    updated = pattern.sub(replacement, content, count=1)
    return updated


def write_daily_notes(summary: dict, workspace: Path, timestamp: str, dry_run: bool = False) -> None:
    """Append summary to today's daily notes file."""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_path = workspace / "memory" / f"{today}.md"

    if not dry_run:
        (workspace / "memory").mkdir(parents=True, exist_ok=True)

    # Read existing content or create skeleton
    if daily_path.exists():
        content = daily_path.read_text(encoding="utf-8")
    else:
        content = f"# Daily Notes — {today}\n"

    content = _ensure_daily_sections(content)

    # Append completed items under Tasks
    completed = summary.get("completed", [])
    content = _append_to_section(content, DAILY_SECTIONS["tasks"], completed, timestamp)

    # Append learned items under Learnings
    learned = summary.get("learned", [])
    content = _append_to_section(content, DAILY_SECTIONS["learnings"], learned, timestamp)

    # Append issues
    issues = summary.get("issues", [])
    content = _append_to_section(content, DAILY_SECTIONS["issues"], issues, timestamp)

    # Append one_liner under End of Day Summary
    one_liner = summary.get("one_liner", "")
    if one_liner:
        content = _append_to_section(content, DAILY_SECTIONS["summary"], [one_liner], timestamp)

    if dry_run:
        log.info("[dry-run] Would write daily notes to %s", daily_path)
        return

    _atomic_write(daily_path, content)
    log.info("Wrote daily notes to %s", daily_path)


# ---------------------------------------------------------------------------
# SESSION_CONTEXT.md helpers
# ---------------------------------------------------------------------------

SESSION_CONTEXT_HEADER = """\
# SESSION_CONTEXT.md

**Auto-generated — do not edit manually**

---

## Recent Sessions (last 5)

"""

SESSION_CONTEXT_FOOTER = """
---

## System State (auto-refresh every 2h)
- Git: see workspace git log
- Blocked: none known
"""


def _build_session_block(summary: dict, dt: datetime) -> str:
    """Format one session entry block."""
    ts = dt.strftime("%Y-%m-%d %H:%M")
    one_liner = summary.get("one_liner", "")
    completed = summary.get("completed", [])
    learned = summary.get("learned", [])
    issues = summary.get("issues", [])
    next_steps = summary.get("next_steps", [])

    lines = [f"### {ts}"]
    lines.append(f"**Summary:** {one_liner}")
    if completed:
        lines.append("**Completed:** " + "; ".join(completed))
    if learned:
        lines.append("**Learned:** " + "; ".join(learned))
    if issues:
        lines.append("**Issues:** " + "; ".join(issues))
    if next_steps:
        lines.append("**Next:** " + "; ".join(next_steps))
    lines.append("")
    return "\n".join(lines)


def _parse_session_blocks(text: str) -> list[str]:
    """Extract individual session blocks (### heading ... next ### heading)."""
    # Split on ### lines
    parts = re.split(r"(?=^### \d{4}-\d{2}-\d{2})", text, flags=re.MULTILINE)
    return [p for p in parts if p.strip().startswith("### ")]


def write_session_context(summary: dict, context_path: Path, dry_run: bool = False) -> None:
    """Prepend new session summary to SESSION_CONTEXT.md, keeping last 5."""
    dt = datetime.now()
    new_block = _build_session_block(summary, dt)

    if context_path.exists():
        existing = context_path.read_text(encoding="utf-8")
    else:
        existing = ""

    # Extract existing session blocks
    old_blocks = _parse_session_blocks(existing)

    # Keep last (MAX_CONTEXT_SESSIONS - 1) old blocks
    kept_blocks = old_blocks[: MAX_CONTEXT_SESSIONS - 1]

    # Build new content
    sessions_section = new_block + "".join(kept_blocks)

    new_content = SESSION_CONTEXT_HEADER + sessions_section + SESSION_CONTEXT_FOOTER

    # Enforce line limit
    lines = new_content.splitlines(keepends=True)
    if len(lines) > MAX_CONTEXT_LINES:
        new_content = "".join(lines[:MAX_CONTEXT_LINES])

    if dry_run:
        log.info("[dry-run] Would write SESSION_CONTEXT.md (%d lines)", len(new_content.splitlines()))
        return

    _atomic_write(context_path, new_content)
    log.info("Updated SESSION_CONTEXT.md")


# ---------------------------------------------------------------------------
# Database write
# ---------------------------------------------------------------------------

def write_to_db(summary: dict, workspace: Path) -> str:
    """Write summary to ai-memory.db via MemoryDB. Returns the memory ID."""
    scripts_dir = workspace / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    from memory_db import MemoryDB  # type: ignore

    db = MemoryDB(workspace / "ai-memory.db")
    title = summary.get("one_liner", "Session summary")[:120]
    content_parts = []
    for key in ("topics", "completed", "learned", "issues", "next_steps"):
        items = summary.get(key, [])
        if items:
            content_parts.append(f"{key}: " + "; ".join(items))
    content = "\n".join(content_parts) if content_parts else title

    tags = ["session", "summary", "auto"]
    mem_id = db.add(
        title,
        content,
        tier="short",
        namespace="workspace",
        tags=tags,
    )
    log.info("Wrote to ai-memory.db: %s (id=%s)", title, mem_id)
    return mem_id


# ---------------------------------------------------------------------------
# Haiku API call
# ---------------------------------------------------------------------------

def _get_api_key() -> str:
    """Return ANTHROPIC_API_KEY from env or briefing.env fallback."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    env_file = Path.home() / ".openclaw" / "workspace" / "config" / "briefing.env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError(
        "ANTHROPIC_API_KEY not set — add to env or config/briefing.env"
    )


def call_haiku(text: str) -> dict:
    """Call Claude Haiku and return parsed JSON summary."""
    api_key = _get_api_key()

    import anthropic  # type: ignore

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model=HAIKU_MODEL,
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Summarize this conversation transcript:\n\n{text[:8000]}",
            }
        ],
    )

    raw = message.content[0].text.strip()
    return parse_summary_json(raw)


def parse_summary_json(raw: str) -> dict:
    """Parse JSON response from Haiku, with fallback for malformed responses."""
    # Strip markdown fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"```\s*$", "", raw, flags=re.MULTILINE)
    raw = raw.strip()

    defaults = {
        "one_liner": "Session summary",
        "topics": [],
        "completed": [],
        "learned": [],
        "issues": [],
        "next_steps": [],
    }

    try:
        parsed = json.loads(raw)
        # Fill in missing fields with defaults
        for key, default in defaults.items():
            if key not in parsed:
                parsed[key] = default
            # Ensure lists are lists
            if key != "one_liner" and not isinstance(parsed[key], list):
                parsed[key] = []
        return parsed
    except json.JSONDecodeError as exc:
        log.warning("Failed to parse Haiku JSON response: %s — raw: %.200s", exc, raw)
        return defaults


# ---------------------------------------------------------------------------
# Atomic write helper
# ---------------------------------------------------------------------------

def _atomic_write(path: Path, content: str) -> None:
    """Write content atomically (tmp + os.replace)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp_path.write_text(content, encoding="utf-8")
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass
        raise


# ---------------------------------------------------------------------------
# Dedup: read last entry from daily notes
# ---------------------------------------------------------------------------

def get_last_daily_entry(workspace: Path) -> Optional[str]:
    """Get the last one_liner from today's daily notes for dedup check."""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_path = workspace / "memory" / f"{today}.md"
    if not daily_path.exists():
        return None
    content = daily_path.read_text(encoding="utf-8")
    # Find last End of Day Summary entry
    matches = re.findall(r"^- \[\d{2}:\d{2}\] (.+)$", content, re.MULTILINE)
    return matches[-1] if matches else None


# ---------------------------------------------------------------------------
# Main summarizer function
# ---------------------------------------------------------------------------

def summarize(
    text: str,
    workspace: Path,
    dry_run: bool = False,
    no_daily: bool = False,
    no_context: bool = False,
    no_db: bool = False,
    min_chars: int = DEFAULT_MIN_CHARS,
    dedup_threshold: float = DEFAULT_DEDUP_THRESHOLD,
) -> int:
    """
    Main entry point. Returns exit code:
      0 = success
      1 = skipped (too short)
      2 = skipped (duplicate)
      3 = error
    """
    text = strip_boilerplate(text)

    # Guard: too short
    if len(text) < min_chars:
        log.info("Input too short (%d chars < %d) — skipping", len(text), min_chars)
        return 1

    # Call Haiku
    try:
        summary = call_haiku(text)
    except Exception as exc:
        log.error("Haiku API call failed: %s", exc)
        return 3

    # Dedup check
    last_entry = get_last_daily_entry(workspace)
    if last_entry is not None:
        sim = jaccard_similarity(summary.get("one_liner", ""), last_entry)
        log.debug("Jaccard similarity vs last entry: %.3f", sim)
        if sim >= dedup_threshold:
            log.info("Duplicate detected (similarity=%.3f >= %.3f) — skipping", sim, dedup_threshold)
            return 2

    timestamp = datetime.now().strftime("%H:%M")
    dt = datetime.now()

    if dry_run:
        print(json.dumps(summary, indent=2))
        log.info("[dry-run] Summary (no writes):\n%s", json.dumps(summary, indent=2))
        # Still exercise the write paths (they check dry_run internally)
        write_daily_notes(summary, workspace, timestamp, dry_run=True)
        write_session_context(summary, workspace / "SESSION_CONTEXT.md", dry_run=True)
        return 0

    # Write daily notes
    if not no_daily:
        try:
            write_daily_notes(summary, workspace, timestamp)
        except Exception as exc:
            log.error("Failed to write daily notes: %s", exc)

    # Write SESSION_CONTEXT.md
    if not no_context:
        try:
            write_session_context(summary, workspace / "SESSION_CONTEXT.md")
        except Exception as exc:
            log.error("Failed to write SESSION_CONTEXT.md: %s", exc)

    # Write to database
    mem_id = ""
    if not no_db:
        try:
            mem_id = write_to_db(summary, workspace)
        except Exception as exc:
            log.error("Failed to write to ai-memory.db (non-fatal): %s", exc)
            # Non-fatal: continue

    # Populate graph — extract entities + relationships (non-fatal)
    if not no_db and mem_id:
        try:
            _scripts = workspace / "scripts"
            if str(_scripts) not in sys.path:
                sys.path.insert(0, str(_scripts))
            from memory_graph import populate_graph  # type: ignore
            from memory_db import MemoryDB  # type: ignore
            db = MemoryDB(workspace / "ai-memory.db")
            graph = populate_graph(summary, mem_id, db)
            entity_count = len(graph.get("entities", []))
            link_count = len(graph.get("relationships", []))
            log.info("Graph: extracted %d entities, %d relationships", entity_count, link_count)
        except Exception as exc:
            log.debug("Graph population skipped (non-fatal): %s", exc)

    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Session memory summarizer — compress conversation text with Haiku"
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--text", type=str, help="Conversation text to summarize")
    input_group.add_argument("--file", type=Path, help="Read conversation from file")
    input_group.add_argument(
        "--session-file", type=Path, help="Read from session file in memory/ directory"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print output, don't write files",
    )
    parser.add_argument("--no-daily", action="store_true", help="Skip daily notes write")
    parser.add_argument("--no-context", action="store_true", help="Skip SESSION_CONTEXT.md write")
    parser.add_argument("--no-db", action="store_true", help="Skip ai-memory.db write")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path(os.environ.get("OPENCLAW_TEST_WORKSPACE", DEFAULT_WORKSPACE)),
        help="Override workspace path (default: ~/.openclaw/workspace)",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=DEFAULT_MIN_CHARS,
        help=f"Skip if input < N chars (default: {DEFAULT_MIN_CHARS})",
    )
    parser.add_argument(
        "--dedup-threshold",
        type=float,
        default=DEFAULT_DEDUP_THRESHOLD,
        help=f"Jaccard threshold for dedup skip (default: {DEFAULT_DEDUP_THRESHOLD})",
    )

    args = parser.parse_args()

    # Read input
    if args.text:
        text = args.text
    elif args.file:
        try:
            text = args.file.read_text(encoding="utf-8")
        except Exception as exc:
            log.error("Failed to read --file: %s", exc)
            return 3
    else:  # --session-file
        sf = args.session_file
        if not sf.is_absolute():
            sf = args.workspace / "memory" / sf
        try:
            text = sf.read_text(encoding="utf-8")
        except Exception as exc:
            log.error("Failed to read --session-file: %s", exc)
            return 3

    return summarize(
        text=text,
        workspace=args.workspace,
        dry_run=args.dry_run,
        no_daily=args.no_daily,
        no_context=args.no_context,
        no_db=args.no_db,
        min_chars=args.min_chars,
        dedup_threshold=args.dedup_threshold,
    )


if __name__ == "__main__":
    sys.exit(main())
