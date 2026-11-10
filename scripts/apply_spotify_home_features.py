import re
import sys

def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Check if already applied
    if 'id="shelfUserPlaylists"' in content:
        print("Already updated with shelfUserPlaylists")
        return

    # A. Add CSS styles
    css_target = '    /* Spotify 6-Card Quick Banners Grid */'
    css_addition = '''    /* Spotify Connect Banner & Personalized Shelves */
    .spotify-connect-banner {
      background: linear-gradient(90deg, rgba(30, 58, 138, 0.45) 0%, rgba(16, 185, 129, 0.16) 100%);
      border: 1px solid rgba(52, 211, 153, 0.28);
      border-radius: 12px;
      padding: 16px 20px;
      margin-bottom: 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }
    .spotify-connect-banner-left {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .spotify-connect-logo-badge {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: #1ed760;
      color: #000;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      box-shadow: 0 4px 14px rgba(30, 215, 96, 0.35);
    }
    .spotify-connect-title {
      font-size: 1rem;
      font-weight: 800;
      color: #ffffff;
      margin-bottom: 2px;
    }
    .spotify-connect-sub {
      font-size: 0.8rem;
      color: #b3b3b3;
      line-height: 1.35;
    }
    .spotify-connect-btn {
      background: #1ed760;
      color: #000000;
      font-weight: 800;
      font-size: 0.82rem;
      padding: 9px 18px;
      border-radius: 9999px;
      border: none;
      cursor: pointer;
      transition: all 0.2s ease;
      white-space: nowrap;
      flex-shrink: 0;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .spotify-connect-btn:hover {
      background: #1fdf64;
      transform: scale(1.03);
    }
    .home-card-add-dj {
      margin-top: 8px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      background: rgba(16, 185, 129, 0.12);
      color: #6ee7b7;
      border: 1px solid rgba(52, 211, 153, 0.35);
      border-radius: 9999px;
      padding: 5px 8px;
      font-size: 0.7rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.15s ease;
      width: 100%;
      text-align: center;
    }
    .home-card-add-dj:hover {
      background: #10b981;
      color: #000000;
      border-color: #10b981;
    }
    .sp-liked-card-art {
      width: 100%;
      aspect-ratio: 1 / 1;
      border-radius: 6px;
      background: linear-gradient(135deg, #450af5 0%, #8e8ee5 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      box-shadow: 0 8px 22px rgba(0, 0, 0, 0.55);
      margin-bottom: 12px;
    }
    .sp-liked-card-art svg {
      width: 44px;
      height: 44px;
      fill: #ffffff;
      filter: drop-shadow(0 4px 10px rgba(0,0,0,0.3));
    }
    .sp-inspected-cover-wrap {
      width: 192px;
      height: 192px;
      border-radius: 8px;
      overflow: hidden;
      background: #282828;
      box-shadow: 0 10px 30px rgba(0,0,0,0.6);
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .sp-inspected-cover-wrap img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .sp-inspected-cover-wrap.liked-gradient {
      background: linear-gradient(135deg, #450af5 0%, #8e8ee5 100%);
    }
    .sp-table-track-cell {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .sp-table-track-thumb {
      width: 40px;
      height: 40px;
      border-radius: 4px;
      object-fit: cover;
      flex-shrink: 0;
    }
    .sp-table-track-info {
      display: flex;
      flex-direction: column;
      gap: 2px;
      min-width: 0;
    }
    .sp-table-track-title {
      font-size: 0.88rem;
      font-weight: 700;
      color: #ffffff;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .sp-table-track-artists {
      font-size: 0.78rem;
      color: #b3b3b3;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    @media (max-width: 768px) {
      .spotify-connect-banner {
        flex-direction: column;
        align-items: flex-start;
        padding: 14px 16px;
        gap: 12px;
      }
      .spotify-connect-btn {
        width: 100%;
        justify-content: center;
      }
      .sp-inspected-cover-wrap {
        width: 112px;
        height: 112px;
      }
    }

'''
    if css_target in content:
        content = content.replace(css_target, css_addition + css_target, 1)
        print("✓ CSS styles inserted")
    else:
        print("✗ CSS target not found")
        sys.exit(1)

    # B. Replace #spotifyHomeShelves HTML
    shelves_target_re = re.compile(r'<!-- ESTANTERÍAS DEL HOME DE SPOTIFY.*?<section class="spotify-home-shelves" id="spotifyHomeShelves">.*?</section>', re.DOTALL)
    shelves_match = shelves_target_re.search(content)
    if not shelves_match:
        print("✗ Shelves HTML target not found")
        sys.exit(1)

    new_shelves_html = '''<!-- ESTANTERÍAS DEL HOME DE SPOTIFY (Playlists + Liked Songs + Top Tracks + Recomendados + Recientes + Artistas + DJ Fredd) -->
      <section class="spotify-home-shelves" id="spotifyHomeShelves">
        <!-- Banner de Conexión / Estado Spotify -->
        <div class="spotify-connect-banner" id="spotifyHomeConnectBanner">
          <!-- Rendered dynamically via JS -->
        </div>

        <!-- 1. Tus Playlists -->
        <div class="home-shelf-section" id="shelfUserPlaylists">
          <div class="home-shelf-header">
            <div>
              <h2 class="home-shelf-title">Tus Playlists</h2>
              <p class="home-shelf-subtitle" id="subUserPlaylists">Listas de reproducción sincronizadas con tu cuenta de Spotify</p>
            </div>
            <button class="home-shelf-more" type="button" id="btnMoreUserPlaylists">Mostrar todas</button>
          </div>
          <div class="home-cards-row" id="userPlaylistsRow">
            <!-- Rendered via JS -->
          </div>
        </div>

        <!-- 2. Canciones que te gustan (Liked Songs) -->
        <div class="home-shelf-section" id="shelfLikedSongs">
          <div class="home-shelf-header">
            <div>
              <h2 class="home-shelf-title">Canciones que te gustan</h2>
              <p class="home-shelf-subtitle" id="subLikedSongs">Tus temas favoritos en Spotify guardados en tu biblioteca</p>
            </div>
            <button class="home-shelf-more" type="button" id="btnMoreLikedSongs">Ver todas</button>
          </div>
          <div class="home-cards-row" id="likedSongsRow">
            <!-- Rendered via JS -->
          </div>
        </div>

        <!-- 3. Tus canciones más escuchadas (Top Tracks) -->
        <div class="home-shelf-section" id="shelfTopTracks">
          <div class="home-shelf-header">
            <div>
              <h2 class="home-shelf-title">Tus canciones más escuchadas</h2>
              <p class="home-shelf-subtitle" id="subTopTracks">Tus temas más reproducidos en Spotify</p>
            </div>
            <button class="home-shelf-more" type="button" id="btnMoreTopTracks">Mostrar todo</button>
          </div>
          <div class="home-cards-row" id="topTracksRow">
            <!-- Rendered via JS -->
          </div>
        </div>

        <!-- 4. Recomendado para ti (Algorithmic Rock Recommendations) -->
        <div class="home-shelf-section" id="shelfRecommendedMusic">
          <div class="home-shelf-header">
            <div>
              <h2 class="home-shelf-title">Recomendado para ti</h2>
              <p class="home-shelf-subtitle" id="subRecommendedMusic">Clásicos y descubrimientos del rock seleccionados para ti</p>
            </div>
            <button class="home-shelf-more" type="button" id="btnMoreRecommended">Actualizar</button>
          </div>
          <div class="home-cards-row" id="recommendedMusicRow">
            <!-- Rendered via JS -->
          </div>
        </div>

        <!-- 5. Escuchado recientemente (Recently Played) -->
        <div class="home-shelf-section" id="shelfRecentlyPlayed">
          <div class="home-shelf-header">
            <div>
              <h2 class="home-shelf-title">Escuchado recientemente</h2>
              <p class="home-shelf-subtitle" id="subRecentlyPlayed">Tu historial reciente de reproducción en Spotify</p>
            </div>
            <button class="home-shelf-more" type="button" id="btnMoreRecentlyPlayed">Mostrar todo</button>
          </div>
          <div class="home-cards-row" id="recentlyPlayedRow">
            <!-- Rendered via JS -->
          </div>
        </div>

        <!-- 6. Tus artistas favoritos -->
        <div class="home-shelf-section" id="shelfFavoriteArtists">
          <div class="home-shelf-header">
            <div>
              <h2 class="home-shelf-title">Tus artistas favoritos</h2>
              <p class="home-shelf-subtitle" id="subFavoriteArtists">Toca cualquier banda o artista para abrir su discografía y letras</p>
            </div>
            <button class="home-shelf-more" type="button" data-filterjump="artists">Mostrar todos</button>
          </div>
          <div class="home-cards-row" id="favoriteArtistsRow">
            <!-- Rendered via JS -->
          </div>
        </div>

        <!-- 7. DJ Fredd - La Radio de la IA -->
        <div class="home-shelf-section" id="shelfDjEddie">
          <div class="home-shelf-header">
            <div>
              <h2 class="home-shelf-title">🎙️ DJ Fredd • La Radio de la IA</h2>
              <p class="home-shelf-subtitle">"La música tiene memoria." Canciones completas con historia real narrada por DJ Fredd</p>
            </div>
            <button class="home-shelf-more" type="button" data-filterjump="djeddie">Mostrar todo</button>
          </div>
          <div class="home-cards-row" id="djEddieTracksRow">
            <!-- Rendered via JS -->
          </div>
        </div>
      </section>'''

    content = content[:shelves_match.start()] + new_shelves_html + content[shelves_match.end():]
    print("✓ Shelves HTML updated")

    # C. Add #spotifyPlaylistSection right after #djEddiePlaylistSection
    dj_playlist_end_target = '</section>\n\n      <!-- Barra para volver al Home cuando estás viendo una Banda -->'
    sp_playlist_section_html = '''</section>

      <!-- ========================================================
           VISTA DE PLAYLIST DE SPOTIFY (INSPECTOR DE PLAYLISTS / LIKED SONGS)
           ======================================================== -->
      <section class="dj-eddie-playlist-view" id="spotifyPlaylistSection" style="display: none;">
        <div class="dj-playlist-top-nav">
          <button class="btn-back-home" id="btnBackHomeFromSpPlaylist" type="button">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>
            <span>Volver al Inicio</span>
          </button>
        </div>

        <div class="dj-playlist-hero" id="spPlaylistHero">
          <div class="sp-inspected-cover-wrap" id="spPlaylistCoverWrap">
            <!-- Cover image or liked gradient -->
          </div>
          <div class="dj-playlist-hero-info">
            <div class="dj-eddie-badge-row">
              <span class="dj-eddie-live-dot" style="background:#1ed760;"></span>
              <span id="spPlaylistTypeBadge">PLAYLIST SPOTIFY</span>
            </div>
            <h1 class="dj-playlist-main-title" id="spPlaylistMainTitle">Nombre de la Playlist</h1>
            <p class="dj-playlist-main-desc" id="spPlaylistMainDesc">Descripción de la playlist...</p>
            <div class="dj-playlist-meta-line">
              <span id="spPlaylistOwner" style="color:#ffffff; font-weight:700;">De Spotify</span>
              <span>•</span>
              <span id="spPlaylistTrackCount">0 canciones</span>
              <span>•</span>
              <span id="spPlaylistDuration" style="color:#b3b3b3;">0 min</span>
            </div>
          </div>
        </div>

        <div class="dj-playlist-action-bar">
          <button class="btn-spotify-play-big" id="btnSpPlaylistPlayAll" type="button" title="Reproducir playlist">
            <svg viewBox="0 0 24 24"><path d="M7.05 3.606l13.49 7.788a.7.7 0 0 1 0 1.212L7.05 20.394A.7.7 0 0 1 6 19.788V4.212a.7.7 0 0 1 1.05-.606z"/></svg>
          </button>
          <button class="btn-dj-eddie-play" id="btnSpPlaylistAddAllToDj" type="button" style="background: rgba(16, 185, 129, 0.2); border: 1px solid rgba(52, 211, 153, 0.45); color: #6ee7b7;">
            <span>🎙️ Añadir todas las canciones a DJ Fredd</span>
          </button>
        </div>

        <div class="dj-playlist-table-wrap">
          <div class="dj-playlist-table-header" style="grid-template-columns: 36px 3fr 2fr 1fr 140px;">
            <div class="dj-col-num">#</div>
            <div>Título y Artista</div>
            <div>Álbum</div>
            <div class="dj-col-year">Duración</div>
            <div style="text-align: right;">Acciones</div>
          </div>
          <div class="dj-playlist-table-body" id="spPlaylistTableBody">
            <!-- Rendered via JS -->
          </div>
        </div>
      </section>

      <!-- Barra para volver al Home cuando estás viendo una Banda -->'''

    if dj_playlist_end_target in content:
        content = content.replace(dj_playlist_end_target, sp_playlist_section_html, 1)
        print("✓ #spotifyPlaylistSection HTML inserted")
    else:
        print("✗ dj_playlist_end_target not found")
        sys.exit(1)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Done phase 1!")

if __name__ == '__main__':
    main()
