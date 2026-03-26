# OpenRouter Setup Guide (Optional Optimization)

**Status:** Deferred (not required for Tier 2, but recommended for cost savings)  
**Benefit:** 40-60% cost reduction via intelligent model selection  
**Effort:** 10 minutes setup  
**Dependencies:** OpenRouter account (free)

---

## Why OpenRouter?

**Current Setup (After Tier 2):**
- Primary: Anthropic Claude Opus (powerful, ~$0.015/1K tokens)
- Fallback: Anthropic Claude Haiku (fast, ~$0.001/1K tokens)
- Cost: $50-100/month for typical usage

**With OpenRouter Auto:**
- Primary: OpenRouter's Auto Model (intelligent routing)
- Routes simple tasks → cheaper models (Haiku, Mistral, etc.)
- Routes complex tasks → powerful models (Opus, GPT-4, etc.)
- Cost: $20-30/month (50-60% reduction)

---

## Step-by-Step Setup

### 1. Create OpenRouter Account (2 min)

Visit: **https://openrouter.ai**

- Click "Sign Up" (top right)
- Sign up with GitHub or email
- Verify email (if needed)
- Accept terms

**Result:** Free account with access to 100+ models

### 2. Get Your API Key (1 min)

1. Go to: **https://openrouter.ai/keys**
2. Click "Create Key" (if first time)
3. Copy the key (looks like: `sk_live_...`)
4. **Save it securely** — you'll need it next

### 3. Configure OpenClaw (5 min)

**Option A: Using Environment Variable (Easiest)**

```bash
# Add to ~/.zshrc or ~/.bash_profile
export OPENROUTER_API_KEY='sk_live_YOUR_KEY_HERE'

# Source the file
source ~/.zshrc
```

**Option B: Using Credentials File (Recommended)**

```bash
# Create credentials file
mkdir -p ~/.openclaw/credentials
echo 'sk_live_YOUR_KEY_HERE' > ~/.openclaw/credentials/openrouter

# Lock it down
chmod 600 ~/.openclaw/credentials/openrouter

# Verify
cat ~/.openclaw/credentials/openrouter
```

**Option C: Using OpenClaw Config**

```bash
# Add auth profile
openclaw config set auth.profiles.openrouter:default '{"provider": "openrouter", "mode": "token", "token": "sk_live_..."}'

# Or via interactive setup
openclaw onboard
# Select "OpenRouter" when prompted
```

### 4. Switch to OpenRouter Auto Model

```bash
# Set primary model to OpenRouter Auto
openclaw config set agents.defaults.model.primary openrouter/openrouter/auto

# Verify
grep '"primary"' ~/.openclaw/openclaw.json
# Should show: "primary": "openrouter/openrouter/auto"
```

### 5. Restart Gateway & Test

```bash
# Restart gateway
openclaw gateway restart

# Wait 10 seconds for startup
sleep 10

# Test simple task (should use cheap model)
# "What's the current time?"

# Test complex task (should use powerful model)
# "Analyze the OpenClaw setup and recommend improvements"

# Check logs
tail -50 ~/.openclaw/logs/gateway.log | grep -i "model\|openrouter"
```

---

## Verification

### Check If OpenRouter Is Active

```bash
# Method 1: Check config
grep '"primary"' ~/.openclaw/openclaw.json

# Expected: "primary": "openrouter/openrouter/auto"

# Method 2: Check logs
tail -100 ~/.openclaw/logs/gateway.log | grep openrouter

# Expected: Should see openrouter model selection
```

### Test Model Selection

**Simple Task (should use cheap model):**
```
User: "What's 2+2?"
Expected: Fast response, Haiku or Mistral
Cost: ~$0.0001
```

**Complex Task (should use powerful model):**
```
User: "Design a microservices architecture for a startup"
Expected: Detailed response, Opus or GPT-4
Cost: ~$0.01
```

### Monitor Costs

1. Go to: **https://openrouter.ai/activity**
2. You'll see:
   - Model selection breakdown
   - Cost per request
   - Total usage this month

---

## Troubleshooting

### Issue: "OpenRouter credentials not found"

**Check:**
```bash
# Method 1: Environment variable
echo $OPENROUTER_API_KEY

# Method 2: Credentials file
cat ~/.openclaw/credentials/openrouter

# Method 3: Config file
grep openrouter ~/.openclaw/openclaw.json
```

**Fix:**
```bash
# Re-add the key
echo 'sk_live_YOUR_KEY' > ~/.openclaw/credentials/openrouter
chmod 600 ~/.openclaw/credentials/openrouter

# Restart gateway
openclaw gateway restart
```

### Issue: "OpenRouter API returned 401 Unauthorized"

**Cause:** Invalid API key

**Fix:**
1. Verify key at https://openrouter.ai/keys
2. Copy fresh key (don't include quotes)
3. Update: `echo 'sk_live_...' > ~/.openclaw/credentials/openrouter`
4. Restart gateway

### Issue: "Still using Opus instead of Auto"

**Check:**
```bash
# Verify config was updated
grep '"primary"' ~/.openclaw/openclaw.json

# Should show: openrouter/openrouter/auto
```

**If not updated:**
```bash
# Set again
openclaw config set agents.defaults.model.primary openrouter/openrouter/auto

# Verify
openclaw config get agents.defaults.model.primary
```

**Restart:**
```bash
openclaw gateway restart
sleep 10
```

### Issue: "OpenRouter is slow"

**Explanation:** OpenRouter aggregates multiple providers, adding 100-200ms latency

**Solutions:**
1. Accept the latency (usually unnoticeable for user)
2. Use direct Anthropic (faster, no aggregation)
3. Configure regional routing (advanced)

---

## Cost Comparison

### Before (Tier 2 - Current)
| Task | Model | Speed | Cost |
|------|-------|-------|------|
| Simple | Opus | 1-2s | $0.015/1K |
| Complex | Opus | 1-2s | $0.015/1K |
| Monthly | - | - | $50-100 |

### After (With OpenRouter Auto)
| Task | Model | Speed | Cost |
|------|-------|-------|------|
| Simple | Haiku/Mistral | 0.5-1s | $0.0001/1K |
| Complex | Opus/GPT-4 | 1-2s | $0.01/1K |
| Monthly | - | - | $20-30 |

**Savings: 50-60% ($20-70/month)**

---

## Advanced: Custom Routing

OpenRouter supports custom routing rules. For example:

```json
{
  "routing": {
    "simple_keywords": ["weather", "time", "status", "what is"],
    "simple_model": "openai/gpt-3.5-turbo:free",
    "complex_model": "openrouter/openrouter/auto"
  }
}
```

This would:
- Route simple tasks to free GPT-3.5
- Route complex tasks to OpenRouter Auto
- **Result:** Nearly $0 cost for simple tasks

---

## When to Set Up OpenRouter

**Do it now if:**
- You want maximum cost savings
- You're comfortable with 100-200ms latency
- You plan to use OpenClaw heavily

**Do it later if:**
- Current costs acceptable
- Want to focus on other features
- Prefer guaranteed latency

**Skip it if:**
- Using Anthropic-only models (direct)
- Cost not a concern
- Need absolute lowest latency

---

## Support

**Issues with OpenRouter?**
- Docs: https://openrouter.ai/docs
- Status: https://status.openrouter.ai
- Support: https://openrouter.ai/support

**Issues with OpenClaw integration?**
- Check logs: `tail -100 ~/.openclaw/logs/gateway.log`
- Run doctor: `openclaw doctor --fix`
- See: https://docs.openclaw.ai/troubleshooting

---

## Summary

**Current State (Tier 2 Implemented):**
- ✅ Gateway: Loopback + TLS secured
- ✅ API Monitoring: 2x daily checks
- ✅ Cron Consolidation: 17 → 14 jobs
- ✅ Model: Anthropic Opus (stable)
- ⏳ OpenRouter: Optional enhancement

**To Activate OpenRouter Auto:**
1. Sign up at openrouter.ai (free)
2. Get API key from openrouter.ai/keys
3. Save to ~/.openclaw/credentials/openrouter
4. Run: `openclaw config set agents.defaults.model.primary openrouter/openrouter/auto`
5. Restart: `openclaw gateway restart`

**Expected Result:** 50-60% cost reduction via intelligent model selection

---

**Setup when ready. This guide will be here.**
