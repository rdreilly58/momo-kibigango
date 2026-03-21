#!/usr/bin/env python3
"""
code-to-pdf.py - Programmatic PDF generation with ReportLab
Part of the pdf-pro OpenClaw skill
"""

import sys
import os
import json
import argparse
import importlib.util
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4, legal, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, KeepTogether, ListFlowable, ListItem
    )
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    from reportlab.platypus.tableofcontents import TableOfContents
    from reportlab.lib.utils import ImageReader
except ImportError:
    print("Error: ReportLab not installed. Install with:", file=sys.stderr)
    print("  python3 -m pip install reportlab", file=sys.stderr)
    sys.exit(1)

# Progress colors
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def show_progress(message: str):
    """Display progress message with timestamp."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{Colors.BLUE}[{timestamp}]{Colors.NC} {message}")

def error_exit(message: str):
    """Display error message and exit."""
    print(f"{Colors.RED}Error:{Colors.NC} {message}", file=sys.stderr)
    sys.exit(1)

def success(message: str):
    """Display success message."""
    print(f"{Colors.GREEN}✓{Colors.NC} {message}")

def warning(message: str):
    """Display warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.NC} {message}")

class PDFGenerator:
    """Base class for PDF generation with ReportLab."""
    
    def __init__(self, filename: str, pagesize=letter, 
                 title: str = "", author: str = "", subject: str = ""):
        self.filename = filename
        self.pagesize = pagesize
        self.title = title or "Generated PDF"
        self.author = author or "PDF Pro"
        self.subject = subject or "Document"
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Add custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        # Custom body text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY
        ))
    
    def add_title(self, text: str, style: str = 'CustomTitle'):
        """Add a title to the document."""
        self.story.append(Paragraph(text, self.styles[style]))
        self.story.append(Spacer(1, 0.2*inch))
    
    def add_subtitle(self, text: str):
        """Add a subtitle to the document."""
        self.story.append(Paragraph(text, self.styles['Subtitle']))
        self.story.append(Spacer(1, 0.1*inch))
    
    def add_paragraph(self, text: str, style: str = 'CustomBody'):
        """Add a paragraph to the document."""
        self.story.append(Paragraph(text, self.styles[style]))
        self.story.append(Spacer(1, 0.1*inch))
    
    def add_heading(self, text: str, level: int = 1):
        """Add a heading to the document."""
        style = f'Heading{level}' if f'Heading{level}' in self.styles else 'Heading1'
        self.story.append(Paragraph(text, self.styles[style]))
        self.story.append(Spacer(1, 0.1*inch))
    
    def add_table(self, data: List[List], headers: Optional[List] = None,
                  col_widths: Optional[List] = None):
        """Add a table to the document."""
        if headers:
            data = [headers] + data
        
        table = Table(data, colWidths=col_widths)
        
        # Apply table style
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        
        table.setStyle(style)
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))
    
    def add_page_break(self):
        """Add a page break."""
        self.story.append(PageBreak())
    
    def add_spacer(self, height: float = 0.2):
        """Add vertical space (in inches)."""
        self.story.append(Spacer(1, height*inch))
    
    def add_image(self, image_path: str, width: Optional[float] = None, 
                  height: Optional[float] = None):
        """Add an image to the document."""
        if not os.path.exists(image_path):
            warning(f"Image not found: {image_path}")
            return
        
        img = Image(image_path, width=width, height=height)
        self.story.append(img)
        self.story.append(Spacer(1, 0.2*inch))
    
    def generate(self):
        """Generate the PDF file."""
        show_progress("Generating PDF document...")
        
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=self.pagesize,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
            title=self.title,
            author=self.author,
            subject=self.subject
        )
        
        # Build PDF
        doc.build(self.story)
        
        # Check result
        if os.path.exists(self.filename):
            size = os.path.getsize(self.filename)
            size_str = f"{size/1024:.1f}KB" if size < 1024*1024 else f"{size/(1024*1024):.1f}MB"
            success(f"Created: {self.filename} ({size_str})")
        else:
            error_exit("PDF generation failed")

# Template generators
def generate_invoice(data: Dict[str, Any], output_file: str):
    """Generate an invoice PDF from JSON data."""
    show_progress("Creating invoice PDF...")
    
    pdf = PDFGenerator(output_file, title="Invoice", subject="Invoice Document")
    
    # Company header
    pdf.add_title(data.get('company_name', 'Invoice'))
    if 'company_address' in data:
        pdf.add_paragraph(data['company_address'], 'Normal')
    
    pdf.add_spacer(0.5)
    
    # Invoice details
    pdf.add_heading(f"Invoice #{data.get('invoice_number', 'N/A')}", 2)
    pdf.add_paragraph(f"Date: {data.get('date', datetime.now().strftime('%Y-%m-%d'))}")
    
    if 'due_date' in data:
        pdf.add_paragraph(f"Due Date: {data['due_date']}")
    
    pdf.add_spacer(0.3)
    
    # Client information
    if 'client' in data:
        pdf.add_heading("Bill To:", 3)
        client = data['client']
        pdf.add_paragraph(client.get('name', ''))
        if 'address' in client:
            pdf.add_paragraph(client['address'])
        if 'email' in client:
            pdf.add_paragraph(client['email'])
    
    pdf.add_spacer(0.5)
    
    # Items table
    if 'items' in data:
        table_data = [['Description', 'Quantity', 'Rate', 'Amount']]
        total = 0
        
        for item in data['items']:
            description = item.get('description', '')
            quantity = item.get('quantity', item.get('hours', 1))
            rate = item.get('rate', item.get('price', 0))
            amount = quantity * rate
            total += amount
            
            table_data.append([
                description,
                str(quantity),
                f"${rate:,.2f}",
                f"${amount:,.2f}"
            ])
        
        # Add total row
        table_data.append(['', '', 'Total:', f"${total:,.2f}"])
        
        pdf.add_table(table_data, col_widths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    
    # Payment terms
    if 'payment_terms' in data:
        pdf.add_heading("Payment Terms", 3)
        pdf.add_paragraph(data['payment_terms'])
    
    # Notes
    if 'notes' in data:
        pdf.add_spacer(0.5)
        pdf.add_heading("Notes", 3)
        pdf.add_paragraph(data['notes'])
    
    pdf.generate()

def generate_report(data: Dict[str, Any], output_file: str):
    """Generate a report PDF from data."""
    show_progress("Creating report PDF...")
    
    pdf = PDFGenerator(
        output_file, 
        title=data.get('title', 'Report'),
        author=data.get('author', ''),
        subject=data.get('subject', 'Report Document')
    )
    
    # Title page
    pdf.add_title(data.get('title', 'Report'))
    if 'subtitle' in data:
        pdf.add_subtitle(data['subtitle'])
    
    if 'date' in data:
        pdf.add_paragraph(f"Date: {data['date']}", 'Normal')
    if 'author' in data:
        pdf.add_paragraph(f"Author: {data['author']}", 'Normal')
    
    pdf.add_page_break()
    
    # Table of contents if sections exist
    if 'sections' in data and len(data['sections']) > 1:
        pdf.add_heading("Table of Contents", 1)
        for i, section in enumerate(data['sections']):
            pdf.add_paragraph(f"{i+1}. {section.get('title', 'Section')}")
        pdf.add_page_break()
    
    # Content sections
    for section in data.get('sections', []):
        if 'title' in section:
            pdf.add_heading(section['title'], 1)
        
        if 'content' in section:
            if isinstance(section['content'], list):
                for item in section['content']:
                    pdf.add_paragraph(str(item))
            else:
                pdf.add_paragraph(str(section['content']))
        
        if 'table' in section:
            pdf.add_table(
                section['table'].get('data', []),
                headers=section['table'].get('headers')
            )
        
        if 'image' in section:
            pdf.add_image(section['image'])
        
        pdf.add_spacer(0.5)
    
    pdf.generate()

def generate_from_custom_template(template_file: str, data: Dict[str, Any], 
                                 output_file: str):
    """Generate PDF using a custom Python template."""
    show_progress(f"Loading custom template: {template_file}")
    
    # Load the template module
    spec = importlib.util.spec_from_file_location("template", template_file)
    if spec is None:
        error_exit(f"Failed to load template: {template_file}")
    
    template = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(template)
    
    # Call the generate function
    if hasattr(template, 'generate'):
        template.generate(data, output_file)
        success(f"Generated using custom template: {template_file}")
    else:
        error_exit("Template must have a 'generate(data, output_file)' function")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate PDF files programmatically using templates and data'
    )
    parser.add_argument('output', help='Output PDF filename')
    parser.add_argument('--template', choices=['invoice', 'report'], 
                       help='Use built-in template')
    parser.add_argument('--custom', help='Path to custom Python template')
    parser.add_argument('--data', help='JSON data file or inline JSON string')
    parser.add_argument('--title', help='PDF title metadata')
    parser.add_argument('--author', help='PDF author metadata')
    parser.add_argument('--subject', help='PDF subject metadata')
    parser.add_argument('--content', help='Simple text content for basic PDF')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    # Load data
    data = {}
    if args.data:
        if os.path.isfile(args.data):
            show_progress(f"Loading data from: {args.data}")
            with open(args.data, 'r') as f:
                data = json.load(f)
        else:
            try:
                data = json.loads(args.data)
            except json.JSONDecodeError:
                error_exit(f"Invalid JSON data: {args.data}")
    
    # Add metadata if provided
    if args.title:
        data['title'] = args.title
    if args.author:
        data['author'] = args.author
    if args.subject:
        data['subject'] = args.subject
    
    # Generate PDF based on template
    if args.template == 'invoice':
        generate_invoice(data, args.output)
    elif args.template == 'report':
        generate_report(data, args.output)
    elif args.custom:
        generate_from_custom_template(args.custom, data, args.output)
    elif args.content:
        # Simple content-based PDF
        pdf = PDFGenerator(
            args.output,
            title=args.title or "Document",
            author=args.author or "",
            subject=args.subject or ""
        )
        pdf.add_title(args.title or "Document")
        pdf.add_paragraph(args.content)
        pdf.generate()
    else:
        error_exit("Must specify --template, --custom, or --content")

if __name__ == '__main__':
    main()