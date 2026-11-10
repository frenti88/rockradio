const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = '/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f';
const CHROME_PATH = '/Users/fredyarroyave/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell';

async function run() {
  const browser = await chromium.launch({
    executablePath: CHROME_PATH,
    headless: true
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 1100 }
  });
  const page = await context.newPage();

  await page.goto('http://localhost:8080/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  // Scroll down to show shelves
  await page.evaluate(() => {
    const el = document.getElementById('spotifyMain');
    if (el) el.scrollTop = 520;
  });
  await page.waitForTimeout(600);

  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'spotify_home_shelves_scrolled.png'), fullPage: false });
  console.log('Saved spotify_home_shelves_scrolled.png');

  await browser.close();
}

run().catch(console.error);
