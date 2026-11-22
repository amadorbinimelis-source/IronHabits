"""Pruebas de la v1.27: vibración mínima en todos los botones (el sonido al abrir se quitó en la v1.33)."""
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
        await ctx.add_init_script("window._vib=[];navigator.vibrate=(x)=>{window._vib.push(x);return true};")
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-25T09:00:00+01:00")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(2500)
        check(await pg.evaluate("typeof fxHello==='undefined'&&typeof HELLO==='undefined'"), "v1.33: ya no hay sonido al abrir")
        n0 = await pg.evaluate("_vib.length")
        await pg.locator("nav button[data-v=set]").tap(); await pg.wait_for_timeout(150)
        await pg.locator("nav button[data-v=hoy]").tap(); await pg.wait_for_timeout(150)
        check(await pg.evaluate("_vib.length") - n0 == 2 and await pg.evaluate("_vib.every(x=>x===12)"), "cada botón da un toque mínimo")
        await pg.evaluate("go('set')"); await pg.wait_for_timeout(200)
        t = await pg.inner_text("#setBody")
        check("Vibración al tocar" in t and "Sonido al abrir" not in t, "la vibración se puede quitar en Ajustes (y ya no está «Sonido al abrir»)")
        await pg.evaluate("S.settings.tapHaptic=false;save()"); n1 = await pg.evaluate("_vib.length")
        await pg.locator("nav button[data-v=hoy]").tap(); await pg.wait_for_timeout(150)
        check(await pg.evaluate("_vib.length") == n1, "con la vibración apagada, no vibra")
        await pg.evaluate("S.settings.tapHaptic=true;save();_vib.length=0;buzz();buzz()")
        check(await pg.evaluate("_vib.length") == 1, "no vibra dos veces seguidas por el mismo toque")
        check(await pg.evaluate("APP_VERSION") >= "1.27", "versión 1.27")
        check(not errs, f"sin errores de JS {errs[:2]}")
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
    print("FALLAN:" if fails else "TODO OK", fails if fails else "")
    sys.exit(1 if fails else 0)
