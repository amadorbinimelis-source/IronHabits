"""Pruebas de la v1.30: la Agenda es solo la Semana (sin pestañas Día / 3 días).
El día ancho enseña todo lo del día (comidas, tiempo libre de fondo, «sin hora» tocables, línea de ahora)."""
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
        ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid", service_workers="block")
        await ctx.add_init_script("Object.defineProperty(navigator,'standalone',{get:()=>true})")
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-25T09:10:00+01:00")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(2500)
        await pg.evaluate("""localStorage.setItem('ironhabits_tour',JSON.stringify({done:true,minis:{}}));S.settings.bootSound=false;
          S.habits.push(Object.assign(blankHabit(),{id:'leer',name:'Leer',emoji:'📖',color:'#F472B6',start:addDays(todayK(),-10)}));save();sel=todayK();go('hoy')""")
        await pg.wait_for_timeout(300)
        # Hoy: filas finas que se despliegan al tocarlas
        r = await pg.evaluate("[...document.querySelectorAll('.tlr .hc.thin')].map(c=>[c.id,c.classList.contains('exp'),!!c.querySelector('.hc-plan'),getComputedStyle(c.querySelector('.hc-menu')).display])")
        check(len(r) >= 2 and all(not e and not pl and d == 'none' for _, e, pl, d in r), f"filas finas: sin plan ni ⋯ hasta tocarlas {r[:2]}")
        hid = r[0][0]
        await pg.locator(f"#{hid} .hc-info").tap(); await pg.wait_for_timeout(300)
        r2 = await pg.evaluate(f"(()=>{{const c=document.querySelector('#{hid}');return [c.classList.contains('exp'),getComputedStyle(c.querySelector('.hc-menu')).display!=='none',!!c.querySelector('.hc-plan,.steps,.start-btn')]}})()")
        check(r2 == [True, True, True], f"tocar la fila la despliega con ⋯ y su contenido {r2}")
        await pg.locator(f"#{hid} .hc-info").tap(); await pg.wait_for_timeout(300)
        check(await pg.evaluate(f"!document.querySelector('#{hid}').classList.contains('exp')"), "otro toque la vuelve a plegar")
        await pg.locator("nav button[data-v=agenda]").tap(); await pg.wait_for_timeout(400)
        r = await pg.evaluate("({tabs:!!document.querySelector('.ag-bar'),seg:document.querySelectorAll('#agBody .seg').length,mini:document.querySelectorAll('.wkm-d').length,title:$('#agTitle').textContent,sub:$('#agSub').textContent})")
        check(not r["tabs"] and r["seg"] == 0 and r["mini"] == 7, f"Agenda: sin pestañas Día / 3 días, empieza en la semana plegada {r}")
        check(r["title"] == "Agenda" and "–" in r["sub"], f"cabecera con el rango de la semana ({r['sub']})")
        # la tira de días de arriba abre ese día en grande
        await pg.locator("#agWeek .wd").nth(4).tap(); await pg.wait_for_timeout(500)
        k4 = await pg.evaluate("addDays(weekStartK(todayK()),4)")
        check(await pg.evaluate(f"WKX.open&&WKX.wide==='{k4}'&&sel==='{k4}'&&!!document.querySelector('.agw-day.wide[data-colk=\"{k4}\"]')"), "tocar un día arriba despliega la semana con ese día en grande")
        # día ancho: ventana de horas de 5 a 24 que se desliza y se abre en las 7:00
        r = await pg.evaluate("(()=>{const sc=$('#agwScroll'),hrs=[...sc.querySelectorAll('.agw-hrs span')].map(s=>+s.textContent);const ev=sc.querySelector('.agw-ev[data-drag]');return {st:sc.scrollTop,sh:sc.scrollHeight,ch:sc.clientHeight,first:hrs[0],last:hrs[hrs.length-1],lo:ev?+ev.dataset.lo:null,hi:ev?+ev.dataset.hi:null}})()")
        check(r["sh"] > r["ch"] + 50 and abs(r["st"] - 80) <= 2, f"el día ancho tiene su ventana de horas y se abre en las 7:00 {r}")
        check(r["first"] == 6 and r["last"] == 24 and r["lo"] == 300 and r["hi"] == 1439, f"se puede bajar/subir de 5 a 24 h y arrastrar en todo ese rango {r}")
        await pg.evaluate("$('#agwScroll').scrollTop=9999"); await pg.wait_for_timeout(200)
        st = await pg.evaluate("$('#agwScroll').scrollTop")
        await pg.locator("#agWeek .wd").nth(3).tap(); await pg.wait_for_timeout(400)
        check(abs(await pg.evaluate("$('#agwScroll').scrollTop") - st) <= 2, "al cambiar de día ancho, la ventana se queda en la misma hora")
        await pg.evaluate("wkWide(WKX.wide)"); await pg.wait_for_timeout(300)
        check(await pg.evaluate("!$('#agwScroll').classList.contains('on')&&WKX.st===null"), "sin día ancho, la semana se ve entera sin ventana")
        await pg.locator("#agWeek .wd").nth(4).tap(); await pg.wait_for_timeout(400)
        # el día ancho enseña todo
        await pg.locator("#agWeek .wd").nth(2).tap(); await pg.wait_for_timeout(500)
        t = await pg.evaluate("todayK()")
        r = await pg.evaluate(f"""(()=>{{const c=document.querySelector('.agw-day.wide[data-colk="{t}"]');const ev=[...c.querySelectorAll('.agw-ev')];
            const allDay=dayEvents('{t}').filter(e=>(e.kind==='habito'||e.kind==='fijo')&&tm(e.end)>tm(e.start)).length;
            return {{n:ev.filter(e=>!e.classList.contains('libre')).length,all:allDay,libre:ev.filter(e=>e.classList.contains('libre')).map(e=>e.getAttribute('aria-label')).slice(0,2),food:ev.some(e=>/🍽|🚶/.test(e.textContent)),
              now:!!c.querySelector('.agw-now'),nt:[...document.querySelectorAll('.agw-nt.wide button')].map(b=>b.textContent)}}}})()""")
        check(r["n"] == r["all"] and r["n"] >= 4 and not r["food"], f"el día ancho enseña hábitos y obligaciones con nombre, sin comidas ni trayectos ({r['n']} de {r['all']})")
        check(len(r["libre"]) >= 1 and "–" in r["libre"][0], f"y el tiempo libre de fondo, con su hora {r['libre']}")
        check(r["now"], "línea roja de la hora actual en hoy")
        check("📖" in r["nt"], f"«sin hora» del día ancho: cada hábito se toca {r['nt']}")
        await pg.locator(".agw-nt.wide button", has_text="📖").tap(); await pg.wait_for_timeout(500)
        check(await pg.evaluate("document.querySelector('#sheet').classList.contains('on')&&$('#sheetBody').textContent.includes('Leer')"), "tocarlo abre su hoja")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(400)
        # el tiempo libre se toca para cambiarlo (y no ensancha)
        await pg.locator(".agw-day.wide .agw-ev.libre").first.tap(); await pg.wait_for_timeout(500)
        check(await pg.evaluate(f"document.querySelector('#sheet').classList.contains('on')&&WKX.wide==='{t}'"), "tocar el tiempo libre abre su hoja")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(400)
        # columnas estrechas: solo lo importante, sin texto
        r = await pg.evaluate("[...document.querySelectorAll('.agw-day:not(.wide) .agw-ev.libre')].every(e=>['','☕'].includes(e.textContent.trim()))")
        check(r, "en los días estrechos el tiempo libre es un contorno (☕ si es largo)")
        # el tutorial de la agenda funciona con la semana
        r = await pg.evaluate("TOUR_STEPS.filter(s=>s.seccion==='agenda').map(s=>s.selector)")
        check(not any(".seg" in x or ".ag-ev" in x for x in r), f"el tutorial ya no usa las pestañas viejas {r}")
        await pg.evaluate("WKX.open=false;WKX.wide=null;renderAgenda()"); await pg.wait_for_timeout(200)
        await pg.evaluate("window.scrollTo(0,120)"); await pg.wait_for_timeout(200); y0 = await pg.evaluate("scrollY")
        await pg.evaluate("document.querySelector('.wk-open').click()"); await pg.wait_for_timeout(900)
        check(abs(await pg.evaluate("scrollY") - y0) < 2, "al desplegar la semana la pantalla no baja sola")
        await pg.evaluate("WKX.open=false;renderAgenda();window.scrollTo(0,0)"); await pg.wait_for_timeout(200)
        check(await pg.evaluate("!!document.querySelector('.wk-open')"), "paso «vista»: la miniatura existe")
        await pg.locator(".wk-open").tap(); await pg.wait_for_timeout(400)
        await pg.locator(".agw-hd.today").tap(); await pg.wait_for_timeout(400)
        check(await pg.evaluate("WKX.wide===todayK()"), "paso «dia»: tocar hoy lo ensancha")
        check(await pg.evaluate("APP_VERSION") >= "1.30", "versión 1.30")
        check(not errs, f"sin errores de JS {errs[:2]}")
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(1 if fails else 0)
