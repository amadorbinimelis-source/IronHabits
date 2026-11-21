"""Pruebas de la v1.29: diseño C (híbrido).
Hoy: tira de la semana con puntitos, tarjeta «Ahora», línea del día con hora, tiempo libre y fichas «sin hora».
Agenda › Semana: miniatura → por horas → día ancho (y vuelta), rachas. Detalle con pasos de hoy, próximas sesiones y meses.
Editor con vista previa en vivo."""
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
          const k=todayK();S.logs={};(S.logs[k]={}).fr={v:0,steps:[getH('fr').steps[0].id]};
          S.habits.push(Object.assign(blankHabit(),{id:'leer',name:'Leer',emoji:'📖',color:'#F472B6',start:addDays(k,-10)}));save();sel=k;go('hoy')""")
        await pg.wait_for_timeout(400)

        # ── Hoy ──
        r = await pg.evaluate("[...document.querySelectorAll('#wkDays .wd')].map((w,i)=>[w.querySelectorAll('.wd-dots i').length,Math.min(6,dayHabits(addDays(weekStartK(sel),i)).length)])")
        check(len(r) == 7 and all(a == b for a, b in r), f"la semana enseña un puntito por hábito de cada día {r[:3]}")
        r = await pg.evaluate("({hero:!!document.querySelector('.hc.hero#hc-en'),tag:(document.querySelector('.hc.hero .hero-tag')||{}).textContent||'',n:document.querySelectorAll('#hc-en').length})")
        check(r["hero"] and "AHORA" in r["tag"] and "quedan" in r["tag"] and r["n"] == 1, f"«Ahora»: Inglés arriba, sin repetirse abajo {r}")
        r = await pg.evaluate("[...document.querySelectorAll('#hoyBody .tlr:not(.free) .tlr-t')].map(e=>e.textContent).filter(Boolean)")
        check(len(r) >= 2 and r[0] <= r[-1], f"cada hábito con su hora a la izquierda {r[:4]}")
        r = await pg.evaluate("[...document.querySelectorAll('#hoyBody .tl-free')].map(e=>e.textContent.trim())")
        check(len(r) >= 1, f"el tiempo libre sale entre los hábitos {r[:2]}")
        check(await pg.evaluate("!!document.querySelector('#hc-fr .hc-fill')"), "Francés a medias enseña el relleno de progreso")
        # fichas sin hora
        check(await pg.evaluate("!!document.querySelector('.ntc#hc-leer') && !document.querySelector('.hc#hc-leer')"), "«Leer» (sin hora, sin plan) sale como ficha")
        await pg.locator(".ntc#hc-leer").tap(); await pg.wait_for_timeout(400)
        r = await pg.evaluate("({d:isDone(getH('leer'),todayK()),on:document.querySelector('.ntc#hc-leer').classList.contains('on'),dup:document.querySelectorAll('#hc-leer').length})")
        check(r["d"] and r["on"] and r["dup"] == 1, f"un toque en la ficha la marca y se queda en su sitio {r}")
        await pg.locator(".ntc#hc-leer").tap(); await pg.wait_for_timeout(400)
        check(await pg.evaluate("!isDone(getH('leer'),todayK())"), "otro toque la desmarca")
        # «Todo hecho» no sale si «Ahora» sigue pendiente
        await pg.evaluate("""const k=todayK();for(const h of dayHabits(k)){if(h.id==='en')continue;const e=ens(h,k);if(h.type==='checklist')e.steps=h.steps.map(s=>s.id);else if(h.type==='check')e.v=1;else e.v=h.target;}save();render()""")
        await pg.wait_for_timeout(300)
        r = await pg.evaluate("[!!document.querySelector('.all-done'),!!document.querySelector('.hc.hero#hc-en')]")
        check(r == [False, True], f"con «Ahora» pendiente no dice «Todo hecho» {r}")
        await pg.evaluate("const h=getH('en'),e=ens(h,todayK());if(h.type==='checklist')e.steps=h.steps.map(s=>s.id);else e.v=h.target;save();render()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("[!!document.querySelector('.all-done'),!!document.querySelector('.hc.hero')]")
        check(r == [True, False], f"todo hecho: desaparece «Ahora» y sale «Todo hecho» {r}")
        await pg.evaluate("S.logs={};save();render()"); await pg.wait_for_timeout(200)
        # otro día: sin «Ahora»
        await pg.evaluate("pick(addDays(todayK(),1))"); await pg.wait_for_timeout(300)
        check(await pg.evaluate("!document.querySelector('.hc.hero')"), "otros días no tienen tarjeta «Ahora»")
        await pg.evaluate("pick(todayK())")

        # ── Agenda › Semana ──
        await pg.evaluate("agView='week';WKX.open=false;go('agenda')"); await pg.wait_for_timeout(400)
        r = await pg.evaluate("({mini:document.querySelectorAll('.wkm-d').length,grid:!!document.querySelector('.agw'),rachas:document.querySelectorAll('.hk').length})")
        check(r["mini"] == 7 and not r["grid"] and r["rachas"] >= 3, f"por defecto: miniatura de 7 días y rachas {r}")
        await pg.locator(".wk-open").tap(); await pg.wait_for_timeout(400)
        r = await pg.evaluate("({grid:!!document.querySelector('.agw.fit'),fits:document.querySelector('#agwWrap').scrollWidth<=document.querySelector('#agwWrap').clientWidth+2,rachas:document.querySelectorAll('.hk').length})")
        check(r["grid"] and r["fits"] and r["rachas"] >= 3, f"al tocarla se despliega por horas en la misma pantalla, sin scroll lateral {r}")
        k3 = await pg.evaluate("addDays(weekStartK(sel),3)")
        await pg.locator(f".agw-hd:has-text('{int(k3[8:])}')").first.tap(); await pg.wait_for_timeout(500)
        r = await pg.evaluate(f"({{w:WKX.wide,cols:document.querySelector('.agw').style.gridTemplateColumns,full:[...document.querySelectorAll('[data-colk=\"{k3}\"] .agw-ev:not(.cmp)')].length,cmp:document.querySelectorAll('.agw-ev.cmp').length}})")
        check(r["w"] == k3 and "6.5fr" in r["cols"] and r["full"] >= 1 and r["cmp"] >= 1, f"tocar un día lo ensancha con nombres; los demás, solo icono {r['w']} {r['full']}/{r['cmp']}")
        wbox = await pg.locator(f".agw-day[data-colk='{k3}']").bounding_box()
        check(wbox["width"] > 150, f"el día ancho ocupa buena parte de la pantalla ({round(wbox['width'])} px)")
        await pg.locator(f".agw-hd:has-text('{int(k3[8:])}')").first.tap(); await pg.wait_for_timeout(500)
        check(await pg.evaluate("WKX.wide===null&&!document.querySelector('.agw').style.gridTemplateColumns.includes('fr 4')"), "otro toque lo devuelve a su tamaño")
        # tocar un bloque abre su hoja y no ensancha
        await pg.locator(f".agw-day[data-colk='{k3}'] .agw-ev").first.tap(); await pg.wait_for_timeout(500)
        r = await pg.evaluate("[document.querySelector('#sheet').classList.contains('on'),WKX.wide]")
        check(r[0] and r[1] is None, f"tocar un bloque abre su hoja sin ensanchar el día {r}")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(400)
        # tocar la columna (fuera de un bloque) también ensancha
        await pg.evaluate(f"document.querySelector('.agw-day[data-colk=\"{k3}\"]').click()"); await pg.wait_for_timeout(300)
        check(await pg.evaluate(f"WKX.wide==='{k3}'"), "tocar el hueco de un día también lo ensancha")
        await pg.evaluate("agView='week';renderAgenda()"); await pg.wait_for_timeout(300)
        await pg.locator(".wkc-h button").tap(); await pg.wait_for_timeout(300)
        check(await pg.evaluate("!WKX.open&&!!document.querySelector('.wkm')&&!document.querySelector('.agw')"), "«Plegar» vuelve a la miniatura")
        # rachas abren el detalle
        await pg.evaluate("agView='week';WKX.open=false;renderAgenda()"); await pg.wait_for_timeout(300)
        await pg.locator(".hk").first.tap(); await pg.wait_for_timeout(500)
        check(await pg.evaluate("document.querySelector('#sheet').classList.contains('on')&&!!document.querySelector('#sheetBody .det-hero')"), "tocar una racha abre el detalle del hábito")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(400)

        # ── Detalle ──
        await pg.evaluate("sel=addDays(todayK(),2);openDetail('fr')"); await pg.wait_for_timeout(500)
        r = await pg.evaluate("({hero:!!document.querySelector('.det-hero'),steps:document.querySelectorAll('.det-hero .step').length,nx:document.querySelectorAll('.nx-row').length,mo:document.querySelectorAll('.mos .mo').length})")
        check(r["hero"] and r["steps"] == 3 and r["nx"] == 3 and r["mo"] >= 1, f"detalle: cabecera, pasos de hoy, 3 próximas sesiones y meses {r}")
        await pg.locator(".det-hero .step").first.tap(); await pg.wait_for_timeout(500)
        r = await pg.evaluate("[(entry(getH('fr'),todayK())||{steps:[]}).steps.length,sel===addDays(todayK(),2),document.querySelector('.det-hero .step').classList.contains('on')]")
        check(r == [1, True, True], f"tachar un paso desde el detalle lo apunta hoy sin cambiar el día que mirabas {r}")
        await pg.evaluate("closeSheet();sel=todayK()"); await pg.wait_for_timeout(400)

        # ── Editor ──
        await pg.evaluate("openEditor(null,{blank:true})"); await pg.wait_for_timeout(400)
        await pg.locator("#sheetBody input").first.fill("Movilidad"); await pg.wait_for_timeout(150)
        check("Movilidad" in await pg.inner_text("#edPrev"), "la vista previa cambia mientras escribes el nombre")
        await pg.locator("#sheetBody .seg button", has_text="Con hora").tap(); await pg.wait_for_timeout(200)
        await pg.locator("#sheetBody .seg button", has_text="Se repite").tap(); await pg.wait_for_timeout(200)
        t = await pg.inner_text("#edPrev")
        check(":" in t and "Cada día" in t, f"y enseña hora y frecuencia ({t.splitlines()[-1]})")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(300)

        # ── Filas compactas, «Pendiente» y botones del plan visibles ──
        await pg.evaluate("S.settings.theme='dark';applyTheme();sel=todayK();for(const k in OPEN)delete OPEN[k];go('hoy')"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("({rows:[...document.querySelectorAll('.tlr .hc')].filter(c=>c.querySelector('.hc-plan')).length,more:document.querySelectorAll('.tlr .hc-more').length,hero:!!document.querySelector('.hc.hero .hc-plan')})")
        check(r["rows"] == 0 and r["more"] >= 2 and r["hero"], f"el resto del día sale compacto; solo «Ahora» abierta {r}")
        r = await pg.evaluate("(()=>{const a=document.querySelector('.hc.hero .blk-go');if(!a)return null;const cs=getComputedStyle(a);return [cs.color,cs.backgroundColor,a.textContent.trim()]})()")
        check(r is None or (r[0] != r[1] and r[2]), f"los botones del plan se leen (texto ≠ fondo) {r}")
        await pg.clock.set_fixed_time("2026-11-25T23:30:00+01:00"); await pg.evaluate("render()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("(document.querySelector('.hc.hero .hero-tag')||{}).textContent||''")
        check("PENDIENTE" in r, f"de noche, «Ahora» enseña lo que quedó pendiente ({r})")
        await pg.clock.set_fixed_time("2026-11-25T09:10:00+01:00")

        # ── Modo claro y objetivos táctiles ──
        await pg.evaluate("S.settings.theme='light';applyTheme();go('hoy')"); await pg.wait_for_timeout(300)
        small = await pg.evaluate("""[...document.querySelectorAll('.ntc,.wkc-h button,.hk,.tl-free,.wd')].filter(e=>e.offsetParent).map(e=>e.getBoundingClientRect()).filter(r=>r.width<43.5||r.height<43.5).length""")
        check(small == 0, f"los nuevos botones miden al menos 44 px ({small})")
        check(await pg.evaluate("APP_VERSION") >= "1.29", "versión 1.29 o posterior")
        check(not errs, f"sin errores de JS {errs[:2]}")
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(1 if fails else 0)
