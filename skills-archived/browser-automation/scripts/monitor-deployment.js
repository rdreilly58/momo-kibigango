#!/usr/bin/env node
/**
 * Vercel Deployment Monitor for ReillyDesignStudio
 * 
 * This script monitors Vercel deployments by:
 * 1. Checking deployment status via Vercel dashboard
 * 2. Taking screenshots of deployment progress
 * 3. Monitoring the live site after deployment
 * 4. Alerting on deployment failures
 */

const { chromium } = require('playwright');
const fs = require('fs').promises;
const path = require('path');

// Configuration
const VERCEL_PROJECT_URL = process.env.VERCEL_PROJECT_URL || 'https://vercel.com/dashboard';
const SITE_URL = process.env.SITE_URL || 'https://reillydesignstudio.com';
const CHECK_INTERVAL = 30000; // 30 seconds
const MAX_CHECKS = 20; // Max 10 minutes
const OUTPUT_DIR = '/tmp/vercel-monitor-' + Date.now();

class VercelMonitor {
  constructor() {
    this.browser = null;
    this.context = null;
    this.checks = 0;
    this.deploymentStatus = 'unknown';
    this.screenshots = [];
  }
  
  async initialize() {
    console.log('🚀 Initializing Vercel Deployment Monitor...');
    console.log(`📍 Monitoring: ${SITE_URL}`);
    console.log(`📂 Output directory: ${OUTPUT_DIR}`);
    
    await fs.mkdir(OUTPUT_DIR, { recursive: true });
    
    this.browser = await chromium.launch({
      headless: process.env.HEADLESS !== 'false'
    });
    
    this.context = await this.browser.newContext({
      viewport: { width: 1920, height: 1080 }
    });
  }
  
  async checkVercelDashboard() {
    console.log('\n🔍 Checking Vercel dashboard...');
    const page = await this.context.newPage();
    
    try {
      // Note: This would require authentication
      // For now, we'll simulate checking the dashboard
      console.log('⚠️  Dashboard check requires authentication');
      console.log('   Implement Vercel API integration for automated checks');
      
      // Placeholder for API integration
      // const deployment = await this.getLatestDeploymentViaAPI();
      
    } catch (error) {
      console.error('❌ Dashboard check failed:', error.message);
    } finally {
      await page.close();
    }
  }
  
  async checkSiteStatus() {
    console.log(`\n🌐 Checking site status (attempt ${this.checks + 1}/${MAX_CHECKS})...`);
    const page = await this.context.newPage();
    
    const timestamp = new Date().toISOString();
    const screenshotName = `site-check-${this.checks + 1}.png`;
    
    try {
      // Set up request monitoring
      const requests = [];
      page.on('request', request => {
        if (request.url().startsWith(SITE_URL)) {
          requests.push({
            url: request.url(),
            method: request.method(),
            type: request.resourceType()
          });
        }
      });
      
      // Navigate to site
      const response = await page.goto(SITE_URL, {
        waitUntil: 'networkidle',
        timeout: 30000
      });
      
      const status = response.status();
      console.log(`📡 Response status: ${status}`);
      
      // Take screenshot
      const screenshotPath = path.join(OUTPUT_DIR, screenshotName);
      await page.screenshot({
        path: screenshotPath,
        fullPage: false // Just viewport for monitoring
      });
      this.screenshots.push(screenshotName);
      
      // Check for key elements that indicate successful deployment
      const healthChecks = await page.evaluate(() => {
        return {
          hasTitle: !!document.title,
          title: document.title,
          hasBody: document.body.children.length > 0,
          hasReactRoot: !!document.querySelector('#__next') || !!document.querySelector('#root'),
          errorMessages: Array.from(document.querySelectorAll('.error, .error-message, [data-error]'))
            .map(el => el.textContent).slice(0, 5),
          isVercelError: document.body.textContent.includes('VERCEL ERROR') ||
                        document.body.textContent.includes('404 - Not Found')
        };
      });
      
      // Log health check results
      console.log('🏥 Health checks:', JSON.stringify(healthChecks, null, 2));
      
      // Determine deployment status
      if (status === 200 && healthChecks.hasReactRoot && !healthChecks.isVercelError) {
        this.deploymentStatus = 'success';
        console.log('✅ Site is healthy and deployed!');
      } else if (status >= 500) {
        this.deploymentStatus = 'error';
        console.log('❌ Server error detected');
      } else if (healthChecks.isVercelError) {
        this.deploymentStatus = 'building';
        console.log('🔨 Site appears to be building...');
      }
      
      // Save check results
      const checkResult = {
        timestamp,
        check: this.checks + 1,
        status,
        url: page.url(),
        screenshot: screenshotName,
        healthChecks,
        requests: requests.slice(0, 10) // First 10 requests
      };
      
      await fs.writeFile(
        path.join(OUTPUT_DIR, `check-${this.checks + 1}.json`),
        JSON.stringify(checkResult, null, 2)
      );
      
    } catch (error) {
      console.error('❌ Site check failed:', error.message);
      this.deploymentStatus = 'error';
      
      // Try to capture error screenshot
      try {
        await page.screenshot({
          path: path.join(OUTPUT_DIR, `error-${this.checks + 1}.png`)
        });
      } catch (e) {
        console.error('Could not capture error screenshot');
      }
    } finally {
      await page.close();
      this.checks++;
    }
  }
  
  async generateReport() {
    console.log('\n📄 Generating deployment report...');
    
    const report = {
      monitoringSession: {
        startTime: new Date(Date.now() - (this.checks * CHECK_INTERVAL)).toISOString(),
        endTime: new Date().toISOString(),
        totalChecks: this.checks,
        finalStatus: this.deploymentStatus,
        siteUrl: SITE_URL
      },
      screenshots: this.screenshots,
      summary: this.getStatusSummary()
    };
    
    await fs.writeFile(
      path.join(OUTPUT_DIR, 'deployment-report.json'),
      JSON.stringify(report, null, 2)
    );
    
    // Create HTML report
    const html = `
<!DOCTYPE html>
<html>
<head>
  <title>Vercel Deployment Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    .status-${this.deploymentStatus} { 
      color: ${this.deploymentStatus === 'success' ? 'green' : 'red'}; 
      font-weight: bold;
    }
    img { max-width: 100%; margin: 10px 0; border: 1px solid #ccc; }
    .screenshot { margin: 20px 0; }
  </style>
</head>
<body>
  <h1>Vercel Deployment Monitor Report</h1>
  <p><strong>Site:</strong> ${SITE_URL}</p>
  <p><strong>Status:</strong> <span class="status-${this.deploymentStatus}">${this.deploymentStatus.toUpperCase()}</span></p>
  <p><strong>Checks:</strong> ${this.checks}</p>
  <p><strong>Time:</strong> ${new Date().toLocaleString()}</p>
  
  <h2>Screenshots</h2>
  ${this.screenshots.map(s => `
    <div class="screenshot">
      <h3>${s}</h3>
      <img src="${s}" alt="${s}">
    </div>
  `).join('')}
</body>
</html>`;
    
    await fs.writeFile(path.join(OUTPUT_DIR, 'report.html'), html);
    
    console.log('✅ Report generated!');
    console.log(`📂 View report: file://${OUTPUT_DIR}/report.html`);
  }
  
  getStatusSummary() {
    switch (this.deploymentStatus) {
      case 'success':
        return '✅ Deployment successful! Site is live and healthy.';
      case 'building':
        return '🔨 Deployment in progress. Site is being built.';
      case 'error':
        return '❌ Deployment failed or site is experiencing errors.';
      default:
        return '❓ Deployment status unknown.';
    }
  }
  
  async monitor() {
    await this.initialize();
    
    // Optional: Check Vercel dashboard first
    if (process.env.CHECK_DASHBOARD === 'true') {
      await this.checkVercelDashboard();
    }
    
    // Monitor site status
    while (this.checks < MAX_CHECKS && this.deploymentStatus !== 'success') {
      await this.checkSiteStatus();
      
      if (this.deploymentStatus !== 'success' && this.checks < MAX_CHECKS) {
        console.log(`\n⏳ Waiting ${CHECK_INTERVAL / 1000} seconds before next check...`);
        await new Promise(resolve => setTimeout(resolve, CHECK_INTERVAL));
      }
    }
    
    // Generate final report
    await this.generateReport();
    
    // Cleanup
    await this.browser.close();
    
    console.log('\n' + this.getStatusSummary());
    return this.deploymentStatus;
  }
  
  // For use with CI/CD pipelines
  async monitorOnce() {
    await this.initialize();
    await this.checkSiteStatus();
    await this.generateReport();
    await this.browser.close();
    return this.deploymentStatus;
  }
}

// CLI interface
if (require.main === module) {
  const monitor = new VercelMonitor();
  
  const mode = process.argv[2] || 'continuous';
  
  if (mode === 'once') {
    monitor.monitorOnce()
      .then(status => {
        process.exit(status === 'success' ? 0 : 1);
      })
      .catch(error => {
        console.error('Monitor failed:', error);
        process.exit(1);
      });
  } else {
    monitor.monitor()
      .then(status => {
        process.exit(status === 'success' ? 0 : 1);
      })
      .catch(error => {
        console.error('Monitor failed:', error);
        process.exit(1);
      });
  }
}

module.exports = { VercelMonitor };