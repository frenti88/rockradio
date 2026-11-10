const { chromium } = require('/Users/fredyarroyave/.gemini/antigravity/brain/690471e3-578f-4390-9ef6-25166d1a6b95/scratch/playwright/node_modules/playwright');
const fs = require('fs');

(async () => {
  console.log('🚀 Starting Native AI Story Generation E2E Test...');
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  });
  const context = await browser.newContext({ viewport: { width: 1440, height: 950 } });
  const page = await context.newPage();

  page.on('console', msg => {
    const text = msg.text();
    if (msg.type() === 'error' || text.includes('FRED') || text.includes('DJ') || text.includes('story')) {
      console.log('BROWSER LOG:', text);
    }
  });

  await page.goto('http://localhost:8080/index.html', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);

  // 1. Open DJ Fredd Playlist View
  console.log('Navigating to DJ Fredd playlist view...');
  await page.evaluate(() => {
    if (typeof openDjEddiePlaylistView === 'function') {
      openDjEddiePlaylistView();
    }
  });
  await page.waitForTimeout(800);

  // 2. Add "Sweet Child O' Mine" to DJ Fredd playlist
  console.log('Adding "Sweet Child O\' Mine" by Guns N\' Roses to playlist...');
  await page.evaluate(() => {
    addSpotifyTrackToDjEddie({
      id: 'gnr_sweet_child_ai_test',
      name: "Sweet Child O' Mine",
      artists: [{ name: "Guns N' Roses" }],
      album: {
        name: 'Appetite for Destruction',
        release_date: '1987-07-21',
        images: [{ url: 'https://i.scdn.co/image/ab67616d0000b27376092040d1e3d3e64816be60' }]
      },
      duration_ms: 356000
    });
  });
  await page.waitForTimeout(800);

  const testPairId = 'sp_gnr_sweet_child_ai_test';
  const introRow = await page.$(`[data-pair-id="${testPairId}"].is-intro-row`);
  if (!introRow) throw new Error(`Row for pairId ${testPairId} not found`);

  // 3. Verify initial state: "Sin historia"
  const initialBadge = await introRow.$eval('.dj-status-badge', el => el.textContent.trim());
  console.log('Initial badge status:', initialBadge);
  if (!initialBadge.includes('Sin historia')) {
    throw new Error(`Expected "Sin historia", got "${initialBadge}"`);
  }

  // 4. Click "✨ Generar historia"
  const genBtn = await introRow.$('.gen-story');
  if (!genBtn) throw new Error('Button "✨ Generar historia" not found');
  console.log('Clicking "✨ Generar historia"...');
  await genBtn.click();

  // 5. Track state transitions
  console.log('Observing state transitions...');
  let seenInvestigando = false;
  let seenGenerandoHistoria = false;
  let seenGuionGenerado = false;
  let seenGenerandoAudio = false;

  const startTime = Date.now();
  while (Date.now() - startTime < 35000) {
    const badgeText = await page.evaluate(pairId => {
      const row = document.querySelector(`[data-pair-id="${pairId}"].is-intro-row`);
      const badge = row ? row.querySelector('.dj-status-badge, .dj-intro-pill') : null;
      return badge ? badge.textContent.trim() : '';
    }, testPairId);

    if (badgeText.includes('Investigando canción')) {
      if (!seenInvestigando) {
        seenInvestigando = true;
        console.log('✓ Observed state: Investigando canción...');
      }
    } else if (badgeText.includes('Generando historia')) {
      if (!seenGenerandoHistoria) {
        seenGenerandoHistoria = true;
        console.log('✓ Observed state: Generando historia con IA...');
      }
    } else if (badgeText.includes('Guion generado')) {
      if (!seenGuionGenerado) {
        seenGuionGenerado = true;
        console.log('✓ Observed state: Guion generado!');
      }
    } else if (badgeText.includes('Generando audio') || badgeText.includes('Sintetizando audio')) {
      if (!seenGenerandoAudio) {
        seenGenerandoAudio = true;
        console.log('✓ Observed state: Generando audio en Chatterbox...');
      }
    } else if (badgeText.includes('Historia') && (badgeText.includes('disponibles') || badgeText.includes('DJ Fredd'))) {
      console.log('✓ Final completed state reached:', badgeText);
      break;
    }

    await page.waitForTimeout(300);
  }

  // 6. Inspect the generated script from the UI item
  const scriptPreviewText = await page.evaluate(pairId => {
    const row = document.querySelector(`[data-pair-id="${pairId}"].is-intro-row`);
    const preview = row ? row.querySelector('.dj-script-preview .dj-script-text') : null;
    return preview ? preview.textContent.trim() : '';
  }, testPairId);

  console.log('\n=== GENERATED SCRIPT PREVIEW IN UI ===');
  console.log(scriptPreviewText);

  if (!scriptPreviewText) {
    throw new Error('Script preview was not rendered in song item');
  }
  if (!scriptPreviewText.includes('Fred Rewind') || !scriptPreviewText.includes('DJ Fredd')) {
    throw new Error('Script does not contain official Apertura');
  }
  if (!scriptPreviewText.includes('La música tiene memoria')) {
    throw new Error('Script does not contain insignia phrase "La música tiene memoria"');
  }
  if (!scriptPreviewText.includes('Sube el volumen') || !scriptPreviewText.includes("Sweet Child O' Mine")) {
    throw new Error('Script does not contain official Cierre');
  }

  // Take screenshot of completed story
  await page.screenshot({ path: '/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f/native_ai_story_completed.png' });
  console.log('Saved native_ai_story_completed.png');

  // 7. Test copying script with mini copy button
  const copyBtn = await introRow.$('.dj-copy-script-mini');
  if (copyBtn) {
    await copyBtn.click();
    console.log('✓ Clicked inline "📋 Copiar" button');
    await page.waitForTimeout(400);
  }

  // 8. Test script modal inspection
  const viewScriptBtn = await introRow.$('.view-script-btn');
  if (viewScriptBtn) {
    await viewScriptBtn.click();
    await page.waitForTimeout(600);
    const modalTitle = await page.$eval('#fredScriptModalSongTitle', el => el.textContent.trim());
    const modalApertura = await page.$eval('#fredScriptAperturaText', el => el.textContent.trim());
    const modalDesarrollo = await page.$eval('#fredScriptDesarrolloText', el => el.textContent.trim());
    const modalCierre = await page.$eval('#fredScriptCierreText', el => el.textContent.trim());

    console.log('\n=== MODAL VERIFICATION ===');
    console.log('Title:', modalTitle);
    console.log('Apertura:', modalApertura);
    console.log('Desarrollo words:', modalDesarrollo.split(/\s+/).length);
    console.log('Cierre:', modalCierre);

    await page.screenshot({ path: '/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f/native_ai_script_modal.png' });
    console.log('Saved native_ai_script_modal.png');

    await page.click('#btnFredScriptModalClose');
    await page.waitForTimeout(400);
  }

  // 9. Test Story Playback
  console.log('Testing Story Audio Playback...');
  const playBtn = await introRow.$('.dj-row-play-btn');
  if (playBtn) {
    await playBtn.click();
    await page.waitForTimeout(1000);
    const audioState = await page.evaluate(() => {
      const a = document.getElementById('spotifyAudio');
      return { src: a ? a.src : null, paused: a ? a.paused : true };
    });
    console.log('Player state:', audioState);
    if (!audioState.src) throw new Error('Audio src not loaded in player');
  }

  // 10. Test Cancellation Flow on second track
  console.log('\nTesting "Detener generación" cancellation flow on AC/DC "Highway to Hell"...');
  await page.evaluate(() => {
    addSpotifyTrackToDjEddie({
      id: 'acdc_highway_cancel_test',
      name: 'Highway to Hell',
      artists: [{ name: 'AC/DC' }],
      album: {
        name: 'Highway to Hell',
        release_date: '1979-07-27',
        images: [{ url: 'https://i.scdn.co/image/ab67616d0000b2737a28e08d6b81a94156dc8122' }]
      },
      duration_ms: 208000
    });
  });
  await page.waitForTimeout(800);

  const cancelTestPairId = 'sp_acdc_highway_cancel_test';
  const cancelRow = await page.$(`[data-pair-id="${cancelTestPairId}"].is-intro-row`);
  const cancelGenBtn = await cancelRow.$('.gen-story');
  await cancelGenBtn.click();
  await page.waitForTimeout(300);

  // Wait for and click cancel button (query from page to avoid stale element reference)
  await page.waitForSelector(`[data-pair-id="${cancelTestPairId}"] .cancel-gen`, { timeout: 5000 });
  const stopBtn = await page.$(`[data-pair-id="${cancelTestPairId}"] .cancel-gen`);
  if (!stopBtn) throw new Error('Button "⏹️ Detener generación" not found during generation');
  console.log('Clicking "⏹️ Detener generación"...');
  await stopBtn.click();
  await page.waitForTimeout(1000);

  // Verify cancelled badge
  const cancelledBadge = await page.$eval(`[data-pair-id="${cancelTestPairId}"] .dj-status-badge.cancelled`, el => el.textContent.trim());
  console.log('Cancelled badge result:', cancelledBadge);
  if (!cancelledBadge.includes('Generación cancelada')) {
    throw new Error(`Expected "Generación cancelada", got "${cancelledBadge}"`);
  }

  // Verify re-trigger button "✨ Generar historia" is back
  const reGenBtn = await page.$(`[data-pair-id="${cancelTestPairId}"] .gen-story`);
  if (!reGenBtn) throw new Error('Button "✨ Generar historia" should be available after cancellation');

  await page.screenshot({ path: '/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f/native_ai_cancellation_verified.png' });
  console.log('Saved native_ai_cancellation_verified.png');

  console.log('\n🎯 ALL NATIVE AI STORY GENERATION TESTS PASSED 100%!');
  await browser.close();
})();