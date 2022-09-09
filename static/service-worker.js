//--------------------------------------------------------------------------
// You can find dozens of practical, detailed, and working examples of 
// service worker usage on https://github.com/mozilla/serviceworker-cookbook
//--------------------------------------------------------------------------

// Cache version
var CACHE_VERSION = '1.0'

// Cache name
var CACHE_NAME = 'narwhal-cache-v' + CACHE_VERSION;

// Files
// var REQUIRED_ROUTES = [
//     '../templates/common/register.html',
//     '../templates/common/login.html',
//     '../templates/common/education-edit.html',
//     '../templates/common/experience-edit.html',
//     '../templates/common/contacts.html',
//     '../templates/common/construction.html',
//     '../templates/common/notifications.html',
//     '../templates/common/password.html',
//     '../templates/common/project-details.html',
//     '../templates/common/project-list.html',
//     '../templates/common/talent-list.html',
//     '../templates/common/terms.html',
//     'https://narwhal-app.com/static/assets/js/lib/bootstrap.min.js'
// ];

var REQUIRED_ROUTES = [
    'https://narwhal-app.com/home',
    'https://narwhal-app.com/profile-details',
    'https://narwhal-app.com/talent',
    'https://narwhal-app.com/projects',
    'https://narwhal-app.com/notifications,',
    'https://narwhal-app.com/contacts',
    // '/static/assets/js/lib/bootstrap.min.js',
    // 'https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js',
    // 'https://unpkg.com/ionicons@5.5.2/dist/ionicons/ionicons.js',
    // '/static/assets/js/plugins/splide/splide.min.js',
    // '/static/assets/js/plugins/progressbar-js/progressbar.min.js',
    // 'https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js',
    // '/static/assets/css/inc/bootstrap/bootstrap.min.css',
    // '/static/assets/css/inc/splide/splide.min.css',
]

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

// On notification Push, Create Notification using event data
self.addEventListener("push", function(event) {
    console.log("[Service Worker] Push Received.");

    let data = {};
    if (event.data) {
        data = event.data.json();
        // console.log("[Service Worker] Push had this title:", data.title)
        // console.log("[Service Worker] Push had this body:", data.body)
    }

    var title = data.title
    var body = data.body;
    var icon = "../static/assets/img/sample/alerts/icon.png";
    var badge = "../static/assets/img/sample/alerts/badge.png";
    var tag = 'simple-push-demo-notification-tag';

    event.waitUntil(
        self.registration.showNotification(title, {
            body: body,
            icon: icon,
            vibrate: [200, 100, 200, 100, 200, 100, 200],
            badge: badge,
            tag: tag
        })
    );

});

// On Notification Click, Go to URL
self.addEventListener("notificationclick", function(event) {
    console.log("[Service Worker] Notification click Received.");
    event.notification.close();
    // event.waitUntil(clients.openWindow('http://0.0.0.0:5000/notifications'));
    event.waitUntil(clients.openWindow('https://narwhal-app.com/notifications'));


    // event.waitUntil(clients.openWindow('http://' + document.domain + ':' + location.port + '/notifications'));
});