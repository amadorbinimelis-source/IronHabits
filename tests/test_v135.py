"""Pruebas de la v1.35: logo sin recuadro, recortado en sus 4 piezas (píxeles originales), y animación de apertura."""
import asyncio, sys, pathlib
import numpy as np
from PIL import Image
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
ROOT = pathlib.Path(__file__).resolve().parent.parent
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

async def main():
    a = Image.open(ROOT / "logo-a.png"); S = a.size[0]
    check(a.mode == "RGBA" and a.size == (768, 768), f"logo-a.png transparente {a.mode} {a.size}")
    al = np.asarray(a)[..., 3]
    check(al[0, 0] == 0 and al[5, 600] == 0, "el fondo blanco es transparente")
    orig = Image.open(ROOT / "logo.png").convert("RGB").resize((S, S), Image.LANCZOS)
    w = Image.new("RGBA", (S, S), (254, 254, 255, 255)); w.alpha_composite(a)
    df = np.abs(np.asarray(w.convert("RGB"), int) - np.asarray(orig, int))
    check(df.mean() < 1.5 and np.percentile(df, 99.5) < 12, f"sobre blanco es igual que el original (media {df.mean():.2f})")
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for theme in ("light", "dark"):
            ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid", service_workers="block")
            await ctx.add_init_script("localStorage.setItem('ironhabits_v1',JSON.stringify({habits:[],settings:{theme:'%s'}}))" % theme)
            pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.goto(URL, wait_until="domcontentloaded"); await pg.wait_for_timeout(120)
            r = await pg.evaluate("""(()=>{const ic=document.querySelector('#boot .boot-ic'),ps=[...ic.querySelectorAll('img.bp')];
              return [ps.map(i=>i.getAttribute('src')),getComputedStyle(ic).boxShadow,getComputedStyle(ic).borderRadius,ps.map(i=>getComputedStyle(i).animationName),ic.offsetWidth]})()""")
            check(r[0] == [f"logo-p{k}.png" for k in range(1, 5)] and r[1] == "none" and r[2] == "0px" and r[4] == 176, f"{theme}: 4 piezas, sin recuadro ni sombra de recuadro {r[1:3]}")
            check(all(x == "bfly" for x in r[3]), f"{theme}: las piezas llegan volando {r[3]}")
            early = await pg.evaluate("[...document.querySelectorAll('#boot .bp')].map(i=>getComputedStyle(i).transform)")
            await pg.wait_for_timeout(1300)
            late = await pg.evaluate("[...document.querySelectorAll('#boot .bp')].map(i=>[getComputedStyle(i).transform,+getComputedStyle(i).opacity])")
            check(any(x != "none" for x in early) and all(t in ("none", "matrix(1, 0, 0, 1, 0, 0)") and o == 1 for t, o in late), f"{theme}: y encajan en su sitio")
            # las piezas montadas reproducen el logo
            box = await pg.evaluate("(()=>{const r=document.querySelector('#boot .boot-ic').getBoundingClientRect();return [r.x,r.y,r.width]})()")
            check(box[2] == 176, "el logo mide 176 px")
            await pg.wait_for_timeout(2200)
            check(not await pg.evaluate("!!document.getElementById('boot')"), f"{theme}: y la pantalla se va sola")
            check(not errs, f"{theme}: sin errores de JS {errs[:2]}")
            await ctx.close()
        await b.close()
    sw = (ROOT / "sw.js").read_text()
    check(all(f"logo-p{k}.png" in sw for k in range(1, 5)) and "logo-a.png" in sw, "las piezas van en la caché (sin conexión)")

if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(1 if fails else 0)
