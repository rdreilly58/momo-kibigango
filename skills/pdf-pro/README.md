# PDF Pro - Quick Start Guide

Professional PDF generation for OpenClaw with multiple conversion methods.

## Installation

```bash
# Install WeasyPrint (required)
brew install weasyprint

# For programmatic generation (optional)
python3 -m pip install reportlab markdown2 beautifulsoup4
```

## Quick Examples

### Convert Markdown to PDF

```bash
# Basic conversion
./scripts/md-to-pdf.sh document.md output.pdf

# With custom styling
./scripts/md-to-pdf.sh document.md output.pdf --style styles/professional.css

# With metadata
./scripts/md-to-pdf.sh document.md output.pdf \
  --title "My Report" \
  --author "John Doe"
```

### Convert HTML to PDF

```bash
# Basic conversion
./scripts/html-to-pdf.sh webpage.html output.pdf

# A4 landscape with margins
./scripts/html-to-pdf.sh report.html report.pdf \
  --page-size A4 \
  --landscape \
  --margins "2cm"
```

### Generate PDF Programmatically

```bash
# Invoice from JSON
python3 scripts/code-to-pdf.py invoice.pdf \
  --template invoice \
  --data invoice_data.json

# Custom report
python3 scripts/code-to-pdf.py report.pdf \
  --template report \
  --data report_data.json
```

## Available Styles

- `default.css` - Clean and readable
- `professional.css` - Business documents
- `technical.css` - Code documentation
- `minimal.css` - Simple and distraction-free
- `github.css` - GitHub markdown style

## Examples

Run all examples:
```bash
./examples/convert_all.sh
```

## Features

✅ Multiple conversion methods (Markdown, HTML, programmatic)  
✅ Custom CSS styling support  
✅ Metadata (title, author, subject)  
✅ Headers and footers  
✅ Table of contents generation  
✅ Code syntax highlighting  
✅ Image optimization  
✅ Batch processing  
✅ Error handling with helpful messages  

## Documentation

See `SKILL.md` for complete documentation, advanced features, and troubleshooting.