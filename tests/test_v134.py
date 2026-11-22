"""Pruebas de la v1.34: logo nuevo (imagen original sin tocar) en iconos y pantalla de carga, con su animación."""
import asyncio, sys, hashlib, pathlib
from PIL import Image
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
ROOT = pathlib.Path(__file__).resolve().parent.parent
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

async def main():
    lg = Image.open(ROOT / "logo.png")
    check(lg.size == (1254, 1254), f"logo.png a tamaño original {lg.size}")
    src = lg.convert("RGB")
    for n, name in [(512, "icon-512.png"), (180, "icon-180.png")]:
        a = list(Image.open(ROOT / name).convert("RGB").getdata()); b = list(src.resize((n, n), Image.LANCZOS).getdata())
        d = max(abs(x - y) for p, q in zip(a, b) for x, y in zip(p, q))
        check(d <= 2, f"{name} sale directamente del logo original (dif. máx {d})")
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for theme, bg in (("light", "rgb(245, 245, 247)"), ("dark", "rgb(11, 11, 15)")):
            ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid", service_workers="block")
            await ctx.add_init_script("localStorage.setItem('ironhabits_v1',JSON.stringify({habits:[],settings:{theme:'%s'}}))" % theme)
            pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.goto(URL, wait_until="domcontentloaded"); await pg.wait_for_timeout(250)
            r = await pg.evaluate("""(()=>{const b=document.getElementById('boot'),s=b.querySelector('.boot-shine');
              return [getComputedStyle(b).backgroundColor,getComputedStyle(s).mixBlendMode,!!b.querySelector('svg')]})()""")
            check(r[0] == bg and r[1] == "overlay" and not r[2], f"{theme}: pantalla de carga con el logo nuevo y el brillo {r}")
            await pg.wait_for_function("document.getElementById('bootRing')&&getComputedStyle(document.getElementById('bootRing')).transform.startsWith('matrix(1,')", timeout=4000)
            check(True, f"{theme}: la barra se llena")
            await pg.wait_for_timeout(3000)
            check(not await pg.evaluate("!!document.getElementById('boot')"), f"{theme}: y se va sola")
            check(not errs, f"{theme}: sin errores de JS {errs[:2]}")
            await ctx.close()
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(1 if fails else 0)
