# PDF Pro - Unified PDF Generation for OpenClaw

A comprehensive PDF generation skill providing multiple methods for converting documents to PDF format with full styling support.

## Quick Start

```bash
# Convert Markdown to PDF
~/.openclaw/workspace/skills/pdf-pro/scripts/md-to-pdf.sh input.md output.pdf

# Convert HTML to PDF
~/.openclaw/workspace/skills/pdf-pro/scripts/html-to-pdf.sh input.html output.pdf

# Generate PDF programmatically
python3 ~/.openclaw/workspace/skills/pdf-pro/scripts/code-to-pdf.py --title "Report" --content "data.json" output.pdf
```

## Features

- **Three conversion methods**: Markdown, HTML, and programmatic generation
- **Custom CSS styling**: Apply your own styles to any document
- **Metadata support**: Set title, author, subject, keywords
- **Progress indicators**: Real-time feedback during conversion
- **Error handling**: Graceful failures with helpful messages
- **Batch processing**: Convert multiple files at once

## Prerequisites

### Required Tools

```bash
# Install WeasyPrint (primary engine)
brew install weasyprint

# For programmatic generation (optional)
python3 -m venv ~/.openclaw/workspace/venv
source ~/.openclaw/workspace/venv/bin/activate
pip install reportlab markdown2 beautifulsoup4
```

## Usage

### Markdown to PDF

The primary method for most document conversions.

```bash
# Basic conversion
./scripts/md-to-pdf.sh document.md output.pdf

# With custom styling
./scripts/md-to-pdf.sh document.md output.pdf --style styles/professional.css

# With metadata
./scripts/md-to-pdf.sh document.md output.pdf \
  --title "My Document" \
  --author "Bob Reilly" \
  --subject "Technical Documentation"

# Batch conversion
./scripts/md-to-pdf.sh *.md --output-dir pdfs/
```

### HTML to PDF

For web content or pre-styled HTML documents.

```bash
# Basic conversion
./scripts/html-to-pdf.sh page.html output.pdf

# With custom CSS overlay
./scripts/html-to-pdf.sh page.html output.pdf --style styles/print.css

# With page settings
./scripts/html-to-pdf.sh page.html output.pdf \
  --page-size A4 \
  --landscape \
  --margins "1in"
```

### Programmatic PDF Generation

For complex layouts, invoices, reports, or dynamic content.

```bash
# Generate from JSON data
python3 scripts/code-to-pdf.py \
  --template invoice \
  --data invoice_data.json \
  output.pdf

# Generate report with charts
python3 scripts/code-to-pdf.py \
  --template report \
  --data analytics.csv \
  --charts bar,pie \
  output.pdf

# Custom Python template
python3 scripts/code-to-pdf.py \
  --custom my_template.py \
  --data data.json \
  output.pdf
```

## Styling

### Default Styles

The skill includes several pre-built styles in the `styles/` directory:

- **default.css**: Clean, readable formatting
- **professional.css**: Business documents
- **technical.css**: Code-heavy documentation
- **minimal.css**: Simple, distraction-free
- **github.css**: GitHub-flavored markdown style

### Custom Styling

Create your own CSS file:

```css
/* styles/custom.css */
body {
    font-family: 'Georgia', serif;
    line-height: 1.8;
    max-width: 800px;
    margin: 0 auto;
    padding: 2em;
}

h1 {
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
}

code {
    background: #f8f9fa;
    padding: 0.2em 0.4em;
    border-radius: 3px;
}

/* Page breaks */
.page-break {
    page-break-after: always;
}

/* Headers and footers */
@page {
    @top-center {
        content: "My Document";
    }
    @bottom-center {
        content: counter(page) " of " counter(pages);
    }
}
```

## Examples

### Invoice Generation

```bash
# Create invoice data
cat > invoice.json << EOF
{
  "invoice_number": "INV-2024-001",
  "date": "2024-03-21",
  "client": {
    "name": "Acme Corp",
    "address": "123 Business St"
  },
  "items": [
    {"description": "Consulting", "hours": 10, "rate": 150},
    {"description": "Development", "hours": 20, "rate": 175}
  ]
}
EOF

# Generate PDF
python3 scripts/code-to-pdf.py \
  --template invoice \
  --data invoice.json \
  invoice.pdf
```

### Technical Documentation

```bash
# Convert with code highlighting
./scripts/md-to-pdf.sh README.md documentation.pdf \
  --style styles/technical.css \
  --highlight-code
```

### Batch Reports

```bash
# Convert all markdown files with consistent styling
for file in reports/*.md; do
  ./scripts/md-to-pdf.sh "$file" "pdfs/$(basename "$file" .md).pdf" \
    --style styles/professional.css \
    --author "Team Reports"
done
```

## Advanced Features

### Page Settings

Control page layout and dimensions:

```bash
# A4 landscape with custom margins
./scripts/html-to-pdf.sh doc.html output.pdf \
  --page-size A4 \
  --landscape \
  --margin-top 1in \
  --margin-bottom 1in \
  --margin-left 0.75in \
  --margin-right 0.75in
```

### Headers and Footers

Add via CSS or command line:

```bash
# With headers/footers
./scripts/md-to-pdf.sh doc.md output.pdf \
  --header "My Company" \
  --footer "Page {page} of {pages}" \
  --header-font "Arial, 10pt"
```

### Table of Contents

Automatically generate TOC:

```bash
# With TOC
./scripts/md-to-pdf.sh doc.md output.pdf \
  --toc \
  --toc-depth 3
```

### Watermarks

Add watermarks or background images:

```bash
# With watermark
./scripts/html-to-pdf.sh doc.html output.pdf \
  --watermark "CONFIDENTIAL" \
  --watermark-opacity 0.1
```

## Troubleshooting

### Common Issues

1. **WeasyPrint not found**
   ```bash
   brew install weasyprint
   ```

2. **Python module errors**
   ```bash
   source ~/.openclaw/workspace/venv/bin/activate
   pip install -r ~/.openclaw/workspace/skills/pdf-pro/requirements.txt
   ```

3. **CSS not loading**
   - Use absolute paths or ensure working directory is correct
   - Check CSS syntax with validator

4. **Memory issues with large files**
   - Split into smaller chunks
   - Use batch mode with limits
   - Reduce image quality with `--compress-images`

### Debug Mode

Enable verbose output:

```bash
# Debug mode
./scripts/md-to-pdf.sh doc.md output.pdf --debug

# Validation only (no output)
./scripts/md-to-pdf.sh doc.md --validate
```

## Performance

### Optimization Tips

1. **Pre-process images**: Reduce resolution before conversion
2. **Use web fonts sparingly**: Embed only needed subsets
3. **Batch similar documents**: Reuse CSS parsing
4. **Cache conversions**: Store frequently used PDFs

### Benchmarks

| Input Size | Conversion Time | Method |
|------------|----------------|---------|
| 1-10 pages | < 2 seconds | WeasyPrint |
| 10-50 pages | 2-10 seconds | WeasyPrint |
| 50+ pages | 10-30 seconds | Reportlab |
| Complex layouts | 5-20 seconds | Reportlab |

## Integration

### With Other Skills

```bash
# Combine with summarize skill
summarize podcast https://example.com/episode.mp3 | \
  ./scripts/md-to-pdf.sh - transcript.pdf

# With daily-briefing
daily-briefing --format markdown | \
  ./scripts/md-to-pdf.sh - "briefing-$(date +%Y-%m-%d).pdf"
```

### API Usage

```python
# Python integration
from pdf_pro import PDFGenerator

gen = PDFGenerator()
gen.from_markdown("document.md", "output.pdf", 
                 style="professional.css")
```

## Best Practices

1. **Choose the right method**:
   - Markdown → PDF for documents
   - HTML → PDF for web content
   - Programmatic for dynamic data

2. **Optimize for output**:
   - Screen: RGB colors, web fonts
   - Print: CMYK safe colors, embedded fonts

3. **Structure content**:
   - Use semantic HTML/Markdown
   - Let CSS handle styling
   - Avoid inline styles

4. **Test across viewers**:
   - Preview on macOS
   - Adobe Reader
   - Web browsers

## References

- **WeasyPrint Documentation**: https://weasyprint.readthedocs.io/
- **CSS Paged Media**: https://www.w3.org/TR/css-page-3/
- **Reportlab Guide**: https://www.reportlab.com/docs/reportlab-userguide.pdf
- **PDF Best Practices**: See `references/pdf-best-practices.md`

## Updates

- **v1.0.0** (2024-03-21): Initial release with three conversion methods
- **Future**: Compression options, PDF/A support, digital signatures