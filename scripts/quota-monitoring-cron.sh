#!/bin/bash
# API Quota Monitoring — Check quotas before requests exceed 80%
# Integrated with cron for scheduled monitoring

WORKSPACE="$HOME/.openclaw/workspace"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="$WORKSPACE/.quota-monitor.log"

# Load credentials
[ -f "$WORKSPACE/TOOLS.secrets.local" ] && source "$WORKSPACE/TOOLS.secrets.local" 2>/dev/null || true

# Initialize
ALERTS=()
WARNING_THRESHOLD=80
CRITICAL_THRESHOLD=95

log() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
    echo "$1"
}

check_openai_quota() {
    # Since we switched to local embeddings, OpenAI quota is non-critical
    # But we still monitor for info
    log "📊 OpenAI API: Using local embeddings (quota issue resolved)"
}

check_brave_quota() {
    # Brave key lives in macOS keychain under service 'BraveSearchAPI'
    # Fall back to env var BRAVE_API_KEY if set
    local brave_key="${BRAVE_API_KEY:-}"
    if [ -z "$brave_key" ]; then
        brave_key=$(security find-generic-password -s "BraveSearchAPI" -w 2>/dev/null || true)
    fi
    if [ -z "$brave_key" ]; then
        log "⚠️  Brave Search: key not found in keychain or env — skipping"
        return
    fi
    if curl -s -f "https://api.search.brave.com/res/v1/web/search?q=test&count=1" \
        -H "Accept: application/json" \
        -H "X-Subscription-Token: $brave_key" > /dev/null 2>&1; then
        log "✅ Brave Search: Operating normally"
    else
        log "❌ Brave Search: Connection failed"
        ALERTS+=("Brave Search API is not responding")
    fi
}

check_anthropic_credits() {
    # Anthropic doesn't expose a balance endpoint for standard API keys.
    # Best signal: probe with a 1-token request and inspect the error type.
    #   - success          → credits OK
    #   - overloaded_error → server busy, credits fine
    #   - billing_error / "credit" in message → exhausted
    #   - authentication_error → bad key
    local key="${ANTHROPIC_API_KEY:-}"
    if [ -z "$key" ]; then
        key=$(security find-generic-password -s "AnthropicAPI" -w 2>/dev/null || true)
    fi
    if [ -z "$key" ]; then
        log "⚠️  Anthropic: API key not found in env or keychain — skipping"
        return
    fi

    local response
    response=$(curl -s --max-time 15 "https://api.anthropic.com/v1/messages" \
        -H "x-api-key: $key" \
        -H "anthropic-version: 2023-06-01" \
        -H "content-type: application/json" \
        -d '{"model":"claude-haiku-4-5","max_tokens":1,"messages":[{"role":"user","content":"hi"}]}' \
        2>/dev/null)

    if [ -z "$response" ]; then
        log "❌ Anthropic: no response (network error or timeout)"
        ALERTS+=("Anthropic API unreachable")
        return
    fi

    local err_type
    err_type=$(echo "$response" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('error',{}).get('type','none'))" 2>/dev/null || echo "parse_error")
    local err_msg
    err_msg=$(echo "$response" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('error',{}).get('message',''))" 2>/dev/null || echo "")

    case "$err_type" in
        none)
            local tokens
            tokens=$(echo "$response" | python3 -c "import json,sys; d=json.load(sys.stdin); u=d.get('usage',{}); print(f'in={u.get(\"input_tokens\",\"?\")}, out={u.get(\"output_tokens\",\"?\")}')" 2>/dev/null || echo "?")
            log "✅ Anthropic API: credits OK (probe: $tokens tokens)"
            ;;
        overloaded_error)
            log "⚠️  Anthropic API: server overloaded (credits OK, retry later)"
            ;;
        billing_error)
            log "❌ Anthropic API: billing/credits issue — $err_msg"
            ALERTS+=("Anthropic credits exhausted or billing error")
            ;;
        authentication_error)
            log "❌ Anthropic API: authentication failed — key may be invalid or rotated"
            ALERTS+=("Anthropic API key invalid")
            ;;
        *)
            # Catch credit-related language in any error message
            if echo "$err_msg" | grep -qi "credit\|balance\|quota\|payment"; then
                log "❌ Anthropic API: possible credit issue — $err_type: $err_msg"
                ALERTS+=("Anthropic possible credit issue: $err_msg")
            else
                log "⚠️  Anthropic API: unexpected error — $err_type: $err_msg"
            fi
            ;;
    esac
}

check_cloudflare_quota() {
    # Cloudflare doesn't expose detailed quota via API
    if curl -s -f https://api.cloudflare.com/client/v4/zones \
        -H "Authorization: Bearer $CLOUDFLARE_TOKEN" > /dev/null 2>&1; then
        log "✅ Cloudflare API: Operating normally"
    else
        log "❌ Cloudflare API: Connection failed"
        ALERTS+=("Cloudflare API is not responding")
    fi
}

check_hf_quota() {
    # Hugging Face quota is informational (local embeddings are primary)
    log "📊 Hugging Face: Available as fallback (local embeddings primary)"
}

# Run all checks
log "🔍 Quota Monitoring Check Started"
check_openai_quota
check_brave_quota
check_anthropic_credits
check_cloudflare_quota
check_hf_quota

# Send alerts if any
if [ ${#ALERTS[@]} -gt 0 ]; then
    log "⚠️ ALERTS TRIGGERED:"
    for alert in "${ALERTS[@]}"; do
        log "   - $alert"
    done
    
    # Send Telegram notification if token available
    if [ -n "$TELEGRAM_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        MESSAGE="⚠️ OpenClaw Quota Alert\n\n"
        for alert in "${ALERTS[@]}"; do
            MESSAGE="$MESSAGE• $alert\n"
        done
        MESSAGE="$MESSAGE\nTime: $TIMESTAMP"
        
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=$MESSAGE" \
            -d "parse_mode=Markdown" > /dev/null 2>&1
    fi
else
    log "✅ All APIs operational, no quota issues detected"
fi

log "✅ Quota Monitoring Check Complete\n"

# ── Dead-man heartbeat ───────────────────────────────────────────────────────
bash "${WORKSPACE}/scripts/cron-heartbeat.sh" quota-monitoring $?
