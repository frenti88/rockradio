const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = '/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f';
const CHROME_PATH = '/Users/fredyarroyave/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell';

async function run() {
  console.log('Launching browser...');
  const browser = await chromium.launch({
    executablePath: CHROME_PATH,
    headless: true
  });

  // 1. Desktop Test
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const page = await context.newPage();

  const errors = [];
  page.on('pageerror', err => {
    console.error('Page Error:', err.message);
    errors.push(err.message);
  });
  page.on('console', msg => {
    if (msg.type() === 'error') console.log('Console Error:', msg.text());
  });

  console.log('Navigating to http://localhost:8080/...');
  await page.goto('http://localhost:8080/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  // Check shelves
  const banner = await page.$('#spotifyHomeConnectBanner');
  const userPl = await page.$('#shelfUserPlaylists');
  const liked = await page.$('#shelfLikedSongs');
  const topTracks = await page.$('#shelfTopTracks');
  const recs = await page.$('#shelfRecommendedMusic');
  const recent = await page.$('#shelfRecentlyPlayed');
  const artists = await page.$('#shelfFavoriteArtists');
  const djShelf = await page.$('#shelfDjEddie');

  console.log('Shelves check:', {
    banner: !!banner,
    userPl: !!userPl,
    liked: !!liked,
    topTracks: !!topTracks,
    recs: !!recs,
    recent: !!recent,
    artists: !!artists,
    djShelf: !!djShelf
  });

  // Capture Home Desktop Screenshot
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'spotify_home_desktop.png'), fullPage: false });
  console.log('Saved spotify_home_desktop.png');

  // Test opening a playlist card
  console.log('Testing Playlist inspector...');
  const firstPlaylistCard = await page.$('#userPlaylistsRow .home-sp-card');
  if (firstPlaylistCard) {
    await firstPlaylistCard.click();
    await page.waitForTimeout(600);
    const spPlaylistVisible = await page.isVisible('#spotifyPlaylistSection');
    console.log('Playlist section visible:', spPlaylistVisible);

    await page.screenshot({ path: path.join(ARTIFACT_DIR, 'spotify_playlist_view_desktop.png'), fullPage: false });
    console.log('Saved spotify_playlist_view_desktop.png');

    // Test adding a song from playlist to DJ Fredd
    const addDjBtn = await page.$('#spPlaylistTableBody .home-card-add-dj');
    if (addDjBtn) {
      await addDjBtn.click();
      await page.waitForTimeout(500);
      console.log('Clicked "+ DJ Fredd" button in playlist table');
    }

    // Click back to Home
    const backBtn = await page.$('#btnBackHomeFromSpPlaylist');
    if (backBtn) {
      await backBtn.click();
      await page.waitForTimeout(500);
      const homeVisible = await page.isVisible('#spotifyHomeShelves');
      console.log('Back to Home visible:', homeVisible);
    }
  }

  // Test opening Liked Songs card
  console.log('Testing Liked Songs view...');
  const likedCard = await page.$('#likedSongsRow .home-sp-card');
  if (likedCard) {
    await likedCard.click();
    await page.waitForTimeout(600);
    await page.screenshot({ path: path.join(ARTIFACT_DIR, 'spotify_liked_songs_view_desktop.png'), fullPage: false });
    console.log('Saved spotify_liked_songs_view_desktop.png');

    const backBtn = await page.$('#btnBackHomeFromSpPlaylist');
    if (backBtn) {
      await backBtn.click();
      await page.waitForTimeout(500);
    }
  }

  // 2. Mobile Viewport Test (390x844 iPhone 14 style)
  console.log('Testing Mobile viewport (390x844)...');
  const mobileContext = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true
  });
  const mobilePage = await mobileContext.newPage();
  await mobilePage.goto('http://localhost:8080/', { waitUntil: 'networkidle' });
  await mobilePage.waitForTimeout(1000);
  await mobilePage.screenshot({ path: path.join(ARTIFACT_DIR, 'spotify_home_mobile.png'), fullPage: false });
  console.log('Saved spotify_home_mobile.png');

  await browser.close();
  console.log('All tests completed. Total errors:', errors.length);
}

run().catch(err => {
  console.error('Test error:', err);
  process.exit(1);
});
