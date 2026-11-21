"""Pruebas de la v1.18 (reevaluación, trozo 2: Hoy inteligente) en un iPhone 13 simulado a las 19:30 de un martes."""
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
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-24T19:30:00+01:00")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(1500)
        # Francés (mañana) hecho; Inglés (mañana) pendiente
        await pg.evaluate("""(()=>{const t=todayK();S.logs={};S.checkins={[t]:{sleep:4,energy:4}};(S.logs[t]={}).fr={v:0,steps:getH('fr').steps.map(s=>s.id)};save();sel=t;go('hoy')})()""")
        await pg.wait_for_timeout(300)
        secs = await pg.evaluate("[...document.querySelectorAll('#hoyBody .sec')].map(s=>s.textContent.trim())")
        check(secs and secs[0].startswith("Resto del día") and "Recolocar" in secs[0], f"v1.32: una sola línea del día con «Recolocar» para lo atrasado {secs[:2]}")
        r = await pg.evaluate("(()=>{const l=[...document.querySelectorAll('#hoyBody .tlr.late')].map(e=>e.querySelector('.hc')&&e.querySelector('.hc').id);return l})()")
        check("hc-en" in r or await pg.evaluate("!!document.querySelector('.hc.hero#hc-en')"), f"lo pendiente de la mañana sale marcado como atrasado (hora en ámbar) o como «Pendiente» arriba {r}")
        r = await pg.evaluate("[!document.querySelector('#hc-fr'),[...document.querySelectorAll('#hoyBody .sec-btn')].map(b=>b.textContent.trim())]")
        check(r[0] and any(x.startswith("✅ Hechos hoy (1)") for x in r[1]), f"lo hecho se pliega en «Hechos hoy» {r[1]}")
        await pg.locator(".sec-btn").tap(); await pg.wait_for_timeout(300)
        check(await pg.evaluate("!!document.querySelector('#hc-fr')"), "«Ver» despliega lo hecho")
        # marcar → baja a Hechos
        await pg.evaluate("act('en')"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("[...document.querySelectorAll('#hoyBody .sec-btn')].map(b=>b.textContent.trim())[0]")
        check(r.startswith("✅ Hechos hoy (2)"), f"al marcar, pasa a «Hechos hoy» ({r})")
        # Después: sin comidas ni trayectos
        r = await pg.evaluate("(()=>{const d=document.createElement('div');d.innerHTML=nowCard(todayK());const n=d.querySelector('.now-row.next b');return n?n.textContent:''})()")
        check(r and not any(x in r for x in ("Merienda", "Cena", "Comida", "margen", "Trayecto")), f"«Después» es el siguiente hábito u obligación ({r.strip()})")
        # cuenta atrás: una meta completa
        r = await pg.evaluate("(()=>{const d=document.createElement('div');d.innerHTML=countdownRow();return [d.querySelectorAll('span').length,d.textContent]})()")
        check(r[0] == 1 and "+" in r[1], f"la cuenta atrás enseña una meta completa y cuántas más hay ({r[1].strip()})")
        # volver a hoy
        await pg.evaluate("wkShift(1)"); await pg.wait_for_timeout(200)
        r = await pg.evaluate("[document.querySelector('#wkLbl').classList.contains('away'),document.querySelector('#wkLbl').textContent]")
        check(r[0] and "Volver a hoy" in r[1], f"en otra semana se ve «Volver a hoy» ({r[1]})")
        await pg.locator("#wkLbl").tap(); await pg.wait_for_timeout(200)
        check(await pg.evaluate("sel===todayK()"), "y al tocarlo vuelves a hoy")
        # otro día (pasado): franjas en orden normal
        await pg.evaluate("pick(addDays(todayK(),-1))"); await pg.wait_for_timeout(200)
        secs = await pg.evaluate("[...document.querySelectorAll('#hoyBody .sec:not(.sec-btn)')].map(s=>s.textContent.trim())")
        check(not any("pendiente" in x for x in secs), f"los demás días, franjas en orden normal {secs[:3]}")
        check(not errs, f"sin errores de JavaScript {errs[:2]}")
        await b.close()

asyncio.run(main())
print("\nRESULTADO:", "OK" if not fails else f"{len(fails)} fallos"); sys.exit(1 if fails else 0)
