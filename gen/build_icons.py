"""Genera los iconos y las pantallas de arranque de iOS a partir de logo.png (logo original de la app, 1254×1254, sin tocar).
Los iconos se reducen con Lanczos directamente desde el original (sin pasos intermedios).
Uso: python gen/build_icons.py  (necesita Pillow, Playwright y Chrome)."""
import asyncio, base64, pathlib
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
from PIL import Image
LOGO = Image.open(ROOT / "logo.png").convert("RGB")
URI = "data:image/png;base64," + base64.b64encode((ROOT / "logo-a.png").read_bytes()).decode()  # pantallas de arranque: logo sin recuadro (gen/cut_logo.py)
ICONS = {"favicon.png": 64, "icon-180.png": 180, "icon-192.png": 192, "icon-512.png": 512, "icon-maskable-512.png": 512}
SPLASH = [(750,1334),(828,1792),(1080,2340),(1125,2436),(1170,2532),(1179,2556),(1206,2622),(1242,2208),(1242,2688),(1284,2778),(1290,2796),(1320,2868)]
THEMES = {"": ("#F5F5F7", "#15151A"), "-dark": ("#0B0B0F radial-gradient(circle at 50% 42%,#2A2A31 0,#16161B 32%,#0B0B0F 62%)", "#F4F4F6")}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for name, n in ICONS.items():
            LOGO.resize((n, n), Image.LANCZOS).save(ROOT / name, optimize=True)
        for w, h in SPLASH:
            for suf, (bg, ink) in THEMES.items():
                sc = 2 if w in (750, 828) else 3
                pg = await b.new_page(viewport={"width": w // sc, "height": h // sc}, device_scale_factor=sc)
                await pg.set_content(f'''<html><body style="margin:0;background:{bg};height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px">
                  <img src="{URI}" style="width:176px;height:176px;margin-top:-60px">
                  <div style="font:800 30px/1 Inter,'Inter Display',system-ui,sans-serif;letter-spacing:-.02em;color:{ink}">IronHabits</div></body></html>''')
                await pg.wait_for_timeout(150); await pg.screenshot(path=str(ROOT / "splash" / f"splash-{w}x{h}{suf}.png")); await pg.close()
        await b.close()

asyncio.run(main())
