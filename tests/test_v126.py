"""Pruebas de la v1.26: inglés hacia «casi C1» (plan en bloques, plan completo, material, notas por partes)
y auditoría del plan (horas, gramática, writings, speaking, controles y simulacros)."""
import asyncio, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "gen"))
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

def plan_checks():
    P = json.load(open(os.path.join(os.path.dirname(__file__), "..", "plan.json"), encoding="utf-8"))
    en = next(h for h in P["habits"] if h["id"] == "en")
    import ingles_plan
    errs = ingles_plan.audit(en)
    check(not errs, f"auditoría del plan de inglés sin fallos {errs}")
    pr = en["plan"]["program"]
    h = sum(e["min"] for e in pr.values()) / 60
    check(h >= 220, f"horas hasta el examen: {h:.0f} (≥ 220 para «casi C1»)")
    wk = [e["min"] for k, e in pr.items() if not e.get("mark") and k >= "2026-11-23" and __import__("datetime").date.fromisoformat(k).weekday() < 5]
    check(wk and all(m == 75 for m in wk), "lunes a viernes: 75 min")
    check(all(e.get("blocks") for e in pr.values()), "cada día tiene sus bloques")
    check(all(b.get("a") or b["m"] <= 10 or b["t"].startswith(("Hoy", "Mañana", "Escríbelo", "Revisión", "Corrige", "Vuelve", "Tus 5", "Repasa", "Logística", "Speaking P1")) or b.get("kit") for e in pr.values() for b in e["blocks"]), "los bloques largos tienen su botón o material")
    ag = P["agenda"]["2026-11-23"]; e = next(x for x in ag if x["id"] == "h:en")
    check(e["start"] < e["end"] and (int(e["end"][:2]) * 60 + int(e["end"][3:])) - (int(e["start"][:2]) * 60 + int(e["start"][3:])) == 75, "la agenda reserva 75 min al inglés")
    ids = {x["id"] for x in en["kit"]}
    check({"book", "claude", "hl", "7esl", "camb", "exam"} <= ids and all(x.get("need") for x in en["kit"]), "material con fecha de cuándo se necesita")
    check(not en.get("guide"), "la guía antigua de inglés ya no está (la sustituye 🧰 Material)")

async def main():
    plan_checks()
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid", service_workers="block", permissions=["clipboard-read", "clipboard-write"])
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-25T08:50:00+01:00")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        popups = []; ctx.on("page", lambda q: popups.append(q))
        await pg.goto(URL); await pg.wait_for_timeout(3000)
        check(await pg.evaluate("S.packs.amador>=13&&!!getH('en').course"), "el plan nuevo se instala solo")
        await pg.evaluate("sel=todayK();OPEN[todayK()+':en']=true;go('hoy');render()"); await pg.wait_for_timeout(300)
        t = await pg.inner_text("#hc-en")
        check("Writing · Essay" in t and "Plan completo" in t, "la tarjeta de Inglés enseña la clase en bloques y el acceso al plan")
        # copiar la orden para Claude
        await pg.locator("#hc-en .blk-go.cl").first.click(); await pg.wait_for_timeout(400)
        clip = await pg.evaluate("navigator.clipboard.readText()")
        check(clip.startswith("WRITING TAREA · Essay"), f"el botón copia la orden exacta para Claude ({clip})")
        check(len(popups) >= 1 and "claude.ai" in popups[-1].url, f"y abre Claude {[x.url for x in popups]}")
        # plan completo
        await pg.evaluate("courseSheet('en')"); await pg.wait_for_timeout(500)
        t = await pg.inner_text("#sheetBody")
        check("días para el examen" in t and "fase 1" in t.lower(), "plan completo: cuenta atrás y fases")
        n = await pg.evaluate("document.querySelectorAll('#crsBody .cw').length")
        check(n >= 30, f"todas las semanas a la vista ({n})")
        check(await pg.evaluate("document.querySelectorAll('#crsBody .cd.control').length>=8&&document.querySelectorAll('#crsBody .cd.mock').length>=12&&!!document.querySelector('#crsBody .cd.exam')"), "controles 📍, simulacros 🧪 y examen 🎯 marcados")
        check(await pg.evaluate("!!document.querySelector('#crsBody .cw.now .cd.today')"), "la semana y el día de hoy resaltados")
        sz = await pg.evaluate("Math.min(...[...document.querySelectorAll('#crsBody .cd:not(.empty)')].map(e=>e.getBoundingClientRect().height))")
        check(sz >= 43.5, f"días tocables (≥ 44 px: {sz:.0f})")
        await pg.evaluate("document.querySelector('#crsBody .cd.control').click()"); await pg.wait_for_timeout(300)
        t = await pg.inner_text("#sheetBody")
        check("Abrir" in t and "Plan completo" in t, "tocar un día abre su clase con el botón exacto")
        # material
        await pg.evaluate("courseSheet('en','kit')"); await pg.wait_for_timeout(300)
        t = await pg.inner_text("#sheetBody")
        check("Lo necesitas" in t and "Copiar instrucciones" in t, "material: cuándo lo necesitas y las instrucciones del proyecto de Claude")
        await pg.evaluate("closeSheet();go('hoy')"); await pg.wait_for_timeout(200)
        check(await pg.evaluate("noticeList(todayK()).some(x=>x.html.includes('Te falta'))"), "aviso en Hoy del material que falta")
        await pg.evaluate("for(const x of getH('en').kit)kitState(getH('en'))[x.id]=true;save();render()"); await pg.wait_for_timeout(200)
        check(await pg.evaluate("!noticeList(todayK()).some(x=>x.html.includes('Te falta'))"), "marcado «Lo tengo», el aviso desaparece")
        # notas por partes
        await pg.evaluate("courseSheet('en','notas');mockSheet();SF.p={p1:6,p2:5,p3:4,p4:7,p5:4,p6:3,p7:7,l:19};renderMockForm()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("[sfMock().r,sfMock().u,mockScore(sfMock()).sc]")
        check(r[0] == 6 + 8 + 6 + 7 and r[1] == 16, f"la app hace las cuentas (Reading {r[0]}/42, UoE {r[1]}/28)")
        check(r[2]["r"] == 165 and r[2]["l"] == 162, f"y pasa a la escala oficial {r[2]}")
        await pg.evaluate("saveMock()"); await pg.wait_for_timeout(300)
        check(await pg.evaluate("S.mocks.length===1&&!!S.mocks[0].parts&&!!document.querySelector('#crsBody')"), "se guarda en el mismo sitio que los simulacros de Progreso (sin duplicar)")
        await pg.evaluate("closeSheet();openDetail('en')"); await pg.wait_for_timeout(300)
        check("7ESL" in await pg.inner_text("#sheetBody") or "simulacros b2 first" in (await pg.inner_text("#sheetBody")).lower(), "y se ve también en el detalle de Inglés (Progreso)")
        await pg.evaluate("closeSheet()")
        # modo Empezar con bloques
        await pg.evaluate("focusMode('en')"); await pg.wait_for_timeout(300)
        check(await pg.evaluate("document.querySelectorAll('#focus .blk').length>=3"), "▶ Empezar enseña los bloques con su botón")
        await pg.evaluate("closeFocus()")
        check(await pg.evaluate("APP_VERSION") >= "1.26", "versión 1.26")
        check(not errs, f"sin errores de JS {errs[:3]}")
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
    print("FALLAN:" if fails else "TODO OK", fails if fails else "")
    sys.exit(1 if fails else 0)
