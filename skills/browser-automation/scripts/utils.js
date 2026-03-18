/**
 * Shared utilities for browser automation scripts
 */

const { chromium, firefox, webkit } = require('playwright');

/**
 * Launch browser with common configuration
 */
async function launchBrowser(options = {}) {
  const browserType = options.browser || process.env.BROWSER || 'chromium';
  const browsers = { chromium, firefox, webkit };
  
  if (!browsers[browserType]) {
    throw new Error(`Unknown browser: ${browserType}`);
  }
  
  const browser = await browsers[browserType].launch({
    headless: process.env.HEADLESS !== 'false',
    devtools: process.env.DEVTOOLS === 'true',
    ...options.launchOptions
  });
  
  const context = await browser.newContext({
    viewport: {
      width: parseInt(process.env.VIEWPORT_WIDTH) || 1280,
      height: parseInt(process.env.VIEWPORT_HEIGHT) || 720
    },
    ...options.contextOptions
  });
  
  return { browser, context };
}

/**
 * Setup debug listeners on a page
 */
function setupDebugger(page) {
  const debugData = {
    requests: [],
    responses: [],
    console: [],
    errors: []
  };
  
  page.on('request', request => {
    debugData.requests.push({
      time: Date.now(),
      url: request.url(),
      method: request.method(),
      type: request.resourceType()
    });
  });
  
  page.on('response', response => {
    debugData.responses.push({
      time: Date.now(),
      url: response.url(),
      status: response.status(),
      statusText: response.statusText()
    });
  });
  
  page.on('console', msg => {
    debugData.console.push({
      time: Date.now(),
      type: msg.type(),
      text: msg.text()
    });
  });
  
  page.on('pageerror', error => {
    debugData.errors.push({
      time: Date.now(),
      message: error.message,
      stack: error.stack
    });
  });
  
  return debugData;
}

/**
 * Take screenshot with options
 */
async function takeScreenshot(page, outputPath, options = {}) {
  const screenshotOptions = {
    path: outputPath,
    fullPage: options.fullPage || false,
    ...options
  };
  
  await page.screenshot(screenshotOptions);
  console.log(`📸 Screenshot saved: ${outputPath}`);
}

/**
 * Wait with timeout and error handling
 */
async function waitForWithTimeout(page, selector, timeout = 30000) {
  try {
    await page.waitForSelector(selector, { timeout });
    return true;
  } catch (error) {
    console.warn(`⚠️  Timeout waiting for selector: ${selector}`);
    return false;
  }
}

/**
 * Extract data using selectors
 */
async function extractData(page, config) {
  return await page.evaluate((cfg) => {
    const results = [];
    const elements = document.querySelectorAll(cfg.selector);
    
    elements.forEach(element => {
      const data = {};
      
      if (cfg.fields) {
        Object.entries(cfg.fields).forEach(([key, selector]) => {
          let value = null;
          
          if (selector.includes('@')) {
            const [sel, attr] = selector.split('@');
            const el = sel ? element.querySelector(sel) : element;
            value = el ? el.getAttribute(attr) : null;
          } else {
            const el = element.querySelector(selector);
            value = el ? el.textContent.trim() : null;
          }
          
          data[key] = value;
        });
      } else {
        data.text = element.textContent.trim();
      }
      
      results.push(data);
    });
    
    return results;
  }, config);
}

/**
 * Common viewport configurations
 */
const viewports = {
  mobile: { width: 375, height: 667 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1920, height: 1080 },
  '4k': { width: 3840, height: 2160 }
};

module.exports = {
  launchBrowser,
  setupDebugger,
  takeScreenshot,
  waitForWithTimeout,
  extractData,
  viewports
};