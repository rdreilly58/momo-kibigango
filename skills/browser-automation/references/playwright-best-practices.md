# Playwright Best Practices

## Performance Optimization

### 1. Reuse Browser Contexts
Instead of launching a new browser for each operation, reuse contexts:

```javascript
const browser = await chromium.launch();
const context = await browser.newContext();

// Use the same context for multiple pages
const page1 = await context.newPage();
const page2 = await context.newPage();

// Close context when done with all pages
await context.close();
await browser.close();
```

### 2. Use Appropriate Wait Strategies
- `networkidle` - Wait until no network requests for 500ms
- `domcontentloaded` - Wait for DOMContentLoaded event
- `load` - Wait for load event
- `commit` - Wait for navigation to commit

```javascript
// Fast navigation for SPAs
await page.goto(url, { waitUntil: 'domcontentloaded' });

// Complete load for static sites
await page.goto(url, { waitUntil: 'networkidle' });
```

### 3. Efficient Selectors
Use specific selectors for better performance:

```javascript
// Good - specific selectors
await page.click('button[data-testid="submit"]');
await page.fill('#email-input', 'user@example.com');

// Avoid - generic selectors that match many elements
await page.click('button'); // Which button?
```

## Error Handling

### 1. Always Use Try-Catch
```javascript
try {
  await page.goto(url);
  await page.click('button');
} catch (error) {
  console.error('Navigation failed:', error.message);
  // Take screenshot for debugging
  await page.screenshot({ path: 'error.png' });
}
```

### 2. Set Reasonable Timeouts
```javascript
// Global timeout
page.setDefaultTimeout(30000); // 30 seconds

// Per-action timeout
await page.click('button', { timeout: 5000 });
```

### 3. Handle Navigation Properly
```javascript
// Wait for navigation after click
await Promise.all([
  page.waitForNavigation(),
  page.click('a[href="/next-page"]')
]);
```

## Memory Management

### 1. Close Pages When Done
```javascript
const page = await context.newPage();
try {
  // Do work
} finally {
  await page.close(); // Always close
}
```

### 2. Limit Concurrent Operations
```javascript
const { default: pLimit } = require('p-limit');
const limit = pLimit(3); // Max 3 concurrent browsers

const tasks = urls.map(url => 
  limit(() => processUrl(url))
);
await Promise.all(tasks);
```

## Debugging

### 1. Use Headed Mode for Development
```bash
HEADLESS=false node script.js
```

### 2. Enable DevTools
```javascript
const browser = await chromium.launch({
  devtools: true,
  headless: false
});
```

### 3. Slow Down Execution
```javascript
const browser = await chromium.launch({
  slowMo: 100 // Slow down by 100ms
});
```

### 4. Take Screenshots at Key Points
```javascript
await page.screenshot({ path: 'before-click.png' });
await page.click('button');
await page.screenshot({ path: 'after-click.png' });
```

## Security Considerations

### 1. Never Hardcode Credentials
```javascript
// Bad
await page.fill('#password', 'mypassword123');

// Good
await page.fill('#password', process.env.PASSWORD);
```

### 2. Respect Rate Limits
```javascript
// Add delays between requests
for (const url of urls) {
  await processUrl(url);
  await page.waitForTimeout(1000); // 1 second delay
}
```

### 3. Handle Sensitive Data Carefully
```javascript
// Clear sensitive fields after use
await page.fill('#credit-card', '');
await page.evaluate(() => {
  localStorage.clear();
  sessionStorage.clear();
});
```

## Common Patterns

### 1. Retry Logic
```javascript
async function retryOperation(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      console.log(`Retry ${i + 1}/${maxRetries}`);
      await new Promise(r => setTimeout(r, 1000 * (i + 1)));
    }
  }
}

// Usage
const result = await retryOperation(async () => {
  await page.goto(url);
  return await page.textContent('h1');
});
```

### 2. Parallel Processing
```javascript
async function processUrls(urls, concurrency = 3) {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  
  const limit = pLimit(concurrency);
  const tasks = urls.map(url => 
    limit(async () => {
      const page = await context.newPage();
      try {
        await page.goto(url);
        // Process page
      } finally {
        await page.close();
      }
    })
  );
  
  await Promise.all(tasks);
  await browser.close();
}
```

### 3. Event Monitoring
```javascript
// Monitor all console messages
page.on('console', msg => console.log('PAGE LOG:', msg.text()));

// Monitor errors
page.on('pageerror', error => console.error('PAGE ERROR:', error));

// Monitor requests
page.on('request', request => console.log('>>>', request.method(), request.url()));
page.on('response', response => console.log('<<<', response.status(), response.url()));
```

## Testing Patterns

### 1. Visual Regression
```javascript
const screenshot1 = await page.screenshot();
// Make changes
const screenshot2 = await page.screenshot();
// Compare screenshots with image diff library
```

### 2. API Mocking
```javascript
await page.route('**/api/*', route => {
  route.fulfill({
    status: 200,
    body: JSON.stringify({ mocked: true })
  });
});
```

### 3. Network Conditions
```javascript
// Simulate slow network
const context = await browser.newContext({
  offline: false,
  downloadThroughput: 50 * 1024, // 50kb/s
  uploadThroughput: 50 * 1024
});
```