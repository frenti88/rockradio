const { chromium } = require('playwright-core');
const path = require('path');
const { execSync } = require('child_process');

const ARTIFACT_DIR = '/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f';

async function run() {
  console.log('🚀 Starting E2E verification for DJ FREDD — Rock Radio Identity & Voice...');
  
  const browser = await chromium.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
    args: ['--no-sandbox', '--disable-gpu']
  });

  const context = await browser.newContext({ viewport: { width: 1400, height: 900 } });
  const page = await context.newPage();

  page.on('console', msg => {
    const text = msg.text();
    if (text.includes('[DJ') || text.includes('Toast') || text.includes('Error')) {
      console.log(`  [BROWSER] ${text}`);
    }
  });

  console.log('1. Navigating to http://localhost:8080/index.html...');
  await page.goto('http://localhost:8080/index.html', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);

  // 2. Verify Home Screen Branding for DJ Fredd
  console.log('2. Verifying Home Screen branding for DJ Fredd...');
  const heroInfo = await page.evaluate(() => {
    const title = document.querySelector('.dj-eddie-title')?.textContent;
    const desc = document.getElementById('djEddieHeroDesc')?.textContent;
    const filterPill = document.querySelector('.djeddie-pill')?.textContent;
    const shelfTitle = document.querySelector('#shelfDjEddie .home-shelf-title')?.textContent;
    const shelfSub = document.querySelector('#shelfDjEddie .home-shelf-subtitle')?.textContent;
    return { title, desc, filterPill, shelfTitle, shelfSub };
  });

  console.log('   Hero branding:', heroInfo);
  if (!heroInfo.title.includes('DJ Fredd') || !heroInfo.desc.includes('La música tiene memoria')) {
    throw new Error('Home hero branding does not match DJ Fredd!');
  }

  const shotHome = path.join(ARTIFACT_DIR, 'dj_fredd_1_home_hero.png');
  await page.screenshot({ path: shotHome, fullPage: false });
  console.log(`   ✓ Saved screenshot: ${shotHome}`);

  // 3. Navigate to DJ Fredd Playlist View
  console.log('3. Navigating to DJ Fredd Playlist View...');
  await page.evaluate(() => {
    openDjEddiePlaylistView();
  });
  await page.waitForTimeout(1000);

  const playlistHeader = await page.evaluate(() => {
    const mainTitle = document.querySelector('.dj-playlist-main-title')?.textContent;
    const mainDesc = document.querySelector('.dj-playlist-main-desc')?.textContent;
    const trackCount = document.getElementById('djPlaylistTrackCount')?.textContent;
    return { mainTitle, mainDesc, trackCount };
  });

  console.log('   Playlist view branding:', playlistHeader);
  if (!playlistHeader.mainTitle.includes('DJ Fredd') || !playlistHeader.mainDesc.includes('La música tiene memoria')) {
    throw new Error('Playlist view branding does not match DJ Fredd!');
  }

  // 4. Test Adding a Track to DJ Fredd
  console.log('4. Adding "Come Together" by The Beatles to DJ Fredd...');
  const addResult = await page.evaluate(() => {
    const track = {
      id: 'sp_the_beatles_come_together',
      name: 'Come Together',
      artists: [{ name: 'The Beatles' }],
      album: {
        name: 'Abbey Road',
        release_date: '1969',
        images: [{ url: 'https://i.scdn.co/image/ab67616d0000b273dc30583ba717007b00cceb25' }]
      },
      duration_ms: 259000
    };
    window.addSpotifyTrackToDjEddie(track);
    const custom = window.getDjEddieCustomTracks();
    const intro = custom.find(t => t.spotifyId === track.id && t.isIntro);
    const song = custom.find(t => t.spotifyId === track.id && !t.isIntro);
    return { introId: intro ? intro.id : null, pairId: intro ? intro.pairId : null, songId: song ? song.id : null };
  });

  console.log('   Add result for DJ Fredd:', addResult);
  await page.waitForTimeout(1000);

  const shotAdded = path.join(ARTIFACT_DIR, 'dj_fredd_2_track_added.png');
  await page.screenshot({ path: shotAdded, fullPage: false });
  console.log(`   ✓ Saved screenshot: ${shotAdded}`);

  // 5. Click 'Generar historia' for DJ Fredd
  console.log('5. Clicking "Generar historia" with DJ Fredd voice engine...');
  const genBtn = await page.waitForSelector(`.dj-song-row[data-pair-id="${addResult.pairId}"].is-intro-row button.dj-action-btn.gen-story`);
  await genBtn.click();

  // Wait 1s and capture generating state with DJ Fredd toast
  await page.waitForTimeout(1200);
  const shotGen = path.join(ARTIFACT_DIR, 'dj_fredd_3_generating_toast.png');
  await page.screenshot({ path: shotGen, fullPage: false });
  console.log(`   ✓ Saved screenshot (generating state + toast): ${shotGen}`);

  // 6. Poll for backend synthesis completion
  console.log('6. Waiting for DJ Fredd audio synthesis (es-CO-GonzaloNeural + analog master chain)...');
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
        summary: intro.summary ? intro.summary.slice(0, 100) + '...' : ''
      } : null;
    }, addResult.pairId);

    console.log(`   [${elapsed}s] Intro Status:`, status);
    if (status && status.status === 'con_audio' && status.hasRealAudio) {
      completed = true;
      console.log(`   ✓ Generation finished in ${status.genElapsedSec}s! Audio: ${status.audioUrl}`);
      console.log(`   Guion DJ Fredd: ${status.summary}`);
      break;
    }
    await page.waitForTimeout(2000);
    elapsed += 2;
  }

  if (!completed) {
    throw new Error('Audio generation timed out for DJ Fredd');
  }

  await page.waitForTimeout(1500);

  const shotDone = path.join(ARTIFACT_DIR, 'dj_fredd_4_completed_state.png');
  await page.screenshot({ path: shotDone, fullPage: false });
  console.log(`   ✓ Saved screenshot (completed state): ${shotDone}`);

  // 7. Test Playback of DJ Fredd Story
  console.log('7. Testing playback of DJ Fredd story...');
  const playBtn = await page.waitForSelector(`.dj-song-row[data-pair-id="${addResult.pairId}"].is-intro-row .dj-row-play-btn`);
  await playBtn.click();

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
      src: audio ? audio.src.slice(0, 60) + '...' : '',
      footerTitle: titleEl ? titleEl.textContent : '',
      footerArtist: artistEl ? artistEl.textContent : '',
      lyricsRendered: lyricsEl ? lyricsEl.children.length : 0,
      activeLyricText: activeLyric ? activeLyric.textContent : ''
    };
  });

  console.log('   Playback state:', playbackState);

  const shotPlay = path.join(ARTIFACT_DIR, 'dj_fredd_5_playback_desktop.png');
  await page.screenshot({ path: shotPlay, fullPage: false });
  console.log(`   ✓ Saved screenshot (desktop playback + synced lyrics): ${shotPlay}`);

  // 8. Mobile Viewport Playback (iPhone 14)
  console.log('8. Testing mobile viewport (iPhone 14: 390x844)...');
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(1200);

  const shotMobile = path.join(ARTIFACT_DIR, 'dj_fredd_6_playback_mobile.png');
  await page.screenshot({ path: shotMobile, fullPage: false });
  console.log(`   ✓ Saved screenshot (mobile playback): ${shotMobile}`);

  await browser.close();
  console.log('🎉 DJ Fredd identity verification passed completely!');
}

run().catch(err => {
  console.error('Test failed with error:', err);
  process.exit(1);
});
