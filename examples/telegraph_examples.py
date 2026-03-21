#!/usr/bin/env python3
"""
Telegraph Examples for OpenClaw
Demonstrates all major use cases
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from telegraph_publisher import TelegraphPublisher
from telegraph_integration import (
    CodeBlockFormatter, TableFormatter, MetricsFormatter,
    SubagentOutputIntegration, TelegraphCliHelper
)
from datetime import datetime


def example_1_simple_markdown():
    """Example 1: Simple Markdown publication"""
    print("\n" + "="*60)
    print("Example 1: Simple Markdown Publication")
    print("="*60)
    
    # Create publisher and account
    publisher = TelegraphPublisher()
    token = publisher.create_account(
        short_name="openclaw_example1",
        author_name="OpenClaw"
    )
    print(f"✓ Account created with token: {token[:30]}...")
    
    # Markdown content
    markdown_content = """
    # Hello Telegraph!
    
    This is a **simple** Markdown document published to Telegraph.
    
    ## Features
    
    - Easy to use
    - Supports *markdown* formatting
    - Fast publication
    
    [Visit GitHub](https://github.com)
    """
    
    # Publish
    url = publisher.publish_markdown(
        title="Simple Markdown Example",
        content=markdown_content,
        author="OpenClaw"
    )
    
    print(f"✓ Published to: {url}")
    return url


def example_2_code_documentation():
    """Example 2: Code documentation with syntax highlighting"""
    print("\n" + "="*60)
    print("Example 2: Code Documentation with Syntax Highlighting")
    print("="*60)
    
    publisher = TelegraphPublisher()
    publisher.create_account(
        short_name="openclaw_example2",
        author_name="OpenClaw"
    )
    
    # Code example
    python_code = """
def fibonacci(n):
    '''Generate Fibonacci sequence up to n'''
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    sequence = [0, 1]
    while sequence[-1] + sequence[-2] <= n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence

# Usage
print(fibonacci(100))
"""
    
    # Format code block
    formatted_code = CodeBlockFormatter.format_code_block(python_code, "python")
    
    html_content = f"""
    <h1>Fibonacci Implementation</h1>
    <p>A simple Python implementation of the Fibonacci sequence:</p>
    {formatted_code}
    <p><strong>Features:</strong></p>
    <ul>
        <li>Efficient algorithm</li>
        <li>Readable code</li>
        <li>Proper documentation</li>
    </ul>
    """
    
    # Publish
    url = publisher.publish_html(
        title="Code Documentation Example",
        content=html_content,
        author="Code Reviewer"
    )
    
    print(f"✓ Published to: {url}")
    return url


def example_3_status_report():
    """Example 3: Status report with metrics"""
    print("\n" + "="*60)
    print("Example 3: Status Report with Metrics")
    print("="*60)
    
    publisher = TelegraphPublisher()
    publisher.create_account(
        short_name="openclaw_example3",
        author_name="OpenClaw"
    )
    
    # Report data
    report_data = {
        "summary": "Daily system status report - All systems operational",
        "metrics": {
            "Uptime": "99.98%",
            "Active Tasks": "24",
            "Completed": "156",
            "Pending": "12",
            "API Latency": "145ms",
            "Error Rate": "0.02%"
        },
        "sections": {
            "System Status": "All systems are running normally. No alerts.",
            "Performance": "Average response time improved by 12% this week.",
            "Deployments": "3 successful deployments, 0 rollbacks"
        }
    }
    
    # Format as status report
    html_content = MetricsFormatter.format_status_report(report_data)
    
    # Publish
    url = publisher.publish_html(
        title=f"Daily Status Report - {datetime.now().strftime('%Y-%m-%d')}",
        content=html_content,
        author="System Monitor"
    )
    
    print(f"✓ Published to: {url}")
    return url


def example_4_blog_post():
    """Example 4: Blog post publishing"""
    print("\n" + "="*60)
    print("Example 4: Blog Post Publishing")
    print("="*60)
    
    publisher = TelegraphPublisher()
    publisher.create_account(
        short_name="openclaw_blog_example",
        author_name="OpenClaw Blog"
    )
    
    blog_content = """
# Getting Started with Telegraph
## A Guide to Publishing Content

Telegraph is a powerful platform for publishing content quickly and easily.
In this post, we'll explore how to use Telegraph with OpenClaw.

### Why Telegraph?

Telegraph offers several advantages:

1. **Speed** - Publish content instantly
2. **Simplicity** - Minimal API, maximum functionality
3. **Reliability** - Built on solid infrastructure
4. **Flexibility** - Supports HTML, Markdown, and more

### Getting Started

Here's a quick example:

```python
from telegraph_publisher import TelegraphPublisher

publisher = TelegraphPublisher()
publisher.create_account()

url = publisher.publish_markdown(
    title="My First Post",
    content="Hello, Telegraph!"
)
print(f"Published: {url}")
```

### Best Practices

- Keep titles concise and descriptive
- Use proper formatting for readability
- Include relevant metadata
- Test before publishing

### Conclusion

Telegraph combined with OpenClaw provides a powerful platform
for automated content publishing and distribution.

**Happy publishing!**
"""
    
    url = publisher.publish_markdown(
        title="Getting Started with Telegraph",
        content=blog_content,
        author="OpenClaw Team"
    )
    
    print(f"✓ Published to: {url}")
    return url


def example_5_media_embedding():
    """Example 5: Media embedding (images and videos)"""
    print("\n" + "="*60)
    print("Example 5: Media Embedding")
    print("="*60)
    
    publisher = TelegraphPublisher()
    publisher.create_account(
        short_name="openclaw_media_example",
        author_name="OpenClaw"
    )
    
    # Create a sample image for upload (1x1 PNG)
    import base64
    from pathlib import Path
    
    # 1x1 transparent PNG
    png_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    
    # Save sample image
    sample_image = Path("/tmp/sample.png")
    sample_image.write_bytes(png_data)
    
    try:
        # Upload media
        media_url = publisher.upload_media(str(sample_image))
        print(f"✓ Media uploaded: {media_url}")
        
        # Create content with embedded media
        html_content = f"""
        <h1>Media Embedding Example</h1>
        <p>This page demonstrates media embedding in Telegraph:</p>
        
        <h2>Embedded Image</h2>
        <img src="{media_url}" alt="Sample Image" style="max-width: 400px;">
        
        <h2>YouTube Embedding</h2>
        <p>You can also embed YouTube videos using iframe:</p>
        <iframe width="400" height="300" 
                src="https://www.youtube.com/embed/dQw4w9WgXcQ" 
                frameborder="0" allowfullscreen></iframe>
        
        <h2>Benefits</h2>
        <ul>
            <li>Rich multimedia content</li>
            <li>Enhanced engagement</li>
            <li>Professional presentation</li>
        </ul>
        """
        
        # Publish
        url = publisher.publish_html(
            title="Media Embedding Example",
            content=html_content,
            author="Media Producer"
        )
        
        print(f"✓ Published to: {url}")
        return url
    
    finally:
        # Cleanup
        if sample_image.exists():
            sample_image.unlink()


def example_6_table_formatting():
    """Example 6: Table formatting"""
    print("\n" + "="*60)
    print("Example 6: Table Formatting")
    print("="*60)
    
    publisher = TelegraphPublisher()
    publisher.create_account(
        short_name="openclaw_table_example",
        author_name="OpenClaw"
    )
    
    # Markdown table
    markdown_table = """
    | Feature | Status | Progress |
    |---------|--------|----------|
    | Core API | ✓ Complete | 100% |
    | Dashboard | ⚠ In Progress | 75% |
    | Mobile App | ◯ Planned | 0% |
    | Documentation | ✓ Complete | 100% |
    """
    
    # Convert to HTML
    html_table = TableFormatter.markdown_table_to_html(markdown_table)
    
    html_content = f"""
    <h1>Project Status Table</h1>
    <p>Current project progress across all components:</p>
    {html_table}
    <p style="font-style: italic; margin-top: 20px;">
        Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S EDT')}
    </p>
    """
    
    url = publisher.publish_html(
        title="Project Status Report",
        content=html_content,
        author="Project Manager"
    )
    
    print(f"✓ Published to: {url}")
    return url


def example_7_subagent_integration():
    """Example 7: Subagent output integration"""
    print("\n" + "="*60)
    print("Example 7: Subagent Output Integration")
    print("="*60)
    
    publisher = TelegraphPublisher()
    publisher.create_account(
        short_name="openclaw_subagent_example",
        author_name="OpenClaw"
    )
    
    # Simulate subagent output
    subagent_output = """
# Analysis Report
## Request Summary
Task: Analyze system performance metrics

## Key Findings

1. **Performance Improvement**
   - Average response time: 245ms → 180ms
   - Throughput increase: 23%
   
2. **Resource Optimization**
   - Memory usage down 15%
   - CPU utilization stable at 42%

## Code Changes
```python
def optimize_cache(cache_size):
    # Increased cache efficiency
    return cache_size * 1.3
```

## Recommendations
- Continue monitoring metrics
- Plan next optimization cycle
- Document changes in wiki

## Status
✓ Complete - Ready for deployment
"""
    
    # Use integration helper
    integration = SubagentOutputIntegration(publisher)
    url = integration.process_subagent_output(
        subagent_output,
        title="Subagent Analysis Report",
        author="Performance Analyst"
    )
    
    print(f"✓ Published to: {url}")
    return url


def run_all_examples():
    """Run all examples"""
    print("\n" + "="*70)
    print("Telegraph Publishing Examples for OpenClaw")
    print("="*70)
    
    examples = [
        ("Simple Markdown", example_1_simple_markdown),
        ("Code Documentation", example_2_code_documentation),
        ("Status Report", example_3_status_report),
        ("Blog Post", example_4_blog_post),
        ("Media Embedding", example_5_media_embedding),
        ("Table Formatting", example_6_table_formatting),
        ("Subagent Integration", example_7_subagent_integration),
    ]
    
    results = []
    
    for name, example_func in examples:
        try:
            url = example_func()
            results.append((name, url, "✓"))
        except Exception as e:
            print(f"✗ Error: {e}")
            results.append((name, str(e), "✗"))
    
    # Summary
    print("\n" + "="*70)
    print("Example Results Summary")
    print("="*70)
    
    for name, result, status in results:
        print(f"{status} {name}: {result[:80]}")
    
    print("\n✓ All examples completed!")


if __name__ == "__main__":
    # Run all examples
    run_all_examples()
