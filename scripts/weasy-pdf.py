#!/usr/bin/env python3
"""
weasy-pdf.py — Fast, reliable PDF generation using WeasyPrint
Converts Markdown → HTML → PDF with zero dependencies beyond WeasyPrint

Usage:
  python3 weasy-pdf.py input.md -o output.pdf -t "Title" -a "Author"
"""

import sys
import os
import tempfile
import argparse
import subprocess
from pathlib import Path

def markdown_to_html(markdown_file, title="", author=""):
    """Convert Markdown to HTML using pandoc"""
    html = subprocess.check_output([
        'pandoc',
        markdown_file,
        '-f', 'markdown',
        '-t', 'html5',
        '-s',
        f'--metadata=title:{title}' if title else '--metadata=title:Document',
        f'--metadata=author:{author}' if author else '--metadata=author:',
    ]).decode('utf-8')
    return html

def html_to_pdf(html_content, output_pdf):
    """Convert HTML to PDF using WeasyPrint"""
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        print("❌ WeasyPrint not installed. Install with: brew install weasyprint")
        sys.exit(1)
    
    # Write HTML to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        html_file = f.name
    
    try:
        # Generate PDF
        HTML(string=html_content).write_pdf(output_pdf)
        print(f"✅ PDF created: {output_pdf} ({os.path.getsize(output_pdf) / 1024:.1f} KB)")
    finally:
        os.unlink(html_file)

def main():
    parser = argparse.ArgumentParser(
        description="Fast PDF generation from Markdown/HTML using WeasyPrint"
    )
    parser.add_argument('input', help='Input Markdown file')
    parser.add_argument('-o', '--output', required=True, help='Output PDF file')
    parser.add_argument('-t', '--title', default='', help='PDF title')
    parser.add_argument('-a', '--author', default='', help='PDF author')
    
    args = parser.parse_args()
    
    # Validate input
    if not os.path.exists(args.input):
        print(f"❌ Input file not found: {args.input}")
        sys.exit(1)
    
    # Convert
    html = markdown_to_html(args.input, args.title, args.author)
    html_to_pdf(html, args.output)

if __name__ == '__main__':
    main()
