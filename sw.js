// Rock Radio — Fred Rewind Service Worker (PWA)
const CACHE_NAME = 'rockradio-pwa-v1';

const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  '/manifest.json',
  '/favicon.ico',
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
      // Use individual caching so missing non-critical assets don't fail install
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

// Activate Event: clean up obsolete caches and claim clients immediately
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            console.log('[SW] Clearing old cache:', name);
            return caches.delete(name);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event
self.addEventListener('fetch', (event) => {
  const req = event.request;

  // Only handle GET requests
  if (req.method !== 'GET') {
    return;
  }

  const url = new URL(req.url);

  // 1. Audio files & range requests: pass through directly to network
  // Streaming audio with HTTP 206 Partial Content should not be intercepted
  if (
    url.pathname.endsWith('.mp3') ||
    url.pathname.includes('/audio/') ||
    req.headers.has('range')
  ) {
    return;
  }

  // 2. Navigation requests (HTML pages): Network-first with Cache fallback
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
          return caches.match('/index.html').then((cachedHtml) => {
            return cachedHtml || caches.match('/');
          });
        })
    );
    return;
  }

  // 3. Static assets & same-origin requests: Stale-While-Revalidate
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

  // 4. External resources (Google Fonts, CDN images): Cache-first with network fallback
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
    return;
  }
});

// Listen for message events (e.g. update prompts)
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
