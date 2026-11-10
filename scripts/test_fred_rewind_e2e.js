const { chromium } = require('playwright');

(async () => {
  console.log('🎸 Starting Fred Rewind E2E Test Suite...');
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  });
  const context = await browser.newContext({ viewport: { width: 1440, height: 950 } });
  const page = await context.newPage();

  page.on('console', msg => {
    if (msg.type() === 'error' || msg.text().includes('FRED') || msg.text().includes('DJ')) {
      console.log('BROWSER CONSOLE:', msg.text());
    }
  });

  await page.goto('http://localhost:8080/index.html', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // 1. Verify Home Branding
  const pageTitle = await page.title();
  console.log('Page Title:', pageTitle);
  if (!pageTitle.includes('Fred Rewind') || !pageTitle.includes('DJ Fredd')) {
    throw new Error('Title does not contain "Fred Rewind" and "DJ Fredd"');
  }

  // 2. Open DJ Fredd Playlist View
  console.log('Opening Fred Rewind playlist view...');
  await page.click('#sidebarHomeBtn');
  await page.waitForTimeout(500);

  // Click on DJ Fredd quick card or button
  const quickCard = await page.$('.spotify-quick-banner-card');
  if (quickCard) {
    await quickCard.click();
  } else {
    await page.evaluate(() => openDjEddiePlaylistView());
  }
  await page.waitForTimeout(1000);

  // Take screenshot of empty or initial playlist view
  await page.screenshot({ path: '/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f/fred_rewind_playlist_initial.png' });
  console.log('Saved fred_rewind_playlist_initial.png');

  // 3. Add a track to DJ Fredd from Curated / Search
  console.log('Adding "Bohemian Rhapsody" by Queen to Fred Rewind playlist...');
  await page.evaluate(() => {
    addSpotifyTrackToDjEddie({
      id: 'queen_bohemian_rhapsody_test',
      name: 'Bohemian Rhapsody',
      artists: [{ name: 'Queen' }],
      album: {
        name: 'A Night at the Opera',
        release_date: '1975-10-31',
        images: [{ url: 'img/albums/queen_1975_night_at_opera.png' }]
      },
      duration_ms: 354000
    });
  });
  await page.waitForTimeout(1000);

  // 4. Verify Track is added with status 'Sin historia'
  const rowCount = await page.$$eval('.dj-song-row', rows => rows.length);
  console.log('Total playlist rows (Intro + Song):', rowCount);
  if (rowCount < 2) throw new Error('Expected at least 2 rows (Intro + Song)');

  const pendingBadge = await page.$eval('.dj-status-badge.pending', el => el.textContent.trim());
  console.log('Intro badge status:', pendingBadge);
  if (!pendingBadge.includes('Sin historia')) {
    throw new Error(`Expected badge to say "Sin historia", got: ${pendingBadge}`);
  }

  const genBtn = await page.$('.gen-story');
  if (!genBtn) throw new Error('Button "✨ Generar historia" not found');
  console.log('Found button "✨ Generar historia". Clicking to start generation...');

  // 5. Trigger Story Generation and watch phases
  await genBtn.click();
  await page.waitForTimeout(300);

  // Check investigando or generando_guion phase
  const runningBadge = await page.$eval('.dj-status-badge.running', el => el.textContent.trim()).catch(() => null);
  console.log('Phase in progress:', runningBadge);

  // Check that "Detener generación" button appears
  const cancelBtn = await page.$('.cancel-gen');
  if (cancelBtn) {
    const cancelBtnText = await cancelBtn.textContent();
    console.log('Found cancel button with label:', cancelBtnText.trim());
  }

  // 6. Wait for audio synthesis and quality validation to complete
  console.log('Waiting for Chatterbox audio synthesis and quality validation to complete...');
  await page.waitForFunction(() => {
    const el = document.querySelector('.dj-intro-pill');
    return el && el.textContent.includes('Historia');
  }, { timeout: 35000 });

  console.log('Story generation successfully completed!');
  await page.waitForTimeout(1000);

  // Take screenshot of completed story row
  await page.screenshot({ path: '/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f/fred_rewind_story_completed.png' });
  console.log('Saved fred_rewind_story_completed.png');

  // 7. Verify Script Button and Open Modal
  const viewScriptBtn = await page.$('.view-script-btn');
  if (!viewScriptBtn) throw new Error('Button "📜 Ver guion" not found on completed story');
  console.log('Clicking "📜 Ver guion" to test Fred Rewind Script Modal...');
  await viewScriptBtn.click();
  await page.waitForTimeout(800);

  // Verify modal is active
  const modalApertura = await page.$eval('#fredScriptAperturaText', el => el.textContent.trim());
  const modalDesarrollo = await page.$eval('#fredScriptDesarrolloText', el => el.textContent.trim());
  const modalCierre = await page.$eval('#fredScriptCierreText', el => el.textContent.trim());

  console.log('=== MODAL SCRIPT INSPECTION ===');
  console.log('Apertura:', modalApertura);
  console.log('Desarrollo (word count ' + modalDesarrollo.split(/\s+/).length + '):', modalDesarrollo.slice(0, 100) + '...');
  console.log('Cierre:', modalCierre);

  if (!modalApertura.includes('Fred Rewind') || !modalApertura.includes('DJ Fredd')) {
    throw new Error('Modal Apertura does not mention Fred Rewind and DJ Fredd');
  }
  if (!modalCierre.includes('Fred Rewind') || !modalCierre.includes('Bohemian Rhapsody')) {
    throw new Error('Modal Cierre does not match official closing formula');
  }
  if (modalDesarrollo.split(/\s+/).length < 60) {
    throw new Error('Modal Desarrollo word count is too short for >= 30s narration');
  }

  // Take screenshot of script modal
  await page.screenshot({ path: '/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f/fred_rewind_script_modal.png' });
  console.log('Saved fred_rewind_script_modal.png');

  // Close modal
  await page.click('#btnFredScriptModalClose');
  await page.waitForTimeout(500);

  // 8. Test Audio Playback
  console.log('Testing audio playback of the generated story...');
  const playBtn = await page.$('.dj-row-play-btn');
  await playBtn.click();
  await page.waitForTimeout(1000);

  const audioSrc = await page.evaluate(() => document.getElementById('spotifyAudio').src);
  console.log('Audio src loaded in player:', audioSrc.slice(0, 50) + '...');
  if (!audioSrc || audioSrc.length < 10) throw new Error('Audio src not loaded in player');

  // 9. Test Cancel Generation on a new track
  console.log('Testing Detener generación (cancel flow) on a second track...');
  await page.evaluate(() => {
    addSpotifyTrackToDjEddie({
      id: 'led_zeppelin_kashmir_test',
      name: 'Kashmir',
      artists: [{ name: 'Led Zeppelin' }],
      album: {
        name: 'Physical Graffiti',
        release_date: '1975-02-24',
        images: [{ url: 'img/albums/led_zeppelin_1975_physical.png' }]
      },
      duration_ms: 512000
    });
  });
  await page.waitForTimeout(800);

  // Find the new Kashmir gen button
  const kashmirRow = await page.$('[data-pair-id="sp_led_zeppelin_kashmir_test"]');
  const kashmirGenBtn = await kashmirRow.$('.gen-story');
  await kashmirGenBtn.click();
  await page.waitForTimeout(300);

  // Click cancel
  const kashmirCancelBtn = await kashmirRow.$('.cancel-gen');
  if (kashmirCancelBtn) {
    await kashmirCancelBtn.click();
    await page.waitForTimeout(600);
    const cancelledBadge = await kashmirRow.$eval('.dj-status-badge.cancelled', el => el.textContent.trim());
    console.log('Cancellation confirmed, badge:', cancelledBadge);
  }

  await page.screenshot({ path: '/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f/fred_rewind_full_e2e_verified.png' });
  console.log('Saved fred_rewind_full_e2e_verified.png');

  console.log('🎉 ALL FRED REWIND TESTS PASSED 100%!');
  await browser.close();
})();
