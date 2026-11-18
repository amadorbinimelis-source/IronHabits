"""Pruebas de la v1.10 (trozo 1 de la auditoría: datos seguros).
Deshacer, marcar desde la agenda, copias automáticas, nube (subida pendiente, gists separados, mejora de privacidad)
y service worker sin conexión. GitHub simulado: no toca ninguna cuenta real."""
import asyncio, json, sys
from playwright.async_api import async_playwright
sys.path.insert(0, __file__.rsplit("/", 1)[0])
URL = "http://localhost:8765/index.html"
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

class FakeGitHub:
    def __init__(self): self.gists = {}; self.calls = []; self.n = 0
    async def handle(self, route):
        req = route.request; u = req.url; m = req.method; H = {"Access-Control-Allow-Origin": "*"}
        body = json.loads(req.post_data) if req.post_data else None
        self.calls.append((m, u, body))
        if "ghp_valido" not in req.headers.get("authorization", ""):
            return await route.fulfill(status=401, json={}, headers=H)
        if u.endswith("/user"): return await route.fulfill(json={"login": "amador"}, headers=H)
        if "/gists?" in u: return await route.fulfill(json=[{"id": k, "files": {n: {} for n in g}} for k, g in self.gists.items()], headers=H)
        if u.endswith("/gists") and m == "POST":
            self.n += 1; gid = f"g{self.n}"; self.gists[gid] = {n: f["content"] for n, f in body["files"].items()}
            return await route.fulfill(status=201, json={"id": gid}, headers=H)
        gid = u.rsplit("/", 1)[-1]
        if gid not in self.gists: return await route.fulfill(status=404, json={}, headers=H)
        if m == "DELETE": del self.gists[gid]; return await route.fulfill(status=204, body="", headers=H)
        if m == "PATCH":
            for n, f in body["files"].items():
                if f is None: self.gists[gid].pop(n, None)
                elif "filename" in f and "content" not in f: self.gists[gid][f["filename"]] = self.gists[gid].pop(n)
                else: self.gists[gid][n] = f["content"]
            return await route.fulfill(json={"id": gid}, headers=H)
        return await route.fulfill(json={"id": gid, "files": {n: {"content": c, "truncated": False} for n, c in self.gists[gid].items()}}, headers=H)

async def confirm(pg):
    await pg.wait_for_timeout(150); await pg.evaluate("dlgDone(true)")

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        gh = FakeGitHub()
        ctx = await b.new_context(**p.devices["iPhone 13"]); await ctx.route("https://api.github.com/**", gh.handle)
        pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(1500)
        await pg.evaluate("S.habits.forEach(h=>h.start=addDays(todayK(),-30));S.logs={};S.checkins={};save();render()")

        # ── B1 · Deshacer ──
        r = await pg.evaluate("""(()=>{const t=todayK();sel=t;act('fr');const a=isDone(getH('fr'),t);
          setCI(t,'sleep',4);const u=undoAct();u[1]();return {a,fr:isDone(getH('fr'),t),ci:JSON.stringify(S.checkins[t]||{})};})()""")
        check(r["a"] and r["fr"] and r["ci"] == "{}", f"deshacer el check-in no desmarca lo anterior {r}")
        r = await pg.evaluate("""(()=>{const t=todayK();act('fr');const old=undoAct();act('fr');const a=isDone(getH('fr'),t);old[1]();return a===isDone(getH('fr'),t);})()""")
        check(r is True and "Ya no se puede" in await pg.inner_text("#toast"), "un «Deshacer» antiguo no devuelve los datos atrás")
        r = await pg.evaluate("""(()=>{const t=todayK();S.mocks=[];pushUndo();S.mocks.push({id:'x',date:t,r:20});const u=undoAct();u[1]();return S.mocks.length;})()""")
        check(r == 0, "deshacer también recupera los simulacros")
        r = await pg.evaluate("""(()=>{const t=todayK();sel=t;dayPlanSheet('fr');$('#dpIn').value='plan de prueba';saveDayPlan('fr');const a=planFor(getH('fr'),t).text;undoAct()[1]();closeSheet();return [a,(planFor(getH('fr'),t)||{}).text||''];})()""")
        check(r[0] == "plan de prueba" and r[1] != "plan de prueba", "deshacer el plan de un día")

        # ── B2 · Marcar desde la agenda marca el día del bloque ──
        r = await pg.evaluate("""(()=>{const t=todayK(),k=addDays(t,-1);sel=t;S.logs={};save();evSheet(k,'h:fr');
          [...document.querySelectorAll('#sheetBody .btn.pri')].find(b=>/Marcar/.test(b.textContent)).click();closeSheet();
          return {k:isDone(getH('fr'),k),hoy:isDone(getH('fr'),t)};})()""")
        check(r["k"] and not r["hoy"], f"«Marcar hecho» en la agenda marca ese día, no el seleccionado {r}")

        # ── B3 · Copias automáticas ──
        await pg.evaluate("S.logs={};(S.logs[addDays(todayK(),-2)]={}).fr={v:1,steps:[]};save()"); await pg.wait_for_timeout(4600)
        r = await pg.evaluate("snapList().then(a=>a.map(x=>x.id+'|'+x.days))")
        check(any(x.startswith("auto-") and x.endswith("|1") for x in r), f"copia automática del día {r}")
        await pg.evaluate("(()=>{wipeAll();})()"); await confirm(pg); await pg.wait_for_timeout(1500)
        n = await pg.evaluate("Object.keys(S.logs).length")
        pre = await pg.evaluate("snapList().then(a=>a.filter(x=>x.kind==='pre').map(x=>x.id))")
        check(n == 0 and pre, "borrar todo deja antes una copia de seguridad")
        await pg.evaluate(f"(()=>{{restoreSnap('{pre[0]}');}})()"); await confirm(pg); await pg.wait_for_timeout(1500)
        r = await pg.evaluate("({d:Object.keys(S.logs).length,p:!!getH('en')&&!!getH('en').plan.program})")
        check(r["d"] == 1 and r["p"], f"restaurar la copia recupera registros y plan {r}")
        await pg.evaluate("go('set');snapSheet()"); await pg.wait_for_timeout(300)
        check("Restaurar" in await pg.inner_text("#sheetBody"), "Ajustes › Copias automáticas lista las copias")
        await pg.evaluate("closeSheet();go('hoy')")
        for i in range(10): await pg.evaluate(f"writeSnap('pre','p{i}')")
        r = await pg.evaluate("snapList().then(a=>a.filter(x=>x.kind==='pre').length)")
        check(r == 6, f"las copias de seguridad no crecen sin límite ({r})")

        # ── B5 · Nube: dos gists ──
        await pg.evaluate("cloudSheet()"); await pg.fill("#tokIn", "ghp_valido1"); await pg.evaluate("(()=>{cloudConnect();})()"); await pg.wait_for_timeout(1000)
        c = await pg.evaluate("cloudCfg()")
        check(c["gistId"] != c["icsGist"] and set(gh.gists[c["gistId"]]) == {"ironhabits-datos.json"} and set(gh.gists[c["icsGist"]]) == {"ironhabits-agenda.ics"},
              "nube nueva: datos y calendario en gists separados")
        check(c["icsGist"] in await pg.evaluate("cloudICS()") and c["gistId"] not in await pg.evaluate("cloudICS()"), "el enlace del calendario no lleva al gist de datos")

        # ── B4 · Cambios que no se llegaron a subir ──
        await pg.evaluate("(()=>{const c=cloudCfg();(S.logs[todayK()]={}).fr={v:1,steps:[]};localStorage.setItem(KEY,JSON.stringify(S));c.dirtyAt=Date.now()+5;cloudSave(c);clearTimeout(_cloudT);})()")
        await pg.evaluate("cloudPull()"); await pg.wait_for_timeout(800)
        data = json.loads(gh.gists[c["gistId"]]["ironhabits-datos.json"])
        check(await pg.evaluate("todayK()") in data["state"]["logs"], "al abrir la app sube lo que quedó pendiente")
        gh.calls.clear()
        await pg.evaluate("(()=>{(S.logs[addDays(todayK(),-3)]={}).fr={v:1,steps:[]};save();flushOnHide();})()"); await pg.wait_for_timeout(800)
        patches = [x for x in gh.calls if x[0] == "PATCH"]
        check(len(patches) == 1 and set(patches[0][2]["files"]) == {"ironhabits-datos.json"}, "al salir de la app sube los datos (solo los datos, rápido)")

        # ── B5 · Mejora de privacidad para nubes antiguas (un solo gist) ──
        gh.gists["g90"] = {"ironhabits-datos.json": gh.gists[c["gistId"]]["ironhabits-datos.json"], "ironhabits-agenda.ics": "BEGIN:VCALENDAR"}
        await pg.evaluate("(()=>{const c=cloudCfg();cloudSave({token:c.token,login:'amador',gistId:'g90',lastSync:c.lastSync,lastPushAt:Date.now()});go('hoy')})()")
        check("Protege tus datos" in await pg.inner_text("#hoyBody"), "aviso en Hoy para proteger la nube antigua")
        await pg.evaluate("(()=>{cloudMigrate();})()"); await confirm(pg); await pg.wait_for_timeout(1200)
        c2 = await pg.evaluate("cloudCfg()")
        check("g90" not in gh.gists and c2["icsGist"] and set(gh.gists[c2["gistId"]]) == {"ironhabits-datos.json"} and set(gh.gists[c2["icsGist"]]) == {"ironhabits-agenda.ics"},
              f"separa datos y calendario y borra el gist antiguo ({c2.get('gistId')}, {c2.get('icsGist')})")
        check("Suscribir" in await pg.inner_text("#sheetBody"), "después abre «Suscribir el calendario»")
        await pg.evaluate("closeSheet();render()")
        # otro dispositivo que seguía apuntando al gist borrado
        for g in ("g1", "g2"): gh.gists.pop(g, None)  # en la vida real solo existe la nube actual
        ctx2 = await b.new_context(viewport={"width": 1200, "height": 900}); await ctx2.route("https://api.github.com/**", gh.handle)
        pg2 = await ctx2.new_page(); await pg2.goto(URL); await pg2.wait_for_timeout(1500)
        await pg2.evaluate("cloudSave({token:'ghp_valido1',login:'amador',gistId:'g90',lastSync:'2000-01-01T00:00:00Z',lastPushAt:1})")
        await pg2.evaluate("cloudPull()"); await pg2.wait_for_timeout(2500)
        r = await pg2.evaluate("({g:cloudCfg().gistId,i:cloudCfg().icsGist,l:Object.keys(S.logs).length})")
        check(r["g"] == c2["gistId"] and r["i"] == c2["icsGist"] and r["l"] > 0, f"el otro dispositivo encuentra los gists nuevos solo {r}")

        # ── B6 · Service worker ──
        await pg.goto(URL); await pg.evaluate("navigator.serviceWorker.ready"); await pg.reload(); await pg.wait_for_timeout(1500)
        ctrl = await pg.evaluate("!!navigator.serviceWorker.controller")
        await ctx.set_offline(True); await pg.reload(); await pg.wait_for_timeout(1500)
        ok = await pg.evaluate("typeof render==='function'&&document.querySelectorAll('nav button').length===4")
        check(ctrl and ok, "sin conexión la app abre desde lo guardado")
        await ctx.set_offline(False)
        r = await pg.evaluate("caches.keys().then(ks=>Promise.all(ks.map(k=>caches.open(k).then(c=>c.keys())))).then(a=>a.flat().map(r=>r.url))")
        check(r and all("localhost:8765" in u for u in r), f"no guarda nada de GitHub en la caché ({len(r)} archivos)")

        check(not errs, f"sin errores de JavaScript {errs[:2]}")
        await b.close()

asyncio.run(main())
print("\nRESULTADO:", "OK" if not fails else f"{len(fails)} fallos"); sys.exit(1 if fails else 0)
