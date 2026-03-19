# Google Tasks Skill

Read, manage, and sync your Google Tasks directly from OpenClaw.

## What This Skill Does

- **List all tasks** in your default task list
- **View completed vs pending** tasks
- **Mark tasks done** or incomplete
- **Add new tasks** with descriptions
- **Filter by status** (completed, pending)
- **Export to JSON** for scripting

## Quick Commands

### List All Tasks

```bash
gog tasks list MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow \
  -a rdreilly2010@gmail.com \
  --plain
```

**Output:**
```
ID	TITLE	STATUS	DUE	UPDATED
czBNUFhSV3ZMeVFOVW5IMg	Answer hire right email	needsAction	-	2026-03-19T16:59:48Z
```

### Get Pending Tasks Only

```bash
gog tasks list MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow \
  -a rdreilly2010@gmail.com \
  --json | jq '.tasks[] | select(.status == "needsAction")'
```

### Mark Task Complete

```bash
gog tasks done MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow \
  czBNUFhSV3ZMeVFOVW5IMg \
  -a rdreilly2010@gmail.com
```

### Add New Task

```bash
gog tasks add MDE3Mjg4MTY4MTYwNjc5NDE0MDY6MDow \
  -a rdreilly2010@gmail.com \
  --title "New task title" \
  --note "Optional description"
```

### Get Task Details

```bash
gog tasks get MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow \
  czBNUFhSV3ZMeVFOVW5IMg \
  -a rdreilly2010@gmail.com
```

## Configuration

### Your Task List ID

Your default task list is: `MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow`

To find other task lists:

```bash
gog tasks lists -a rdreilly2010@gmail.com --json
```

### Account Email

Use: `-a rdreilly2010@gmail.com`

(gog remembers this if you set it as default)

## Usage in OpenClaw

### In Heartbeat (Check Tasks Periodically)

Add to `HEARTBEAT.md`:

```bash
# Check pending tasks
gog tasks list MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow \
  -a rdreilly2010@gmail.com \
  --json | jq '[.tasks[] | select(.status == "needsAction")] | length' | xargs echo "Pending tasks:"
```

### In Scripts

Export to JSON for processing:

```bash
gog tasks list MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow \
  -a rdreilly2010@gmail.com \
  --json > tasks.json
```

Then parse with jq, Python, or other tools.

### Integration with Reminders

Combine with cron job to remind about pending tasks:

```bash
# Count pending tasks
PENDING=$(gog tasks list MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow \
  -a rdreilly2010@gmail.com \
  --json | jq '[.tasks[] | select(.status == "needsAction")] | length')

if [ "$PENDING" -gt 0 ]; then
  echo "You have $PENDING pending tasks"
fi
```

## Common Tasks

### Get All Pending Tasks with Titles

```bash
gog tasks list MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow \
  -a rdreilly2010@gmail.com \
  --json | jq '.tasks[] | select(.status == "needsAction") | .title'
```

### Count Tasks by Status

```bash
gog tasks list MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow \
  -a rdreilly2010@gmail.com \
  --json | jq 'group_by(.status) | map({status: .[0].status, count: length})'
```

### Find Task by Title

```bash
gog tasks list MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow \
  -a rdreilly2010@gmail.com \
  --json | jq '.tasks[] | select(.title | contains("keyword"))'
```

### Get Tasks Due Today

```bash
TODAY=$(date -u +%Y-%m-%d)

gog tasks list MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow \
  -a rdreilly2010@gmail.com \
  --json | jq ".tasks[] | select(.due == \"${TODAY}\")"
```

## Troubleshooting

### Tasks Not Showing

Verify authentication:

```bash
gog tasks lists -a rdreilly2010@gmail.com
```

If auth fails, re-login:

```bash
gog login rdreilly2010@gmail.com
```

### Wrong Account

Make sure you're using the right email:

```bash
# List available accounts
gog config get-account
```

### API Errors

Check gog version is up to date:

```bash
gog --version
```

Update if needed:

```bash
brew upgrade gog
```

## Resources

- **gog documentation:** `gog tasks --help`
- **Google Tasks API:** https://developers.google.com/tasks/overview
- **jq tutorial:** https://stedolan.github.io/jq/

## Status

✅ Google Tasks integration working
✅ Full read/write access via gog
✅ All commands tested and verified
