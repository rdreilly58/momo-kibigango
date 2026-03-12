#!/usr/bin/env python3
"""
Generate professional PDF briefing using reportlab with enhanced styling
"""

import sys
import os
from datetime import datetime
import re

def generate_pdf_from_html(html_content, output_path, briefing_type='morning'):
    """Generate PDF from HTML content using reportlab with professional styling."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
        from reportlab.pdfgen import canvas
        
        # Color scheme
        if briefing_type == 'morning':
            primary_color = '#2c5aa0'  # Blue
            emoji = '☀️'
            title = 'Morning Briefing'
        else:
            primary_color = '#8b5cf6'  # Purple
            emoji = '🌙'
            title = 'Evening Briefing'
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              topMargin=0.6*inch,
                              bottomMargin=0.6*inch,
                              leftMargin=0.8*inch,
                              rightMargin=0.8*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'BriefingTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor(primary_color),
            spaceAfter=8,
            spaceBefore=0,
            alignment=0,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'BriefingSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            spaceAfter=12,
            spaceBefore=0,
            fontName='Helvetica'
        )
        
        heading_style = ParagraphStyle(
            'BriefingHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor(primary_color),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'BriefingBody',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            leading=13
        )
        
        # Add title and date
        story.append(Paragraph(f"{emoji} {title}", title_style))
        now = datetime.now()
        date_text = now.strftime("%A, %B %d, %Y at %I:%M %p")
        story.append(Paragraph(date_text, subtitle_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor(primary_color)))
        story.append(Spacer(1, 0.15*inch))
        
        # Email Status
        if 'Email' in html_content or 'unread' in html_content.lower():
            story.append(Paragraph("📬 Email Status", heading_style))
            match = re.search(r'<span class="badge">(\d+)', html_content)
            if match:
                unread = match.group(1)
                story.append(Paragraph(f"<b>{unread}</b> unread messages in your inbox", body_style))
            else:
                story.append(Paragraph("Email status unavailable", body_style))
            story.append(Spacer(1, 0.12*inch))
        
        # Calendar Events
        if '48 Hours' in html_content or 'calendar' in html_content.lower():
            story.append(Paragraph("🗓️ Calendar Events", heading_style))
            # Extract calendar table
            calendar_matches = re.findall(r'<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>', html_content)
            if calendar_matches:
                for event_title, event_date in calendar_matches[:5]:
                    title_clean = event_title.strip()
                    date_clean = event_date.strip()
                    story.append(Paragraph(f"• <b>{title_clean}</b> — {date_clean}", body_style))
            else:
                story.append(Paragraph("No events scheduled", body_style))
            story.append(Spacer(1, 0.12*inch))
        
        # Analytics
        if 'Analytics' in html_content or 'Sessions' in html_content:
            story.append(Paragraph("📊 Website Analytics", heading_style))
            if 'unavailable' in html_content.lower():
                story.append(Paragraph("<i>GA4 analytics unavailable (permissions pending)</i>", body_style))
            else:
                # Try to extract analytics metrics
                sessions = re.search(r'>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>([\d.]+%)</td>', html_content)
                if sessions:
                    story.append(Paragraph(f"• Sessions: {sessions.group(1)}", body_style))
                    story.append(Paragraph(f"• Users: {sessions.group(2)}", body_style))
                    story.append(Paragraph(f"• Bounce Rate: {sessions.group(3)}", body_style))
                else:
                    story.append(Paragraph("Analytics data unavailable", body_style))
            story.append(Spacer(1, 0.12*inch))
        
        # Priorities (Morning)
        if 'Priorities' in html_content and briefing_type == 'morning':
            story.append(Paragraph("⭐ Today's Priorities", heading_style))
            priorities = re.findall(r'<strong>([^<]+)</strong><br/>\s*<span>([^<]+)</span>', html_content)
            if priorities:
                for idx, (priority_title, priority_desc) in enumerate(priorities, 1):
                    story.append(Paragraph(f"<b>{priority_title.strip()}</b>", body_style))
                    story.append(Paragraph(f"  → {priority_desc.strip()}", body_style))
                    if idx < len(priorities):
                        story.append(Spacer(1, 0.06*inch))
            story.append(Spacer(1, 0.12*inch))
        
        # Work Summary (Evening)
        if 'Completed' in html_content and briefing_type == 'evening':
            story.append(Paragraph("✅ Today's Work", heading_style))
            # Extract completed items
            completed = re.findall(r'<span class="completed">[^<]*</span>([^<]+)', html_content)
            if completed:
                for item in completed[:5]:
                    story.append(Paragraph(f"✓ {item.strip()}", body_style))
                story.append(Spacer(1, 0.12*inch))
        
        # Blockers (Evening)
        if 'Blocker' in html_content and briefing_type == 'evening':
            story.append(Paragraph("⚠️ Current Blockers", heading_style))
            blockers = re.findall(r'<span class="blocked">[^<]*</span>([^<]+)', html_content)
            if blockers:
                for blocker in blockers[:3]:
                    story.append(Paragraph(f"• {blocker.strip()}", body_style))
                story.append(Spacer(1, 0.12*inch))
        
        # Tomorrow Preview (Evening)
        if 'Tomorrow' in html_content and briefing_type == 'evening':
            story.append(Paragraph("📅 Tomorrow's Preview", heading_style))
            # Extract tomorrow's events
            tomorrow_matches = re.findall(r'<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>', html_content)
            if tomorrow_matches:
                for event_title, event_date in tomorrow_matches[:5]:
                    title_clean = event_title.strip()
                    date_clean = event_date.strip()
                    story.append(Paragraph(f"• <b>{title_clean}</b> — {date_clean}", body_style))
            else:
                story.append(Paragraph("No events scheduled", body_style))
            story.append(Spacer(1, 0.12*inch))
        
        # Tomorrow's Focus (Evening)
        if 'Focus' in html_content and briefing_type == 'evening':
            story.append(Paragraph("🎯 Tomorrow's Focus", heading_style))
            focus_items = re.findall(r'<strong>([^<]+)</strong><br/>\s*<span>([^<]+)</span>', html_content)
            if focus_items:
                for focus_title, focus_desc in focus_items[:3]:
                    story.append(Paragraph(f"<b>{focus_title.strip()}</b>", body_style))
                    story.append(Paragraph(f"  → {focus_desc.strip()}", body_style))
                    story.append(Spacer(1, 0.06*inch))
        
        # Footer
        story.append(Spacer(1, 0.15*inch))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
        story.append(Spacer(1, 0.08*inch))
        story.append(Paragraph("<font size=9 color='#999'>Generated by Momotaro 🍑 • Keep making progress</font>", body_style))
        
        # Build PDF
        doc.build(story)
        
        if os.path.exists(output_path):
            return output_path
            
    except Exception as e:
        print(f"PDF generation error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: html_to_pdf.py <input.html> <output.pdf> [briefing_type]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    briefing_type = sys.argv[3] if len(sys.argv) > 3 else 'morning'
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        result = generate_pdf_from_html(html_content, output_file, briefing_type)
        if result:
            print(f"✅ PDF created: {result}")
            sys.exit(0)
        else:
            print("❌ PDF generation failed")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
