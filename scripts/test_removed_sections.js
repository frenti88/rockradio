const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = '/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f';

async function run() {
  console.log('🚀 Verifying removal of "Hecho para ti" and "⚡ Cápsulas: Rock en 45 Segundos"...');
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

  const madeForYou = await page.$('#shelfMadeForYou');
  const capsules45 = await page.$('#shelfCapsules45');
  console.log(`shelfMadeForYou exists: ${!!madeForYou}`);
  console.log(`shelfCapsules45 exists: ${!!capsules45}`);

  if (madeForYou || capsules45) {
    throw new Error('Sections were not completely removed!');
  }

  const shelfTitles = await page.$$eval('.home-shelf-title', titles => titles.map(t => t.textContent.trim()));
  console.log('Remaining Home Shelves:', shelfTitles);

  const screenshotPath = path.join(ARTIFACT_DIR, 'home_clean_no_capsules_no_mixes.png');
  await page.screenshot({ path: screenshotPath, fullPage: false });
  console.log(`Saved screenshot: ${screenshotPath}`);

  // Mobile screenshot
  const mobileContext = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true
  });
  const mobilePage = await mobileContext.newPage();
  await mobilePage.goto('http://127.0.0.1:8080/index.html', { waitUntil: 'networkidle' });
  await mobilePage.waitForTimeout(1000);

  const mobileScreenshotPath = path.join(ARTIFACT_DIR, 'home_clean_mobile.png');
  await mobilePage.screenshot({ path: mobileScreenshotPath, fullPage: false });
  console.log(`Saved mobile screenshot: ${mobileScreenshotPath}`);

  await browser.close();
  console.log('🎉 Verification passed! Both sections successfully removed.');
}

run().catch(err => {
  console.error('❌ Test failed:', err);
  process.exit(1);
});
