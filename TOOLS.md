
## Calendar (Primary — Apple Calendar)

**Tool:** `apple-calendar-cli` (installed at `/opt/homebrew/bin/apple-calendar-cli`)
**Skill:** `~/.openclaw/workspace/skills/apple-calendar-cli/SKILL.md`
**Always use `--json`** for reliable parsing.

```bash
# Today's events
apple-calendar-cli list-events --from 2026-04-26 --to 2026-04-27 --json

# List calendars
apple-calendar-cli list-calendars --json

# Create event
apple-calendar-cli create-event --title "Meeting" --start "2026-04-27T10:00:00" --end "2026-04-27T11:00:00" --json

# Update / delete
apple-calendar-cli update-event EVENT-ID --title "New title" --json
apple-calendar-cli delete-event EVENT-ID --json
```

**Note:** Use Apple Calendar CLI for ALL calendar operations. The `memory__calendar_today` / `memory__calendar_range` Google Calendar tools are secondary fallback only — prefer native Apple Calendar which has richer data (attendees, alarms, recurrence, notes).

---

## Git Commit Author (ENFORCED)

**Global (default for all repos):** `robert.reilly@peraton.com` / `Robert Reilly`
Vercel only builds reillydesignstudio with this author.

**Workspace override (momo-kibigango only):** `rdreilly2010@gmail.com` / `Robert Reilly`
Set as local config in `~/.openclaw/workspace/.git/config`. Updated 2026-04-27 (was reillyrd58, migrated to active address).

| Repo | Email | Set via |
|------|-------|---------|
| reillydesignstudio | robert.reilly@peraton.com | global |
| momo-kibigango (workspace) | rdreilly2010@gmail.com | local override |
| All others | robert.reilly@peraton.com | global |

---

## Email Operations

✅ **CURRENT STATUS (as of April 27, 2026):**
- `rdreilly2010@gmail.com` — **ACTIVE** (full OAuth: gmail, calendar, drive, docs, tasks, sheets, contacts, etc.)
- `robert@reillydesignstudio.com` — **ACTIVE** (gmail OAuth, added 2026-04-27 — replaces reillyrd58)
- ~~`reillyrd58@gmail.com`~~ — token **REMOVED** 2026-04-27. Abandoned (was broken since 2026-03-21).

**Send to Bob:** `gog gmail send -a "rdreilly2010@gmail.com" --to "..."` (most reliable inbox)

**Read inbox:** `gog gmail search -a rdreilly2010@gmail.com "is:inbox"`

**ReillyDesignStudio** (`robert@reillydesignstudio.com`):  
- **Native send:** `gog gmail send -a robert@reillydesignstudio.com --to "..." --subject "..." --body "..."`
- **Native read:** `gog gmail search -a robert@reillydesignstudio.com "is:inbox"`
- **Send-as via rdreilly2010** (legacy forwarding path, still works): `gog gmail send -a rdreilly2010@gmail.com --from robert@reillydesignstudio.com --to "..."`

---

## Total Recall Search — Unified Memory + Disk Search (Added April 9, 2026)

**Tool:** `total-recall-search`
**Location:** `~/bin/total-recall-search` → `~/.openclaw/workspace/scripts/total_recall_search.py`
**Skill:** `~/.openclaw/workspace/skills/total-recall-search/SKILL.md`
**Usage:** `total-recall-search <query> [--type auto|semantic|keyword] [--limit N] [--path /dir] [--json]`
**Purpose:** Unified search across semantic memory (Sentence Transformers over memory files) and local disk (momo-kioku-search/Spotlight). Auto-routes: file/path queries → keyword; prose/concept queries → semantic.
**Examples:**
```bash
total-recall-search "cascade proxy savings"          # auto-route (semantic)
total-recall-search "SOUL.md" --type keyword         # file search
total-recall-search "Leidos job" --type semantic     # memory recall
total-recall-search "config" --json --limit 5        # JSON output
```
**Output:** JSON array with `type`, `path`, `snippet`, `score`, `source_line` fields.
**Note:** Semantic search requires `sentence-transformers` in workspace venv (~5-15s first run).

---

## Compute Fallback Hierarchy (Updated April 2026)

When GPU/inference compute is needed, use this priority order:

| Priority | Resource | Status | Notes |
|----------|----------|--------|-------|
| 1 | Local M4 Mac Mini GPU (MLX) | ✅ Active | Best for everyday inference |
| 2 | Google Colab H100 | ✅ Available | Manual setup; use notebooks in repo |
| 3 | AWS EC2 `54.81.20.218` | ❌ DOWN | Down since April 5 — restart in AWS console |

**GPU health check scripts** archived to `scripts/_archive/` — do not use until AWS instance is back.

---

## Known API Reliability Issues

**Anthropic Sonnet `:01` timeout:** Sonnet times out at exactly :01 past the hour (61s). Gemini fallback succeeds. Manual retry is rarely needed now.

**Retry config (applied April 19, 2026):**
- `channels.telegram.retry`: attempts=3, minDelayMs=5000, maxDelayMs=30000
- `cron.retry`: maxAttempts=3, backoffMs=[5000,15000,30000], retryOn all transient types

Gateway restart required to activate (or restart automatically next gateway cycle).

**OpenRouter credits:** Monitor at `openrouter.ai/settings/credits`. Credits exhausted ~April 11 — Total Recall Observer fell back to Anthropic Haiku silently. The `api-quota-monitor.sh` now checks and alerts when below $1.

---

## Pre-Reboot Graceful App-Quit (Added April 30, 2026)

**Problem:** macOS 26.3 (Tahoe) Mail.app's WebKit child processes refuse to terminate cleanly during shutdown, causing 60–90 s hangs (`pageCount > 0` with `shutdownPreventingScopeCounter = 0`). Bob's M4 hung 88 s on Apr 30 reboot.

**Solution:** Pre-quit known offenders before invoking `shutdown`/`reboot`.

```bash
bob-reboot         # graceful restart (quits Mail/Music/Photos/Safari first)
bob-shutdown       # graceful power-off
```

**Files:**
- `~/.openclaw/workspace/scripts/pre-reboot-quit-apps.sh` — the quit logic (8 s grace per app, then SIGTERM)
- `~/.openclaw/workspace/scripts/bob-reboot.sh` — wrapper that calls quit script + `sudo shutdown -r now`
- `~/Library/LaunchAgents/com.momotaro.pre-reboot-quit-apps.plist` — watches `~/.openclaw/state/reboot-trigger` (manual hook for future automation)
- Aliases in `~/.zshrc`: `bob-reboot`, `bob-shutdown`
- Logs: `~/.openclaw/logs/pre-reboot-quit-apps.log`

**Add new offenders:** edit `BLOCKING_APPS` array in `pre-reboot-quit-apps.sh`. Detection rule: search `/usr/bin/log show ... eventMessage CONTAINS "canTerminateAuxiliaryProcess"` after a slow shutdown.

---

## Fast Disk Search (via mdfind) - Added April 8, 2026

**Tool:** `fast-find.sh`
**Location:** `~/.openclaw/workspace/scripts/fast-find.sh`
**Usage:** `bash ~/.openclaw/workspace/scripts/fast-find.sh "your query" [limit]`
**Purpose:** Leverages macOS Spotlight (`mdfind`) for very fast keyword searching across the entire disk.
**Example:** `bash ~/.openclaw/workspace/scripts/fast-find.sh "momo-akira" 20`

---

## Remote Access (Updated May 1, 2026)

**Tailscale: UNINSTALLED** — removed 2026-05-01.

Remote access to Mac mini is now via **direct SSH only**:
- **Termius** on iPhone/iPad → direct IP or local network
- **SSH** via standard port on local network
- No VPN tunnel required

For exec on Mac from agent: use `exec host=node` (Bob's M4 Mac mini node is registered in OpenClaw).
