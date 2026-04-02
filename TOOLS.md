# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

**Note:** Detailed configs for email, printers, AA meetings, Leidos work, and API keys
are in dedicated `memory/` files for better search. This file has active tool references only.

---

## ReillyDesignStudio Deployment (March 22, 2026)

**Deployment Platform:** Vercel (primary)
- Auto-deploys from `main` branch pushes
- Build time: ~4-5 minutes from push to live
- URL: https://reillydesignstudio.com
- Domain: reillydesignstudio.com (via Cloudflare)
- Framework: Next.js 16
- **Commit Author:** MUST be `robert.reilly@peraton.com` (Vercel requirement)

---

## Roblox Development Setup (March 21, 2026)

- **Username:** reillyrdai
- **API Key:** Stored in 1Password (OpenClaw Secrets vault)
- **Permissions:** universe-places (read/write), universe-datastores (read/write), universe-assets (write), universe-analytics (read)
- **Status:** ✅ ACTIVE
- **Automation:** `scripts/roblox-full-automation.sh` (GitHub → Studio → test → report)

---

## Calendar Operations (gog)

**Primary Account:** `reillyrd58@gmail.com`

```bash
gog calendar list -a reillyrd58@gmail.com
gog calendar list -a reillyrd58@gmail.com --json
```

**Legacy:** `gog calendar list -a rdreilly2010@gmail.com`

**If auth fails:** `gog auth login -a reillyrd58@gmail.com`

---

## Google Tasks

**Status:** ✅ Integrated via gog CLI

- **Task List ID:** `MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow`
- **Account:** rdreilly2010@gmail.com

```bash
# List pending
gog tasks list MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow -a rdreilly2010@gmail.com --json | jq '.tasks[] | select(.status == "needsAction")'

# Add task
gog tasks add MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow -a rdreilly2010@gmail.com --title "Task title"

# Mark done
gog tasks done MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow <TASK_ID> -a rdreilly2010@gmail.com
```

---

## PDF Generation (WeasyPrint)

**Status:** ✅ PRODUCTION READY

```bash
# Markdown to PDF
bash ~/.openclaw/workspace/scripts/pdf-from-markdown.sh document.md -o output.pdf -t "Title" -a "Author"

# Direct HTML to PDF
weasyprint input.html output.pdf
```

Pipeline: Markdown → HTML (pandoc) → PDF (weasyprint)

---

## PDF Extraction from Emails

```bash
# Get thread ID
THREAD_ID=$(gog gmail search 'subject:"YOUR_SUBJECT"' --json | jq -r '.threads[0].id')

# Download attachments
cd /tmp && gog gmail thread attachments $THREAD_ID --download --out-dir /tmp

# Extract text
pdftotext /tmp/FILE.pdf - | head -200
```

---

## Sudo Access & Permissions

**Status:** ✅ ACTIVE - Passwordless sudo for whitelisted commands
**Config:** `/etc/sudoers.d/momotaro`

**Whitelisted:** softwareupdate, brew, xcode-select, launchctl, systemctl, dscacheutil, log, diskutil, lsof, clawhub

Use sudo freely — it's whitelisted and expected. Don't ask permission.

---

## Orion Paper (Apple Neural Engine Research)

- **Title:** Orion: Characterizing and Programming Apple's Neural Engine for LLM Training and Inference
- **Link:** https://arxiv.org/pdf/2603.06728
- **Significance:** First detailed public ANE architecture documentation
- **Status:** ✅ Referenced for momo-kiji development

---

## Current Date & Time

**Always run `session_status` to get current date/time. Never infer or hardcode.**

---

## Location

**Default location:** Reston, VA

---

## Default Email

**Default email:** rdreilly2010@gmail.com (sender) / reillyrd58@gmail.com (receiving/work)

---

## What Goes Here

Things like camera names, SSH hosts, preferred voices, speaker names, device nicknames — anything environment-specific. Detailed configs go in `memory/` files for searchability.

---

## BigQuery + GA4 (Reference)

- **GCP Project ID:** `127601657025`
- **GA4 Property ID:** `526836321` (ReillyDesignStudio)
- **Dataset:** `ga4_reillydesignstudio`
- **Status:** ⏳ Awaiting GA4 Admin linkage (manual step at analytics.google.com)
