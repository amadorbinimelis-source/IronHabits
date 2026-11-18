"""Arrastrar bloques de la agenda para cambiarles la hora (iPhone simulado con toques reales y ordenador con ratón)."""
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
        cdp = await ctx.new_cdp_session(pg)
        async def touch(t, x=0, y=0):
            await cdp.send("Input.dispatchTouchEvent", {"type": t, "touchPoints": [] if t == "touchEnd" else [{"x": x, "y": y}]})
        ov = lambda k, i: pg.evaluate(f"agOv('{k}','{i}')")
        sheet_open = lambda: pg.evaluate("document.querySelector('#sheet').classList.contains('on')")

        for view, sel_ in (("week", ".agw-ev[data-id='h:fr'][data-k='2026-11-24']"), ("day", ".ag-ev[data-id='h:fr'][data-k='2026-11-24']")):
            await pg.evaluate(f"S.agenda={{}};save();sel='2026-11-24';agView='{view}';go('agenda')"); await pg.wait_for_timeout(400)
            el = pg.locator(sel_).first
            await el.scroll_into_view_if_needed(); bx = await el.bounding_box()
            x, y = bx["x"] + bx["width"] / 2, bx["y"] + min(10, bx["height"] / 2)
            s0 = await pg.evaluate(f"dayEvents('2026-11-24').find(e=>e.id==='h:fr').start")
            px = float(await el.get_attribute("data-px"))
            # 1. Mantener pulsado y arrastrar 1 h hacia abajo
            await touch("touchStart", x, y); await pg.wait_for_timeout(450)
            dy = 60 * px
            for i in range(1, 11): await touch("touchMove", x, y + dy * i / 10); await pg.wait_for_timeout(16)
            if view == "week": await pg.screenshot(path="/tmp/t/drag_week.png")
            await touch("touchEnd"); await pg.wait_for_timeout(500)
            o = await ov("2026-11-24", "h:fr")
            exp = await pg.evaluate(f"fmtT(tm('{s0}')+60)")
            check(o and o.get("start") == exp, f"[{view}] mantener y arrastrar 1 h: {s0} → {o and o.get('start')} (esperado {exp})")
            check(not await sheet_open(), f"[{view}] al soltar no se abre la ventana")
            check("Deshacer" in await pg.inner_text("#toast"), f"[{view}] aparece Deshacer")
            await pg.evaluate("doUndo()"); await pg.wait_for_timeout(300)
            check(not await ov("2026-11-24", "h:fr"), f"[{view}] Deshacer vuelve a la hora original")
            # 2. Deslizar rápido (scroll) no mueve nada
            el = pg.locator(sel_).first; bx = await el.bounding_box(); x, y = bx["x"] + bx["width"] / 2, bx["y"] + min(10, bx["height"] / 2)
            await touch("touchStart", x, y)
            for i in range(1, 6): await touch("touchMove", x, y + 20 * i); await pg.wait_for_timeout(16)
            await touch("touchEnd"); await pg.wait_for_timeout(400)
            check(not await ov("2026-11-24", "h:fr"), f"[{view}] deslizar rápido es scroll, no mueve el bloque")
            await pg.evaluate("closeSheet()")
            # 3. Toque normal abre la ventana (opción manual)
            el = pg.locator(sel_).first; bb = await el.bounding_box(); await pg.touchscreen.tap(bb['x']+bb['width']/2, bb['y']+4); await pg.wait_for_timeout(450)
            check(await sheet_open() and await pg.locator("#evS").count() == 1, f"[{view}] tocar abre la ventana con la hora manual")
            await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(300)
        await pg.screenshot(path="/tmp/t/drag_day.png")
        # 4. Ratón (ordenador)
        ctx2 = await b.new_context(viewport={"width": 1200, "height": 900}); pg2 = await ctx2.new_page()
        await pg2.goto(URL); await pg2.wait_for_timeout(1500)
        await pg2.evaluate("sel='2026-11-24';agView='week';go('agenda')"); await pg2.wait_for_timeout(400)
        el = pg2.locator(".agw-ev[data-id='h:fr'][data-k='2026-11-24']").first; bx = await el.bounding_box(); px = float(await el.get_attribute("data-px"))
        await pg2.mouse.move(bx["x"] + 20, bx["y"] + 8); await pg2.mouse.down()
        for i in range(1, 9): await pg2.mouse.move(bx["x"] + 20, bx["y"] + 8 - 30 * px * i / 8)
        await pg2.mouse.up(); await pg2.wait_for_timeout(400)
        o = await pg2.evaluate("agOv('2026-11-24','h:fr')")
        check(o and o.get("start"), f"ratón: arrastrar 30 min hacia arriba → {o and o.get('start')}")
        check(not errs, f"sin errores de JavaScript {errs[:2]}")
        await b.close()

asyncio.run(main())
print("\nRESULTADO:", "OK" if not fails else f"{len(fails)} fallos"); sys.exit(1 if fails else 0)
