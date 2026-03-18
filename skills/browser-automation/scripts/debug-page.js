#!/usr/bin/env node
/**
 * Admin Panel Debugger for ReillyDesignStudio
 * 
 * This script investigates the hanging /admin issue by:
 * 1. Loading the admin page
 * 2. Monitoring network requests
 * 3. Capturing console errors
 * 4. Taking screenshots at key stages
 * 5. Checking for auth redirects or infinite loops
 */

const { chromium } = require('playwright');
const fs = require('fs').promises;
const path = require('path');

// Configuration
const ADMIN_URL = process.env.ADMIN_URL || 'https://reillydesignstudio.com/admin';
const TIMEOUT = 30000; // 30 seconds
const DEBUG_DIR = '/tmp/admin-debug-' + Date.now();

async function debugAdminPanel() {
  console.log('🔍 Starting Admin Panel Debug...');
  console.log(`📍 Target URL: ${ADMIN_URL}`);
  console.log(`📂 Debug output: ${DEBUG_DIR}`);
  
  // Create debug directory
  await fs.mkdir(DEBUG_DIR, { recursive: true });
  
  // Launch browser with debugging enabled
  const browser = await chromium.launch({
    headless: process.env.HEADLESS !== 'false',
    devtools: process.env.DEVTOOLS === 'true'
  });
  
  const context = await browser.newContext({
    // Record video for debugging
    recordVideo: {
      dir: DEBUG_DIR,
      size: { width: 1280, height: 720 }
    }
  });
  
  const page = await context.newPage();
  
  // Arrays to collect debug data
  const networkRequests = [];
  const consoleMessages = [];
  const errors = [];
  
  // Monitor network activity
  page.on('request', request => {
    networkRequests.push({
      time: new Date().toISOString(),
      url: request.url(),
      method: request.method(),
      type: request.resourceType()
    });
    console.log(`📡 ${request.method()} ${request.url()}`);
  });
  
  page.on('response', response => {
    if (response.status() >= 400) {
      console.log(`❌ Error response: ${response.status()} ${response.url()}`);
    }
  });
  
  // Capture console messages
  page.on('console', msg => {
    const entry = {
      time: new Date().toISOString(),
      type: msg.type(),
      text: msg.text()
    };
    consoleMessages.push(entry);
    console.log(`🖥️  Console [${msg.type()}]: ${msg.text()}`);
  });
  
  // Capture errors
  page.on('pageerror', error => {
    errors.push({
      time: new Date().toISOString(),
      message: error.message,
      stack: error.stack
    });
    console.error('🚨 Page error:', error.message);
  });
  
  try {
    console.log('\n📥 Loading admin panel...');
    
    // Navigate with extended timeout
    const response = await page.goto(ADMIN_URL, {
      waitUntil: 'domcontentloaded',
      timeout: TIMEOUT
    });
    
    console.log(`✅ Initial response: ${response.status()}`);
    console.log(`📍 Final URL: ${page.url()}`);
    
    // Take initial screenshot
    await page.screenshot({
      path: path.join(DEBUG_DIR, '1-initial-load.png'),
      fullPage: true
    });
    
    // Wait a bit for JavaScript to execute
    console.log('\n⏳ Waiting for JavaScript execution...');
    await page.waitForTimeout(3000);
    
    // Take screenshot after JS execution
    await page.screenshot({
      path: path.join(DEBUG_DIR, '2-after-js.png'),
      fullPage: true
    });
    
    // Check for common auth elements
    console.log('\n🔐 Checking for authentication elements...');
    const authElements = await page.evaluate(() => {
      const selectors = [
        'input[type="password"]',
        'input[name="password"]',
        'button[type="submit"]',
        'form[action*="login"]',
        'form[action*="auth"]',
        '#login',
        '.login',
        '[data-testid*="login"]'
      ];
      
      const found = {};
      selectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        if (elements.length > 0) {
          found[selector] = elements.length;
        }
      });
      
      return found;
    });
    
    if (Object.keys(authElements).length > 0) {
      console.log('🔑 Found authentication elements:', authElements);
    }
    
    // Try to wait for network idle
    console.log('\n🌐 Waiting for network idle...');
    try {
      await page.waitForLoadState('networkidle', { timeout: 10000 });
      console.log('✅ Network is idle');
    } catch (e) {
      console.log('⚠️  Network did not become idle within 10s');
    }
    
    // Take final screenshot
    await page.screenshot({
      path: path.join(DEBUG_DIR, '3-final-state.png'),
      fullPage: true
    });
    
    // Get page metrics
    const metrics = await page.evaluate(() => ({
      title: document.title,
      url: window.location.href,
      readyState: document.readyState,
      scripts: Array.from(document.scripts).map(s => s.src).filter(Boolean),
      forms: document.forms.length,
      iframes: document.querySelectorAll('iframe').length,
      bodyText: document.body.innerText.substring(0, 500)
    }));
    
    console.log('\n📊 Page Metrics:');
    console.log(JSON.stringify(metrics, null, 2));
    
    // Save debug data
    await fs.writeFile(
      path.join(DEBUG_DIR, 'network-log.json'),
      JSON.stringify(networkRequests, null, 2)
    );
    
    await fs.writeFile(
      path.join(DEBUG_DIR, 'console-log.json'),
      JSON.stringify(consoleMessages, null, 2)
    );
    
    await fs.writeFile(
      path.join(DEBUG_DIR, 'errors.json'),
      JSON.stringify(errors, null, 2)
    );
    
    await fs.writeFile(
      path.join(DEBUG_DIR, 'page-metrics.json'),
      JSON.stringify(metrics, null, 2)
    );
    
    // Get page HTML for analysis
    const html = await page.content();
    await fs.writeFile(path.join(DEBUG_DIR, 'page.html'), html);
    
  } catch (error) {
    console.error('🚨 Debug failed:', error.message);
    
    // Take error screenshot
    try {
      await page.screenshot({
        path: path.join(DEBUG_DIR, 'error-state.png'),
        fullPage: true
      });
    } catch (e) {
      console.error('Could not take error screenshot');
    }
  } finally {
    await browser.close();
    
    console.log('\n✅ Debug complete!');
    console.log(`📂 Results saved to: ${DEBUG_DIR}`);
    console.log('\nFiles created:');
    const files = await fs.readdir(DEBUG_DIR);
    files.forEach(file => console.log(`  - ${file}`));
  }
}

// Run the debugger
if (require.main === module) {
  debugAdminPanel().catch(console.error);
}

module.exports = { debugAdminPanel };