// IronHabits · service worker
// - La app (index.html) y el plan: red primero, pero si en 3 s no responde se abre lo guardado (mala cobertura = app al instante).
// - Iconos y manifest: lo guardado al momento y se actualiza por detrás.
// - Solo se guardan respuestas correctas de esta web; las llamadas a GitHub (nube) no pasan por aquí.
const CACHE = 'ironhabits-v14';
const ASSETS = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './plan.json'];
const TIMEOUT = 3000;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});

const okToCache = r => r && r.ok && r.type === 'basic';

function networkFirst(req) {
  return caches.open(CACHE).then(c => new Promise(resolve => {
    let done = false;
    const finish = r => { if (!done && r) { done = true; resolve(r); } };
    const fromCache = () => c.match(req, { ignoreSearch: true })
      .then(r => r || (req.mode === 'navigate' ? c.match('./index.html') : null));
    const timer = setTimeout(() => fromCache().then(finish), TIMEOUT);
    fetch(req)
      .then(r => { clearTimeout(timer); if (okToCache(r)) c.put(req, r.clone()); finish(r); })
      .catch(() => { clearTimeout(timer); fromCache().then(r => { if (!done) { done = true; resolve(r || Response.error()); } }); });
  }));
}

function staleWhileRevalidate(req) {
  return caches.open(CACHE).then(c => c.match(req, { ignoreSearch: true }).then(hit => {
    const net = fetch(req).then(r => { if (okToCache(r)) c.put(req, r.clone()); return r; }).catch(() => hit || Response.error());
    return hit || net;
  }));
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // GitHub y demás: directo a la red, sin guardar nada
  const isPage = req.mode === 'navigate' || /\/(index\.html)?$/.test(url.pathname);
  if (isPage || url.pathname.endsWith('/plan.json')) e.respondWith(networkFirst(req));
  else e.respondWith(staleWhileRevalidate(req));
});
