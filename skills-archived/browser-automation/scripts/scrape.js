#!/usr/bin/env node
/**
 * Web scraping tool using Playwright
 * 
 * Usage:
 *   node scrape.js <url> --selector <selector> [options]
 * 
 * Options:
 *   --selector        CSS selector for elements to scrape (required)
 *   --fields          Field mapping (name:selector,price:.price)
 *   --eval            Custom JS to evaluate
 *   --output          Output file (default: stdout)
 *   --format          Output format: json, csv (default: json)
 *   --limit           Max items to scrape
 *   --wait            Wait for selector before scraping
 */

const { chromium } = require('playwright');
const fs = require('fs').promises;
const { launchBrowser, setupDebugger, extractData } = require('./utils');

async function parseArgs() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
Web Scraper - Extract data from websites using Playwright

Usage:
  node scrape.js <url> --selector <selector> [options]

Options:
  --selector        CSS selector for elements to scrape (required)
  --fields          Field mapping (name:selector,price:.price)
  --eval            Custom JS to evaluate
  --output          Output file (default: stdout)
  --format          Output format: json, csv (default: json)
  --limit           Max items to scrape
  --wait            Wait for selector before scraping
  --browser         Browser to use (chromium, firefox, webkit)

Examples:
  node scrape.js https://shop.example.com --selector ".product"
  node scrape.js https://shop.example.com --selector ".product" --fields "name:.title,price:.price"
  node scrape.js https://example.com --eval "Array.from(document.links).map(a => a.href)"
  node scrape.js https://example.com --selector "table tr" --format csv --output data.csv
`);
    process.exit(0);
  }
  
  const config = {
    url: args[0],
    selector: null,
    fields: null,
    evalCode: null,
    output: null,
    format: 'json',
    limit: null,
    waitSelector: null,
    browser: 'chromium'
  };
  
  for (let i = 1; i < args.length; i++) {
    switch (args[i]) {
      case '--selector':
        config.selector = args[++i];
        break;
      case '--fields':
        config.fields = {};
        args[++i].split(',').forEach(field => {
          const [name, selector] = field.split(':');
          config.fields[name] = selector;
        });
        break;
      case '--eval':
        config.evalCode = args[++i];
        break;
      case '--output':
        config.output = args[++i];
        break;
      case '--format':
        config.format = args[++i];
        break;
      case '--limit':
        config.limit = parseInt(args[++i]);
        break;
      case '--wait':
        config.waitSelector = args[++i];
        break;
      case '--browser':
        config.browser = args[++i];
        break;
    }
  }
  
  if (!config.selector && !config.evalCode) {
    console.error('❌ Error: Either --selector or --eval is required');
    process.exit(1);
  }
  
  return config;
}

async function scrapeData(config) {
  console.log(`🕷️  Web scraper starting...`);
  console.log(`🌐 URL: ${config.url}`);
  
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
    
    let results;
    
    if (config.evalCode) {
      // Execute custom JavaScript
      console.log(`🧮 Executing custom code...`);
      results = await page.evaluate(new Function('', `return ${config.evalCode}`));
    } else {
      // Extract data using selectors
      console.log(`🔍 Extracting data with selector: ${config.selector}`);
      results = await extractData(page, {
        selector: config.selector,
        fields: config.fields
      });
      
      if (config.limit && results.length > config.limit) {
        results = results.slice(0, config.limit);
      }
    }
    
    console.log(`✅ Extracted ${Array.isArray(results) ? results.length : 1} items`);
    
    // Format output
    let output;
    if (config.format === 'csv' && Array.isArray(results) && results.length > 0) {
      // Convert to CSV
      const headers = Object.keys(results[0]);
      const rows = results.map(item => 
        headers.map(h => JSON.stringify(item[h] || '')).join(',')
      );
      output = [headers.join(','), ...rows].join('\n');
    } else {
      // JSON format
      output = JSON.stringify(results, null, 2);
    }
    
    // Write output
    if (config.output) {
      await fs.writeFile(config.output, output);
      console.log(`📄 Data saved to: ${config.output}`);
    } else {
      console.log('\n--- Scraped Data ---');
      console.log(output);
    }
    
    // Log any errors encountered
    if (debugData.errors.length > 0) {
      console.log('\n⚠️  Page errors detected:');
      debugData.errors.forEach(err => console.log(`  - ${err.message}`));
    }
    
  } catch (error) {
    console.error(`❌ Scraping failed:`, error.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

// Main execution
if (require.main === module) {
  parseArgs()
    .then(config => scrapeData(config))
    .catch(error => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
}

module.exports = { scrapeData };