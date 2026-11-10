const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = '/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f';

async function run() {
  console.log('🚀 Verifying that category filter pills (Todo, DJ Fredd, Artistas) are removed...');
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/Users/fredyarroyave/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell',
    args: ['--use-fake-ui-for-media-stream', '--no-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 950 }
  });
  const page = await context.newPage();

  console.log('Navigating to http://127.0.0.1:8080/index.html...');
  await page.goto('http://127.0.0.1:8080/index.html', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  const filterBar = await page.$('#spotifyHomeFilterBar');
  const pillsCount = await page.$$eval('.home-filter-pill', pills => pills.length);
  console.log(`spotifyHomeFilterBar exists: ${!!filterBar}`);
  console.log(`home-filter-pill count: ${pillsCount}`);

  if (filterBar || pillsCount > 0) {
    throw new Error('Filter bar or pills still exist in DOM!');
  }

  const screenshotPath = path.join(ARTIFACT_DIR, 'home_no_filter_pills_desktop.png');
  await page.screenshot({ path: screenshotPath, fullPage: false });
  console.log(`Saved desktop screenshot: ${screenshotPath}`);

  // Mobile screenshot
  const mobileContext = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true
  });
  const mobilePage = await mobileContext.newPage();
  await mobilePage.goto('http://127.0.0.1:8080/index.html', { waitUntil: 'networkidle' });
  await mobilePage.waitForTimeout(1000);

  const mobileScreenshotPath = path.join(ARTIFACT_DIR, 'home_no_filter_pills_mobile.png');
  await mobilePage.screenshot({ path: mobileScreenshotPath, fullPage: false });
  console.log(`Saved mobile screenshot: ${mobileScreenshotPath}`);

  await browser.close();
  console.log('🎉 Verification passed! Filter pills removed cleanly.');
}

run().catch(err => {
  console.error('❌ Test failed:', err);
  process.exit(1);
});
