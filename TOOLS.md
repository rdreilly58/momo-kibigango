
## Calendar (Primary — Apple Calendar)

**Tool:** `apple-calendar-cli` at `/opt/homebrew/bin/apple-calendar-cli`
**Always use `--json`.** Google Calendar tools (`memory__calendar_today` / `memory__calendar_range`) are secondary fallback only.
**Skill:** `~/.openclaw/workspace/skills/apple-calendar-cli/SKILL.md`

---

## Git Commit Author (ENFORCED)

| Repo | Email |
|------|-------|
| reillydesignstudio | robert.reilly@peraton.com (global default — Vercel requires this) |
| momo-kibigango (workspace) | rdreilly2010@gmail.com (local override) |
| All others | robert.reilly@peraton.com |

---

## Email Operations

- **`rdreilly2010@gmail.com`** — ✅ Active, full OAuth (primary for all read/search/calendar)
- **`robert@reillydesignstudio.com`** — ✅ Active OAuth (gmail scope, added 2026-04-27)
- ~~`reillyrd58@gmail.com`~~ — 🗑️ Abandoned. Do NOT use.

**Send to Bob:** `gog gmail send -a "rdreilly2010@gmail.com" --to "..."`
**Send as RDS:** `gog gmail send -a robert@reillydesignstudio.com --to "..." --subject "..." --body "..."`

---

## Memory Search

**Primary:** `total-recall-search <query> [--json] [--limit N]`
→ `~/.openclaw/workspace/scripts/total_recall_search.py`

**With reranking:** `total-recall-search "query" --rerank --json`

---

## Compute

| Priority | Resource | Status |
|----------|----------|--------|
| 1 | Local M4 Mac Mini GPU (MLX) | ✅ Primary |
| 2 | Google Colab H100 | ✅ Available (manual) |

---

## Known API Issues

**Anthropic Sonnet `:01` timeout:** Times out at exactly :01 past the hour (61s). Gemini fallback handles it automatically.

**Anthropic spend check:**
```bash
ADMIN_KEY=$(security find-generic-password -s "AnthropicAdminKey" -w)
curl -s "https://api.anthropic.com/v1/organizations/usage_report/messages?starting_at=$(date -v-7d +%Y-%m-%d)&ending_at=$(date +%Y-%m-%d)&group_by[]=model" \
  -H "x-api-key: $ADMIN_KEY" -H "anthropic-version: 2023-06-01" \
  | python3 ~/.openclaw/workspace/scripts/anthropic-spend-check.py
```

---

## Pre-Reboot (macOS shutdown hang fix)

```bash
bob-reboot      # graceful restart — quits Mail/Music/Photos/Safari first
bob-shutdown    # graceful power-off
```
Scripts: `~/.openclaw/workspace/scripts/pre-reboot-quit-apps.sh` + `bob-reboot.sh`

---

## Remote Access

Direct SSH / Termius on local network. No VPN. Tailscale removed 2026-05-01.
For agent exec on Mac: `exec host=node`.
