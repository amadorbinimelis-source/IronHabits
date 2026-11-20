"""Pruebas de la v1.25: modo «Empezar» (anillo de progreso que se mueve al tachar, barra de tiempo, pregunta si
terminas antes de tiempo, minutos que se acumulan) y horas de Inglés y Francés en Progreso."""
import asyncio, sys
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

RING = "(()=>{const L=[...document.querySelectorAll('#foRing svg circle')];if(L.length<2)return 0;const c=L[1],C=parseFloat(c.getAttribute('stroke-dasharray'));return (C-parseFloat(c.getAttribute('stroke-dashoffset')))/C})()"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid", service_workers="block")
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-24T09:30:00+01:00")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(2500)
        await pg.evaluate("S.logs={};S.focus=null;save();sel=todayK();focusMode('fr')"); await pg.wait_for_timeout(400)
        t = await pg.inner_text("#focus")
        check("0%" in t and "0 de 3 pasos" in t, "el anillo muestra el progreso de los pasos (0 %)")
        check(await pg.evaluate("!!document.querySelector('#foBar')") and "de 45 min" in t, "barra de tiempo hasta los 45 min previstos")
        r0 = await pg.evaluate(RING)
        await pg.locator("#focus .step").nth(0).tap(); await pg.wait_for_timeout(300)
        r1 = await pg.evaluate(RING); t = await pg.inner_text("#focus")
        check(r0 == 0 and abs(r1 - 1/3) < .01 and "33%" in t, f"al tachar un paso el anillo avanza ({r0:.2f}→{r1:.2f})")
        await pg.locator("#focus .step").nth(0).tap(); await pg.wait_for_timeout(300)
        check(await pg.evaluate(RING) == 0, "y retrocede al destachar")
        await pg.clock.run_for(10 * 60 * 1000); await pg.wait_for_timeout(300)
        w = await pg.evaluate("parseFloat(document.querySelector('#foBar').style.width)")
        check(20 < w < 25, f"la barra de tiempo se llena con el tiempo (10 de 45 min → {w:.0f} %)")
        for i in range(3): await pg.locator("#focus .step").nth(i).tap(); await pg.wait_for_timeout(200)
        a = await pg.evaluate("!document.querySelector('#foAsk').hidden"); t = await pg.inner_text("#foAsk")
        check(a and "¿Ya has terminado?" in t and "10 min" in t, "todo tachado antes de tiempo → pregunta si ya has terminado")
        await pg.locator("#foAsk .btn.ghost").tap(); await pg.wait_for_timeout(200)
        check(await pg.evaluate("document.querySelector('#foAsk').hidden&&!!document.querySelector('#focus.on')"), "«Sigo un rato» vuelve a la sesión")
        await pg.locator("#focus .fo-ft .btn.pri").tap(); await pg.wait_for_timeout(300)
        m = await pg.evaluate("[(entry(getH('fr'),todayK())||{}).mins,isDone(getH('fr'),todayK()),!!S.focus]")
        check(m == [10, True, False], f"«Terminar» guarda los minutos de la sesión {m}")
        # Salir a medias y volver: no cuenta dos veces
        await pg.evaluate("focusMode('en')"); await pg.wait_for_timeout(300)
        await pg.clock.run_for(8 * 60 * 1000); await pg.locator("#focus .fo-x").tap(); await pg.wait_for_timeout(200)
        await pg.evaluate("focusMode('en')"); await pg.wait_for_timeout(300)
        await pg.clock.run_for(5 * 60 * 1000); await pg.wait_for_timeout(1200)
        c = await pg.inner_text("#foClock")
        await pg.locator("#focus .fo-x").tap(); await pg.wait_for_timeout(200)
        m = await pg.evaluate("(entry(getH('en'),todayK())||{}).mins")
        check(c.startswith("13:") and m == 13, f"salir y volver suma sin contar dos veces (reloj {c}, {m} min)")
        # tiempo cumplido sin pasos → aviso
        await pg.evaluate("focusMode('en')"); await pg.wait_for_timeout(300)
        await pg.clock.run_for(33 * 60 * 1000); await pg.wait_for_timeout(1300)
        check(await pg.evaluate("document.querySelector('#foTime').classList.contains('full')") and "Tiempo cumplido" in await pg.inner_text("#toast"), "al llegar al tiempo previsto, la barra se pone verde y avisa")
        await pg.locator("#focus .fo-x").tap(); await pg.wait_for_timeout(200)
        # Horas
        await pg.evaluate("(()=>{const f=getH('fr');for(let i=1;i<=14;i++){const k=addDays(todayK(),-i);(S.logs[k]=S.logs[k]||{}).fr=i%2?{v:0,steps:f.steps.map(s=>s.id),mins:45}:{v:0,steps:f.steps.map(s=>s.id)};}save();go('prog')})()"); await pg.wait_for_timeout(400)
        t = await pg.inner_text("#statsBody")
        check("horas de idiomas" in t.lower() and "Francés" in t and "Inglés" in t and "Media semanal" in t, "Progreso: horas de Inglés y Francés con total y media semanal")
        x = await pg.evaluate("hoursOf(getH('fr'))")
        check(x["real"] == 7 * 45 + 10 and x["est"] == 7 * 45 and x["weeks"] == 3, f"cuenta cronometradas y estimadas {x}")
        check(not await pg.evaluate("S.habits.filter(h=>!['fr','en'].includes(h.id)).some(h=>document.querySelector('#statsBody').textContent.includes(h.name+'Total'))"), "solo Inglés y Francés")
        await pg.evaluate("openDetail('fr')"); await pg.wait_for_timeout(300)
        check("horas de estudio" in (await pg.inner_text("#sheetBody")).lower(), "y en el detalle del hábito")
        await pg.evaluate("closeSheet();openDetail('fuerza')"); await pg.wait_for_timeout(300)
        check("horas de estudio" not in (await pg.inner_text("#sheetBody")).lower(), "los demás hábitos no tienen recuento de horas")
        check(await pg.evaluate("APP_VERSION") >= "1.25", "versión 1.25")
        check(not errs, f"sin errores de JS {errs[:3]}")
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
    print("FALLAN:" if fails else "TODO OK", fails if fails else "")
    sys.exit(1 if fails else 0)
