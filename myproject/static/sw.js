// myproject/static/sw.js

const CACHE_NAME = 'news-cache-v1';
const urlsToCache = [
  '/', // The homepage
  '/static/css/base.css', // Or whatever your main stylesheet is
  // Add other critical static assets here
];

self.addEventListener('install', event => {
  // Perform installation steps
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }
        // No cache hit - fetch from network
        return fetch(event.request).catch(() => {
            // Fallback for offline pages that aren't in the cache (like a specific detail page)
            // You might want to return an 'Offline' HTML page here
            console.log('Offline fallback active');
        });
      })
  );
});