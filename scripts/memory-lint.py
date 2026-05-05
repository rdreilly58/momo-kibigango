#!/usr/bin/env python3
"""
memory-lint.py — Consistency audit for the OpenClaw memory system.

Checks both:
  - ~/.openclaw/workspace/memory/  (OpenClaw workspace memory)
  - ~/.claude/projects/*/memory/   (Claude Code auto-memory)

Run manually:  python3 scripts/memory-lint.py
Run with fix:  python3 scripts/memory-lint.py --fix
JSON output:   python3 scripts/memory-lint.py --json
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

WORKSPACE_MEMORY = Path.home() / ".openclaw" / "workspace" / "memory"
CLAUDE_MEMORY_GLOB = str(Path.home() / ".claude" / "projects" / "*" / "memory")
VALID_TYPES = {
    "user",
    "feedback",
    "project",
    "reference",
    "concept",
    "tool",
    "decision",
    "lesson",
    "analysis",
}
STALE_DAYS = 45  # project files older than this without update are flagged

# Files to skip (daily notes, metrics, archives are not linted)
SKIP_PATTERNS = [
    r"^\d{4}-\d{2}-\d{2}.*\.md$",  # daily notes
    r"^DAILY_METRICS_",  # metrics files
    r"^memories\.db$",  # sqlite db
]

issues = []
stats = {"files_checked": 0, "issues": 0, "warnings": 0}


def should_skip(filename: str) -> bool:
    for pattern in SKIP_PATTERNS:
        if re.match(pattern, filename):
            return True
    return False


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter dict and body. Returns ({}, content) if none."""
    if not content.startswith("---"):
        return {}, content
    end = content.find("\n---", 4)
    if end == -1:
        return {}, content
    fm_text = content[4:end]
    body = content[end + 4 :].strip()
    fm = {}
    for line in fm_text.strip().splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            val = val.strip().strip('"').strip("'")
            # Parse list values like [a, b, c]
            if val.startswith("[") and val.endswith("]"):
                val = [v.strip().strip('"') for v in val[1:-1].split(",") if v.strip()]
            fm[key.strip()] = val
    return fm, body


def extract_backlinks(content: str) -> list[str]:
    """Find all [[link]] references in content."""
    return re.findall(r"\[\[([^\]]+)\]\]", content)


def add_issue(severity: str, file: str, message: str, fix: Optional[str] = None):
    issues.append(
        {
            "severity": severity,
            "file": file,
            "message": message,
            "fix": fix,
        }
    )
    if severity == "error":
        stats["issues"] += 1
    else:
        stats["warnings"] += 1


def lint_file(path: Path, all_stems: set[str], memory_root: Path):
    """Lint a single memory file."""
    rel = str(path.relative_to(memory_root))
    if should_skip(path.name):
        return

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        add_issue("error", rel, f"Could not read file: {e}")
        return

    stats["files_checked"] += 1
    fm, body = parse_frontmatter(content)

    # --- Frontmatter checks ---
    if not fm:
        add_issue(
            "warning",
            rel,
            "No YAML frontmatter found",
            fix="Add ---\\nname/title: ...\\ntype: ...\\n---",
        )
    else:
        # Check type
        ftype = fm.get("type", "")
        if not ftype:
            add_issue(
                "error",
                rel,
                "Missing 'type' in frontmatter",
                fix=f"Add type: <one of {sorted(VALID_TYPES)}>",
            )
        elif ftype not in VALID_TYPES:
            add_issue(
                "warning", rel, f"Unknown type '{ftype}' — valid: {sorted(VALID_TYPES)}"
            )

        # Check name or title
        if not fm.get("name") and not fm.get("title"):
            add_issue("warning", rel, "Missing 'name' or 'title' in frontmatter")

        # Check stale project files
        if ftype == "project":
            updated_str = fm.get("updated") or fm.get("created") or ""
            if updated_str:
                try:
                    updated = datetime.strptime(updated_str[:10], "%Y-%m-%d")
                    age = (datetime.now() - updated).days
                    if age > STALE_DAYS:
                        add_issue(
                            "warning",
                            rel,
                            f"Stale project file — last updated {age} days ago ({updated_str})",
                            fix="Update 'updated' date or archive if complete",
                        )
                except ValueError:
                    pass

    # --- Backlink checks ---
    links = extract_backlinks(content)
    for link in links:
        stem = link.strip()
        if stem not in all_stems:
            add_issue(
                "warning", rel, f"Broken backlink: [[{stem}]] — no matching file found"
            )

    # --- Content checks ---
    if len(content.strip()) < 50:
        add_issue("warning", rel, "Very short file — may be a stub or placeholder")


def lint_memory_dir(memory_root: Path, label: str):
    """Lint all eligible markdown files in a memory directory."""
    if not memory_root.exists():
        print(
            f"  Skipping {label} — directory not found: {memory_root}", file=sys.stderr
        )
        return

    # Build set of all stems for backlink resolution (non-skipped .md files)
    all_md = list(memory_root.rglob("*.md"))
    all_stems = {f.stem for f in all_md if not should_skip(f.name)}

    print(
        f"  Scanning {label}: {len(all_md)} markdown files ({len(all_stems)} lintable)",
        file=sys.stderr,
    )

    for path in sorted(all_md):
        if path.is_dir():
            continue
        lint_file(path, all_stems, memory_root)


def check_memory_index(memory_root: Path):
    """Check that MEMORY.md index entries point to real files (Claude Code memory)."""
    index_path = memory_root / "MEMORY.md"
    if not index_path.exists():
        return

    content = index_path.read_text(encoding="utf-8")
    # Find all [text](file.md) links
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
    for text, href in links:
        if href.startswith("http"):
            continue
        target = memory_root / href
        if not target.exists():
            add_issue(
                "error",
                "MEMORY.md",
                f"Index link points to missing file: [{text}]({href})",
            )

    # Find files in memory_root not in MEMORY.md
    for path in sorted(memory_root.glob("*.md")):
        if path.name in ("MEMORY.md",) or should_skip(path.name):
            continue
        if path.name not in content and path.stem not in content:
            add_issue(
                "warning",
                "MEMORY.md",
                f"File '{path.name}' exists but is not listed in MEMORY.md index",
                fix=f"Add entry for {path.name} to MEMORY.md",
            )


def main():
    parser = argparse.ArgumentParser(
        description="Audit memory files for consistency issues"
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument(
        "--fix", action="store_true", help="Apply safe auto-fixes (dry run by default)"
    )
    parser.add_argument(
        "--errors-only", action="store_true", help="Show only errors, not warnings"
    )
    args = parser.parse_args()

    print("memory-lint: scanning memory directories...", file=sys.stderr)

    # Scan OpenClaw workspace memory
    lint_memory_dir(WORKSPACE_MEMORY, "OpenClaw workspace memory")

    # Scan Claude Code auto-memory directories
    for claude_mem_dir in glob.glob(CLAUDE_MEMORY_GLOB):
        p = Path(claude_mem_dir)
        label = f"Claude Code memory ({p.parent.name})"
        lint_memory_dir(p, label)
        check_memory_index(p)

    # Filter
    filtered = issues
    if args.errors_only:
        filtered = [i for i in issues if i["severity"] == "error"]

    stats["issues_shown"] = len(filtered)

    if args.json:
        print(json.dumps({"stats": stats, "issues": filtered}, indent=2))
        return

    # Human-readable output
    print(f"\n{'=' * 60}")
    print(f"Memory Lint Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'=' * 60}")
    print(f"Files checked: {stats['files_checked']}")
    print(f"Errors:        {stats['issues']}")
    print(f"Warnings:      {stats['warnings']}")
    print()

    if not filtered:
        print("✅ No issues found.")
        return

    errors = [i for i in filtered if i["severity"] == "error"]
    warnings = [i for i in filtered if i["severity"] == "warning"]

    if errors:
        print("🔴 ERRORS (must fix):")
        for i in errors:
            print(f"  [{i['file']}] {i['message']}")
            if i.get("fix"):
                print(f"    → Fix: {i['fix']}")
        print()

    if warnings and not args.errors_only:
        print("🟡 WARNINGS (should fix):")
        for i in warnings:
            print(f"  [{i['file']}] {i['message']}")
            if i.get("fix"):
                print(f"    → Fix: {i['fix']}")
        print()

    if stats["issues"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
