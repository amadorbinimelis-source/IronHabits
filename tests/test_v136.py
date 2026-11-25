"""Pruebas de la v1.36: plan de inglés ajustado al nivel real (meta 180, controles 170/175/180,
Listening Part 2 en las semanas 2–4 y traducción inversa semanal) y que llega al móvil al actualizar el plan."""
import asyncio, sys, json, pathlib, datetime
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
ROOT = pathlib.Path(__file__).resolve().parent.parent
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

async def main():
    p = json.loads((ROOT / "plan.json").read_text())
    en = next(h for h in p["habits"] if h["id"] == "en"); pr = en["plan"]["program"]; c = en["course"]
    check(p["version"] >= 14, f"plan v{p['version']}")
    check(c["goal"] == 180 and [x["goal"] for x in c["controls"]] == [170, 175, 180] and "180" in en["desc"], "meta 180 y controles 170/175/180")
    lp = [k for k, e in pr.items() if any(b["t"].startswith("Listening Part 2 ·") for b in e["blocks"])]
    check(len(lp) == 6 and lp[0] == "2026-11-30" and max(lp) <= "2026-12-18", f"6 sesiones de Listening Part 2 (semanas 2–4) {lp}")
    inv = [k for k, e in pr.items() if any(b["t"].startswith("Traducción inversa") for b in e["blocks"])]
    check(len(inv) >= 30 and all(datetime.date.fromisoformat(k).weekday() in (1, 3) for k in inv), f"traducción inversa martes y jueves ({len(inv)} días)")
    bad = [k for k, e in pr.items() if e.get("phase") in (1, 2) and not e.get("mark") and datetime.date.fromisoformat(k).weekday() < 5 and e["min"] != 75]
    check(not bad, f"los días L–V siguen siendo de 75 min {bad[:3]}")
    check(any("idea → por qué → ejemplo" in d for e in pr.values() for b in e["blocks"] if b["t"].startswith("Writing ·") for d in b["d"]), "cada writing empieza con el plan de 5 min")
    kitc = next(x for x in en["kit"] if x["id"] == "claude")["copy"]
    check("MODELO ·" in kitc and "COMPARA" in kitc and "180" in kitc, "el proyecto de Claude tiene las órdenes MODELO y COMPARA")
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path="/usr/bin/google-chrome")
        ctx = await b.new_context(**pw.devices["iPhone 13"], timezone_id="Europe/Madrid", service_workers="block")
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-30T08:00:00+01:00")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(3500)
        await pg.evaluate("localStorage.setItem('ironhabits_tour',JSON.stringify({done:true,minis:{}}))")
        r = await pg.evaluate("(()=>{const h=getH('en');return h&&[h.course.goal,(h.plan.program['2026-11-30']||{}).tag]})()")
        check(r and r[0] == 180 and "Listening Part 2" in r[1], f"la app tiene el plan nuevo {r}")
        await pg.evaluate("courseSheet('en','notes')"); await pg.wait_for_timeout(400)
        t = await pg.inner_text("#sheet")
        check("180 = tu meta" in t and "175" not in t, "Notas: «180 = tu meta»")
        check(not errs, f"sin errores de JS {errs[:2]}")
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(1 if fails else 0)
