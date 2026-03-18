# Browser Automation Skill

Automate web browsers using Playwright for testing, monitoring, scraping, and debugging web applications.

## Overview

This skill provides powerful browser automation capabilities using Playwright, supporting:
- Web scraping and data extraction
- Automated testing and debugging
- Visual regression testing with screenshots
- Site monitoring and health checks
- Form automation and interaction
- Multi-browser support (Chrome, Firefox, WebKit)

## Installation

```bash
# Install Playwright globally
npm install -g playwright

# Install browsers
npx playwright install
```

## Key Capabilities

### 1. Debug Web Applications
```bash
# Debug admin panel hanging issue
node ~/.openclaw/workspace/skills/browser-automation/scripts/debug-page.js https://example.com/admin

# Custom debugging with options
HEADLESS=false DEVTOOLS=true node scripts/debug-page.js https://example.com
```

### 2. Monitor Deployments
```bash
# Monitor Vercel deployment
node ~/.openclaw/workspace/skills/browser-automation/scripts/monitor-deployment.js

# Single check mode
node scripts/monitor-deployment.js once

# With custom site URL
SITE_URL=https://mysite.vercel.app node scripts/monitor-deployment.js
```

### 3. Take Screenshots
```bash
# Simple screenshot
node ~/.openclaw/workspace/skills/browser-automation/scripts/screenshot.js https://example.com

# Full page screenshot
node scripts/screenshot.js https://example.com --full-page

# Multiple viewports
node scripts/screenshot.js https://example.com --viewports mobile,tablet,desktop
```

### 4. Extract Data
```bash
# Scrape structured data
node ~/.openclaw/workspace/skills/browser-automation/scripts/scrape.js https://example.com --selector ".item"

# Extract with custom script
node scripts/scrape.js https://example.com --eval "document.title"
```

### 5. Form Automation
```bash
# Fill and submit forms
node ~/.openclaw/workspace/skills/browser-automation/scripts/form-fill.js https://example.com/form --data form-data.json
```

## Core Scripts

### `debug-page.js`
Comprehensive page debugger that:
- Monitors network requests
- Captures console logs and errors
- Takes progressive screenshots
- Analyzes page load performance
- Detects authentication requirements
- Saves all debug data to organized output directory

### `monitor-deployment.js`
Deployment monitoring tool that:
- Checks site availability repeatedly
- Takes screenshots of deployment progress
- Validates page health (React roots, error messages)
- Generates HTML reports with screenshots
- Exits with appropriate status codes for CI/CD

### `screenshot.js`
Versatile screenshot tool supporting:
- Multiple browsers (chromium, firefox, webkit)
- Various viewports (mobile, tablet, desktop)
- Full page captures
- Element-specific screenshots
- Batch processing of multiple URLs

### `scrape.js`
Data extraction tool featuring:
- CSS/XPath selector support
- Custom JavaScript evaluation
- JSON output formatting
- Pagination handling
- Rate limiting for polite scraping

### `form-fill.js`
Form automation supporting:
- JSON-based form data
- File uploads
- Multi-step forms
- CAPTCHA detection
- Form validation checking

## Usage Examples

### Debug a Hanging Page
```bash
# Investigate admin panel that won't load
URL=https://mysite.com/admin node ~/.openclaw/workspace/skills/browser-automation/scripts/debug-page.js

# Check output
ls -la /tmp/admin-debug-*/
open /tmp/admin-debug-*/1-initial-load.png
cat /tmp/admin-debug-*/network-log.json | jq '.[] | select(.status >= 400)'
```

### Monitor Production Deployment
```bash
# Watch deployment progress
SITE_URL=https://myapp.vercel.app node scripts/monitor-deployment.js

# Use in CI/CD pipeline
node scripts/monitor-deployment.js once || echo "Deployment failed!"
```

### Visual Regression Testing
```bash
# Capture baseline screenshots
node scripts/screenshot.js https://mysite.com --output baseline.png

# After changes, compare
node scripts/screenshot.js https://mysite.com --output current.png
```

### Extract Structured Data
```bash
# Scrape product listings
node scripts/scrape.js https://shop.example.com \
  --selector ".product" \
  --fields "name:.title,price:.price,image:img@src" \
  --output products.json
```

## Environment Variables

- `HEADLESS` - Run browser in headless mode (default: true)
- `DEVTOOLS` - Open browser devtools (default: false)  
- `BROWSER` - Browser to use: chromium|firefox|webkit (default: chromium)
- `TIMEOUT` - Default navigation timeout in ms (default: 30000)
- `VIEWPORT_WIDTH` - Default viewport width (default: 1280)
- `VIEWPORT_HEIGHT` - Default viewport height (default: 720)

## Advanced Usage

### Custom Automation Scripts
Create your own automation by importing the utilities:

```javascript
const { launchBrowser, setupDebugger, takeScreenshot } = require('./scripts/utils');

async function myAutomation() {
  const { browser, context } = await launchBrowser();
  const page = await context.newPage();
  
  // Set up debugging
  const debugData = setupDebugger(page);
  
  // Your automation logic here
  await page.goto('https://example.com');
  await page.click('button.submit');
  
  // Save results
  await takeScreenshot(page, 'result.png');
  await browser.close();
}
```

### Parallel Execution
Run multiple automations concurrently:

```javascript
const { chromium } = require('playwright');
const pLimit = require('p-limit');

const limit = pLimit(3); // Max 3 concurrent browsers

const urls = ['url1', 'url2', 'url3', ...];
const tasks = urls.map(url => limit(() => processUrl(url)));
await Promise.all(tasks);
```

## Best Practices

1. **Error Handling**: Always wrap navigation in try-catch blocks
2. **Timeouts**: Set reasonable timeouts for different operations
3. **Cleanup**: Close browsers properly to avoid memory leaks
4. **Rate Limiting**: Be respectful when scraping external sites
5. **Debugging**: Use `HEADLESS=false` to see what's happening
6. **Screenshots**: Take screenshots at key points for debugging
7. **Logging**: Use structured logging for easier analysis

## Troubleshooting

### Browser Won't Launch
```bash
# Reinstall browsers
npx playwright install --force

# Check system dependencies
npx playwright install-deps
```

### Timeout Errors
```javascript
// Increase timeout for slow sites
await page.goto(url, { timeout: 60000 });

// Wait for specific elements
await page.waitForSelector('.content', { timeout: 10000 });
```

### Memory Issues
```javascript
// Close pages after use
await page.close();

// Reuse contexts for multiple pages
const context = await browser.newContext();
// ... use context for multiple pages
await context.close();
```

## Script Templates

All scripts follow a similar pattern for consistency:

```javascript
#!/usr/bin/env node
const { chromium } = require('playwright');

async function main() {
  const browser = await chromium.launch({
    headless: process.env.HEADLESS !== 'false'
  });
  
  try {
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Your automation here
    
  } catch (error) {
    console.error('Automation failed:', error);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

if (require.main === module) {
  main();
}
```

## Integration with OpenClaw

This skill integrates seamlessly with OpenClaw workflows:

```bash
# Use in OpenClaw commands
openclaw exec "node ~/.openclaw/workspace/skills/browser-automation/scripts/screenshot.js https://example.com"

# Schedule monitoring
openclaw cron add "0 */6 * * *" "node ~/.openclaw/workspace/skills/browser-automation/scripts/monitor-deployment.js once"
```

## Security Considerations

- Never hardcode credentials in scripts
- Use environment variables for sensitive data
- Be cautious with `--eval` option in scraping
- Respect robots.txt and rate limits
- Don't automate CAPTCHAs or anti-bot measures

## References

- [Playwright Documentation](https://playwright.dev/docs/intro)
- [Playwright API Reference](https://playwright.dev/docs/api/class-playwright)
- [Best Practices Guide](references/playwright-best-practices.md)
- [Example Scripts](scripts/)