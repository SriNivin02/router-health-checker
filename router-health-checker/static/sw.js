// Router Health Checker - Service Worker (Offline-First Static Shell)
const CACHE_NAME = 'rhc-shell-v1';
const STATIC_ASSETS = [
  '/',
  '/static/css/theme.css',
  '/static/js/app.js',
  '/static/js/i18n.js',
  '/static/js/voice.js',
  '/static/js/chart_helper.js',
  '/static/vendor/chart.umd.min.js',
  '/static/manifest.json',
  '/static/locales/en.json',
  '/static/locales/hi.json',
  '/static/locales/ta.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  // NEVER cache API requests or websocket/streaming endpoints
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // Cache-first for static shell assets
  event.respondWith(
    caches.match(event.request).then((cached) => {
      return cached || fetch(event.request);
    })
  );
});
