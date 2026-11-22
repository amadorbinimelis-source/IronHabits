"""Pruebas de la v1.24 (bugs de hábitos y agenda) en un iPhone 13 simulado:
1) un hábito nuevo sale en la agenda diaria y semanal, con o sin hora, y sigue tras recargar;
2) hora con «Sin hora / Con hora», inicio y fin; 3) plantillas con sus pasos (copia independiente, editables, migración);
4) tiempo libre que se recorta y solapes reales lado a lado."""
import asyncio, json, sys
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
        await ctx.add_init_script("Object.defineProperty(navigator,'standalone',{get:()=>true})")
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-24T10:00:00+01:00")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(2500)

        # ── Migración v3 → v4: plantillas desde tus hábitos, sin tocar nada más
        old = await pg.evaluate("(()=>{const st=JSON.parse(localStorage.getItem(KEY));st.schema=3;delete st.templates;localStorage.setItem(KEY,JSON.stringify(st));return JSON.stringify([st.habits,st.logs])})()")
        await pg.reload(); await pg.wait_for_timeout(2500)
        r = await pg.evaluate("[S.schema,S.templates.map(t=>t.name),(S.templates.find(t=>t.name==='Francés')||{}).steps,JSON.stringify([lightState().habits,S.logs])]")
        check(r[0] >= 4 and "Francés" in r[1] and "Inglés" in r[1], f"migración a v4: plantillas desde tus hábitos {r[1]}")
        check(r[2] and len(r[2]) == 3 and "Smart Review" in r[2][0], f"la plantilla de Francés trae sus 3 pasos {r[2]}")
        check(json.loads(r[3])[1] == json.loads(old)[1] and len(json.loads(r[3])[0]) == len(json.loads(old)[0]), "la migración no toca hábitos ni registros")

        # ── Bug 2 + 1: crear con el formulario, con y sin hora
        await pg.evaluate("go('hoy');sel=todayK();openEditor()"); await pg.wait_for_timeout(300)
        check("En blanco" in await pg.inner_text("#sheetBody") and "Francés" in await pg.inner_text("#sheetBody"), "al pulsar + eliges «En blanco» o una plantilla")
        await pg.locator("#sheetBody .row-btn").first.tap(); await pg.wait_for_timeout(300)
        labels = await pg.evaluate("[...document.querySelectorAll('#sheetBody .lbl')].map(l=>l.textContent)")
        check(labels.index("¿A qué hora?") <= 1, f"«¿A qué hora?» justo después del nombre {labels[:3]}")
        await pg.locator("#sheetBody input").first.fill("Leer")
        await pg.locator("#sheetBody .btn.pri").last.tap(); await pg.wait_for_timeout(400)
        check(await pg.evaluate("!S.habits.some(h=>h.name==='Leer')") and "Elige cuándo" in await pg.inner_text("#toast"), "sin elegir «¿Cuándo?» no deja crearlo (siempre lo pregunta)")
        await pg.locator("#sheetBody .seg button", has_text="Se repite").tap(); await pg.wait_for_timeout(150)
        check(await pg.evaluate("D.schedule.mode") == "daily" and "Cada día" in await pg.inner_text("#sheetBody"), "«Se repite» muestra cada cuánto (por defecto, cada día)")
        await pg.locator("#sheetBody .seg button", has_text="Solo el").tap(); await pg.wait_for_timeout(150)
        await pg.locator("#sheetBody .btn.pri").last.tap(); await pg.wait_for_timeout(400)
        r = await pg.evaluate("(()=>{const h=S.habits.find(h=>h.name==='Leer');return [dayHabits(todayK()).includes(h),dayHabits(addDays(todayK(),1)).includes(h)]})()")
        check(r == [True, False], f"«Solo el …»: sale hoy y mañana no {r}")
        await pg.evaluate("openEditor(null,{blank:true})"); await pg.wait_for_timeout(300)
        await pg.locator("#sheetBody input").first.fill("Meditar")
        await pg.locator("#sheetBody .seg button", has_text="Se repite").tap(); await pg.wait_for_timeout(150)
        await pg.locator("#sheetBody .seg button", has_text="Con hora").tap(); await pg.wait_for_timeout(200)
        await pg.locator("#edTs").fill("17:00"); await pg.locator("#edTs").dispatch_event("change"); await pg.wait_for_timeout(150)
        await pg.locator("#edTe").fill("17:40"); await pg.locator("#edTe").dispatch_event("change"); await pg.wait_for_timeout(150)
        await pg.locator("#sheetBody .btn.pri").last.tap(); await pg.wait_for_timeout(400)
        t = await pg.evaluate("JSON.stringify(S.habits.find(h=>h.name==='Meditar').time)")
        check(t == '{"start":"17:00","dur":40}', f"hora con inicio y fin {t}")
        await pg.reload(); await pg.wait_for_timeout(2500)
        await pg.evaluate("go('agenda');sel=todayK();WKX.open=true;WKX.wide=todayK();renderAgenda()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("(()=>{const l=S.habits.find(h=>h.name==='Leer');return [[...document.querySelectorAll('.agw-nt.wide button')].some(b=>b.textContent.includes(l.emoji)),[...document.querySelectorAll('.agw-day.wide .agw-ev')].some(e=>/Meditar/.test(e.textContent)&&/17:00/.test(e.textContent))]})()")
        check(r[0], "tras recargar: el hábito sin hora sale en la fila «Sin hora» del día")
        check(r[1], "y el de hora, en su franja 17:00")
        await pg.evaluate("agView='week';WKX.open=true;renderAgenda()"); await pg.wait_for_timeout(300)
        w = await pg.evaluate("(()=>{const ids=['Leer','Meditar'].map(n=>S.habits.find(h=>h.name===n));return [document.querySelectorAll('.agw-nt').length,[...document.querySelectorAll('.agw-nt')].some(b=>b.textContent.includes(ids[0].emoji)),[...document.querySelectorAll('.agw-ev')].some(e=>e.title.startsWith('Meditar'))]})()")
        check(w[0] == 7 and w[1] and w[2], f"en la semana: fila «sin hora» y Meditar en su hora {w}")
        await pg.evaluate("evSheet(todayK(),'h:'+S.habits.find(h=>h.name==='Leer').id)"); await pg.wait_for_timeout(300)
        check("Ponerle hora" in await pg.inner_text("#sheetBody"), "un hábito sin hora tiene «Ponerle hora» desde la agenda")
        await pg.evaluate("closeSheet()")
        # Un solo día, creado mirando otro día
        k2 = await pg.evaluate("addDays(todayK(),2)")
        await pg.evaluate(f"go('hoy');sel='{k2}';openEditor(null,{{blank:true}})"); await pg.wait_for_timeout(300)
        await pg.locator("#sheetBody input").first.fill("Dentista")
        await pg.locator("#sheetBody .seg button", has_text="Solo el").tap(); await pg.wait_for_timeout(150)
        await pg.locator("#sheetBody .btn.pri").last.tap(); await pg.wait_for_timeout(300)
        r = await pg.evaluate(f"(()=>{{const h=S.habits.find(h=>h.name==='Dentista');return [h.start,h.schedule.mode,h.schedule.dates,dayHabits('{k2}').includes(h),dayHabits(todayK()).includes(h),dayHabits(addDays('{k2}',1)).includes(h)]}})()")
        check(r[0] == k2 and r[3] and not r[4] and not r[5], f"«Un solo día» creado mirando otro día: solo ese día {r}")

        # ── Bug 3: plantillas
        await pg.evaluate("sel=todayK();openEditor(null,{tpl:S.templates.find(t=>t.name==='Francés')})"); await pg.wait_for_timeout(300)
        await pg.locator("#sheetBody input").first.fill("Francés 2")
        await pg.locator("#sheetBody .seg button", has_text="Se repite").tap(); await pg.wait_for_timeout(150)
        await pg.locator("#sheetBody .btn.pri").last.tap(); await pg.wait_for_timeout(300)
        r = await pg.evaluate("(()=>{const a=getH('fr'),b=S.habits.find(h=>h.name==='Francés 2');return [b.type,b.steps.map(s=>s.text),b.steps.every(s=>!a.steps.some(x=>x.id===s.id)),!!(b.plan.program&&Object.keys(b.plan.program).length)]})()")
        check(r[0] == "checklist" and len(r[1]) == 3 and r[2], f"Francés desde plantilla: 3 pasos con ids propios {r[1]}")
        check(not r[3], "no copia el programa día a día (va ligado a las fechas de tu Francés)")
        await pg.evaluate("(()=>{const b=S.habits.find(h=>h.name==='Francés 2');sel=todayK();stepT(b.id,b.steps[0].id)})()")
        r = await pg.evaluate("(()=>{const b=S.habits.find(h=>h.name==='Francés 2'),t=S.templates.find(t=>t.name==='Francés');return [(entry(b,todayK())||{}).steps.length,(entry(getH('fr'),todayK())||{steps:[]}).steps.length,t.steps.length,JSON.stringify(t).includes(b.steps[0].id)]})()")
        check(r[0] == 1 and r[1] == 0 and r[2] == 3 and not r[3], f"tachar un paso de la copia no toca la plantilla ni tu Francés {r}")
        # editar una plantilla
        await pg.evaluate("go('set')"); await pg.wait_for_timeout(200)
        check("Plantillas de hábitos" in await pg.inner_text("#setBody"), "Ajustes › Plantillas de hábitos")
        await pg.evaluate("tplSheet()"); await pg.wait_for_timeout(300)
        i = await pg.evaluate("S.templates.findIndex(t=>t.name==='Francés')")
        await pg.evaluate(f"openEditor(null,{{tplEdit:{i}}})"); await pg.wait_for_timeout(300)
        check("Editar plantilla" in await pg.inner_text("#sheetBody"), "se edita con el mismo editor")
        await pg.evaluate("D.steps.push({id:uid(),text:'Repaso de vocabulario · 5 min'});edR()")
        await pg.locator("#sheetBody .btn.pri").last.tap(); await pg.wait_for_timeout(300)
        r = await pg.evaluate(f"[S.templates[{i}].steps.length,getH('fr').steps.length,S.habits.find(h=>h.name==='Francés 2').steps.length]")
        check(r == [4, 3, 3], f"editar los pasos de la plantilla no cambia los hábitos ya creados {r}")
        # guardar como plantilla al crear
        await pg.evaluate("openEditor(null,{blank:true});D.name='Estirar';D.type='checklist';D.steps=[{id:uid(),text:'Cuello'},{id:uid(),text:'Espalda'}];edWhen('repeat');D._saveTpl=true;edSave()"); await pg.wait_for_timeout(300)
        check(await pg.evaluate("S.templates.some(t=>t.name==='Estirar'&&t.steps.length===2)"), "«Guardar también como plantilla»")

        # ── Bug 4: tiempo libre
        await pg.evaluate("(()=>{const k=todayK(),l=dayEvents(k).find(e=>e.kind==='libre'&&tm(e.end)-tm(e.start)>=75);window._lib=l;agSet(k,'h:fr',{start:l.start,end:fmtT(tm(l.start)+45)});save();go('agenda');sel=k;WKX.open=true;WKX.wide=k;renderAgenda()})()"); await pg.wait_for_timeout(400)
        r = await pg.evaluate("(()=>{const ev=[...document.querySelectorAll('.agw-day.wide .agw-ev')],f=ev.find(e=>/Francés/.test(e.textContent)),fr=f.getBoundingClientRect(),full=document.querySelector('.agw-day.wide').getBoundingClientRect().width,libs=ev.filter(e=>e.classList.contains('libre')).map(e=>e.getAttribute('aria-label').split(' ').pop());return [Math.round(fr.width),Math.round(full),libs]})()")
        lib = await pg.evaluate("[_lib.start,_lib.end]")
        st = lib[0]; en45 = await pg.evaluate("fmtT(tm(_lib.start)+45)")
        check(abs(r[0] - r[1]) <= 4, f"un hábito sobre tiempo libre se ve a ancho completo ({r[0]} de {r[1]} px)")
        check(f"{st}–{lib[1]}" not in r[2] and f"{en45}–{lib[1]}" in r[2], f"el tiempo libre se recorta alrededor ({r[2]})")
        r = await pg.evaluate("freeParts([{kind:'libre',start:'18:00',end:'21:00',id:'l'},{kind:'habito',start:'19:00',end:'20:00',id:'h'}]).map(f=>fmtT(f.s)+'-'+fmtT(f.e))")
        check(r == ["18:00-19:00", "20:00-21:00"], f"libre 18–21 + hábito 19–20 → 18–19 y 20–21 {r}")
        # solape real: lado a lado
        await pg.evaluate("(()=>{const k=todayK(),c=dayEvents(k).find(e=>e.kind==='fijo');window._fx=c;agSet(k,'h:en',{start:c.start,end:fmtT(tm(c.start)+40)});save();renderAgenda()})()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("(()=>{const ev=[...document.querySelectorAll('.agw-day.wide .agw-ev')],a=ev.find(e=>/Inglés/.test(e.textContent)).getBoundingClientRect(),c=ev.find(e=>e.title.startsWith(_fx.title)&&!e.classList.contains('libre')).getBoundingClientRect();return [a.right<=c.left+1||c.right<=a.left+1,Math.round(a.width),Math.round(c.width)]})()")
        check(r[0], f"con un evento real se ven lado a lado, sin taparse {r}")
        await pg.evaluate("agView='week';WKX.open=true;WKX.wide=null;renderAgenda()"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("[...document.querySelectorAll('[data-colk=\"'+todayK()+'\"] .agw-ev.narrow')].map(e=>e.textContent.trim())")
        check(len(r) >= 2 and all(len(x) <= 9 for x in r), f"en la semana, lo que comparte columna se ve con icono y hora, sin texto cortado {r}")

        check(await pg.evaluate("APP_VERSION") >= "1.24", "versión 1.24 o posterior")
        check(not errs, f"sin errores de JS {errs[:3]}")
        await b.close()


async def eliminar():
    """v1.24.2: «Eliminar hábito» en el menú ⋯, el editor y la agenda; pide confirmación y se puede deshacer."""
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid", service_workers="block")
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-24T10:00:00+01:00")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(2500)
        await pg.evaluate("openEditor(null,{tpl:tplFrom(getH('fr'))});D.name='Francés prueba';edWhen('once');edSave()"); await pg.wait_for_timeout(300)
        hid = await pg.evaluate("S.habits.find(h=>h.name==='Francés prueba').id")
        await pg.evaluate(f"go('hoy');cardMenu('{hid}')"); await pg.wait_for_timeout(300)
        check("Eliminar hábito" in await pg.inner_text("#sheetBody"), "«Eliminar hábito» en el menú ⋯")
        await pg.locator("#sheetBody .row-btn.danger").tap(); await pg.wait_for_timeout(300)
        check("¿Seguro?" in await pg.inner_text("#sheetBody"), "pide confirmación")
        await pg.locator("#sheetBody .btn.danger").tap(); await pg.wait_for_timeout(600)
        check(await pg.evaluate(f"!getH('{hid}')"), "se elimina")
        await pg.locator("#toast button").first.tap(); await pg.wait_for_timeout(300)
        check(await pg.evaluate(f"!!getH('{hid}')"), "y se puede deshacer")
        await pg.evaluate(f"openEditor('{hid}')"); await pg.wait_for_timeout(300)
        check(await pg.evaluate("[...document.querySelectorAll('#sheetBody .btn.danger')].some(b=>/Eliminar hábito/.test(b.textContent))"), "y al final del editor")
        await pg.evaluate("closeSheet()"); await pg.wait_for_timeout(300)
        await pg.evaluate(f"evSheet(todayK(),'h:{hid}')"); await pg.wait_for_timeout(300)
        check("Eliminar hábito" in await pg.inner_text("#sheetBody"), "y al tocar su bloque en la Agenda")
        await pg.evaluate("openEditor(null,{blank:true})"); await pg.wait_for_timeout(300)
        check(not await pg.evaluate("[...document.querySelectorAll('#sheetBody .btn.danger')].length"), "al crear uno nuevo no sale «Eliminar»")
        check(not errs, f"sin errores de JS {errs[:2]}")
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(eliminar())
    print("FALLAN:" if fails else "TODO OK", fails if fails else "")
    sys.exit(1 if fails else 0)
