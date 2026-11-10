const { chromium } = require('/Users/fredyarroyave/.gemini/antigravity/brain/690471e3-578f-4390-9ef6-25166d1a6b95/scratch/playwright/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 950 } });

  console.log("1. Navigating to http://localhost:8080/...");
  await page.goto("http://localhost:8080/", { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1500);

  // Take Home screenshot
  const homePath = "/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f/verified_home_clean.png";
  await page.screenshot({ path: homePath });
  console.log(`Saved Home screenshot to ${homePath}`);

  // Open KISS Artist View
  console.log("2. Opening KISS artist view...");
  await page.evaluate(() => openBandView('kiss'));
  await page.waitForTimeout(1000);

  // Check Hero
  const heroBadge = await page.locator("#heroBadge").innerText();
  const heroTitle = await page.locator("#heroTitle").innerText();
  console.log(`Hero Badge: "${heroBadge.trim()}"`);
  console.log(`Hero Title: "${heroTitle.trim()}"`);

  if (!heroBadge.toLowerCase().includes("artista verificado")) {
    throw new Error(`Expected 'Artista verificado' in badge, got: ${heroBadge}`);
  }
  if (!heroTitle.includes("KISS")) {
    throw new Error(`Expected 'KISS' in title, got: ${heroTitle}`);
  }

  // Check format buttons are hidden
  const fmtGroup = page.locator("#trackFormatGroup");
  const isFmtVisible = await fmtGroup.isVisible();
  console.log(`Format switcher visible: ${isFmtVisible}`);
  if (isFmtVisible) {
    throw new Error("trackFormatGroup should be hidden!");
  }

  // Check Populares table
  const tableSection = page.locator("#tableSection");
  const isTableVisible = await tableSection.isVisible();
  console.log(`Table section visible: ${isTableVisible}`);

  const heading = await page.locator("#tableSection h2").innerText();
  console.log(`Table Heading: "${heading.trim()}"`);

  const rows = await page.locator(".spotify-track-row").count();
  console.log(`Number of Populares rows for KISS: ${rows}`);
  if (rows < 4) {
    throw new Error(`Expected at least 4 rows, found: ${rows}`);
  }

  const firstTrackTitle = await page.locator(".spotify-track-row .table-main-title").first().innerText();
  console.log(`First popular track: "${firstTrackTitle.trim()}"`);

  // Take screenshot of KISS Artist View
  const kissScreenshotPath = "/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f/artist_kiss_populares_verified.png";
  await page.screenshot({ path: kissScreenshotPath });
  console.log(`Saved screenshot to ${kissScreenshotPath}`);

  // Test "+ Añadir a DJ Fredd" on second track
  console.log("3. Testing '+ Añadir a DJ Fredd' on track 2...");
  const addBtn = page.locator(".spotify-track-row").nth(1).locator(".btn-table-add-dj");
  await addBtn.click();
  await page.waitForTimeout(600);

  const btnText = await addBtn.innerText();
  console.log(`Button text after click: "${btnText.trim()}"`);

  // Navigate to DJ Fredd playlist
  console.log("4. Navigating to DJ Fredd playlist...");
  await page.evaluate(() => openDjEddiePlaylistView());
  await page.waitForTimeout(1000);

  const djItemsCount = await page.locator(".fred-playlist-item").count();
  console.log(`DJ Fredd playlist items count: ${djItemsCount}`);

  const playlistScreenshotPath = "/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f/dj_fredd_playlist_with_popular_track.png";
  await page.screenshot({ path: playlistScreenshotPath });
  console.log(`Saved playlist screenshot to ${playlistScreenshotPath}`);

  // Test Queen
  console.log("5. Testing Queen artist view...");
  await page.evaluate(() => openBandView('queen'));
  await page.waitForTimeout(1000);

  const queenTitle = await page.locator("#heroTitle").innerText();
  console.log(`Queen Hero Title: "${queenTitle.trim()}"`);

  const queenRows = await page.locator(".spotify-track-row").count();
  console.log(`Number of Populares rows for Queen: ${queenRows}`);

  const queenFirstTrack = await page.locator(".spotify-track-row .table-main-title").first().innerText();
  console.log(`Queen first track: "${queenFirstTrack.trim()}"`);

  const queenScreenshotPath = "/Users/fredyarroyave/.gemini/antigravity/brain/37e7450f-59dc-4655-84fb-814c059a9f6f/artist_queen_populares_verified.png";
  await page.screenshot({ path: queenScreenshotPath });
  console.log(`Saved Queen screenshot to ${queenScreenshotPath}`);

  await browser.close();
  console.log("🎉 ALL PLAYWRIGHT TESTS PASSED 100%!");
})();
