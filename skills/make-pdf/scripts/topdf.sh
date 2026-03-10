#!/bin/bash
# topdf.sh — Convert text/markdown to PDF using pandoc + weasyprint
# Falls back to simple text → HTML → PDF via macOS Quartz

set -euo pipefail

INPUT_FILE=""
OUTPUT_FILE=""
TITLE=""
FROM_STDIN=false

while [[ $# -gt 0 ]]; do
  case $1 in
    -o|--output)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    -t|--title)
      TITLE="$2"
      shift 2
      ;;
    --stdin)
      FROM_STDIN=true
      shift
      ;;
    *)
      INPUT_FILE="$1"
      shift
      ;;
  esac
done

if [[ -z "$OUTPUT_FILE" ]]; then
  echo "Error: -o OUTPUT_FILE is required" >&2
  exit 1
fi

# Temp file
TEMP_HTML=$(mktemp /tmp/topdf.XXXXXX.html)
trap "rm -f $TEMP_HTML" EXIT

echo "[topdf] Creating PDF: $OUTPUT_FILE"

# Build HTML
if [[ "$FROM_STDIN" = true ]]; then
  CONTENT=$(cat)
else
  if [[ ! -f "$INPUT_FILE" ]]; then
    echo "[topdf] Error: file not found: $INPUT_FILE" >&2
    exit 1
  fi
  CONTENT=$(cat "$INPUT_FILE")
fi

# Try pandoc first (best quality)
if which pandoc > /dev/null 2>&1; then
  echo "$CONTENT" | pandoc -f markdown -t html > "$TEMP_HTML" 2>/dev/null || {
    # Fallback to plain text conversion
    cat > "$TEMP_HTML" << 'HTMLEOF'
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Document</title><style>body{font-family:system-ui;margin:40px;line-height:1.6;white-space:pre-wrap;}</style></head><body>
HTMLEOF
    echo "$CONTENT" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g' >> "$TEMP_HTML"
    echo "</body></html>" >> "$TEMP_HTML"
  }
else
  # Fallback: plain HTML wrapping
  cat > "$TEMP_HTML" << HTMLEOF
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>${TITLE:-Document}</title>
<style>body{font-family:system-ui;margin:40px;line-height:1.6;white-space:pre-wrap;}</style>
</head>
<body>
$(echo "$CONTENT" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')
</body></html>
HTMLEOF
fi

# Convert HTML to PDF using Python (Cocoa/Quartz)
python3 << PYTHON
import os, sys
from pathlib import Path

html_file = "$TEMP_HTML"
pdf_file = "$OUTPUT_FILE"

# Try with weasyprint if available
try:
  from weasyprint import HTML
  HTML(html_file).write_pdf(pdf_file)
  print(f"[topdf] Created {Path(pdf_file).stat().st_size} bytes")
  sys.exit(0)
except ImportError:
  pass

# Fallback: use native macOS PDF generation
try:
  from PyPDF2 import PdfWriter  # Check if available
except ImportError:
  pass

# Last resort: use system CUPS printing to PDF
import subprocess
result = subprocess.run([
  'lp', '-d', 'Save as PDF', '-o', f'OutputFile={pdf_file}', html_file
], capture_output=True, text=True)

if result.returncode == 0 and os.path.exists(pdf_file):
  print(f"[topdf] Created {Path(pdf_file).stat().st_size} bytes")
  sys.exit(0)
else:
  print("[topdf] Error: Could not create PDF", file=sys.stderr)
  sys.exit(1)
PYTHON

if [[ -f "$OUTPUT_FILE" ]]; then
  echo "[topdf] Done: $(ls -lh "$OUTPUT_FILE" | awk '{print $5}')"
else
  echo "[topdf] Error: PDF creation failed" >&2
  exit 1
fi
