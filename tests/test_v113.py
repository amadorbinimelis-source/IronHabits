"""Pruebas de la v1.13 (trozo 4 de la auditoría: navegación y pantalla Hoy) en un iPhone 13 simulado.
4 pestañas, Hoy con los hábitos a la vista, una sola tarjeta destacada y campana, plan al tocar el nombre,
menú de 5 opciones, hoja «Apuntar», deslizar para Saltar o Mañana, Progreso y Ajustes sin duplicados."""
import asyncio, sys
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        # Hoy cambia según la hora: se prueba por la noche (la tarjeta de mañana es la más alta)
        ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid")
        await ctx.add_init_script("Object.defineProperty(navigator,'standalone',{get:()=>true})")
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-19T21:30:00+01:00"); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(1500)
        await pg.evaluate("S.habits.forEach(h=>h.start=addDays(todayK(),-30));S.logs={};S.checkins={};S.reviews={};save();sel=todayK();go('hoy')"); await pg.wait_for_timeout(300)

        # Navegación
        r = await pg.evaluate("[...document.querySelectorAll('nav button')].map(b=>b.textContent.trim())")
        check(r == ["Hoy", "Agenda", "Progreso", "Ajustes"], f"4 pestañas {r}")
        await pg.evaluate("go('hab')"); check(await pg.evaluate("view") == "prog", "las rutas antiguas (Hábitos, Stats) llevan a Progreso")
        await pg.evaluate("go('hoy')"); await pg.wait_for_timeout(200)

        # Hoy: lo principal a la vista
        r = await pg.evaluate("(()=>{const e=document.querySelector('.hc');const nav=document.querySelector('nav').getBoundingClientRect().top;return e?[Math.round(e.getBoundingClientRect().top),Math.round(nav)]:null})()")
        check(r and r[0] < r[1] - 60, f"el primer hábito se ve sin hacer scroll (empieza en {r and r[0]} px, la barra en {r and r[1]})")
        n = await pg.evaluate("document.querySelectorAll('#hoyBody > .banner, #hoyBody > .now-card, #hoyBody > .card:not(.wk-card):not(.note):not(.empty)').length")
        check(n <= 1, f"una sola tarjeta destacada arriba ({n})")
        r = await pg.evaluate("[document.querySelectorAll('#hoyBody .sec')[0].textContent, !!document.querySelector('.wk-card'), !document.querySelector('.wk-card .wk-row')]")
        check(r[0].startswith(("Por la", "En cualquier")) and r[1] and r[2], f"franjas «Por la…» y total semanal plegado {r[0]}")
        await pg.evaluate("S.reviews={};S.settings.lastExport=null;for(let i=1;i<6;i++)S.logs[addDays(todayK(),-i)]={fr:{v:0,steps:[]}};save();render()")
        r = await pg.evaluate("[!document.querySelector('#hoyBell').hidden, document.querySelector('#hoyBellN').textContent]")
        check(r[0] and int(r[1] or 0) >= 1, f"la campana guarda el resto de avisos ({r[1]})")
        await pg.evaluate("noticesSheet()"); await pg.wait_for_timeout(300)
        check(await pg.evaluate("document.querySelectorAll('#sheetBody .banner, #sheetBody .card').length") >= 1, "la campana enseña los avisos")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(300)

        # Tarjeta: tocar el nombre despliega/pliega el plan; ⋯ abre el menú de 5
        await pg.evaluate("S.logs={};save();render()"); await pg.wait_for_timeout(200)
        a = await pg.evaluate("!!document.querySelector('#hc-fr .hc-plan')")
        await pg.locator("#hc-fr .hc-info").tap(); await pg.wait_for_timeout(300)
        bb = await pg.evaluate("!!document.querySelector('#hc-fr .hc-plan')")
        check(a and not bb and not await pg.evaluate("$('#sheet').classList.contains('on')"), "tocar el nombre pliega el plan (sin abrir menús)")
        await pg.locator("#hc-fr .hc-info").tap(); await pg.wait_for_timeout(300)
        await pg.locator("#hc-fr .hc-menu").tap(); await pg.wait_for_timeout(400)
        r = await pg.evaluate("[...document.querySelectorAll('#sheetBody .row-btn')].map(b=>b.querySelector('div').firstChild.textContent.trim())")
        check(len(r) == 6 and r[-1] == "Eliminar hábito", f"menú del hábito: 5 opciones + «Eliminar hábito» al final {r}")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(300)

        # Apuntar: tiempo + progreso + nota en una hoja
        await pg.evaluate("logSheet('fuerza',todayK())"); await pg.wait_for_timeout(300)
        await pg.fill("#mnH", "1"); await pg.fill("#mnM", "15"); await pg.fill("#mtNote", "buena sesión")
        await pg.evaluate("saveLog('fuerza',todayK(),+document.querySelector('#mnH').defaultValue*60+ +document.querySelector('#mnM').defaultValue)"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("(()=>{const e=entry(getH('fuerza'),todayK());return e&&[e.mins,e.note,isDone(getH('fuerza'),todayK())]})()")
        check(r == [75, "buena sesión", True], f"«Apuntar» guarda tiempo y nota {r}")
        # B16: en una checklist, apuntar tiempo no la completa
        await pg.evaluate("logSheet('fr',todayK())"); await pg.wait_for_timeout(300)
        await pg.fill("#mnH", "0"); await pg.fill("#mnM", "20")
        await pg.evaluate("saveLog('fr',todayK(),-1)"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("[minsOf(getH('fr'),todayK()),isDone(getH('fr'),todayK())]")
        check(r == [20, False], f"en una checklist el tiempo suma pero no la completa {r}")

        # Deslizar a la izquierda → Saltar
        await pg.evaluate("S.logs={};save();render()"); await pg.wait_for_timeout(200)
        cdp = await ctx.new_cdp_session(pg)
        async def touch(t, x=0, y=0): await cdp.send("Input.dispatchTouchEvent", {"type": t, "touchPoints": [] if t == "touchEnd" else [{"x": x, "y": y}]})
        card = pg.locator("#hc-fr .hc-in"); await card.scroll_into_view_if_needed(); bx = await card.bounding_box()
        x0, y0 = bx["x"] + bx["width"] - 30, bx["y"] + 30
        await touch("touchStart", x0, y0)
        for i in range(1, 11): await touch("touchMove", x0 - i * 20, y0 + 2); await pg.wait_for_timeout(16)
        await touch("touchEnd"); await pg.wait_for_timeout(400)
        check(await pg.evaluate("document.querySelector('#hc-fr .hc-in').classList.contains('open')"), "deslizar a la izquierda enseña Mañana / Saltar")
        await pg.locator("#hc-fr .hc-act.skip").tap(); await pg.wait_for_timeout(400)
        r = await pg.evaluate("[!!agOv(todayK(),'h:fr')&&agOv(todayK(),'h:fr').cancel, dayHabits(todayK()).some(h=>h.id==='fr')]")
        check(r == [True, False], f"«Saltar» lo quita de hoy {r}")
        await pg.evaluate("undoAct()[1]()"); await pg.wait_for_timeout(200)
        check(await pg.evaluate("dayHabits(todayK()).some(h=>h.id==='fr')"), "y se puede deshacer")

        # Progreso
        await pg.evaluate("go('prog')"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("({kpi:document.querySelectorAll('#v-prog .kpi').length,hab:document.querySelectorAll('#v-prog .hl').length,rank:!!document.querySelector('#v-prog .rk'),bars:!!document.querySelector('#v-prog .bars'),mock:document.querySelector('#v-prog').textContent.includes('Simulacros')})")
        check(r["kpi"] >= 4 and r["hab"] >= 5 and not r["rank"] and r["bars"] and not r["mock"], f"Progreso: resumen, tus hábitos y gráficas, sin duplicados {r}")
        # Ajustes y Agenda sin duplicados
        await pg.evaluate("go('set')"); await pg.wait_for_timeout(300)
        t = await pg.inner_text("#setBody")
        check(t.count("Suscribir el calendario") == 1 and "Exportar unas semanas" not in t and "Descargar el archivo" not in t, "Ajustes: una forma de calendario y una de copia")
        await pg.evaluate("WKX.open=true;sel='2026-11-23';go('agenda')"); await pg.wait_for_timeout(300)
        check(not await pg.evaluate("!!document.querySelector('.ag-legend')"), "Agenda sin leyenda")
        # Ejemplos sin duplicar y borrar sin perder el plan
        await pg.evaluate("go('hoy');loadExamples()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("(()=>{const n={};S.habits.forEach(h=>{const k=h.name.split(' ')[0].toLowerCase();n[k]=(n[k]||0)+1});return [Object.values(n).every(v=>v===1),S.habits.filter(h=>h.example).map(h=>h.name)]})()")
        check(r[0] and "Boxeo" not in r[1] and "Francés" not in r[1], f"los ejemplos no duplican hábitos del plan {r[1]}")
        await pg.evaluate("(()=>{removeExamples();})()"); await pg.wait_for_timeout(150); await pg.evaluate("dlgDone(true)"); await pg.wait_for_timeout(500)
        check(await pg.evaluate("!S.habits.some(h=>h.example)&&!!getH('fr')"), "«Quitar los hábitos de ejemplo» deja solo tu plan")
        await pg.evaluate("(S.logs[todayK()]={}).fr={v:0,steps:[getH('fr').steps[0].id]};S.notes[todayK()]='x';agSet('2026-11-25','h:fr',{cancel:true});save()")
        await pg.evaluate("(()=>{wipeLogs();})()"); await pg.wait_for_timeout(150); await pg.evaluate("dlgDone(true)"); await pg.wait_for_timeout(500)
        r = await pg.evaluate("({l:Object.keys(S.logs).length,n:Object.keys(S.notes).length,a:Object.keys(S.agenda).length,h:S.habits.length,ag:Object.keys(S.agendaBase).length>100,p:!!getH('en').plan.program})")
        check(r["l"] == 0 and r["n"] == 0 and r["a"] == 0 and r["h"] >= 6 and r["ag"] and r["p"], f"«Borrar solo mis registros» conserva hábitos, plan y agenda {r}")
        await pg.evaluate("(()=>{wipeAll();})()"); await pg.wait_for_timeout(150); await pg.evaluate("dlgDone(true)"); await pg.wait_for_timeout(2500)
        r = await pg.evaluate("({h:S.habits.length,ag:Object.keys(S.agendaBase).length>100,p:!!(getH('en')&&getH('en').plan.program)})")
        check(r["h"] >= 6 and r["ag"] and r["p"], f"«Borrar todo» vuelve a cargar el plan inicial y la agenda {r}")
        check(not errs, f"sin errores de JavaScript {errs[:2]}")
        await b.close()

asyncio.run(main())
print("\nRESULTADO:", "OK" if not fails else f"{len(fails)} fallos"); sys.exit(1 if fails else 0)
