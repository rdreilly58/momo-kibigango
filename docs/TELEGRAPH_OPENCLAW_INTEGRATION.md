# Telegraph + OpenClaw Integration Guide

Complete guide to integrating Telegraph publishing with OpenClaw workflows, subagents, and automation.

## Quick Integration

### 1. Add to HEARTBEAT.md

Enable periodic Telegraph publishing in your heartbeat:

```yaml
# ~/.openclaw/workspace/HEARTBEAT.md

## Telegraph Publishing
- [ ] Publish daily status report to Telegraph
- [ ] Check for pending subagent outputs to publish
- [ ] Verify token validity and refresh if needed
```

### 2. Subagent Output Integration

Automatically publish subagent results:

```python
# In your subagent result handler
from telegraph_integration import SubagentOutputIntegration
from telegraph_publisher import TelegraphPublisher

# Initialize publisher
publisher = TelegraphPublisher()
if token_file.exists():
    token = TelegraphPublisher.load_token(str(token_file))
    publisher = TelegraphPublisher(access_token=token)
else:
    publisher.create_account()
    publisher.save_token(str(token_file))

# Publish subagent output
integration = SubagentOutputIntegration(publisher)
url = integration.process_subagent_output(
    output=subagent_result,
    title=f"Subagent Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    author="OpenClaw"
)

# Store URL in memory or send to user
print(f"Subagent output published: {url}")
```

### 3. Daily Briefing Integration

Extend daily briefing to publish to Telegraph:

```python
# In daily_briefing skill or function
from telegraph_integration import MetricsFormatter
from telegraph_publisher import TelegraphPublisher

def publish_briefing_to_telegraph(briefing_data):
    """Publish briefing to Telegraph"""
    publisher = TelegraphPublisher()
    
    # Load or create token
    token_path = Path.home() / ".openclaw" / ".telegraph_token"
    if token_path.exists():
        token = TelegraphPublisher.load_token(str(token_path))
        publisher = TelegraphPublisher(access_token=token)
    else:
        publisher.create_account()
        publisher.save_token(str(token_path))
    
    # Format briefing as status report
    html = MetricsFormatter.format_status_report(briefing_data)
    
    # Publish
    url = publisher.publish_html(
        title=f"Morning Briefing - {date.today().isoformat()}",
        content=html,
        author="OpenClaw"
    )
    
    return url
```

## Workflow Examples

### Workflow 1: Automated Report Generation

```python
# schedule_reports.py - Use with cron or heartbeat

from telegraph_publisher import TelegraphPublisher
from telegraph_integration import MetricsFormatter
from pathlib import Path
from datetime import datetime

def generate_daily_report():
    """Generate and publish daily report"""
    
    # Initialize publisher
    token_file = Path.home() / ".telegraph_token"
    if token_file.exists():
        token = TelegraphPublisher.load_token(str(token_file))
        publisher = TelegraphPublisher(access_token=token)
    else:
        publisher = TelegraphPublisher()
        publisher.create_account()
        publisher.save_token(str(token_file))
    
    # Gather metrics (pseudo-code)
    metrics = {
        "Emails Processed": "42",
        "Tasks Completed": "8",
        "API Calls": "3,421",
        "Uptime": "99.98%"
    }
    
    report_data = {
        "summary": "Daily automated report generated successfully",
        "metrics": metrics,
        "sections": {
            "System Status": "All systems operational",
            "Performance": "Average response time: 145ms",
            "Errors": "0 critical, 2 warnings"
        }
    }
    
    # Format and publish
    html = MetricsFormatter.format_status_report(report_data)
    url = publisher.publish_html(
        title=f"Daily Report - {datetime.now().strftime('%Y-%m-%d')}",
        content=html,
        author="OpenClaw Bot"
    )
    
    print(f"Report published: {url}")
    return url

if __name__ == "__main__":
    generate_daily_report()
```

### Workflow 2: Subagent Result Publishing

```python
# subagent_handler.py - Called after subagent completes

from telegraph_integration import SubagentOutputIntegration
from telegraph_publisher import TelegraphPublisher
from pathlib import Path

def handle_subagent_result(subagent_output: str, task_name: str):
    """Publish subagent results to Telegraph"""
    
    # Get or create publisher
    token_file = Path.home() / ".telegraph_token"
    publisher = TelegraphPublisher()
    
    if token_file.exists():
        token = TelegraphPublisher.load_token(str(token_file))
        publisher = TelegraphPublisher(access_token=token)
    else:
        publisher.create_account()
        publisher.save_token(str(token_file))
    
    # Publish using integration
    integration = SubagentOutputIntegration(publisher)
    url = integration.process_subagent_output(
        output=subagent_output,
        title=f"Subagent Result: {task_name}",
        author="OpenClaw"
    )
    
    # Log and return
    print(f"Subagent output published: {url}")
    return url
```

### Workflow 3: CI/CD Pipeline Integration

```python
# ci_cd_publisher.py - Publish build and test results

from telegraph_integration import CodeBlockFormatter, MetricsFormatter
from telegraph_publisher import TelegraphPublisher
from pathlib import Path
import json

def publish_build_report(build_id: str, status: str, logs: str, metrics: dict):
    """Publish CI/CD build report to Telegraph"""
    
    publisher = TelegraphPublisher()
    token_file = Path.home() / ".telegraph_token"
    
    if token_file.exists():
        token = TelegraphPublisher.load_token(str(token_file))
        publisher = TelegraphPublisher(access_token=token)
    else:
        publisher.create_account()
        publisher.save_token(str(token_file))
    
    # Format report
    html = f"""
    <h1>Build #{build_id}</h1>
    <h2>Status: {status}</h2>
    
    <h3>Metrics</h3>
    {MetricsFormatter.format_metrics(metrics)}
    
    <h3>Build Logs</h3>
    {CodeBlockFormatter.format_code_block(logs[:1000], 'log')}
    """
    
    url = publisher.publish_html(
        title=f"Build #{build_id} - {status}",
        content=html,
        author="CI/CD Pipeline"
    )
    
    return url
```

## Setup Instructions

### Step 1: Install Dependencies

```bash
cd ~/.openclaw/workspace
pip install html-telegraph-poster requests pydantic
```

### Step 2: Create Telegraph Account

```bash
# Option A: Using CLI
python scripts/telegraph-cli.py create-account --token ~/.telegraph_token

# Option B: Using Python directly
python -c "
from scripts.telegraph_publisher import TelegraphPublisher
pub = TelegraphPublisher()
token = pub.create_account()
pub.save_token('~/.telegraph_token')
print(f'Token saved: {token[:30]}...')
"
```

### Step 3: Verify Configuration

```bash
# Test connection
python scripts/telegraph-cli.py test --token ~/.telegraph_token

# Or manually
python -c "
from scripts.telegraph_publisher import TelegraphPublisher
token = TelegraphPublisher.load_token('~/.telegraph_token')
pub = TelegraphPublisher(access_token=token)
print(f'Token loaded successfully: {token[:20]}...')
"
```

### Step 4: Create Token Environment Variable (Optional)

Add to your shell profile:

```bash
# ~/.zshrc or ~/.bash_profile
export TELEGRAPH_TOKEN_PATH="$HOME/.telegraph_token"
```

Then use in scripts:

```python
import os
token_path = os.getenv('TELEGRAPH_TOKEN_PATH', str(Path.home() / '.telegraph_token'))
```

## Usage in OpenClaw Skills

### Creating a Telegraph Skill

```python
# skills/telegraph/SKILL.md

# Telegraph Publishing Skill

Publish content to Telegraph for sharing and archival.

## Usage

### Publish Markdown
telegraph.publish("title", "# Content", format="markdown")

### Publish HTML
telegraph.publish("title", "<h1>Content</h1>", format="html")

### Upload Media
telegraph.upload("path/to/image.png")
```

### Integrating with Existing Skills

```python
# In any skill that produces output

from telegraph_publisher import TelegraphPublisher
from telegraph_integration import SubagentOutputIntegration

class MySkill:
    def __init__(self):
        self.publisher = TelegraphPublisher()
        self.integration = SubagentOutputIntegration(self.publisher)
    
    def process_and_publish(self, data):
        # Process data
        output = self.process(data)
        
        # Publish to Telegraph
        url = self.integration.process_subagent_output(
            output=output,
            title="Skill Output"
        )
        
        return url
```

## Environment Configuration

### TOOLS.md Entry

Add to your TOOLS.md:

```markdown
## Telegraph Configuration (March 21, 2026)

**Setup:** Telegraph publishing for OpenClaw automation

### Token Management
- **Token File:** ~/.telegraph_token
- **Created:** March 21, 2026
- **Account:** OpenClaw
- **Status:** ✅ Active

### Quick Commands
```bash
# Publish Markdown
python scripts/telegraph-cli.py publish file.md

# Create account
python scripts/telegraph-cli.py create-account --token ~/.telegraph_token

# Test connection
python scripts/telegraph-cli.py test
```

### Integration Points
- HEARTBEAT tasks (periodic reports)
- Subagent output (auto-publishing)
- Daily briefing (briefing summaries)
- CI/CD pipeline (build reports)
```

## Monitoring & Maintenance

### Check Token Status

```bash
python -c "
from pathlib import Path
from telegraph_publisher import TelegraphPublisher

token_path = Path.home() / '.telegraph_token'
if token_path.exists():
    token = TelegraphPublisher.load_token(str(token_path))
    print(f'✓ Token found: {token[:30]}...')
else:
    print('✗ Token not found')
"
```

### Publish Test Page

```bash
python -c "
from telegraph_publisher import TelegraphPublisher
from pathlib import Path

token_path = Path.home() / '.telegraph_token'
token = TelegraphPublisher.load_token(str(token_path))
pub = TelegraphPublisher(access_token=token)

url = pub.publish_markdown('Test Page', '# Test\n\nThis is a test.')
print(f'Test page: {url}')
"
```

### Monitor Telegraph URLs

Create a file to track published pages:

```python
# ~/.openclaw/workspace/memory/telegraph_log.json

{
  "published_pages": [
    {
      "date": "2026-03-21T12:00:00Z",
      "title": "Daily Report",
      "url": "https://telegra.ph/Daily-Report-12345",
      "type": "heartbeat"
    }
  ]
}
```

## Troubleshooting

### Token Issues

```bash
# Regenerate token if needed
rm ~/.telegraph_token
python scripts/telegraph-cli.py create-account --token ~/.telegraph_token
```

### Publishing Failures

```bash
# Test connection
python scripts/telegraph-cli.py test --verbose

# Check network
curl -I https://api.telegra.ph/createAccount

# Verify Python installation
python -c "import requests; print('✓ requests installed')"
```

### Permission Issues

```bash
# Make CLI executable
chmod +x scripts/telegraph-cli.py

# Make token file readable only to user
chmod 600 ~/.telegraph_token
```

## Best Practices

1. **Token Security**
   - Store token file with user-only permissions (600)
   - Never commit token file to git
   - Use environment variables for sensitive contexts

2. **Rate Limiting**
   - Add small delays between requests in batch operations
   - Telegraph API is generous but implement backoff just in case

3. **Error Handling**
   - Always wrap Telegraph calls in try/except
   - Log failures for monitoring
   - Implement fallback strategies

4. **Content Formatting**
   - Use proper Markdown syntax
   - Validate HTML before publishing
   - Test rendering before publishing to Telegraph

5. **Scheduled Publishing**
   - Use heartbeat for periodic tasks
   - Implement idempotency (same input = same output)
   - Log all published URLs for reference

## Advanced Integration

### Custom Skill

Create a Telegraph skill:

```bash
mkdir -p ~/.openclaw/workspace/skills/telegraph
cd ~/.openclaw/workspace/skills/telegraph

# Create SKILL.md
cat > SKILL.md << 'EOF'
# Telegraph Skill

Publish content to Telegraph.

## Commands

telegraph publish [file] [--title TITLE] [--format FORMAT]
telegraph upload [file]
telegraph test
EOF
```

### Python Package

Create a reusable package:

```python
# setup.py
from setuptools import setup

setup(
    name="openclaw-telegraph",
    version="1.0.0",
    packages=["telegraph"],
    install_requires=[
        "html-telegraph-poster>=1.0.0",
        "requests>=2.28.0",
        "pydantic>=2.0.0"
    ]
)
```

## Support & Documentation

- **Full Documentation:** `docs/TELEGRAPH_IMPLEMENTATION.md`
- **Examples:** `examples/telegraph_examples.py`
- **Configuration:** `config/telegraph.json`
- **CLI Help:** `python scripts/telegraph-cli.py --help`

---

**Status:** ✅ Ready for OpenClaw Integration

**Next:** Follow setup instructions above to get started!
