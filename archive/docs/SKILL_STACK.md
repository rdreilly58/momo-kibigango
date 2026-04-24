# Core Skill Stack — April 22, 2026

## Active Skills (24 installed)

### Essential — Always Available
- **gog** (via CLI) — Gmail, Calendar, Drive, Tasks
- **ga4-analytics** — Google Analytics 4 reporting + BigQuery queries
- **ios-dev** — Xcode, iPhone builds, simulators (Momotaro app)
- **aws-deploy** — AWS Amplify deployments (ReillyDesignStudio)
- **agent-browser** — Web automation + screenshot (Agent-Browser Rust CLI)
- **swift-expert** — SwiftUI + async/concurrency patterns

### Always-On Automation
- **ai-daily-briefing** — Morning & evening briefing system
- **daily-briefing** — Legacy briefing (retained for compatibility)
- **openclaw-ops-guardrails** — Ops runbook + troubleshooting standards
- **slack** — Slack messaging + integrations

### Memory & Context
- **elite-longterm-memory** — 5-layer memory architecture (SESSION-STATE.md, MEMORY.md, daily logs, LanceDB optional, git-notes)
- **total-recall-search** — Comprehensive cross-source search (memory, files, git)
- **openclaw-agent-discovery** — Agent discovery + evaluation

### Utilities
- **make-pdf** — Pandoc-based PDF generation
- **office-docs** — Microsoft Word + Excel (python-docx)
- **print-local** — Brother printer control (local)
- **printer-brother** — Brother printer (legacy; consolidate with print-local)
- **invoice-generator** — Invoice creation from templates
- **gmail-send** — Email delivery via SMTP
- **apple-calendar-cli** — Calendar CLI (evaluate overlap with gog)

### Development & Infrastructure
- **address-lookup** — OSM Nominatim address verification
- **roblox-loader** — Roblox game automation
- **s3** — AWS S3 bucket operations
- **web-perf** — Web performance analysis + optimization
- **telegram-voice-to-voice-macos** — Telegram voice-to-voice on macOS

---

## Hooks (settings.json — ~/.claude/settings.json)

| Event | Matcher | Script | Purpose |
|-------|---------|--------|---------|
| Stop | * | session-stop-hook.sh | Session summary to daily notes |
| UserPromptSubmit | * | session-start-hook.sh | Session init |
| PostToolUse | * | session-checkpoint-hook.sh | Mid-session checkpoints every 20 tool uses |
| PostToolUse | Write\|Edit | auto-format-hook.sh | ruff format on .py files (P1 — Apr 22) |
| PreToolUse | Bash\|Write | secret-scan-hook.sh | Block credential/key leaks (P1 — Apr 22) |

---

## P2 Candidates (install when needed)

```bash
clawhub install taskflow          # Multi-session task tracking
clawhub install memory-tiering    # Tiered memory (evaluate vs elite-longterm-memory)
clawhub install code-review       # PR review automation
```

---

## Archived Skills (can reinstall)

| Skill | Reason |
|-------|--------|
| browser-automation | Redundant with agent-browser |
| email-best-practices | Reference docs, not executable |
| email-daily-summary | Replaced by daily-briefing |
| himalaya | Slow (30-60s); gog is faster |
| mbse | YAML diagrams, low use |
| speculative-decoding | Phase 1 research — deleted Apr 22 (backed up) |
| security-monitor | Not integrated |
| linkedin-automation | On-demand reinstall |
| notion | No Notion workspace |
| sovereign-aws-cost-optimizer | One-time tool |

---

## Notes
- `printer-brother` + `print-local` may be duplicates — consolidate at next audit
- `apple-calendar-cli` may overlap with `gog` calendar — evaluate at next audit
- LanceDB warm tier initialized and populated: 217 records (200 flat-file chunks + 17 original) as of Apr 23 2026
- Weekly sync: `memory-sync-flat-files.py` runs Wed 10am; smart prune runs Wed 9am
- ruff installed in workspace venv: `~/.openclaw/workspace/venv/bin/ruff`

---

*Last updated: April 22, 2026*
*Maintained by: Momotaro*
