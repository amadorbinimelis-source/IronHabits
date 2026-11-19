// IronHabits · servidor de avisos.
// La app le manda la lista de avisos de los próximos días (hora y texto) y él, cada minuto, envía los que tocan.
// No guarda tus registros ni tus notas: solo la suscripción del iPhone y los avisos pendientes.
import { genVapid, sendPush } from './push.js';

const ORIGINS = ['https://amadorbinimelis-source.github.io', 'http://localhost:8765'];
const SUBJECT = 'https://amadorbinimelis-source.github.io/IronHabits/';
const ID_RE = /^[a-z0-9]{16,48}$/;

function cors(req) {
  const o = req.headers.get('Origin') || '';
  return { 'Access-Control-Allow-Origin': ORIGINS.includes(o) ? o : ORIGINS[0], 'Access-Control-Allow-Methods': 'GET,POST,OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', Vary: 'Origin' };
}
const json = (req, data, status = 200) => new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json', ...cors(req) } });

async function vapid(env) {
  let v = await env.PUSH.get('vapid', 'json');
  if (!v) { v = await genVapid(); await env.PUSH.put('vapid', JSON.stringify(v)); }
  return v;
}
async function getIdx(env) { return (await env.PUSH.get('idx', 'json')) || []; }
async function addIdx(env, id) { const idx = await getIdx(env); if (!idx.includes(id)) { idx.push(id); await env.PUSH.put('idx', JSON.stringify(idx)); } }
async function removeDev(env, id) { await env.PUSH.delete('dev:' + id); const idx = (await getIdx(env)).filter(x => x !== id); await env.PUSH.put('idx', JSON.stringify(idx)); }

function cleanItems(items) {
  const now = Date.now();
  return (Array.isArray(items) ? items : []).filter(i => i && typeof i.at === 'number' && i.at > now - 60000 && i.at < now + 8 * 864e5)
    .slice(0, 200).map(i => ({ at: i.at, title: String(i.title || 'IronHabits').slice(0, 120), body: String(i.body || '').slice(0, 300), tag: String(i.tag || '').slice(0, 80), url: String(i.url || '').slice(0, 200) }));
}

export default {
  async fetch(req, env) {
    if (req.method === 'OPTIONS') return new Response(null, { headers: cors(req) });
    const url = new URL(req.url);
    try {
      if (url.pathname === '/vapid') return json(req, { publicKey: (await vapid(env)).publicKey });
      if (req.method !== 'POST') return json(req, { ok: true, app: 'IronHabits push' });
      const body = await req.json();
      if (!ID_RE.test(body.id || '')) return json(req, { error: 'id' }, 400);
      const key = 'dev:' + body.id;
      if (url.pathname === '/sync') {
        if (!body.sub || !/^https:\/\//.test(body.sub.endpoint || '') || !body.sub.keys) return json(req, { error: 'sub' }, 400);
        const items = cleanItems(body.items);
        await env.PUSH.put(key, JSON.stringify({ sub: body.sub, items, updated: Date.now() }));
        await addIdx(env, body.id);
        return json(req, { ok: true, items: items.length });
      }
      if (url.pathname === '/test') {
        const dev = await env.PUSH.get(key, 'json'); if (!dev) return json(req, { error: 'no' }, 404);
        const r = await sendPush(dev.sub, { title: '💪 IronHabits', body: '¡Los avisos funcionan! Así te llegarán tus hábitos.', tag: 'test', url: './' }, await vapid(env), SUBJECT, 120);
        if (r.status === 404 || r.status === 410) { await removeDev(env, body.id); return json(req, { error: 'gone' }, 410); }
        return json(req, { ok: r.ok, status: r.status });
      }
      if (url.pathname === '/unsubscribe') { await removeDev(env, body.id); return json(req, { ok: true }); }
      return json(req, { error: 'ruta' }, 404);
    } catch (e) { return json(req, { error: String(e && e.message || e) }, 500); }
  },
  // Cada minuto: envía los avisos cuya hora cae en este minuto
  async scheduled(event, env) {
    const now = event.scheduledTime || Date.now(), from = now - 60000, to = now + 5000;
    const v = await vapid(env);
    for (const id of await getIdx(env)) {
      const dev = await env.PUSH.get('dev:' + id, 'json');
      if (!dev) continue;
      for (const it of dev.items.filter(i => i.at > from && i.at <= to)) {
        try {
          const r = await sendPush(dev.sub, it, v, SUBJECT);
          if (r.status === 404 || r.status === 410) { await removeDev(env, id); break; }
        } catch (e) { /* se reintenta con el siguiente aviso */ }
      }
    }
  },
};
