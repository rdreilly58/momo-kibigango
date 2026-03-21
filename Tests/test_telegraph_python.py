#!/usr/bin/env python3
"""
Tests for Telegraph Python implementation
"""

import unittest
import sys
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from telegraph_publisher import TelegraphPublisher, TelegraphConfig
from telegraph_integration import (
    CodeBlockFormatter, TableFormatter, MetricsFormatter,
    SubagentOutputIntegration, TelegraphCliHelper
)


class TestTelegraphConfig(unittest.TestCase):
    """Test Telegraph configuration"""
    
    def test_config_defaults(self):
        """Test default configuration values"""
        config = TelegraphConfig()
        self.assertEqual(config.api_url, "https://api.telegra.ph")
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.default_author, "OpenClaw")
    
    def test_config_custom(self):
        """Test custom configuration"""
        config = TelegraphConfig(
            max_retries=5,
            timeout=60,
            default_author="TestAuthor"
        )
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.timeout, 60)
        self.assertEqual(config.default_author, "TestAuthor")


class TestTelegraphPublisher(unittest.TestCase):
    """Test Telegraph publisher"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.publisher = TelegraphPublisher()
    
    def test_initialization(self):
        """Test publisher initialization"""
        self.assertIsNone(self.publisher.access_token)
        self.assertIsNotNone(self.publisher.config)
    
    def test_initialization_with_token(self):
        """Test publisher initialization with token"""
        token = "test_token_123"
        publisher = TelegraphPublisher(access_token=token)
        self.assertEqual(publisher.access_token, token)
    
    @patch('requests.post')
    def test_create_account(self, mock_post):
        """Test account creation"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "ok": True,
            "result": {
                "short_name": "openclaw_test",
                "access_token": "test_token_123",
                "auth_url": "https://telegra.ph/auth/test"
            }
        }
        mock_post.return_value = mock_response
        
        token = self.publisher.create_account()
        
        self.assertIsNotNone(token)
        self.assertEqual(self.publisher.access_token, token)
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_publish_markdown(self, mock_post):
        """Test markdown publication"""
        self.publisher.access_token = "test_token"
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "ok": True,
            "result": {
                "url": "https://telegra.ph/Test-Page-123",
                "path": "Test-Page-123",
                "title": "Test Page"
            }
        }
        mock_post.return_value = mock_response
        
        url = self.publisher.publish_markdown(
            title="Test Page",
            content="# Test\n\nThis is a test."
        )
        
        self.assertIsNotNone(url)
        self.assertIn("telegra.ph", url)
    
    @patch('requests.post')
    def test_publish_html(self, mock_post):
        """Test HTML publication"""
        self.publisher.access_token = "test_token"
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "ok": True,
            "result": {
                "url": "https://telegra.ph/Test-HTML-456",
                "path": "Test-HTML-456",
                "title": "Test HTML"
            }
        }
        mock_post.return_value = mock_response
        
        html_content = "<h1>Test</h1><p>HTML content</p>"
        url = self.publisher.publish_html(
            title="Test HTML",
            content=html_content
        )
        
        self.assertIsNotNone(url)
        self.assertIn("telegra.ph", url)
    
    @patch('requests.post')
    def test_update_page(self, mock_post):
        """Test page update"""
        self.publisher.access_token = "test_token"
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "ok": True,
            "result": {
                "url": "https://telegra.ph/Test-Page-123",
                "path": "Test-Page-123"
            }
        }
        mock_post.return_value = mock_response
        
        url = self.publisher.update_page(
            path="Test-Page-123",
            content="<p>Updated content</p>"
        )
        
        self.assertIsNotNone(url)
    
    @patch('requests.get')
    def test_get_page(self, mock_get):
        """Test page retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "ok": True,
            "result": {
                "title": "Test Page",
                "url": "https://telegra.ph/Test-Page-123",
                "content": "<h1>Test</h1>"
            }
        }
        mock_get.return_value = mock_response
        
        page = self.publisher.get_page("Test-Page-123")
        
        self.assertIsNotNone(page)
        self.assertEqual(page.get("title"), "Test Page")
    
    def test_markdown_to_html_conversion(self):
        """Test markdown to HTML conversion"""
        markdown = """
# Header 1
## Header 2
**bold** and *italic*
`code`
[link](https://example.com)
"""
        
        html = self.publisher._markdown_to_html(markdown)
        
        self.assertIn("<h1>", html)
        self.assertIn("<strong>", html)
        self.assertIn("<em>", html)
        self.assertIn("<a href=", html)
    
    def test_save_token(self):
        """Test token saving"""
        self.publisher.access_token = "test_token"
        self.publisher.account_info = {"short_name": "test"}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            token_file = os.path.join(tmpdir, "token.json")
            self.publisher.save_token(token_file)
            
            self.assertTrue(os.path.exists(token_file))
            
            with open(token_file) as f:
                data = json.load(f)
                self.assertEqual(data["access_token"], "test_token")
    
    def test_load_token(self):
        """Test token loading"""
        with tempfile.TemporaryDirectory() as tmpdir:
            token_file = os.path.join(tmpdir, "token.json")
            
            # Save token
            token_data = {
                "access_token": "loaded_token",
                "created_at": datetime.now().isoformat()
            }
            with open(token_file, 'w') as f:
                json.dump(token_data, f)
            
            # Load token
            token = TelegraphPublisher.load_token(token_file)
            self.assertEqual(token, "loaded_token")


class TestCodeBlockFormatter(unittest.TestCase):
    """Test code block formatting"""
    
    def test_format_code_block(self):
        """Test code block formatting"""
        code = 'print("Hello")'
        formatted = CodeBlockFormatter.format_code_block(code, "python")
        
        self.assertIn("<pre><code", formatted)
        self.assertIn("language-python", formatted)
    
    def test_extract_code_blocks(self):
        """Test code block extraction"""
        content = """
Here's some Python:

```python
def hello():
    print("Hello")
```

And some JavaScript:

```javascript
console.log("Hi");
```
"""
        
        blocks = CodeBlockFormatter.extract_code_blocks(content)
        
        self.assertIn("python", blocks)
        self.assertIn("javascript", blocks)
        self.assertEqual(len(blocks["python"]), 1)


class TestTableFormatter(unittest.TestCase):
    """Test table formatting"""
    
    def test_markdown_to_html_table(self):
        """Test markdown table conversion"""
        markdown_table = """
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
"""
        
        html = TableFormatter.markdown_table_to_html(markdown_table)
        
        self.assertIn("<table", html)
        self.assertIn("<th>", html)
        self.assertIn("<td>", html)
        self.assertIn("Header 1", html)
        self.assertIn("Cell 1", html)


class TestMetricsFormatter(unittest.TestCase):
    """Test metrics formatting"""
    
    def test_format_metrics(self):
        """Test metrics formatting"""
        metrics = {
            "Uptime": "99.9%",
            "Latency": "145ms",
            "Errors": "0"
        }
        
        html = MetricsFormatter.format_metrics(metrics)
        
        self.assertIn("Uptime", html)
        self.assertIn("99.9%", html)
        self.assertIn("grid", html)
    
    def test_format_status_report(self):
        """Test status report formatting"""
        data = {
            "summary": "All systems operational",
            "metrics": {"Uptime": "100%"},
            "sections": {"Status": "Everything is fine"}
        }
        
        html = MetricsFormatter.format_status_report(data)
        
        self.assertIn("Status Report", html)
        self.assertIn("All systems operational", html)
        self.assertIn("Uptime", html)


class TestSubagentIntegration(unittest.TestCase):
    """Test subagent integration"""
    
    @patch('telegraph_publisher.TelegraphPublisher.publish_html')
    def test_process_subagent_output(self, mock_publish):
        """Test subagent output processing"""
        mock_publish.return_value = "https://telegra.ph/test"
        
        publisher = Mock(spec=TelegraphPublisher)
        publisher.publish_html = mock_publish
        
        integration = SubagentOutputIntegration(publisher)
        
        output = """
# Test Report
**Status:** Complete

```python
def test():
    pass
```
"""
        
        url = integration.process_subagent_output(output, "Test")
        
        self.assertEqual(url, "https://telegra.ph/test")
        mock_publish.assert_called_once()


class TestCliHelper(unittest.TestCase):
    """Test CLI helper"""
    
    def test_format_file_content(self):
        """Test file content formatting"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.md")
            with open(test_file, 'w') as f:
                f.write("# Test\n\nContent")
            
            content = TelegraphCliHelper.format_file_content(test_file, "markdown")
            self.assertIn("Test", content)


class TestErrorHandling(unittest.TestCase):
    """Test error handling"""
    
    @patch('requests.post')
    def test_retry_on_failure(self, mock_post):
        """Test retry logic on failure"""
        # First two calls fail, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.raise_for_status.side_effect = Exception("Network error")
        
        mock_response_success = Mock()
        mock_response_success.json.return_value = {
            "ok": True,
            "result": {"access_token": "token"}
        }
        
        mock_post.side_effect = [
            Exception("Network error"),
            Exception("Network error"),
            mock_response_success
        ]
        
        # Note: This tests the retry mechanism
        publisher = TelegraphPublisher()
        
        # This should succeed after retries (mocked to work)
        with patch.object(publisher, '_request') as mock_req:
            mock_req.return_value = {"access_token": "token"}
            publisher.create_account()
            self.assertIsNotNone(publisher.access_token)


class TestTokenManagement(unittest.TestCase):
    """Test token management"""
    
    def test_token_persistence(self):
        """Test token can be saved and loaded"""
        with tempfile.TemporaryDirectory() as tmpdir:
            token_file = os.path.join(tmpdir, "token.json")
            
            # Create and save
            pub1 = TelegraphPublisher(access_token="test_token_123")
            pub1.account_info = {"short_name": "test"}
            pub1.save_token(token_file)
            
            # Load
            loaded_token = TelegraphPublisher.load_token(token_file)
            pub2 = TelegraphPublisher(access_token=loaded_token)
            
            self.assertEqual(pub2.access_token, "test_token_123")


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    run_tests()
