# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## Discord Integration (March 21, 2026)

**Status:** ✅ CONFIGURED - Ready for deployment

### Configuration Details (March 21, 04:46 EDT)

**Server:**
- **Server ID:** `1484831927914594425`
- **Email:** New (fresh setup)
- **Bot Status:** Authorized & configured

**Channel IDs:**
| Channel | ID | Purpose |
|---------|---|---------|
| #general | 1484830406300930220 | Main chat with Momotaro |
| #subagents | 1484830460717568171 | Subagent task results |
| #telegraph | 1484830547766280212 | Telegraph articles |
| #heartbeat | 1484830618226528389 | Status reports |
| #archive | 1484830728121487440 | Message archive |
| #dev-tools | 1484830760870613054 | Dev commands (Bob only) |
| #logs | 1484830298389741650 | Error logs (Bob only) |

**Bot Configuration:**
- **Bot Token:** Stored securely (`9c309ce3d4e566c117ca...***`)
- **Config File:** `~/.openclaw/config/discord.json` ✅
- **Validation:** PASSED ✅
- **Command Prefix:** `!`
- **Status Message:** "Playing with Momotaro 🍑"

### Features Enabled
✅ Auto-threading for organized discussions
✅ Auto-embed Telegraph links with previews
✅ Archive all messages to searchable index
✅ Telegraph formatting in Discord
✅ Message logging to #logs
✅ Error logging and reporting

### Files
- **Config:** `~/.openclaw/config/discord.json` (960 bytes)
- **Validator:** `scripts/validate_discord_config.py` (executable)
- **Bot Script:** `scripts/discord_bot.py` (ready)
- **Logs:** `~/.openclaw/logs/discord.log`

### CLI to Deploy Bot
```bash
# Validate config (should pass)
python3 scripts/validate_discord_config.py

# Start bot
python3 scripts/discord_bot.py

# View logs
tail -f ~/.openclaw/logs/discord.log

# Test connectivity
# Send message in Discord #general → should see response
```

### Next: Gateway Integration
- Update gateway config to enable Discord channel
- Restart gateway
- Test message routing: Telegram ↔ Discord
- Verify Telegraph auto-posting
- Verify subagent integration

---

## Telegraph Publishing System (March 21, 2026)

**Status:** ✅ ACTIVE - Full integration deployed

### Account & Configuration
- **Account:** OpenClaw/Momotaro (created March 21, 2026 00:47 EDT)
- **Access Token:** Stored securely at `~/.telegraph_token` (600 permissions)
- **Config File:** `~/.openclaw/workspace/config/telegraph.json`
- **API Endpoint:** https://api.telegra.ph (connectivity verified ✅)

### What It Does
- **Auto-publishes formatted output** from subagents (>2000 chars or contains tables)
- **Publishes HEARTBEAT reports** (tasks, calendar, metrics) to Telegraph
- **Manual CLI publishing** for direct article creation
- **Secure token management** with encrypted storage
- **Retry logic** with exponential backoff (3 attempts, max 30s delay)
- **Comprehensive logging** to `~/.openclaw/logs/telegraph.log`

### CLI Commands

```bash
# Status & validation
python3 ~/.openclaw/workspace/scripts/telegraph-cli.py status
python3 ~/.openclaw/workspace/scripts/telegraph-cli.py config validate
python3 ~/.openclaw/workspace/scripts/telegraph-cli.py logs --lines 50

# Publishing
python3 ~/.openclaw/workspace/scripts/telegraph-cli.py publish-md "Title" /path/to/file.md
python3 ~/.openclaw/workspace/scripts/telegraph-cli.py publish-text "Title" "Content"
python3 ~/.openclaw/workspace/scripts/telegraph-cli.py test
```

### File Locations
- **Token:** `~/.telegraph_token` (600 perms)
- **Config:** `~/.openclaw/workspace/config/telegraph.json` (600 perms)
- **Publisher:** `~/.openclaw/workspace/scripts/telegraph_publisher.py`
- **CLI:** `~/.openclaw/workspace/scripts/telegraph-cli.py`
- **Heartbeat:** `~/.openclaw/workspace/scripts/telegraph_heartbeat.py`
- **Logs:** `~/.openclaw/logs/telegraph.log`

### First Published Article
✅ **URL:** https://telegra.ph/OpenClaw-Telegraph-Integration-Test-03-21  
✅ **Published:** March 21, 2026 00:48:41 EDT

---

## Password Manager Configuration (March 20, 2026)

**Setup:** Consolidated from multiple managers → Apple Passwords (personal) + 1Password (OpenClaw)

### Division of Responsibilities
- **Apple Passwords:** Personal accounts, websites, Bob's daily use
- **1Password:** OpenClaw/Momotaro secrets only (API keys, tokens, service accounts)

### 1Password Setup Details
- **Account:** robert@reillydesignstudio.com
- **Vault:** "OpenClaw Secrets" (default)
- **Emergency Kit:** ~/.openclaw/workspace/backups/1password_emergency_kit_2026-03-20.pdf
- **Desktop Integration:** Enabled (Settings → Developer → Integrate with 1Password CLI)

### 1Password CLI Usage
```bash
# Test CLI integration
~/.openclaw/workspace/scripts/test_1password_cli.sh

# Sign in (requires desktop app unlocked)
op signin

# List vaults
op vault list

# Read an item
op item get "Brave Search API" --fields password

# Create new API key entry
op item create --category="API Key" --title="Service Name" --vault="OpenClaw Secrets" password="key_value"
```

### Migration Status
- ✅ Dashlane: No installation found (already unused)
- ⏳ Chrome passwords: Manual export required → Apple Passwords
- ✅ Old 1Password: Deleted and backed up
- ⏳ New 1Password: App installed, awaiting account creation
- ⏳ CLI integration: Ready to configure after account setup

### Backup Locations
- Chrome export instructions: ~/.openclaw/workspace/backups/chrome_passwords_export_instructions_2026-03-20.txt
- 1Password setup guide: ~/.openclaw/workspace/backups/1password_setup_instructions_2026-03-20.txt
- Old 1Password data: ~/Library/Application Support/1Password.backup.*

---

## API Keys & Credentials

**⚠️ Location:** Keep all API keys here in TOOLS.md (workspace file), NOT in ~/.openclaw/config.json (system file)

**Why:** This workspace file is where you naturally look for your setup details. System config files get updated/reset by OpenClaw.

### Brave Search API
- **Key:** `REDACTED_BRAVE_API_TOKEN`
- **Source:** ~/.openclaw/config.json (originally) → moved to TOOLS.md for reference
- **Used for:** Web search via `web_search` tool (gas prices, news, research)
- **Status:** ✅ Active
- **Last validated:** March 15, 2026

### Cloudflare API Token
- **Token:** `REDACTED_CLOUDFLARE_TOKEN`
- **Used for:** DNS management for reillydesignstudio.com
- **Permissions:** Zone.DNS
- **Status:** ✅ Active
- **Last used:** March 22, 2026

### Cloudflare Support Case (March 22, 2026)
- **Case ID:** 02033456
- **Issue:** Account recovery — old email (robert.reilly@peraton.com) no longer accessible
- **Requested Changes:** 
  - Update primary email to `robert@reillydesignstudio.com`
  - Add secondary email: `reillyrd58@gmail.com`
- **Phone on file:** 703-955-1838
- **Status:** Awaiting Cloudflare response (created 4:59 PM EDT March 22, 2026)
- **Follow-up:** Reply to support case email or visit https://dash.cloudflare.com/support

### Healthchecks.io (Cron Monitoring)
- **Account:** https://healthchecks.io (free tier)
- **Setup date:** March 16, 2026

**Active Checks:**
- **Morning Briefing:** `https://hc-ping.com/43edd8e8-e569-4bad-b044-90ab1546c271`
  - Schedule: Daily, 6:00 AM EDT
  - Grace time: 5 min
  - Auto-pings on completion
  
- **Evening Briefing:** `https://hc-ping.com/d570cbc7-1164-492b-98f1-0443ce23482e`
  - Schedule: Daily, 5:00 PM EDT
  - Grace time: 5 min
  - Auto-pings on completion

**How it works:**
- If briefing doesn't complete within grace period, Healthchecks alerts via Telegram
- Each cron job is configured to ping URL automatically after success
- Prevents silent failures in automation

## Embeddings Provider (Hugging Face API)

**Setup Date:** March 20, 2026, 4:11 AM EDT
**Status:** ✅ ACTIVE - Using Hugging Face API for memory search
**Provider:** Hugging Face Inference API

### Configuration
- **Model:** sentence-transformers/all-MiniLM-L6-v2
- **API Token:** `REDACTED_HF_API_TOKEN`
- **Endpoint:** api-inference.huggingface.co
- **Performance:** ~500-1000ms per embedding (API latency)
- **Dimension:** 384 (vector size)
- **Cost:** Free (generous free tier, no quota limits)
- **Fallback:** Local Sentence Transformers if API fails

### Installation
- **Python Environment:** `~/.openclaw/workspace/venv/`
- **Package:** sentence-transformers v5.3.0
- **Dependencies:** PyTorch, transformers, numpy

### Usage

**Embedding Service:**
```bash
# Single text
cd ~/.openclaw/workspace && source venv/bin/activate
python scripts/embedding_service.py "text to embed"

# Batch processing
echo '["text 1", "text 2", "text 3"]' | python scripts/embedding_service.py --batch

# Check stats
python scripts/embedding_service.py --stats
```

**Memory Search:**
```bash
# Search memory files
cd ~/.openclaw/workspace && source venv/bin/activate
python scripts/memory_search.py "search query"

# With options
python scripts/memory_search.py "password manager" --top-k 5 --context 3

# JSON output for scripts
python scripts/memory_search.py "query" --json

# Force reindex
python scripts/memory_search.py "query" --reindex
```

### Performance Characteristics
- **First load:** 2-5 seconds (model initialization)
- **Subsequent embeddings:** 50-100ms per text
- **Memory indexing:** ~5 seconds for 595 chunks (22 files)
- **Search latency:** <1 second (after initial indexing)
- **Cache:** In-memory cache reduces duplicate embeddings

### Integration with OpenClaw
The local embedding service is available as standalone Python scripts that can be called:
- `scripts/embedding_service.py` - Generate embeddings for any text
- `scripts/memory_search.py` - Search MEMORY.md and memory/*.md files

These scripts use the virtual environment at `~/.openclaw/workspace/venv/` with all dependencies installed.

### Fallback Plan
If local embeddings fail (e.g., model corruption, PyTorch issues):
1. **Option 1:** Reinstall: `rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install sentence-transformers`
2. **Option 2:** Use Hugging Face API (requires API key):
   - Sign up at https://huggingface.co
   - Get API key from https://huggingface.co/settings/tokens
   - Set environment variable: `export HF_API_TOKEN=hf_xxx`
   - Modify scripts to use API instead of local model

### Why This Solution?
- **No quota limits:** Unlimited local embeddings (vs OpenAI quota exceeded)
- **Fast:** 100ms per embedding after model loads
- **Private:** All processing happens locally, no API calls
- **Reliable:** Works offline, no external dependencies
- **Cost-effective:** $0 ongoing cost

## Hugging Face API (TEMPORARY FALLBACK - March 20, 2026)

**Status:** ✅ Available as backup if local embeddings fail

**Why this exists:**
- Local Sentence Transformers is the primary solution (no quota issues, no API calls)
- Hugging Face API provides a fallback if local model becomes corrupted
- Evaluated and approved March 20, 2026 but not required for normal operation

### Configuration (If Needed)
- **Endpoint:** api-inference.huggingface.co
- **Model:** sentence-transformers/all-MiniLM-L6-v2
- **Setup:** https://huggingface.co/settings/tokens (free tier, generous limits)
- **Environment variable:** `HF_API_TOKEN=hf_xxx`
- **Latency:** 500-1000ms per request (slower than local, but reliable)
- **Cost:** Free tier sufficient for moderate usage

### When to Use Hugging Face API Fallback
1. **Only if local embeddings fail** with import errors
2. **If PyTorch becomes incompatible** with system updates
3. **For distributed systems** needing API-based embeddings

### Quick Fallback Setup
```bash
# 1. Create Hugging Face account (if needed)
# https://huggingface.co/signup

# 2. Get API token
# https://huggingface.co/settings/tokens (free tier)

# 3. Set environment variable
export HF_API_TOKEN=hf_xxx

# 4. Modify scripts to use API
# See hf_embedding_wrapper.py for implementation details
```

### Future Plan
- **Primary:** Keep using local Sentence Transformers (current setup)
- **Fallback:** Use Hugging Face API only if local model fails
- **Long-term:** Full local integration (already working, no action needed)

## Roblox Development Setup (March 21, 2026)

**Account & Configuration**
- **Roblox Username:** reillyrdai
- **API Key:** Stored securely in 1Password (OpenClaw Secrets vault)
- **Permissions:** universe-places (read/write), universe-datastores (read/write), universe-assets (write), universe-analytics (read)
- **Status:** ✅ ACTIVE - Ready for game creation & debugging

**Current Projects:**
1. **RPG Prototype** (in progress)
   - Status: Scripts added, MainGameScript syntax issue found (line 1 comment corruption)
   - Next: Fix syntax error, run F5 test
   - Location: Roblox Studio

2. **Future projects:** To be determined

**API Usage:**
- Create & manage games
- Manage DataStores (game data/player progress)
- Publish game updates
- Monitor game analytics
- Debug games via API

---

## Work Account (Leidos - March 21, 2026)

**New Position:**
- **Title:** Team Lead - Principal Software Engineer
- **Company:** Leidos (Airborne & Mission Solutions, Decision Advantage)
- **Email:** Robert.D.Reilly@Leidos.com
- **Phone:** +1 (703) 995-1838
- **Start Date:** March 21, 2026

**Organization:**
- **Local Workspace:** `~/.openclaw/workspace/leidos/` (CUI + sensitive content)
- **GitHub Repo:** [leidos-engineering-notes](https://github.com/rdreilly58/leidos-engineering-notes) (Private, unclassified only)
- **Structure:** Hybrid model with segregated security classifications
  - 🔴 Classified: SCIF/GFE only
  - 🟡 CUI: `leidos/cui/` (never GitHub)
  - 🟢 Unclassified: GitHub private repo (after sanitization)

**Daily Notes:** `~/.openclaw/workspace/leidos/memory/daily/`  
**Architecture Decisions:** `~/.openclaw/workspace/leidos/memory/decisions/` (ADRs)  
**Meeting Notes:** `~/.openclaw/workspace/leidos/memory/meetings/`  
**Knowledge Base:** `~/.openclaw/workspace/leidos/knowledge/`

---

## Gmail Account Migration (March 22, 2026 — ACTIVE)

**NEW PRIMARY GMAIL:** `reillyrd58@gmail.com`
- **Status:** ✅ ACTIVE — All work-related email uses this account NOW
- **Decision:** March 22, 5:29 AM EDT — Bob approved transition
- **Implementation:** All future email operations default to reillyrd58@gmail.com

**Account Status:**
- ✅ `reillyrd58@gmail.com` — Primary work account (ACTIVE)
- ✓ `rdreilly2010@gmail.com` — Legacy, stays for backward compatibility
- ✓ `robert@reillydesignstudio.com` — Primary design studio email

**Services Migrated to reillyrd58:**
- ✅ First Day & First Week Plan email (March 22, 5:29 AM)
- ✅ Future leadership planning emails (Sunday 3 AM plans)
- ✅ Future strategy review notifications
- ✅ All Leidos work-related communication

**gog Default:**
- When sending work email: `gog gmail send -a reillyrd58@gmail.com ...`
- For backward compat: older scripts may still reference rdreilly2010@gmail.com (update as encountered)

## Calendar Operations (gog)

**Primary Account:** `reillyrd58@gmail.com` (use for all new operations)

```bash
# Get calendar events
gog calendar list -a reillyrd58@gmail.com

# Get specific date
gog calendar list -a reillyrd58@gmail.com [filter options]

# JSON output for scripting
gog calendar list -a reillyrd58@gmail.com --json
```

**Legacy (rdreilly2010) still available if needed:**
```bash
gog calendar list -a rdreilly2010@gmail.com
```

**If authentication fails:**
- Run: `gog login reillyrd58@gmail.com`
- Follow the browser OAuth flow
- Token will be refreshed and stored

---

## PDF Generation (DEFAULT - March 22, TESTED & VERIFIED)

**Status:** ✅ PRODUCTION READY - Use WeasyPrint

### Quick Usage

**Markdown to PDF:**
```bash
bash ~/.openclaw/workspace/scripts/pdf-from-markdown.sh \
  document.md \
  -o output.pdf \
  -t "Document Title" \
  -a "Author Name"
```

**Direct WeasyPrint (HTML):**
```bash
weasyprint input.html output.pdf
```

### Why WeasyPrint Works

- ✅ Already installed: `/opt/homebrew/bin/weasyprint` (v68.1)
- ✅ Fast: ~2 seconds for 15KB Markdown → PDF
- ✅ Professional quality: HTML rendering
- ✅ No missing dependencies (unlike pandoc backends)
- ✅ Reliable: Used successfully multiple times (tested March 22)

### Pipeline

1. Markdown → HTML (pandoc)
2. HTML → PDF (weasyprint)
3. Metadata (title, author) preserved

### Scripts Available

- `scripts/pdf-from-markdown.sh` — Shell wrapper (recommended)
- `scripts/weasy-pdf.py` — Python wrapper (for programmatic use)

### Previous Attempts (DO NOT USE)

❌ ReportLab — fragile, complex
❌ Pandoc xelatex — backend not installed
❌ Pandoc wkhtmltopdf — backend not installed

---

## Email Operations (STANDARD METHOD - March 22, ACTIVE)

**Default for SENDING (Work-Related):** `gog gmail send -a reillyrd58@gmail.com ...`

```bash
# Simple email
gog gmail send \
  -a "reillyrd58@gmail.com" \
  --to "reillyrd58@gmail.com" \
  --subject "Subject Line" \
  --body-file <(cat file.txt)

# Multiple recipients
gog gmail send \
  -a "reillyrd58@gmail.com" \
  --to "user1@example.com,user2@example.com" \
  --subject "Subject" \
  --body-file <(echo "Body text")

# Direct text (no file)
gog gmail send \
  -a "reillyrd58@gmail.com" \
  --to "recipient@example.com" \
  --subject "Subject" \
  --body "Email body text here"
```

**Why:** Already authenticated, reliable, fast, work-related primary account (reillyrd58)

**Default for READING:** `gog gmail search` (Google CLI with Gmail API)

**Why:** 10-12x faster than Himalaya, already authenticated, supports combined filters

**Usage:**
```bash
# Find emails from sender
gog gmail search 'from:rdreilly2010@gmail.com'

# Find by subject
gog gmail search 'subject:OpenClaw iOS'

# Date range
gog gmail search 'after:2026-02-10 before:2026-03-12'

# Combined filters
gog gmail search 'from:rdreilly2010@gmail.com AND subject:briefing AND after:2026-03-10'

# Export to JSON for processing
gog gmail search 'QUERY' --json | jq '.threads[] | ...'
```

**Performance:**
- Himalaya: 30-60s per query (pagination-limited)
- gog: 2-5s per query (Gmail API)
- Notmuch: <1s (if local index needed)

**When to use alternatives:**
- Himalaya: Single email reads, interactive use
- gmail-send skill: Only if gog fails (requires app password)
- Notmuch: If doing heavy local analysis (set up with `notmuch new`)
- Python IMAP: For building comprehensive email database

---

## PDF Extraction from Emails

**Complete pipeline to read email with PDF attachment:**

```bash
# Step 1: Search for email and get thread ID
THREAD_ID=$(gog gmail search 'subject:"YOUR_SUBJECT"' --json | jq -r '.threads[0].id')

# Step 2: Read email content
gog gmail thread get $THREAD_ID

# Step 3: Download PDF attachment
cd /tmp && gog gmail thread attachments $THREAD_ID --download --out-dir /tmp

# Step 4: Extract PDF text
pdftotext /tmp/*_*.pdf - | less
```

**Quick commands:**
```bash
# Get thread ID for a search
gog gmail search 'subject:"App Store"' --json | jq -r '.threads[0].id'

# Download all attachments from thread
gog gmail thread attachments THREAD_ID --download --out-dir /tmp

# Extract and read PDF
pdftotext /tmp/FILE.pdf - | head -200
```

**Requirements:**
- `gog` (Google CLI) — already configured
- `jq` — for JSON parsing
- `pdftotext` — for PDF extraction (part of poppler-utils)

---

## Local LLM: Qwen 3.5 35B-A3B (MLX)

**Setup:** Installed March 14, 2026 at 10:25 AM EDT
- **Location:** `/Users/rreilly/models/qwen35b-4bit` (38GB)
- **Framework:** MLX (Apple Silicon optimized)
- **Python Environment:** `~/mlx-env` (venv)
- **Hardware:** M4 Mac mini (optimized for Neural Engine)

**Usage:**

```bash
# Activate MLX environment
source ~/mlx-env/bin/activate

# Interactive chat
python3 << 'EOF'
import os
from mlx_lm import generate, load

model_path = os.path.expanduser("~/models/qwen35b-4bit")
model, tokenizer = load(model_path)

# Chat loop
while True:
    prompt = input("You: ")
    if prompt.lower() in ['quit', 'exit']: break
    result = generate(model, tokenizer, prompt=prompt, max_tokens=512)
    print(f"Qwen: {result}\n")
EOF
```

**Performance Characteristics:**
- Intelligence: Comparable to Claude Sonnet 3.5 (83rd percentile on benchmarks)
- Speed: ~50-100 tokens/sec on M4 (sparse MoE, only 3B active params)
- Context: 262K native, extensible to 1M tokens
- Multimodal: Vision-language capable
- Coding: Strong on Next.js, Three.js, Python (79th percentile)

**Known Issues:**
- First load: 2-5 minutes (initializes weights for Neural Engine)
- Memory: Uses ~8-12GB active during inference
- OpenClaw integration: Not yet native (local-only for now)

**Next Steps:**
- Spawn local inference sessions via subagent with MLX backend
- Test on coding tasks vs. Claude/GPT-4 benchmarks
- Consider Ollama integration if GGUF version is needed

## Current Date & Time (Updated via session_status)

**Always run `session_status` to get the current date and time from the computer. Never infer or hardcode.**

Current: Saturday, March 14th, 2026 — 10:25 AM (America/New_York)

## BigQuery + GA4 Integration

**Setup Complete:** March 14, 2026, 11:35 AM EDT

### Connection Details
- **GCP Project ID:** `127601657025`
- **GA4 Property ID:** `526836321` (ReillyDesignStudio)
- **BigQuery Dataset:** `ga4_reillydesignstudio`
- **Dataset Location:** US
- **Export Type:** Real-time streaming (automatic)

### Status
✅ BigQuery API enabled
✅ Dataset created
⏳ Awaiting GA4 Admin linkage (manual step)

### Link GA4 to BigQuery (Manual Step in UI)

1. Go to: https://analytics.google.com
2. Admin (bottom left) → **Property** → **BigQuery Links**
3. Click **Link BigQuery Project**
4. Select project: `127601657025`
5. Choose dataset: `ga4_reillydesignstudio`
6. Authorize & confirm

**Note:** After linking, GA4 will take ~24 hours to begin streaming data.

### Query Examples (BigQuery SQL)

**Recent Events (Last 24h)**
```sql
SELECT
  event_timestamp,
  event_name,
  user_pseudo_id,
  page_location,
  page_referrer,
  device.category,
  geo.country
FROM `127601657025.ga4_reillydesignstudio.events_*`
WHERE _TABLE_SUFFIX = FORMAT_DATE('%Y%m%d', CURRENT_DATE()-1)
LIMIT 100
```

**Sessions by Device (Last 7 Days)**
```sql
SELECT
  device.category AS device,
  COUNT(DISTINCT user_pseudo_id) AS unique_users,
  COUNT(DISTINCT (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'session_id')) AS sessions,
  COUNT(*) AS events
FROM `127601657025.ga4_reillydesignstudio.events_*`
WHERE _TABLE_SUFFIX BETWEEN FORMAT_DATE('%Y%m%d', CURRENT_DATE()-7) 
  AND FORMAT_DATE('%Y%m%d', CURRENT_DATE()-1)
GROUP BY device
ORDER BY sessions DESC
```

**Top Pages (Last 7 Days)**
```sql
SELECT
  (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_location') AS page,
  COUNT(*) AS pageviews,
  COUNT(DISTINCT user_pseudo_id) AS users
FROM `127601657025.ga4_reillydesignstudio.events_*`
WHERE event_name = 'page_view'
  AND _TABLE_SUFFIX BETWEEN FORMAT_DATE('%Y%m%d', CURRENT_DATE()-7)
  AND FORMAT_DATE('%Y%m%d', CURRENT_DATE()-1)
GROUP BY page
ORDER BY pageviews DESC
LIMIT 20
```

**Conversion Funnel (Custom Events)**
```sql
SELECT
  event_name,
  COUNT(*) AS count,
  COUNT(DISTINCT user_pseudo_id) AS unique_users,
  ROUND(100.0 * COUNT(DISTINCT user_pseudo_id) / 
    (SELECT COUNT(DISTINCT user_pseudo_id) FROM 
      `127601657025.ga4_reillydesignstudio.events_*` 
     WHERE _TABLE_SUFFIX = FORMAT_DATE('%Y%m%d', CURRENT_DATE()-1)), 2) AS percent
FROM `127601657025.ga4_reillydesignstudio.events_*`
WHERE event_name IN ('page_view', 'click', 'form_submit', 'purchase')
  AND _TABLE_SUFFIX = FORMAT_DATE('%Y%m%d', CURRENT_DATE()-1)
GROUP BY event_name
ORDER BY count DESC
```

**User Behavior (Bounce Rate, Session Duration)**
```sql
WITH sessions AS (
  SELECT
    user_pseudo_id,
    (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'session_id') AS session_id,
    COUNT(*) AS events,
    MAX(event_timestamp) - MIN(event_timestamp) AS session_duration_ms
  FROM `127601657025.ga4_reillydesignstudio.events_*`
  WHERE _TABLE_SUFFIX = FORMAT_DATE('%Y%m%d', CURRENT_DATE()-1)
  GROUP BY user_pseudo_id, session_id
)
SELECT
  COUNT(*) AS total_sessions,
  ROUND(100.0 * COUNTIF(events = 1) / COUNT(*), 2) AS bounce_rate_percent,
  ROUND(AVG(session_duration_ms) / 1000, 2) AS avg_session_duration_seconds,
  AVG(events) AS avg_events_per_session
FROM sessions
```

### Streaming Real-Time Updates

Once GA4 is linked, data flows into BigQuery automatically:
- **Latency:** 10-30 minutes for real-time data
- **Historic data:** Backfilled from GA4 property creation date
- **Schema:** Auto-managed by GA4 (events_* tables)

### Scheduled Queries (Optional)

To export reports to GCS or email:

```bash
# Create scheduled query for daily report
bq query \
  --use_legacy_sql=false \
  --schedule="every day 09:00" \
  --destination_table=127601657025:ga4_reillydesignstudio.daily_summary \
  'SELECT CURRENT_DATE() as date, COUNT(*) as events FROM `127601657025.ga4_reillydesignstudio.events_*` WHERE _TABLE_SUFFIX = FORMAT_DATE("%Y%m%d", CURRENT_DATE()-1)'
```

## Location

**Default location:** Reston, VA

## Email

**Default email:** rdreilly2010@gmail.com

## Sudo Access & Permissions (March 16, 2026)

**Status:** ✅ ACTIVE - Momotaro has passwordless sudo for whitelisted commands

**Configuration:** `/etc/sudoers.d/momotaro`

**Whitelisted Commands (Passwordless):**
- `sudo softwareupdate` — System updates
- `sudo brew` / `sudo /opt/homebrew/bin/brew` — Package management & dev tools
- `sudo xcode-select` — Xcode tools
- `sudo launchctl` — Service management (launch agents, daemons)
- `sudo systemctl` — System service control
- `sudo dscacheutil` — DNS cache operations (debugging)
- `sudo log` — System logging
- `sudo diskutil` — Disk operations
- `sudo lsof` — File descriptor diagnostics
- `sudo clawhub` — Skill management

**What This Enables:**
- ✅ Automatic system updates + patching
- ✅ Install dev tools (Xcode, libraries, SDKs)
- ✅ Manage OpenClaw Gateway service
- ✅ Debug DNS, network, and system issues
- ✅ Install and manage skills from Clawhub

**Security Notes:**
- ✅ Whitelist-based (only these commands, nothing else)
- ✅ No password required (safe because scoped)
- ✅ Full audit trail in `/var/log/system.log`
- ⚠️ Never used for modifications outside whitelist
- ⚠️ Never used for file deletion or permission changes

**Testing:**
```bash
# Verify whitelist is active
sudo -l 2>/dev/null | grep NOPASSWD

# Or try a safe command
sudo dscacheutil -flushcache
```

---

## Orion Paper (Apple Neural Engine Research)

**Title:** Orion: Characterizing and Programming Apple's Neural Engine for LLM Training and Inference

**Link:** https://arxiv.org/pdf/2603.06728

**Authors:** Ramchand Kumaresan + team

**Significance:** 
- Detailed ANE architecture documentation
- First public detailed analysis of Apple Neural Engine
- Foundation for momo-kiji project
- Core reference for understanding ANE capabilities

**Key Topics:**
- ANE tensor operations
- Memory layout & optimization
- LLM training on ANE
- Performance characteristics
- Quantization strategies

**Status:** ✅ Referenced for momo-kiji development

---

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Google Tasks

**Status:** ✅ Integrated via gog CLI

### Your Task List
- **Task List ID:** `MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow`
- **Account:** rdreilly2010@gmail.com
- **List Name:** "ToDo"

### Quick Commands

**List all tasks:**
```bash
gog tasks list MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow -a rdreilly2010@gmail.com --plain
```

**List pending only:**
```bash
gog tasks list MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow -a rdreilly2010@gmail.com --json | jq '.tasks[] | select(.status == "needsAction")'
```

**Mark task done:**
```bash
gog tasks done MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow <TASK_ID> -a rdreilly2010@gmail.com
```

**Add new task:**
```bash
gog tasks add MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow -a rdreilly2010@gmail.com --title "Task title"
```

**Current tasks:** 15 total (11 pending, 4 completed)

See **skills/google-tasks/SKILL.md** for full documentation.

---

## AA Meetings

**Bob's regular AA meetings:**

| Meeting | Day/Time | Notes |
|---------|----------|-------|
| **GMG AA Meeting** | Daily, 8:00 AM EDT | Calendar: "GMG AA Meeting" (recurring daily) |
| **Tech host** | Thu 8:00 AM EDT | Bob hosts tech for GMG AA |
| **Life is Beautiful AA** | Sat 10:00 AM EDT | Calendar: "Life is Beautiful AA Meeting" |
| **St Annes AA** | Sun 7:00 PM EDT | Calendar: "St Annes AA meeting" |

**When Bob says "start my AA meeting":**
1. Search calendar for entries with "AA" in title
2. Find today's upcoming AA meeting (use `gog calendar list`)
3. Extract Zoom link from event description (gog calendar get EVENT_ID)
4. Open Zoom link in browser
5. Remember: This is a recurring pattern, repeat for future requests

**Zoom Links (extract from calendar event description):**
- GMG AA Meeting: [need to extract from event]
- Life is Beautiful: [need to extract from event]
- St Annes AA: [need to extract from event]

---

Add whatever helps you do your job. This is your cheat sheet.

## Zoom Meeting Links (Extracted from Calendar)

### GMG AA Meeting
- **Zoom Link:** https://us06web.zoom.us/j/89378046012?pwd=UmRzSDZKREQ4bTcrb2ZSUHVBK2trUT09
- **Meeting ID:** 893 7804 6012
- **Time:** Daily 8:00-9:00 AM EDT
- **When requested:** Open this link automatically

---

## GPU Inference Instance (March 17, 2026)

**Setup:** Always-on for 3-day test (March 17-19), then decide on cost model

### Instance Details
- **Type:** g5.2xlarge (8 vCPU, 32GB RAM, 1x A10G GPU)
- **Instance ID:** i-046d1154c0f4a9b2e
- **Region:** us-east-1 (us-east-1c)
- **Public IP:** 54.81.20.218
- **GPU:** NVIDIA A10G (24GB VRAM)
- **Storage:** 100GB root + 200GB /mnt/data (EBS)

### SSH Access
```bash
ssh -i ~/.ssh/vlm-deploy-key.pem ubuntu@54.81.20.218
```

### Models & Installation
- **Model:** Mistral-7B-Instruct-v0.1 (cached)
- **venv:** `/mnt/data/venv/`
- **Cache:** `/mnt/data/.cache/hf/models/`
- **Python:** `/mnt/data/venv/bin/python3`

### Performance Baseline (Mistral-7B)
- **Speed:** 27.98 tok/s (14.3x faster than CPU)
- **Load time:** ~105 seconds (first run, cached after)
- **Latency:** ~2.1 seconds for 3-token prompt
- **VRAM usage:** 23.7GB (headroom available)

### Cost
- **Monthly:** $980
- **Hourly:** $1.36
- **Per inference:** ~$0.05 for 500-token generation

### Health Check System
- **Quick check (@reboot):** `~/.openclaw/workspace/scripts/gpu-health-check-quick.sh` (~5s)
- **Full check (heartbeat):** `~/.openclaw/workspace/scripts/gpu-health-check-full.sh` (~90s)
- **Log:** `~/.openclaw/logs/gpu-health.log`
- **Cron:** `@reboot /Users/rreilly/.openclaw/workspace/scripts/gpu-startup-notify.sh`

### Usage Pattern
- **Simple tasks:** Use local Claude Haiku (weather, quick facts, emails)
- **Complex tasks:** SSH to GPU (articles, code, analysis, long-form writing)
- **Latency tolerance:** 2-3 minutes first request (acceptable for complex work)
- **Cached latency:** ~60 seconds (model stays in memory)

### Documentation
- **Skill guide:** `~/.openclaw/workspace/skills/gpu-health-check/SKILL.md`
- **Setup guide:** `~/.openclaw/workspace/docs/GPU_HEALTH_CHECK_SETUP.md`
- **HEARTBEAT.md:** Configured for periodic health checks

### Decision Points (March 20, 2026)
- **Keep always-on:** If using >3 times/day, worth $980/month
- **Switch to on-demand:** If <3 times/day, save money with per-request billing
- **Review metrics:** Check logs for actual usage patterns + latency tolerance

---

## Local Brother Printers (March 22, 2026)

**Status:** ✅ DISCOVERED & CONFIGURED

### Printers on Network

| Printer | Model | Type | Status | Notes |
|---------|-------|------|--------|-------|
| **Brother_HL_L2350DW_series** | HL-L2350DW | Laser (B&W) | ✅ Online | General printing |
| **Brother_MFC_L2700DW_series** | MFC-L2700DW | MFP (B&W) | ✅ Online | Default (has scanner) |

### Network Details

- **Connection:** Bonjour/mDNS (dnssd://)
- **CUPS Status:** Running
- **Default Printer:** Brother_MFC_L2700DW_series
- **Network:** Local network (192.168.x.x range)

### Quick Print Commands

**List printers:**
```bash
bash ~/.openclaw/workspace/skills/printer-brother/scripts/list-printers.sh
```

**Print a document:**
```bash
# To default printer
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh -f document.pdf

# To specific printer with options
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh \
  -f document.pdf \
  -p Brother_MFC_L2700DW_series \
  -c 2 --duplex --fit-to-page
```

**Test printer:**
```bash
bash ~/.openclaw/workspace/skills/printer-brother/scripts/test-printer.sh -p Brother_MFC_L2700DW_series
```

### Printer Skill Location

- **Skill:** `~/.openclaw/workspace/skills/printer-brother/`
- **SKILL.md:** Full documentation with all options
- **README.md:** Quick reference guide
- **Scripts:** list-printers.sh, print-file.sh, test-printer.sh

### Print Options

- `-f, --file FILE` — File to print (required)
- `-p, --printer PRINTER` — Target printer (default: system default)
- `-c, --copies N` — Number of copies
- `--duplex` — Print double-sided
- `--fit-to-page` — Scale to fit page
- `--landscape` — Landscape orientation
- `--grayscale` — Force grayscale
- `--status` — Show printer status only

### Supported File Formats

- ✅ PDF (native, best quality)
- ✅ PostScript (.ps)
- ✅ Text (.txt)
- ⚠️ Images (.jpg, .png) — convert to PDF first
- ⚠️ Office (.docx, .xlsx) — convert to PDF first

### Printer Capabilities

**Brother HL-L2350DW (Laser):**
- Resolution: 2400 x 600 dpi
- Speed: 32 ppm
- Color: Black & white only
- Best for: Documents, text

**Brother MFC-L2700DW (Multifunction):**
- Resolution: 2400 x 600 dpi
- Speed: 34 ppm
- Color: Black & white only
- Features: Print, scan, copy, fax, ADF
- Best for: Office documents, multi-page scanning

### Common Tasks

**Print 3 copies with duplex:**
```bash
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh \
  -f report.pdf \
  -p Brother_MFC_L2700DW_series \
  -c 3 --duplex
```

**Batch print all PDFs:**
```bash
for pdf in *.pdf; do
  bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh \
    -f "$pdf" \
    -p Brother_MFC_L2700DW_series
done
```

**Convert Markdown and print:**
```bash
pandoc document.md -o document.pdf
bash ~/.openclaw/workspace/skills/printer-brother/scripts/print-file.sh -f document.pdf
```

### Troubleshooting

**List all printers:**
```bash
lpstat -p
```

**Check printer status:**
```bash
lpstat -p -l
```

**View print queue:**
```bash
lpq -P Brother_MFC_L2700DW_series
```

**Cancel print job:**
```bash
lprm -P Brother_MFC_L2700DW_series JOB_ID
```

**Restart CUPS:**
```bash
sudo launchctl stop org.cups.cupsd
sudo launchctl start org.cups.cupsd
```

### Performance

- **Max jobs in queue:** 50+
- **Network latency:** <100ms (local network)
- **Print speed:** 32-34 ppm
- **Max file size:** 500 MB
- **Job timeout:** 30 minutes

### References

- **CUPS Docs:** https://www.cups.org/doc/
- **Brother Support:** https://support.brother.com/
- **macOS Printing:** https://support.apple.com/guide/mac-help/mh1607/

