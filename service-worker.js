// Service Worker pour Ancient Vocabulary
// Permet le fonctionnement offline de l'application

const CACHE_NAME = 'ancient-vocabulary-v1';
const urlsToCache = [
  '/letzvisit/',
  '/letzvisit/index.html',
  '/letzvisit/greek_vocabulary.html',
  '/letzvisit/manifest.json'
];

// Installation du Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Cache ouvert');
        return cache.addAll(urlsToCache);
      })
  );
});

// Activation et nettoyage des anciens caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Suppression ancien cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Stratégie de cache: Network First, puis Cache
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Si la requête réussit, met à jour le cache
        if (response && response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        // Si offline, utilise le cache
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          
          // Si pas dans le cache et que c'est une navigation, retourne la page d'accueil
          if (event.request.mode === 'navigate') {
            return caches.match('/letzvisit/index.html');
          }
          
          return new Response('Contenu non disponible offline', {
            status: 503,
            statusText: 'Service Unavailable'
          });
        });
      })
  );
});
