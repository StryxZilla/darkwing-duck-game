const CACHE = 'darkwing-v3';
const ASSETS = [
  '/darkwing-duck-game/',
  '/darkwing-duck-game/index.html',
  '/darkwing-duck-game/manifest.json',
  '/darkwing-duck-game/icon-192.svg',
  '/darkwing-duck-game/icon-512.svg',
  '/darkwing-duck-game/assets/titleBg.png',
  '/darkwing-duck-game/assets/bgRooftops.png',
  '/darkwing-duck-game/assets/bgFunhouse.png',
  '/darkwing-duck-game/assets/bgGreenhouse.png',
  '/darkwing-duck-game/assets/bgDam.png',
  '/darkwing-duck-game/assets/bgFortress.png',
  '/darkwing-duck-game/assets/portraitDarkwing.png',
  '/darkwing-duck-game/assets/portraitMegavolt.png',
  '/darkwing-duck-game/assets/portraitQuackerjack.png',
  '/darkwing-duck-game/assets/portraitBushroot.png',
  '/darkwing-duck-game/assets/portraitLiquidator.png',
  '/darkwing-duck-game/assets/portraitNegaduck.png',
  '/darkwing-duck-game/assets/portraitLaunchpad.png',
  '/darkwing-duck-game/assets/portraitGosalyn.png',
  '/darkwing-duck-game/assets/portraitMorgana.png',
  '/darkwing-duck-game/assets/portraitGizmoduck.png',
  '/darkwing-duck-game/assets/gameOver.png',
  '/darkwing-duck-game/assets/victory.png',
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request).then(resp => {
      if (resp.ok) {
        const clone = resp.clone();
        caches.open(CACHE).then(c => c.put(e.request, clone));
      }
      return resp;
    })).catch(() => caches.match('/darkwing-duck-game/'))
  );
});
