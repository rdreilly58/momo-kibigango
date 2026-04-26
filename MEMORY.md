

## 📅 Calendar

- **Primary:** `apple-calendar-cli` — native Apple Calendar via EventKit. Richer data than Google (attendees, alarms, recurrence, notes). Always use `--json`.
- **Secondary/fallback:** `memory__calendar_today` / `memory__calendar_range` (Google Calendar)
- **Set as default:** April 26, 2026
- **Skill:** `~/.openclaw/workspace/skills/apple-calendar-cli/SKILL.md`

---

## 🛠️ Infrastructure & Tools

### Total Recall Search (Added April 9, 2026)
- **Tool:** `~/bin/total-recall-search` → `~/.openclaw/workspace/scripts/total_recall_search.py`
- Unified semantic + keyword search over memory files and disk
- 7 improvements implemented; 63/63 tests passing; documented in momo-kioku GitHub
- Auto-routes: file/path queries → keyword; prose/concept → semantic
- **Skill:** `openclaw-skills:total-recall-search`

### FastFindApp (Fixed April 8, 2026)
- FileSearcher.swift fully rewritten in native Swift
- Uses `kMDItemFSName` Spotlight AND logic for multi-word filename search (not OR)
- Script at `~/bin/fast-find-improved.sh` (user-owned — macOS sandbox blocks system paths)
- App installed at `~/Applications/FastFindApp.app`, running in menu bar

### Memory Search Override
- **Built-in `memory_search` tool is BROKEN** — hardcoded to OpenAI, quota exceeded
- Use `mem-search "query"` alias instead (local Sentence Transformers)
- Or use `total-recall-search` for full unified search

### Total Recall Observer (Cross-session memory)
- Reads `memory/observations.md` at session startup for cross-session context
- Observer cron auto-consolidates observations into MEMORY.md when over threshold
- Config: `vectorWeight: 0.7`, `textWeight: 0.3`, MMR `lambda: 0.7`

---

## 🔧 Known Issues / Troubleshooting

### Google Tasks `jq` Display Issue (April 9, 2026)
- During heartbeat checks, `jq` sometimes shows `• \(.title)` instead of task names
- Task count is correct; only the formatted list is broken
- Root cause: escaping issue within `exec` call for `jq`

### OpenClaw 2026.4.2 Regressions (April 7, 2026)
- `claude-cli/` provider prefix no longer recognized → use `anthropic/claude-sonnet-4-6` directly
- Telegram requires explicit `plugins.allow` + `plugins.entries` registration (was built-in)
- Anthropic Sonnet times out at exactly :01 past the hour (61s); Gemini fallback succeeds

### Rocket.Chat Plugin (Broken since April 2, 2026)
- Bundled plugin broken in OpenClaw 2026.4.5 — SDK incompatibilities (GitHub Issue openclaw/openclaw#16706)
- `RuntimeEnv` properties (`channel`, `config`, `logging`) renamed/removed
- Decision: install third-party plugin (Option 2); blocked by JSON config error (position 336)
- Status as of April 13: migration still pending

---

## 🖥️ System State

### AWS GPU Instance
- **`54.81.20.218` is DOWN** — 100% packet loss since ~April 5, 2026
- Requires restart/replacement in AWS console
- Workarounds available: local M4 Mac Mini GPU, Google Colab H100

### Telegram
- Credentials configured April 11, 2026
- Bot token: `(stored in ~/.openclaw/config.json)`
- Chat ID: `8755120444`
- Daily briefings and heartbeat notifications now enabled

### OpenRouter API Credits
- Credits exhausted as of ~April 11, 2026
- Total Recall Observer falling back to Anthropic Haiku native API
- Replenish at: https://openrouter.ai/settings/credits

---

## 📋 Active Projects

### ReDrafter Benchmarking
- `benchmark_redrafter_rewritten.py` running with `Qwen/Qwen2.5-7B-Instruct`
- Output: `redrafter_benchmark_output.txt`
- Colab training notebooks committed to repo (A100, all fixes applied)

### momo-kioku GitHub Repo
- `total_recall_search` README.md pushed April 9, 2026
- Documents all 7 improvements and CLI usage

---

## ✅ Decisions Made

### Cascade Proxy (Decommissioned April 11, 2026)
- Trial ended April 5, 2026; zero requests routed
- Bob ordered full removal of measurement and reporting infrastructure
- Cascade Daily Report cron deleted April 12, 2026

### Model Routing (Updated April 16, 2026)
- Three-tier routing: Haiku (simple/short) → Sonnet (default/medium) → Opus (complex)
- `openrouter/auto` removed — explicit model IDs used instead
- Sonnet 4-6 is now the default tier for most tasks
- See `TASK_ROUTING.md` and `config/classifier-config.json` for details

---

## 📋 Lessons Learned

- **File**: `memory/lessons-learned.md`
- Running record of non-trivial problems, root causes, fixes, and prevention steps
- **Convention**: `fix:` commits should reference the relevant entry with `(see lessons-learned.md#anchor)` in the commit body
- Observer agent flags new `fix:` commits → reminds to add a lessons entry
- Quarterly review cron (Jan/Apr/Jul/Oct 1st, 09:03) surfaces entries older than 90 days for promotion to MEMORY.md or archival

---

## 📝 Pending Tasks

Tracked in Things 3 (migrated 2026-04-16). Use `things today` or `things inbox` — not this file.
