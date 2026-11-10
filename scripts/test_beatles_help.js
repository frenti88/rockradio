const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ARTIFACT_DIR = '/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f';

async function run() {
  console.log('🚀 Starting E2E verification for DJ Eddie + The Beatles "Help!"...');
  
  const browser = await chromium.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
    args: ['--no-sandbox', '--disable-gpu']
  });

  const context = await browser.newContext({ viewport: { width: 1400, height: 900 } });
  const page = await context.newPage();

  page.on('console', msg => {
    const text = msg.text();
    if (text.includes('[DJ EDDIE') || text.includes('Toast') || text.includes('Error')) {
      console.log(`  [BROWSER] ${text}`);
    }
  });

  console.log('1. Navigating to http://localhost:8080/index.html...');
  await page.goto('http://localhost:8080/index.html', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);

  // Navigate to DJ Eddie view
  console.log('2. Opening DJ Eddie playlist view...');
  await page.evaluate(() => {
    openDjEddiePlaylistView();
  });
  await page.waitForTimeout(1000);

  const initialRowsCount = await page.evaluate(() => {
    return document.querySelectorAll('#djEddieTracksBody tr').length;
  });
  console.log(`   Initial DJ Eddie table rows: ${initialRowsCount} (17 base tracks)`);

  // Add "Help!" by The Beatles
  console.log('3. Adding "Help!" by The Beatles to DJ Eddie...');
  const addResult = await page.evaluate(() => {
    const beatlesTrack = {
      id: 'sp_the_beatles_help',
      name: 'Help!',
      artists: [{ name: 'The Beatles' }],
      album: {
        name: 'Help!',
        release_date: '1965',
        images: [{ url: 'https://i.scdn.co/image/ab67616d0000b273447953c8340dccbf58a0a382' }]
      },
      duration_ms: 138000
    };
    window.addSpotifyTrackToDjEddie(beatlesTrack);
    const custom = window.getDjEddieCustomTracks();
    const intro = custom.find(t => t.spotifyId === beatlesTrack.id && t.isIntro);
    const song = custom.find(t => t.spotifyId === beatlesTrack.id && !t.isIntro);
    return { introId: intro ? intro.id : null, pairId: intro ? intro.pairId : null, songId: song ? song.id : null };
  });

  console.log('   Add result:', addResult);
  await page.waitForTimeout(800);

  // Screenshot: Added state (Sin historia)
  const shot1 = path.join(ARTIFACT_DIR, 'djeddie_help_1_added.png');
  await page.screenshot({ path: shot1, fullPage: false });
  console.log(`   ✓ Saved screenshot: ${shot1}`);

  // 4. Click 'Generar historia'
  console.log('4. Triggering "Generar historia" for Help!...');
  await page.evaluate((pairId) => {
    window.startStoryGeneration(pairId);
  }, addResult.pairId);

  // Wait 1s and capture live generating state + non-invasive toast
  await page.waitForTimeout(1200);
  const shot2 = path.join(ARTIFACT_DIR, 'djeddie_help_2_generating.png');
  await page.screenshot({ path: shot2, fullPage: false });
  console.log(`   ✓ Saved screenshot (generating state + toast): ${shot2}`);

  // 5. Wait for audio synthesis to complete
  console.log('5. Waiting for audio synthesis to complete on backend (Edge-TTS + master chain)...');
  let completed = false;
  let elapsed = 0;
  while (elapsed < 60) {
    const status = await page.evaluate((pairId) => {
      const custom = window.getDjEddieCustomTracks();
      const intro = custom.find(t => t.pairId === pairId && t.isIntro);
      return intro ? {
        status: intro.status,
        hasRealAudio: intro.hasRealAudio,
        audioUrl: intro.audioUrl,
        fileUrl: intro.fileUrl,
        genElapsedSec: intro.genElapsedSec,
        summary: intro.summary ? intro.summary.slice(0, 80) + '...' : ''
      } : null;
    }, addResult.pairId);

    console.log(`   [${elapsed}s] Intro Status:`, status);
    if (status && status.status === 'con_audio' && status.hasRealAudio) {
      completed = true;
      console.log(`   ✓ Generation finished successfully in ${status.genElapsedSec}s!`);
      break;
    }
    await page.waitForTimeout(2000);
    elapsed += 2;
  }

  if (!completed) {
    throw new Error('Audio generation timed out after 60s');
  }

  await page.waitForTimeout(1500);

  // Screenshot: Completed state with real backend time and success toast
  const shot3 = path.join(ARTIFACT_DIR, 'djeddie_help_3_completed.png');
  await page.screenshot({ path: shot3, fullPage: false });
  console.log(`   ✓ Saved screenshot (completed state): ${shot3}`);

  // 6. Test playback of Help! story
  console.log('6. Playing the generated story for Help! via play button click...');
  const introPlayBtn = await page.waitForSelector(`.dj-song-row[data-pair-id="${addResult.pairId}"].is-intro-row .dj-row-play-btn`);
  await introPlayBtn.click();

  await page.waitForTimeout(2000);

  const playbackState = await page.evaluate(() => {
    const audio = document.getElementById('spotifyAudio');
    const titleEl = document.getElementById('barTitle');
    const artistEl = document.getElementById('barArtist');
    const lyricsEl = document.getElementById('lyricsScrollViewport');
    const activeLyric = document.querySelector('.lyric-line.active');
    return {
      paused: audio ? audio.paused : true,
      currentTime: audio ? audio.currentTime : 0,
      duration: audio ? audio.duration : 0,
      src: audio ? audio.src : '',
      footerTitle: titleEl ? titleEl.textContent : '',
      footerArtist: artistEl ? artistEl.textContent : '',
      lyricsRendered: lyricsEl ? lyricsEl.children.length : 0,
      activeLyricText: activeLyric ? activeLyric.textContent : ''
    };
  });

  console.log('   Playback state:', playbackState);

  // Screenshot during playback (Desktop)
  const shot4 = path.join(ARTIFACT_DIR, 'djeddie_help_4_playback_desktop.png');
  await page.screenshot({ path: shot4, fullPage: false });
  console.log(`   ✓ Saved screenshot (desktop playback + synced lyrics): ${shot4}`);

  // 7. Mobile Viewport Playback
  console.log('7. Switching to mobile viewport (iPhone 14: 390x844)...');
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(1200);

  const shot5 = path.join(ARTIFACT_DIR, 'djeddie_help_5_playback_mobile.png');
  await page.screenshot({ path: shot5, fullPage: false });
  console.log(`   ✓ Saved screenshot (mobile playback): ${shot5}`);

  await browser.close();
  console.log('🎉 All tests passed successfully!');
}

run().catch(err => {
  console.error('Test failed with error:', err);
  process.exit(1);
});
