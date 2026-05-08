const CACHE_NAME = 'rafvalyn-v3';
const OFFLINE_PAGE = '/offline';

// Asset yang di-cache saat install
const PRECACHE_ASSETS = [
    '/',
    '/home',
    '/wisata',
    '/shop/products',
    '/static/manifest.json',
    OFFLINE_PAGE
];

// ===== INSTALL =====
self.addEventListener('install', event => {
    console.log('[SW] Installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return Promise.allSettled(
                    PRECACHE_ASSETS.map(url =>
                        cache.add(url).catch(e => console.warn('[SW] Failed to cache:', url, e))
                    )
                );
            })
            .then(() => {
                console.log('[SW] Installed!');
                return self.skipWaiting();
            })
    );
});

// ===== ACTIVATE =====
self.addEventListener('activate', event => {
    console.log('[SW] Activating...');
    event.waitUntil(
        caches.keys()
            .then(cacheNames =>
                Promise.all(
                    cacheNames
                        .filter(name => name !== CACHE_NAME)
                        .map(name => {
                            console.log('[SW] Deleting old cache:', name);
                            return caches.delete(name);
                        })
                )
            )
            .then(() => self.clients.claim())
    );
});

// ===== FETCH =====
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET, socket.io, dan external requests tertentu
    if (request.method !== 'GET') return;
    if (url.pathname.startsWith('/socket.io')) return;
    if (url.pathname.startsWith('/admin')) return;

    // Strategi: Network first untuk HTML, Cache first untuk assets
    if (request.destination === 'document') {
        event.respondWith(networkFirstStrategy(request));
    } else if (
        request.destination === 'style' ||
        request.destination === 'script' ||
        request.destination === 'font' ||
        request.destination === 'image'
    ) {
        event.respondWith(cacheFirstStrategy(request));
    } else {
        event.respondWith(networkFirstStrategy(request));
    }
});

// Network first, fallback to cache, fallback to offline page
async function networkFirstStrategy(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) return cachedResponse;

        // Jika halaman HTML, tampilkan offline page
        if (request.destination === 'document') {
            const offlinePage = await caches.match(OFFLINE_PAGE);
            if (offlinePage) return offlinePage;
        }

        return new Response('Offline', { status: 503 });
    }
}

// Cache first, fallback to network
async function cacheFirstStrategy(request) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) return cachedResponse;

    try {
        const networkResponse = await fetch(request);
        if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        return new Response('', { status: 404 });
    }
}

// ===== BACKGROUND SYNC =====
self.addEventListener('sync', event => {
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

async function doBackgroundSync() {
    console.log('[SW] Background sync triggered');
}

// ===== PUSH NOTIFICATIONS =====
self.addEventListener('push', event => {
    let data = { title: 'RafValyn 🌹', body: 'Ada update baru!', url: '/home' };
    try {
        data = { ...data, ...event.data.json() };
    } catch (e) {}

    event.waitUntil(
        self.registration.showNotification(data.title, {
            body: data.body,
            icon: '/static/uploads/logo.png',
            badge: '/static/uploads/logo.png',
            tag: 'rafvalyn-notif',
            renotify: true,
            vibrate: [100, 50, 100, 50, 100],
            data: { url: data.url },
            actions: [
                { action: 'open', title: '🌹 Buka', icon: '/static/uploads/logo.png' },
                { action: 'close', title: '✕ Tutup' }
            ]
        })
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    if (event.action === 'close') return;

    const urlToOpen = event.notification.data?.url || '/home';
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(windowClients => {
                for (const client of windowClients) {
                    if (client.url.includes(self.location.origin)) {
                        client.focus();
                        client.navigate(urlToOpen);
                        return;
                    }
                }
                return clients.openWindow(urlToOpen);
            })
    );
});