#!/bin/bash
# auto-update-system.sh — Scheduled system and package updates with health monitoring
#
# Purpose: Keep system, brew packages, and npm packages up to date
# Schedule: Daily at 2:00 AM EDT (configurable)
# Health check: Monitors success/failure, reports to Telegram
# Logging: Full logs to ~/.openclaw/logs/auto-update-*.log
#
# Updated: March 22, 2026 (6:31 AM EDT)

set -Eeuo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_NAME="$(basename "$0")"
LOG_DIR="$HOME/.openclaw/logs"
LOG_FILE="$LOG_DIR/auto-update-$(date +%Y%m%d-%H%M%S).log"
mkdir -p "$LOG_DIR"

# Rotate logs older than 30 days
find "$LOG_DIR" -name "auto-update-*.log" -mtime +30 -delete 2>/dev/null || true

# Load shared notification library
# shellcheck source=lib/notify.sh
source "$(dirname "$0")/lib/notify.sh"

# Timing
UPDATE_TIME="${UPDATE_TIME:-02:00}"  # 2:00 AM EDT
TIMEZONE="${TIMEZONE:-America/New_York}"

# Health check / notifications (optional — set in env to enable)
HEALTHCHECK_URL="${HEALTHCHECK_URL:-}"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"

# Features (control what updates)
UPDATE_MACOS="${UPDATE_MACOS:-true}"
UPDATE_BREW="${UPDATE_BREW:-true}"
UPDATE_BREW_CASK="${UPDATE_BREW_CASK:-true}"
UPDATE_NPM="${UPDATE_NPM:-true}"
UPDATE_PIP="${UPDATE_PIP:-false}"  # Disabled by default (virtualenv safety)

# Flags
DRY_RUN="${DRY_RUN:-false}"
SKIP_BREW="${SKIP_BREW:-false}"

# ============================================================================
# ERROR TRAP
# ============================================================================

trap '_notify_err_handler $LINENO' ERR

# ============================================================================
# LOGGING & REPORTING
# ============================================================================

log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARN: $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE"
}

report_status() {
    local status="$1"  # success, warning, failure
    local summary="$2"
    local details="${3:-}"
    
    case "$status" in
        success)
            emoji="✅"
            ;;
        warning)
            emoji="⚠️"
            ;;
        failure)
            emoji="❌"
            ;;
        *)
            emoji="ℹ️"
            ;;
    esac
    
    log_info "$emoji Auto-update $status: $summary"
    
    # Health check ping (if configured)
    if [[ "$status" == "success" ]]; then
        hc_success
    elif [[ "$status" == "failure" ]]; then
        hc_fail
    fi

    # Telegram notification on failure
    if [[ "$status" == "failure" ]]; then
        notify_telegram "❌ Auto-update failed: ${summary}"
    fi
}

# ============================================================================
# SYSTEM UPDATES (macOS)
# ============================================================================

update_macos() {
    log_info "Checking for macOS updates..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warn "DRY RUN: Skipping macOS updates"
        return 0
    fi
    
    local sw_output=""
    local updates_num=0
    sw_output=$(softwareupdate -l --include-config-data 2>&1) || true
    updates_num=$(echo "$sw_output" | grep -c "^\*") || updates_num=0

    if [[ "$updates_num" -gt 0 ]]; then
        log_info "Found $updates_num macOS updates"
        
        # Install all updates (requires sudo, but whitelisted)
        if sudo softwareupdate -i -a 2>&1 | tee -a "$LOG_FILE"; then
            log_info "✅ macOS updates installed"
            return 0
        else
            log_error "Failed to install macOS updates"
            return 1
        fi
    else
        log_info "No macOS updates available"
        return 0
    fi
}

# ============================================================================
# HOMEBREW UPDATES
# ============================================================================

update_brew() {
    log_info "Updating Homebrew packages..."
    
    if [[ "$SKIP_BREW" == "true" ]] || [[ "$UPDATE_BREW" != "true" ]]; then
        log_warn "Skipping Homebrew updates (disabled)"
        return 0
    fi
    
    if ! command -v brew &> /dev/null; then
        log_warn "Homebrew not installed"
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warn "DRY RUN: Checking outdated packages only"
        brew outdated | tee -a "$LOG_FILE"
        return 0
    fi
    
    # Update brew itself
    if brew update 2>&1 | tee -a "$LOG_FILE"; then
        log_info "Homebrew index updated"
    else
        log_error "Failed to update Homebrew index"
        return 1
    fi
    
    # Upgrade packages
    if brew upgrade 2>&1 | tee -a "$LOG_FILE"; then
        log_info "✅ Homebrew packages upgraded"
    else
        log_error "Failed to upgrade packages"
        # Attempt to fix common link issues
        if grep -q "brew link --overwrite" "$LOG_FILE"; then
            log_warn "Detected link issue. Attempting to force link pillow..."
            if brew link --overwrite pillow 2>&1 | tee -a "$LOG_FILE"; then
                log_info "✅ Forced link for pillow successful"
            else
                log_error "Failed to force link pillow"
                return 1
            fi
        else
            return 1
        fi
    fi
    
    # Upgrade casks (if enabled)
    if [[ "$UPDATE_BREW_CASK" == "true" ]]; then
        if brew upgrade --cask 2>&1 | tee -a "$LOG_FILE"; then
            log_info "✅ Homebrew casks upgraded"
        else
            log_warn "Failed to upgrade casks (non-fatal)"
        fi
    fi
    
    return 0
}

# ============================================================================
# NPM GLOBAL UPDATES
# ============================================================================

update_npm() {
    log_info "Updating npm global packages..."
    
    if [[ "$UPDATE_NPM" != "true" ]]; then
        log_warn "Skipping npm updates (disabled)"
        return 0
    fi
    
    if ! command -v npm &> /dev/null; then
        log_warn "npm not installed"
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warn "DRY RUN: Checking outdated packages only"
        npm outdated -g 2>/dev/null | tee -a "$LOG_FILE" || true
        return 0
    fi
    
    # Update npm itself first
    if npm install -g npm 2>&1 | tee -a "$LOG_FILE"; then
        log_info "npm updated"
    else
        log_warn "Failed to update npm (non-fatal)"
    fi
    
    # Update global packages
    if npm update -g 2>&1 | tee -a "$LOG_FILE"; then
        log_info "✅ npm global packages updated"
        return 0
    else
        log_error "Failed to update npm packages"
        return 1
    fi
}

# ============================================================================
# VERIFICATION & HEALTH CHECK
# ============================================================================

verify_updates() {
    log_info "Verifying system health after updates..."
    
    # Check if system is responsive
    if ! ping -c 1 8.8.8.8 > /dev/null 2>&1; then
        log_error "Network connectivity issue"
        return 1
    fi
    
    # Check critical commands
    for cmd in gog brew npm; do
        if command -v "$cmd" &> /dev/null; then
            log_info "✅ $cmd available"
        else
            log_error "❌ $cmd not found (may need update)"
            return 1
        fi
    done
    
    return 0
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    log_info "=========================================="
    log_info "Starting auto-update run"
    log_info "Time: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    log_info "=========================================="
    
    local failed_checks=0
    
    # Run updates
    if [[ "$UPDATE_MACOS" == "true" ]]; then
        update_macos || failed_checks=$((failed_checks + 1))
    fi
    
    if [[ "$UPDATE_BREW" == "true" ]]; then
        update_brew || failed_checks=$((failed_checks + 1))
    fi
    
    if [[ "$UPDATE_NPM" == "true" ]]; then
        update_npm || failed_checks=$((failed_checks + 1))
    fi
    
    # Verify (skip in dry-run — network/command checks don't apply)
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Skipping verify_updates"
    elif verify_updates; then
        log_info "✅ System health verified"
    else
        log_warn "⚠️ System health check failed (non-fatal)"
        failed_checks=$((failed_checks + 1))
    fi
    
    # Final report
    log_info "=========================================="
    if [[ $failed_checks -eq 0 ]]; then
        report_status "success" "All updates completed successfully" "Log: $LOG_FILE"
        log_info "✅ Auto-update completed successfully"
        exit 0
    else
        report_status "failure" "Some updates failed" "Check log: $LOG_FILE"
        log_error "❌ Auto-update completed with $failed_checks error(s)"
        exit 1
    fi
}

# ============================================================================
# DRY RUN MODE
# ============================================================================

if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN="true"
    log_info "Running in DRY RUN mode (no changes will be made)"
fi

# ============================================================================
# EXECUTE
# ============================================================================

main
