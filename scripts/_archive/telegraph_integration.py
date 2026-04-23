#!/usr/bin/env python3
"""
Telegraph Integration Module
Integrates Telegraph publishing with OpenClaw workflows
"""

import logging
import re
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from telegraph_publisher import TelegraphPublisher, TelegraphConfig

logger = logging.getLogger(__name__)


class CodeBlockFormatter:
    """Formats code blocks with syntax highlighting metadata"""
    
    @staticmethod
    def format_code_block(code: str, language: str = "python") -> str:
        """
        Format code block with language specification
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            Formatted code block HTML
        """
        # Escape HTML
        code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        return f"""<pre><code class="language-{language}">{code}</code></pre>"""
    
    @staticmethod
    def extract_code_blocks(content: str) -> Dict[str, List[str]]:
        """
        Extract code blocks from markdown/content
        
        Args:
            content: Content containing code blocks
            
        Returns:
            Dict with language as key, list of code blocks as value
        """
        blocks = {}
        
        # Match ```language ... ``` blocks
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for lang, code in matches:
            lang = lang or "plaintext"
            if lang not in blocks:
                blocks[lang] = []
            blocks[lang].append(code.strip())
        
        return blocks


class TableFormatter:
    """Formats tables as HTML"""
    
    @staticmethod
    def markdown_table_to_html(markdown_table: str) -> str:
        """
        Convert Markdown table to HTML
        
        Args:
            markdown_table: Markdown-formatted table
            
        Returns:
            HTML table
        """
        lines = markdown_table.strip().split('\n')
        if len(lines) < 2:
            return ""
        
        # Extract headers
        headers = [h.strip() for h in lines[0].split('|') if h.strip()]
        
        # Skip separator line
        # Extract rows
        rows = []
        for line in lines[2:]:
            if line.strip():
                cells = [c.strip() for c in line.split('|') if c.strip()]
                rows.append(cells)
        
        # Generate HTML
        html = '<table border="1" cellpadding="5">'
        
        # Header
        html += '<thead><tr>'
        for header in headers:
            html += f'<th>{header}</th>'
        html += '</tr></thead>'
        
        # Body
        html += '<tbody>'
        for row in rows:
            html += '<tr>'
            for cell in row:
                html += f'<td>{cell}</td>'
            html += '</tr>'
        html += '</tbody>'
        
        html += '</table>'
        return html


class MetricsFormatter:
    """Formats metrics and statistics for visualization"""
    
    @staticmethod
    def format_metrics(metrics: Dict[str, Any]) -> str:
        """
        Format metrics as HTML cards
        
        Args:
            metrics: Dictionary of metric names to values
            
        Returns:
            HTML metrics display
        """
        html = '<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">'
        
        for metric_name, metric_value in metrics.items():
            html += f"""
            <div style="border: 1px solid #ccc; padding: 10px; border-radius: 5px;">
                <strong>{metric_name}</strong><br/>
                <span style="font-size: 24px; color: #0066cc;">{metric_value}</span>
            </div>
            """
        
        html += '</div>'
        return html
    
    @staticmethod
    def format_status_report(data: Dict[str, Any]) -> str:
        """
        Format status report with metrics and summary
        
        Args:
            data: Status report data
            
        Returns:
            Formatted HTML report
        """
        html = "<h2>Status Report</h2>"
        html += f"<p><em>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S EDT')}</em></p>"
        
        if "summary" in data:
            html += f"<p>{data['summary']}</p>"
        
        if "metrics" in data:
            html += "<h3>Metrics</h3>"
            html += MetricsFormatter.format_metrics(data['metrics'])
        
        if "sections" in data:
            for section_name, section_content in data['sections'].items():
                html += f"<h3>{section_name}</h3>"
                html += f"<p>{section_content}</p>"
        
        return html


class SubagentOutputIntegration:
    """Integrates with subagent output for automatic publishing"""
    
    def __init__(self, publisher: TelegraphPublisher):
        """
        Initialize integration
        
        Args:
            publisher: TelegraphPublisher instance
        """
        self.publisher = publisher
    
    def process_subagent_output(self, output: str, title: Optional[str] = None,
                               author: Optional[str] = None) -> str:
        """
        Process subagent output and publish to Telegraph
        
        Args:
            output: Subagent output (Markdown or HTML)
            title: Page title (auto-generated if not provided)
            author: Author name
            
        Returns:
            Telegraph URL
        """
        if not title:
            title = f"Subagent Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Format output
        formatted_output = self._format_subagent_output(output)
        
        # Publish
        url = self.publisher.publish_html(title, formatted_output, author)
        
        logger.info(f"Subagent output published: {url}")
        return url
    
    def _format_subagent_output(self, output: str) -> str:
        """
        Format subagent output with proper styling
        
        Args:
            output: Raw output
            
        Returns:
            Formatted HTML
        """
        html = "<div style='font-family: system-ui, -apple-system, sans-serif; line-height: 1.6;'>"
        
        # Process code blocks
        output = re.sub(
            r'```(\w+)?\n(.*?)```',
            lambda m: CodeBlockFormatter.format_code_block(m.group(2), m.group(1) or "plaintext"),
            output,
            flags=re.DOTALL
        )
        
        # Convert basic markdown
        output = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', output, flags=re.MULTILINE)
        output = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', output, flags=re.MULTILINE)
        output = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', output, flags=re.MULTILINE)
        
        # Bold and italic
        output = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', output)
        output = re.sub(r'\*(.*?)\*', r'<em>\1</em>', output)
        
        # Links
        output = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', output)
        
        # Line breaks
        output = output.replace('\n\n', '</p><p>')
        output = f'<p>{output}</p>'
        
        html += output
        html += "</div>"
        
        return html


class TelegraphHeartbeatIntegration:
    """Integrates Telegraph publishing with HEARTBEAT tasks"""
    
    def __init__(self, publisher: TelegraphPublisher, token_path: str):
        """
        Initialize heartbeat integration
        
        Args:
            publisher: TelegraphPublisher instance
            token_path: Path to token file
        """
        self.publisher = publisher
        self.token_path = token_path
    
    def publish_heartbeat_report(self, report_data: Dict[str, Any]) -> str:
        """
        Publish heartbeat report to Telegraph
        
        Args:
            report_data: Heartbeat report data
            
        Returns:
            Telegraph URL
        """
        title = f"OpenClaw Heartbeat - {datetime.now().strftime('%Y-%m-%d %H:%M EDT')}"
        content = MetricsFormatter.format_status_report(report_data)
        
        url = self.publisher.publish_html(title, content, author="OpenClaw")
        
        logger.info(f"Heartbeat report published: {url}")
        return url
    
    def log_heartbeat_history(self, heartbeat_log: Dict[str, str], file_path: str) -> None:
        """
        Log heartbeat URLs to file for history
        
        Args:
            heartbeat_log: Dict of heartbeat name to Telegraph URL
            file_path: Path to log file
        """
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing log
        log_data = []
        if Path(file_path).exists():
            with open(file_path, 'r') as f:
                log_data = json.load(f)
        
        # Add new entries
        for name, url in heartbeat_log.items():
            log_data.append({
                "timestamp": datetime.now().isoformat(),
                "name": name,
                "url": url
            })
        
        # Save
        with open(file_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        logger.info(f"Heartbeat history logged: {file_path}")


class TelegraphCliHelper:
    """Helper for command-line interface"""
    
    @staticmethod
    def load_or_create_publisher(token_path: Optional[str] = None) -> TelegraphPublisher:
        """
        Load publisher from token file or create new account
        
        Args:
            token_path: Path to token file (optional)
            
        Returns:
            TelegraphPublisher instance
        """
        if token_path and Path(token_path).exists():
            token = TelegraphPublisher.load_token(token_path)
            logger.info(f"Loaded token from {token_path}")
            return TelegraphPublisher(access_token=token)
        else:
            logger.info("Creating new Telegraph account...")
            publisher = TelegraphPublisher()
            publisher.create_account()
            if token_path:
                publisher.save_token(token_path)
            return publisher
    
    @staticmethod
    def format_file_content(file_path: str, format_type: str = "markdown") -> str:
        """
        Load and format file content
        
        Args:
            file_path: Path to file
            format_type: Content format (markdown, html, text)
            
        Returns:
            Formatted content
        """
        with open(file_path, 'r') as f:
            content = f.read()
        
        if format_type == "markdown":
            # Markdown is handled by telegraph_publisher
            pass
        elif format_type == "html":
            pass
        elif format_type == "text":
            # Wrap in <pre> for code/text
            content = f"<pre>{content}</pre>"
        
        return content


if __name__ == "__main__":
    # Example integration
    publisher = TelegraphPublisher()
    publisher.create_account()
    
    # Test subagent integration
    subagent_integration = SubagentOutputIntegration(publisher)
    test_output = """
    # Test Report
    
    This is a test subagent output.
    
    ```python
    def hello():
        print("Hello, Telegraph!")
    ```
    
    **Status:** Complete
    """
    
    url = subagent_integration.process_subagent_output(test_output, "Test Subagent Output")
    print(f"Published: {url}")
