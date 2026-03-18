# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

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
- **Last used:** March 18, 2026

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

## Calendar Operations (gog)

**Important:** Always use the `-a rdreilly2010@gmail.com` flag for calendar requests!

```bash
# Get calendar events
gog calendar list -a rdreilly2010@gmail.com

# Get specific date
gog calendar list -a rdreilly2010@gmail.com [filter options]

# JSON output for scripting
gog calendar list -a rdreilly2010@gmail.com --json
```

**If authentication fails:**
- Run: `gog login rdreilly2010@gmail.com`
- Follow the browser OAuth flow
- Token will be refreshed and stored

---

## Email Operations (STANDARD METHOD)

**Default method:** `gog gmail search` (Google CLI with Gmail API)

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
