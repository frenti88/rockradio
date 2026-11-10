import json
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update bands JSON
bands_match = re.search(r'const bands = (\{[\s\S]*?\});\s*const bandKeys', content)
if not bands_match:
    print('Failed to match bands')
    exit(1)

bands = json.loads(bands_match.group(1))

spotify_artists_map = {
    'kiss': {
        'artistPhoto': 'img/artists/artist_kiss.jpg',
        'spotifyArtistPhoto': 'https://image-cdn-ak.spotifycdn.com/image/ab67616100005174d8205a492a79bfe4b34c567a',
        'fullCover': 'img/albums/kiss_1976_destroyer.png'
    },
    'acdc': {
        'artistPhoto': 'img/artists/artist_acdc.jpg',
        'spotifyArtistPhoto': 'https://image-cdn-ak.spotifycdn.com/image/ab67616100005174c4c77549095c86acb4e77b37',
        'fullCover': 'img/albums/acdc_1980_back_in_black.png'
    },
    'queen': {
        'artistPhoto': 'img/artists/artist_queen.jpg',
        'spotifyArtistPhoto': 'https://image-cdn-ak.spotifycdn.com/image/ab6761610000517473e4d22612ac8d944b5789b4',
        'fullCover': 'img/albums/queen_1975_night_at_opera.png'
    },
    'led_zeppelin': {
        'artistPhoto': 'img/artists/artist_led_zeppelin.jpg',
        'spotifyArtistPhoto': 'https://i.scdn.co/image/ab6775700000ee85b0277cabdc556a31e643fdc5',
        'fullCover': 'img/albums/led_zeppelin_1971_iv.png'
    },
    'black_sabbath': {
        'artistPhoto': 'img/artists/artist_black_sabbath.jpg',
        'spotifyArtistPhoto': 'https://image-cdn-ak.spotifycdn.com/image/ab67616100005174d109fa1e6b28ddfc5846cc4f',
        'fullCover': 'img/albums/black_sabbath_1970_paranoid.png'
    },
    'guns_n_roses': {
        'artistPhoto': 'img/artists/artist_guns_n_roses.jpg',
        'spotifyArtistPhoto': 'https://image-cdn-ak.spotifycdn.com/image/ab6761610000517450defaf9fc059a1efc541f4c',
        'fullCover': 'img/albums/guns_n_roses_1987_appetite.png'
    },
    'metallica': {
        'artistPhoto': 'img/artists/artist_metallica.jpg',
        'spotifyArtistPhoto': 'https://image-cdn-fa.spotifycdn.com/image/ab6761610000517469ca98dd3083f1082d740e44',
        'fullCover': 'img/albums/metallica_1988_and_justice_for_all.png'
    },
    'def_leppard': {
        'artistPhoto': 'img/artists/artist_def_leppard.jpg',
        'spotifyArtistPhoto': 'https://image-cdn-ak.spotifycdn.com/image/ab67616100005174732222a7a4c725918f485a42',
        'fullCover': 'img/albums/def_leppard_1987_hysteria.png'
    },
    'rush': {
        'artistPhoto': 'img/artists/artist_rush.jpg',
        'spotifyArtistPhoto': 'https://image-cdn-ak.spotifycdn.com/image/ab67616100005174896c4b043fb3063178afd716',
        'fullCover': 'img/albums/rush_1981_moving_pictures.png'
    },
    'toto': {
        'artistPhoto': 'img/artists/artist_toto.jpg',
        'spotifyArtistPhoto': 'https://image-cdn-ak.spotifycdn.com/image/ab67616100005174a2e75d072e19a6150744f924',
        'fullCover': 'img/albums/toto_1982_toto_iv.png'
    },
    'alphaville': {
        'artistPhoto': 'img/artists/artist_alphaville.jpg',
        'spotifyArtistPhoto': 'https://image-cdn-ak.spotifycdn.com/image/ab676161000051743f8779bb1c97be855c6b51a8',
        'fullCover': 'img/albums/alphaville_1984_forever_young.png'
    },
    'motley_crue': {
        'artistPhoto': 'img/artists/artist_motley_crue.jpg',
        'spotifyArtistPhoto': 'https://image-cdn-ak.spotifycdn.com/image/ab67616100005174ab0922f900e6c22b8ef4c01c',
        'fullCover': 'img/albums/motley_crue_1983_shout.png'
    },
    'tears_for_fears': {
        'artistPhoto': 'img/artists/artist_tears_for_fears.jpg',
        'spotifyArtistPhoto': 'https://image-cdn-ak.spotifycdn.com/image/ab676161000051741e63dea1bded4ae1d53b5c9a',
        'fullCover': 'img/albums/tff_1985_songs_from_the_big_chair.png'
    }
}

for k, b in bands.items():
    if k in spotify_artists_map:
        info = spotify_artists_map[k]
        b['artistPhoto'] = info['artistPhoto']
        b['spotifyArtistPhoto'] = info['spotifyArtistPhoto']
        if b.get('hasFullTrack') and b.get('fullTrack'):
            b['fullTrack']['cover'] = info['fullCover']

bands_serialized = json.dumps(bands)
content = content[:bands_match.start(1)] + bands_serialized + content[bands_match.end(1):]

# 2. Update default HTML covers
content = content.replace('src="img/covers/cover_kiss.png"', 'src="img/artists/artist_kiss.jpg"')

# 3. Update loadBand image assignments
old_loadband_imgs = """      const heroArtImg = document.getElementById('heroArtImg');
      if (heroArtImg && b.cover) heroArtImg.src = b.cover;"""
new_loadband_imgs = """      const heroArtImg = document.getElementById('heroArtImg');
      if (heroArtImg) {
        heroArtImg.src = isFull ? (b.fullTrack.cover || b.artistPhoto || b.cover) : (b.artistPhoto || b.cover);
      }"""
content = content.replace(old_loadband_imgs, new_loadband_imgs)

old_bar_thumb = """      if (barThumbImg && b.cover) barThumbImg.src = b.cover;"""
new_bar_thumb = """      if (barThumbImg) {
        barThumbImg.src = isFull ? (b.fullTrack.cover || b.artistPhoto || b.cover) : (b.artistPhoto || b.cover);
      }"""
content = content.replace(old_bar_thumb, new_bar_thumb)

old_modal_art = """      if (modalArtImg && b.cover) modalArtImg.src = b.cover;"""
new_modal_art = """      if (modalArtImg) {
        modalArtImg.src = isFull ? (b.fullTrack.cover || b.artistPhoto || b.cover) : (b.artistPhoto || b.cover);
      }"""
content = content.replace(old_modal_art, new_modal_art)

old_spotify_about = """      if (spotifyAboutBg && b.cover) {
        spotifyAboutBg.style.backgroundImage = `url("${b.cover}")`;
      }"""
new_spotify_about = """      if (spotifyAboutBg) {
        spotifyAboutBg.style.backgroundImage = `url("${b.artistPhoto || b.cover}")`;
      }"""
content = content.replace(old_spotify_about, new_spotify_about)

# 4. Update tracklistTableBody thumbnails
content = content.replace(
    '<img src="${b.cover}" alt="${b.name}" style="width: 100%; height: 100%; object-fit: contain; background: #000;">',
    '<img src="${b.artistPhoto || b.cover}" alt="${b.name}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 4px;">'
)

# 5. Define CURATED_SPOTIFY_ARTISTS constant before CURATED_RECENTLY_PLAYED_TRACKS
curated_artists_js = """    const CURATED_SPOTIFY_ARTISTS = [
      {
        id: 'kiss',
        name: 'KISS',
        genreLabel: 'Hard Rock • Glam Rock',
        images: [{ url: 'https://image-cdn-ak.spotifycdn.com/image/ab67616100005174d8205a492a79bfe4b34c567a' }],
        fallbackImg: 'img/artists/artist_kiss.jpg',
        isLocalBand: true
      },
      {
        id: 'acdc',
        name: 'AC/DC',
        genreLabel: 'Hard Rock • High Voltage',
        images: [{ url: 'https://image-cdn-ak.spotifycdn.com/image/ab67616100005174c4c77549095c86acb4e77b37' }],
        fallbackImg: 'img/artists/artist_acdc.jpg',
        isLocalBand: true
      },
      {
        id: 'queen',
        name: 'Queen',
        genreLabel: 'Glam Rock • Arena Rock',
        images: [{ url: 'https://image-cdn-ak.spotifycdn.com/image/ab6761610000517473e4d22612ac8d944b5789b4' }],
        fallbackImg: 'img/artists/artist_queen.jpg',
        isLocalBand: true
      },
      {
        id: 'led_zeppelin',
        name: 'Led Zeppelin',
        genreLabel: 'Hard Rock • Blues Rock',
        images: [{ url: 'https://i.scdn.co/image/ab6775700000ee85b0277cabdc556a31e643fdc5' }],
        fallbackImg: 'img/artists/artist_led_zeppelin.jpg',
        isLocalBand: true
      },
      {
        id: 'black_sabbath',
        name: 'Black Sabbath',
        genreLabel: 'Heavy Metal • Doom',
        images: [{ url: 'https://image-cdn-ak.spotifycdn.com/image/ab67616100005174d109fa1e6b28ddfc5846cc4f' }],
        fallbackImg: 'img/artists/artist_black_sabbath.jpg',
        isLocalBand: true
      },
      {
        id: 'guns_n_roses',
        name: "Guns N' Roses",
        genreLabel: 'Hard Rock • Sleaze',
        images: [{ url: 'https://image-cdn-ak.spotifycdn.com/image/ab6761610000517450defaf9fc059a1efc541f4c' }],
        fallbackImg: 'img/artists/artist_guns_n_roses.jpg',
        isLocalBand: true
      },
      {
        id: 'metallica',
        name: 'Metallica',
        genreLabel: 'Thrash Metal • Speed Metal',
        images: [{ url: 'https://image-cdn-fa.spotifycdn.com/image/ab6761610000517469ca98dd3083f1082d740e44' }],
        fallbackImg: 'img/artists/artist_metallica.jpg',
        isLocalBand: true
      },
      {
        id: 'def_leppard',
        name: 'Def Leppard',
        genreLabel: 'Glam Metal • Arena Rock',
        images: [{ url: 'https://image-cdn-ak.spotifycdn.com/image/ab67616100005174732222a7a4c725918f485a42' }],
        fallbackImg: 'img/artists/artist_def_leppard.jpg',
        isLocalBand: true
      },
      {
        id: 'rush',
        name: 'Rush',
        genreLabel: 'Prog Rock • Hard Rock',
        images: [{ url: 'https://image-cdn-ak.spotifycdn.com/image/ab67616100005174896c4b043fb3063178afd716' }],
        fallbackImg: 'img/artists/artist_rush.jpg',
        isLocalBand: true
      },
      {
        id: 'toto',
        name: 'Toto',
        genreLabel: 'Classic Rock • Soft Rock',
        images: [{ url: 'https://image-cdn-ak.spotifycdn.com/image/ab67616100005174a2e75d072e19a6150744f924' }],
        fallbackImg: 'img/artists/artist_toto.jpg',
        isLocalBand: true
      },
      {
        id: 'alphaville',
        name: 'Alphaville',
        genreLabel: 'Synth-Pop • New Wave',
        images: [{ url: 'https://image-cdn-ak.spotifycdn.com/image/ab676161000051743f8779bb1c97be855c6b51a8' }],
        fallbackImg: 'img/artists/artist_alphaville.jpg',
        isLocalBand: true
      },
      {
        id: 'motley_crue',
        name: 'Mötley Crüe',
        genreLabel: 'Glam Metal • Hard Rock',
        images: [{ url: 'https://image-cdn-ak.spotifycdn.com/image/ab67616100005174ab0922f900e6c22b8ef4c01c' }],
        fallbackImg: 'img/artists/artist_motley_crue.jpg',
        isLocalBand: true
      },
      {
        id: 'tears_for_fears',
        name: 'Tears for Fears',
        genreLabel: 'New Wave • Synth-Pop',
        images: [{ url: 'https://image-cdn-ak.spotifycdn.com/image/ab676161000051741e63dea1bded4ae1d53b5c9a' }],
        fallbackImg: 'img/artists/artist_tears_for_fears.jpg',
        isLocalBand: true
      },
      {
        id: 'the_beatles',
        name: 'The Beatles',
        genreLabel: 'Classic Rock • British Invasion',
        images: [{ url: 'https://image-cdn-ak.spotifycdn.com/image/ab67616100005174357fdaf56c64a36a36741538' }],
        fallbackImg: 'img/artists/artist_the_beatles.jpg',
        isLocalBand: false
      }
    ];

    const CURATED_RECENTLY_PLAYED_TRACKS = ["""

content = content.replace('    const CURATED_RECENTLY_PLAYED_TRACKS = [', curated_artists_js)

# 6. Update shelfFavoriteArtists rendering in renderSpotifyHomeShelves
old_art_shelf = """      // 7. Shelf: Tus Artistas Favoritos (Circular Spotify Artist Cards)
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
          const imgUrl = (a.images && a.images.length > 0 && a.images[0].url) ? a.images[0].url : 'img/albums/queen_1975_night_at_opera.png';
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
      }"""

new_art_shelf = """      // 7. Shelf: Tus Artistas Favoritos (Circular Spotify Artist Cards with Authentic Spotify Photography)
      const artRow = document.getElementById('favoriteArtistsRow');
      if (artRow) {
        artRow.innerHTML = '';
        let artistsToShow = [];
        if (token) {
          const userTopArtists = await fetchSpotifyTopArtists(token, 14);
          if (userTopArtists && userTopArtists.length) {
            artistsToShow = userTopArtists;
          }
        }
        if (!artistsToShow.length) {
          artistsToShow = CURATED_SPOTIFY_ARTISTS;
        }

        artistsToShow.forEach(a => {
          const imgUrl = (a.images && a.images.length > 0 && a.images[0].url)
            ? a.images[0].url
            : (a.fallbackImg || 'img/artists/artist_queen.jpg');
          const fallback = a.fallbackImg || 'img/artists/artist_queen.jpg';
          const card = document.createElement('div');
          card.className = 'home-sp-card';
          card.innerHTML = `
            <div class="home-sp-card-art circle">
              <img src="${imgUrl}" alt="${escapeHtmlStr(a.name)}" loading="eager" onerror="this.onerror=null; this.src='${fallback}';">
              <button class="home-sp-card-play" type="button" title="Abrir discografía oficial de ${escapeHtmlStr(a.name)}">
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
      }"""

if old_art_shelf in content:
    content = content.replace(old_art_shelf, new_art_shelf)
    print('Replaced art shelf successfully')
else:
    print('WARNING: old_art_shelf not found in content!')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

for replica in ['kiss.html', 'rock45.html', 'kiss-podcast.html']:
    with open(replica, 'w', encoding='utf-8') as f:
        f.write(content)

print('Updated index.html and all replicas successfully!')
