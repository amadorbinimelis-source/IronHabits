"""Pruebas de las hojas emergentes en un iPhone simulado (toques reales): cerrar con ✕, tocando fuera,
deslizando hacia abajo, y que abrir una hoja desde otra no la cierre."""
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
        ctx = await b.new_context(**p.devices["iPhone 13"])
        pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(1500)
        is_open = lambda: pg.evaluate("document.querySelector('#sheet').classList.contains('on')")
        async def open_task():
            await pg.evaluate("sel='2026-11-23';go('hoy')"); await pg.wait_for_timeout(300)
            await pg.locator(".hc-menu").first.tap(); await pg.wait_for_timeout(450)
        # 1. ✕
        await open_task(); check(await is_open(), "al tocar una tarea se abre la hoja")
        await pg.screenshot(path="/tmp/t/sheet_movil.png")
        await pg.locator(".sheet-x").tap(); await pg.wait_for_timeout(450)
        check(not await is_open(), "se cierra con ✕")
        # 2. Tocar fuera (zona oscura de arriba)
        await open_task(); await pg.touchscreen.tap(195, 30); await pg.wait_for_timeout(450)
        check(not await is_open(), "se cierra tocando la zona oscura")
        # 3. Deslizar hacia abajo desde el asa
        await open_task()
        box = await pg.locator("#sheetTop").bounding_box(); x = box["x"] + box["width"] / 2; y = box["y"] + 10
        cdp = await ctx.new_cdp_session(pg)
        async def touch(t, yy): await cdp.send("Input.dispatchTouchEvent", {"type": t, "touchPoints": [] if t == "touchEnd" else [{"x": x, "y": yy}]})
        await touch("touchStart", y)
        for i in range(1, 11): await touch("touchMove", y + i * 25)
        await touch("touchEnd", y + 250); await pg.wait_for_timeout(500)
        check(not await is_open(), "se cierra deslizando hacia abajo")
        # 4. Hoja encadenada (menú → agenda) sigue abierta
        await open_task()
        await pg.locator(".row-btn", has_text="Mover, cambiar la hora").tap(); await pg.wait_for_timeout(700)
        check(await is_open() and "saltar solo este día" in (await pg.inner_text("#sheetBody")).lower(), "abrir una hoja desde otra no la cierra")
        await pg.locator(".sheet-x").tap(); await pg.wait_for_timeout(450)
        check(not await is_open(), "y luego se cierra con ✕")
        # 5. Botón atrás del navegador
        await open_task(); await pg.go_back(); await pg.wait_for_timeout(450)
        check(not await is_open() and "index.html" in pg.url, "el botón atrás cierra la hoja sin salir de la app")
        # 6. La hoja deja ver zona para tocar fuera
        await open_task(); top = (await pg.locator("#sheet").bounding_box())["y"]
        check(top >= 60, f"la hoja deja libre la parte de arriba ({top:.0f}px)")
        check(not errs, f"sin errores de JavaScript {errs[:2]}")
        await b.close()

asyncio.run(main())
print("\nRESULTADO:", "OK" if not fails else f"{len(fails)} fallos"); sys.exit(1 if fails else 0)
