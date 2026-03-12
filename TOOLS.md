# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

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
