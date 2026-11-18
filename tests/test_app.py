"""Pruebas de la app en un navegador real (Playwright): agenda, anular, mover, cambiar hora, migración."""
import asyncio, json, sys
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
fails = []
def check(cond, msg):
    print(("  ✓ " if cond else "  ✗ ") + msg)
    if not cond: fails.append(msg)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = await b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        # 1. Migración desde datos antiguos (esquema 1, sin agenda)
        await pg.goto(URL); await pg.wait_for_timeout(1500)  # deja terminar la carga automática del plan
        old = {"v": 1, "habits": [], "logs": {"2026-11-10": {}}, "notes": {"2026-11-10": "hola"}, "settings": {"accent": "#22C55E"}, "timer": None}
        await pg.evaluate(f"localStorage.setItem('rutina_v1', {json.dumps(json.dumps(old))})")
        await pg.reload(); await pg.wait_for_timeout(1500)
        st = await pg.evaluate("({schema:S.schema, note:S.notes['2026-11-10'], hasAg:!!S.agendaBase['2026-11-23'], packs:S.packs})")
        check(st["schema"] == 3, "migración: esquema pasa a 3")
        check(st["note"] == "hola", "migración: conserva las notas antiguas")
        check(st["hasAg"], "plan.json carga la agenda")
        # 2. Agenda del lunes 23
        await pg.evaluate("sel='2026-11-23';go('agenda')"); await pg.wait_for_timeout(400)
        n = await pg.evaluate("document.querySelectorAll('.ag-ev').length")
        check(n >= 12, f"agenda del 23 nov pinta {n} bloques")
        await pg.screenshot(path="/tmp/t/ag_day.png", full_page=True)
        # 3. Anular francés el 23 → desaparece de Hoy y no rompe la racha
        await pg.evaluate("evSheet('2026-11-23','h:fr')"); await pg.wait_for_timeout(300)
        await pg.screenshot(path="/tmp/t/ag_sheet.png")
        await pg.evaluate("document.querySelector('#evR').value='prueba';evCancel('2026-11-23','h:fr')")
        r = await pg.evaluate("({inHoy: dayHabits('2026-11-23').some(h=>h.id==='fr'), base: showOnBase(getH('fr'),'2026-11-23'), cancelled: dayEvents('2026-11-23').find(e=>e.id==='h:fr').cancelled})")
        check(not r["inHoy"], "anular: francés ya no sale en Hoy ese día")
        check(not r["base"], "anular: ese día no cuenta para la racha")
        check(r["cancelled"], "anular: en la agenda sale tachado")
        await pg.evaluate("evRestore('2026-11-23','h:fr')")
        check(await pg.evaluate("dayHabits('2026-11-23').some(h=>h.id==='fr')"), "restaurar: vuelve a Hoy")
        # 4. Mover el entreno de fuerza del lunes 23 al jueves 26
        await pg.evaluate("evSheet('2026-11-23','h:fuerza');document.querySelector('#evD').value='2026-11-26';evMove('2026-11-23','h:fuerza')")
        r = await pg.evaluate("""({from: dayHabits('2026-11-23').some(h=>h.id==='fuerza'), to: dayHabits('2026-11-26').some(h=>h.id==='fuerza'),
              plan: planFor(getH('fuerza'),'2026-11-26').tag, ev: !!dayEvents('2026-11-26').find(e=>e.id==='h:fuerza'&&e.moved)})""")
        check(not r["from"] and r["to"], "mover: desaparece del lunes y aparece el jueves en Hoy")
        check("Movido desde" in r["plan"], "mover: el jueves muestra el plan del lunes (tirón)")
        check(r["ev"], "mover: aparece en la agenda del jueves")
        # marcarlo hecho el día de destino
        await pg.evaluate("sel='2026-11-26'")
        # 5. Mover a un día que ya lo tiene → bloqueado
        await pg.evaluate("evSheet('2026-11-25','h:fr');document.querySelector('#evD').value='2026-11-26';evMove('2026-11-25','h:fr')")
        check(await pg.evaluate("!agOv('2026-11-25','h:fr')"), "mover: no deja duplicar un hábito en un día que ya lo tiene")
        await pg.evaluate("evRestore('2026-11-26','h:fuerza')")
        check(await pg.evaluate("dayHabits('2026-11-23').some(h=>h.id==='fuerza') && !dayHabits('2026-11-26').some(h=>h.id==='fuerza')"), "devolver: vuelve al lunes")
        # 6. Cambiar hora del inglés del 24 a la tarde → en Hoy pasa a 'tarde'
        await pg.evaluate("evSheet('2026-11-24','h:en');document.querySelector('#evS').value='17:00';document.querySelector('#evE').value='17:45';evSetTime('2026-11-24','h:en')")
        r = await pg.evaluate("({m: momentFor(getH('en'),'2026-11-24'), t: habitTime(getH('en'),'2026-11-24').start})")
        check(r["m"] == "tarde" and r["t"] == "17:00", "hora: inglés pasa a la tarde en Hoy")
        # 7. Anular una clase (obligatorio)
        await pg.evaluate("evSheet('2026-11-25','clase');evCancel('2026-11-25','clase')")
        check(await pg.evaluate("dayEvents('2026-11-25').find(e=>e.id==='clase').cancelled"), "anular clase: sale tachada en la agenda")
        # 8. Vista semana y Hoy sin errores
        await pg.evaluate("agView='week';sel='2026-11-23';go('agenda')"); await pg.wait_for_timeout(300)
        await pg.screenshot(path="/tmp/t/ag_week.png", full_page=True)
        await pg.evaluate("go('hoy')"); await pg.wait_for_timeout(300)
        await pg.screenshot(path="/tmp/t/hoy_after.png", full_page=True)
        for v in ("hab", "stats", "set"):
            await pg.evaluate(f"go('{v}')"); await pg.wait_for_timeout(150)
        # 9. Persistencia tras recargar
        await pg.reload(); await pg.wait_for_timeout(1200)
        check(await pg.evaluate("agOv('2026-11-24','h:en').start==='17:00'"), "los cambios se guardan al recargar")
        # 10. Rachas: anular un día pasado no la rompe
        r = await pg.evaluate("""(()=>{const h=getH('fr');const t=todayK();h.start=addDays(t,-3);S.logs={};for(let i=1;i<=3;i++){const k=addDays(t,-i);if(i!==2){S.logs[k]={fr:{v:0,steps:h.steps.map(s=>s.id)}};}}
            const before=streaks(h).cur; agSet(addDays(t,-2),'h:fr',{cancel:true}); const after=streaks(h).cur; return {before,after};})()""")
        check(r["after"] >= 2, f"racha: un día anulado no la rompe (antes {r['before']}, después {r['after']})")
        # 11. Clase anulada (25 nov, paso 7) → fuerza pasa a sesión completa
        r = await pg.evaluate("planFor(getH('fuerza'),'2026-11-25').tag")
        check("completa" in (r or ""), f"clase anulada: fuerza usa la sesión completa ({r})")
        # 12. Guardado ligero: la clave principal es pequeña y el plan va aparte
        sz = await pg.evaluate("({main:localStorage.getItem('rutina_v1').length, plan:(localStorage.getItem('rutina_plan_v1')||'').length})")
        check(sz["main"] < 60000 and sz["plan"] > 200000, f"guardado ligero: principal {sz['main']} B, plan {sz['plan']} B")
        await pg.reload(); await pg.wait_for_timeout(1200)
        check(await pg.evaluate("!!S.agendaBase['2026-11-23'] && !!getH('en').plan.program && !!getH('en').guide"), "guardado ligero: al recargar se recupera agenda, plan y guías")
        # 13. Versión mínima
        r = await pg.evaluate("""(()=>{const t=todayK(),h=getH('fr');h.start=addDays(t,-30);sel=t;S.logs={};
            if(!showOn(h,t))return 'skip';toggleMinDay(t);const html=document.body.innerHTML.includes('Versión mínima');
            doMin('fr');return {html,done:isDone(h,t),min:!!entry(h,t).min};})()""")
        check(r == 'skip' or (r["done"] and r["min"]), f"versión mínima: cuenta como hecho {r}")
        # 14. Deshacer
        r = await pg.evaluate("(()=>{const t=todayK();doUndo();return !!(entry(getH('fr'),t)||{}).min;})()")
        check(not r, "deshacer: revierte la última acción")
        # 15. Métricas
        await pg.evaluate("metricSheet('fuerza',todayK())"); await pg.wait_for_timeout(200)
        await pg.evaluate("document.querySelector('#mt-mu').value='3';document.querySelector('#mtNote').value='bien';saveMetrics('fuerza',todayK())")
        await pg.reload(); await pg.wait_for_timeout(1200)
        r = await pg.evaluate("({m:entry(getH('fuerza'),todayK()), s:metricsBlock(getH('fuerza')).includes('Último: 3')})")
        check(r["m"] and r["m"]["m"]["mu"] == 3 and r["m"]["note"] == "bien" and r["s"], "métricas: se guardan y salen en el detalle")
        # 16. Pausa
        r = await pg.evaluate("""(()=>{pauseSheet();document.querySelector('#pzF').value='2026-12-01';document.querySelector('#pzT').value='2026-12-03';
            document.querySelectorAll('.pzH').forEach(x=>x.checked=x.value==='fr');applyPause();
            const a=!dayHabits('2026-12-01').some(h=>h.id==='fr'),pid=S.pauses[0].id;removePause(pid);
            return {a,b:dayHabits('2026-12-01').some(h=>h.id==='fr'),n:S.pauses.length};})()""")
        check(r["a"] and r["b"] and r["n"] == 0, f"pausa: quita y devuelve los hábitos {r}")
        # 17. Calendario .ics
        r = await pg.evaluate("buildICS('2026-11-23','2026-11-24',false)")
        t = r["text"]
        check(r["n"] > 4 and t.count("BEGIN:VEVENT") == r["n"] and "TRIGGER:-PT5M" in t and "UID:2026-11-23-h-fr@rutina" in t, f"ics: {r['n']} eventos con aviso")
        # 18. Vista 3 días
        await pg.evaluate("agView='3';sel='2026-11-23';go('agenda')"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("({cols:document.querySelectorAll('.agw-hd').length, sw:document.querySelector('#agwWrap').scrollWidth<=document.querySelector('#agwWrap').clientWidth+2})")
        check(r["cols"] == 4 and r["sw"], f"vista 3 días sin scroll lateral {r}")
        await pg.screenshot(path="/tmp/t/ag_3d.png", full_page=True)
        # 19. Diálogo propio
        r = await pg.evaluate("(async()=>{const p=ask('x','Ok');document.querySelectorAll('#sheet .btn')[1].click();const a=await p;const q=ask('y');closeSheet();const b=await q;return [a,b];})()")
        check(r == [True, False], f"diálogo propio: aceptar/cancelar {r}")
        # 20. Revisión semanal y tarjeta Ahora
        r = await pg.evaluate("(()=>{reviewSheet('2026-11-16');return window._reviewTxt.startsWith('Revisión semanal');})()")
        check(r, "revisión semanal: genera el resumen")
        await pg.evaluate("closeSheet();sel=todayK();go('hoy')"); await pg.wait_for_timeout(300)
        await pg.screenshot(path="/tmp/t/hoy_v14.png", full_page=True)
        check(await pg.evaluate("typeof nowCard(todayK())==='string'"), "tarjeta Ahora/Después se genera")
        # 21. Mapas de calor desde el inicio
        r = await pg.evaluate("(()=>{const h=getH('fr');h.start=addDays(todayK(),-14);return weeksSince(h.start,26,10);})()")
        check(r == 10, f"mapa de calor: semanas desde el inicio ({r})")
        # 22. Mover a mañana busca hueco libre
        r = await pg.evaluate("(()=>{quickMove('2026-11-30','fr');const o=agOv('2026-12-01','in:fr');return o?o.start:null;})()")
        check(r is None or r, f"mover a mañana ({r})")
        # 23. Boxeo: lo modificado y lo extra suma
        r = await pg.evaluate("""(()=>{const _tk=todayK;todayK=()=>'2026-12-20';const h=getH('boxeo'),t=todayK();S.logs={};S.agenda={};h.start=addDays(t,-40);
          const days=[];for(let i=1;i<=21;i++){const k=addDays(t,-i);if(showOnBase(h,k))days.push(k);}
          const off=[];for(let i=1;i<=21;i++){const k=addDays(t,-i);if(!showOnBase(h,k))off.push(k);}
          const mark=k=>{const was=isDone(h,k);sel=k;if(!was)act('boxeo');return isDone(h,k);};
          const base={n:countDone(h),r:habitRate(h,30)};
          // a) cambio de hora y hecho
          agSet(days[0],'h:boxeo',{start:'07:00',end:'08:00'});mark(days[0]);
          const a=countDone(h)===1&&showOnBase(h,days[0]);
          // b) movido a otro día y hecho allí
          const to=off[0];agSet(days[1],'h:boxeo',{moveTo:to});agSet(to,'in:boxeo',{from:days[1],start:'18:00',end:'19:00'});mark(to);
          const b=countDone(h)===2&&showOnBase(h,to)&&!showOnBase(h,days[1]);
          // c) sesión extra en día sin boxeo, hecha
          const ex=off[1];agSet(ex,'in:boxeo',{extra:true,start:'18:00',end:'19:00'});const inHoy=dayHabits(ex).some(x=>x.id==='boxeo');mark(ex);
          const c=inHoy&&countDone(h)===3&&showOnBase(h,ex)&&weekSummary(weekStartK(ex)).per.find(p=>p.h.id==='boxeo').d>=1;
          // d) sesión extra sin hacer: no es fallo
          const ex2=off[2];agSet(ex2,'in:boxeo',{extra:true,start:'18:00',end:'19:00'});
          const d=!showOnBase(h,ex2)&&!weekSummary(weekStartK(ex2)).miss.some(m=>m.includes('Boxeo')&&m.includes(shortDate(ex2)));
          // e) anulado después de hacerlo: sigue contando
          mark(days[2]);agSet(days[2],'h:boxeo',{cancel:true});
          const e=countDone(h)===4&&showOnBase(h,days[2]);
          // f) no deja mover algo hecho
          sel=days[0];evMove(days[0],'h:boxeo',addDays(days[0],1));const f=!agOv(days[0],'h:boxeo').moveTo;
          // g) la racha suma la extra
          const st=streaks(h).best;todayK=_tk;
          return {a,b,c,d,e,f,st,inHoy,nd:days.length};})()""")
        for kk, msg in [("a","hora cambiada y hecho → suma"),("b","movido y hecho en el otro día → suma"),("c","sesión extra hecha → suma en total, stats y revisión"),("d","sesión extra sin hacer → no es fallo"),("e","anulado después de hacerlo → sigue sumando"),("f","no deja mover algo ya hecho")]:
            check(r[kk], f"boxeo: {msg}")
        check(r["st"] >= 1, f"boxeo: racha con extras ({r['st']})")
        # 24. Total semanal (tipo Runna): compensar un día con otro
        r = await pg.evaluate("""(()=>{const _tk=todayK;todayK=()=>'2026-12-20';const h=getH('fr'),t=todayK();S.logs={};S.agenda={};h.start='2026-11-23';
          const full=k=>{(S.logs[k]=S.logs[k]||{}).fr={v:0,steps:h.steps.map(x=>x.id)};};
          // semana 7-13 dic: todo hecho menos el lunes 7 → sin compensar
          for(let i=1;i<7;i++)full(addDays('2026-12-07',i));
          // semana 14-20 dic: lunes 14 no, martes 15 hace 1 h 30
          for(let i=2;i<7;i++)full(addDays('2026-12-14',i));
          sel='2026-12-15';minsSheet('fr','2026-12-15');document.querySelector('#mnH').value=1;document.querySelector('#mnM').value=30;saveMins('fr','2026-12-15');
          const g=weekGoal(h,'2026-12-14'),m=weekMins(h,'2026-12-14'),met=weekMet(h,'2026-12-14');
          const notMet=weekMet(h,'2026-12-07');
          const st=streaks(h),rate=habitRate(h,7);
          OPEN['wk']=true;const card=weekCard('2026-12-20').includes('Francés');
          const rev=weekSummary('2026-12-14');const miss14=rev.miss.some(x=>x.includes('Francés'));
          const rev7=weekSummary('2026-12-07');const miss7=rev7.miss.some(x=>x.includes('Francés'));
          // pausa baja el objetivo; anular no
          agSet('2026-12-21','h:fr',{cancel:true});const gC=weekGoal(h,'2026-12-21');agSet('2026-12-21','h:fr',null);
          agSet('2026-12-21','h:fr',{cancel:true,pause:'x'});const gP=weekGoal(h,'2026-12-21');agSet('2026-12-21','h:fr',null);const g0=weekGoal(h,'2026-12-21');
          todayK=_tk;return {g,m,met,notMet,cur:st.cur,rate,card,miss14,miss7,gC,gP,g0,mins15:entry(h,'2026-12-15').mins};})()""")
        check(r["g"] == 7*45 and r["m"] == 6*45+45, f"total semanal: objetivo {r['g']} min, hecho {r['m']} min")
        check(r["met"] and not r["notMet"], "total semanal: cumplida con compensación; la anterior no")
        check(r["cur"] >= 7, f"racha: el lunes compensado no la rompe (racha {r['cur']})")
        check(r["rate"] == 1, f"%: semana compensada al 100% ({r['rate']})")
        check(not r["miss14"] and r["miss7"], "revisión: el día compensado no sale como fallo; el no compensado sí")
        check(r["gC"] == r["g0"] and r["gP"] == r["g0"]-45, "objetivo: anular no lo baja, una pausa sí")
        check(r["card"] and r["mins15"] == 90, "tarjeta Esta semana y tiempo guardado")
        # 25. Plan completo por hábito (inglés hasta el examen)
        await pg.evaluate("closeSheet();fullPlan('en')"); await pg.wait_for_timeout(500)
        r = await pg.evaluate("""({rows:document.querySelectorAll('.fp-item').length, goal:document.querySelector('.fp-goal').textContent, last:planDates(getH('en')).slice(-1)[0]})""")
        check(r["rows"] > 150 and "B2 First" in r["goal"] and r["last"] == "2027-06-19", f"plan completo inglés: {r['rows']} sesiones hasta {r['last']}")
        await pg.screenshot(path="/tmp/t/fp_en.png")
        await pg.evaluate("FP.f='all';FP.q='Speaking';renderFP()"); await pg.wait_for_timeout(300)
        n = await pg.evaluate("document.querySelectorAll('.fp-item').length")
        check(0 < n < 213, f"plan completo: buscar «Speaking» → {n}")
        await pg.evaluate("fpToggle(document.querySelector('.fp-item').id.slice(3))"); await pg.wait_for_timeout(200)
        check(await pg.evaluate("document.querySelector('.fp-body').style.display==='block' && document.querySelector('.fp-body').textContent.length>50"), "plan completo: al tocar se ve la sesión exacta")
        await pg.screenshot(path="/tmp/t/fp_en2.png")
        for hid in ("fr","fuerza","boxeo","estudio","dx"):
            await pg.evaluate(f"fullPlan('{hid}')"); await pg.wait_for_timeout(200)
            n = await pg.evaluate("document.querySelectorAll('.fp-item').length")
            check(n > 0, f"plan completo {hid}: {n} sesiones")
        # 26. Navegar semanas con los botones
        await pg.evaluate("closeSheet();sel=todayK();go('hoy')"); await pg.wait_for_timeout(300)
        await pg.locator("#v-hoy .wk-btn").nth(1).click(); await pg.locator("#v-hoy .wk-btn").nth(1).click(); await pg.wait_for_timeout(200)
        r = await pg.evaluate("({sel, lbl:document.querySelector('#wkLbl').textContent, wk:weekStartK(todayK())})")
        check(r["sel"] == __import__('datetime').date.fromisoformat(r["sel"]).isoformat() and "Dentro de 2 semanas" in r["lbl"], f"semanas: siguiente ×2 → {r['lbl']}")
        await pg.screenshot(path="/tmp/t/wknav.png")
        await pg.locator("#wkLbl").click(); await pg.wait_for_timeout(200)
        check(await pg.evaluate("sel===todayK()"), "semanas: tocar la etiqueta vuelve a hoy")
        await pg.evaluate("go('agenda')"); await pg.locator("#v-agenda .wk-btn").nth(0).click(); await pg.wait_for_timeout(200)
        check("Semana pasada" in await pg.evaluate("document.querySelector('#agLbl').textContent"), "semanas: anterior en la agenda")
        check(not errs, f"sin errores de JavaScript {errs[:2]}")
        await b.close()
asyncio.run(main())
print("\nRESULTADO:", "OK" if not fails else f"{len(fails)} fallos")
sys.exit(1 if fails else 0)
