#!/bin/bash
# pdf-from-markdown.sh — Fast, reliable PDF generation from Markdown
# Uses WeasyPrint (installed by default on Bob's Mac)
# Fallback: pandoc with WeasyPrint backend

set -e

usage() {
    cat << EOF
Usage: $(basename "$0") INPUT_FILE -o OUTPUT_FILE [options]

Options:
  -o, --output FILE     Output PDF filename (required)
  -t, --title TITLE     PDF title
  -a, --author AUTHOR   PDF author
  --css STYLESHEET      Custom CSS file

Example:
  $(basename "$0") document.md -o output.pdf -t "My Document" -a "Bob Reilly"
EOF
    exit 1
}

# Parse arguments
INPUT=""
OUTPUT=""
TITLE=""
AUTHOR=""
CSS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT="$2"
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
        --css)
            CSS="$2"
            shift 2
            ;;
        -*)
            echo "Unknown option: $1"
            usage
            ;;
        *)
            INPUT="$1"
            shift
            ;;
    esac
done

# Validation
if [[ -z "$INPUT" ]] || [[ -z "$OUTPUT" ]]; then
    usage
fi

if [[ ! -f "$INPUT" ]]; then
    echo "Error: Input file not found: $INPUT"
    exit 1
fi

# Convert Markdown to HTML first (WeasyPrint handles HTML best)
HTML_TEMP=$(mktemp /tmp/momotaro-pdf-XXXXXX.html)
trap "rm -f $HTML_TEMP" EXIT

# Use pandoc for Markdown → HTML conversion
pandoc "$INPUT" \
    -f markdown \
    -t html5 \
    -s \
    -o "$HTML_TEMP" \
    ${TITLE:+--metadata title="$TITLE"} \
    ${AUTHOR:+--metadata author="$AUTHOR"}

# Generate PDF with WeasyPrint
weasyprint "$HTML_TEMP" "$OUTPUT" 2>/dev/null

if [[ -f "$OUTPUT" ]]; then
    SIZE=$(du -h "$OUTPUT" | cut -f1)
    echo "✅ PDF created: $OUTPUT ($SIZE)"
else
    echo "❌ PDF generation failed"
    exit 1
fi
