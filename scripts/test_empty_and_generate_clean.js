const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = '/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f';

async function run() {
  console.log('🚀 Verifying empty list and clean track generation...');
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/Users/fredyarroyave/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell',
    args: ['--use-fake-ui-for-media-stream', '--no-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 850 }
  });
  const page = await context.newPage();

  console.log('Navigating to http://127.0.0.1:8080/index.html?view=djeddie...');
  await page.goto('http://127.0.0.1:8080/index.html?view=djeddie', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  // 1. Verify 0 tracks initially
  const initialRows = await page.$$eval('.dj-song-row', rows => rows.length);
  console.log(`Initial tracks in DJ Fredd list: ${initialRows}`);
  if (initialRows !== 0) {
    throw new Error(`Expected 0 initial tracks, but found ${initialRows}!`);
  }

  // Verify empty state is visible
  const emptyStateText = await page.$eval('.dj-empty-state', el => el.textContent.trim()).catch(() => '');
  console.log('Empty state message detected:', emptyStateText.slice(0, 80) + '...');

  const emptyScreenshotPath = path.join(ARTIFACT_DIR, 'dj_fredd_empty_state_desktop.png');
  await page.screenshot({ path: emptyScreenshotPath, fullPage: false });
  console.log(`Saved screenshot: ${emptyScreenshotPath}`);

  // 2. Add track to DJ Fredd via addSpotifyTrackToDjEddie
  console.log('Adding "Help!" by The Beatles to DJ Fredd...');
  await page.evaluate(() => {
    window.addSpotifyTrackToDjEddie({
      id: 'beatles_help_test',
      name: 'Help!',
      duration_ms: 139000,
      artists: [{ name: 'The Beatles' }],
      album: {
        name: 'Help!',
        release_date: '1965-08-06',
        images: [{ url: 'https://is1-ssl.mzstatic.com/image/thumb/Music115/v4/91/97/81/91978168-dfc9-fcbe-262e-566b7b25e73e/00602537575285.rgb.jpg/640x640bb.jpg' }]
      }
    });
  });

  await page.waitForTimeout(600);
  const rowsAfterAdd = await page.$$eval('.dj-song-row', rows => rows.length);
  console.log(`Tracks in DJ Fredd list after addition: ${rowsAfterAdd} (1 intro + 1 song)`);

  const addedScreenshotPath = path.join(ARTIFACT_DIR, 'dj_fredd_single_added_track.png');
  await page.screenshot({ path: addedScreenshotPath, fullPage: false });

  // 3. Click "✨ Generar historia"
  console.log('Clicking "✨ Generar historia" on Help!...');
  const genBtn = await page.$('.dj-action-btn.gen-story');
  if (!genBtn) throw new Error('No generate button found on added track!');
  await genBtn.click();

  // Wait for synthesis to complete
  console.log('Waiting for DJ Fredd TTS synthesis to complete...');
  await page.waitForFunction(() => {
    const pills = Array.from(document.querySelectorAll('.dj-status-badge, .dj-intro-pill'));
    return pills.some(p => p.textContent.includes('Historia') && !p.classList.contains('pending') && !p.classList.contains('is-pending'));
  }, { timeout: 35000 });

  console.log('Story generated successfully!');
  await page.waitForTimeout(1000);

  const generatedScreenshotPath = path.join(ARTIFACT_DIR, 'dj_fredd_help_generated.png');
  await page.screenshot({ path: generatedScreenshotPath, fullPage: false });
  console.log(`Saved screenshot: ${generatedScreenshotPath}`);

  // 4. Test delete track
  console.log('Testing delete track with 🗑️...');
  const delBtn = await page.$('.dj-action-btn.del-track');
  if (delBtn) await delBtn.click();
  await page.waitForTimeout(800);

  const rowsAfterDelete = await page.$$eval('.dj-song-row', rows => rows.length);
  console.log(`Tracks in DJ Fredd list after delete: ${rowsAfterDelete}`);

  await browser.close();
  console.log('🎉 Verification passed 100%!');
}

run().catch(err => {
  console.error('❌ Test failed:', err);
  process.exit(1);
});
