# Codex Integration Setup Guide

## Step 1: Get OpenAI API Key

### Create OpenAI Account (if you don't have one)
1. Go to: https://platform.openai.com/account/api-keys
2. Sign up with email or existing account
3. Verify your account

### Generate API Key
1. Go to: https://platform.openai.com/account/api-keys
2. Click **"+ Create new secret key"**
3. Name it: "Momotaro Codex Backup"
4. Copy the key (you'll only see it once!)
5. Store it securely

**Important:** Don't share this key. Treat it like a password.

---

## Step 2: Add to OpenClaw Configuration

Once you have your API key, I'll add it to your OpenClaw config:

```bash
# This will be added to your OpenClaw config
export OPENAI_API_KEY="sk-..."
```

---

## Step 3: Test Codex Integration

After setup, we'll test with a simple coding task:

```bash
# Test command
sessions_spawn runtime="acp" agentId="codex" task="Create a simple Swift function that returns 'Hello, World!'"
```

---

## Step 4: Create Fallback Routing Script

I'll create a helper script that:
- Checks if Claude Code is available
- Falls back to Codex if not
- Falls back to Opus if Codex unavailable
- Logs which model was used

---

## Cost & Usage

### Pricing
- **Codex:** ~$0.01-0.03 per request for average file
- **Example:** 100 coding tasks/month = $1-3/month
- **Estimated budget:** $10-20/month for active development

### Rate Limits
- Codex: Generous limits (thousands per day)
- No blocking expected for your use case

### Monitoring
- We'll set up logging to track:
  - Which backup model was used
  - When Claude Code was unavailable
  - Cost per task

---

## Setup Checklist

- [ ] OpenAI account created
- [ ] API key generated
- [ ] API key added to OpenClaw config
- [ ] Codex tested with sample task
- [ ] Fallback routing script created
- [ ] Documentation updated
- [ ] Ready for production use

---

## Next Steps

1. **You:** Create OpenAI account and get API key
2. **Me:** Add key to OpenClaw config
3. **Me:** Test Codex with Momotaro-iOS project
4. **Me:** Create fallback routing script
5. **You:** Review and approve setup

---

## Questions?

- **How do I pay?** Credit card on OpenAI account. You set a usage limit to prevent surprises.
- **Is it secure?** Yes, API keys are encrypted in OpenClaw.
- **Can I disable it?** Yes, anytime. Just remove the key.
- **What if I don't use it?** No charges (pay-per-use model).

---

Ready to proceed? You can:

1. **Get your API key now** and paste it here
2. **Let me know when you're ready** and I'll walk you through it
3. **Skip this step** and use Opus as fallback instead (free but slower)

What's your preference? 🍑
