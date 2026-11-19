"""Pruebas de la v1.22: sonido y vibración al avanzar (pasos más agudos, acorde al completar) e interruptor de sonido."""
import asyncio, sys
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--autoplay-policy=no-user-gesture-required"])
        ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid", service_workers="block")
        await ctx.add_init_script("Object.defineProperty(navigator,'standalone',{get:()=>true})")
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-24T08:00:00+01:00")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(2000)
        await pg.evaluate("S.logs={};save();sel=todayK();go('hoy')"); await pg.wait_for_timeout(300)
        # espías sobre las funciones de efectos y los tonos
        await pg.evaluate("""window._fx=[];const s=fxStep,g=fxGoal,t=tone;
          window.fxStep=p=>{_fx.push(['step',+p.toFixed(2)]);s(p)};window.fxGoal=b=>{_fx.push(['goal',!!b]);g(b)};
          window._tones=[];window.tone=(ac,o)=>{_tones.push(o);t(ac,o)};0""")
        hid = await pg.evaluate("(()=>{const h=S.habits.find(h=>!h.archived&&h.type==='checklist'&&h.steps.length>=3&&dayHabits(todayK()).includes(h));return h&&h.id})()")
        if not hid:
            await pg.evaluate("S.habits.push({id:'tst',name:'Prueba',emoji:'🧪',type:'checklist',steps:[{id:'a',text:'A'},{id:'b',text:'B'},{id:'c',text:'C'}],freq:{type:'daily'}});save()")
            hid = 'tst'
        steps = await pg.evaluate(f"getH('{hid}').steps.map(s=>s.id)")
        for sid in steps: await pg.evaluate(f"stepT('{hid}','{sid}')")
        fx = await pg.evaluate("_fx")
        st = [x for x in fx if x[0] == 'step']
        check(len(st) == len(steps) - 1, f"un efecto por paso antes de la meta ({len(st)})")
        check(all(st[i][1] < st[i+1][1] for i in range(len(st)-1)), f"cada paso más cerca de la meta {st}")
        check(fx and fx[-1][0] == 'goal', "al tachar el último: efecto de meta")
        f0 = await pg.evaluate("_tones.filter(o=>o.partials===MARIMBA).map(o=>o.f1)")
        check(len(f0) >= 2 and all(f0[i] < f0[i+1] for i in range(len(f0)-1)), f"cada paso suena más agudo {[round(x) for x in f0]}")
        check(await pg.evaluate("_tones.filter(o=>o.partials===MARIMBA).every(o=>o.f1>o.f0)"), "cada nota de paso va de grave a agudo")
        check(await pg.evaluate("_tones.filter(o=>o.partials===BELL).length") >= 2, "la meta suena con notas de campana")
        await pg.evaluate("_fx.length=0;")
        await pg.evaluate(f"stepT('{hid}','{steps[-1]}')")
        check(await pg.evaluate("_fx.length") == 0, "desmarcar no hace sonido")
        # sonido apagado
        await pg.evaluate("S.settings.sound=false;_tones.length=0;")
        await pg.evaluate(f"stepT('{hid}','{steps[-1]}')")
        check(await pg.evaluate("_tones.length") == 0, "con el sonido apagado no suena")
        await pg.evaluate("S.settings.sound=true;save();go('set')"); await pg.wait_for_timeout(200)
        check("Sonido al completar" in await pg.inner_text("#setBody"), "interruptor «Sonido al completar» en Ajustes")
        ap = await pg.evaluate("getComputedStyle(document.querySelector('#hapticSw input')).webkitAppearance||getComputedStyle(document.querySelector('#hapticSw input')).appearance")
        check(ap != "none", f"el interruptor oculto de vibración del iPhone mantiene su aspecto nativo ({ap})")
        check(await pg.evaluate("APP_VERSION") == "1.22", "versión 1.22")
        check(not errs, f"sin errores de JS {errs[:2]}")
        await b.close()

asyncio.run(main())
print("FALLAN:" if fails else "TODO OK", fails if fails else "")
sys.exit(1 if fails else 0)
