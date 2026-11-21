"""Pruebas de la v1.31: claro por defecto y pantalla de carga del color del tema (también al primer instante)."""
import asyncio, sys, json
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

async def boot_bg(p, b, stored):
    ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid", service_workers="block")
    if stored is not None:
        await ctx.add_init_script(f"try{{if(!sessionStorage.getItem('x')){{sessionStorage.setItem('x','1');localStorage.setItem('ironhabits_v1',JSON.stringify({json.dumps(stored)}));}}}}catch(e){{}}")
    await ctx.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const b=document.getElementById('boot');window._bootBg=getComputedStyle(b).backgroundColor;window._bootTxt=getComputedStyle(b.querySelector('.boot-name')).color;},{once:true})")
    pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    await pg.goto(URL); await pg.wait_for_timeout(2500)
    r = await pg.evaluate("[window._bootBg,window._bootTxt,document.documentElement.dataset.theme,document.querySelector('meta[name=theme-color]').content]")
    return pg, ctx, r, errs

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg, ctx, r, errs = await boot_bg(p, b, None)
        check(r[0] == "rgb(245, 245, 247)" and r[2] == "light" and r[3] == "#F5F5F7", f"sin nada guardado: claro y pantalla de carga blanca {r}")
        check(r[1] == "rgb(21, 21, 26)", f"con el nombre en oscuro {r[1]}")
        check(await pg.evaluate("(S.settings.theme||'light')==='light'&&themeNow()==='light'"), "el tema por defecto es «Claro»")
        await pg.evaluate("go('set')"); await pg.wait_for_timeout(300)
        check(await pg.evaluate("[...document.querySelectorAll('#setBody .seg button.on')].some(b=>b.textContent==='Claro')"), "Ajustes marca «Claro»")
        await pg.evaluate("setTheme('dark')"); await pg.wait_for_timeout(200)
        check(await pg.evaluate("document.documentElement.dataset.theme==='dark'&&document.querySelector('meta[name=theme-color]').content==='#0B0B0F'"), "al pasar a oscuro cambia al momento")
        await pg.reload(); await pg.wait_for_timeout(2500)
        r2 = await pg.evaluate("[window._bootBg,document.documentElement.dataset.theme]")
        check(r2 == ["rgb(11, 11, 15)", "dark"], f"al volver a abrir en oscuro, sale negra desde el primer instante {r2}")
        check(not errs, f"sin errores de JS {errs[:2]}")
        await ctx.close()
        # «Como el iPhone» con el iPhone en oscuro
        ctx2 = await b.new_context(**p.devices["iPhone 13"], color_scheme="dark", service_workers="block")
        await ctx2.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const b=document.getElementById('boot');window._bg=b&&getComputedStyle(b).backgroundColor},{once:true})")
        pg2 = await ctx2.new_page(); await pg2.goto(URL); await pg2.wait_for_timeout(2000)
        await pg2.evaluate("S.settings.theme='auto';save()"); await pg2.reload(); await pg2.wait_for_timeout(2000)
        r = await pg2.evaluate("[window._bg,document.documentElement.dataset.theme]")
        check(r == ["rgb(11, 11, 15)", "dark"], f"«Como el iPhone» con el iPhone en oscuro: carga negra desde el primer instante {r}")
        r = await pg2.evaluate("[...document.querySelectorAll('link[rel=apple-touch-startup-image]')].map(l=>[l.getAttribute('href'),l.media])")
        dk = [h for h, m in r if 'prefers-color-scheme: dark' in m]
        check(len(dk) * 2 == len(r) and all(h.endswith('-dark.png') for h in dk), f"pantallas de arranque de iOS en claro y en oscuro ({len(r)})")
        ok = await pg2.evaluate("(hs)=>Promise.all(hs.map(u=>fetch(u).then(r=>r.ok)))", [h for h, _ in r])
        check(all(ok), "todas existen")
        r = await pg2.evaluate("fetch('icon.svg').then(r=>r.text()).then(t=>t.includes('#E63946')&&t.includes('#2BB673'))")
        check(r, "el logo nuevo (icon.svg) está en la app")
        check(await pg2.evaluate("APP_VERSION") >= "1.31", "versión 1.31")
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(1 if fails else 0)
