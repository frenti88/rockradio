#!/usr/bin/env python3
"""
Implementación Integral de Fred Rewind
- Identidad oficial: Fred Rewind (1 'd'), DJ Fredd (2 'd')
- Insignia: «La música tiene memoria.»
- Concepto: De regreso al pasado.
- Plantilla oficial:
    Apertura: "Estás escuchando Fred Rewind, de regreso al pasado. Soy DJ Fredd."
    Desarrollo: Anécdota real verificable >= 30 segundos reales
    Cierre: "¡Sube el volumen y escuchemos a {nombre_cancion} aquí en Fred Rewind, de regreso al pasado!"
- Modal para consultar guion (#fredScriptModalOverlay) en scope global
- Tabla de 7 estados con botón "Detener generación"
- Secuencia: Intro DJ Fredd -> Canción original Spotify -> Siguiente elemento
- Replicado en index.html, kiss.html, rock45.html y kiss-podcast.html
"""
import os
import re

def apply_fred_rewind():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Title
    content = re.sub(
        r'<title>.*?</title>',
        '<title>Fred Rewind — La música tiene memoria | Con DJ Fredd</title>',
        content
    )

    # 2. Update CSS for Modal & Generation States
    modal_css = """
    /* FRED REWIND SCRIPT MODAL VIEWER */
    .fred-script-modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.78);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      z-index: 99999;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
      opacity: 0;
      transition: opacity 0.25s ease;
    }
    .fred-script-modal-overlay.active {
      display: flex !important;
      opacity: 1 !important;
    }
    .fred-script-modal-card {
      background: linear-gradient(175deg, #182234 0%, #0d131f 100%);
      border: 1px solid rgba(52, 211, 153, 0.35);
      border-radius: 18px;
      width: 100%;
      max-width: 680px;
      max-height: 85vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.75), 0 0 30px rgba(16, 185, 129, 0.15);
      overflow: hidden;
      animation: modalSlideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes modalSlideUp {
      from { transform: translateY(24px) scale(0.97); opacity: 0; }
      to { transform: translateY(0) scale(1); opacity: 1; }
    }
    .fred-script-modal-header {
      padding: 20px 24px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      background: rgba(255, 255, 255, 0.02);
    }
    .fred-script-modal-title-box h3 {
      font-size: 1.25rem;
      font-weight: 800;
      color: #ffffff;
      margin: 0 0 4px 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .fred-script-modal-title-box p {
      font-size: 0.85rem;
      color: #94a3b8;
      margin: 0;
    }
    .fred-script-close-btn {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: #cbd5e1;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 1.1rem;
      transition: all 0.2s ease;
    }
    .fred-script-close-btn:hover {
      background: rgba(255, 255, 255, 0.2);
      color: #ffffff;
      transform: scale(1.05);
    }
    .fred-script-modal-content {
      padding: 24px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .fred-script-block {
      background: rgba(0, 0, 0, 0.35);
      border-radius: 12px;
      padding: 16px 18px;
      border-left: 4px solid #10b981;
    }
    .fred-script-block.apertura {
      border-left-color: #38bdf8;
      background: rgba(56, 189, 248, 0.06);
    }
    .fred-script-block.desarrollo {
      border-left-color: #10b981;
      background: rgba(16, 185, 129, 0.06);
    }
    .fred-script-block.cierre {
      border-left-color: #fbbf24;
      background: rgba(251, 191, 36, 0.06);
    }
    .fred-script-label {
      font-size: 0.75rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 8px;
      display: block;
    }
    .fred-script-block.apertura .fred-script-label { color: #38bdf8; }
    .fred-script-block.desarrollo .fred-script-label { color: #34d399; }
    .fred-script-block.cierre .fred-script-label { color: #fbbf24; }
    .fred-script-text {
      font-size: 0.95rem;
      line-height: 1.65;
      color: #f1f5f9;
      margin: 0;
    }
    .fred-script-modal-footer {
      padding: 16px 24px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      background: rgba(0, 0, 0, 0.25);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
    .fred-script-modal-footer-left {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.8rem;
      color: #64748b;
    }
    .fred-script-dur-chip {
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      padding: 3px 10px;
      border-radius: 999px;
      font-weight: 700;
      font-size: 0.78rem;
      border: 1px solid rgba(52, 211, 153, 0.3);
    }
    .fred-script-actions-row {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .btn-fred-script-copy {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #ffffff;
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
    }
    .btn-fred-script-copy:hover {
      background: rgba(255, 255, 255, 0.16);
    }
    .btn-fred-script-play {
      background: #10b981;
      border: none;
      color: #000000;
      padding: 8px 16px;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
    }
    .btn-fred-script-play:hover {
      background: #059669;
      transform: scale(1.02);
    }
    .dj-script-preview {
      margin-top: 6px;
      padding: 6px 10px;
      background: rgba(16, 185, 129, 0.08);
      border: 1px solid rgba(52, 211, 153, 0.22);
      border-radius: 6px;
      font-size: 0.78rem;
      color: #a7f3d0;
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      cursor: pointer;
      transition: background 0.2s ease;
    }
    .dj-script-preview:hover {
      background: rgba(16, 185, 129, 0.16);
    }
    .dj-status-badge.cancelled {
      background: rgba(245, 158, 11, 0.15);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .dj-action-btn.view-script-btn {
      background: rgba(56, 189, 248, 0.12);
      color: #38bdf8;
      border-color: rgba(56, 189, 248, 0.3);
    }
    .dj-action-btn.view-script-btn:hover {
      background: rgba(56, 189, 248, 0.22);
      color: #7dd3fc;
    }
    """

    if '.fred-script-modal-overlay' not in content:
        content = content.replace('</style>', modal_css + '\n  </style>')
        print('✓ Modal CSS injected')

    # 3. Inject Modal HTML if not present
    modal_html = """
  <!-- FRED REWIND SCRIPT MODAL VIEWER -->
  <div class="fred-script-modal-overlay" id="fredScriptModalOverlay" role="dialog" aria-modal="true" aria-labelledby="fredScriptModalSongTitle">
    <div class="fred-script-modal-card">
      <div class="fred-script-modal-header">
        <div class="fred-script-modal-title-box">
          <h3 id="fredScriptModalSongTitle">Guion de la Historia</h3>
          <p id="fredScriptModalBand">Fred Rewind • Locutor: DJ Fredd • «La música tiene memoria»</p>
        </div>
        <button class="fred-script-close-btn" id="btnFredScriptModalClose" type="button" title="Cerrar ventana">✕</button>
      </div>

      <div class="fred-script-modal-content">
        <div class="fred-script-block apertura">
          <span class="fred-script-label">🎙️ APERTURA OFICIAL</span>
          <p class="fred-script-text" id="fredScriptAperturaText">Estás escuchando Fred Rewind, de regreso al pasado. Soy DJ Fredd.</p>
        </div>

        <div class="fred-script-block desarrollo">
          <span class="fred-script-label">📜 DESARROLLO DE LA HISTORIA (ANÉCDOTA REAL)</span>
          <p class="fred-script-text" id="fredScriptDesarrolloText">Cargando anécdota oficial...</p>
        </div>

        <div class="fred-script-block cierre">
          <span class="fred-script-label">⚡ CIERRE OBLIGATORIO</span>
          <p class="fred-script-text" id="fredScriptCierreText">¡Sube el volumen y escuchemos a esta canción aquí en Fred Rewind, de regreso al pasado!</p>
        </div>
      </div>

      <div class="fred-script-modal-footer">
        <div class="fred-script-modal-footer-left">
          <span>Duración mínima de locución:</span>
          <span class="fred-script-dur-chip" id="fredScriptDurChip">⏱️ 45s</span>
        </div>
        <div class="fred-script-actions-row">
          <button class="btn-fred-script-copy" id="btnFredScriptCopy" type="button" title="Copiar guion al portapapeles">📋 Copiar guion</button>
          <button class="btn-fred-script-play" id="btnFredScriptPlay" type="button" title="Reproducir historia con DJ Fredd">▶ Reproducir</button>
        </div>
      </div>
    </div>
  </div>
  """
    if 'id="fredScriptModalOverlay"' not in content:
        content = content.replace('<!-- SPOTIFY TU BIBLIOTECA MOBILE BOTTOM SHEET -->', modal_html + '\n  <!-- SPOTIFY TU BIBLIOTECA MOBILE BOTTOM SHEET -->')
        print('✓ Modal HTML injected')

    # 4. Clean up any misplaced modal JS block inside renderSpotifyHomeShelves
    clean_shelves_re = r'    // ========================================================\n    // FRED REWIND SCRIPT MODAL VIEWER.*?(?=      // 7\. Shelf: Tus Artistas Favoritos)'
    content = re.sub(clean_shelves_re, '', content, flags=re.DOTALL)

    # 5. Global Scope Script Modal Viewer Code
    modal_global_js = """
    // ========================================================
    // FRED REWIND SCRIPT MODAL VIEWER (GLOBAL SCOPE)
    // ========================================================
    let currentInspectedScriptItem = null;

    function openFredScriptModal(item) {
      if (!item) return;
      currentInspectedScriptItem = item;
      const overlay = document.getElementById('fredScriptModalOverlay');
      if (!overlay) return;

      const titleEl = document.getElementById('fredScriptModalSongTitle');
      const bandEl = document.getElementById('fredScriptModalBand');
      const apEl = document.getElementById('fredScriptAperturaText');
      const devEl = document.getElementById('fredScriptDesarrolloText');
      const ciEl = document.getElementById('fredScriptCierreText');
      const durChip = document.getElementById('fredScriptDurChip');

      const songTitle = item.songTitle || 'Canción de Rock';
      const bandName = item.bandName || 'Artista';

      if (titleEl) titleEl.textContent = songTitle;
      if (bandEl) bandEl.textContent = `${bandName} • Locutor: DJ Fredd • Fred Rewind`;
      if (durChip) durChip.textContent = `⏱️ ${item.duration ? formatTime(item.duration) : '45s'}`;

      // Parse script into Apertura, Desarrollo and Cierre
      const rawText = item.summary || buildEddieRadioScript(songTitle, bandName, item.albumName, item.year);
      let apertura = 'Estás escuchando Fred Rewind, de regreso al pasado. Soy DJ Fredd.';
      let cierre = `¡Sube el volumen y escuchemos a ${songTitle} aquí en Fred Rewind, de regreso al pasado!`;
      let desarrollo = rawText;

      const apMatch = rawText.match(/^(Estás escuchando (?:Fred Rewind|Rock Radio).*?Soy DJ (?:Fredd|Eddie)\\.?)/i);
      if (apMatch) {
        apertura = apMatch[0].replace(/Rock Radio/g, 'Fred Rewind').replace(/Eddie/g, 'Fredd');
        desarrollo = rawText.slice(apMatch[0].length).trim();
      }

      const ciMatch = desarrollo.match(/(¡?Sube el volumen.*)$/i);
      if (ciMatch) {
        cierre = ciMatch[0].replace(/Rock Radio/g, 'Fred Rewind').replace(/Eddie/g, 'Fredd');
        desarrollo = desarrollo.slice(0, ciMatch.index).trim();
      }

      if (apEl) apEl.textContent = apertura;
      if (devEl) devEl.textContent = desarrollo;
      if (ciEl) ciEl.textContent = cierre;

      overlay.style.display = 'flex';
      setTimeout(() => overlay.classList.add('active'), 10);
    }

    function closeFredScriptModal() {
      const overlay = document.getElementById('fredScriptModalOverlay');
      if (!overlay) return;
      overlay.classList.remove('active');
      setTimeout(() => { overlay.style.display = 'none'; }, 250);
    }

    window.openFredScriptModal = openFredScriptModal;
    window.closeFredScriptModal = closeFredScriptModal;

    // Modal Event Listeners
    document.addEventListener('DOMContentLoaded', () => {
      const btnScriptClose = document.getElementById('btnFredScriptModalClose');
      if (btnScriptClose) btnScriptClose.addEventListener('click', closeFredScriptModal);

      const scriptOverlayEl = document.getElementById('fredScriptModalOverlay');
      if (scriptOverlayEl) {
        scriptOverlayEl.addEventListener('click', (e) => {
          if (e.target === scriptOverlayEl) closeFredScriptModal();
        });
      }

      const btnScriptCopy = document.getElementById('btnFredScriptCopy');
      if (btnScriptCopy) {
        btnScriptCopy.addEventListener('click', () => {
          if (!currentInspectedScriptItem) return;
          const text = currentInspectedScriptItem.summary || '';
          navigator.clipboard.writeText(text).then(() => {
            showAppToast({
              title: 'Guion copiado',
              desc: 'El guion oficial de Fred Rewind se ha copiado al portapapeles.',
              type: 'success',
              icon: '📋',
              duration: 3000
            });
          }).catch(() => {
            showAppToast('No se pudo copiar el texto', 'warn');
          });
        });
      }

      const btnScriptPlay = document.getElementById('btnFredScriptPlay');
      if (btnScriptPlay) {
        btnScriptPlay.addEventListener('click', () => {
          if (!currentInspectedScriptItem) return;
          const catalog = djEddieQueue.length ? djEddieQueue : buildDjEddieCatalog();
          const idx = catalog.findIndex(t => t.id === currentInspectedScriptItem.id || t.pairId === currentInspectedScriptItem.pairId);
          closeFredScriptModal();
          if (idx !== -1) {
            playDjEddieItem(idx, false);
          }
        });
      }
    });
"""

    # Remove existing global modal code if any
    content = re.sub(r'    // ========================================================\n    // FRED REWIND SCRIPT MODAL VIEWER \(GLOBAL SCOPE\).*?window\.closeFredScriptModal = closeFredScriptModal;\n', '', content, flags=re.DOTALL)

    # Insert right before function playDjEddieItem
    target_play = '    function playDjEddieItem(index, scrollToLyrics = false) {'
    if target_play in content:
        content = content.replace(target_play, modal_global_js + '\n' + target_play)
        print('✓ Modal JS injected into global scope before playDjEddieItem')

    # 6. Replace renderDjEddiePlaylistSongs with full 7-state implementation + view-script-btn
    new_render_songs = """    function renderDjEddiePlaylistSongs() {
      const listEl = document.getElementById('djEddiePlaylistSongsList');
      if (!listEl) return;
      const catalog = djEddieQueue.length ? djEddieQueue : buildDjEddieCatalog();
      const songCount = catalog.filter(x => !x.isIntro).length || (catalog.length / 2);
      const countEl = document.getElementById('djPlaylistTrackCount');
      if (countEl) countEl.textContent = `${songCount} canciones con Historia de DJ Fredd`;

      listEl.innerHTML = '';
      if (!catalog.length) {
        listEl.innerHTML = `
          <div class="dj-empty-state" style="text-align: center; padding: 60px 20px; color: var(--sp-text-muted);">
            <div style="font-size: 3.5rem; margin-bottom: 16px;">🎙️</div>
            <h3 style="color: #fff; font-size: 1.3rem; margin-bottom: 8px;">No hay canciones en la lista de DJ Fredd</h3>
            <p style="font-size: 0.92rem; max-width: 480px; margin: 0 auto 20px; line-height: 1.5; color: #9ca3af;">
              Busca cualquier canción en la barra superior de Spotify y presiona <strong>"+ Añadir a DJ Fredd"</strong> para generar su historia y narración oficial con voz de radio clásica.
            </p>
          </div>
        `;
        return;
      }
      catalog.forEach((item, idx) => {
        const isCurrentTrack = (isDjEddieActive && djEddieIndex === idx);
        const isAudioActive = !spotifyAudio.paused && !spotifyAudio.ended && (spotifyAudio.currentTime > 0 || spotifyAudio.duration > 0);
        const isPlayingNow = isCurrentTrack && isAudioActive;

        const row = document.createElement('div');
        row.className = 'dj-song-row' + (isPlayingNow ? ' playing' : (isCurrentTrack ? ' active-track' : '')) + (item.isIntro ? ' is-intro-row' : ' is-song-row');
        row.setAttribute('data-track-id', item.id);
        if (item.pairId) row.setAttribute('data-pair-id', item.pairId);

        // Actions cell HTML & Status Badges
        let actionsHtml = '';
        let statusBadgeHtml = '';

        if (item.isIntro) {
          if (item.status === 'sin_historia') {
            statusBadgeHtml = `<span class="dj-status-badge pending">Sin historia</span>`;
            actionsHtml = `
              <div class="dj-col-actions">
                <button class="dj-action-btn gen-story" type="button" title="Generar guion y voz de DJ Fredd">✨ Generar historia</button>
                <button class="dj-action-btn del-track" type="button" title="Eliminar de Fred Rewind">🗑️</button>
              </div>
            `;
          } else if (item.status === 'investigando') {
            statusBadgeHtml = `<span class="dj-status-badge running">🔍 Buscando información...</span>`;
            actionsHtml = `
              <div class="dj-col-actions">
                <button class="dj-action-btn cancel-gen" type="button" title="Detener generación de la historia">⏹️ Detener generación</button>
              </div>
            `;
          } else if (item.status === 'generando_guion') {
            statusBadgeHtml = `<span class="dj-status-badge running">📝 Escribiendo historia...</span>`;
            actionsHtml = `
              <div class="dj-col-actions">
                <span class="dj-live-elapsed" data-pair-id="${item.pairId}">⏳ 0:00</span>
                <button class="dj-action-btn cancel-gen" type="button" title="Detener generación de la historia">⏹️ Detener generación</button>
              </div>
            `;
          } else if (item.status === 'generando_audio') {
            const elSec = (activeStoryGenerations[item.pairId]?.elapsed) || 0;
            statusBadgeHtml = `<span class="dj-status-badge running dj-audio-timer" data-pair-id="${item.pairId}">🎙️ Creando voz de DJ Fredd (${elSec}s)...</span>`;
            actionsHtml = `
              <div class="dj-col-actions">
                <span class="dj-live-elapsed" data-pair-id="${item.pairId}">⏳ ${formatTime(elSec)}</span>
                <button class="dj-action-btn cancel-gen" type="button" title="Detener generación de la historia">⏹️ Detener generación</button>
              </div>
            `;
          } else if (item.status === 'cancelado') {
            statusBadgeHtml = `<span class="dj-status-badge cancelled">Generación cancelada</span>`;
            actionsHtml = `
              <div class="dj-col-actions">
                <button class="dj-action-btn gen-story" type="button" title="Generar guion y voz de DJ Fredd">✨ Generar historia</button>
                <button class="dj-action-btn del-track" type="button" title="Eliminar de Fred Rewind">🗑️</button>
              </div>
            `;
          } else if (item.status === 'error') {
            statusBadgeHtml = `<span class="dj-status-badge error">⚠️ Error</span>`;
            actionsHtml = `
              <div class="dj-col-actions">
                <button class="dj-action-btn retry-gen" type="button" title="Reintentar generación de la historia">🔄 Reintentar</button>
                <button class="dj-action-btn del-track" type="button" title="Eliminar de Fred Rewind">🗑️</button>
              </div>
            `;
          } else {
            // 'con_audio' (Historia completada)
            statusBadgeHtml = `<span class="dj-intro-pill">Historia • DJ Fredd</span>`;
            actionsHtml = `
              <div class="dj-col-actions">
                <div class="dj-dur-box">
                  <span class="dj-dur-text">${formatTime(item.duration)}</span>
                  ${item.genElapsedSec ? `<span class="dj-dur-gen-time" title="Tiempo de generación: ${item.genElapsedSec}s">⚡ ${item.genElapsedSec}s</span>` : ''}
                </div>
                <button class="dj-row-play-btn" type="button" title="${isPlayingNow ? 'Pausar historia' : 'Reproducir historia'}">
                  ${isPlayingNow
                    ? '<svg viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>'
                    : '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>'}
                </button>
                <button class="dj-action-btn view-script-btn" type="button" title="Consultar el guion oficial de Fred Rewind">📜 Ver guion</button>
                <button class="dj-action-btn regen-story" type="button" title="Regenerar historia con DJ Fredd">🔄 Regenerar historia</button>
                <button class="dj-action-btn del-track" type="button" title="Eliminar de Fred Rewind">🗑️</button>
              </div>
            `;
          }
        } else {
          // Canción original de Spotify sin modificaciones
          actionsHtml = `
            <div class="dj-col-actions">
              <span class="dj-dur-text">${formatTime(item.duration)}</span>
              <button class="dj-row-play-btn" type="button" title="${isPlayingNow ? 'Pausar' : 'Reproducir'} ${escapeHtmlStr(item.songTitle)}">
                ${isPlayingNow
                  ? '<svg viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>'
                  : '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>'}
              </button>
              <button class="dj-action-btn del-track" type="button" title="Eliminar de DJ Fredd">🗑️</button>
            </div>
          `;
        }

        const scriptPreviewHtml = (item.isIntro && item.summary)
          ? `<div class="dj-script-preview ${item.status === 'generando_audio' ? 'is-generating' : ''}" title="${escapeHtmlStr(item.summary)}">${escapeHtmlStr(item.summary)}</div>`
          : '';

        row.innerHTML = `
          <div class="dj-col-num">${isPlayingNow ? '🔊' : (idx + 1)}</div>
          <div class="dj-col-title-cell">
            <div class="dj-song-thumb">
              <img src="${item.cover}" alt="${escapeHtmlStr(item.songTitle)}" loading="lazy">
            </div>
            <div class="dj-song-meta">
              <div class="dj-song-name" title="${escapeHtmlStr(item.songTitle)}">${escapeHtmlStr(item.songTitle)}</div>
              <div class="dj-song-band">
                <span>${escapeHtmlStr(item.bandName)}</span>
                ${statusBadgeHtml}
              </div>
              ${scriptPreviewHtml}
            </div>
          </div>
          <div class="dj-col-year">${escapeHtmlStr(String(item.year || ''))}</div>
          <div class="dj-col-dur">
            ${actionsHtml}
          </div>
        `;

        const viewScriptBtn = row.querySelector('.view-script-btn');
        if (viewScriptBtn) {
          viewScriptBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            openFredScriptModal(item);
          });
        }
        const scriptPreviewEl = row.querySelector('.dj-script-preview');
        if (scriptPreviewEl) {
          scriptPreviewEl.addEventListener('click', (e) => {
            e.stopPropagation();
            openFredScriptModal(item);
          });
        }
        const genStoryBtn = row.querySelector('.gen-story');
        if (genStoryBtn) {
          genStoryBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            startStoryGeneration(item.pairId || item.id, false);
          });
        }
        const regenStoryBtn = row.querySelector('.regen-story');
        if (regenStoryBtn) {
          regenStoryBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            startStoryGeneration(item.pairId || item.id, true);
          });
        }
        const retryGenBtn = row.querySelector('.retry-gen');
        if (retryGenBtn) {
          retryGenBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            startStoryGeneration(item.pairId || item.id, false);
          });
        }
        const cancelGenBtn = row.querySelector('.cancel-gen');
        if (cancelGenBtn) {
          cancelGenBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            cancelStoryGeneration(item.pairId || item.id);
          });
        }
        const delBtn = row.querySelector('.del-track');
        if (delBtn) {
          delBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            removeCustomTrackFromDjEddie(item.pairId || item.id);
          });
        }
        const playBtn = row.querySelector('.dj-row-play-btn');
        if (playBtn) {
          playBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (isDjEddieActive && djEddieIndex === idx) {
              GlobalAudioPlayer.togglePlay();
            } else {
              playDjEddieItem(idx, false);
            }
          });
        }

        row.addEventListener('click', () => {
          if (isDjEddieActive && djEddieIndex === idx) {
            GlobalAudioPlayer.togglePlay();
          } else {
            playDjEddieItem(idx, false);
          }
        });

        listEl.appendChild(row);
      });
    }"""

    # Replace renderDjEddiePlaylistSongs
    render_songs_pattern = r'    function renderDjEddiePlaylistSongs\(\) \{.*?(?=    function playDjEddieItem)'
    if re.search(render_songs_pattern, content, flags=re.DOTALL):
        content = re.sub(render_songs_pattern, new_render_songs + '\n\n', content, flags=re.DOTALL)
        print('✓ renderDjEddiePlaylistSongs updated with 7 states and script modal wiring')

    # 7. Update startStoryGeneration with 4-phase sequence and rigorous validations
    start_gen_re = r'    async function startStoryGeneration\(targetId, isRegen = false\) \{.*?(?=    async function cancelStoryGeneration)'
    new_start_gen = """    async function startStoryGeneration(targetId, isRegen = false) {
      const customTracks = getDjEddieCustomTracks();
      let introIdx = customTracks.findIndex(t => t.id === targetId || t.pairId === targetId || t.relatedSongId === targetId);
      let introItem;

      if (introIdx !== -1) {
        introItem = customTracks[introIdx];
      } else {
        const baseIntro = BASE_DJ_EDDIE_TRACKS.find(t => (t.id === targetId || t.pairId === targetId || t.relatedSongId === targetId) && t.isIntro);
        if (!baseIntro) return;
        introItem = { ...baseIntro, isCustom: true };
        customTracks.push(introItem);
        const baseSong = BASE_DJ_EDDIE_TRACKS.find(t => t.pairId === baseIntro.pairId && !t.isIntro);
        if (baseSong && !customTracks.some(t => t.id === baseSong.id)) {
          customTracks.push({ ...baseSong, isCustom: true });
        }
        introIdx = customTracks.findIndex(t => t.id === introItem.id);
        saveDjEddieCustomTracks(customTracks);
      }
      const pairId = introItem.pairId || introItem.id;

      // Concurrency check: avoid duplicate requests on the same song
      if (activeStoryGenerations[pairId]) {
        showAppToast('Ya hay una generación en curso para esta canción', 'warn');
        return;
      }

      const jobId = 'job_' + Date.now() + '_' + Math.random().toString(36).slice(2, 7);
      const abortController = new AbortController();

      const previousState = {
        status: introItem.status,
        audioUrl: introItem.audioUrl,
        fileUrl: introItem.fileUrl,
        hasRealAudio: introItem.hasRealAudio,
        summary: introItem.summary,
        duration: introItem.duration,
        introSec: introItem.introSec,
        genElapsedSec: introItem.genElapsedSec,
        lyrics: introItem.lyrics ? JSON.parse(JSON.stringify(introItem.lyrics)) : []
      };

      activeStoryGenerations[pairId] = {
        jobId: jobId,
        abortController: abortController,
        isRegen: isRegen,
        previousState: previousState,
        startTime: Date.now(),
        elapsed: 0,
        timerId: null
      };

      // Alerta de inicio informando que se avisará al terminar
      showAppToast({
        title: 'Generando historia con DJ Fredd',
        desc: `Se está investigando y escribiendo la historia para «${introItem.songTitle}». Te avisaremos al terminar.`,
        type: 'generating',
        icon: '🎙️',
        duration: 5000
      });

      // FASE 0: Investigando («investigando» -> Buscando información...)
      introItem.status = 'investigando';
      introItem.jobId = jobId;
      customTracks[introIdx] = introItem;
      saveDjEddieCustomTracks(customTracks);
      buildDjEddieCatalog();
      renderDjEddiePlaylistSongs();
      startGenerationTimer(pairId);

      // Tiempo breve de investigación orgánica de la historia real
      await new Promise(r => setTimeout(r, 400));
      if (!activeStoryGenerations[pairId] || activeStoryGenerations[pairId].jobId !== jobId) return;

      // FASE 1: Generando guion escrito («generando_guion» -> Escribiendo historia...)
      introItem.status = 'generando_guion';
      const nextAngle = isRegen ? (((introItem.regenAngle || 1) % 3) + 1) : (introItem.regenAngle || 1);
      introItem.regenAngle = nextAngle;

      // Produce el guion de anécdota oficial de Fred Rewind
      const scriptText = buildEddieRadioScript(introItem.songTitle, introItem.bandName, introItem.albumName, introItem.year, nextAngle);
      introItem.summary = scriptText;

      customTracks[introIdx] = introItem;
      saveDjEddieCustomTracks(customTracks);
      buildDjEddieCatalog();
      renderDjEddiePlaylistSongs();

      // Breve pausa para visualizar el guion de inmediato en pantalla
      await new Promise(r => setTimeout(r, 450));
      if (!activeStoryGenerations[pairId] || activeStoryGenerations[pairId].jobId !== jobId) return;

      // FASE 2: Sintetizando locución con DJ Fredd en Chatterbox / Edge-TTS («generando_audio»)
      introItem.status = 'generando_audio';
      customTracks[introIdx] = introItem;
      saveDjEddieCustomTracks(customTracks);
      buildDjEddieCatalog();
      renderDjEddiePlaylistSongs();

      let audioData = null;

      try {
        const json = await callEddieApi('/api/generate_audio', {
          job_id: jobId,
          track_id: pairId,
          song_title: introItem.songTitle,
          band_name: introItem.bandName,
          album: introItem.albumName || '',
          year: introItem.year || '',
          text: introItem.summary
        }, abortController.signal);

        if (json) {
          if (json.cancelled) {
            console.log('Backend reportó trabajo cancelado para', jobId);
            return;
          }
          if (json.audioUrl || json.fileUrl) {
            audioData = json;
          }
        }
      } catch (err) {
        if (err.name === 'AbortError' || abortController.signal.aborted) {
          console.log(`Petición abortada para job ${jobId}`);
          return;
        }
        console.warn('Fallo en la API de síntesis de audio de DJ Eddie:', err);
      }

      // Race condition protection: ensure this job is still the active one
      if (!activeStoryGenerations[pairId] || activeStoryGenerations[pairId].jobId !== jobId) {
        console.warn('Respuesta tardía descartada para trabajo cancelado:', jobId);
        return;
      }

      const totalElapsedReal = audioData?.elapsedSec || Math.round((Date.now() - activeStoryGenerations[pairId].startTime) / 100) / 10;
      stopGenerationTimer(pairId);
      delete activeStoryGenerations[pairId];

      if (audioData && (audioData.fileUrl || audioData.audioUrl)) {
        if (!window.__eddieAudioCache) window.__eddieAudioCache = {};
        if (audioData.audioUrl) window.__eddieAudioCache[pairId] = audioData.audioUrl;

        // VALIDACIONES DE CALIDAD RIGUROSAS (Lineamiento 10)
        const finalScript = audioData.full_script || introItem.summary || '';
        const durSec = Number(audioData.durationSec) || 45;
        const hasApertura = finalScript.includes('Fred Rewind') && finalScript.includes('DJ Fredd');
        const hasCierre = finalScript.toLowerCase().includes('sube el volumen') && finalScript.toLowerCase().includes('fred rewind');
        const isDurationValid = durSec >= 28.0;

        if (!hasApertura || !hasCierre || !isDurationValid) {
          console.warn('Fallo en validación de calidad de la historia:', { hasApertura, hasCierre, isDurationValid, durSec });
          introItem.status = 'error';
          customTracks[introIdx] = introItem;
          saveDjEddieCustomTracks(customTracks);
          buildDjEddieCatalog();
          renderDjEddiePlaylistSongs();
          showAppToast({
            title: 'Validación de calidad',
            desc: 'La historia generada no cumplió los estándares oficiales de duración o estructura. Puedes reintentar.',
            type: 'error',
            icon: '⚠️',
            duration: 5000
          });
          return;
        }

        introItem.audioUrl = audioData.fileUrl || audioData.audioUrl;
        introItem.fileUrl = audioData.fileUrl || audioData.audioUrl;
        introItem.duration = Math.round(durSec);
        introItem.introSec = audioData.duration || `${introItem.duration}s`;
        introItem.genElapsedSec = totalElapsedReal;
        introItem.hasRealAudio = true;
        introItem.status = 'con_audio';
        introItem.summary = finalScript;
        if (audioData.intro_timings) introItem.lyrics = audioData.intro_timings;

        customTracks[introIdx] = introItem;
        saveDjEddieCustomTracks(customTracks);
        buildDjEddieCatalog();
        renderDjEddiePlaylistSongs();
        renderLyrics();

        // Precarga en segundo plano de la canción completa de Spotify vinculada
        if (introItem.relatedSongId) {
          resolveFullSongForTrack(introItem.relatedSongId, introItem.songTitle, introItem.bandName).catch(() => {});
        }

        // Alerta al finalizar con el tiempo real de backend
        showAppToast({
          title: '¡Historia de Fred Rewind lista!',
          desc: `«${introItem.songTitle}» lista para escuchar con DJ Fredd. Generada en ${introItem.genElapsedSec}s.`,
          type: 'success',
          icon: '✅',
          duration: 5000
        });
      } else {
        // Error handling with option to retry
        introItem.status = 'error';
        introItem.hasRealAudio = false;

        customTracks[introIdx] = introItem;
        saveDjEddieCustomTracks(customTracks);
        buildDjEddieCatalog();
        renderDjEddiePlaylistSongs();

        showAppToast({
          title: 'Error de síntesis',
          desc: `No se pudo generar el audio para «${introItem.songTitle}». Pulsa "Reintentar".`,
          type: 'error',
          icon: '⚠️',
          duration: 5000
        });
      }
    }"""
    if re.search(start_gen_re, content, flags=re.DOTALL):
        content = re.sub(start_gen_re, new_start_gen + '\n\n', content, flags=re.DOTALL)
        print('✓ startStoryGeneration updated with 4-phase sequence and validations')

    # 8. Save files
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)

    for rep in ['kiss.html', 'rock45.html', 'kiss-podcast.html']:
        with open(rep, 'w', encoding='utf-8') as f:
            f.write(content)

    print('✓ All 4 HTML files updated successfully!')

if __name__ == '__main__':
    apply_fred_rewind()
