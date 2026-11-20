# 🎸 Rock Radio — Fred Rewind

Plataforma interactiva de historias musicales en 45 segundos con diseño estilo Spotify Desktop. Conecta la historia del Rock Clásico, Hard Rock y Heavy Metal con narración de **DJ Fred** (*"De vuelta al pasado"*) antes de cada canción original completa.

🌐 **Sitio Web:** [https://www.trackstories.space](https://www.trackstories.space)

---

## ⚡ Características Principales

- **Interfaz Estilo Spotify Desktop & PWA:** Reproductor unificado en barra inferior, barra lateral de navegación, estanterías dinámicas de Spotify, vista de artista y panel de historia sincronizada.
- **Fred Rewind (DJ Fred):** Narración en 3 párrafos con pausas instrumentales de 3 segundos, música de fondo continua con auto-ducking (-14 dB) y cierre progresivo de hasta 45 segundos.
- **Integración con Spotify Web API & SDK (OAuth PKCE):** Búsqueda en el catálogo de Spotify, playlists del usuario, canciones favoritas y reproducción de pistas originales después de cada historia.
- **Generación con IA & Fish Audio:** Investigación de anécdotas verificables con OpenAI (`gpt-4o-mini`) y síntesis de voz de DJ Fred con Fish Audio desde [`scripts/generate_dj_fred_track.py`](scripts/generate_dj_fred_track.py).
- **Discografía Real & Carátulas Oficiales:** Portadas auténticas de álbumes e integrantes con fotografías reales.

---

## 🛠️ Tecnologías

- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Service Worker PWA.
- **Backend / Generación:** Node.js serverless ([`api/generate_story_text.js`](api/generate_story_text.js)), Python + FFmpeg + Fish Audio + OpenAI ([`scripts/generate_dj_fred_track.py`](scripts/generate_dj_fred_track.py)).
- **Hosting & CDN:** Vercel.
