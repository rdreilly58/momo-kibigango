#!/bin/bash
# print-file.sh — Print files to Brother printers with flexible options

set -uo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

FILE=""
PRINTER=""
COPIES=1
DUPLEX=false
FIT_TO_PAGE=false
LANDSCAPE=false
GRAYSCALE=false
STATUS_ONLY=false

# ============================================================================
# FUNCTIONS
# ============================================================================

show_help() {
    cat << 'EOF'
Usage: bash print-file.sh [OPTIONS]

OPTIONS:
  -f, --file FILE              PDF or text file to print (required unless --status)
  -p, --printer PRINTER        Printer name (default: system default)
  -c, --copies N               Number of copies (default: 1)
  --duplex                     Print double-sided (if supported)
  --fit-to-page                Scale to fit page
  --landscape                  Landscape orientation
  --grayscale                  Force grayscale
  --status                     Show printer status only
  -h, --help                   Show this help message

EXAMPLES:
  # Print to default printer
  bash print-file.sh -f document.pdf

  # Print to specific printer, 2 copies, duplex
  bash print-file.sh -f document.pdf -p Brother_MFC_L2700DW_series -c 2 --duplex

  # Show printer status
  bash print-file.sh --status

AVAILABLE PRINTERS:
  Brother_HL_L2350DW_series   (Laser - B&W)
  Brother_MFC_L2700DW_series  (MFP - B&W, has scanner)
EOF
    exit 0
}

log_info() {
    echo "ℹ️  $1"
}

log_success() {
    echo "✅ $1"
}

log_error() {
    echo "❌ $1" >&2
}

get_default_printer() {
    lpstat -d 2>/dev/null | awk '{print $NF}' || echo ""
}

check_printer_status() {
    local printer="$1"
    if [[ -z "$printer" ]]; then
        printer=$(get_default_printer)
    fi
    
    if [[ -z "$printer" ]]; then
        log_error "No printer specified and no default printer set"
        return 1
    fi
    
    echo ""
    echo "📠 Printer Status: $printer"
    echo "=============================="
    lpstat -p "$printer" 2>/dev/null || log_error "Printer not found: $printer"
    
    # Check network connectivity
    echo ""
    echo "🌐 Network Check:"
    if lpstat -v | grep -q "$printer"; then
        log_success "Printer registered in CUPS"
    else
        log_error "Printer not registered in CUPS"
    fi
    
    echo ""
}

print_document() {
    local file="$1"
    local printer="$2"
    
    # Use default if not specified
    if [[ -z "$printer" ]]; then
        printer=$(get_default_printer)
        if [[ -z "$printer" ]]; then
            log_error "No default printer set. Use -p to specify printer."
            return 1
        fi
    fi
    
    # Validate file
    if [[ ! -f "$file" ]]; then
        log_error "File not found: $file"
        return 1
    fi
    
    # Validate printer
    if ! lpstat -v | grep -q "$printer"; then
        log_error "Printer not found: $printer"
        log_info "Use: bash list-printers.sh"
        return 1
    fi
    
    # Build lp command
    local cmd=("lp" "-d" "$printer")
    
    # Add copies
    if [[ $COPIES -gt 1 ]]; then
        cmd+=("-n" "$COPIES")
    fi
    
    # Add options
    local opts=()
    
    if $DUPLEX; then
        opts+=("-o" "sides=two-sided-long-edge")
    fi
    
    if $FIT_TO_PAGE; then
        opts+=("-o" "fit-to-page")
    fi
    
    if $LANDSCAPE; then
        opts+=("-o" "orientation-requested=4")
    fi
    
    if $GRAYSCALE; then
        opts+=("-o" "ColorModel=Gray")
    fi
    
    # Add options to command
    for opt in "${opts[@]}"; do
        cmd+=("$opt")
    done
    
    # Add file
    cmd+=("$file")
    
    # Execute print
    echo ""
    log_info "Printing to: $printer"
    log_info "File: $(basename "$file")"
    log_info "Copies: $COPIES"
    [[ $DUPLEX == true ]] && log_info "Mode: Duplex (2-sided)"
    [[ $FIT_TO_PAGE == true ]] && log_info "Scaling: Fit to page"
    [[ $LANDSCAPE == true ]] && log_info "Orientation: Landscape"
    [[ $GRAYSCALE == true ]] && log_info "Color: Grayscale"
    
    echo ""
    
    if "${cmd[@]}"; then
        log_success "Print job submitted"
        echo ""
        log_info "Job ID: $(lpq -P "$printer" | tail -1 | awk '{print $1}')"
        echo ""
        return 0
    else
        log_error "Print job failed"
        return 1
    fi
}

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

while [[ $# -gt 0 ]]; do
    case "$1" in
        -f|--file)
            FILE="$2"
            shift 2
            ;;
        -p|--printer)
            PRINTER="$2"
            shift 2
            ;;
        -c|--copies)
            COPIES="$2"
            shift 2
            ;;
        --duplex)
            DUPLEX=true
            shift
            ;;
        --fit-to-page)
            FIT_TO_PAGE=true
            shift
            ;;
        --landscape)
            LANDSCAPE=true
            shift
            ;;
        --grayscale)
            GRAYSCALE=true
            shift
            ;;
        --status)
            STATUS_ONLY=true
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            ;;
    esac
done

# ============================================================================
# MAIN
# ============================================================================

if $STATUS_ONLY; then
    check_printer_status "$PRINTER"
    exit $?
fi

if [[ -z "$FILE" ]]; then
    log_error "File required. Use -f FILE or --help for usage"
    exit 1
fi

print_document "$FILE" "$PRINTER"
