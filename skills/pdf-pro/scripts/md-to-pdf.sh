#!/bin/bash
# md-to-pdf.sh - Convert Markdown to PDF with WeasyPrint
# Part of the pdf-pro OpenClaw skill

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Default values
OUTPUT=""
STYLE="${SKILL_DIR}/styles/default.css"
TITLE=""
AUTHOR=""
SUBJECT=""
KEYWORDS=""
DEBUG=false
VALIDATE_ONLY=false
TOC=false
TOC_DEPTH=3
HEADER=""
FOOTER=""
COMPRESS_IMAGES=false
OUTPUT_DIR=""
HIGHLIGHT_CODE=false

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
    
    # Check for required tools
    if ! command -v weasyprint &> /dev/null; then
        error_exit "WeasyPrint not found. Install with: brew install weasyprint"
    fi
    
    if ! command -v pandoc &> /dev/null; then
        error_exit "Pandoc not found. Install with: brew install pandoc"
    fi
    
    # Check for optional Python dependencies
    if ! python3 -c "import markdown2" &> /dev/null 2>&1; then
        warning "markdown2 not installed. Some features may be limited."
        warning "Install with: pip install markdown2"
    fi
    
    success "All required dependencies found"
}

# Usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS] INPUT_FILE [OUTPUT_FILE]

Convert Markdown files to PDF using WeasyPrint with HTML intermediary.

Options:
    -h, --help              Show this help message
    -s, --style CSS_FILE    Use custom CSS file (default: styles/default.css)
    -t, --title TITLE       Set PDF title metadata
    -a, --author AUTHOR     Set PDF author metadata
    -j, --subject SUBJECT   Set PDF subject metadata
    -k, --keywords KEYWORDS Set PDF keywords metadata
    -d, --debug             Enable debug output
    -v, --validate          Validate input only, don't create PDF
    --toc                   Generate table of contents
    --toc-depth N           TOC depth (default: 3)
    --header TEXT           Add header to pages
    --footer TEXT           Add footer to pages (use {page} for page number)
    --highlight-code        Enable syntax highlighting for code blocks
    --compress-images       Compress images in PDF
    --output-dir DIR        Output directory for batch conversion

Examples:
    # Basic conversion
    $0 document.md output.pdf

    # With custom styling and metadata
    $0 -s custom.css -t "My Report" -a "John Doe" report.md report.pdf

    # Batch conversion
    $0 --output-dir pdfs/ *.md

    # With table of contents
    $0 --toc --toc-depth 2 manual.md manual.pdf

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
            -t|--title)
                TITLE="$2"
                shift 2
                ;;
            -a|--author)
                AUTHOR="$2"
                shift 2
                ;;
            -j|--subject)
                SUBJECT="$2"
                shift 2
                ;;
            -k|--keywords)
                KEYWORDS="$2"
                shift 2
                ;;
            -d|--debug)
                DEBUG=true
                shift
                ;;
            -v|--validate)
                VALIDATE_ONLY=true
                shift
                ;;
            --toc)
                TOC=true
                shift
                ;;
            --toc-depth)
                TOC_DEPTH="$2"
                shift 2
                ;;
            --header)
                HEADER="$2"
                shift 2
                ;;
            --footer)
                FOOTER="$2"
                shift 2
                ;;
            --highlight-code)
                HIGHLIGHT_CODE=true
                shift
                ;;
            --compress-images)
                COMPRESS_IMAGES=true
                shift
                ;;
            --output-dir)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            -*)
                error_exit "Unknown option: $1"
                ;;
            *)
                if [[ -z "${INPUT_FILE:-}" ]]; then
                    INPUT_FILE="$1"
                elif [[ -z "${OUTPUT:-}" && -z "${OUTPUT_DIR}" ]]; then
                    OUTPUT="$1"
                fi
                shift
                ;;
        esac
    done
}

# Validate input file
validate_input() {
    if [[ -z "${INPUT_FILE:-}" ]]; then
        error_exit "No input file specified"
    fi
    
    # Handle glob patterns for batch mode
    if [[ "$INPUT_FILE" == *"*"* ]]; then
        # Batch mode
        FILES=($INPUT_FILE)
        if [[ ${#FILES[@]} -eq 0 ]]; then
            error_exit "No files match pattern: $INPUT_FILE"
        fi
        show_progress "Found ${#FILES[@]} files to convert"
    else
        # Single file mode
        if [[ ! -f "$INPUT_FILE" ]]; then
            error_exit "Input file not found: $INPUT_FILE"
        fi
        FILES=("$INPUT_FILE")
    fi
    
    # Validate output
    if [[ ${#FILES[@]} -gt 1 ]]; then
        # Batch mode requires output directory
        if [[ -z "$OUTPUT_DIR" ]]; then
            error_exit "Output directory required for batch conversion. Use --output-dir"
        fi
        mkdir -p "$OUTPUT_DIR"
    elif [[ -z "$OUTPUT" && -z "$OUTPUT_DIR" ]]; then
        # Single file mode - generate output name if not provided
        OUTPUT="${INPUT_FILE%.md}.pdf"
    elif [[ -n "$OUTPUT_DIR" ]]; then
        # Single file with output directory
        mkdir -p "$OUTPUT_DIR"
        OUTPUT="$OUTPUT_DIR/$(basename "${INPUT_FILE%.md}.pdf")"
    fi
}

# Convert single file
convert_file() {
    local input_file="$1"
    local output_file="$2"
    local temp_html="/tmp/pdf_pro_$$.html"
    local temp_css="/tmp/pdf_pro_$$.css"
    
    show_progress "Converting: $input_file → $output_file"
    
    # Create HTML from Markdown
    show_progress "Parsing Markdown..."
    
    # Build pandoc command
    PANDOC_CMD=(pandoc "$input_file" -t html5 --standalone)
    
    # Add metadata
    [[ -n "$TITLE" ]] && PANDOC_CMD+=(--metadata "title=$TITLE")
    [[ -n "$AUTHOR" ]] && PANDOC_CMD+=(--metadata "author=$AUTHOR")
    [[ -n "$SUBJECT" ]] && PANDOC_CMD+=(--metadata "subject=$SUBJECT")
    
    # Add TOC if requested
    [[ "$TOC" == "true" ]] && PANDOC_CMD+=(--toc "--toc-depth=$TOC_DEPTH")
    
    # Add code highlighting
    if [[ "$HIGHLIGHT_CODE" == "true" ]]; then
        PANDOC_CMD+=(--highlight-style=pygments)
    fi
    
    # Debug output
    if [[ "$DEBUG" == "true" ]]; then
        echo "Pandoc command: ${PANDOC_CMD[@]}"
    fi
    
    # Execute pandoc
    if ! "${PANDOC_CMD[@]}" > "$temp_html"; then
        error_exit "Pandoc conversion failed"
    fi
    
    # Process CSS
    show_progress "Applying styles..."
    
    # Start with base CSS
    cat > "$temp_css" << 'EOF'
/* PDF Pro Base Styles */
@page {
    size: Letter;
    margin: 1in;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

/* Ensure code blocks don't break */
pre {
    white-space: pre-wrap;
    word-wrap: break-word;
    page-break-inside: avoid;
}

/* Avoid breaking inside elements */
h1, h2, h3, h4, h5, h6 {
    page-break-after: avoid;
}

p, li, blockquote {
    orphans: 3;
    widows: 3;
}

table {
    page-break-inside: avoid;
}

EOF
    
    # Add custom header/footer CSS if provided
    if [[ -n "$HEADER" ]] || [[ -n "$FOOTER" ]]; then
        cat >> "$temp_css" << EOF
@page {
EOF
        if [[ -n "$HEADER" ]]; then
            echo "    @top-center { content: '$HEADER'; }" >> "$temp_css"
        fi
        if [[ -n "$FOOTER" ]]; then
            # Replace {page} placeholder
            FOOTER_PROCESSED="${FOOTER//\{page\}/counter(page)}"
            FOOTER_PROCESSED="${FOOTER_PROCESSED//\{pages\}/counter(pages)}"
            echo "    @bottom-center { content: '$FOOTER_PROCESSED'; }" >> "$temp_css"
        fi
        echo "}" >> "$temp_css"
    fi
    
    # Append custom style if provided
    if [[ -f "$STYLE" ]]; then
        echo "" >> "$temp_css"
        echo "/* Custom styles from $STYLE */" >> "$temp_css"
        cat "$STYLE" >> "$temp_css"
    elif [[ "$STYLE" != "${SKILL_DIR}/styles/default.css" ]]; then
        warning "Style file not found: $STYLE"
    fi
    
    # Validate only mode
    if [[ "$VALIDATE_ONLY" == "true" ]]; then
        success "Validation complete: $input_file"
        rm -f "$temp_html" "$temp_css"
        return 0
    fi
    
    # Convert HTML to PDF with WeasyPrint
    show_progress "Generating PDF..."
    
    WEASY_CMD=(weasyprint)
    
    # Add CSS
    WEASY_CMD+=(-s "$temp_css")
    
    # Add compression if requested
    if [[ "$COMPRESS_IMAGES" == "true" ]]; then
        WEASY_CMD+=(--optimize-images)
    fi
    
    # Add metadata flag if any metadata is set
    if [[ -n "$TITLE" ]] || [[ -n "$AUTHOR" ]] || [[ -n "$SUBJECT" ]] || [[ -n "$KEYWORDS" ]]; then
        WEASY_CMD+=(--custom-metadata)
    fi
    
    # Input and output
    WEASY_CMD+=("$temp_html" "$output_file")
    
    # Debug output
    if [[ "$DEBUG" == "true" ]]; then
        echo "WeasyPrint command: ${WEASY_CMD[@]}"
        "${WEASY_CMD[@]}"
    else
        "${WEASY_CMD[@]}" 2>/dev/null
    fi
    
    # Check result
    if [[ ! -f "$output_file" ]]; then
        error_exit "PDF generation failed"
    fi
    
    # Clean up temp files
    rm -f "$temp_html" "$temp_css"
    
    # Get file size
    local size=$(ls -lh "$output_file" | awk '{print $5}')
    success "Created: $output_file ($size)"
}

# Main execution
main() {
    # Parse arguments
    parse_args "$@"
    
    # Check dependencies
    check_dependencies
    
    # Validate input
    validate_input
    
    # Convert files
    local converted=0
    local failed=0
    
    for file in "${FILES[@]}"; do
        # Determine output file
        if [[ ${#FILES[@]} -gt 1 ]] || [[ -n "$OUTPUT_DIR" ]]; then
            output_file="$OUTPUT_DIR/$(basename "${file%.md}.pdf")"
        else
            output_file="$OUTPUT"
        fi
        
        # Convert
        if convert_file "$file" "$output_file"; then
            ((converted++))
        else
            ((failed++))
            warning "Failed to convert: $file"
        fi
    done
    
    # Summary for batch mode
    if [[ ${#FILES[@]} -gt 1 ]]; then
        echo ""
        success "Conversion complete: $converted succeeded, $failed failed"
    fi
}

# Run main function
main "$@"