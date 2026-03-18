#!/usr/bin/env node
/**
 * Screenshot capture tool using Playwright
 * 
 * Usage:
 *   node screenshot.js <url> [options]
 * 
 * Options:
 *   --output, -o      Output filename (default: screenshot-timestamp.png)
 *   --full-page       Capture full page (default: false)
 *   --viewports       Comma-separated list of viewports (mobile,tablet,desktop)
 *   --selector        Capture specific element
 *   --wait            Wait for selector before capture
 *   --delay           Delay in ms before capture (default: 0)
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs').promises;
const { launchBrowser, takeScreenshot, viewports } = require('./utils');

async function parseArgs() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
Screenshot Tool - Capture web pages using Playwright

Usage:
  node screenshot.js <url> [options]

Options:
  --output, -o      Output filename (default: screenshot-timestamp.png)
  --full-page       Capture full page (default: false)
  --viewports       Comma-separated list of viewports (mobile,tablet,desktop)
  --selector        Capture specific element
  --wait            Wait for selector before capture
  --delay           Delay in ms before capture (default: 0)
  --browser         Browser to use (chromium, firefox, webkit)

Examples:
  node screenshot.js https://example.com
  node screenshot.js https://example.com --full-page
  node screenshot.js https://example.com --viewports mobile,desktop
  node screenshot.js https://example.com --selector ".header" --output header.png
`);
    process.exit(0);
  }
  
  const config = {
    url: args[0],
    output: `screenshot-${Date.now()}.png`,
    fullPage: false,
    viewportList: ['desktop'],
    selector: null,
    waitSelector: null,
    delay: 0,
    browser: 'chromium'
  };
  
  for (let i = 1; i < args.length; i++) {
    switch (args[i]) {
      case '--output':
      case '-o':
        config.output = args[++i];
        break;
      case '--full-page':
        config.fullPage = true;
        break;
      case '--viewports':
        config.viewportList = args[++i].split(',');
        break;
      case '--selector':
        config.selector = args[++i];
        break;
      case '--wait':
        config.waitSelector = args[++i];
        break;
      case '--delay':
        config.delay = parseInt(args[++i]);
        break;
      case '--browser':
        config.browser = args[++i];
        break;
    }
  }
  
  return config;
}

async function captureScreenshot(config) {
  console.log(`📸 Screenshot tool starting...`);
  console.log(`🌐 URL: ${config.url}`);
  
  const { browser, context } = await launchBrowser({ browser: config.browser });
  
  try {
    for (const viewportName of config.viewportList) {
      const viewport = viewports[viewportName] || viewports.desktop;
      console.log(`\n📱 Capturing ${viewportName} view (${viewport.width}x${viewport.height})...`);
      
      // Create new page with viewport
      const page = await context.newPage();
      await page.setViewportSize(viewport);
      
      // Navigate to URL
      console.log(`🔄 Loading page...`);
      await page.goto(config.url, { waitUntil: 'networkidle' });
      
      // Wait for specific selector if requested
      if (config.waitSelector) {
        console.log(`⏳ Waiting for selector: ${config.waitSelector}`);
        await page.waitForSelector(config.waitSelector);
      }
      
      // Add delay if specified
      if (config.delay > 0) {
        console.log(`⏰ Waiting ${config.delay}ms...`);
        await page.waitForTimeout(config.delay);
      }
      
      // Determine output filename
      let outputPath = config.output;
      if (config.viewportList.length > 1) {
        const ext = path.extname(config.output);
        const base = path.basename(config.output, ext);
        outputPath = `${base}-${viewportName}${ext}`;
      }
      
      // Take screenshot
      if (config.selector) {
        console.log(`🎯 Capturing element: ${config.selector}`);
        const element = await page.$(config.selector);
        if (element) {
          await element.screenshot({ path: outputPath });
          console.log(`✅ Element screenshot saved: ${outputPath}`);
        } else {
          console.error(`❌ Element not found: ${config.selector}`);
        }
      } else {
        await takeScreenshot(page, outputPath, { fullPage: config.fullPage });
      }
      
      await page.close();
    }
    
    console.log(`\n✅ Screenshot(s) captured successfully!`);
    
  } catch (error) {
    console.error(`❌ Error capturing screenshot:`, error.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

// Main execution
if (require.main === module) {
  parseArgs()
    .then(config => captureScreenshot(config))
    .catch(error => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
}

module.exports = { captureScreenshot };