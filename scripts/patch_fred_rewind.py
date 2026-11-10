#!/usr/bin/env python3
"""
Patch index.html, kiss.html, rock45.html, kiss-podcast.html with precision
"""
import sys

def patch():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Title
    import re
    content = re.sub(r'<title>.*?</title>', '<title>Fred Rewind — La música tiene memoria | Con DJ Fredd</title>', content)

    # 2. Modal CSS
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
        print('✓ Modal CSS added')

    # 3. Modal HTML
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
        print('✓ Modal HTML added')

    # 4. Update the con_audio branch in renderDjEddiePlaylistSongs to include .view-script-btn
    old_con_audio_block = """          } else {
            // 'con_audio' (o historias estándar del catálogo)
            statusBadgeHtml = `<span class="dj-intro-pill">Historia</span>`;
            actionsHtml = `
              <div class="dj-col-actions">
                <div class="dj-dur-box">
                  <span class="dj-dur-text">${formatTime(item.duration)}</span>
                  ${item.genElapsedSec ? `<span class="dj-dur-gen-time" title="Tiempo real de generación en backend: ${item.genElapsedSec}s">⚡ ${item.genElapsedSec}s</span>` : ''}
                </div>
                <button class="dj-row-play-btn" type="button" title="${isPlayingNow ? 'Pausar' : 'Escuchar Historia'}">
                  ${isPlayingNow
                    ? '<svg viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>'
                    : '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>'}
                </button>
                <button class="dj-action-btn regen-story" type="button" title="Regenerar historia con DJ Fredd">🔄 Regenerar</button>
                <button class="dj-action-btn del-track" type="button" title="Eliminar de DJ Fredd">🗑️</button>
              </div>
            `;
          }"""

    new_con_audio_block = """          } else {
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
          }"""

    if old_con_audio_block in content:
        content = content.replace(old_con_audio_block, new_con_audio_block)
        print('✓ Updated con_audio actionsHtml with .view-script-btn')
    else:
        print('Warning: old_con_audio_block not matched')

    # 5. Wire viewScriptBtn and scriptPreviewEl inside renderDjEddiePlaylistSongs
    old_gen_btn_wire = """        const genStoryBtn = row.querySelector('.gen-story');
        if (genStoryBtn) {
          genStoryBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            startStoryGeneration(item.pairId || item.id, false);
          });
        }"""

    new_gen_btn_wire = """        const viewScriptBtn = row.querySelector('.view-script-btn');
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
        }"""

    if old_gen_btn_wire in content:
        content = content.replace(old_gen_btn_wire, new_gen_btn_wire)
        print('✓ Wired viewScriptBtn and scriptPreviewEl')
    else:
        print('Warning: old_gen_btn_wire not matched')

    # 6. Global Modal Functions before function playDjEddieItem
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
    target_play = '    function playDjEddieItem(index, scrollToLyrics = false) {'
    if target_play in content and 'function openFredScriptModal' not in content:
        content = content.replace(target_play, modal_global_js + '\n' + target_play)
        print('✓ Injected modal_global_js right before playDjEddieItem')

    # 7. Update buildEddieRadioScript to use official template
    old_script_builder = """      const apertura = `Estás escuchando Rock Radio, la emisora que te lleva de regreso al pasado con los grandes clásicos que marcaron tu vida. Te acompaña DJ Eddie`;
      const cierre = `¡Sube el volumen y siente el rock aquí en Rock Radio!`;
      return `${apertura}. ${devStory} ${cierre}`;"""

    new_script_builder = """      const apertura = "Estás escuchando Fred Rewind, de regreso al pasado. Soy DJ Fredd.";
      const cierre = `¡Sube el volumen y escuchemos a ${songTitle} aquí en Fred Rewind, de regreso al pasado!`;
      return `${apertura} ${devStory} ${cierre}`;"""

    if old_script_builder in content:
        content = content.replace(old_script_builder, new_script_builder)
        print('✓ Updated buildEddieRadioScript template')

    # 8. Update quality validation in startStoryGeneration
    old_validation = """        introItem.audioUrl = audioData.fileUrl || audioData.audioUrl;
        introItem.fileUrl = audioData.fileUrl || audioData.audioUrl;
        introItem.duration = Math.round(Number(audioData.durationSec) || 45);
        introItem.introSec = audioData.duration || `${introItem.duration}s`;
        introItem.genElapsedSec = totalElapsedReal;
        introItem.hasRealAudio = true;
        introItem.status = 'con_audio';
        if (audioData.full_script) introItem.summary = audioData.full_script;
        if (audioData.intro_timings) introItem.lyrics = audioData.intro_timings;

        customTracks[introIdx] = introItem;
        saveDjEddieCustomTracks(customTracks);
        buildDjEddieCatalog();
        renderDjEddiePlaylistSongs();
        renderLyrics();"""

    new_validation = """        // VALIDACIONES DE CALIDAD RIGUROSAS (Lineamiento 10)
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
        renderLyrics();"""

    if old_validation in content:
        content = content.replace(old_validation, new_validation)
        print('✓ Updated Quality Validation block in startStoryGeneration')

    # Save to index.html and replicas
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)

    for rep in ['kiss.html', 'rock45.html', 'kiss-podcast.html']:
        with open(rep, 'w', encoding='utf-8') as f:
            f.write(content)

    print('✓ Successfully patched index.html and all replicas!')

if __name__ == '__main__':
    patch()
