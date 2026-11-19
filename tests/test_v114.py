"""Pruebas de la v1.14 (trozo 5, funciones básicas) en un iPhone 13 simulado:
hora en el editor, cuenta atrás, celebración al cerrar el día, historial de notas y guía de bienvenida."""
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
        ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid")
        await ctx.add_init_script("Object.defineProperty(navigator,'standalone',{get:()=>true})")
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-23T09:00:00+01:00")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(1500)
        await pg.evaluate("S.logs={};S.checkins={'2026-11-23':{sleep:4,energy:4}};save();sel=todayK();go('hoy')")

        # Hora en el editor (hábito propio, sin agenda del plan)
        await pg.evaluate("openEditor()"); await pg.wait_for_timeout(300)
        await pg.fill("#sheetBody input[placeholder^='Ej.: Boxeo']", "Leer")
        r = await pg.evaluate("!!document.querySelector('#sheetBody input[aria-label=\"Hora de inicio\"]')")
        check(r, "el editor de un hábito nuevo tiene campo de hora")
        await pg.evaluate("D.time={start:'21:30',dur:30};edSave()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("""(()=>{const h=S.habits.find(h=>h.name==='Leer');const t=todayK();const ev=dayEvents(t).find(e=>e.id==='h:'+h.id);
          return {ev:ev&&ev.start+'-'+ev.end,mom:momentFor(h,t),ics:buildICS(t,t,false).text.includes('Leer')}})()""")
        check(r["ev"] == "21:30-22:00" and r["mom"] == "noche" and r["ics"], f"con hora sale en la agenda, en su franja y en el calendario {r}")
        await pg.evaluate("openEditor('en')"); await pg.wait_for_timeout(300)
        check("viene de tu agenda" in await pg.inner_text("#sheetBody"), "en un hábito del plan, la hora se cambia desde la agenda")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(300)
        # mover el hábito con hora propia
        r = await pg.evaluate("""(()=>{const h=S.habits.find(h=>h.name==='Leer'),t=todayK();setEvTime(t,'h:'+h.id,'22:00','22:30');const a=habitTime(h,t);return a.start})()""")
        check(r == "22:00", f"cambiar la hora de un hábito propio ({r})")

        # Cuenta atrás
        r = await pg.evaluate("countdowns().map(x=>x.label)")
        check(any("examen" in x.lower() for x in r) and any("B2" in x for x in r), f"cuenta atrás con exámenes y metas {r[:3]}…")
        await pg.evaluate("render()"); await pg.wait_for_timeout(200)
        check(await pg.evaluate("!!document.querySelector('#hoyBody .cd-row')"), "la cuenta atrás sale en Hoy")
        await pg.evaluate("countdownSheet()"); await pg.wait_for_timeout(300)
        check(await pg.evaluate("document.querySelectorAll('#sheetBody .row-btn').length") >= 2, "la hoja de cuenta atrás lista los próximos")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(300)

        # Celebración al completar el día
        await pg.evaluate("""(()=>{const t=todayK();sel=t;S.settings.celebrated={};for(const h of dayHabits(t)){if(h.type==='time'){(S.logs[t]=S.logs[t]||{})[h.id]={v:h.target,steps:[]};}}save();
          const rest=dayHabits(t).filter(h=>!isDone(h,t));for(const h of rest.slice(0,-1)){const e=ens(h,t);if(h.type==='checklist')e.steps=h.steps.map(s=>s.id);else if(h.type==='count')e.v=h.target;else e.v=1;}save();
          const last=rest[rest.length-1];if(last)act(last.id,t);})()"""); await pg.wait_for_timeout(500)
        r = await pg.evaluate("[!!document.querySelector('.celebrate'),dayStats(todayK()).done===dayStats(todayK()).total]")
        check(r == [True, True], f"al completar el día sale la celebración {r}")
        await pg.wait_for_timeout(3200)
        check(not await pg.evaluate("!!document.querySelector('.celebrate')"), "la celebración desaparece sola")
        await pg.evaluate("(()=>{const t=todayK();const h=dayHabits(t)[0];act(h.id,t);act(h.id,t);})()"); await pg.wait_for_timeout(400)
        check(not await pg.evaluate("!!document.querySelector('.celebrate')"), "solo se celebra una vez al día")

        # Historial de notas
        await pg.evaluate("S.notes['2026-11-20']='me molesta la rodilla';(S.logs['2026-11-21']=S.logs['2026-11-21']||{}).boxeo={v:1,steps:[],note:'sparring duro'};save();NQ='';notesSheet()"); await pg.wait_for_timeout(300)
        t = await pg.inner_text("#sheetBody")
        check("rodilla" in t and "sparring" in t, "Tus notas: las del día y las de cada hábito")
        await pg.fill("#nq", "rodilla"); await pg.wait_for_timeout(700)
        t = await pg.inner_text("#sheetBody")
        check("rodilla" in t and "sparring" not in t, "el buscador de notas filtra")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(300)

        check(not errs, f"sin errores de JavaScript {errs[:2]}")
        await b.close()

asyncio.run(main())
print("\nRESULTADO:", "OK" if not fails else f"{len(fails)} fallos"); sys.exit(1 if fails else 0)
