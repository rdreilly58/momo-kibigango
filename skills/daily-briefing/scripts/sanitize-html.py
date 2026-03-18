#!/usr/bin/env python3
"""
Sanitize HTML briefing for email/PDF — remove CSS, clean up structure
"""

import sys
import re
from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip_content = False
        self.in_style = False
        self.in_script = False
        self.current_section = None
        
    def handle_starttag(self, tag, attrs):
        if tag in ['style', 'script']:
            self.skip_content = True
        elif tag == 'h1':
            self.text.append('\n')
        elif tag == 'h2':
            self.text.append('\n')
        elif tag == 'br':
            self.text.append('\n')
        elif tag == 'p':
            pass
        elif tag == 'div' and dict(attrs).get('class') in ['section', 'item']:
            pass
            
    def handle_endtag(self, tag):
        if tag in ['style', 'script']:
            self.skip_content = False
        elif tag in ['h1', 'h2', 'p', 'div']:
            self.text.append('\n')
            
    def handle_data(self, data):
        if not self.skip_content:
            # Clean up the data
            cleaned = data.strip()
            if cleaned:
                self.text.append(cleaned)
                self.text.append(' ')
    
    def get_text(self):
        result = ''.join(self.text)
        # Clean up multiple newlines and spaces
        result = re.sub(r'\n\n+', '\n', result)
        result = re.sub(r' +', ' ', result)
        return result.strip()

def sanitize_html(html_content):
    """Remove all HTML tags and return clean text"""
    # Remove style tags and content
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    
    # Remove HTML comments
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    
    # Convert some tags to newlines for readability
    html_content = re.sub(r'</div>', '\n', html_content)
    html_content = re.sub(r'</h[1-6]>', '\n', html_content)
    html_content = re.sub(r'</p>', '\n', html_content)
    html_content = re.sub(r'<br\s*/?>', '\n', html_content)
    
    # Remove all remaining HTML tags
    html_content = re.sub(r'<[^>]+>', '', html_content)
    
    # Decode HTML entities
    html_content = html_content.replace('&nbsp;', ' ')
    html_content = html_content.replace('&lt;', '<')
    html_content = html_content.replace('&gt;', '>')
    html_content = html_content.replace('&amp;', '&')
    html_content = html_content.replace('&quot;', '"')
    
    # Remove non-printable characters (but keep newlines)
    html_content = ''.join(c for c in html_content if c.isprintable() or c in '\n\r\t ')
    
    # Clean up whitespace
    lines = [line.strip() for line in html_content.split('\n')]
    lines = [line for line in lines if line]  # Remove empty lines
    
    return '\n'.join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sanitize-html.py <html_file>", file=sys.stderr)
        sys.exit(1)
    
    html_file = sys.argv[1]
    
    try:
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        clean_text = sanitize_html(html_content)
        print(clean_text)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
