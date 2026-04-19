#!/usr/bin/env node
/**
 * Form automation tool using Playwright
 * 
 * Usage:
 *   node form-fill.js <url> --data <json-file> [options]
 * 
 * Options:
 *   --data            JSON file with form data (required)
 *   --submit          Submit form after filling (default: true)
 *   --screenshot      Take screenshot after filling
 *   --wait            Wait for selector before filling
 */

const { chromium } = require('playwright');
const fs = require('fs').promises;
const path = require('path');
const { launchBrowser, setupDebugger, takeScreenshot } = require('./utils');

async function parseArgs() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
Form Automation - Fill and submit web forms using Playwright

Usage:
  node form-fill.js <url> --data <json-file> [options]

Options:
  --data            JSON file with form data (required)
  --submit          Submit form after filling (default: true)
  --screenshot      Take screenshot after filling
  --wait            Wait for selector before filling
  --browser         Browser to use (chromium, firefox, webkit)

JSON Data Format:
{
  "fields": {
    "#email": "user@example.com",
    "#password": "secret123",
    "input[name='firstName']": "John",
    "select#country": "US",
    "input[type='checkbox']": true,
    "textarea#message": "Hello world"
  },
  "submitButton": "button[type='submit']"
}

Examples:
  node form-fill.js https://example.com/form --data form-data.json
  node form-fill.js https://example.com/login --data login.json --screenshot
  node form-fill.js https://example.com/signup --data signup.json --submit false
`);
    process.exit(0);
  }
  
  const config = {
    url: args[0],
    dataFile: null,
    submit: true,
    screenshot: false,
    waitSelector: null,
    browser: 'chromium'
  };
  
  for (let i = 1; i < args.length; i++) {
    switch (args[i]) {
      case '--data':
        config.dataFile = args[++i];
        break;
      case '--submit':
        config.submit = args[++i] !== 'false';
        break;
      case '--screenshot':
        config.screenshot = true;
        break;
      case '--wait':
        config.waitSelector = args[++i];
        break;
      case '--browser':
        config.browser = args[++i];
        break;
    }
  }
  
  if (!config.dataFile) {
    console.error('❌ Error: --data argument is required');
    process.exit(1);
  }
  
  return config;
}

async function fillForm(config) {
  console.log(`📝 Form automation starting...`);
  console.log(`🌐 URL: ${config.url}`);
  
  // Load form data
  let formData;
  try {
    const dataContent = await fs.readFile(config.dataFile, 'utf-8');
    formData = JSON.parse(dataContent);
    console.log(`📄 Loaded form data from: ${config.dataFile}`);
  } catch (error) {
    console.error(`❌ Error loading form data:`, error.message);
    process.exit(1);
  }
  
  const { browser, context } = await launchBrowser({ browser: config.browser });
  
  try {
    const page = await context.newPage();
    const debugData = setupDebugger(page);
    
    // Navigate to URL
    console.log(`🔄 Loading page...`);
    await page.goto(config.url, { waitUntil: 'networkidle' });
    
    // Wait for specific selector if requested
    if (config.waitSelector) {
      console.log(`⏳ Waiting for selector: ${config.waitSelector}`);
      await page.waitForSelector(config.waitSelector, { timeout: 30000 });
    }
    
    // Fill form fields
    if (formData.fields) {
      console.log(`\n🖊️  Filling form fields...`);
      
      for (const [selector, value] of Object.entries(formData.fields)) {
        try {
          console.log(`  📍 ${selector} = ${typeof value === 'string' ? value : JSON.stringify(value)}`);
          
          // Wait for element
          await page.waitForSelector(selector, { timeout: 5000 });
          
          // Get element type
          const element = await page.$(selector);
          const tagName = await element.evaluate(el => el.tagName.toLowerCase());
          const type = await element.evaluate(el => el.type);
          
          // Fill based on element type
          if (tagName === 'select') {
            await page.selectOption(selector, value);
          } else if (type === 'checkbox' || type === 'radio') {
            if (value) {
              await page.check(selector);
            } else {
              await page.uncheck(selector);
            }
          } else if (tagName === 'textarea' || tagName === 'input') {
            await page.fill(selector, value.toString());
          } else {
            console.warn(`  ⚠️  Unknown element type for selector: ${selector}`);
          }
          
        } catch (error) {
          console.error(`  ❌ Error filling ${selector}:`, error.message);
        }
      }
    }
    
    // Take screenshot if requested
    if (config.screenshot) {
      const screenshotPath = `form-filled-${Date.now()}.png`;
      await takeScreenshot(page, screenshotPath, { fullPage: true });
    }
    
    // Submit form if requested
    if (config.submit && formData.submitButton) {
      console.log(`\n🚀 Submitting form...`);
      console.log(`  📍 Submit button: ${formData.submitButton}`);
      
      // Click submit and wait for navigation
      await Promise.all([
        page.waitForNavigation({ waitUntil: 'networkidle' }).catch(() => {}),
        page.click(formData.submitButton)
      ]);
      
      console.log(`✅ Form submitted`);
      console.log(`📍 New URL: ${page.url()}`);
      
      // Take screenshot of result page
      if (config.screenshot) {
        const resultPath = `form-result-${Date.now()}.png`;
        await takeScreenshot(page, resultPath, { fullPage: true });
      }
      
      // Check for success/error messages
      const messages = await page.evaluate(() => {
        const selectors = [
          '.success', '.error', '.alert', '.message',
          '[role="alert"]', '[class*="error"]', '[class*="success"]'
        ];
        
        const found = [];
        selectors.forEach(sel => {
          document.querySelectorAll(sel).forEach(el => {
            if (el.textContent.trim()) {
              found.push({
                selector: sel,
                text: el.textContent.trim()
              });
            }
          });
        });
        
        return found;
      });
      
      if (messages.length > 0) {
        console.log(`\n📋 Form messages:`);
        messages.forEach(msg => {
          console.log(`  - ${msg.text}`);
        });
      }
    }
    
    // Log any errors
    if (debugData.errors.length > 0) {
      console.log('\n⚠️  JavaScript errors detected:');
      debugData.errors.forEach(err => console.log(`  - ${err.message}`));
    }
    
    console.log(`\n✅ Form automation complete!`);
    
  } catch (error) {
    console.error(`❌ Form automation failed:`, error.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

// Main execution
if (require.main === module) {
  parseArgs()
    .then(config => fillForm(config))
    .catch(error => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
}

module.exports = { fillForm };