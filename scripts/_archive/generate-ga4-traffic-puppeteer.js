#!/usr/bin/env node

/**
 * GA4 Traffic Generator with Puppeteer
 * Generates real GA4 events by visiting pages in headless Chrome
 */

const puppeteer = require('puppeteer');

const PAGES = [
  {
    url: 'https://www.reillydesignstudio.com',
    title: 'Home',
    waitTime: 3000
  },
  {
    url: 'https://www.reillydesignstudio.com/blog',
    title: 'Blog',
    waitTime: 2000
  },
  {
    url: 'https://www.reillydesignstudio.com/blog/featured',
    title: 'Featured Posts',
    waitTime: 2000
  },
  {
    url: 'https://www.reillydesignstudio.com/blog/speculative-decoding',
    title: 'Speculative Decoding Post',
    waitTime: 3000
  },
  {
    url: 'https://www.reillydesignstudio.com/contact',
    title: 'Contact',
    waitTime: 2000
  },
  {
    url: 'https://www.reillydesignstudio.com/shop/services',
    title: 'Shop Services',
    waitTime: 2000
  },
];

async function generateTraffic() {
  console.log('🚀 GA4 Traffic Generator — Puppeteer');
  console.log('='.repeat(60));
  console.log('');

  let browser;
  try {
    // Launch browser
    console.log('⏳ Launching headless Chrome...');
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    console.log('✓ Browser launched');
    console.log('');

    // Visit each page
    for (const page of PAGES) {
      await visitPage(browser, page);
    }

    console.log('');
    console.log('='.repeat(60));
    console.log('✓ Traffic generation complete!');
    console.log('');
    console.log('📊 Check GA4 Realtime:');
    console.log('   https://analytics.google.com');
    console.log('   (Realtime section shows events within 5-10 seconds)');
    console.log('');
    console.log('💾 After 24-48 hours, data will appear in BigQuery:');
    console.log('   Dataset: ga4_reillydesignstudio');
    console.log('');

  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

async function visitPage(browser, pageConfig) {
  const page = await browser.newPage();
  const { url, title, waitTime } = pageConfig;

  try {
    console.log(`📍 Visiting: ${title}`);
    console.log(`   URL: ${url}`);

    // Set realistic viewport
    await page.setViewport({
      width: 1920,
      height: 1080,
    });

    // Set User-Agent to look like real browser
    await page.setUserAgent(
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    );

    // Navigate to page
    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: 30000,
    });

    // Wait for gtag to load
    console.log(`   ⏳ Waiting ${waitTime / 1000}s for GA4 to fire...`);
    await new Promise(resolve => setTimeout(resolve, waitTime));

    // Verify gtag is present
    const hasGtag = await page.evaluate(() => {
      return typeof window.gtag !== 'undefined' || 
             typeof window.dataLayer !== 'undefined';
    });

    if (hasGtag) {
      console.log('   ✓ GA4 tracking detected and fired');
    } else {
      console.log('   ⚠️  GA4 not detected (may still have fired)');
    }

    // Optional: Interact with page slightly
    await page.evaluate(() => {
      // Scroll a bit to trigger engagement
      window.scrollBy(0, window.innerHeight / 2);
    });

    console.log(`   ✓ Page visit complete`);
    console.log('');

  } catch (error) {
    console.error(`   ✗ Error visiting ${title}: ${error.message}`);
  } finally {
    await page.close();
  }
}

// Run the traffic generator
generateTraffic();
