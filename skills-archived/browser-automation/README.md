# Browser Automation Skill

This skill provides comprehensive browser automation capabilities using Playwright.

## Quick Start

```bash
# Take a screenshot
node scripts/screenshot.js https://example.com

# Debug a problematic page
node scripts/debug-page.js https://example.com/admin

# Scrape data from a website
node scripts/scrape.js https://example.com --selector ".item"

# Monitor deployment
node scripts/monitor-deployment.js
```

## Features

- 🔍 **Page Debugging** - Diagnose issues with comprehensive logging
- 📸 **Screenshots** - Capture pages in multiple viewports
- 🕷️ **Web Scraping** - Extract structured data from websites
- 📝 **Form Automation** - Fill and submit forms automatically
- 📊 **Deployment Monitoring** - Track site deployments with visual reports
- 🌐 **Multi-browser Support** - Chrome, Firefox, and WebKit

## Requirements

- Node.js 14+
- Playwright browsers (installed automatically)

## Installation

```bash
cd ~/.openclaw/workspace/skills/browser-automation
npm install
```

## Documentation

See [SKILL.md](SKILL.md) for complete documentation and examples.

## License

MIT