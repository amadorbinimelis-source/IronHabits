"""Genera los iconos y las pantallas de arranque de iOS a partir de icon.svg (logo de la app).
Uso: python gen/build_icons.py  (necesita Playwright y Chrome)."""
import asyncio, base64, pathlib
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
SVG = (ROOT / "icon.svg").read_text()
URI = "data:image/svg+xml;base64," + base64.b64encode(SVG.encode()).decode()
ICONS = {"favicon.png": 64, "icon-180.png": 180, "icon-192.png": 192, "icon-512.png": 512, "icon-maskable-512.png": 512}
SPLASH = [(750,1334),(828,1792),(1080,2340),(1125,2436),(1170,2532),(1179,2556),(1206,2622),(1242,2208),(1242,2688),(1284,2778),(1290,2796),(1320,2868)]
THEMES = {"": ("#F5F5F7", "#15151A", "0 30px 60px rgba(0,0,0,.18)"), "-dark": ("#0B0B0F", "#F4F4F6", "0 16px 36px rgba(0,0,0,.45)")}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for name, n in ICONS.items():
            pg = await b.new_page(viewport={"width": n, "height": n})
            await pg.set_content(f'<html><body style="margin:0"><img src="{URI}" style="width:{n}px;height:{n}px;display:block"></body></html>')
            await pg.wait_for_timeout(150); await pg.screenshot(path=str(ROOT / name)); await pg.close()
        for w, h in SPLASH:
            for suf, (bg, ink, sh) in THEMES.items():
                sc = 2 if w in (750, 828) else 3
                pg = await b.new_page(viewport={"width": w // sc, "height": h // sc}, device_scale_factor=sc)
                await pg.set_content(f'''<html><body style="margin:0;background:{bg};height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px">
                  <img src="{URI}" style="width:116px;height:116px;border-radius:26px;box-shadow:{sh};margin-top:-60px">
                  <div style="font:800 30px/1 Inter,'Inter Display',system-ui,sans-serif;letter-spacing:-.02em;color:{ink}">IronHabits</div></body></html>''')
                await pg.wait_for_timeout(150); await pg.screenshot(path=str(ROOT / "splash" / f"splash-{w}x{h}{suf}.png")); await pg.close()
        await b.close()

asyncio.run(main())
