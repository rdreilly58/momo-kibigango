# Contributing

## Branches

Work on `main` directly for workspace maintenance and small fixes. For larger features, create a branch:

```bash
git checkout -b feature/short-description
```

Avoid committing directly to `main` for non-trivial changes.

## Commit messages

Follow this format: `type(scope): short description`

Types: `feat`, `fix`, `chore`, `security`, `docs`, `refactor`

Examples:
```
feat(memory): add 7-day TTL to working-tier inserts
fix(briefing): replace hardcoded date with live $(date) call
security(P0): remove exposed API key, harden .gitignore
chore: weekly memory consolidation
```

Keep the subject line under 72 characters. Add a body for anything non-obvious.

## Secrets

**Never commit secrets.** The pre-commit hook will block most cases, but be proactive:

- Store credentials in `TOOLS.secrets.local` (gitignored)
- Use placeholders in committed files: `TOKEN=  # stored in TOOLS.secrets.local`
- If you accidentally commit a secret: rotate it immediately, then remove from history

## Pre-commit hook

The hook at `.git/hooks/pre-commit` scans staged additions for token-like values and previously-exposed credentials. It runs automatically on `git commit`.

To bypass in a genuine emergency (e.g. removing a secret): `git commit --no-verify`. Do not make this a habit.

## Tests

Run the memory test suite before pushing:

```bash
python3 Tests/ai_memory_test_suite.py -v
```

Check script syntax for any shell script you modify:

```bash
bash -n scripts/your-script.sh
```

## Scripts

- `scripts/memory_db.py` — SQLite API for `ai-memory.db`. CLI and module.
- `scripts/observer-agent.sh` — Called by the Total Recall Observer cron every 2h.
- `scripts/weekly-memory-consolidation.sh` — Runs Sunday 1 AM; archives memory, DB dump, TTL expiry.
- `scripts/auto-flush-session-context.sh` — Writes session context to DB on context flush.
- `scripts/total_recall_search.py` — Borda-count search across keyword, semantic, and DB backends.

## Memory system

Three layers run in parallel:

| Layer | Location | Purpose |
|-------|----------|---------|
| File-based | `memory/` + `MEMORY.md` | Human-readable, version-controlled |
| SQLite | `ai-memory.db` (gitignored) | Structured, FTS5, TTL, graph links |
| OpenClaw built-in | `~/.openclaw/` | Session memory, semantic search |

`ai-memory.db` is machine-local and gitignored. Weekly SQL dumps land in `memory/archive/`.
