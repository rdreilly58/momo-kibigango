#!/usr/bin/env python3
"""
Telegraph Publisher - Publish formatted content to Telegraph.ph
Used for OpenClaw subagent output, HEARTBEAT reports, and manual publishing.
"""

import requests
import json
import os
import time
import re
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser("~/.openclaw/logs/telegraph.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegraphPublisher:
    """Publish content to Telegraph with retry logic and error handling."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize publisher with config."""
        self.config_path = config_path or os.path.expanduser("~/.openclaw/workspace/config/telegraph.json")
        self.config = self._load_config()
        self.token = self._load_token()
        self.api_endpoint = self.config['api']['endpoint']
        self.timeout = self.config['api']['timeout_seconds']
        
    def _load_config(self) -> Dict[str, Any]:
        """Load Telegraph configuration."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _load_token(self) -> str:
        """Load access token from secure storage."""
        token_path = os.path.expanduser(self.config['token']['storage'])
        
        if not os.path.exists(token_path):
            raise FileNotFoundError(f"Telegraph token not found: {token_path}")
        
        with open(token_path, 'r') as f:
            return f.read().strip()
    
    def _retry_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make request with exponential backoff retry."""
        retry_config = self.config['api']['retry']
        max_attempts = retry_config['max_attempts']
        initial_delay = retry_config['initial_delay_ms'] / 1000
        max_delay = retry_config['max_delay_ms'] / 1000
        
        delay = initial_delay
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                if method.upper() == 'POST':
                    response = requests.post(endpoint, timeout=self.timeout, **kwargs)
                else:
                    response = requests.get(endpoint, timeout=self.timeout, **kwargs)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    last_error = f"HTTP {response.status_code}: {response.text}"
                    
                    if response.status_code == 429:  # Rate limit
                        delay = min(delay * 2, max_delay)
                        logger.warning(f"Rate limited, retry in {delay:.1f}s")
                        time.sleep(delay)
                        continue
                    
                    raise Exception(last_error)
            
            except requests.Timeout:
                last_error = f"Timeout after {self.timeout}s"
                if attempt < max_attempts - 1:
                    time.sleep(delay)
                    delay = min(delay * 2, max_delay)
            
            except Exception as e:
                last_error = str(e)
                if attempt < max_attempts - 1:
                    time.sleep(delay)
                    delay = min(delay * 2, max_delay)
        
        raise Exception(f"Failed after {max_attempts} attempts: {last_error}")
    
    def _markdown_to_telegraph_content(self, markdown: str) -> list:
        """Convert Markdown to Telegraph content format."""
        content = []
        lines = markdown.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Headings (H2-H6)
            if line.startswith('## '):
                content.append({'tag': 'h3', 'children': [line[3:].strip()]})
            elif line.startswith('### '):
                content.append({'tag': 'h4', 'children': [line[4:].strip()]})
            elif line.startswith('#### '):
                content.append({'tag': 'h5', 'children': [line[5:].strip()]})
            
            # Code blocks
            elif line.startswith('```'):
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                
                code_content = '\n'.join(code_lines).strip()
                if code_content:
                    content.append({'tag': 'pre', 'children': [code_content]})
            
            # Tables (basic support)
            elif '|' in line and i + 1 < len(lines) and '|' in lines[i + 1]:
                # Simple table to paragraph conversion for now
                content.append({'tag': 'p', 'children': [line]})
            
            # Lists
            elif line.startswith('- '):
                content.append({'tag': 'p', 'children': ['• ' + line[2:].strip()]})
            elif line.startswith('* '):
                content.append({'tag': 'p', 'children': ['• ' + line[2:].strip()]})
            
            # Paragraphs
            elif line.strip():
                # Inline formatting: bold (**text**) and italic (*text*)
                formatted = line.strip()
                formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', formatted)
                formatted = re.sub(r'\*(.+?)\*', r'<em>\1</em>', formatted)
                content.append({'tag': 'p', 'children': [formatted]})
            
            i += 1
        
        return content if content else [{'tag': 'p', 'children': ['(empty content)']}]
    
    def publish_markdown(self, title: str, markdown_content: str, 
                        return_content: bool = False) -> Dict[str, Any]:
        """
        Publish Markdown content to Telegraph.
        
        Args:
            title: Article title
            markdown_content: Markdown formatted content
            return_content: If True, return full Telegraph content
        
        Returns:
            Dict with 'url' key and Telegraph response
        """
        logger.info(f"Publishing: {title}")
        
        if not markdown_content.strip():
            raise ValueError("Content cannot be empty")
        
        # Convert to Telegraph content format
        content = self._markdown_to_telegraph_content(markdown_content)
        
        # Create page
        url = f"{self.api_endpoint}/createPage"
        payload = {
            'access_token': self.token,
            'title': title[:256],  # Telegraph limit
            'author_name': self.config['author']['name'],
            'author_url': 'https://github.com/rreilly/openclaw',
            'content': content,
            'return_content': return_content
        }
        
        try:
            response = self._retry_request('POST', url, json=payload)
            
            if 'result' in response:
                result = response['result']
                page_url = result['url']
                logger.info(f"✅ Published: {page_url}")
                
                return {
                    'success': True,
                    'url': f"https://telegra.ph{page_url}",
                    'path': result.get('path'),
                    'title': result.get('title')
                }
            else:
                error_msg = response.get('error', 'Unknown error')
                logger.error(f"❌ API Error: {error_msg}")
                return {'success': False, 'error': error_msg}
        
        except Exception as e:
            logger.error(f"❌ Publish failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def publish_html(self, title: str, html_content: str,
                    return_content: bool = False) -> Dict[str, Any]:
        """Publish HTML content to Telegraph."""
        logger.info(f"Publishing HTML: {title}")
        
        url = f"{self.api_endpoint}/createPage"
        payload = {
            'access_token': self.token,
            'title': title[:256],
            'author_name': self.config['author']['name'],
            'author_url': 'https://github.com/rreilly/openclaw',
            'content': html_content,
            'return_content': return_content
        }
        
        try:
            response = self._retry_request('POST', url, json=payload)
            
            if 'result' in response:
                result = response['result']
                page_url = result['url']
                logger.info(f"✅ Published: {page_url}")
                
                return {
                    'success': True,
                    'url': f"https://telegra.ph{page_url}",
                    'path': result.get('path'),
                    'title': result.get('title')
                }
            else:
                error_msg = response.get('error', 'Unknown error')
                logger.error(f"❌ API Error: {error_msg}")
                return {'success': False, 'error': error_msg}
        
        except Exception as e:
            logger.error(f"❌ Publish failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def test_connectivity(self) -> bool:
        """Test Telegraph API connectivity."""
        logger.info("Testing Telegraph API connectivity...")
        
        try:
            url = f"{self.api_endpoint}/getPageViews"
            response = requests.get(url, params={'path': 'test'}, timeout=self.timeout)
            
            if response.status_code == 200:
                logger.info("✅ Telegraph API is accessible")
                return True
            else:
                logger.warning(f"⚠️  Telegraph API returned {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Cannot reach Telegraph API: {str(e)}")
            return False


def main():
    """CLI entry point for testing."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: telegraph_publisher.py <command> [args]")
        print("\nCommands:")
        print("  test              - Test API connectivity")
        print("  publish-md <title> <file>  - Publish Markdown file")
        print("  publish-html <title> <file> - Publish HTML file")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        pub = TelegraphPublisher()
        
        if command == 'test':
            result = pub.test_connectivity()
            sys.exit(0 if result else 1)
        
        elif command == 'publish-md':
            if len(sys.argv) < 4:
                print("Usage: telegraph_publisher.py publish-md <title> <file>")
                sys.exit(1)
            
            title = sys.argv[2]
            filepath = sys.argv[3]
            
            with open(filepath, 'r') as f:
                content = f.read()
            
            result = pub.publish_markdown(title, content)
            
            if result['success']:
                print(f"\n✅ Published: {result['url']}")
            else:
                print(f"\n❌ Error: {result['error']}")
                sys.exit(1)
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
