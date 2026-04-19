#!/bin/bash
# email-utils.sh — Standardized email operations for OpenClaw
# 
# Purpose: Single source of truth for all email sending/searching
# Updated: March 22, 2026 (6:31 AM EDT)
# 
# Usage:
#   source ~/.openclaw/workspace/lib/email-utils.sh
#   send_email "subject" "body" "recipient@example.com" [--html] [--attach file.pdf]
#   search_email "from:bob@example.com AND subject:test"

set -uo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

# Primary email account (migrate all to this)
export MOMOTARO_EMAIL="${MOMOTARO_EMAIL:-rdreilly2010@gmail.com}"

# Logging
MOMOTARO_LOG_DIR="${MOMOTARO_LOG_DIR:-$HOME/.openclaw/logs}"
mkdir -p "$MOMOTARO_LOG_DIR"

# ============================================================================
# SEND EMAIL (Standardized)
# ============================================================================

send_email() {
    local subject="$1"
    local body="$2"
    local recipient="$3"
    local body_type="text"  # text or html
    declare -a attachments=()
    
    # Parse optional flags
    shift 3
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --html)
                body_type="html"
                shift
                ;;
            --attach)
                attachments+=("$2")
                shift 2
                ;;
            *)
                echo "❌ Unknown flag: $1" >&2
                return 1
                ;;
        esac
    done
    
    # Build gog command
    local cmd=(
        "gog" "gmail" "send"
        "-a" "$MOMOTARO_EMAIL"
        "--to" "$recipient"
        "--subject" "$subject"
    )
    
    # Add body (text or html)
    if [[ "$body_type" == "html" ]]; then
        cmd+=("--body-html")
    else
        cmd+=("--body")
    fi
    cmd+=("$body")
    
    # Add attachments (only if any exist)
    if [[ ${#attachments[@]} -gt 0 ]]; then
        for attach in "${attachments[@]}"; do
            if [[ ! -f "$attach" ]]; then
                echo "❌ Attachment not found: $attach" >&2
                return 1
            fi
            cmd+=("--attach" "$attach")
        done
    fi
    
    # Execute and log
    local log_file="$MOMOTARO_LOG_DIR/email-send-$(date +%Y%m%d).log"
    if "${cmd[@]}" 2>&1 | tee -a "$log_file"; then
        echo "✅ Email sent to $recipient" >&2
        return 0
    else
        echo "❌ Failed to send email to $recipient" >&2
        return 1
    fi
}

# ============================================================================
# SEARCH EMAIL (Standardized)
# ============================================================================

search_email() {
    local query="$1"
    local output_format="${2:-json}"  # json or text
    
    if [[ "$output_format" == "json" ]]; then
        gog gmail search "$query" -a "$MOMOTARO_EMAIL" --json 2>/dev/null || return 1
    else
        gog gmail search "$query" -a "$MOMOTARO_EMAIL" 2>/dev/null || return 1
    fi
}

# ============================================================================
# GET EMAIL (Read a specific email by ID)
# ============================================================================

get_email() {
    local message_id="$1"
    
    gog gmail get "$message_id" -a "$MOMOTARO_EMAIL" --json 2>/dev/null || return 1
}

# ============================================================================
# LIST EMAILS (Inbox, labels, etc)
# ============================================================================

list_emails() {
    local label="${1:-INBOX}"
    local max_results="${2:-10}"
    
    gog gmail list -a "$MOMOTARO_EMAIL" \
        --label "$label" \
        --max-results "$max_results" \
        --json 2>/dev/null || return 1
}

# ============================================================================
# MARK EMAIL AS READ
# ============================================================================

mark_email_read() {
    local message_id="$1"
    
    gog gmail modify "$message_id" -a "$MOMOTARO_EMAIL" \
        --add-labels UNREAD \
        2>/dev/null || return 1
}

# ============================================================================
# DELETE EMAIL
# ============================================================================

delete_email() {
    local message_id="$1"
    
    gog gmail delete "$message_id" -a "$MOMOTARO_EMAIL" 2>/dev/null || return 1
}

# ============================================================================
# HELPER: Validate email address
# ============================================================================

validate_email() {
    local email="$1"
    if [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

export -f send_email
export -f search_email
export -f get_email
export -f list_emails
export -f mark_email_read
export -f delete_email
export -f validate_email
