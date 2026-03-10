# Claude Code Integration Guide 🍑

## Setup Complete ✅

Your OpenClaw is now configured to use:
- **Claude Code** — All programming tasks (Anthropic)
- **GPT-4o** — All chat/analysis/general tasks (OpenAI)
- **Skills** — Specialized tasks (GA4, weather, etc.)

## How It Works

### For Coding Tasks
Use Claude Code directly:

```bash
# Quick one-shot
claude --permission-mode bypassPermissions --print "Write a Python function to calculate fibonacci"

# In a project directory
cd ~/my-project
claude --permission-mode bypassPermissions --print "Add TypeScript types to src/utils.js"
```

### For Chat/Analysis (Automatic)
Just ask Bob (or message me). Automatically routed to GPT-4o.

Examples:
- "Summarize this article"
- "What's the weather?"
- "Explain how this code works"
- "Write an email"

### For Specialized Tasks (Skill-based)
Use dedicated skills (no LLM):

```bash
# Analytics
bash ~/.openclaw/workspace/skills/daily-briefing/scripts/morning-briefing.sh --send

# Weather
weather "New York"

# Search Twitter/X
xurl search "query"
```

## Examples

### ✅ Claude Code
```
Task: Build a REST API
→ Use Claude Code
```

### ✅ GPT-4o
```
Task: Explain the API I built
→ Automatic (you just ask)
```

### ✅ Skill
```
Task: Get GA4 analytics
→ Use GA4 skill directly
```

## Current Config

**Default Model:** `openai/gpt-4o`
**Coding Agent:** `claude-code` (Anthropic)

Location: `~/.openclaw/config.yaml`

## Testing

Try asking me to:
1. **Build something** → I'll spawn Claude Code
2. **Analyze/chat** → I'll respond with GPT-4o
3. **Get data** → I'll use the appropriate skill

Example workflow:
```
You: "Build a todo app in React"
Me:  [spawns Claude Code]
     ↓
Claude Code: [builds the app]
     ↓
Me: "The app is ready at ~/todo-app"

You: "How does it work?"
Me:  [uses GPT-4o to explain]
     ↓
GPT-4o: [explains the architecture]
```

---

## Notes

- Claude Code requires `--permission-mode bypassPermissions` (no interactive prompts)
- GPT-4o is the default for all non-coding tasks
- Skills don't use LLMs (they're API/command-based)
- Your preference is: **Anthropic (coding only), NOT Anthropic (everything else)**

Let me know if you want to adjust routing! 🍑
