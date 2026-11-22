"""Pruebas de la v1.33: interruptores de Ajustes que se ven bien, fuera el sonido al abrir,
comidas en la línea del día (sin «Descanso») y limpieza de hábitos repetidos sin usar."""
import asyncio, sys, json
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
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-25T06:30:00+01:00")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(2500)
        await pg.evaluate("localStorage.setItem('ironhabits_tour',JSON.stringify({done:true,minis:{}}));sel=todayK();go('hoy')"); await pg.wait_for_timeout(300)

        # ── comidas en la línea del día ──
        r = await pg.evaluate("[...document.querySelectorAll('#hoyBody .tl-meal')].map(b=>b.textContent.trim())")
        check(any("Desayuno" in x for x in r) and any("Comida" in x for x in r) and any("Cena" in x for x in r), f"desayuno, comida y cena en la línea del día {r}")
        r2 = await pg.evaluate("[...document.querySelectorAll('#hoyBody .tl-free')].map(b=>b.textContent.trim())")
        check(not any("Descanso" in x for x in r2) and not any("Merienda" in x for x in r), f"sin «Descanso» ni merienda {r2}")
        t = await pg.evaluate("[...document.querySelectorAll('#hoyBody .tlr')].map(e=>e.querySelector('.tlr-t').textContent).filter(Boolean)")
        check(t == sorted(t), f"todo en orden de hora {t}")
        await pg.locator("#hoyBody .tl-meal").first.tap(); await pg.wait_for_timeout(500)
        check(await pg.evaluate("document.querySelector('#sheet').classList.contains('on')"), "tocar una comida abre su hoja (para cambiarla)")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(400)
        await pg.clock.set_fixed_time("2026-11-25T15:00:00+01:00"); await pg.evaluate("render()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("[...document.querySelectorAll('#hoyBody .tl-meal')].map(b=>b.textContent.trim())")
        check(not any("Desayuno" in x for x in r) and any("Cena" in x for x in r), f"a las 15:00 ya no salen las comidas pasadas {r}")

        # ── interruptores de Ajustes ──
        await pg.evaluate("go('set')"); await pg.wait_for_timeout(300)
        sw = "#setBody label:has-text('Vibración al tocar') input"
        look = "(()=>{const i=[...document.querySelectorAll('#setBody label')].find(l=>l.textContent.includes('Vibración al tocar')).querySelector('input');const cs=getComputedStyle(i),a=getComputedStyle(i,'::after');return [i.checked,cs.backgroundColor,a.left]})()"
        on = await pg.evaluate(look)
        await pg.locator(sw).tap(); await pg.wait_for_timeout(300)
        off = await pg.evaluate(look)
        check(on[0] and not off[0] and on[1] != off[1] and on[2] == "21px" and off[2] == "3px", f"encendido y apagado se ven distintos {on} {off}")
        check(await pg.evaluate("S.settings.tapHaptic===false"), "y el ajuste cambia de verdad")
        await pg.locator(sw).tap(); await pg.wait_for_timeout(300)
        check(await pg.evaluate("S.settings.tapHaptic===true") and (await pg.evaluate(look))[2] == "21px", "otro toque lo vuelve a encender")
        r = await pg.evaluate("[...document.querySelectorAll('#setBody input[type=checkbox][switch]')].every(i=>getComputedStyle(i,'::after').left===(i.checked?'21px':'3px'))")
        check(r, "todos los interruptores enseñan su estado real")
        t = await pg.inner_text("#setBody")
        check("Sonido al abrir" not in t and await pg.evaluate("typeof fxHello==='undefined'"), "fuera el sonido al abrir (ajuste y código)")

        # ── limpieza de repetidos (datos guardados con el esquema 4) ──
        st = await pg.evaluate("""(()=>{const o=JSON.parse(localStorage.getItem('ironhabits_v1'));o.schema=4;o.settings.bootSound=true;
          const mk=(id,name,e)=>Object.assign(blankHabit(),{id,name,emoji:e,color:'#A855F7',start:'2026-11-19'});
          o.habits.push(mk('gym1','Gimnasio','🧘'),mk('est2','Estudio para los exámenes','📚'),mk('gym2','Gimnasio','🏋️'),mk('leer','Leer','📖'));
          o.logs['2026-11-20']={gym2:true,leer:true};o.logs['2026-11-21']={gym1:true,fuerza:false};localStorage.setItem('ironhabits_v1',JSON.stringify(o));return o.habits.length})()""")
        await pg.reload(); await pg.wait_for_timeout(2500)
        r = await pg.evaluate("({l20:S.logs['2026-11-20'],l21:S.logs['2026-11-21'],ids:S.habits.map(h=>h.id),schema:S.schema,t1:!!(S.touch||{})['h:gym1'],t2:!!(S.touch||{})['h:est2'],bs:'bootSound' in S.settings,toast:$('#toast').textContent})")
        check(not {"gym1","gym2","est2"} & set(r["ids"]) and "estudio" in r["ids"] and "fuerza" in r["ids"], f"se van los «Gimnasio» y el «Estudio para los exámenes» repetido {r['ids']}")
        check("leer" in r["ids"], "los que no son repetidos se quedan")
        check(r["l20"] == {"fuerza": True, "leer": True} and r["l21"] == {"fuerza": False}, f"los registros pasan al hábito del plan sin pisar los suyos {r['l20']} {r['l21']}")
        check(r["t1"] and r["t2"] and r["schema"] == 5 and not r["bs"], f"quedan marcados como borrados para la nube y el ajuste viejo fuera {r['schema']}")
        await pg.wait_for_timeout(800)
        check("repetidos" in await pg.evaluate("$('#toast').textContent"), "y te avisa")
        # la nube no los resucita
        r = await pg.evaluate("""(()=>{const L=JSON.parse(JSON.stringify(S));const R=JSON.parse(JSON.stringify(S));R.habits.push(Object.assign(blankHabit(),{id:'gym1',name:'Gimnasio'}));R.touch={...R.touch,'h:gym1':1};
          return mergeStates(L,R,false).habits.some(h=>h.id==='gym1')})()""")
        check(r is False, "al juntar con la nube no vuelven")
        check(await pg.evaluate("APP_VERSION") >= "1.33", "versión 1.33")
        check(not errs, f"sin errores de JS {errs[:2]}")
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(1 if fails else 0)
