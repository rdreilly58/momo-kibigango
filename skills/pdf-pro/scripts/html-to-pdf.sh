#!/bin/bash
# html-to-pdf.sh - Convert HTML to PDF with WeasyPrint
# Part of the pdf-pro OpenClaw skill

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Default values
OUTPUT=""
STYLE=""
PAGE_SIZE="Letter"
LANDSCAPE=false
MARGIN_TOP="1in"
MARGIN_BOTTOM="1in"
MARGIN_LEFT="1in"
MARGIN_RIGHT="1in"
WATERMARK=""
WATERMARK_OPACITY="0.1"
DEBUG=false
OPTIMIZE_IMAGES=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Progress indicator
show_progress() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

# Error handler
error_exit() {
    echo -e "${RED}Error:${NC} $1" >&2
    exit 1
}

# Success message
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Warning message
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check dependencies
check_dependencies() {
    show_progress "Checking dependencies..."
    
    if ! command -v weasyprint &> /dev/null; then
        error_exit "WeasyPrint not found. Install with: brew install weasyprint"
    fi
    
    success "Dependencies verified"
}

# Usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS] INPUT_HTML OUTPUT_PDF

Convert HTML files to PDF using WeasyPrint.

Options:
    -h, --help                  Show this help message
    -s, --style CSS_FILE        Apply additional CSS file
    -p, --page-size SIZE        Page size (Letter, A4, Legal, etc.)
    -l, --landscape             Use landscape orientation
    -m, --margins SIZE          Set all margins (e.g., "1in", "2cm")
    --margin-top SIZE           Set top margin
    --margin-bottom SIZE        Set bottom margin
    --margin-left SIZE          Set left margin
    --margin-right SIZE         Set right margin
    -w, --watermark TEXT        Add watermark text
    --watermark-opacity N       Watermark opacity (0.0-1.0, default: 0.1)
    -o, --optimize-images       Optimize images in PDF
    -d, --debug                 Enable debug output

Examples:
    # Basic conversion
    $0 page.html output.pdf

    # A4 landscape with custom margins
    $0 -p A4 -l --margins "2cm" report.html report.pdf

    # With watermark
    $0 -w "CONFIDENTIAL" invoice.html invoice.pdf

    # With custom styling
    $0 -s print.css webpage.html printed.pdf

EOF
    exit 0
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                ;;
            -s|--style)
                STYLE="$2"
                shift 2
                ;;
            -p|--page-size)
                PAGE_SIZE="$2"
                shift 2
                ;;
            -l|--landscape)
                LANDSCAPE=true
                shift
                ;;
            -m|--margins)
                MARGIN_TOP="$2"
                MARGIN_BOTTOM="$2"
                MARGIN_LEFT="$2"
                MARGIN_RIGHT="$2"
                shift 2
                ;;
            --margin-top)
                MARGIN_TOP="$2"
                shift 2
                ;;
            --margin-bottom)
                MARGIN_BOTTOM="$2"
                shift 2
                ;;
            --margin-left)
                MARGIN_LEFT="$2"
                shift 2
                ;;
            --margin-right)
                MARGIN_RIGHT="$2"
                shift 2
                ;;
            -w|--watermark)
                WATERMARK="$2"
                shift 2
                ;;
            --watermark-opacity)
                WATERMARK_OPACITY="$2"
                shift 2
                ;;
            -o|--optimize-images)
                OPTIMIZE_IMAGES=true
                shift
                ;;
            -d|--debug)
                DEBUG=true
                shift
                ;;
            -*)
                error_exit "Unknown option: $1"
                ;;
            *)
                if [[ -z "${INPUT_FILE:-}" ]]; then
                    INPUT_FILE="$1"
                elif [[ -z "${OUTPUT:-}" ]]; then
                    OUTPUT="$1"
                fi
                shift
                ;;
        esac
    done
}

# Validate inputs
validate_inputs() {
    if [[ -z "${INPUT_FILE:-}" ]]; then
        error_exit "No input file specified"
    fi
    
    if [[ ! -f "$INPUT_FILE" ]]; then
        error_exit "Input file not found: $INPUT_FILE"
    fi
    
    if [[ -z "$OUTPUT" ]]; then
        error_exit "No output file specified"
    fi
    
    # Validate page size
    case "$PAGE_SIZE" in
        Letter|A4|A3|Legal|Tabloid|A5|B4|B5) ;;
        *) warning "Unusual page size: $PAGE_SIZE" ;;
    esac
    
    # Validate watermark opacity
    if [[ -n "$WATERMARK" ]]; then
        if ! python3 -c "assert 0.0 <= $WATERMARK_OPACITY <= 1.0" 2>/dev/null; then
            error_exit "Invalid watermark opacity: $WATERMARK_OPACITY (must be 0.0-1.0)"
        fi
    fi
}

# Create temporary CSS with page settings
create_page_css() {
    local temp_css="/tmp/pdf_pro_page_$$.css"
    
    # Start with page configuration
    {
        echo "@page {"
        echo "    size: $PAGE_SIZE$(if [[ "$LANDSCAPE" == "true" ]]; then echo " landscape"; fi);"
        echo "    margin-top: $MARGIN_TOP;"
        echo "    margin-bottom: $MARGIN_BOTTOM;"
        echo "    margin-left: $MARGIN_LEFT;"
        echo "    margin-right: $MARGIN_RIGHT;"
        echo "}"
        echo ""
        
        # Add watermark if specified
        if [[ -n "$WATERMARK" ]]; then
            cat << EOF
/* Watermark */
body::before {
    content: "$WATERMARK";
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-45deg);
    font-size: 72pt;
    font-weight: bold;
    color: rgba(0, 0, 0, $WATERMARK_OPACITY);
    z-index: -1;
    white-space: nowrap;
    pointer-events: none;
}
EOF
        fi
        
        # Basic print optimization
        cat << 'EOF'

/* Print optimization */
* {
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
}

/* Avoid page breaks inside elements */
h1, h2, h3, h4, h5, h6 {
    page-break-after: avoid;
    page-break-inside: avoid;
}

p, li, blockquote, tr {
    page-break-inside: avoid;
}

table {
    page-break-inside: avoid;
}

img {
    max-width: 100%;
    page-break-inside: avoid;
}

/* Keep headings with their content */
h1, h2, h3, h4, h5, h6 {
    orphans: 3;
    widows: 3;
}

/* Avoid single lines at page boundaries */
p, li {
    orphans: 3;
    widows: 3;
}
EOF
    } > "$temp_css"
    
    echo "$temp_css"
}

# Convert HTML to PDF
convert_html_to_pdf() {
    show_progress "Converting HTML to PDF..."
    
    # Create page CSS
    local page_css=$(create_page_css)
    
    # Build WeasyPrint command
    WEASY_CMD=(weasyprint)
    
    # Add page CSS
    WEASY_CMD+=(-s "$page_css")
    
    # Add custom CSS if provided
    if [[ -n "$STYLE" ]]; then
        if [[ -f "$STYLE" ]]; then
            WEASY_CMD+=(-s "$STYLE")
            show_progress "Applying custom styles from: $STYLE"
        else
            warning "Style file not found: $STYLE"
        fi
    fi
    
    # Add optimization if requested
    if [[ "$OPTIMIZE_IMAGES" == "true" ]]; then
        WEASY_CMD+=(--optimize-images)
        show_progress "Image optimization enabled"
    fi
    
    # Input and output
    WEASY_CMD+=("$INPUT_FILE" "$OUTPUT")
    
    # Debug output
    if [[ "$DEBUG" == "true" ]]; then
        echo "WeasyPrint command: ${WEASY_CMD[@]}"
        echo "Page CSS contents:"
        cat "$page_css"
        echo "---"
    fi
    
    # Execute conversion
    if [[ "$DEBUG" == "true" ]]; then
        "${WEASY_CMD[@]}"
    else
        "${WEASY_CMD[@]}" 2>/dev/null
    fi
    
    local exit_code=$?
    
    # Clean up
    rm -f "$page_css"
    
    # Check result
    if [[ $exit_code -ne 0 ]]; then
        error_exit "PDF conversion failed"
    fi
    
    if [[ ! -f "$OUTPUT" ]]; then
        error_exit "Output file was not created"
    fi
    
    # Report success with file size
    local size=$(ls -lh "$OUTPUT" | awk '{print $5}')
    success "Created: $OUTPUT ($size)"
    
    # Show page settings
    if [[ "$DEBUG" == "true" ]]; then
        echo "Page settings:"
        echo "  Size: $PAGE_SIZE$(if [[ "$LANDSCAPE" == "true" ]]; then echo " (landscape)"; fi)"
        echo "  Margins: T=$MARGIN_TOP R=$MARGIN_RIGHT B=$MARGIN_BOTTOM L=$MARGIN_LEFT"
        [[ -n "$WATERMARK" ]] && echo "  Watermark: $WATERMARK (opacity: $WATERMARK_OPACITY)"
        [[ "$OPTIMIZE_IMAGES" == "true" ]] && echo "  Images: optimized"
    fi
}

# Main execution
main() {
    # Parse arguments
    parse_args "$@"
    
    # Check dependencies
    check_dependencies
    
    # Validate inputs
    validate_inputs
    
    # Perform conversion
    convert_html_to_pdf
}

# Run main function
main "$@"