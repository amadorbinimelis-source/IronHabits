"""Pruebas de la v1.9: carga de entreno, simulacros B2, check-in, resumen de mañana, mover de día arrastrando
y sincronización con la nube (GitHub simulado: no toca ninguna cuenta real)."""
import asyncio, json, sys
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

class FakeGitHub:
    def __init__(self): self.gists = {}; self.calls = []
    async def handle(self, route):
        req = route.request; u = req.url; m = req.method; self.calls.append((m, u))
        auth = req.headers.get("authorization", "")
        if "ghp_valido" not in auth:
            return await route.fulfill(status=401, json={"message": "Bad credentials"}, headers={"Access-Control-Allow-Origin": "*"})
        H = {"Access-Control-Allow-Origin": "*"}
        if u.endswith("/user"): return await route.fulfill(json={"login": "amador"}, headers=H)
        if "/gists?" in u: return await route.fulfill(json=[{"id": k, "files": {n: {} for n in g}} for k, g in self.gists.items()], headers=H)
        if u.endswith("/gists") and m == "POST":
            body = json.loads(req.post_data); gid = f"g{len(self.gists)+1}"
            self.gists[gid] = {n: f["content"] for n, f in body["files"].items()}
            return await route.fulfill(status=201, json={"id": gid}, headers=H)
        gid = u.rsplit("/", 1)[-1]
        if gid not in self.gists: return await route.fulfill(status=404, json={}, headers=H)
        if m == "DELETE":
            del self.gists[gid]; return await route.fulfill(status=204, body="", headers=H)
        if m == "PATCH":
            body = json.loads(req.post_data)
            for n, f in body["files"].items():
                if f is None: self.gists[gid].pop(n, None)
                else: self.gists[gid][n] = f["content"]
            return await route.fulfill(json={"id": gid}, headers=H)
        if m == "GET" and gid in self.gists:
            return await route.fulfill(json={"id": gid, "files": {n: {"content": c, "truncated": False} for n, c in self.gists[gid].items()}}, headers=H)
        await route.fulfill(status=404, json={}, headers=H)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        gh = FakeGitHub()
        ctx = await b.new_context(**p.devices["iPhone 13"]); await ctx.route("https://api.github.com/**", gh.handle)
        pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(1500)

        # ── Simulacros B2 (tablas oficiales) ──
        r = await pg.evaluate("[toScale('r',24),toScale('u',18),toScale('w',24),toScale('l',18),toScale('s',36),toScale('r',37),toScale('r',30),toScale('r',9),toScale('s',60)]")
        check(r[:5] == [160]*5 and r[5] == 180 and r[6] == 169 and r[7] is None and r[8] == 190, f"escala Cambridge: {r}")
        r = await pg.evaluate("(()=>{const m={date:'2026-12-01',r:30,u:20,w:26,l:20,s:40};const q=mockScore(m);return [q.overall,grade(q.overall)[0]]})()")
        check(r[0] == 166 and r[1].startswith("C"), f"nota global de un simulacro: {r}")
        await pg.evaluate("mockSheet('2026-12-01')"); await pg.wait_for_timeout(200)
        for part, v in (("r", 30), ("u", 20), ("w", 26), ("l", 14), ("s", 40)): await pg.fill(f"#mk-{part}", str(v))
        txt = await pg.inner_text("#mkTot")
        await pg.evaluate("saveMock()"); await pg.wait_for_timeout(200)
        blk = await pg.evaluate("mocksBlock(true)")
        check("Nota global: 162" in txt and len(await pg.evaluate("S.mocks")) == 1 and "Listening" in blk and "más floja" in blk, f"registrar simulacro y parte floja ({txt.splitlines()[0]})")

        # ── Carga de entreno ──
        r = await pg.evaluate("""(()=>{const _tk=todayK;todayK=()=>'2027-01-31';S.logs={};
          const h=getH('boxeo'),f=getH('fuerza');h.start='2026-11-01';f.start='2026-11-01';
          // 4 semanas a ~60 min RPE 6 y la última semana con picos a RPE 9 y 90 min
          for(let i=27;i>=0;i--){const k=addDays('2027-01-31',-i);if(i%2)continue;(S.logs[k]=S.logs[k]||{}).boxeo={v:1,mins:i<7?90:60,m:{rpe:i<7?9:6}};}
          const a=acwr('2027-01-31');const z=acwrZone(a.r)[0];const blk=loadBlock();const ban=banners('2027-01-31');todayK=_tk;
          return {r:+a.r.toFixed(2),z,enough:a.enough,blk:blk.includes('Carga de entreno'),ban:ban.includes('Pico de carga')};})()""")
        check(r["enough"] and r["r"] > 1.5 and r["z"] == "Riesgo" and r["ban"], f"ACWR detecta el pico de carga: {r}")
        r = await pg.evaluate("(()=>{S.logs={};const k=todayK();(S.logs[k]={}).boxeo={v:1,mins:60};rpeSheet('boxeo',k);saveRPE('boxeo',k,8);return sessLoad(getH('boxeo'),k);})()")
        check(r["load"] == 480 and not r["est"], f"RPE 8 × 60 min = carga {r['load']}")

        # ── Check-in ──
        r = await pg.evaluate("""(()=>{const t=todayK();S.checkins={};const a=checkinCard(t).includes('Cómo estás');setCI(t,'sleep',4);setCI(t,'energy',5);const b=checkinCard(t)==='';
          for(let i=1;i<8;i++){S.checkins[addDays(t,-i)]={sleep:i%2?2:5,energy:i%2?2:5};}return {a,b,e:energyBlock().includes('Energía media')};})()""")
        check(r["a"] and r["b"] and r["e"], f"check-in de sueño y energía {r}")

        # ── Resumen de mañana ──
        r = await pg.evaluate("(()=>{const _tk=todayK;todayK=()=>'2026-11-23';const i=tomorrowInfo();todayK=_tk;return i&&{n:i.evs.length,wake:i.wake,bed:i.bed,t:i.text};})()")
        check(r and r["n"] > 0 and r["wake"] and r["bed"], f"resumen de mañana: {r and r['t']}")

        # ── Arrastrar a otro día ──
        await pg.evaluate("S.agenda={};S.logs={};save();sel='2026-11-24';agView='week';go('agenda')"); await pg.wait_for_timeout(400)
        cdp = await ctx.new_cdp_session(pg)
        async def touch(t, x=0, y=0): await cdp.send("Input.dispatchTouchEvent", {"type": t, "touchPoints": [] if t == "touchEnd" else [{"x": x, "y": y}]})
        async def drag(hid, frm, to):
            el = pg.locator(f".agw-ev[data-id='h:{hid}'][data-k='{frm}']").first; await el.scroll_into_view_if_needed(); bx = await el.bounding_box()
            col = await pg.locator(f".agw-day[data-colk='{to}']").bounding_box()
            x0, y0 = bx["x"] + bx["width"] / 2, bx["y"] + 6; x1 = col["x"] + col["width"] / 2
            await touch("touchStart", x0, y0); await pg.wait_for_timeout(450)
            for i in range(1, 11): await touch("touchMove", x0 + (x1 - x0) * i / 10, y0); await pg.wait_for_timeout(16)
            await touch("touchEnd"); await pg.wait_for_timeout(500)
        # hábito del martes que no esté el miércoles
        found = await pg.evaluate("""(()=>{const ws='2026-11-23';for(let i=0;i<7;i++)for(let j=0;j<7;j++){if(i===j)continue;const a=addDays(ws,i),b=addDays(ws,j);
            for(const h of dayHabits(a))if(!showOn(h,b)&&document.querySelector(`.agw-ev[data-id='h:${h.id}'][data-k='${a}']`))return [h.id,a,b];}return null;})()""")
        check(found is not None, f"hay un hábito que se puede cambiar de día esta semana ({found})")
        if found:
            hid, a, bday = found
            await drag(hid, a, bday)
            r = await pg.evaluate(f"({{a:agOv('{a}','h:{hid}'),b:agOv('{bday}','in:{hid}'),show:dayHabits('{a}').some(h=>h.id==='{hid}'),on:dayHabits('{bday}').some(h=>h.id==='{hid}')}})")
            check(r["a"] and r["a"].get("moveTo") == bday and r["b"] and not r["show"] and r["on"], f"arrastrar a otro día mueve el hábito ({hid}: {a} → {bday})")
            await pg.evaluate("doUndo()")
            check(not await pg.evaluate(f"agOv('{a}','h:{hid}')"), "deshacer el cambio de día")
        await drag("fr", "2026-11-24", "2026-11-26")
        check(not await pg.evaluate("agOv('2026-11-24','h:fr')") and "ya tienes" in await pg.inner_text("#toast"), "no deja moverlo a un día que ya lo tiene")
        # ── Nube ──
        await pg.evaluate("S.logs={'2026-11-20':{fr:{v:1,mins:45}}};S.mocks=[];save()")
        await pg.evaluate("cloudSheet()"); await pg.wait_for_timeout(200)
        await pg.fill("#tokIn", "ghp_malo"); await pg.evaluate("cloudConnect()"); await pg.wait_for_timeout(500)
        check("no válido" in await pg.inner_text("#toast") and not await pg.evaluate("cloudCfg()"), "nube: código incorrecto no conecta")
        await pg.fill("#tokIn", "ghp_valido123"); await pg.evaluate("cloudConnect()"); await pg.wait_for_timeout(800)
        c = await pg.evaluate("cloudCfg()")
        check(c and c["gistId"] == "g1" and c["icsGist"] == "g2" and set(gh.gists["g1"]) == {"rutina-datos.json"} and set(gh.gists["g2"]) == {"rutina-agenda.ics"}, f"nube: crea dos gists secretos, datos y calendario por separado ({c and c.get('gistId')}, {c and c.get('icsGist')})")
        ics = gh.gists["g2"]["rutina-agenda.ics"]
        check(ics.startswith("BEGIN:VCALENDAR") and ics.count("BEGIN:VEVENT") > 300, f"nube: calendario con {ics.count('BEGIN:VEVENT')} eventos")
        check(await pg.evaluate("cloudICS()") == "https://gist.githubusercontent.com/amador/g2/raw/rutina-agenda.ics", "nube: enlace de suscripción con tus cambios")
        # un cambio se sube solo
        await pg.evaluate("sel='2026-11-21';(S.logs['2026-11-21']={}).fr={v:1,mins:30};save();agSet('2026-11-25','h:fr',{cancel:true,reason:'test'});save()")
        await pg.wait_for_timeout(7000)
        data = json.loads(gh.gists["g1"]["rutina-datos.json"])
        check("2026-11-21" in data["state"]["logs"] and "agendaBase" not in data["state"], "nube: los cambios se suben solos (y sin la parte pesada)")
        check("2026-11-25" not in "".join(l for l in gh.gists["g2"]["rutina-agenda.ics"].splitlines() if l.startswith("UID:2026-11-25-h-fr")), "nube: el calendario refleja la tarea anulada")
        check(await pg.evaluate("Object.keys(localStorage).every(k=>!localStorage.getItem(k).includes('ghp_valido')||k==='rutina_cloud')") and "ghp_" not in await pg.evaluate("backupJSON()"), "nube: el código no sale en las copias")
        # otro dispositivo
        ctx2 = await b.new_context(viewport={"width": 1200, "height": 900}); await ctx2.route("https://api.github.com/**", gh.handle)
        pg2 = await ctx2.new_page(); await pg2.goto(URL); await pg2.wait_for_timeout(1500)
        await pg2.evaluate("go('set');cloudSheet()"); await pg2.wait_for_timeout(200)
        await pg2.fill("#tokIn", "ghp_valido123"); await pg2.evaluate("cloudConnect()"); await pg2.wait_for_timeout(2500)
        r = await pg2.evaluate("({l:Object.keys(S.logs),p:!!getH('en').plan.program,ag:!!agOv('2026-11-25','h:fr')})")
        check("2026-11-21" in r["l"] and r["p"] and r["ag"], f"nube: en otro dispositivo se recupera todo {r}")
        await pg2.screenshot(path="/tmp/t/cloud_set.png", full_page=True)
        # cambio desde el ordenador → el iPhone lo recibe al volver a la app
        await pg2.evaluate("(S.logs['2026-11-22']={}).fr={v:1,mins:45};save();cloudPush(true)"); await pg2.wait_for_timeout(800)
        await pg.evaluate("cloudPull()"); await pg.wait_for_timeout(1500)
        check(await pg.evaluate("!!S.logs['2026-11-22']"), "nube: el iPhone recibe lo hecho en el ordenador")
        check(not errs, f"sin errores de JavaScript {errs[:2]}")
        await pg.evaluate("go('stats')"); await pg.wait_for_timeout(300); await pg.screenshot(path="/tmp/t/stats_v19.png", full_page=True)
        await b.close()

asyncio.run(main())
print("\nRESULTADO:", "OK" if not fails else f"{len(fails)} fallos"); sys.exit(1 if fails else 0)
