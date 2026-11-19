"""Pruebas de la v1.20 (reevaluación, trozo 4: funciones nuevas) en un iPhone 13 simulado:
recolocar lo pendiente, modo «Empezar», comodín de racha, disposición del día, resumen del mes con imagen,
ordenar arrastrando, tema claro y exportar CSV."""
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
        ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid")
        await ctx.add_init_script("Object.defineProperty(navigator,'standalone',{get:()=>true})")
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-24T21:45:00+01:00")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(2000)
        await pg.evaluate("S.logs={};S.checkins={};S.agenda={};save();sel=todayK();go('hoy')"); await pg.wait_for_timeout(300)

        # Recolocar lo pendiente (21:45, nada hecho)
        r = await pg.evaluate("overdue(todayK()).map(h=>h.id)")
        check(len(r) >= 2, f"detecta lo pendiente cuya hora ya pasó {r}")
        check("pendiente" in await pg.evaluate("banners(todayK())") and await pg.evaluate("!!document.querySelector('.sec-act')"), "aviso «pendientes de hoy» y botón Recolocar en la franja")
        await pg.evaluate("replanSheet()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("window._replan.map(x=>x.p?[x.h.id,x.p.day,fmtT(x.p.start)]:[x.h.id,null])")
        mv = [x for x in r if x[1]]
        check(mv and all(x[1] > "2026-11-24" for x in mv), f"propone un hueco libre en los próximos días {mv[:2]}")
        check("Toca cada día" in await pg.inner_text("#sheetBody"), "a lo que toca todos los días le propone compensarlo en la semana")
        hid, day = mv[0][0], mv[0][1]
        await pg.evaluate("replanOne(0)"); await pg.wait_for_timeout(300)
        rr = await pg.evaluate(f"[!dayHabits(todayK()).some(h=>h.id==='{hid}'),dayHabits('{day}').some(h=>h.id==='{hid}'),!!agOv('{day}','in:{hid}')]")
        check(rr == [True, True, True], f"«Mover» lo pasa a ese día y hora {rr}")
        ov = await pg.evaluate(f"(()=>{{const o=agOv('{day}','in:{hid}');return overlaps('{day}','h:{hid}',tm(o.start),tm(o.end)).length}})()")
        check(ov == 0, "el hueco propuesto no se solapa con nada")
        await pg.evaluate("replanAll()"); await pg.wait_for_timeout(300)
        check(await pg.evaluate("overdue(todayK()).every(h=>!proposeSlot(h,todayK()))"), "«Recolocar todo» mueve todo lo que se puede mover")
        await pg.evaluate("closeSheet();undoAct()[1]()"); await pg.wait_for_timeout(300)
        check(await pg.evaluate("overdue(todayK()).length") >= 1, "y se puede deshacer")

        # Disposición del día
        await pg.evaluate("S.checkins[todayK()]={sleep:1,energy:2};save();render()"); await pg.wait_for_timeout(200)
        r = await pg.evaluate("[readiness(todayK()).score,!!document.querySelector('.rd-chip.rd-lo'),!!document.querySelector('.min-btn.suggest')]")
        check(r[0] < 45 and r[1] and r[2], f"disposición baja ({r[0]}) → propone el Día flojo")
        await pg.evaluate("S.checkins[todayK()]={sleep:5,energy:5};save();render()")
        check(await pg.evaluate("readiness(todayK()).score") >= 70, "disposición alta con buen sueño y energía")

        # Modo «Empezar»
        await pg.evaluate("S.agenda={};save();render()")
        check(await pg.evaluate("!!document.querySelector('.start-btn')"), "botón «▶ Empezar» en los hábitos pendientes de hoy")
        await pg.evaluate("focusMode('fuerza')"); await pg.wait_for_timeout(300)
        await pg.clock.run_for(125000); await pg.wait_for_timeout(300)
        r = await pg.evaluate("[document.querySelector('#focus').classList.contains('on'),document.querySelector('#foClock').textContent]")
        check(r[0] and r[1].startswith("02:0"), f"pantalla completa con el cronómetro en marcha ({r[1]})")
        await pg.evaluate("finishFocus()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("[isDone(getH('fuerza'),todayK()),entry(getH('fuerza'),todayK()).mins,document.querySelector('#focus').classList.contains('on')]")
        check(r[0] and r[1] == 2 and not r[2], f"«Terminar» lo marca hecho y guarda el tiempo {r}")
        await pg.evaluate("focusMode('fr')"); await pg.wait_for_timeout(300)
        await pg.evaluate("document.querySelector('#focus .step').click()"); await pg.wait_for_timeout(200)
        check(await pg.evaluate("(entry(getH('fr'),todayK()).steps||[]).length") == 1, "en una checklist se marcan los pasos desde el modo concentración")
        await pg.evaluate("closeFocus()")

        # Comodín de racha: semana anterior cumplida → un fallo esta semana no rompe la racha
        r = await pg.evaluate("""(()=>{const h=getH('fr'),t=todayK();S.logs={};h.start=addDays(t,-15);
          for(let i=15;i>=1;i--){const k=addDays(t,-i);if(i===1)continue;(S.logs[k]=S.logs[k]||{}).fr={v:0,steps:h.steps.map(s=>s.id)};}
          _wc=null;const st=streaks(h);return {cur:st.cur,frozen:st.frozen,freeze:st.freeze};})()""")
        check(True, f"(racha con hueco ayer, semana en curso: {r})")
        r = await pg.evaluate("""(()=>{const h=getH('fr');const _tk=todayK;todayK=()=>'2026-12-02';S.logs={};h.start='2026-11-16';
          for(let k='2026-11-16';k<='2026-12-01';k=addDays(k,1)){if(k==='2026-11-25')continue;(S.logs[k]=S.logs[k]||{}).fr={v:0,steps:h.steps.map(s=>s.id)};}
          _wc=null;const st=streaks(h);const fz=heatCells(h,4,false).cells.includes('var(--ice)');todayK=_tk;_wc=null;return {cur:st.cur,frozen:st.frozen,fz};})()""")
        check(r["frozen"] == ["2026-11-25"] and r["cur"] >= 15 and r["fz"], f"un día fallado gasta un comodín y la racha sigue {r}")
        await pg.evaluate("openDetail('fr')"); await pg.wait_for_timeout(300)
        check("comodín" in (await pg.inner_text("#sheetBody")).lower(), "el detalle enseña tus comodines")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(300)

        # Resumen del mes
        await pg.evaluate("S.logs={};for(let i=1;i<20;i++){const k=addDays(todayK(),-i);if(k.slice(0,7)!=='2026-11')continue;S.logs[k]={};for(const h of S.habits)if(showOn(h,k))S.logs[k][h.id]={v:60,steps:h.steps.map(s=>s.id)};}save()")
        await pg.evaluate("monthSheet('2026-11')"); await pg.wait_for_timeout(300)
        t = await pg.inner_text("#sheetBody")
        check("Resumen de noviembre" in t and "Días completos" in t, "resumen del mes con días completos y horas")
        size = await pg.evaluate("monthImage(monthSummary('2026-11')).then(b=>b.size)")
        check(size > 20000, f"genera la imagen para compartir ({size//1024} KB)")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(300)

        # Ordenar arrastrando
        await pg.evaluate("sortSheet()"); await pg.wait_for_timeout(300)
        before = await pg.evaluate("S.habits.map(h=>h.id)")
        h0 = await pg.locator(".so-row .so-h").nth(0).bounding_box(); h2 = await pg.locator(".so-row").nth(2).bounding_box()
        await pg.mouse.move(h0["x"] + 20, h0["y"] + 20); await pg.mouse.down()
        for i in range(1, 16): await pg.mouse.move(h0["x"] + 20, h0["y"] + 20 + (h2["y"] + h2["height"] - h0["y"]) * i / 15); await pg.wait_for_timeout(16)
        await pg.mouse.up(); await pg.wait_for_timeout(300)
        after = await pg.evaluate("S.habits.map(h=>h.id)")
        check(after != before and after.index(before[0]) >= 2, f"arrastrar cambia el orden ({before[:3]} → {after[:3]})")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(300)

        # Tema claro
        await pg.evaluate("setTheme('light');go('hoy')"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("[document.documentElement.dataset.theme,getComputedStyle(document.body).backgroundColor,getComputedStyle(document.querySelector('.hc')||document.body).color]")
        check(r[0] == "light" and r[1] in ("rgb(245, 245, 247)",), f"tema claro {r}")
        await pg.evaluate("setTheme('dark')")
        check(await pg.evaluate("document.documentElement.dataset.theme") == "dark", "vuelve al tema oscuro")

        # CSV
        csv = await pg.evaluate("(()=>{let out='';const _sf=shareFile;shareFile=(n,t)=>{out=n+'|'+t;return Promise.resolve(false)};exportCSV();shareFile=_sf;return out})()")
        check(csv.startswith("ironhabits-registros-") and "fecha;hábito;hecho;minutos" in csv and csv.count("\r\n") > 20, "exportar registros en CSV")
        check(not errs, f"sin errores de JavaScript {errs[:2]}")
        await b.close()

asyncio.run(main())
print("\nRESULTADO:", "OK" if not fails else f"{len(fails)} fallos"); sys.exit(1 if fails else 0)
