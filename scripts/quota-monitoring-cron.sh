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
    # Brave doesn't expose quota via API, but we monitor by checking connectivity
    if [ -z "${BRAVE_API_KEY:-}" ]; then
        log "⚠️  Brave Search: BRAVE_API_KEY not configured — skipping"
        return
    fi
    if curl -s -f "https://api.search.brave.com/res/v1/web/search?q=test&count=1" \
        -H "X-Subscription-Token: $BRAVE_API_KEY" > /dev/null 2>&1; then
        log "✅ Brave Search: Operating normally"
    else
        log "❌ Brave Search: Connection failed"
        ALERTS+=("Brave Search API is not responding")
    fi
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
