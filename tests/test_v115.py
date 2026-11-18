"""Pruebas de la v1.15: la app pasa a llamarse IronHabits sin perder nada de lo guardado con el nombre antiguo (Rutina).
GitHub simulado: no toca ninguna cuenta real."""
import asyncio, json, sys
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

class FakeGitHub:
    def __init__(self): self.gists = {}; self.desc = {}
    async def handle(self, route):
        req = route.request; u = req.url; m = req.method; H = {"Access-Control-Allow-Origin": "*"}
        body = json.loads(req.post_data) if req.post_data else None
        if u.endswith("/user"): return await route.fulfill(json={"login": "amador"}, headers=H)
        if "/gists?" in u: return await route.fulfill(json=[{"id": k, "files": {n: {} for n in g}} for k, g in self.gists.items()], headers=H)
        gid = u.rsplit("/", 1)[-1]
        if gid not in self.gists: return await route.fulfill(status=404, json={}, headers=H)
        if m == "PATCH":
            if "description" in body: self.desc[gid] = body["description"]
            for n, f in body["files"].items():
                if f is None: self.gists[gid].pop(n, None)
                elif "filename" in f and "content" not in f: self.gists[gid][f["filename"]] = self.gists[gid].pop(n)
                else: self.gists[gid][n] = f["content"]
            return await route.fulfill(json={"id": gid}, headers=H)
        return await route.fulfill(json={"id": gid, "files": {n: {"content": c, "truncated": False} for n, c in self.gists[gid].items()}}, headers=H)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        gh = FakeGitHub()
        ctx = await b.new_context(**p.devices["iPhone 13"]); await ctx.route("https://api.github.com/**", gh.handle)
        pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(1500)

        # Nombre en todas partes
        r = await pg.evaluate("[document.title,document.querySelector('meta[name=apple-mobile-web-app-title]').content]")
        man = await pg.evaluate("fetch('manifest.webmanifest').then(r=>r.json()).then(m=>[m.name,m.short_name])")
        check(r == ["IronHabits", "IronHabits"] and man == ["IronHabits", "IronHabits"], f"título, nombre en el iPhone y manifest: {r} {man}")
        seen = []
        for v in ("hoy", "agenda", "prog", "set"):
            await pg.evaluate(f"go('{v}')"); await pg.wait_for_timeout(250)
            t = await pg.inner_text(f"#v-{v}")
            if "Rutina" in t.replace("Rutina de tu hermano", "").replace("antes Rutina", ""): seen.append(v)
        await pg.evaluate("welcomeSheet(0)"); await pg.wait_for_timeout(250)
        w = await pg.inner_text("#sheetBody"); await pg.evaluate("closeSheet()")
        check(not seen and "IronHabits" in w, f"ninguna pantalla dice «Rutina» como nombre de la app {seen}")
        ics = await pg.evaluate("buildICS(todayK(),addDays(todayK(),7),false).text")
        check("X-WR-CALNAME:IronHabits" in ics and "@ironhabits" in ics and "Rutina" not in ics, "el calendario se llama IronHabits")
        check("IronHabits" in await pg.evaluate("reviewText(weekSummary(weekStartK(todayK())))"), "el resumen semanal dice IronHabits")

        # Datos guardados con el nombre antiguo → se conservan
        await pg.evaluate("""(()=>{const s=JSON.parse(localStorage.getItem('ironhabits_v1'));s.notes={'2026-11-10':'nota antigua'};
          localStorage.clear();localStorage.setItem('rutina_v1',JSON.stringify(s));localStorage.setItem('rutina_cloud',JSON.stringify({token:'ghp_x',login:'amador',gistId:'g1',icsGist:'g2',lastSync:'2026-11-18T10:00:00Z'}));})()""")
        await pg.evaluate("""new Promise(r=>{const q=indexedDB.open('rutina-copias',1);q.onupgradeneeded=()=>q.result.createObjectStore('snaps',{keyPath:'id'});
          q.onsuccess=()=>{const tx=q.result.transaction('snaps','readwrite');tx.objectStore('snaps').put({id:'auto-2026-11-17',kind:'auto',at:'2026-11-17T10:00:00Z',habits:6,days:3,state:{habits:[],logs:{}}});tx.oncomplete=()=>{q.result.close();r();};};})""")
        gh.gists = {"g1": {"rutina-datos.json": json.dumps({"kind": "rutina-sync", "savedAt": "2026-11-18T10:00:00Z", "device": "iPhone", "state": {"habits": [], "logs": {}}})}, "g2": {"rutina-agenda.ics": "BEGIN:VCALENDAR"}}
        await pg.reload(); await pg.wait_for_timeout(2500)
        r = await pg.evaluate("({old:['rutina_v1','rutina_plan_v1','rutina_cloud'].some(k=>localStorage.getItem(k)!==null),note:S.notes['2026-11-10'],cloud:!!localStorage.getItem('ironhabits_cloud'),hab:S.habits.length})")
        check(not r["old"] and r["note"] == "nota antigua" and r["cloud"] and r["hab"] >= 6, f"lo guardado como «Rutina» pasa a IronHabits sin perder nada {r}")
        r = await pg.evaluate("snapList().then(a=>a.map(x=>x.id))")
        check("auto-2026-11-17" in r, f"las copias automáticas antiguas se conservan {r}")
        # Nube: los archivos se renombran y pide volver a suscribir el calendario
        await pg.evaluate("cloudPush(true)"); await pg.wait_for_timeout(1500)
        c = await pg.evaluate("cloudCfg()")
        check(set(gh.gists["g1"]) == {"ironhabits-datos.json"} and set(gh.gists["g2"]) == {"ironhabits-agenda.ics"} and c.get("names2") and c.get("resub"),
              f"la nube renombra sus archivos ({list(gh.gists['g1'])}, {list(gh.gists['g2'])})")
        ics_url = await pg.evaluate("cloudICS()")
        check(gh.desc.get("g1", "").startswith("IronHabits") and ics_url.endswith("/g2/raw/ironhabits-agenda.ics"), "descripciones y enlace del calendario con el nombre nuevo")
        await pg.evaluate("go('hoy')"); await pg.wait_for_timeout(300)
        check("Vuelve a suscribir" in await pg.evaluate("banners(todayK())"), "avisa de volver a suscribir el calendario")
        check(not errs, f"sin errores de JavaScript {errs[:2]}")
        await b.close()

asyncio.run(main())
print("\nRESULTADO:", "OK" if not fails else f"{len(fails)} fallos"); sys.exit(1 if fails else 0)
