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

Add whatever helps you do your job. This is your cheat sheet.
