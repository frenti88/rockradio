import re
import sys

def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update SPOTIFY_SCOPES
    old_scopes = """    const SPOTIFY_SCOPES = [
      'user-read-private',
      'user-read-email',
      'streaming',
      'user-read-playback-state',
      'user-modify-playback-state',
      'user-read-currently-playing'
    ].join(' ');"""

    new_scopes = """    const SPOTIFY_SCOPES = [
      'user-read-private',
      'user-read-email',
      'streaming',
      'user-read-playback-state',
      'user-modify-playback-state',
      'user-read-currently-playing',
      'playlist-read-private',
      'playlist-read-collaborative',
      'user-top-read',
      'user-library-read',
      'user-read-recently-played'
    ].join(' ');"""

    if old_scopes in content:
        content = content.replace(old_scopes, new_scopes, 1)
        print("✓ SPOTIFY_SCOPES updated")
    else:
        print("✗ old_scopes not found")
        sys.exit(1)

    # 2. Update switchAppView to handle 'playlist' mode
    old_switch_app_view = """    function switchAppView(mode) {
      currentAppView = mode;
      const quickSec = document.getElementById('spotifyQuickBannersSection');
      const filterBarEl = document.getElementById('spotifyHomeFilterBar');
      const djHeroSec = document.getElementById('djEddieHeroSection');
      const homeShelvesSec = document.getElementById('spotifyHomeShelves');
      const djPlaylistSec = document.getElementById('djEddiePlaylistSection');
      const bandTopNav = document.getElementById('bandViewTopNav');
      const heroBannerEl = document.getElementById('heroBanner');
      const actionBarEl = document.querySelector('.action-bar');
      const tableSecEl = document.querySelector('.table-section');
      const lyricsSecEl = document.getElementById('lyricsSection');
      const aboutSecEl = document.querySelector('.spotify-about-section');
      const discoSecEl = document.querySelector('.spotify-discography-section');
      const membersSecEl = document.querySelector('.spotify-members-section');

      if (mode === 'home') {
        if (filterBarEl) filterBarEl.style.display = 'flex';
        if (quickSec) quickSec.style.display = '';
        if (djHeroSec) djHeroSec.style.display = '';
        if (homeShelvesSec) homeShelvesSec.style.display = '';
        if (djPlaylistSec) djPlaylistSec.style.display = 'none';
        if (bandTopNav) bandTopNav.style.display = 'none';
        if (heroBannerEl) heroBannerEl.style.display = 'none';
        if (actionBarEl) actionBarEl.style.display = 'none';
        if (tableSecEl) tableSecEl.style.display = 'none';
        if (lyricsSecEl) lyricsSecEl.style.display = 'none';
        if (aboutSecEl) aboutSecEl.style.display = 'none';
        if (discoSecEl) discoSecEl.style.display = 'none';
        if (membersSecEl) membersSecEl.style.display = 'none';
      } else if (mode === 'djeddie') {
        if (filterBarEl) filterBarEl.style.display = 'none';
        if (quickSec) quickSec.style.display = 'none';
        if (djHeroSec) djHeroSec.style.display = 'none';
        if (homeShelvesSec) homeShelvesSec.style.display = 'none';
        if (djPlaylistSec) djPlaylistSec.style.display = 'block';
        if (bandTopNav) bandTopNav.style.display = 'none';
        if (heroBannerEl) heroBannerEl.style.display = 'none';
        if (actionBarEl) actionBarEl.style.display = 'none';
        if (tableSecEl) tableSecEl.style.display = 'none';
        if (lyricsSecEl) lyricsSecEl.style.display = '';
        if (aboutSecEl) aboutSecEl.style.display = 'none';
        if (discoSecEl) discoSecEl.style.display = 'none';
        if (membersSecEl) membersSecEl.style.display = 'none';
        renderDjEddiePlaylistSongs();
      } else if (mode === 'band') {
        if (filterBarEl) filterBarEl.style.display = 'none';
        if (quickSec) quickSec.style.display = 'none';
        if (djHeroSec) djHeroSec.style.display = 'none';
        if (homeShelvesSec) homeShelvesSec.style.display = 'none';
        if (djPlaylistSec) djPlaylistSec.style.display = 'none';
        if (bandTopNav) bandTopNav.style.display = 'flex';
        if (heroBannerEl) heroBannerEl.style.display = '';
        if (actionBarEl) actionBarEl.style.display = '';
        if (tableSecEl) tableSecEl.style.display = '';
        if (lyricsSecEl) lyricsSecEl.style.display = '';
        if (aboutSecEl) aboutSecEl.style.display = '';
        if (discoSecEl) discoSecEl.style.display = '';
        if (membersSecEl) membersSecEl.style.display = '';
      }

      renderSidebarPlaylists();
      renderQuickBanners();
      const mainStage = document.getElementById('spotifyMain');
      if (mainStage && typeof mainStage.scrollTo === 'function') {
        mainStage.scrollTo({ top: 0, behavior: 'smooth' });
      }
      if (typeof window.scrollTo === 'function') {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }"""

    new_switch_app_view = """    let activeInspectedPlaylistId = null;

    function switchAppView(mode) {
      currentAppView = mode;
      const quickSec = document.getElementById('spotifyQuickBannersSection');
      const filterBarEl = document.getElementById('spotifyHomeFilterBar');
      const djHeroSec = document.getElementById('djEddieHeroSection');
      const homeShelvesSec = document.getElementById('spotifyHomeShelves');
      const djPlaylistSec = document.getElementById('djEddiePlaylistSection');
      const spPlaylistSec = document.getElementById('spotifyPlaylistSection');
      const bandTopNav = document.getElementById('bandViewTopNav');
      const heroBannerEl = document.getElementById('heroBanner');
      const actionBarEl = document.querySelector('.action-bar');
      const tableSecEl = document.querySelector('.table-section');
      const lyricsSecEl = document.getElementById('lyricsSection');
      const aboutSecEl = document.querySelector('.spotify-about-section');
      const discoSecEl = document.querySelector('.spotify-discography-section');
      const membersSecEl = document.querySelector('.spotify-members-section');

      if (mode === 'home') {
        if (filterBarEl) filterBarEl.style.display = 'none';
        if (quickSec) quickSec.style.display = '';
        if (djHeroSec) djHeroSec.style.display = '';
        if (homeShelvesSec) homeShelvesSec.style.display = '';
        if (djPlaylistSec) djPlaylistSec.style.display = 'none';
        if (spPlaylistSec) spPlaylistSec.style.display = 'none';
        if (bandTopNav) bandTopNav.style.display = 'none';
        if (heroBannerEl) heroBannerEl.style.display = 'none';
        if (actionBarEl) actionBarEl.style.display = 'none';
        if (tableSecEl) tableSecEl.style.display = 'none';
        if (lyricsSecEl) lyricsSecEl.style.display = 'none';
        if (aboutSecEl) aboutSecEl.style.display = 'none';
        if (discoSecEl) discoSecEl.style.display = 'none';
        if (membersSecEl) membersSecEl.style.display = 'none';
      } else if (mode === 'djeddie') {
        if (filterBarEl) filterBarEl.style.display = 'none';
        if (quickSec) quickSec.style.display = 'none';
        if (djHeroSec) djHeroSec.style.display = 'none';
        if (homeShelvesSec) homeShelvesSec.style.display = 'none';
        if (djPlaylistSec) djPlaylistSec.style.display = 'block';
        if (spPlaylistSec) spPlaylistSec.style.display = 'none';
        if (bandTopNav) bandTopNav.style.display = 'none';
        if (heroBannerEl) heroBannerEl.style.display = 'none';
        if (actionBarEl) actionBarEl.style.display = 'none';
        if (tableSecEl) tableSecEl.style.display = 'none';
        if (lyricsSecEl) lyricsSecEl.style.display = '';
        if (aboutSecEl) aboutSecEl.style.display = 'none';
        if (discoSecEl) discoSecEl.style.display = 'none';
        if (membersSecEl) membersSecEl.style.display = 'none';
        renderDjEddiePlaylistSongs();
      } else if (mode === 'playlist') {
        if (filterBarEl) filterBarEl.style.display = 'none';
        if (quickSec) quickSec.style.display = 'none';
        if (djHeroSec) djHeroSec.style.display = 'none';
        if (homeShelvesSec) homeShelvesSec.style.display = 'none';
        if (djPlaylistSec) djPlaylistSec.style.display = 'none';
        if (spPlaylistSec) spPlaylistSec.style.display = 'block';
        if (bandTopNav) bandTopNav.style.display = 'none';
        if (heroBannerEl) heroBannerEl.style.display = 'none';
        if (actionBarEl) actionBarEl.style.display = 'none';
        if (tableSecEl) tableSecEl.style.display = 'none';
        if (lyricsSecEl) lyricsSecEl.style.display = 'none';
        if (aboutSecEl) aboutSecEl.style.display = 'none';
        if (discoSecEl) discoSecEl.style.display = 'none';
        if (membersSecEl) membersSecEl.style.display = 'none';
      } else if (mode === 'band') {
        if (filterBarEl) filterBarEl.style.display = 'none';
        if (quickSec) quickSec.style.display = 'none';
        if (djHeroSec) djHeroSec.style.display = 'none';
        if (homeShelvesSec) homeShelvesSec.style.display = 'none';
        if (djPlaylistSec) djPlaylistSec.style.display = 'none';
        if (spPlaylistSec) spPlaylistSec.style.display = 'none';
        if (bandTopNav) bandTopNav.style.display = 'flex';
        if (heroBannerEl) heroBannerEl.style.display = '';
        if (actionBarEl) actionBarEl.style.display = '';
        if (tableSecEl) tableSecEl.style.display = '';
        if (lyricsSecEl) lyricsSecEl.style.display = '';
        if (aboutSecEl) aboutSecEl.style.display = '';
        if (discoSecEl) discoSecEl.style.display = '';
        if (membersSecEl) membersSecEl.style.display = '';
      }

      renderSidebarPlaylists();
      renderQuickBanners();
      const mainStage = document.getElementById('spotifyMain');
      if (mainStage && typeof mainStage.scrollTo === 'function') {
        mainStage.scrollTo({ top: 0, behavior: 'smooth' });
      }
      if (typeof window.scrollTo === 'function') {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }"""

    if old_switch_app_view in content:
        content = content.replace(old_switch_app_view, new_switch_app_view, 1)
        print("✓ switchAppView updated")
    else:
        print("✗ old_switch_app_view not found")
        sys.exit(1)

    # 3. Replace renderSidebarPlaylists and renderSpotifyHomeShelves with full-featured implementations
    old_sidebar_render = """    function renderSidebarPlaylists() {
      sidebarPlaylists.innerHTML = '';

      const count = djEddieQueue.length ? djEddieQueue.length : 11;
      // Item #1 pinned: DJ Fredd • Radio IA
      const djItem = document.createElement('div');
      djItem.className = 'playlist-item' + (currentAppView === 'djeddie' ? ' active' : '');
      djItem.innerHTML = `
        <div class="playlist-icon" style="background: radial-gradient(circle, #10b981 0%, #1e3a8a 100%); display:flex; align-items:center; justify-content:center; font-size:1.3rem; border: 1px solid rgba(52,211,153,0.45);">
          <span>🎙️</span>
        </div>
        <div class="playlist-info">
          <div class="playlist-name" style="color:#6ee7b7;">DJ Fredd • Radio IA</div>
          <div class="playlist-sub">Playlist IA • ${count} canciones</div>
        </div>
      `;
      djItem.addEventListener('click', () => {
        openDjEddiePlaylistView();
      });
      sidebarPlaylists.appendChild(djItem);

      Object.values(bands).forEach(b => {
        const item = document.createElement('div');
        item.className = 'playlist-item' + (currentAppView === 'band' && b.id === activeBandId ? ' active' : '');
        item.innerHTML = `
          <div class="playlist-icon" style="background: #000; padding: 3px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08);">
            <img src="${b.cover}" alt="${b.name}" style="width: 100%; height: 100%; object-fit: contain; background: #000;">
          </div>
          <div class="playlist-info">
            <div class="playlist-name">${b.name}</div>
            <div class="playlist-sub">Cápsula 45s • ${b.genreLabel}</div>
          </div>
        `;
        item.addEventListener('click', () => {
          openBandView(b.id, true, '45s');
        });
        sidebarPlaylists.appendChild(item);
      });
    }"""

    new_sidebar_render = """    async function renderSidebarPlaylists() {
      if (!sidebarPlaylists) return;
      sidebarPlaylists.innerHTML = '';

      const count = djEddieQueue.length ? djEddieQueue.length : 11;
      // Item #1 pinned: DJ Fredd • Radio IA
      const djItem = document.createElement('div');
      djItem.className = 'playlist-item' + (currentAppView === 'djeddie' ? ' active' : '');
      djItem.innerHTML = `
        <div class="playlist-icon" style="background: radial-gradient(circle, #10b981 0%, #1e3a8a 100%); display:flex; align-items:center; justify-content:center; font-size:1.3rem; border: 1px solid rgba(52,211,153,0.45);">
          <span>🎙️</span>
        </div>
        <div class="playlist-info">
          <div class="playlist-name" style="color:#6ee7b7;">DJ Fredd • Radio IA</div>
          <div class="playlist-sub">Playlist IA • ${count} canciones</div>
        </div>
      `;
      djItem.addEventListener('click', () => {
        openDjEddiePlaylistView();
      });
      sidebarPlaylists.appendChild(djItem);

      // Item #2: Liked Songs (Purple Heart Card in Sidebar)
      const token = await getValidSpotifyToken();
      if (token) {
        const likedItem = document.createElement('div');
        likedItem.className = 'playlist-item' + (currentAppView === 'playlist' && activeInspectedPlaylistId === 'liked_songs' ? ' active' : '');
        likedItem.innerHTML = `
          <div class="playlist-icon" style="background: linear-gradient(135deg, #450af5 0%, #8e8ee5 100%); display:flex; align-items:center; justify-content:center;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="#ffffff"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
          </div>
          <div class="playlist-info">
            <div class="playlist-name" style="color:#ffffff;">Canciones que te gustan</div>
            <div class="playlist-sub">Playlist • Guardadas</div>
          </div>
        `;
        likedItem.addEventListener('click', () => {
          openSpotifyLikedSongsView();
        });
        sidebarPlaylists.appendChild(likedItem);

        // User Playlists from Spotify
        try {
          const userPlaylists = await fetchSpotifyUserPlaylists(token);
          userPlaylists.slice(0, 15).forEach(pl => {
            const plImg = (pl.images && pl.images.length > 0 && pl.images[0].url) ? pl.images[0].url : 'img/covers/cover_queen.png';
            const pItem = document.createElement('div');
            pItem.className = 'playlist-item' + (currentAppView === 'playlist' && activeInspectedPlaylistId === pl.id ? ' active' : '');
            pItem.innerHTML = `
              <div class="playlist-icon" style="background:#000; overflow:hidden;">
                <img src="${plImg}" alt="${escapeHtmlStr(pl.name)}" style="width:100%;height:100%;object-fit:cover;">
              </div>
              <div class="playlist-info">
                <div class="playlist-name">${escapeHtmlStr(pl.name)}</div>
                <div class="playlist-sub">Playlist • ${pl.tracks ? pl.tracks.total : 0} temas</div>
              </div>
            `;
            pItem.addEventListener('click', () => {
              openSpotifyPlaylistView(pl);
            });
            sidebarPlaylists.appendChild(pItem);
          });
        } catch (e) {}
      }

      // Classic Bands
      Object.values(bands).forEach(b => {
        const item = document.createElement('div');
        item.className = 'playlist-item' + (currentAppView === 'band' && b.id === activeBandId ? ' active' : '');
        item.innerHTML = `
          <div class="playlist-icon" style="background: #000; padding: 3px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08);">
            <img src="${b.cover}" alt="${b.name}" style="width: 100%; height: 100%; object-fit: contain; background: #000;">
          </div>
          <div class="playlist-info">
            <div class="playlist-name">${b.name}</div>
            <div class="playlist-sub">Cápsula 45s • ${b.genreLabel}</div>
          </div>
        `;
        item.addEventListener('click', () => {
          openBandView(b.id, true, '45s');
        });
        sidebarPlaylists.appendChild(item);
      });
    }"""

    if old_sidebar_render in content:
        content = content.replace(old_sidebar_render, new_sidebar_render, 1)
        print("✓ renderSidebarPlaylists updated")
    else:
        print("✗ old_sidebar_render not found")
        sys.exit(1)

    # 4. Replace renderSpotifyHomeShelves and add API fetchers + inspector logic
    old_home_shelves_render_re = re.compile(r'    function renderSpotifyHomeShelves\(\) \{.*?function applyHomeCategoryFilter\(cat\) \{', re.DOTALL)
    if not old_home_shelves_render_re.search(content):
        print("✗ old_home_shelves_render_re not found")
        sys.exit(1)

    new_home_shelves_render = """    // ========================================================
    // SPOTIFY WEB API DATA FETCHERS & CACHE (PLAYLISTS, TOP, LIKED, RECS)
    // ========================================================
    async function fetchSpotifyUserPlaylists(token) {
      if (!token) return [];
      try {
        const cached = sessionStorage.getItem('sp_cache_playlists');
        if (cached) return JSON.parse(cached);
        const res = await fetch('https://api.spotify.com/v1/me/playlists?limit=50', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) return [];
        const data = await res.json();
        const items = data.items || [];
        sessionStorage.setItem('sp_cache_playlists', JSON.stringify(items));
        return items;
      } catch (e) {
        console.warn('fetchSpotifyUserPlaylists error:', e);
        return [];
      }
    }

    async function fetchSpotifyLikedSongs(token, limit = 20) {
      if (!token) return { items: [], total: 0 };
      try {
        const cached = sessionStorage.getItem('sp_cache_liked_songs');
        if (cached) return JSON.parse(cached);
        const res = await fetch(`https://api.spotify.com/v1/me/tracks?limit=${limit}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) return { items: [], total: 0 };
        const data = await res.json();
        sessionStorage.setItem('sp_cache_liked_songs', JSON.stringify(data));
        return data;
      } catch (e) {
        console.warn('fetchSpotifyLikedSongs error:', e);
        return { items: [], total: 0 };
      }
    }

    async function fetchSpotifyTopTracks(token, limit = 20) {
      if (!token) return [];
      try {
        const cached = sessionStorage.getItem('sp_cache_top_tracks');
        if (cached) return JSON.parse(cached);
        const res = await fetch(`https://api.spotify.com/v1/me/top/tracks?limit=${limit}&time_range=medium_term`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) return [];
        const data = await res.json();
        const items = data.items || [];
        sessionStorage.setItem('sp_cache_top_tracks', JSON.stringify(items));
        return items;
      } catch (e) {
        console.warn('fetchSpotifyTopTracks error:', e);
        return [];
      }
    }

    async function fetchSpotifyTopArtists(token, limit = 20) {
      if (!token) return [];
      try {
        const cached = sessionStorage.getItem('sp_cache_top_artists');
        if (cached) return JSON.parse(cached);
        const res = await fetch(`https://api.spotify.com/v1/me/top/artists?limit=${limit}&time_range=medium_term`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) return [];
        const data = await res.json();
        const items = data.items || [];
        sessionStorage.setItem('sp_cache_top_artists', JSON.stringify(items));
        return items;
      } catch (e) {
        console.warn('fetchSpotifyTopArtists error:', e);
        return [];
      }
    }

    async function fetchSpotifyRecentlyPlayed(token, limit = 20) {
      if (!token) return [];
      try {
        const cached = sessionStorage.getItem('sp_cache_recently_played');
        if (cached) return JSON.parse(cached);
        const res = await fetch(`https://api.spotify.com/v1/me/player/recently-played?limit=${limit}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) return [];
        const data = await res.json();
        const items = (data.items || []).map(x => x.track).filter(Boolean);
        sessionStorage.setItem('sp_cache_recently_played', JSON.stringify(items));
        return items;
      } catch (e) {
        console.warn('fetchSpotifyRecentlyPlayed error:', e);
        return [];
      }
    }

    async function fetchSpotifyRecommendations(token, seedGenres = 'rock,classic-rock,hard-rock') {
      if (!token) return [];
      try {
        const cached = sessionStorage.getItem('sp_cache_recommendations');
        if (cached) return JSON.parse(cached);
        const res = await fetch(`https://api.spotify.com/v1/recommendations?limit=20&seed_genres=${encodeURIComponent(seedGenres)}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) return [];
        const data = await res.json();
        const items = data.tracks || [];
        sessionStorage.setItem('sp_cache_recommendations', JSON.stringify(items));
        return items;
      } catch (e) {
        console.warn('fetchSpotifyRecommendations error:', e);
        return [];
      }
    }

    async function fetchSpotifyCurrentPlayback(token) {
      if (!token) return null;
      try {
        const res = await fetch('https://api.spotify.com/v1/me/player', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.status === 204 || !res.ok) return null;
        return await res.json();
      } catch (e) {
        return null;
      }
    }

    // Curated Fallback Collections for Rock
    const CURATED_ROCK_PLAYLISTS = [
      {
        id: 'curated_rock_classics',
        name: 'Rock Clásicos 70s y 80s',
        description: 'Los himnos inmortales de Queen, Led Zeppelin, The Beatles, Pink Floyd y las mayores leyendas.',
        images: [{ url: 'img/covers/cover_queen.png' }],
        owner: { display_name: 'Rock Radio' },
        tracks: { total: 8 },
        items: [
          { id: 'sp_cur_1', name: 'Bohemian Rhapsody', artists: [{ name: 'Queen' }], album: { name: 'A Night at the Opera (1975)', release_date: '1975', images: [{ url: 'img/covers/cover_queen.png' }] }, duration_ms: 354000 },
          { id: 'sp_cur_2', name: 'Stairway to Heaven', artists: [{ name: 'Led Zeppelin' }], album: { name: 'Led Zeppelin IV (1971)', release_date: '1971', images: [{ url: 'img/covers/cover_led_zeppelin.png' }] }, duration_ms: 482000 },
          { id: 'sp_cur_3', name: 'Back in Black', artists: [{ name: 'AC/DC' }], album: { name: 'Back in Black (1980)', release_date: '1980', images: [{ url: 'img/covers/cover_acdc.png' }] }, duration_ms: 255000 },
          { id: 'sp_cur_4', name: 'Help!', artists: [{ name: 'The Beatles' }], album: { name: 'Help! (1965)', release_date: '1965', images: [{ url: 'img/covers/cover_queen.png' }] }, duration_ms: 139000 },
          { id: 'sp_cur_5', name: 'Enter Sandman', artists: [{ name: 'Metallica' }], album: { name: 'Metallica (1991)', release_date: '1991', images: [{ url: 'img/covers/cover_metallica.png' }] }, duration_ms: 331000 },
          { id: 'sp_cur_6', name: "Sweet Child O' Mine", artists: [{ name: "Guns N' Roses" }], album: { name: 'Appetite for Destruction (1987)', release_date: '1987', images: [{ url: 'img/covers/cover_guns_n_roses.png' }] }, duration_ms: 356000 },
          { id: 'sp_cur_7', name: 'Paranoid', artists: [{ name: 'Black Sabbath' }], album: { name: 'Paranoid (1970)', release_date: '1970', images: [{ url: 'img/covers/cover_black_sabbath.png' }] }, duration_ms: 168000 },
          { id: 'sp_cur_8', name: 'Rock and Roll All Nite', artists: [{ name: 'KISS' }], album: { name: 'Dressed to Kill (1975)', release_date: '1975', images: [{ url: 'img/covers/cover_kiss.png' }] }, duration_ms: 169000 }
        ]
      },
      {
        id: 'curated_hard_rock_stadiums',
        name: 'Hard Rock Stadiums',
        description: 'Riffs demoledores y coros para cantar con el volumen de la radio al 100%.',
        images: [{ url: 'img/covers/cover_acdc.png' }],
        owner: { display_name: 'Rock Radio' },
        tracks: { total: 6 },
        items: [
          { id: 'sp_hr_1', name: 'Highway to Hell', artists: [{ name: 'AC/DC' }], album: { name: 'Highway to Hell', release_date: '1979', images: [{ url: 'img/covers/cover_acdc.png' }] }, duration_ms: 208000 },
          { id: 'sp_hr_2', name: 'Paradise City', artists: [{ name: "Guns N' Roses" }], album: { name: 'Appetite for Destruction', release_date: '1987', images: [{ url: 'img/covers/cover_guns_n_roses.png' }] }, duration_ms: 406000 },
          { id: 'sp_hr_3', name: 'Detroit Rock City', artists: [{ name: 'KISS' }], album: { name: 'Destroyer', release_date: '1976', images: [{ url: 'img/covers/cover_kiss.png' }] }, duration_ms: 317000 },
          { id: 'sp_hr_4', name: 'Pour Some Sugar on Me', artists: [{ name: 'Def Leppard' }], album: { name: 'Hysteria', release_date: '1987', images: [{ url: 'img/covers/cover_def_leppard.png' }] }, duration_ms: 267000 },
          { id: 'sp_hr_5', name: 'Kickstart My Heart', artists: [{ name: 'Mötley Crüe' }], album: { name: 'Dr. Feelgood', release_date: '1989', images: [{ url: 'img/covers/cover_motley_crue.png' }] }, duration_ms: 284000 },
          { id: 'sp_hr_6', name: 'Tom Sawyer', artists: [{ name: 'Rush' }], album: { name: 'Moving Pictures', release_date: '1981', images: [{ url: 'img/covers/cover_rush.png' }] }, duration_ms: 276000 }
        ]
      },
      {
        id: 'curated_heavy_metal_anthems',
        name: 'Heavy Metal Anthems',
        description: 'La forja del metal: guitarras afinadas en oscuridad y distorsión pura.',
        images: [{ url: 'img/covers/cover_metallica.png' }],
        owner: { display_name: 'Rock Radio' },
        tracks: { total: 5 },
        items: [
          { id: 'sp_hm_1', name: 'Master of Puppets', artists: [{ name: 'Metallica' }], album: { name: 'Master of Puppets', release_date: '1986', images: [{ url: 'img/covers/cover_metallica.png' }] }, duration_ms: 515000 },
          { id: 'sp_hm_2', name: 'Iron Man', artists: [{ name: 'Black Sabbath' }], album: { name: 'Paranoid', release_date: '1970', images: [{ url: 'img/covers/cover_black_sabbath.png' }] }, duration_ms: 356000 },
          { id: 'sp_hm_3', name: 'One', artists: [{ name: 'Metallica' }], album: { name: '...And Justice for All', release_date: '1988', images: [{ url: 'img/covers/cover_metallica.png' }] }, duration_ms: 446000 },
          { id: 'sp_hm_4', name: 'War Pigs', artists: [{ name: 'Black Sabbath' }], album: { name: 'Paranoid', release_date: '1970', images: [{ url: 'img/covers/cover_black_sabbath.png' }] }, duration_ms: 474000 },
          { id: 'sp_hm_5', name: 'Kashmir', artists: [{ name: 'Led Zeppelin' }], album: { name: 'Physical Graffiti', release_date: '1975', images: [{ url: 'img/covers/cover_led_zeppelin.png' }] }, duration_ms: 512000 }
        ]
      },
      {
        id: 'curated_rock_ballads',
        name: 'Baladas Inmortales del Rock',
        description: 'Sensibilidad, solos desgarradores y letras que marcaron épocas.',
        images: [{ url: 'img/covers/cover_kiss.png' }],
        owner: { display_name: 'Rock Radio' },
        tracks: { total: 5 },
        items: [
          { id: 'sp_rb_1', name: 'Forever', artists: [{ name: 'KISS' }], album: { name: 'Hot in the Shade', release_date: '1989', images: [{ url: 'img/covers/cover_kiss.png' }] }, duration_ms: 233000 },
          { id: 'sp_rb_2', name: 'November Rain', artists: [{ name: "Guns N' Roses" }], album: { name: 'Use Your Illusion I', release_date: '1991', images: [{ url: 'img/covers/cover_guns_n_roses.png' }] }, duration_ms: 537000 },
          { id: 'sp_rb_3', name: 'Africa', artists: [{ name: 'Toto' }], album: { name: 'Toto IV', release_date: '1982', images: [{ url: 'img/covers/cover_toto.png' }] }, duration_ms: 295000 },
          { id: 'sp_rb_4', name: 'Forever Young', artists: [{ name: 'Alphaville' }], album: { name: 'Forever Young', release_date: '1984', images: [{ url: 'img/covers/cover_alphaville.png' }] }, duration_ms: 226000 },
          { id: 'sp_rb_5', name: 'Love Bites', artists: [{ name: 'Def Leppard' }], album: { name: 'Hysteria', release_date: '1987', images: [{ url: 'img/covers/cover_def_leppard.png' }] }, duration_ms: 346000 }
        ]
      }
    ];

    const CURATED_ROCK_TRACKS = [
      { id: 'cur_trk_1', name: 'Stairway to Heaven', artists: [{ name: 'Led Zeppelin' }], album: { name: 'Led Zeppelin IV', release_date: '1971', images: [{ url: 'img/covers/cover_led_zeppelin.png' }] }, duration_ms: 482000 },
      { id: 'cur_trk_2', name: 'Bohemian Rhapsody', artists: [{ name: 'Queen' }], album: { name: 'A Night at the Opera', release_date: '1975', images: [{ url: 'img/covers/cover_queen.png' }] }, duration_ms: 354000 },
      { id: 'cur_trk_3', name: 'Back in Black', artists: [{ name: 'AC/DC' }], album: { name: 'Back in Black', release_date: '1980', images: [{ url: 'img/covers/cover_acdc.png' }] }, duration_ms: 255000 },
      { id: 'cur_trk_4', name: 'Help!', artists: [{ name: 'The Beatles' }], album: { name: 'Help!', release_date: '1965', images: [{ url: 'img/covers/cover_queen.png' }] }, duration_ms: 139000 },
      { id: 'cur_trk_5', name: 'Enter Sandman', artists: [{ name: 'Metallica' }], album: { name: 'Metallica (The Black Album)', release_date: '1991', images: [{ url: 'img/covers/cover_metallica.png' }] }, duration_ms: 331000 },
      { id: 'cur_trk_6', name: "Sweet Child O' Mine", artists: [{ name: "Guns N' Roses" }], album: { name: 'Appetite for Destruction', release_date: '1987', images: [{ url: 'img/covers/cover_guns_n_roses.png' }] }, duration_ms: 356000 },
      { id: 'cur_trk_7', name: 'Paranoid', artists: [{ name: 'Black Sabbath' }], album: { name: 'Paranoid', release_date: '1970', images: [{ url: 'img/covers/cover_black_sabbath.png' }] }, duration_ms: 168000 },
      { id: 'cur_trk_8', name: 'Rock and Roll All Nite', artists: [{ name: 'KISS' }], album: { name: 'Dressed to Kill', release_date: '1975', images: [{ url: 'img/covers/cover_kiss.png' }] }, duration_ms: 169000 }
    ];

    // Card UI Builders
    function createSpotifyHomeTrackCard(track, queue = [], index = 0) {
      const imgUrl = (track.album && track.album.images && track.album.images.length > 0 && track.album.images[0].url)
        ? track.album.images[0].url
        : 'img/covers/cover_kiss.png';
      const artists = (track.artists || []).map(a => a.name).join(', ') || 'Rock';
      const durSec = Math.floor((track.duration_ms || 180000) / 1000);

      const card = document.createElement('div');
      card.className = 'home-sp-card';
      card.innerHTML = `
        <div class="home-sp-card-art">
          <img src="${imgUrl}" alt="${escapeHtmlStr(track.name)}" loading="lazy">
          <span class="home-sp-card-dur">${formatTime(durSec)}</span>
          <button class="home-sp-card-play" type="button" title="Reproducir ${escapeHtmlStr(track.name)}">
            <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
          </button>
        </div>
        <div class="home-sp-card-title" title="${escapeHtmlStr(track.name)}">${escapeHtmlStr(track.name)}</div>
        <div class="home-sp-card-sub" title="${escapeHtmlStr(artists)}">${escapeHtmlStr(artists)}</div>
      `;

      const playBtn = card.querySelector('.home-sp-card-play');
      if (playBtn) {
        playBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          playSpotifyTrack(track, card, queue, index);
        });
      }

      const addBtn = document.createElement('button');
      addBtn.className = 'home-card-add-dj';
      addBtn.type = 'button';
      addBtn.innerHTML = '<span>🎙️ + Añadir a DJ Fredd</span>';
      addBtn.title = `Añadir "${track.name}" a DJ Fredd para narrar su historia`;
      addBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        addSpotifyTrackToDjEddie(track);
      });
      card.appendChild(addBtn);

      card.addEventListener('click', () => {
        playSpotifyTrack(track, card, queue, index);
      });
      return card;
    }

    function createSpotifyHomePlaylistCard(playlist) {
      const imgUrl = (playlist.images && playlist.images.length > 0 && playlist.images[0].url)
        ? playlist.images[0].url
        : 'img/covers/cover_queen.png';
      const owner = (playlist.owner && playlist.owner.display_name) ? playlist.owner.display_name : 'Spotify';
      const trackCount = (playlist.tracks && playlist.tracks.total !== undefined) ? `${playlist.tracks.total} canciones` : 'Playlist';

      const card = document.createElement('div');
      card.className = 'home-sp-card';
      card.innerHTML = `
        <div class="home-sp-card-art">
          <img src="${imgUrl}" alt="${escapeHtmlStr(playlist.name)}" loading="lazy">
          <span class="home-sp-card-badge">PLAYLIST</span>
          <button class="home-sp-card-play" type="button" title="Abrir playlist ${escapeHtmlStr(playlist.name)}">
            <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
          </button>
        </div>
        <div class="home-sp-card-title" title="${escapeHtmlStr(playlist.name)}">${escapeHtmlStr(playlist.name)}</div>
        <div class="home-sp-card-sub">De ${escapeHtmlStr(owner)} • ${trackCount}</div>
      `;

      card.addEventListener('click', () => {
        openSpotifyPlaylistView(playlist);
      });
      return card;
    }

    function createSpotifyLikedSongsCard(total = 0) {
      const card = document.createElement('div');
      card.className = 'home-sp-card';
      card.style.background = 'linear-gradient(145deg, #181818 0%, #20183b 100%)';
      card.innerHTML = `
        <div class="sp-liked-card-art">
          <svg viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
          <button class="home-sp-card-play" type="button" title="Abrir Canciones que te gustan">
            <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
          </button>
        </div>
        <div class="home-sp-card-title" style="color:#ffffff;">Canciones que te gustan</div>
        <div class="home-sp-card-sub">${total > 0 ? `${total} canciones guardadas` : 'Tus temas favoritos en Spotify'}</div>
      `;
      card.addEventListener('click', () => {
        openSpotifyLikedSongsView();
      });
      return card;
    }

    // ========================================================
    // SPOTIFY PLAYLIST & LIKED SONGS INSPECTOR VIEW
    // ========================================================
    async function openSpotifyPlaylistView(playlist) {
      if (!playlist) return;
      activeInspectedPlaylistId = playlist.id;

      const titleEl = document.getElementById('spPlaylistMainTitle');
      const descEl = document.getElementById('spPlaylistMainDesc');
      const ownerEl = document.getElementById('spPlaylistOwner');
      const countEl = document.getElementById('spPlaylistTrackCount');
      const durEl = document.getElementById('spPlaylistDuration');
      const coverWrap = document.getElementById('spPlaylistCoverWrap');
      const bodyEl = document.getElementById('spPlaylistTableBody');
      const playAllBtn = document.getElementById('btnSpPlaylistPlayAll');
      const addAllBtn = document.getElementById('btnSpPlaylistAddAllToDj');
      const badgeEl = document.getElementById('spPlaylistTypeBadge');

      if (titleEl) titleEl.textContent = playlist.name || 'Playlist de Spotify';
      if (descEl) descEl.textContent = playlist.description || 'Playlist sincronizada con Spotify Web API.';
      const owner = (playlist.owner && playlist.owner.display_name) ? playlist.owner.display_name : 'Spotify';
      if (ownerEl) ownerEl.textContent = `De ${owner}`;
      if (badgeEl) badgeEl.textContent = 'PLAYLIST SPOTIFY';

      const imgUrl = (playlist.images && playlist.images.length > 0 && playlist.images[0].url)
        ? playlist.images[0].url
        : 'img/covers/cover_queen.png';
      if (coverWrap) {
        coverWrap.className = 'sp-inspected-cover-wrap';
        coverWrap.innerHTML = `<img src="${imgUrl}" alt="${escapeHtmlStr(playlist.name)}">`;
      }

      switchAppView('playlist');
      if (bodyEl) bodyEl.innerHTML = '<div style="padding:20px; color:#b3b3b3;">Cargando canciones de la playlist...</div>';

      let tracks = [];
      if (playlist.items && playlist.items.length) {
        tracks = playlist.items;
      } else {
        const token = await getValidSpotifyToken();
        if (token && playlist.id) {
          try {
            const res = await fetch(`https://api.spotify.com/v1/playlists/${playlist.id}/tracks?limit=50`, {
              headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
              const data = await res.json();
              tracks = (data.items || []).map(x => x && x.track).filter(Boolean);
            }
          } catch (e) {
            console.warn('Error fetching playlist tracks:', e);
          }
        }
      }

      if (!tracks.length) {
        tracks = CURATED_ROCK_TRACKS;
      }

      if (countEl) countEl.textContent = `${tracks.length} canciones`;
      const totalMs = tracks.reduce((acc, t) => acc + (t.duration_ms || 180000), 0);
      const totalMin = Math.round(totalMs / 60000);
      if (durEl) durEl.textContent = `Aprox. ${totalMin} min`;

      if (bodyEl) {
        bodyEl.innerHTML = '';
        tracks.forEach((t, idx) => {
          const row = document.createElement('div');
          row.className = 'dj-song-row';
          row.style.gridTemplateColumns = '36px 3fr 2fr 1fr 140px';
          row.style.alignItems = 'center';
          const tImg = (t.album && t.album.images && t.album.images.length > 0 && t.album.images[0].url) ? t.album.images[0].url : 'img/covers/cover_kiss.png';
          const tArtists = (t.artists || []).map(a => a.name).join(', ') || 'Rock';
          const durSec = Math.floor((t.duration_ms || 180000) / 1000);
          const albumName = (t.album && t.album.name) ? t.album.name : 'Álbum Oficial';

          row.innerHTML = `
            <div class="dj-col-num">${idx + 1}</div>
            <div class="sp-table-track-cell">
              <img src="${tImg}" alt="${escapeHtmlStr(t.name)}" class="sp-table-track-thumb">
              <div class="sp-table-track-info">
                <span class="sp-table-track-title">${escapeHtmlStr(t.name)}</span>
                <span class="sp-table-track-artists">${escapeHtmlStr(tArtists)}</span>
              </div>
            </div>
            <div style="font-size:0.8rem; color:#b3b3b3; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${escapeHtmlStr(albumName)}</div>
            <div class="dj-col-year" style="font-size:0.8rem; color:#b3b3b3;">${formatTime(durSec)}</div>
            <div style="text-align:right;">
              <button class="home-card-add-dj sp-row-add-btn" type="button" style="margin:0; width:auto; padding:4px 10px;">+ DJ Fredd</button>
            </div>
          `;

          const rowAddBtn = row.querySelector('.sp-row-add-btn');
          if (rowAddBtn) {
            rowAddBtn.addEventListener('click', (e) => {
              e.stopPropagation();
              addSpotifyTrackToDjEddie(t);
            });
          }

          row.addEventListener('click', () => {
            playSpotifyTrack(t, row, tracks, idx);
          });
          bodyEl.appendChild(row);
        });
      }

      if (playAllBtn) {
        playAllBtn.onclick = () => {
          if (tracks.length > 0) {
            const firstRow = bodyEl.querySelector('.dj-song-row');
            playSpotifyTrack(tracks[0], firstRow, tracks, 0);
          }
        };
      }

      if (addAllBtn) {
        addAllBtn.onclick = () => {
          let countAdded = 0;
          tracks.forEach(tr => {
            addSpotifyTrackToDjEddie(tr);
            countAdded++;
          });
          showAppToast(`✓ ${countAdded} canciones añadidas a DJ Fredd para narrar sus historias`, 'success');
        };
      }
    }

    async function openSpotifyLikedSongsView() {
      activeInspectedPlaylistId = 'liked_songs';

      const titleEl = document.getElementById('spPlaylistMainTitle');
      const descEl = document.getElementById('spPlaylistMainDesc');
      const ownerEl = document.getElementById('spPlaylistOwner');
      const countEl = document.getElementById('spPlaylistTrackCount');
      const durEl = document.getElementById('spPlaylistDuration');
      const coverWrap = document.getElementById('spPlaylistCoverWrap');
      const bodyEl = document.getElementById('spPlaylistTableBody');
      const playAllBtn = document.getElementById('btnSpPlaylistPlayAll');
      const addAllBtn = document.getElementById('btnSpPlaylistAddAllToDj');
      const badgeEl = document.getElementById('spPlaylistTypeBadge');

      if (titleEl) titleEl.textContent = 'Canciones que te gustan';
      if (descEl) descEl.textContent = 'Colección de tus temas favoritos guardados en tu cuenta oficial de Spotify.';
      if (ownerEl) ownerEl.textContent = 'Tu Biblioteca de Spotify';
      if (badgeEl) badgeEl.textContent = 'CANCIONES QUE TE GUSTAN';

      if (coverWrap) {
        coverWrap.className = 'sp-inspected-cover-wrap liked-gradient';
        coverWrap.innerHTML = `<svg width="72" height="72" viewBox="0 0 24 24" fill="#ffffff"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>`;
      }

      switchAppView('playlist');
      if (bodyEl) bodyEl.innerHTML = '<div style="padding:20px; color:#b3b3b3;">Cargando tus canciones favoritas...</div>';

      let tracks = [];
      const token = await getValidSpotifyToken();
      if (token) {
        const likedData = await fetchSpotifyLikedSongs(token, 50);
        tracks = (likedData.items || []).map(x => x.track).filter(Boolean);
      }
      if (!tracks.length) {
        tracks = CURATED_ROCK_TRACKS;
      }

      if (countEl) countEl.textContent = `${tracks.length} canciones`;
      const totalMs = tracks.reduce((acc, t) => acc + (t.duration_ms || 180000), 0);
      const totalMin = Math.round(totalMs / 60000);
      if (durEl) durEl.textContent = `Aprox. ${totalMin} min`;

      if (bodyEl) {
        bodyEl.innerHTML = '';
        tracks.forEach((t, idx) => {
          const row = document.createElement('div');
          row.className = 'dj-song-row';
          row.style.gridTemplateColumns = '36px 3fr 2fr 1fr 140px';
          row.style.alignItems = 'center';
          const tImg = (t.album && t.album.images && t.album.images.length > 0 && t.album.images[0].url) ? t.album.images[0].url : 'img/covers/cover_kiss.png';
          const tArtists = (t.artists || []).map(a => a.name).join(', ') || 'Rock';
          const durSec = Math.floor((t.duration_ms || 180000) / 1000);
          const albumName = (t.album && t.album.name) ? t.album.name : 'Álbum Oficial';

          row.innerHTML = `
            <div class="dj-col-num">${idx + 1}</div>
            <div class="sp-table-track-cell">
              <img src="${tImg}" alt="${escapeHtmlStr(t.name)}" class="sp-table-track-thumb">
              <div class="sp-table-track-info">
                <span class="sp-table-track-title">${escapeHtmlStr(t.name)}</span>
                <span class="sp-table-track-artists">${escapeHtmlStr(tArtists)}</span>
              </div>
            </div>
            <div style="font-size:0.8rem; color:#b3b3b3; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${escapeHtmlStr(albumName)}</div>
            <div class="dj-col-year" style="font-size:0.8rem; color:#b3b3b3;">${formatTime(durSec)}</div>
            <div style="text-align:right;">
              <button class="home-card-add-dj sp-row-add-btn" type="button" style="margin:0; width:auto; padding:4px 10px;">+ DJ Fredd</button>
            </div>
          `;

          const rowAddBtn = row.querySelector('.sp-row-add-btn');
          if (rowAddBtn) {
            rowAddBtn.addEventListener('click', (e) => {
              e.stopPropagation();
              addSpotifyTrackToDjEddie(t);
            });
          }

          row.addEventListener('click', () => {
            playSpotifyTrack(t, row, tracks, idx);
          });
          bodyEl.appendChild(row);
        });
      }

      if (playAllBtn) {
        playAllBtn.onclick = () => {
          if (tracks.length > 0) {
            const firstRow = bodyEl.querySelector('.dj-song-row');
            playSpotifyTrack(tracks[0], firstRow, tracks, 0);
          }
        };
      }

      if (addAllBtn) {
        addAllBtn.onclick = () => {
          let countAdded = 0;
          tracks.forEach(tr => {
            addSpotifyTrackToDjEddie(tr);
            countAdded++;
          });
          showAppToast(`✓ ${countAdded} canciones añadidas a DJ Fredd para narrar sus historias`, 'success');
        };
      }
    }

    // ========================================================
    // HOME SHELVES MASTER RENDERER (AUTHENTIC SPOTIFY PATTERNS)
    // ========================================================
    async function renderSpotifyHomeShelves() {
      const catalog = buildDjEddieCatalog();
      const token = await getValidSpotifyToken();

      // Connect Back Button in Playlist View
      const backFromPlaylistBtn = document.getElementById('btnBackHomeFromSpPlaylist');
      if (backFromPlaylistBtn && !backFromPlaylistBtn.dataset.bound) {
        backFromPlaylistBtn.dataset.bound = 'true';
        backFromPlaylistBtn.addEventListener('click', () => switchAppView('home'));
      }

      // 1. Spotify Connect Banner on Home
      const bannerEl = document.getElementById('spotifyHomeConnectBanner');
      if (bannerEl) {
        if (token) {
          let profile = null;
          try { profile = JSON.parse(localStorage.getItem('sp_user_profile') || 'null'); } catch (e) {}
          const userName = profile ? (profile.display_name || profile.email) : 'Usuario Spotify';
          const product = profile ? (profile.product || 'Conectado') : 'Activo';

          bannerEl.innerHTML = `
            <div class="spotify-connect-banner-left">
              <div class="spotify-connect-logo-badge">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="#000000"><path d="M12 2C6.477 2 2 6.477 2 12c0 5.524 4.477 10 10 10s10-4.476 10-10c0-5.523-4.477-10-10-10zm4.586 14.424c-.18.295-.563.387-.857.207-2.35-1.434-5.308-1.758-8.793-.963-.335.077-.67-.133-.746-.469-.077-.334.132-.67.467-.747 3.812-.871 7.076-.508 9.721 1.116.295.18.388.563.208.856zm1.223-2.723c-.226.367-.709.482-1.075.257-2.69-1.653-6.79-2.133-9.972-1.168-.413.125-.85-.107-.975-.521-.125-.414.108-.851.521-.976 3.633-1.102 8.147-.568 11.244 1.332.366.226.482.71.257 1.076zm.106-2.835C14.692 8.95 9.375 8.775 6.297 9.71c-.496.15-1.022-.134-1.173-.63-.151-.497.133-1.022.63-1.173 3.532-1.072 9.404-.87 13.115 1.333.447.265.592.846.327 1.293-.266.447-.847.592-1.294.326z"/></svg>
              </div>
              <div>
                <div class="spotify-connect-title">🟢 Conectado con Spotify • ${escapeHtmlStr(userName)}</div>
                <div class="spotify-connect-sub">Tu cuenta (${product.toUpperCase()}) está vinculada. Explora tus playlists, tus canciones favoritas o añade cualquier tema a DJ Fredd.</div>
              </div>
            </div>
            <button class="spotify-connect-btn" type="button" id="btnHomeOpenSearch" style="background:rgba(255,255,255,0.1); color:#ffffff; border:1px solid rgba(255,255,255,0.2);">
              <span>🔍 Buscar en Spotify</span>
            </button>
          `;
          const btnSearch = bannerEl.querySelector('#btnHomeOpenSearch');
          if (btnSearch) {
            btnSearch.addEventListener('click', () => {
              if (spotifySearchInput) {
                spotifySearchInput.focus();
                spotifySearchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
              }
            });
          }
        } else {
          bannerEl.innerHTML = `
            <div class="spotify-connect-banner-left">
              <div class="spotify-connect-logo-badge">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="#000000"><path d="M12 2C6.477 2 2 6.477 2 12c0 5.524 4.477 10 10 10s10-4.476 10-10c0-5.523-4.477-10-10-10zm4.586 14.424c-.18.295-.563.387-.857.207-2.35-1.434-5.308-1.758-8.793-.963-.335.077-.67-.133-.746-.469-.077-.334.132-.67.467-.747 3.812-.871 7.076-.508 9.721 1.116.295.18.388.563.208.856zm1.223-2.723c-.226.367-.709.482-1.075.257-2.69-1.653-6.79-2.133-9.972-1.168-.413.125-.85-.107-.975-.521-.125-.414.108-.851.521-.976 3.633-1.102 8.147-.568 11.244 1.332.366.226.482.71.257 1.076zm.106-2.835C14.692 8.95 9.375 8.775 6.297 9.71c-.496.15-1.022-.134-1.173-.63-.151-.497.133-1.022.63-1.173 3.532-1.072 9.404-.87 13.115 1.333.447.265.592.846.327 1.293-.266.447-.847.592-1.294.326z"/></svg>
              </div>
              <div>
                <div class="spotify-connect-title">Conecta tu cuenta de Spotify</div>
                <div class="spotify-connect-sub">Accede a tus playlists reales, tus canciones favoritas y recomendaciones personalizadas para escucharlas o narrarlas con DJ Fredd.</div>
              </div>
            </div>
            <button class="spotify-connect-btn" type="button" id="btnHomeConnectSp">
              <span>Iniciar sesión con Spotify</span>
            </button>
          `;
          const btnConn = bannerEl.querySelector('#btnHomeConnectSp');
          if (btnConn) {
            btnConn.addEventListener('click', startSpotifyLogin);
          }
        }
      }

      // 2. Shelf: Tus Playlists
      const userPlRow = document.getElementById('userPlaylistsRow');
      const subUserPl = document.getElementById('subUserPlaylists');
      const btnMoreUserPl = document.getElementById('btnMoreUserPlaylists');
      if (userPlRow) {
        userPlRow.innerHTML = '';
        let playlistsToShow = [];
        if (token) {
          playlistsToShow = await fetchSpotifyUserPlaylists(token);
          if (subUserPl) subUserPl.textContent = `${playlistsToShow.length} playlists sincronizadas desde tu cuenta de Spotify`;
        }
        if (!playlistsToShow || !playlistsToShow.length) {
          playlistsToShow = CURATED_ROCK_PLAYLISTS;
          if (subUserPl) subUserPl.textContent = 'Selección de playlists clásicas de rock para ti';
        }
        playlistsToShow.slice(0, 6).forEach(pl => {
          userPlRow.appendChild(createSpotifyHomePlaylistCard(pl));
        });
        if (btnMoreUserPl) {
          btnMoreUserPl.onclick = () => {
            if (playlistsToShow.length) openSpotifyPlaylistView(playlistsToShow[0]);
          };
        }
      }

      // 3. Shelf: Canciones que te gustan (Liked Songs)
      const likedRow = document.getElementById('likedSongsRow');
      const subLiked = document.getElementById('subLikedSongs');
      const btnMoreLiked = document.getElementById('btnMoreLikedSongs');
      if (likedRow) {
        likedRow.innerHTML = '';
        let likedSongs = [];
        let totalLiked = 0;
        if (token) {
          const lData = await fetchSpotifyLikedSongs(token, 10);
          likedSongs = (lData.items || []).map(x => x.track).filter(Boolean);
          totalLiked = lData.total || likedSongs.length;
          if (subLiked) subLiked.textContent = `${totalLiked} canciones guardadas en tu biblioteca`;
        }
        if (!likedSongs.length) {
          likedSongs = CURATED_ROCK_TRACKS.slice(0, 5);
          if (subLiked) subLiked.textContent = 'Tus canciones favoritas guardadas en Spotify';
        }

        // First item is iconic purple liked songs card
        likedRow.appendChild(createSpotifyLikedSongsCard(totalLiked));

        likedSongs.slice(0, 5).forEach((trk, idx) => {
          likedRow.appendChild(createSpotifyHomeTrackCard(trk, likedSongs, idx));
        });

        if (btnMoreLiked) {
          btnMoreLiked.onclick = openSpotifyLikedSongsView;
        }
      }

      // 4. Shelf: Tus canciones más escuchadas (Top Tracks)
      const topTracksRow = document.getElementById('topTracksRow');
      const subTopTracks = document.getElementById('subTopTracks');
      if (topTracksRow) {
        topTracksRow.innerHTML = '';
        let topTracks = [];
        if (token) {
          topTracks = await fetchSpotifyTopTracks(token, 8);
          if (subTopTracks) subTopTracks.textContent = 'Tus temas más escuchados en Spotify';
        }
        if (!topTracks || !topTracks.length) {
          topTracks = CURATED_ROCK_TRACKS;
          if (subTopTracks) subTopTracks.textContent = 'Los himnos más escuchados del rock mundial';
        }
        topTracks.slice(0, 6).forEach((trk, idx) => {
          topTracksRow.appendChild(createSpotifyHomeTrackCard(trk, topTracks, idx));
        });
      }

      // 5. Shelf: Recomendado para ti (Algorithmic Rock Recommendations)
      const recRow = document.getElementById('recommendedMusicRow');
      const subRec = document.getElementById('subRecommendedMusic');
      const btnMoreRec = document.getElementById('btnMoreRecommended');
      if (recRow) {
        recRow.innerHTML = '';
        let recTracks = [];
        if (token) {
          recTracks = await fetchSpotifyRecommendations(token, 'rock,classic-rock,hard-rock');
          if (subRec) subRec.textContent = 'Recomendaciones algorítmicas de rock basadas en tu gusto';
        }
        if (!recTracks || !recTracks.length) {
          recTracks = CURATED_ROCK_TRACKS.slice().reverse();
          if (subRec) subRec.textContent = 'Descubrimientos y joyas del rock seleccionados para ti';
        }
        recTracks.slice(0, 6).forEach((trk, idx) => {
          recRow.appendChild(createSpotifyHomeTrackCard(trk, recTracks, idx));
        });
        if (btnMoreRec) {
          btnMoreRec.onclick = () => {
            sessionStorage.removeItem('sp_cache_recommendations');
            renderSpotifyHomeShelves();
            showAppToast('🔄 Recomendaciones actualizadas', 'info');
          };
        }
      }

      // 6. Shelf: Escuchado recientemente (Recently Played)
      const recPlayedRow = document.getElementById('recentlyPlayedRow');
      const subRecPlayed = document.getElementById('subRecentlyPlayed');
      if (recPlayedRow) {
        recPlayedRow.innerHTML = '';
        let recentTracks = [];
        if (token) {
          recentTracks = await fetchSpotifyRecentlyPlayed(token, 6);
          if (subRecPlayed) subRecPlayed.textContent = 'Tus últimas reproducciones en Spotify';
        }
        if (!recentTracks || !recentTracks.length) {
          recentTracks = CURATED_ROCK_TRACKS.slice(2, 8);
          if (subRecPlayed) subRecPlayed.textContent = 'Historial reciente de clásicos del rock';
        }
        recentTracks.slice(0, 6).forEach((trk, idx) => {
          recPlayedRow.appendChild(createSpotifyHomeTrackCard(trk, recentTracks, idx));
        });
      }

      // 7. Shelf: Tus Artistas Favoritos (Circular Spotify Artist Cards)
      const artRow = document.getElementById('favoriteArtistsRow');
      if (artRow) {
        artRow.innerHTML = '';
        let artistsToShow = [];
        if (token) {
          const userTopArtists = await fetchSpotifyTopArtists(token, 8);
          if (userTopArtists && userTopArtists.length) {
            artistsToShow = userTopArtists;
          }
        }
        if (!artistsToShow.length) {
          artistsToShow = Object.values(bands).map(b => ({
            id: b.id,
            name: b.name,
            genreLabel: b.genreLabel,
            images: [{ url: b.cover }],
            isLocalBand: true
          }));
        }

        artistsToShow.slice(0, 6).forEach(a => {
          const imgUrl = (a.images && a.images.length > 0 && a.images[0].url) ? a.images[0].url : 'img/covers/cover_kiss.png';
          const card = document.createElement('div');
          card.className = 'home-sp-card';
          card.innerHTML = `
            <div class="home-sp-card-art circle">
              <img src="${imgUrl}" alt="${escapeHtmlStr(a.name)}" loading="lazy">
              <button class="home-sp-card-play" type="button" title="Abrir perfil de ${escapeHtmlStr(a.name)}">
                <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
              </button>
            </div>
            <div class="home-sp-card-title" style="text-align:center;">${escapeHtmlStr(a.name)}</div>
            <div class="home-sp-card-sub" style="text-align:center;">Artista • ${escapeHtmlStr(a.genreLabel || 'Rock')}</div>
          `;
          card.addEventListener('click', () => {
            if (a.isLocalBand) {
              openBandView(a.id, true, '45s');
            } else {
              openSpotifyArtistCatalog(a);
            }
          });
          artRow.appendChild(card);
        });
      }

      // 8. Shelf: DJ Fredd • La Radio de la IA (Main Card)
      const djRow = document.getElementById('djEddieTracksRow');
      if (djRow) {
        djRow.innerHTML = '';
        const moreBtn = document.querySelector('[data-filterjump="djeddie"]');
        if (moreBtn) moreBtn.textContent = `Mostrar todo (${catalog.length})`;
        const startBtnLabel = document.getElementById('btnStartDjEddieLabel');
        if (startBtnLabel) startBtnLabel.textContent = `Ver listado de canciones (${catalog.length})`;

        const mainDjCard = document.createElement('div');
        mainDjCard.className = 'home-sp-card' + (isDjEddieActive ? ' active-playing' : '');
        mainDjCard.style.borderColor = 'rgba(52, 211, 153, 0.45)';
        mainDjCard.style.background = 'linear-gradient(160deg, rgba(15,23,42,0.95) 0%, rgba(30,58,138,0.55) 55%, rgba(6,95,70,0.55) 100%)';
        mainDjCard.innerHTML = `
          <div class="home-sp-card-art" style="background: radial-gradient(circle at 50% 45%, #10b981 0%, #1d4ed8 55%, #090d16 100%); display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px;">
            <div style="font-size:3rem; filter:drop-shadow(0 6px 16px rgba(0,0,0,0.6));">🤖</div>
            <div style="font-size:0.75rem; font-weight:900; letter-spacing:0.12em; color:#ffffff; background:rgba(0,0,0,0.45); padding:3px 10px; border-radius:999px; border:1px solid rgba(255,255,255,0.2);">DJ FREDD</div>
            <span class="home-sp-card-badge">${catalog.length} CANCIONES</span>
            <button class="home-sp-card-play" type="button" title="Ver listado de canciones de DJ Fredd">
              <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            </button>
          </div>
          <div class="home-sp-card-title" style="color:#6ee7b7;">DJ Fredd • La Radio de la IA</div>
          <div class="home-sp-card-sub">Ingresa para ver el listado de las ${catalog.length} canciones con historias narradas por DJ Fredd</div>
        `;
        mainDjCard.addEventListener('click', () => {
          openDjEddiePlaylistView();
        });
        djRow.appendChild(mainDjCard);
      }
    }

    function applyHomeCategoryFilter(cat) {"""

    content = old_home_shelves_render_re.sub(new_home_shelves_render, content, 1)
    print("✓ renderSpotifyHomeShelves and fetchers updated")

    # 5. Clear caches in logoutSpotify
    old_logout = """    function logoutSpotify() {
      localStorage.removeItem('sp_access_token');
      localStorage.removeItem('sp_refresh_token');
      localStorage.removeItem('sp_expires_at');
      localStorage.removeItem('sp_user_profile');
      if (spotifySdkPlayer) {
        try { spotifySdkPlayer.disconnect(); } catch (e) {}
      }
      updateSpotifyAuthUI(null);
      if (spotifyApiSearchSection) {
        spotifyApiSearchSection.classList.remove('visible');
      }
    }"""

    new_logout = """    function logoutSpotify() {
      localStorage.removeItem('sp_access_token');
      localStorage.removeItem('sp_refresh_token');
      localStorage.removeItem('sp_expires_at');
      localStorage.removeItem('sp_user_profile');
      sessionStorage.removeItem('sp_cache_playlists');
      sessionStorage.removeItem('sp_cache_liked_songs');
      sessionStorage.removeItem('sp_cache_top_tracks');
      sessionStorage.removeItem('sp_cache_top_artists');
      sessionStorage.removeItem('sp_cache_recently_played');
      sessionStorage.removeItem('sp_cache_recommendations');
      if (spotifySdkPlayer) {
        try { spotifySdkPlayer.disconnect(); } catch (e) {}
      }
      updateSpotifyAuthUI(null);
      if (spotifyApiSearchSection) {
        spotifyApiSearchSection.classList.remove('visible');
      }
      renderSpotifyHomeShelves();
      renderSidebarPlaylists();
    }"""

    if old_logout in content:
        content = content.replace(old_logout, new_logout, 1)
        print("✓ logoutSpotify updated")
    else:
        print("✗ old_logout not found")
        sys.exit(1)

    # 6. Call renderSpotifyHomeShelves and renderSidebarPlaylists when auth succeeds
    old_init_token_cb = """        const token = await exchangeCodeForToken(authCode);
        if (token) {
          const profile = await fetchSpotifyUserProfile();
          updateSpotifyAuthUI(profile);
        }"""

    new_init_token_cb = """        const token = await exchangeCodeForToken(authCode);
        if (token) {
          const profile = await fetchSpotifyUserProfile();
          updateSpotifyAuthUI(profile);
          renderSpotifyHomeShelves();
          renderSidebarPlaylists();
        }"""

    if old_init_token_cb in content:
        content = content.replace(old_init_token_cb, new_init_token_cb, 1)
        print("✓ authCode token callback updated")
    else:
        print("✗ old_init_token_cb not found")
        sys.exit(1)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Done phase 2!")

if __name__ == '__main__':
    main()
