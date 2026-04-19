
## Git Commit Author (ENFORCED)

**Always use:** `robert.reilly@peraton.com` / `Robert Reilly`  
Vercel only builds reillydesignstudio with this author. Set globally: `git config --global user.email "robert.reilly@peraton.com"`

---

## Email Operations

**Primary account:** `reillyrd58@gmail.com` — use `gog` CLI for all Gmail ops.  
- **Send:** `gog gmail send -a "reillyrd58@gmail.com" --to "..." --subject "..." --body-file <(cat file.txt)`  
- **Read:** `gog gmail search -a reillyrd58@gmail.com "is:inbox"` (supports `from:X AND subject:Y AND after:DATE`)  
- **Never use:** Himalaya for Gmail, `mail` command, `rdreilly2010@gmail.com` (expired)  

**ReillyDesignStudio** (`robert@reillydesignstudio.com`): Routed via reillyrd58@gmail.com (forwarding + send-as)  
- **Receive:** forwards to reillyrd58 inbox — read with `gog gmail search -a reillyrd58@gmail.com "is:inbox"`  
- **Send as robert@:** `gog gmail send -a reillyrd58@gmail.com --from robert@reillydesignstudio.com --to "..." --subject "..." --body "..."`

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

## Fast Disk Search (via mdfind) - Added April 8, 2026

**Tool:** `fast-find.sh`
**Location:** `~/.openclaw/workspace/scripts/fast-find.sh`
**Usage:** `bash ~/.openclaw/workspace/scripts/fast-find.sh "your query" [limit]`
**Purpose:** Leverages macOS Spotlight (`mdfind`) for very fast keyword searching across the entire disk.
**Example:** `bash ~/.openclaw/workspace/scripts/fast-find.sh "momo-akira" 20`
