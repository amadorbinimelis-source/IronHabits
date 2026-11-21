"""Pruebas de la v1.28: tarjetas de «Hoy» teñidas con el color de cada hábito (se puede quitar)."""
import asyncio, sys
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
SHOT = len(sys.argv) > 1
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid", service_workers="block")
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-25T09:00:00+01:00")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(2500)
        await pg.evaluate("localStorage.setItem('ironhabits_tour',JSON.stringify({done:true,minis:{}}));S.settings.bootSound=false;save();go('hoy')")
        await pg.wait_for_timeout(400)
        cards = await pg.evaluate("""[...document.querySelectorAll('.hc')].slice(0,4).map(c=>getComputedStyle(c.querySelector('.hc-in')).backgroundImage)""")
        check(len(cards) >= 2 and all('gradient' in c for c in cards), "cada tarjeta lleva fondo de color")
        check(len(set(cards)) >= 2, "hábitos distintos, colores distintos")
        if SHOT: await pg.screenshot(path="/tmp/v128_after.png")
        await pg.evaluate("go('set')"); await pg.wait_for_timeout(200)
        check("Tarjetas de color" in await pg.inner_text("#setBody"), "opción en Ajustes")
        await pg.evaluate("S.settings.cardTint=false;save();applyTheme();go('hoy')"); await pg.wait_for_timeout(300)
        bg = await pg.evaluate("getComputedStyle(document.querySelector('.hc .hc-in')).backgroundImage")
        check(bg == "none", "apagado vuelve al negro")
        if SHOT: await pg.screenshot(path="/tmp/v128_before.png")
        await pg.evaluate("S.settings.cardTint=true;save();location.reload()"); await pg.wait_for_timeout(2500)
        check(not await pg.evaluate("document.documentElement.classList.contains('no-tint')"), "se mantiene al reabrir")
        check(await pg.evaluate("APP_VERSION") >= "1.28", "versión 1.28")
        check(not errs, f"sin errores de JS {errs[:2]}")
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(1 if fails else 0)
