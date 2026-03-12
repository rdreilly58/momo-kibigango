const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  const siteUrl = 'https://www.ReillyDesignStudio.com';
  
  try {
    await page.goto(siteUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    console.log('✅ Loaded www.ReillyDesignStudio.com');
    
    // Get all links
    const links = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('a')).map(a => ({
        text: a.textContent.trim(),
        href: a.href
      }));
    });
    
    console.log('\n🔗 Available links:');
    links.forEach(link => {
      if (link.text.length > 0 && link.text.length < 100) {
        console.log(`- ${link.text} -> ${link.href}`);
      }
    });
    
    // Try to find and click work/portfolio link
    const workLink = links.find(l => 
      l.text.toLowerCase().includes('work') || 
      l.text.toLowerCase().includes('portfolio')
    );
    
    if (workLink) {
      console.log(`\n✅ Found work link: ${workLink.text}`);
      await page.goto(workLink.href, { waitUntil: 'domcontentloaded', timeout: 30000 });
      console.log('✅ Navigated to work page');
      
      // Extract all project titles and descriptions
      const projects = await page.evaluate(() => {
        const items = [];
        // Try multiple selectors for project cards
        const selectors = [
          '[class*="project"]',
          '[class*="work"]',
          '[class*="portfolio"]',
          'article',
          '.card'
        ];
        
        selectors.forEach(selector => {
          document.querySelectorAll(selector).forEach(el => {
            const title = el.querySelector('h2, h3, .title')?.textContent.trim();
            if (title && title.length > 0 && title.length < 200) {
              items.push(title);
            }
          });
        });
        
        return [...new Set(items)]; // Remove duplicates
      });
      
      console.log('\n📋 Projects found:');
      projects.forEach((proj, idx) => {
        console.log(`${idx + 1}. ${proj}`);
        if (proj.toLowerCase().includes('packaging')) {
          console.log('   ⭐ FOUND: Packaging System');
        }
      });
    } else {
      console.log('\n⚠️  Could not find work/portfolio link');
    }
    
    // Also get full page text to ensure we catch everything
    const bodyText = await page.evaluate(() => document.body.innerText);
    console.log('\n📄 Page content (first 3000 chars):');
    console.log(bodyText.substring(0, 3000));
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
  
  await browser.close();
})();
