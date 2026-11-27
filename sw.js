// TrackStories Service Worker (PWA + Offline Audio Cache with HTTP Range support)
const CACHE_NAME = 'trackstories-pwa-v24';
const OFFLINE_CACHE = 'trackstories-offline-v1';

const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  '/favicon.ico',
  '/icons/favicon.png',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/icons/icon-180.png',
  '/icons/icon-maskable-192.png',
  '/icons/icon-maskable-512.png'
];

// Install Event: cache core app shell assets
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return Promise.allSettled(
        PRECACHE_ASSETS.map((url) =>
          cache.add(url).catch((err) => {
            console.warn('[SW] Precache failed for:', url, err);
          })
        )
      );
    })
  );
});

// Activate Event: clean up obsolete app caches while preserving OFFLINE_CACHE
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME && name !== OFFLINE_CACHE) {
            return caches.delete(name);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Serve cached audio with proper 206 Partial Content when browser sends a Range header
async function serveCachedAudio(req) {
  const offlineCache = await caches.open(OFFLINE_CACHE);
  const cached = await offlineCache.match(req.url, { ignoreSearch: false });
  if (!cached) return null;

  const rangeHeader = req.headers.get('range');
  if (!rangeHeader) return cached;

  const buf = await cached.arrayBuffer();
  const total = buf.byteLength;
  const match = /bytes=(\d+)-(\d*)/.exec(rangeHeader);
  if (!match) return cached;

  const start = Number(match[1]);
  const end = match[2] ? Math.min(Number(match[2]), total - 1) : total - 1;
  if (start >= total || start > end) {
    return new Response(null, {
      status: 416,
      headers: { 'Content-Range': `bytes */${total}` }
    });
  }

  const chunk = buf.slice(start, end + 1);
  return new Response(chunk, {
    status: 206,
    statusText: 'Partial Content',
    headers: {
      'Content-Type': cached.headers.get('Content-Type') || 'audio/mpeg',
      'Content-Range': `bytes ${start}-${end}/${total}`,
      'Accept-Ranges': 'bytes',
      'Content-Length': String(chunk.byteLength)
    }
  });
}

// Fetch Event
self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Never intercept backend API calls
  if (url.pathname.startsWith('/api/')) {
    return;
  }

  // Audio & offline media: check OFFLINE_CACHE first (with Range support), fallback to network
  if (
    url.origin === self.location.origin &&
    (url.pathname.endsWith('.mp3') || url.pathname.includes('/audio/') || url.pathname.includes('/specials/'))
  ) {
    event.respondWith(
      serveCachedAudio(req).then((cachedResp) => cachedResp || fetch(req))
    );
    return;
  }

  // Navigation requests (HTML pages): Network-first with Cache fallback
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((networkResp) => {
          if (networkResp && networkResp.status === 200) {
            const respClone = networkResp.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, respClone));
          }
          return networkResp;
        })
        .catch(() => {
          return caches.match('/index.html').then((cachedHtml) => cachedHtml || caches.match('/'));
        })
    );
    return;
  }

  // Static assets & same-origin requests: check OFFLINE_CACHE + CACHE_NAME
  if (url.origin === self.location.origin) {
    event.respondWith(
      caches.match(req).then((cachedResp) => {
        const fetchPromise = fetch(req)
          .then((networkResp) => {
            if (networkResp && networkResp.status === 200) {
              const respClone = networkResp.clone();
              caches.open(CACHE_NAME).then((cache) => cache.put(req, respClone));
            }
            return networkResp;
          })
          .catch(() => cachedResp);

        return cachedResp || fetchPromise;
      })
    );
    return;
  }

  // External Google Fonts: Cache-first with network fallback
  if (url.hostname.includes('googleapis.com') || url.hostname.includes('gstatic.com')) {
    event.respondWith(
      caches.match(req).then((cachedResp) => {
        if (cachedResp) return cachedResp;
        return fetch(req).then((networkResp) => {
          if (networkResp && networkResp.status === 200) {
            const respClone = networkResp.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, respClone));
          }
          return networkResp;
        }).catch(() => cachedResp);
      })
    );
  }
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
