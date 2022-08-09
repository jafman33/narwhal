//--------------------------------------------------------------------------
// You can find dozens of practical, detailed, and working examples of 
// service worker usage on https://github.com/mozilla/serviceworker-cookbook
//--------------------------------------------------------------------------

// Cache version
var CACHE_VERSION = '2.9'

// Cache name
var CACHE_NAME = '3l-ranch-cache-v' + CACHE_VERSION;

// Files
var REQUIRED_ROUTES = [
    // '/home',
    // '/my-lessons',
    // '/how-to-play',
    // '/profile'
];

self.addEventListener('install', function(event) {
    // Perform install step:  loading each required file into cache
    event.waitUntil(
        caches.open(CACHE_NAME)
        .then(function(cache) {
            // Add all offline dependencies to the cache
            return cache.addAll(REQUIRED_ROUTES);
        })
        .then(function() {
            return self.skipWaiting();
        })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
        .then(function(response) {
            // Cache hit - return the response from the cached version
            if (response) {
                return response;
            }
            // Not in cache - return the result from the live server
            // `fetch` is essentially a "fallback"
            return fetch(event.request);
        })
    );
});

self.addEventListener('activate', function(event) {
    // Calling claim() to force a "controllerchange" event on navigator.serviceWorker
    event.waitUntil(self.clients.claim());
});