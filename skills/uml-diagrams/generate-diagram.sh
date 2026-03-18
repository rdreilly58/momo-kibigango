#!/bin/bash
# generate-diagram.sh — Quick UML diagram generator
#
# Usage:
#   generate-diagram.sh class MyClass.mmd
#   generate-diagram.sh sequence flow.mmd --format png
#   generate-diagram.sh er schema.mmd --output ~/diagrams/

set -euo pipefail

DIAGRAM_TYPE="${1:-}"
DIAGRAM_FILE="${2:-}"
FORMAT="${3:-svg}"
OUTPUT_DIR="${4:-.}"

if [[ -z "$DIAGRAM_TYPE" ]] || [[ -z "$DIAGRAM_FILE" ]]; then
  echo "Usage: generate-diagram.sh <type> <file.mmd> [--format png|svg] [--output dir]"
  echo ""
  echo "Types: class, sequence, state, er, deployment"
  echo "Example: generate-diagram.sh class diagram.mmd --format png"
  exit 1
fi

# Handle format flags
if [[ "$FORMAT" == "--format" ]]; then
  FORMAT="${OUTPUT_DIR:-svg}"
  OUTPUT_DIR="."
fi

if [[ "$OUTPUT_DIR" == "--output" ]]; then
  OUTPUT_DIR="${FORMAT:-.}"
fi

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Generate diagram
OUTPUT_FILE="${OUTPUT_DIR}/$(basename "$DIAGRAM_FILE" .mmd).${FORMAT}"

echo "🎨 Generating $DIAGRAM_TYPE diagram..."
echo "   Input: $DIAGRAM_FILE"
echo "   Output: $OUTPUT_FILE"

mermaid "$DIAGRAM_FILE" --output "$OUTPUT_FILE" --puppeteerConfigFile /dev/null 2>/dev/null || {
  echo "⚠️  Falling back to default mermaid CLI..."
  mmdc -i "$DIAGRAM_FILE" -o "$OUTPUT_FILE" -t default 2>/dev/null || {
    echo "❌ Failed to generate diagram"
    exit 1
  }
}

echo "✅ Diagram generated: $OUTPUT_FILE"

# Try to open in default app (macOS only)
if command -v open &>/dev/null; then
  open "$OUTPUT_FILE"
fi
