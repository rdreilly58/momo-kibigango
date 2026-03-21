#!/bin/bash
# Example: Batch convert all markdown files with different styles

SKILL_DIR="$HOME/.openclaw/workspace/skills/pdf-pro"
EXAMPLES_DIR="$SKILL_DIR/examples"
OUTPUT_DIR="$EXAMPLES_DIR/output"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "PDF Pro - Example Conversions"
echo "============================"

# Convert simple.md with different styles
echo -e "\n1. Converting simple.md with various styles..."

styles=("default" "professional" "technical" "minimal" "github")
for style in "${styles[@]}"; do
    echo "   - Using $style style..."
    "$SKILL_DIR/scripts/md-to-pdf.sh" \
        "$EXAMPLES_DIR/simple.md" \
        "$OUTPUT_DIR/simple-$style.pdf" \
        --style "$SKILL_DIR/styles/$style.css" \
        --title "Simple Example - $style" \
        --author "PDF Pro Demo"
done

# Generate invoice
echo -e "\n2. Generating invoice from JSON..."
python3 "$SKILL_DIR/scripts/code-to-pdf.py" \
    "$OUTPUT_DIR/invoice.pdf" \
    --template invoice \
    --data "$EXAMPLES_DIR/invoice_template.json"

# Create a simple report
echo -e "\n3. Creating report programmatically..."
cat > "$OUTPUT_DIR/report_data.json" << EOF
{
  "title": "Quarterly Report",
  "subtitle": "Q1 2024 Performance Analysis",
  "author": "Analytics Team",
  "date": "March 21, 2024",
  "sections": [
    {
      "title": "Executive Summary",
      "content": "This quarter showed significant growth across all key metrics."
    },
    {
      "title": "Financial Performance",
      "table": {
        "headers": ["Metric", "Q1 2024", "Q4 2023", "Change"],
        "data": [
          ["Revenue", "$1.2M", "$980K", "+22%"],
          ["Profit", "$320K", "$250K", "+28%"],
          ["Customers", "1,250", "1,100", "+14%"]
        ]
      }
    },
    {
      "title": "Conclusion",
      "content": "The positive trends indicate strong momentum heading into Q2."
    }
  ]
}
EOF

python3 "$SKILL_DIR/scripts/code-to-pdf.py" \
    "$OUTPUT_DIR/report.pdf" \
    --template report \
    --data "$OUTPUT_DIR/report_data.json"

# Summary
echo -e "\n✅ All examples converted successfully!"
echo "Output files in: $OUTPUT_DIR"
echo ""
ls -la "$OUTPUT_DIR"/*.pdf