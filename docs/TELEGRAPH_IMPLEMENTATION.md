# Telegraph Implementation for OpenClaw

Complete implementation of Telegraph publishing support for OpenClaw, with Python and JavaScript/TypeScript implementations.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Python Implementation](#python-implementation)
4. [JavaScript/TypeScript Implementation](#javascripttypescript-implementation)
5. [Configuration](#configuration)
6. [Integration Patterns](#integration-patterns)
7. [CLI Usage](#cli-usage)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Overview

Telegraph is a lightweight publishing platform that enables rapid content distribution. This implementation provides:

- **Python wrapper** (`telegraph_publisher.py`) with full Telegraph API support
- **TypeScript wrapper** (`telegraph_publisher.ts`) for Deno and Node.js
- **Integration modules** for subagent output, heartbeat tasks, and automation
- **CLI tool** for command-line publishing
- **Examples** demonstrating all major use cases
- **Tests** covering core functionality

### Features

✅ Publish Markdown and HTML content
✅ Automatic account creation and token management
✅ Media upload support (images, videos)
✅ Page updates and retrieval
✅ Error handling with exponential backoff retries
✅ Full TypeScript support with strong typing
✅ Works in both Deno and Node.js
✅ Integration with OpenClaw automation workflows
✅ CLI interface for manual publishing
✅ Comprehensive documentation and examples

## Quick Start

### Python

```python
from telegraph_publisher import TelegraphPublisher

# Create publisher
publisher = TelegraphPublisher()

# Create account (or use existing token)
token = publisher.create_account()

# Publish Markdown
url = publisher.publish_markdown(
    title="Hello Telegraph",
    content="# Welcome\n\nThis is my first post!"
)
print(f"Published: {url}")

# Save token for later use
publisher.save_token("~/.telegraph_token")
```

### TypeScript/Deno

```typescript
import TelegraphPublisher from "./telegraph_publisher.ts";

// Create publisher
const publisher = new TelegraphPublisher();

// Create account
const token = await publisher.createAccount();

// Publish Markdown
const url = await publisher.publishMarkdown(
  "Hello Telegraph",
  "# Welcome\n\nThis is my first post!"
);
console.log(`Published: ${url}`);

// Save token
await publisher.saveToken("~/.telegraph_token");
```

## Python Implementation

### Installation

```bash
# Install dependencies
pip install html-telegraph-poster requests pydantic

# Or add to requirements.txt
html-telegraph-poster>=1.0.0
requests>=2.28.0
pydantic>=2.0.0
```

### TelegraphPublisher Class

#### Methods

##### `create_account(short_name, author_name, author_url) -> str`

Create a new Telegraph account and return access token.

```python
publisher = TelegraphPublisher()
token = publisher.create_account(
    short_name="my_app",
    author_name="My App",
    author_url="https://myapp.com"
)
```

##### `publish_markdown(title, content, author, author_url) -> str`

Publish Markdown content to Telegraph.

```python
url = publisher.publish_markdown(
    title="My Post",
    content="# Hello\n\nThis is **bold**",
    author="Bob"
)
```

##### `publish_html(title, content, author, author_url) -> str`

Publish HTML content to Telegraph.

```python
url = publisher.publish_html(
    title="My Post",
    content="<h1>Hello</h1><p>This is <strong>bold</strong></p>",
    author="Bob"
)
```

##### `update_page(path, content, title, author, author_url) -> str`

Update an existing Telegraph page.

```python
url = publisher.update_page(
    path="my-post-12345",
    content="<p>Updated content</p>",
    title="Updated Title"
)
```

##### `get_page(path, return_content) -> Dict`

Retrieve page information and optionally content.

```python
page = publisher.get_page("my-post-12345", return_content=True)
print(page["title"])
print(page["url"])
```

##### `upload_media(file_path) -> str`

Upload media file and return Telegraph URL.

```python
media_url = publisher.upload_media("path/to/image.png")
html = f"<img src='{media_url}' alt='My Image'>"
```

#### Token Management

```python
# Save token for later use
publisher.save_token("~/.telegraph_token")

# Load token
token = TelegraphPublisher.load_token("~/.telegraph_token")
publisher = TelegraphPublisher(access_token=token)
```

### Integration Module

#### CodeBlockFormatter

Format code blocks with language specification:

```python
from telegraph_integration import CodeBlockFormatter

code = "def hello():\n    print('Hello')"
html = CodeBlockFormatter.format_code_block(code, "python")
```

#### TableFormatter

Convert Markdown tables to HTML:

```python
from telegraph_integration import TableFormatter

markdown_table = """
| Col 1 | Col 2 |
|-------|-------|
| A     | B     |
"""
html = TableFormatter.markdown_table_to_html(markdown_table)
```

#### MetricsFormatter

Format metrics and status reports:

```python
from telegraph_integration import MetricsFormatter

metrics = {
    "Uptime": "99.9%",
    "Latency": "145ms"
}
html = MetricsFormatter.format_metrics(metrics)
```

#### SubagentOutputIntegration

Auto-publish subagent results:

```python
from telegraph_integration import SubagentOutputIntegration

integration = SubagentOutputIntegration(publisher)
url = integration.process_subagent_output(
    output="# Report\n\nAnalysis complete",
    title="Analysis Report"
)
```

## JavaScript/TypeScript Implementation

### Installation

#### Deno

```bash
# No installation needed - uses standard library
deno run --allow-net examples/telegraph_examples.ts
```

#### Node.js

```bash
npm install @dcdunkan/telegraph marked jsdom
# Or
yarn add @dcdunkan/telegraph marked jsdom
```

### TelegraphPublisher Class

#### Methods

##### `async createAccount(shortName, authorName, authorUrl) -> string`

Create a new Telegraph account and return access token.

```typescript
const publisher = new TelegraphPublisher();
const token = await publisher.createAccount(
  "my_app",
  "My App",
  "https://myapp.com"
);
```

##### `async publishMarkdown(title, content, author, authorUrl) -> string`

Publish Markdown content to Telegraph.

```typescript
const url = await publisher.publishMarkdown(
  "My Post",
  "# Hello\n\nThis is **bold**",
  "Bob"
);
```

##### `async publishHtml(title, content, author, authorUrl) -> string`

Publish HTML content to Telegraph.

```typescript
const url = await publisher.publishHtml(
  "My Post",
  "<h1>Hello</h1><p>This is <strong>bold</strong></p>",
  "Bob"
);
```

##### `async updatePage(path, content, title, author, authorUrl) -> string`

Update an existing Telegraph page.

```typescript
const url = await publisher.updatePage(
  "my-post-12345",
  "<p>Updated content</p>",
  "Updated Title"
);
```

##### `async getPage(path, returnContent) -> PageResult`

Retrieve page information.

```typescript
const page = await publisher.getPage("my-post-12345", true);
console.log(page.title);
console.log(page.url);
```

##### `async uploadMedia(filePath) -> string`

Upload media file and return Telegraph URL.

```typescript
const mediaUrl = await publisher.uploadMedia("path/to/image.png");
const html = `<img src='${mediaUrl}' alt='My Image'>`;
```

#### Token Management

```typescript
// Save token for later use
await publisher.saveToken("~/.telegraph_token");

// Load token
const token = await TelegraphPublisher.loadToken("~/.telegraph_token");
const publisher = new TelegraphPublisher(token);
```

### Integration Module

#### CodeBlockFormatter

```typescript
import { CodeBlockFormatter } from "./telegraph_integration.ts";

const code = "function hello() { console.log('Hello'); }";
const html = CodeBlockFormatter.formatCodeBlock(code, "javascript");
```

#### TableFormatter

```typescript
import { TableFormatter } from "./telegraph_integration.ts";

const markdownTable = `
| Col 1 | Col 2 |
|-------|-------|
| A     | B     |
`;
const html = TableFormatter.markdownTableToHtml(markdownTable);
```

#### MetricsFormatter

```typescript
import { MetricsFormatter } from "./telegraph_integration.ts";

const metrics = {
  "Uptime": "99.9%",
  "Latency": "145ms"
};
const html = MetricsFormatter.formatMetrics(metrics);
```

#### MediaHandler

```typescript
import { MediaHandler } from "./telegraph_integration.ts";

const mediaHandler = new MediaHandler(publisher);
const mediaUrl = await mediaHandler.uploadMedia("image.png");

// Create embed
const imageEmbed = mediaHandler.createImageEmbed(mediaUrl);
const videoEmbed = mediaHandler.createVideoEmbed("dQw4w9WgXcQ");
```

## Configuration

Configuration is managed in `config/telegraph.json`:

```json
{
  "api": {
    "base_url": "https://api.telegra.ph",
    "timeout": 30,
    "max_retries": 3
  },
  "defaults": {
    "author": "OpenClaw",
    "author_url": "https://github.com/anthropics/openclaw"
  },
  "features": {
    "media_upload": true,
    "auto_publish": true,
    "syntax_highlighting": true
  }
}
```

### Custom Configuration

#### Python

```python
from telegraph_publisher import TelegraphConfig, TelegraphPublisher

config = TelegraphConfig(
    max_retries=5,
    timeout=60,
    default_author="Custom Author"
)
publisher = TelegraphPublisher(config=config)
```

#### TypeScript

```typescript
const config: Partial<TelegraphConfig> = {
  maxRetries: 5,
  timeout: 60000,
  defaultAuthor: "Custom Author"
};
const publisher = new TelegraphPublisher(undefined, config);
```

## Integration Patterns

### Pattern 1: Subagent Output Auto-Publishing

Automatically publish subagent results:

```python
# In subagent result handler
from telegraph_integration import SubagentOutputIntegration

integration = SubagentOutputIntegration(publisher)
url = integration.process_subagent_output(subagent_output)
# Subagent results now available at Telegraph URL
```

### Pattern 2: Heartbeat Reports

Publish periodic heartbeat status reports:

```python
from telegraph_integration import TelegraphHeartbeatIntegration

heartbeat = TelegraphHeartbeatIntegration(publisher, token_path)
url = await heartbeat.publish_heartbeat_report({
    "summary": "All systems operational",
    "metrics": {"uptime": "99.99%"}
})
```

### Pattern 3: CI/CD Pipeline Integration

Publish build reports:

```python
# In CI/CD pipeline
integration = SubagentOutputIntegration(publisher)
url = integration.process_subagent_output(
    output=build_report,
    title=f"Build #{build_id}"
)
# Post URL to PR/commit
```

### Pattern 4: Daily Briefings

Publish daily briefing summaries:

```python
briefing_data = {
    "summary": "Daily briefing for ...",
    "metrics": {
        "emails": "12 new",
        "tasks": "8 completed",
        "meetings": "3 scheduled"
    },
    "sections": {
        "Calendar": "3 events scheduled",
        "Tasks": "8/15 completed (53%)"
    }
}
url = await publisher.publishHtml(
    title=f"Daily Briefing - {date.today()}",
    content=MetricsFormatter.formatStatusReport(briefing_data)
)
```

## CLI Usage

### Publish Command

Publish Markdown or HTML files:

```bash
# Publish Markdown file
telegraph publish README.md --title "My Document"

# Publish HTML file
telegraph publish index.html --format html --author "John Doe"

# Save token for future use
telegraph publish file.md --token ~/.telegraph_token

# Output as JSON
telegraph publish file.md --output json
```

### Create Account

Create a new Telegraph account:

```bash
# Auto-generate short name
telegraph create-account

# Custom short name
telegraph create-account --name my-app --author "My App"

# Save token
telegraph create-account --name my-app --token ~/.telegraph_token
```

### Upload Media

Upload media files:

```bash
# Upload image
telegraph upload-media image.png

# Output as URL only
telegraph upload-media image.png --output url
```

### Configuration

Manage configuration:

```bash
# Set access token
telegraph config --set-token YOUR_TOKEN_HERE

# Show current configuration
telegraph config --show-config

# Test connection
telegraph test --token ~/.telegraph_token
```

## Best Practices

### 1. Token Management

```python
# Save tokens securely
publisher.save_token("~/.telegraph_token")

# Load from file
token = TelegraphPublisher.load_token("~/.telegraph_token")
```

### 2. Error Handling

```python
try:
    url = publisher.publish_markdown(title, content)
except Exception as e:
    logger.error(f"Publication failed: {e}")
    # Fallback or retry logic
```

### 3. Markdown Formatting

```python
# Use proper Markdown syntax
content = """
# Main Title

## Subtitle

**Bold text** and *italic text*

- List item 1
- List item 2

```python
code_block()
```

[Link text](https://example.com)
"""
```

### 4. Media Embedding

```python
# Publish with embedded media
media_url = publisher.upload_media("image.png")
html_content = f"""
<h1>My Post</h1>
<img src="{media_url}" alt="My Image" style="max-width: 500px;">
<p>Content here</p>
"""
url = publisher.publish_html("My Post", html_content)
```

### 5. Batch Publishing

```python
# Publish multiple pages efficiently
urls = []
for content in contents:
    url = publisher.publish_markdown(content["title"], content["body"])
    urls.append(url)
    time.sleep(0.1)  # Rate limiting
```

## Troubleshooting

### Issue: "Access token required"

**Solution:** Create account or load token:

```python
# Create new account
token = publisher.create_account()

# Or load existing token
publisher = TelegraphPublisher(access_token=loaded_token)
```

### Issue: "API error: Unknown error"

**Solution:** Check Telegraph API status and retry:

```python
# Automatic retry with exponential backoff is built-in
# If still failing, check:
# 1. API endpoint availability
# 2. Network connectivity
# 3. Request payload formatting
```

### Issue: Media upload fails

**Solution:** Verify file exists and is readable:

```python
from pathlib import Path

file_path = Path("image.png")
if not file_path.exists():
    raise FileNotFoundError(f"File not found: {file_path}")

if not os.access(file_path, os.R_OK):
    raise PermissionError(f"Cannot read: {file_path}")

url = publisher.upload_media(str(file_path))
```

### Issue: Token file not found

**Solution:** Create account first:

```python
# If token file doesn't exist, create new account
token_path = Path.home() / ".telegraph_token"
if not token_path.exists():
    publisher = TelegraphPublisher()
    token = publisher.create_account()
    publisher.save_token(str(token_path))
else:
    token = TelegraphPublisher.load_token(str(token_path))
    publisher = TelegraphPublisher(access_token=token)
```

## Advanced Usage

### Custom HTML Templates

```python
template = """
<html>
<head>
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; }}
        code {{ background: #f0f0f0; padding: 2px 4px; }}
    </style>
</head>
<body>
{content}
</body>
</html>
"""

html_content = template.format(content="Your content here")
url = publisher.publish_html("My Post", html_content)
```

### Dynamic Content Generation

```python
from telegraph_integration import MetricsFormatter

# Generate from data
metrics = {f"Metric {i}": f"{100-i}%" for i in range(5)}
html = MetricsFormatter.format_metrics(metrics)

url = publisher.publish_html("Metrics Report", html)
```

### Scheduled Publishing

```python
import schedule
import time

def publish_daily_report():
    content = generate_daily_report()
    url = publisher.publish_markdown(f"Daily {date.today()}", content)
    logger.info(f"Published: {url}")

schedule.every().day.at("09:00").do(publish_daily_report)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Support

For issues or questions:

1. Check this documentation
2. Review examples in `examples/`
3. Check tests in `tests/` for usage patterns
4. Report issues with detailed error messages

## License

This implementation is part of OpenClaw and follows the same license terms.
