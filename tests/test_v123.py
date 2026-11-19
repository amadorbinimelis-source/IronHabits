"""Pruebas de la v1.23: tutorial interactivo guiado, recorrido entero en un iPhone 13 simulado pulsando los elementos
de verdad (si el foco no deja pasar el toque, Playwright falla), bloqueo de lo demás, datos de prueba que se borran,
saltar, continuar a medias, mini-tour de sección y bocadillo siempre dentro de la pantalla."""
import asyncio, json, sys
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

async def swipe(cdp, x0, y0, x1, y1, steps=8):
    await cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x0, "y": y0}]})
    for i in range(1, steps + 1):
        await cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": x0 + (x1 - x0) * i / steps, "y": y0 + (y1 - y0) * i / steps}]})
        await asyncio.sleep(0.02)
    await cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})

async def center(pg, sel):
    return await pg.evaluate(f"(()=>{{const e=tourTarget({{selector:{json.dumps(sel)}}});if(!e)return null;const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2,r.width,r.height]}})()")

async def walk(pg, cdp, limit=80, stop_at=None):
    seen, tip_out = [], []
    for _ in range(limit):
        await pg.wait_for_timeout(450)
        cur = await pg.evaluate("(()=>{if(!TOUR)return null;if(TOUR.pending)return 'wait';const s=tourCur();return s?{id:s.id,acc:s.accion,sel:s.selector||null}:'wait'})()")
        if not cur: break
        if cur == "wait": continue
        if stop_at and cur["id"] == stop_at: return seen, tip_out
        if not seen or seen[-1] != cur["id"]: seen.append(cur["id"])
        box = await pg.evaluate("(()=>{const r=document.querySelector('#tour .tr-tip').getBoundingClientRect();return [r.left,r.top,r.right,r.bottom,innerWidth,innerHeight]})()")
        if box[0] < 0 or box[1] < 0 or box[2] > box[4] + 0.5 or box[3] > box[5] + 0.5: tip_out.append(cur["id"])
        a, sel = cur["acc"], cur["sel"]
        if a == "info": await pg.locator("#tour .tr-ok").tap(); continue
        if a == "input":
            await pg.locator(sel).tap(); await pg.locator(sel).fill("30"); continue
        if a == "gesto":
            c = await center(pg, sel); await swipe(cdp, c[0] + 60, c[1], c[0] - 120, c[1]); continue
        if a == "scroll":
            c = await center(pg, sel); await swipe(cdp, c[0], c[1] + 120, c[0], c[1] - 200, 10); continue
        if cur["id"] == "pasos":
            await pg.locator("#hc-tour .step:not(.on)").first.tap(); continue
        try: await pg.locator(sel).first.tap(timeout=4000)
        except Exception as e:
            print("   atascado en", cur, str(e).split("\n")[-3:]); await pg.screenshot(path="/tmp/atasco.png"); raise
    return seen, tip_out

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid", service_workers="block")
        await ctx.add_init_script("Object.defineProperty(navigator,'standalone',{get:()=>true})")
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-24T10:00:00+01:00")
        cdp = await ctx.new_cdp_session(pg)
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(2000)
        # nube conectada (falsa) para comprobar que el tutorial no marca nada para subir
        await pg.evaluate("S.logs[todayK()]={};S.logs[todayK()].fr={v:1,steps:[]};save();sel=todayK();go('hoy')")
        await pg.evaluate("localStorage.setItem(CLOUD_KEY,JSON.stringify({token:'t',login:'u',gistId:'g',icsGist:'i',names2:true,lastSync:new Date().toISOString(),dirtyAt:0,lastPushAt:Date.now()}));window.gh=async()=>{throw new Error('sin red')};0")
        before = await pg.evaluate("JSON.stringify({h:S.habits.map(h=>h.id),l:S.logs,n:S.notes,a:S.agenda})")
        check(await pg.evaluate("typeof GUIDE==='undefined'&&typeof welcomeSheet==='undefined'&&!document.querySelector('[onclick*=guideIndex]')"), "el librito de pantallas de texto ya no está")

        # ── Recorrido completo
        await pg.evaluate("tourStart('full',TOUR_STEPS)"); await pg.wait_for_timeout(500)
        check(await pg.evaluate("!!getH('tour')&&inTour()"), "al empezar: hábito de prueba y copia de tus datos")
        t = await pg.inner_text("#tour .tr-tip")
        check("Paso 1/" in t and "Saltar" in t, "indicador «Paso 1/N» y «Saltar» visibles")
        await pg.locator("#tour .tr-ok").tap(); await pg.wait_for_timeout(600)
        # bloqueo: tocar fuera (pestaña Ajustes) no hace nada y el objetivo avisa
        await pg.mouse.click(30, 100); await pg.wait_for_timeout(120)
        check(await pg.evaluate("view==='hoy'&&document.querySelector('#tour .tr-hole').classList.contains('nudge')"), "tocar fuera está bloqueado y el objetivo hace «shake»")
        check(await pg.evaluate("tourCur().id") == "plan", "un «Entendido» solo en los pasos informativos; los demás esperan la acción")
        await pg.wait_for_timeout(800)
        check(await pg.evaluate("tourCur().id") == "plan", "no avanza solo: espera a que pulses")
        seen, out = await walk(pg, cdp, stop_at="nav-agenda")
        check(seen[:4] == ["plan", "deslizar", "saltar", "deshacer"], f"Hoy: plan, deslizar, «Saltar» y deshacer {seen[:4]}")
        check({"menu", "apuntar", "minutos", "guardar", "empezar", "salir", "paso1", "pasos"} <= set(seen), "Hoy: menú ⋯, apuntar 30 min, guardar, ▶ Empezar, salir y tachar pasos")
        check(await pg.evaluate("(entry(getH('tour'),todayK())||{}).mins===30&&isDone(getH('tour'),todayK())"), "lo hecho durante el tutorial funciona de verdad (30 min y hábito completado)")
        nav = await pg.evaluate("tourCur()&&tourCur().accion")
        check(nav == "navegar" and await pg.evaluate("view") == "hoy", "para cambiar de sección pide pulsar la pestaña (no cambia sola)")
        await pg.evaluate("tourNudge=(()=>{})"); 
        seen2, out2 = await walk(pg, cdp); await pg.wait_for_timeout(400)
        allseen = seen + seen2
        check({"nav-agenda", "vista", "dia", "bloque", "bloque-x"} <= set(allseen), "Agenda: pestaña, vistas y bloque del hábito")
        check({"nav-prog", "detalle", "mapa", "detalle-x", "revision", "revision-x"} <= set(allseen), "Progreso: pestaña, detalle con scroll y revisión")
        check({"nav-set", "avisos", "avisos-x", "nube", "repetir", "fin"} <= set(allseen), "Ajustes: avisos, nube, repetir y pantalla final")
        infos = [s for s in allseen if s in ("hola", "campana", "nube", "repetir")]
        check(len(infos) * 5 <= len(allseen) + 1, f"como mucho 1 paso informativo de cada 5 ({len(infos)}/{len(allseen)})")
        check(not out and not out2, f"el bocadillo nunca se sale de la pantalla {out + out2}")
        after = await pg.evaluate("JSON.stringify({h:S.habits.map(h=>h.id),l:S.logs,n:S.notes,a:S.agenda})")
        if after != before:
            A, B = json.loads(before), json.loads(after)
            for k in A:
                if A[k] != B[k]: print("   dif", k, str(A[k])[:200], "→", str(B[k])[:200])
        check(after == before and not await pg.evaluate("inTour()||!!getH('tour')||!!document.getElementById('tour')"), "al acabar: tus datos exactamente como estaban, sin datos de prueba")
        st = await pg.evaluate("tourState()")
        check(st.get("done") and st.get("completed") and not st.get("active") and set(st.get("seen", [])) >= {"hoy", "agenda", "prog", "set"}, f"estado guardado aparte: completado y secciones vistas {st}")
        check(await pg.evaluate("!cloudPending(cloudCfg())"), "nada de prueba se marca para subir a la nube")

        # ── Saltar
        await pg.evaluate("go('hoy');tourStart('full',TOUR_STEPS)"); await pg.wait_for_timeout(500)
        await pg.locator("#tour .tr-ok").tap(); await pg.wait_for_timeout(500)
        await pg.locator("#hc-tour .hc-info").tap(); await pg.wait_for_timeout(600)
        await pg.locator("#tour .tr-skip").tap(); await pg.wait_for_timeout(200)
        check("¿Saltar el tutorial?" in await pg.inner_text("#tour"), "«Saltar» pide confirmación")
        await pg.locator("#tour .btn.danger").tap(); await pg.wait_for_timeout(500)
        check(await pg.evaluate("JSON.stringify({h:S.habits.map(h=>h.id),l:S.logs,n:S.notes,a:S.agenda})") == before and not await pg.evaluate("!!TOUR||inTour()"), "al saltarlo: se borra lo de prueba y tus datos quedan igual")

        # ── Cerrar a medias y continuar
        await pg.evaluate("go('hoy');tourStart('full',TOUR_STEPS)"); await pg.wait_for_timeout(500)
        await walk(pg, cdp, stop_at="minutos")
        await pg.reload(); await pg.wait_for_timeout(2000)
        check(await pg.evaluate("inTour()&&tourState().active==='full'&&!!getH('tour')"), "si cierras la app a medias, lo recuerda (y la nube sigue en pausa)")
        await pg.evaluate("tourResumeAsk()"); await pg.wait_for_timeout(300)
        t = await pg.inner_text("#tour")
        check("Continuar" in t and "Saltar" in t, "al volver: «Continuar» o «Saltar»")
        await pg.locator("#tour .btn.pri").tap(); await pg.wait_for_timeout(800)
        check(await pg.evaluate("tourCur().id") in ("hola", "plan"), "continúa desde el principio de esa sección, con datos de prueba limpios")
        await pg.evaluate("tourEnd(false)"); await pg.wait_for_timeout(400)
        check(await pg.evaluate("JSON.stringify({h:S.habits.map(h=>h.id),l:S.logs,n:S.notes,a:S.agenda})") == before, "y al salir, tus datos intactos")

        # ── Tutorial de una sección y mini-tour
        await pg.evaluate("go('set')"); await pg.wait_for_timeout(300)
        check(await pg.evaluate("!!document.querySelector('#tourRow')") and "Solo Agenda" in await pg.inner_text("#setBody"), "Ajustes: repetir el tutorial completo o por secciones")
        await pg.evaluate("tourSection('agenda')"); await pg.wait_for_timeout(500)
        check(await pg.evaluate("tourCur().id") == "nav-agenda", "el de una sección empieza pidiendo ir a ella")
        s3, _ = await walk(pg, cdp)
        check(s3 == ["nav-agenda", "vista", "dia", "bloque", "bloque-x"], f"tutorial de la Agenda {s3}")
        await pg.evaluate("go('prog');tourStart('mini:prog',tourSteps('mini:prog'))"); await pg.wait_for_timeout(500)
        s4, _ = await walk(pg, cdp)
        check(2 <= len(s4) <= 4, f"mini-tour de Progreso de 2-4 pasos {s4}")
        await pg.evaluate("tourSet({offered:true,seen:['hoy']})")
        check(await pg.evaluate("(()=>{const w=Object.getOwnPropertyDescriptor(Navigator.prototype,'webdriver');Object.defineProperty(navigator,'webdriver',{get:()=>false});go('agenda');return true})()"), "")
        await pg.wait_for_timeout(900)
        check(await pg.evaluate("!!TOUR&&TOUR.name==='mini:agenda'"), "la primera vez que entras en una sección no vista, arranca su mini-tour")
        await pg.evaluate("tourEnd(false)"); await pg.wait_for_timeout(300)
        await pg.evaluate("go('hoy');go('agenda')"); await pg.wait_for_timeout(900)
        check(await pg.evaluate("!TOUR"), "y no se repite")

        # ── Robustez: elemento que no aparece se salta; girar la pantalla recoloca
        await pg.evaluate("TOUR_STEPS.splice(1,0,{id:'fantasma',seccion:'hoy',selector:'#no-existe',accion:'click',texto:'x'})")
        await pg.evaluate("go('hoy');tourStart('sec:hoy',tourSteps('sec:hoy'))"); await pg.wait_for_timeout(300)
        await pg.wait_for_timeout(4800)
        check(await pg.evaluate("tourCur().id") == "plan", "si un elemento no aparece en 4 s, se salta ese paso sin romper el tutorial")
        await pg.set_viewport_size({"width": 844, "height": 390}); await pg.wait_for_timeout(400)
        r = await pg.evaluate("(()=>{const h=document.querySelector('#tour .tr-hole').getBoundingClientRect(),e=tourTarget(tourCur()).getBoundingClientRect(),t=document.querySelector('#tour .tr-tip').getBoundingClientRect();return [Math.abs(h.left-(e.left-6))<2&&Math.abs(h.top-(e.top-6))<2,t.right<=innerWidth&&t.bottom<=innerHeight&&t.left>=0&&t.top>=0]})()")
        check(r == [True, True], f"al girar el móvil, el foco sigue al elemento y el bocadillo cabe {r}")
        await pg.set_viewport_size({"width": 390, "height": 664})
        await pg.evaluate("tourEnd(false)")
        check(await pg.evaluate("APP_VERSION") >= "1.23", "versión 1.23 o posterior")
        check(not errs, f"sin errores de JS {errs[:3]}")
        await b.close()


async def teclado():
    """Teclado abierto (vista visible reducida y desplazada): el bocadillo queda en la parte visible; «Guardar» cierra el teclado."""
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid", service_workers="block")
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-24T10:00:00+01:00")
        cdp = await ctx.new_cdp_session(pg)
        await pg.goto(URL); await pg.wait_for_timeout(2000)
        await pg.evaluate("go('hoy');tourStart('full',TOUR_STEPS)"); await pg.wait_for_timeout(500)
        await walk(pg, cdp, stop_at="minutos"); await pg.wait_for_timeout(600)
        await pg.locator("#mnM").tap()
        # simula el teclado del iPhone: la parte visible mide 330 px y está desplazada 180 px hacia abajo
        await pg.evaluate("Object.defineProperty(window,'visualViewport',{configurable:true,value:{width:390,height:330,offsetTop:180,offsetLeft:0,addEventListener(){},removeEventListener(){}}});tourPlace(true)")
        r = await pg.evaluate("(()=>{const t=document.querySelector('#tour .tr-tip').getBoundingClientRect();return [t.top,t.bottom]})()")
        check(r[0] >= 180 and r[1] <= 510, f"con el teclado abierto, el bocadillo queda en la parte visible {[round(x) for x in r]}")
        await pg.locator("#mnM").fill("30"); await pg.wait_for_timeout(900)
        await pg.evaluate("delete window.visualViewport;0")
        st = await pg.evaluate("[tourCur().id,document.activeElement.id]")
        check(st[0] == "guardar" and st[1] != "mnM", f"al pasar a «Guardar» se cierra el teclado {st}")
        await pg.evaluate("tourEnd(false)"); await b.close()

if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(teclado())
    print("FALLAN:" if fails else "TODO OK", fails if fails else "")
    sys.exit(1 if fails else 0)
