"""Pruebas de la v1.19 (reevaluación, trozo 3: marca IronHabits): iconos, arranque de iOS, manifest, plan en IndexedDB
(con migración desde localStorage) y estilo de marca."""
import asyncio, json, sys
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid")
        await ctx.add_init_script("Object.defineProperty(navigator,'standalone',{get:()=>true})")
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-24T19:30:00+01:00")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL, wait_until="domcontentloaded")
        r0 = await pg.evaluate("[!!document.getElementById('boot'),getComputedStyle(document.getElementById('boot')).pointerEvents]")
        await pg.wait_for_timeout(3000)
        r1 = await pg.evaluate("[!!document.getElementById('boot'),document.getElementById('bootRing')?document.getElementById('bootRing').style.strokeDashoffset:'']")
        check(r0 == [True, "none"] and r1[0] is False, f"pantalla de arranque con el anillo: aparece, no bloquea toques y se va sola ({r0}, {r1})")
        # Iconos y arranque
        r = await pg.evaluate("""Promise.all(['icon-180.png','icon-192.png','icon-512.png','icon-maskable-512.png','favicon.png'].map(u=>new Promise(res=>{const i=new Image();i.onload=()=>res(u+':'+i.naturalWidth);i.onerror=()=>res(u+':error');i.src=u;})))""")
        check(r == ["icon-180.png:180", "icon-192.png:192", "icon-512.png:512", "icon-maskable-512.png:512", "favicon.png:64"], f"iconos con su tamaño {r}")
        r = await pg.evaluate("[document.querySelector('link[rel=apple-touch-icon]').getAttribute('href'),[...document.querySelectorAll('link[rel=apple-touch-startup-image]')].map(l=>l.getAttribute('href'))]")
        ok = await pg.evaluate("(hrefs)=>Promise.all(hrefs.map(u=>fetch(u).then(r=>r.ok)))", r[1])
        check(r[0] == "icon-180.png" and len(r[1]) >= 10 and all(ok), f"icono de iPhone de 180 px y {len(r[1])} pantallas de arranque")
        m = await pg.evaluate("fetch('manifest.webmanifest').then(r=>r.json())")
        check(m.get("id") == "./" and any(i["purpose"] == "maskable" for i in m["icons"]) and all(i["purpose"] in ("any", "maskable") for i in m["icons"]), "manifest con id e icono maskable aparte")
        # Plan en IndexedDB
        r = await pg.evaluate("planIDB('readonly').then(P=>({idb:!!(P&&P.agendaBase),ls:localStorage.getItem(PLAN_KEY),prog:!!getH('en').plan.program}))")
        check(r["idb"] and r["ls"] is None and r["prog"], f"el plan se guarda en IndexedDB y no en localStorage {r}")
        # Migración: plan antiguo en localStorage → IndexedDB
        await pg.evaluate("planIDB('readonly').then(P=>{localStorage.setItem(PLAN_KEY,JSON.stringify(P));return planIDB('readwrite',null)})")
        await pg.reload(); await pg.wait_for_timeout(2000)
        r = await pg.evaluate("planIDB('readonly').then(P=>({idb:!!(P&&P.agendaBase),ls:localStorage.getItem(PLAN_KEY),prog:!!getH('en').plan.program,ag:Object.keys(S.agendaBase).length}))")
        check(r["idb"] and r["ls"] is None and r["prog"] and r["ag"] > 100, f"un plan guardado por una versión anterior pasa solo a IndexedDB {r}")
        # Tras recargar, el plan sigue (lectura desde IndexedDB)
        await pg.reload(); await pg.wait_for_timeout(2000)
        r = await pg.evaluate("({prog:!!getH('en').plan.program,ag:Object.keys(S.agendaBase).length,evs:dayEvents(todayK()).length})")
        check(r["prog"] and r["ag"] > 100 and r["evs"] > 3, f"al volver a abrir, el plan y la agenda se cargan desde IndexedDB {r}")
        # Marca
        await pg.evaluate("(S.logs[addDays(todayK(),-1)]={}).fr={v:0,steps:getH('fr').steps.map(s=>s.id)};save();go('hoy')"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("({plus:getComputedStyle(document.querySelector('#v-hoy .icon-btn.acc')).backgroundImage,secs:[...document.querySelectorAll('#hoyBody .sec:not(.sec-btn)')].map(s=>s.textContent.trim()),ic:document.querySelectorAll('#hoyBody .sec .sec-ic svg').length})")
        check("gradient" in r["plus"] and r["ic"] >= 1 and not any(ch in "".join(r["secs"]) for ch in "☀🌤🌙"), f"botón + de marca y franjas con iconos dibujados {r['secs'][:2]}")
        r = await pg.evaluate("[...document.querySelectorAll('#hoyBody .banner, #sheetBody .banner')].map(b=>b.firstElementChild&&b.firstElementChild.className)")
        check(all(x == "ri" for x in r), f"los avisos usan iconos dibujados {r}")
        check(not errs, f"sin errores de JavaScript {errs[:2]}")
        await b.close()

asyncio.run(main())
print("\nRESULTADO:", "OK" if not fails else f"{len(fails)} fallos"); sys.exit(1 if fails else 0)
