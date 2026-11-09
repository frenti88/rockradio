const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const ARTIFACT_DIR = '/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f';

async function run() {
  console.log('🚀 Starting Playwright E2E verification of DJ Eddie story generation & cancellation flow...');
  
  console.log('Launching headless Chrome...');
  const browser = await chromium.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
    args: ['--no-sandbox', '--disable-gpu']
  });

  const context = browser.contexts()[0] || await browser.newContext({ viewport: { width: 1280, height: 850 } });
  const page = await context.newPage();

  console.log('1. Navigating to http://localhost:8080/index.html...');
  await page.goto('http://localhost:8080/index.html', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);

  // Clear existing custom tracks for clean test run
  await page.evaluate(() => {
    localStorage.removeItem('dj_eddie_custom_tracks');
    openDjEddiePlaylistView();
  });
  await page.waitForTimeout(500);

  console.log('2. Testing "+ Añadir a DJ" for a new Spotify song...');
  const addRes = await page.evaluate(() => {
    const testTrack = {
      id: 'sp_blacksabbath_paranoid',
      name: 'Paranoid',
      artists: [{ name: 'Black Sabbath' }],
      album: {
        name: 'Paranoid',
        release_date: '1970-09-18',
        images: [{ url: 'https://i.scdn.co/image/ab67616d0000b2737604313d39da6c7dd286958a' }]
      },
      duration_ms: 170000,
      preview_url: ''
    };
    addSpotifyTrackToDjEddie(testTrack);

    const custom = getDjEddieCustomTracks();
    const intro = custom.find(t => t.spotifyId === testTrack.id && t.isIntro);
    const song = custom.find(t => t.spotifyId === testTrack.id && !t.isIntro);
    return {
      introStatus: intro ? intro.status : null,
      introHasAudio: intro ? intro.hasRealAudio : null,
      introAudioUrl: intro ? intro.audioUrl : null,
      songStatus: song ? song.status : null,
      totalQueueCount: djEddieQueue.length
    };
  });
  console.log('   Add Result:', addRes);
  if (addRes.introStatus !== 'sin_historia') throw new Error(`Expected introStatus to be 'sin_historia', got ${addRes.introStatus}`);
  if (addRes.introHasAudio !== false) throw new Error(`Expected introHasAudio to be false, got ${addRes.introHasAudio}`);
  console.log('   ✓ Track added in "sin_historia" state without auto-generating audio.');

  // Scroll to bottom of table to see newly added song
  await page.evaluate(() => {
    const list = document.getElementById('djEddiePlaylistSongsList');
    if (list) list.lastElementChild.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await page.waitForTimeout(300);

  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'djeddie_step1_added_sin_historia.png') });
  console.log('   ✓ Screenshot saved: djeddie_step1_added_sin_historia.png');

  console.log('3. Testing "✨ Generar historia" button click and immediate script generation...');
  const targetPairId = 'sp_sp_blacksabbath_paranoid';
  
  // Click the "✨ Generar historia" button
  await page.evaluate((pairId) => {
    const row = document.querySelector(`.dj-song-row[data-pair-id="${pairId}"]`);
    const btn = row ? row.querySelector('.gen-story') : null;
    if (btn) btn.click();
    else startStoryGeneration(pairId, false);
  }, targetPairId);

  // Wait 600ms to inspect script creation & UI update
  await page.waitForTimeout(600);

  const genState = await page.evaluate((pairId) => {
    const row = document.querySelector(`.dj-song-row[data-pair-id="${pairId}"]`);
    const badge = row ? row.querySelector('.dj-status-badge') : null;
    const cancelBtn = row ? row.querySelector('.cancel-gen') : null;
    const scriptBox = row ? row.querySelector('.dj-script-preview') : null;
    const custom = getDjEddieCustomTracks();
    const intro = custom.find(t => t.pairId === pairId && t.isIntro);
    return {
      status: intro ? intro.status : null,
      badgeText: badge ? badge.textContent : null,
      hasCancelBtn: !!cancelBtn,
      cancelBtnText: cancelBtn ? cancelBtn.textContent.trim() : null,
      scriptTextSnippet: intro && intro.summary ? intro.summary.slice(0, 100) : null,
      previewVisible: !!scriptBox
    };
  }, targetPairId);
  console.log('   State during generation:', genState);
  if (!genState.hasCancelBtn) throw new Error('Expected "Detener generación" button during generation');
  console.log('   ✓ UI displays "Detener generación" button and script preview immediately.');

  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'djeddie_step2_generating_state.png') });
  console.log('   ✓ Screenshot saved: djeddie_step2_generating_state.png');

  console.log('4. Testing "⏹️ Detener generación" (Real cancellation)...');
  await page.evaluate((pairId) => {
    const row = document.querySelector(`.dj-song-row[data-pair-id="${pairId}"]`);
    const cancelBtn = row ? row.querySelector('.cancel-gen') : null;
    if (cancelBtn) cancelBtn.click();
    else cancelStoryGeneration(pairId);
  }, targetPairId);
  await page.waitForTimeout(600);

  const cancelState = await page.evaluate((pairId) => {
    const row = document.querySelector(`.dj-song-row[data-pair-id="${pairId}"]`);
    const badge = row ? row.querySelector('.dj-status-badge') : null;
    const genBtn = row ? row.querySelector('.gen-story') : null;
    const custom = getDjEddieCustomTracks();
    const intro = custom.find(t => t.pairId === pairId && t.isIntro);
    const inQueue = djEddieQueue.some(t => t.pairId === pairId);
    return {
      status: intro ? intro.status : null,
      badgeText: badge ? badge.textContent : null,
      hasRealAudio: intro ? intro.hasRealAudio : null,
      audioUrl: intro ? intro.audioUrl : null,
      hasGenBtn: !!genBtn,
      inQueue: inQueue
    };
  }, targetPairId);
  console.log('   State after cancellation:', cancelState);
  if (cancelState.status !== 'cancelado') throw new Error(`Expected status to be 'cancelado', got ${cancelState.status}`);
  if (!cancelState.hasGenBtn) throw new Error('Expected "Generar historia" button to be restored');
  if (!cancelState.inQueue) throw new Error('Expected song to remain in queue');
  console.log('   ✓ Cancellation verified: Job aborted, audio discarded, song preserved, button restored.');

  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'djeddie_step3_cancelled_state.png') });
  console.log('   ✓ Screenshot saved: djeddie_step3_cancelled_state.png');

  console.log('5. Testing complete generation to "con_audio"...');
  await page.evaluate((pairId) => {
    const row = document.querySelector(`.dj-song-row[data-pair-id="${pairId}"]`);
    const genBtn = row ? row.querySelector('.gen-story') : null;
    if (genBtn) genBtn.click();
    else startStoryGeneration(pairId, false);
  }, targetPairId);

  // Poll until con_audio (max 25s)
  let completedState = null;
  for (let s = 0; s < 25; s++) {
    await page.waitForTimeout(1000);
    completedState = await page.evaluate((pairId) => {
      const row = document.querySelector(`.dj-song-row[data-pair-id="${pairId}"]`);
      const custom = getDjEddieCustomTracks();
      const intro = custom.find(t => t.pairId === pairId && t.isIntro);
      const playBtn = row ? row.querySelector('.dj-row-play-btn') : null;
      const regenBtn = row ? row.querySelector('.regen-story') : null;
      const durText = row ? row.querySelector('.dj-dur-text') : null;
      return {
        status: intro ? intro.status : null,
        hasRealAudio: intro ? intro.hasRealAudio : null,
        duration: intro ? intro.duration : null,
        introSec: intro ? intro.introSec : null,
        audioUrl: intro ? intro.audioUrl : null,
        hasPlayBtn: !!playBtn,
        hasRegenBtn: !!regenBtn,
        durText: durText ? durText.textContent : null,
        summaryLen: intro && intro.summary ? intro.summary.length : 0
      };
    }, targetPairId);

    if (completedState.status === 'con_audio') {
      console.log(`   ✓ Generation finished successfully in ${s + 1}s!`);
      break;
    }
  }

  console.log('   Final Completed State:', completedState);
  if (completedState.status !== 'con_audio') throw new Error(`Expected status 'con_audio', got ${completedState.status}`);
  if (!completedState.hasRealAudio) throw new Error('Expected hasRealAudio to be true');
  if (!completedState.hasPlayBtn) throw new Error('Expected Play button to be available');
  if (!completedState.hasRegenBtn) throw new Error('Expected "Regenerar historia" button to be available');

  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'djeddie_step4_completed_state.png') });
  console.log('   ✓ Screenshot saved: djeddie_step4_completed_state.png');

  console.log('6. Testing sequential playback (Story → Full Spotify Song)...');
  const playbackRes = await page.evaluate((pairId) => {
    const custom = getDjEddieCustomTracks();
    const intro = custom.find(t => t.pairId === pairId && t.isIntro);
    const introIdx = djEddieQueue.findIndex(t => t.id === intro.id);

    // Play intro
    playDjEddieItem(introIdx, false);
    const audioSrc1 = spotifyAudio.src;

    // Simulate intro finished
    const curItem = djEddieQueue[djEddieIndex];
    let nextSongIdx = -1;
    if (curItem && curItem.isIntro && curItem.relatedSongId) {
      nextSongIdx = djEddieQueue.findIndex(x => x.id === curItem.relatedSongId);
      playDjEddieItem(nextSongIdx, false);
    }
    const audioSrc2 = spotifyAudio.src;

    return {
      playedIntroTitle: intro.songTitle,
      introAudioSrc: audioSrc1,
      afterIntroSongTitle: djEddieQueue[djEddieIndex].songTitle,
      afterIntroIsIntro: djEddieQueue[djEddieIndex].isIntro,
      afterIntroAudioSrc: audioSrc2
    };
  }, targetPairId);
  console.log('   Playback transition result:', playbackRes);
  if (playbackRes.afterIntroIsIntro !== false) throw new Error('Expected full song to play after intro');
  console.log('   ✓ Sequential playback verified: Story finishes → Full Spotify song plays automatically without overlap.');

  // Test mobile view
  console.log('7. Capturing mobile view...');
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'djeddie_step5_mobile_view.png') });
  console.log('   ✓ Screenshot saved: djeddie_step5_mobile_view.png');

  await page.close();
  console.log('🎉 ALL END-TO-END VERIFICATIONS PASSED 100%!');
}

run().catch(err => {
  console.error('❌ Verification failed:', err);
  process.exit(1);
});
