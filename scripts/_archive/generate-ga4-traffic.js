#!/usr/bin/env node

/**
 * GA4 Traffic Generator for ReillyDesignStudio
 * Simulates real user visits to trigger GA4 events
 */

const fetch = require('node-fetch');
const { v4: uuidv4 } = require('uuid');

// GA4 Configuration
const MEASUREMENT_ID = 'G-XXXXXXXXXX'; // Will be extracted from site
const API_SECRET = process.env.GA4_API_SECRET || 'test_secret'; // Placeholder

// Pages to visit
const PAGES = [
  'https://www.reillydesignstudio.com',
  'https://www.reillydesignstudio.com/blog',
  'https://www.reillydesignstudio.com/blog/featured',
  'https://www.reillydesignstudio.com/blog/speculative-decoding',
  'https://www.reillydesignstudio.com/contact',
  'https://www.reillydesignstudio.com/shop/services',
];

// Simulate GA4 Measurement Protocol events
async function generateGA4Event(pagePath, pageTitle) {
  const clientId = uuidv4();
  const timestamp = Date.now();
  
  const payload = {
    client_id: clientId,
    user_id: `user_${clientId.slice(0, 8)}`,
    timestamp_micros: timestamp * 1000,
    events: [
      {
        name: 'page_view',
        params: {
          page_location: pagePath,
          page_title: pageTitle,
          engagement_time_msec: '100',
        }
      }
    ]
  };

  console.log(`📊 Generating GA4 event for: ${pagePath}`);
  
  // Note: Real GA4 events come from gtag.js on client-side
  // This is demonstration of event structure
  return payload;
}

async function generateTraffic() {
  console.log('🚀 Starting GA4 Traffic Generation');
  console.log('=' .repeat(50));
  console.log('');

  for (const url of PAGES) {
    try {
      // Fetch the page
      console.log(`📍 Visiting: ${url}`);
      const response = await fetch(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
      });
      
      if (response.status === 200) {
        const html = await response.text();
        
        // Check if gtag is present
        if (html.includes('gtag') || html.includes('google-analytics')) {
          console.log('  ✓ GA4 tracking detected');
          
          // Extract measurement ID if possible
          const gtagMatch = html.match(/gtag\("config",\s*"(G-[A-Z0-9]+)"/);
          if (gtagMatch) {
            console.log(`  ✓ Measurement ID: ${gtagMatch[1]}`);
          }
        } else {
          console.log('  ⚠️  GA4 tracking not found in HTML');
        }

        // Extract page title
        const titleMatch = html.match(/<title[^>]*>([^<]+)<\/title>/i);
        const pageTitle = titleMatch ? titleMatch[1] : 'Page';
        
        // Generate event structure (for demonstration)
        const event = await generateGA4Event(url, pageTitle);
        console.log(`  ℹ️  Event structure:`);
        console.log(`     - Event: ${event.events[0].name}`);
        console.log(`     - Title: ${event.events[0].params.page_title}`);
        console.log('');
      } else {
        console.log(`  ✗ Failed: HTTP ${response.status}`);
      }
    } catch (error) {
      console.error(`  ✗ Error: ${error.message}`);
    }

    // Small delay between requests
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  console.log('');
  console.log('=' .repeat(50));
  console.log('⏳ Traffic generation complete!');
  console.log('');
  console.log('Note: GA4 events are fired by gtag.js in the browser.');
  console.log('Server-side curl/fetch requests do NOT trigger GA4 events.');
  console.log('');
  console.log('To generate real GA4 traffic, you need:');
  console.log('1. A real browser (Chrome, Firefox, Safari)');
  console.log('2. Or use Puppeteer/Playwright to render JavaScript');
  console.log('3. Or manually visit the site in your browser');
  console.log('');
}

generateTraffic().catch(console.error);
