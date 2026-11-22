# Reporte Técnico y Editorial de Calidad
## GLAM ROCK: Cuando el rock conquistó los 80 — TrackStories

### 1. Estado de Producción y Entregables
- **Investigación y cronología verificada:** `research/timeline_and_sources.md` (`COMPLETADO`)
- **Curaduría musical ponderada (9 canciones):** `research/song_selection.md` (`COMPLETADO`)
- **Guion maestro (10 capítulos / 13 escenas):** `scripts/master_script.md` (`COMPLETADO`)
- **Portada editorial:** `artwork/glam_rock_80s_cover.jpg` (`COMPLETADO`)
- **Narración Fred (13 escenas, Fish Audio `drama-3`):** `narration/ch01_s01.mp3` … `narration/ch10_s01.mp3` (`COMPLETADO`)
- **Música instrumental original estéreo (13 camas, 48 kHz):** `original-music/bed_*.wav` (`COMPLETADO`)
- **Mezcla y masterización por escena (`-16 LUFS / -1 dBTP`):** `mixes/ch01_s01_mix.mp3` … `mixes/ch10_s01_mix.mp3` (`COMPLETADO`)
- **Archivo maestro continuo (Narración + Score Original):** `masters/glam_rock_80s_narration_master.mp3` (`644.62 s` / `10:45`, `COMPLETADO`)
- **Manifiesto de reproducción:** `manifest.json` (`COMPLETADO`)
- **Integración en TrackStories:** Tarjeta destacada + reproductor con capítulos navegables, barra de progreso, indicador Fred vs. Canción y reanudación en `localStorage` (`index.html`, `trackstories.html`, `trackstories-player.html`, `trackstories-podcast.html`, `COMPLETADO`).

### 2. Auditoría de Audio
- Se auditaron de oído los masters finales `mixes/ch01_s01_mix.mp3` (Apertura — Sunset Strip) y `mixes/ch10_s01_mix.mp3` (Cierre — *TrackStories. La música tiene memoria*): voz cálida y natural, cama instrumental equilibrada sin competir con la locución y transiciones limpias.
- Las 11 escenas restantes fueron validadas mediante `ffprobe` (duración y tasa de muestreo 48 kHz) y normalización automática `loudnorm=I=-16:TP=-1.0:LRA=11`.

### 3. Registro Honesto de Licencias y Duración
- **Canciones comerciales (9 temas, `2.129 s` / `35:29`):** Registradas como `REQUIERE_LICENCIA_LOCAL_USA_SPOTIFY`. Por cumplimiento estricto de derechos de autor y términos de servicio, no se descargaron ni mezclaron grabaciones comerciales protegidas dentro del archivo MP3 maestro. En TrackStories, el reproductor documental dispara automáticamente cada canción mediante **Spotify Web Playback SDK** entre los capítulos narrados.
- **Duración medida real:** `644.62 s` de narración + score original + `2.129 s` de las 9 canciones = **`2.774,05 s` (`46:14`)** de experiencia continua sin relleno artificial. Si deseas extenderla exactamente a `60:00` (`3.600 s`), el pipeline resumible (`build_documentary.py`) permite añadir 3 canciones licenciadas adicionales o ampliar las escenas narradas y volver a ejecutar solo los segmentos nuevos.
