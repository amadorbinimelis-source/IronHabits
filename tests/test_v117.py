"""Pruebas de la v1.17 (reevaluación, trozo 1): eliminar/editar con copia y deshacer, áreas táctiles en TODAS las hojas,
primera copia del día, la tarjeta deslizada no se cierra sola y el plan sin instrucciones antiguas."""
import asyncio, sys
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

SMALL = """(sel)=>[...document.querySelectorAll(sel+' button,'+sel+' a,'+sel+' input,'+sel+' select,'+sel+' textarea')].filter(e=>{
  if(!e.offsetParent||e.closest('.ag-day,.agw,.hm,.hm-big,#hapticSw,.hc-plan,.chk'))return false;const r=e.getBoundingClientRect();return r.width&&(r.width<43.5||r.height<43.5);})
  .map(e=>(e.className||e.tagName)+' '+Math.round(e.getBoundingClientRect().width)+'x'+Math.round(e.getBoundingClientRect().height))"""
SHEETS = {"menú": "cardMenu('fr')", "apuntar": "logSheet('fuerza',todayK())", "mover": "evSheet(todayK(),'h:fr')", "detalle": "openDetail('en')",
          "plan completo": "fullPlan('fr')", "revisión": "reviewSheet()", "pausa": "pauseSheet()", "nube": "cloudSheet()", "copias": "snapSheet()",
          "simulacro": "mockSheet()", "notas": "NQ='';notesSheet()", "cuenta atrás": "countdownSheet()",
          "avisos": "S.checkins={};S.reviews={};render();noticesSheet()", "exportar ics": "icsSheet()", "suscribir": "subscribeSheet()", "más calendario": "calMoreSheet()",
          "copia": "backupSheet()", "borrar": "wipe()", "extra": "extraSheet(todayK())", "plan del día": "sel=todayK();dayPlanSheet('fr')",
          "editor": "openEditor('fr')", "rpe": "rpeSheet('boxeo',todayK())", "novedades": "historySheet()"}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid")
        await ctx.add_init_script("Object.defineProperty(navigator,'standalone',{get:()=>true})")
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-24T19:30:00+01:00")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(1500)
        await pg.evaluate("""(()=>{const t=todayK();S.logs={};(S.logs[addDays(t,-1)]={}).fr={v:0,steps:getH('fr').steps.map(s=>s.id),note:'hola'};agSet(t,'h:dx',{cancel:true,reason:'x'});
          S.pauses=[{id:'pz1',from:t,to:addDays(t,3),reason:'prueba',habits:['dx']}];save();sel=t;go('hoy')})()""")
        await pg.wait_for_timeout(5000)  # deja que se guarde la primera copia del día

        # Áreas táctiles en todas las pantallas y hojas
        bad = {}
        for v in ("hoy", "agenda", "prog", "set"):
            await pg.evaluate(f"go('{v}')"); await pg.wait_for_timeout(250)
            sm = await pg.evaluate(SMALL, f"#v-{v}")
            if sm: bad[v] = sm[:3]
        for n, js in SHEETS.items():
            await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(330)
            await pg.evaluate(js); await pg.wait_for_timeout(330)
            sm = await pg.evaluate(SMALL, "#sheet")
            if sm: bad[n] = sm[:3]
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(330)
        check(not bad, f"todos los botones de las 4 pantallas y {len(SHEETS)} hojas miden 44 px o más {bad}")

        # Primera copia del día
        r = await pg.evaluate("snapList().then(a=>a.map(x=>x.id))")
        check(any(x.startswith("dia-") for x in r) and any(x.startswith("auto-") for x in r), f"se guardan la primera y la última copia del día {r}")

        # Eliminar: copia + deshacer con todo su historial
        await pg.evaluate("go('prog');(()=>{deleteH('fr');})()"); await pg.wait_for_timeout(150); await pg.evaluate("dlgDone(true)"); await pg.wait_for_timeout(500)
        r = await pg.evaluate("[!!getH('fr'),Object.values(S.logs).some(d=>d.fr)]")
        snaps = await pg.evaluate("snapList().then(a=>a.filter(x=>x.kind==='pre').map(x=>x.reason))")
        check(r == [False, False] and any("eliminar «Francés»" in x for x in snaps), f"eliminar guarda antes una copia {snaps[:2]}")
        await pg.evaluate("toastAct(0)"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("[!!getH('fr'),Object.values(S.logs).some(d=>d.fr&&d.fr.note==='hola'),!!getH('fr').plan.program,S.habits.findIndex(h=>h.id==='fr')]")
        check(r[0] and r[1] and r[2] and r[3] == 2, f"«Deshacer» recupera el hábito, su historial, su plan y su posición {r}")
        # Editar: deshacer
        await pg.evaluate("openEditor('fr');D.name='Francés editado';edSave()"); await pg.wait_for_timeout(300)
        await pg.evaluate("toastAct(0)"); await pg.wait_for_timeout(300)
        check(await pg.evaluate("getH('fr').name") == "Francés", "deshacer la edición de un hábito")
        # Archivar: deshacer
        await pg.evaluate("archiveH('fr')"); await pg.wait_for_timeout(200); await pg.evaluate("toastAct(0)"); await pg.wait_for_timeout(200)
        check(await pg.evaluate("!getH('fr').archived"), "deshacer archivar")

        # La tarjeta deslizada no se cierra al repintar cada minuto
        await pg.evaluate("go('hoy')"); await pg.wait_for_timeout(300)
        await pg.evaluate("(()=>{const c=document.querySelector('.hc-in[data-swipe]');c.classList.add('open');c.style.transform='translateX(-168px)';})()")
        await pg.clock.run_for(65000); await pg.wait_for_timeout(300)
        check(await pg.evaluate("!!document.querySelector('.hc-in.open')"), "una tarjeta deslizada sigue abierta al pasar el minuto")

        # Plan sin instrucciones antiguas
        r = await pg.evaluate("JSON.stringify(getH('en').plan.program).includes('toca «Inglés» → 📘 Guía')")
        check(not r and await pg.evaluate("S.packs.amador") >= 12, "el plan ya no dice «toca Inglés → Guía» (plan v12)")
        check(not errs, f"sin errores de JavaScript {errs[:2]}")
        await b.close()

asyncio.run(main())
print("\nRESULTADO:", "OK" if not fails else f"{len(fails)} fallos"); sys.exit(1 if fails else 0)
