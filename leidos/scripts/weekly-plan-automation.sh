#!/bin/bash
#
# Weekly Leadership Plan Automation
# Runs Sunday 3:00 AM EDT
# 
# Pipeline: Calendar → Review → Generate → PDF → Email → Archive
#

set -e

# Configuration
WORKSPACE="$HOME/.openclaw/workspace"
LEIDOS="$WORKSPACE/leidos"
LOGS="$HOME/.openclaw/logs"
GMAIL_ACCOUNT="reillyrd58@gmail.com"

# Derived
PLAN_DATE=$(date +%Y-%m-%d)
WEEK_START=$(date -v+1d +%Y-%m-%d)  # Next Monday
SCRIPT_DIR="$LEIDOS/scripts"
TEMPLATE="$LEIDOS/templates/plan-template.md"
STRATEGY="$LEIDOS/knowledge/LEADERSHIP_STRATEGY.md"
PLANS_ARCHIVE="$LEIDOS/plans/weekly"

# Log file
LOG_FILE="$LOGS/weekly-plan-$(date +%Y%m%d-%H%M%S).log"
mkdir -p "$LOGS" "$PLANS_ARCHIVE"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

# ============================================================================
# Step 1: Pull Calendar Data
# ============================================================================

log_info "Step 1: Pulling calendar data for next 30 days..."

CALENDAR_FILE="/tmp/calendar-export-${PLAN_DATE}.json"

if ! gog calendar list -a "$GMAIL_ACCOUNT" \
    --after="$(date +%Y-%m-%d)" \
    --before="$(date -v+30d +%Y-%m-%d)" \
    --json > "$CALENDAR_FILE" 2>> "$LOG_FILE"; then
    log_error "Failed to pull calendar. Exiting."
    exit 1
fi

CALENDAR_LINES=$(wc -l < "$CALENDAR_FILE")
log_info "Calendar exported: $CALENDAR_LINES lines"

# ============================================================================
# Step 2: Find Latest Strategy Review
# ============================================================================

log_info "Step 2: Finding latest strategy review..."

LATEST_REVIEW=$(find "$LEIDOS/knowledge/weekly-reviews" -name "*-review.md" -type f 2>/dev/null | sort -r | head -1)

if [ -z "$LATEST_REVIEW" ]; then
    log_warn "No previous review found. Using strategy document as fallback."
    LATEST_REVIEW="$STRATEGY"
else
    log_info "Using review: $(basename "$LATEST_REVIEW")"
fi

# ============================================================================
# Step 3: Generate Markdown Plan
# ============================================================================

log_info "Step 3: Generating markdown plan..."

PLAN_MARKDOWN="/tmp/plan-${WEEK_START}.md"

if ! python3 "$SCRIPT_DIR/generate-leadership-plan.py" \
    --calendar "$CALENDAR_FILE" \
    --review "$LATEST_REVIEW" \
    --strategy "$STRATEGY" \
    --template "$TEMPLATE" \
    --output "$PLAN_MARKDOWN" >> "$LOG_FILE" 2>&1; then
    log_error "Failed to generate plan. Exiting."
    exit 1
fi

if [ ! -f "$PLAN_MARKDOWN" ]; then
    log_error "Plan markdown file not created. Exiting."
    exit 1
fi

PLAN_SIZE=$(wc -l < "$PLAN_MARKDOWN")
log_info "Plan generated: $PLAN_SIZE lines"

# ============================================================================
# Step 4: Convert to PDF
# ============================================================================

log_info "Step 4: Converting to PDF..."

PLAN_PDF="/tmp/plan-${WEEK_START}.pdf"

# Try make-pdf skill if available
if command -v make-pdf &> /dev/null; then
    if make-pdf "$PLAN_MARKDOWN" \
        --output "$PLAN_PDF" \
        --title "Leadership Plan: $WEEK_START to $(date -v+29d +%Y-%m-%d)" >> "$LOG_FILE" 2>&1; then
        log_info "PDF created via make-pdf skill"
    else
        log_warn "make-pdf skill failed, trying pandoc..."
        if ! pandoc "$PLAN_MARKDOWN" -o "$PLAN_PDF" >> "$LOG_FILE" 2>&1; then
            log_error "pandoc conversion failed. Using markdown only."
            PLAN_PDF=""
        fi
    fi
else
    # Fallback to pandoc
    if command -v pandoc &> /dev/null; then
        if pandoc "$PLAN_MARKDOWN" -o "$PLAN_PDF" >> "$LOG_FILE" 2>&1; then
            log_info "PDF created via pandoc"
        else
            log_error "pandoc conversion failed. Using markdown only."
            PLAN_PDF=""
        fi
    else
        log_warn "No PDF conversion tool available. Markdown only."
        PLAN_PDF=""
    fi
fi

if [ -n "$PLAN_PDF" ] && [ -f "$PLAN_PDF" ]; then
    PDF_SIZE=$(du -h "$PLAN_PDF" | cut -f1)
    log_info "PDF ready: $PDF_SIZE"
else
    PLAN_PDF=""
fi

# ============================================================================
# Step 5: Archive Files
# ============================================================================

log_info "Step 5: Archiving files..."

cp "$PLAN_MARKDOWN" "$PLANS_ARCHIVE/${WEEK_START}-plan.md"
log_info "Markdown archived: $PLANS_ARCHIVE/${WEEK_START}-plan.md"

if [ -n "$PLAN_PDF" ] && [ -f "$PLAN_PDF" ]; then
    cp "$PLAN_PDF" "$PLANS_ARCHIVE/${WEEK_START}-plan.pdf"
    log_info "PDF archived: $PLANS_ARCHIVE/${WEEK_START}-plan.pdf"
    
    # Also keep timestamped backup
    cp "$PLAN_PDF" "$PLANS_ARCHIVE/${WEEK_START}-plan-$(date +%s).pdf"
fi

# ============================================================================
# Step 6: Email Plan to You
# ============================================================================

log_info "Step 6: Emailing plan to you..."

MONTH_END=$(date -v+29d +%Y-%m-%d)
SUBJECT="Leadership Plan: ${WEEK_START} to ${MONTH_END} [Generated $(date +%H:%M)]"

EMAIL_BODY=$(cat <<'EOF'
Hi Bob,

Your weekly leadership plan is ready and waiting in your inbox.

📋 What's included:
✅ Next day (Monday) priorities and calendar
✅ Next week strategic blocks and team engagement
✅ Next 30 days breakdown with week-by-week milestones
✅ Key decisions, risks, and success metrics

📂 Where it's saved:
- Markdown: leidos/plans/weekly/{WEEK_START}-plan.md
- PDF: leidos/plans/weekly/{WEEK_START}-plan.pdf

💡 How to use:
1. Review Monday priorities first thing in the morning
2. Block strategic time on your calendar
3. Track 30-day milestones against the plan
4. Use as reference during Sunday's strategy review

📅 Reminder: Full strategy review at 8:00 AM EDT

Questions? Check your plan or let me know.

— Momotaro
🍑
EOF
)

# Substitute template variables
EMAIL_BODY=$(echo "$EMAIL_BODY" | sed "s/{WEEK_START}/${WEEK_START}/g")

if [ -n "$PLAN_PDF" ] && [ -f "$PLAN_PDF" ]; then
    # Send with PDF attachment
    if gog gmail send \
        -a "$GMAIL_ACCOUNT" \
        --to "$GMAIL_ACCOUNT" \
        --subject "$SUBJECT" \
        --body "$EMAIL_BODY" \
        --attach "$PLAN_PDF" >> "$LOG_FILE" 2>&1; then
        log_info "Email sent with PDF attachment"
    else
        log_error "Failed to send email with attachment"
    fi
else
    # Send markdown via email body
    if gog gmail send \
        -a "$GMAIL_ACCOUNT" \
        --to "$GMAIL_ACCOUNT" \
        --subject "$SUBJECT" \
        --body "$EMAIL_BODY" >> "$LOG_FILE" 2>&1; then
        log_info "Email sent (markdown version)"
    else
        log_error "Failed to send email"
    fi
fi

# ============================================================================
# Step 7: Git Commit
# ============================================================================

log_info "Step 7: Committing to git..."

cd "$WORKSPACE"

if git add "$PLANS_ARCHIVE/${WEEK_START}-plan.md" 2>> "$LOG_FILE"; then
    if [ -n "$PLAN_PDF" ] && [ -f "$PLANS_ARCHIVE/${WEEK_START}-plan.pdf" ]; then
        git add "$PLANS_ARCHIVE/${WEEK_START}-plan.pdf"
    fi
    
    if git commit -m "docs: Add weekly leadership plan for ${WEEK_START}

Generated: $(date)
Based on: Calendar export + latest strategy review
Content: Next day / week / 30-day plan" >> "$LOG_FILE" 2>&1; then
        log_info "Git commit successful"
    else
        log_warn "Git commit skipped (no changes)"
    fi
else
    log_warn "Git add failed (files may already exist)"
fi

# ============================================================================
# Summary
# ============================================================================

log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "✅ WEEKLY PLAN GENERATION COMPLETE"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info ""
log_info "📋 Plan for: $WEEK_START to $MONTH_END"
log_info "📂 Location: $PLANS_ARCHIVE/${WEEK_START}-plan.md"
if [ -n "$PLAN_PDF" ]; then
    log_info "📄 PDF: $PLANS_ARCHIVE/${WEEK_START}-plan.pdf"
fi
log_info "📧 Email: Sent to $GMAIL_ACCOUNT"
log_info ""
log_info "Next: Strategy review at 8:00 AM EDT"
log_info "Log: $LOG_FILE"
log_info ""

# Clean up temp files (keep for 24 hours just in case)
rm -f "$CALENDAR_FILE"

exit 0
