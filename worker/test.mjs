// Prueba del servidor de avisos sin Cloudflare: cifrado (descifra con la librería de referencia), firma VAPID y envío por minutos.
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { encrypt, genVapid, vapidAuth, b64u } from './src/push.js';
import worker from './src/index.js';
const ece = createRequire(import.meta.url)('http_ece');
const ok = (c, m) => { if (!c) { console.error('FALLA:', m); process.exit(1); } console.log('ok ·', m); };

const ecdh = crypto.createECDH('prime256v1'); ecdh.generateKeys(); const auth = crypto.randomBytes(16);
const sub = { endpoint: 'https://web.push.apple.com/ok', keys: { p256dh: b64u.enc(ecdh.getPublicKey()), auth: b64u.enc(auth) } };
const dec = ece.decrypt(Buffer.from(await encrypt(sub, '{"t":"ñ💪"}')), { version: 'aes128gcm', privateKey: ecdh, authSecret: auth });
ok(dec.toString() === '{"t":"ñ💪"}', 'cifrado aes128gcm');
const v = await genVapid(), h = await vapidAuth(sub.endpoint, v, 'https://x'), [a, b, s] = h.slice(8).split(', k=')[0].split('.');
const pub = crypto.createPublicKey({ key: { kty: 'EC', crv: 'P-256', x: v.privateJwk.x, y: v.privateJwk.y }, format: 'jwk' });
ok(crypto.verify('sha256', Buffer.from(a + '.' + b), { key: pub, dsaEncoding: 'ieee-p1363' }, b64u.dec(s)), 'firma VAPID');

const store = new Map(), sent = [];
const env = { PUSH: { async get(k, t) { const x = store.get(k); return x == null ? null : t === 'json' ? JSON.parse(x) : x; }, async put(k, x) { store.set(k, x); }, async delete(k) { store.delete(k); } } };
globalThis.fetch = async url => { sent.push(url); return new Response('', { status: url.includes('gone') ? 410 : 201 }); };
const req = (p, body) => new Request('https://x' + p, { method: body ? 'POST' : 'GET', body: body && JSON.stringify(body), headers: { Origin: 'https://amadorbinimelis-source.github.io' } });
const now = Date.now();
ok((await (await worker.fetch(req('/vapid'), env)).json()).publicKey.length === 87, '/vapid da la clave pública');
const r = await (await worker.fetch(req('/sync', { id: 'abcdefghijklmnop1234', sub, items: [{ at: now + 10e3, title: 'A' }, { at: now + 3600e3, title: 'B' }, { at: now - 864e5, title: 'vieja' }] }), env)).json();
ok(r.items === 2, '/sync guarda solo los avisos futuros');
ok((await worker.fetch(req('/sync', { id: '../x', sub }), env)).status === 400, 'rechaza ids raros');
await worker.scheduled({ scheduledTime: now + 30e3 }, env); ok(sent.length === 1, 'envía el aviso de este minuto');
await worker.scheduled({ scheduledTime: now + 90e3 }, env); ok(sent.length === 1, 'no lo repite el minuto siguiente');
await worker.fetch(req('/sync', { id: 'zzzzzzzzzzzzzzzz9999', sub: { ...sub, endpoint: 'https://web.push.apple.com/gone' }, items: [{ at: now + 3600e3 - 1e3, title: 'x' }] }), env);
await worker.scheduled({ scheduledTime: now + 3600e3 }, env);
ok(sent.length === 3 && JSON.parse(store.get('idx')).length === 1, 'borra los móviles que ya no existen');
ok((await worker.fetch(req('/unsubscribe', { id: 'abcdefghijklmnop1234' }), env)).ok && !store.get('dev:abcdefghijklmnop1234'), '/unsubscribe borra');
