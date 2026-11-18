"""Pruebas de la v1.11 (trozo 2 de la auditoría: arreglos de iPhone).
Mide en un iPhone 13 simulado: botones de 44 px o más, letra de 11 px o más, contraste del texto tenue,
toasts dentro de la pantalla, fondo bloqueado con las hojas abiertas y cambio de día a medianoche."""
import asyncio, sys
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

SMALL = """(sel)=>[...document.querySelectorAll(sel+' button,'+sel+' a.btn,'+sel+' input,'+sel+' select')].filter(e=>{
  if(!e.offsetParent||e.closest('.ag-day,.agw,.hm,.hm-big,#hapticSw'))return false;const r=e.getBoundingClientRect();return r.width&&(r.width<43.5||r.height<43.5);})
  .map(e=>(e.className||e.tagName)+' '+Math.round(e.getBoundingClientRect().width)+'x'+Math.round(e.getBoundingClientRect().height)+' «'+(e.textContent||'').trim().slice(0,14)+'»')"""
FONTS = """(sel)=>[...document.querySelectorAll(sel+' *')].filter(e=>e.offsetParent&&!e.closest('#hapticSw')&&[...e.childNodes].some(n=>n.nodeType==3&&n.textContent.trim()))
  .map(e=>parseFloat(getComputedStyle(e).fontSize)).filter(x=>x<11)"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        ctx = await b.new_context(**p.devices["iPhone 13"]); pg = await ctx.new_page()
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(1500)
        await pg.evaluate("S.habits.forEach(h=>h.start=addDays(todayK(),-30));(S.logs[todayK()]={}).fr={v:0,steps:[]};save();render()")
        for v in ("hoy", "agenda", "prog", "set"):
            await pg.evaluate(f"go('{v}')"); await pg.wait_for_timeout(250)
            sm = await pg.evaluate(SMALL, "#v-" + v); fs = await pg.evaluate(FONTS, "#v-" + v)
            check(not sm, f"{v}: todos los botones miden 44 px o más {sm[:4]}")
            check(not fs, f"{v}: ninguna letra por debajo de 11 px {sorted(set(fs))[:4]}")
        sm = await pg.evaluate(SMALL, "nav"); check(not sm, f"barra inferior: botones de 44 px o más {sm[:3]}")
        for name, js in (("menú del hábito", "go('hoy');cardMenu('fr')"), ("editor", "openEditor('fr')"), ("sesión extra", "extraSheet(todayK())"), ("check-in/RPE", "rpeSheet('boxeo',todayK())")):
            await pg.evaluate(js); await pg.wait_for_timeout(350)
            sm = await pg.evaluate(SMALL, "#sheet"); fs = await pg.evaluate(FONTS, "#sheet")
            check(not sm, f"hoja «{name}»: botones de 44 px o más {sm[:4]}")
            check(not fs, f"hoja «{name}»: letra de 11 px o más {sorted(set(fs))[:4]}")
            await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(350)
        # la hora vacía no se queda sin altura y los selectores usan el tema oscuro
        await pg.evaluate("extraSheet(todayK())"); await pg.wait_for_timeout(350)
        r = await pg.evaluate("({h:document.querySelector('#exS').getBoundingClientRect().height,cs:getComputedStyle(document.documentElement).colorScheme})")
        check(r["h"] >= 44 and r["cs"] == "dark", f"campo de hora vacío visible y tema oscuro {r}")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(350)
        # contraste del texto tenue
        r = await pg.evaluate("""(()=>{const L=h=>{const c=[1,3,5].map(i=>parseInt(h.slice(i,i+2),16)/255).map(x=>x<=.03928?x/12.92:((x+.055)/1.055)**2.4);return .2126*c[0]+.7152*c[1]+.0722*c[2]};
          const v=getComputedStyle(document.documentElement).getPropertyValue('--dim').trim();return (L(v)+.05)/(L('#15151B')+.05);})()""")
        check(r >= 4.5, f"texto tenue con contraste suficiente ({r:.2f}:1)")
        # check-in centrado
        await pg.evaluate("S.checkins={};openSheet(checkinCard(todayK()))"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("getComputedStyle(document.querySelector('#sheet .ci button')).textAlign")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(300)
        check(r == "center", f"números del check-in centrados ({r})")
        # toast largo dentro de la pantalla
        await pg.evaluate("toast('💪 Fuerza / calistenia → miércoles 25 nov a las 18:30 · se solapa con Fútbol · entreno (fisio)',[undoAct()])"); await pg.wait_for_timeout(400)
        r = await pg.evaluate("(()=>{const r=document.querySelector('#toast').getBoundingClientRect();return [Math.round(r.left),Math.round(r.right),innerWidth]})()")
        check(r[0] >= 0 and r[1] <= r[2], f"un aviso largo cabe en la pantalla {r}")
        # fondo bloqueado con una hoja abierta y posición recuperada al cerrar
        await pg.evaluate("go('hab');window.scrollTo(0,400)"); await pg.wait_for_timeout(200)
        await pg.evaluate("openDetail('fr')"); await pg.wait_for_timeout(350)
        fixed = await pg.evaluate("getComputedStyle(document.body).position")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(350)
        y = await pg.evaluate("Math.round(scrollY)")
        check(fixed == "fixed" and y == 400, f"con una hoja abierta el fondo no se mueve y al cerrar vuelves al mismo sitio ({fixed}, {y})")
        # medianoche con la app abierta
        r = await pg.evaluate("""(()=>{const t=todayK(),n=addDays(t,1);sel=t;go('hoy');const _tk=todayK;todayK=()=>n;const ch=dayRollover();const s=sel;todayK=_tk;_lastDay=t;sel=t;return [ch,s===n];})()""")
        check(r == [True, True], f"a medianoche «Hoy» pasa al día nuevo {r}")
        # el control de arrastre no bloquea el scroll normal
        r = await pg.evaluate("typeof dragTouchMove==='function'")
        check(r, "el arrastre de bloques sigue disponible")
        check(not errs, f"sin errores de JavaScript {errs[:2]}")
        await pg.evaluate("go('hoy')"); await pg.wait_for_timeout(300); await pg.screenshot(path="/tmp/t/hoy_v111.png", full_page=False)
        await pg.evaluate("go('set')"); await pg.wait_for_timeout(300); await pg.screenshot(path="/tmp/t/set_v111.png", full_page=False)
        await b.close()

asyncio.run(main())
print("\nRESULTADO:", "OK" if not fails else f"{len(fails)} fallos"); sys.exit(1 if fails else 0)
