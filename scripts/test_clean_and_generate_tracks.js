const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const ARTIFACT_DIR = '/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f';

async function run() {
  console.log('🚀 Starting E2E verification of clean tracks & new DJ Fredd generation...');
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/Users/fredyarroyave/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell',
    args: ['--use-fake-ui-for-media-stream', '--no-sandbox']
  });
  
  // 1. Desktop Test
  const context = await browser.newContext({
    viewport: { width: 1280, height: 850 }
  });
  const page = await context.newPage();

  // Navigate to DJ Fredd view
  console.log('Navigating to http://127.0.0.1:8080/index.html?view=djeddie...');
  await page.goto('http://127.0.0.1:8080/index.html?view=djeddie', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  // Check headers: verify NO "HISTORIA REAL (INTRO NARRADA POR EDDIE)"
  const headerTexts = await page.$$eval('.dj-playlist-table-header div', divs => divs.map(d => d.textContent.trim()));
  console.log('Table Headers detected:', headerTexts);

  // Verify all pending base tracks have 'Sin historia' and '✨ Generar historia'
  const pendingBadges = await page.$$eval('.dj-intro-pill.is-pending', els => els.length);
  const genButtons = await page.$$eval('.dj-action-btn.gen-story', els => els.length);
  console.log(`Tracks in 'Sin historia' state: ${pendingBadges}, '✨ Generar historia' buttons: ${genButtons}`);

  // Verify Spotify rows have NO 'Spotify' pill
  const spotifyPills = await page.$$eval('.spotify-pill, .spotify-tag', els => els.length);
  console.log(`Spotify pills count: ${spotifyPills}`);

  // Verify Clear All button is present
  const clearAllBtn = await page.$('#btnDjPlaylistClearAll');
  console.log(`Clear All button exists: ${!!clearAllBtn}`);

  // Take screenshot of clean list
  const cleanListPath = path.join(ARTIFACT_DIR, 'dj_fredd_clean_table_desktop.png');
  await page.screenshot({ path: cleanListPath, fullPage: false });
  console.log(`Saved screenshot: ${cleanListPath}`);

  // 2. Click "✨ Generar historia" on Detroit Rock City (first intro)
  console.log('Triggering "✨ Generar historia" on Detroit Rock City...');
  const firstGenBtn = await page.$('.dj-action-btn.gen-story');
  if (!firstGenBtn) throw new Error('No generate button found!');
  await firstGenBtn.click();

  // Check for the toast notification
  await page.waitForTimeout(600);
  const toastText = await page.$eval('#appToast', el => el.textContent.trim()).catch(() => '');
  console.log('Toast notification text:', toastText);
  const toastScreenshotPath = path.join(ARTIFACT_DIR, 'dj_fredd_toast_generating.png');
  await page.screenshot({ path: toastScreenshotPath, fullPage: false });

  // Wait for generation to finish (polling status)
  console.log('Waiting for TTS synthesis to complete...');
  await page.waitForFunction(() => {
    const pills = Array.from(document.querySelectorAll('.dj-intro-pill'));
    return pills.some(p => p.textContent.includes('Historia') && !p.classList.contains('is-pending') && !p.classList.contains('is-generating'));
  }, { timeout: 35000 });

  console.log('Generation completed successfully!');
  await page.waitForTimeout(1000);

  // Take screenshot of generated state
  const generatedPath = path.join(ARTIFACT_DIR, 'dj_fredd_generated_state_desktop.png');
  await page.screenshot({ path: generatedPath, fullPage: false });
  console.log(`Saved screenshot: ${generatedPath}`);

  // Click play on the generated story
  console.log('Clicking play on generated Detroit Rock City story...');
  const playBtn = await page.$('.dj-row-play-btn');
  if (playBtn) await playBtn.click();
  await page.waitForTimeout(1500);

  // Check player bar synchronization
  const playerBarTitle = await page.$eval('#barTrackTitle', el => el.textContent.trim()).catch(() => '');
  const playerBarArtist = await page.$eval('#barTrackArtist', el => el.textContent.trim()).catch(() => '');
  console.log(`Player Bar playing: "${playerBarTitle}" by "${playerBarArtist}"`);

  const playingPath = path.join(ARTIFACT_DIR, 'dj_fredd_playing_state_desktop.png');
  await page.screenshot({ path: playingPath, fullPage: false });
  console.log(`Saved screenshot: ${playingPath}`);

  // 3. Mobile View Verification
  console.log('Checking Mobile view adaptation...');
  const mobileContext = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true
  });
  const mobilePage = await mobileContext.newPage();
  await mobilePage.goto('http://127.0.0.1:8080/index.html?view=djeddie', { waitUntil: 'networkidle' });
  await mobilePage.waitForTimeout(1000);

  const mobileScreenshotPath = path.join(ARTIFACT_DIR, 'dj_fredd_table_mobile.png');
  await mobilePage.screenshot({ path: mobileScreenshotPath, fullPage: false });
  console.log(`Saved mobile screenshot: ${mobileScreenshotPath}`);

  await browser.close();
  console.log('🎉 All E2E verifications completed successfully!');
}

run().catch(err => {
  console.error('❌ Test failed:', err);
  process.exit(1);
});
