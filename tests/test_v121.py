"""Pruebas de la v1.21 (reevaluación, trozo 5) en un iPhone 13 simulado:
avisos push (lista de avisos, ajustes, envío al servidor) y nube que junta los cambios día a día."""
import asyncio, json, sys
from playwright.async_api import async_playwright
URL = "http://localhost:8765/index.html"
WORKER = "https://ironhabits-push.prueba.workers.dev"
fails = []
def check(c, m):
    print(("  ✓ " if c else "  ✗ ") + m)
    if not c: fails.append(m)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        ctx = await b.new_context(**p.devices["iPhone 13"], timezone_id="Europe/Madrid", service_workers="block")
        await ctx.add_init_script("Object.defineProperty(navigator,'standalone',{get:()=>true})")
        pg = await ctx.new_page(); await pg.clock.install(time="2026-11-24T08:00:00+01:00")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(2000)
        await pg.evaluate("S.logs={};S.agenda={};save();sel=todayK();go('hoy')"); await pg.wait_for_timeout(300)

        # ── Avisos: sin servidor publicado
        await pg.evaluate("go('set')"); await pg.wait_for_timeout(200)
        check("Avisos de tus hábitos" in await pg.inner_text("#setBody"), "fila «Avisos de tus hábitos» en Ajustes")
        await pg.evaluate("pushSheet()"); await pg.wait_for_timeout(500)
        check("aún no está listo" in await pg.inner_text("#sheetBody"), "sin push.json avisa de que el servidor no está listo (no falla)")
        await pg.evaluate("closeSheet()")

        # ── Lista de avisos
        it = await pg.evaluate("pushItems()")
        now = await pg.evaluate("Date.now()")
        check(len(it) > 10 and all(i["at"] > now for i in it), f"programa avisos futuros de 7 días ({len(it)})")
        check(all(it[i]["at"] <= it[i+1]["at"] for i in range(len(it)-1)), "ordenados por hora")
        check(max(i["at"] for i in it) - now < 7*864e5, "no pasa de 7 días")
        hab = await pg.evaluate("(()=>{const i=pushItems().find(x=>x.tag.startsWith(todayK()+'-h'));return i&&i.tag.split('-').slice(3).join('-')})()")
        hid = hab.split(':')[1] if hab and ':' in hab else None
        check(bool(hid), f"incluye hábitos de hoy con hora ({hid})")
        first = await pg.evaluate(f"pushItems().find(x=>x.tag.endsWith('h:{hid}')&&x.tag.startsWith(todayK()))")
        check(first and "En 5 min" in first["body"], "por defecto avisa 5 min antes y dice la hora")
        st = await pg.evaluate(f"(()=>{{const e=dayEvents(todayK()).find(e=>e.habit==='{hid}');const d=pk(todayK());d.setHours(0,tm(e.start)-5,0,0);return d.getTime()}})()")
        check(first and first["at"] == st, "la hora del aviso es la del hábito menos 5 min")
        await pg.evaluate(f"act('{hid}',todayK())"); await pg.wait_for_timeout(200)
        check(await pg.evaluate(f"!pushItems().some(x=>x.tag===todayK()+'-h:{hid}')"), "si ya lo marcaste hecho, no avisa")
        await pg.evaluate(f"pushHabit('{hid}',false)")
        check(await pg.evaluate(f"!pushItems().some(x=>x.tag.endsWith('h:{hid}'))"), "apagar un hábito quita sus avisos")
        await pg.evaluate(f"pushHabit('{hid}',true)")
        nf = await pg.evaluate("pushItems().filter(x=>!x.tag.includes('h:')).length")
        await pg.evaluate("pushCfg().fixed=false")
        check(nf > 0 and await pg.evaluate("pushItems().every(x=>x.tag.includes('h:'))"), "«también lo fijo» añade o quita clases y fútbol")
        await pg.evaluate("pushCfg().fixed=true;pushCfg().before=0")
        f0 = await pg.evaluate(f"pushItems().find(x=>x.tag.endsWith('h:{hid}'))")
        check(f0 and f0["body"].startswith("Ahora"), "«A la hora» avisa justo al empezar")
        await pg.evaluate("pushCfg().before=5;save()")

        # ── Envío al servidor (servidor y suscripción simulados)
        sent = []
        async def worker(route):
            if route.request.url.endswith("/sync"): sent.append(json.loads(route.request.post_data))
            await route.fulfill(status=200, content_type="application/json", body='{"ok":true,"publicKey":"x"}', headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Allow-Methods": "GET,POST,OPTIONS"})
        await pg.route(WORKER + "/**", worker)
        await pg.route("**/push.json", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps({"url": WORKER})))
        await pg.evaluate("window.pushSub=async()=>({endpoint:'https://web.push.apple.com/abc',toJSON(){return{endpoint:this.endpoint,keys:{p256dh:'a',auth:'b'}}}});pushCfg().on=true;save()")
        ok = await pg.evaluate("pushSync(true)")
        check(ok and len(sent) == 1 and sent[0]["sub"]["endpoint"].startswith("https://web.push.apple.com") and len(sent[0]["items"]) > 5, "manda la suscripción y los avisos al servidor")
        check(sent and all(set(i) == {"at", "title", "body", "tag", "url"} for i in sent[0]["items"]) and "logs" not in sent[0], "solo manda avisos: ni registros ni notas")
        n0 = len(sent[0]["items"]) if sent else 0
        nxt = await pg.evaluate("pushItems().find(x=>x.tag.includes('h:'))")
        nid = nxt["tag"].split("h:")[1]; nk = nxt["tag"][:10]
        await pg.evaluate(f"act('{nid}','{nk}')"); await pg.clock.run_for(5000); await pg.wait_for_timeout(300)
        check(len(sent) == 2 and len(sent[1]["items"]) == n0 - 1, "al marcar algo hecho vuelve a mandar la lista sin ese aviso")
        await pg.evaluate("pushSync()")
        check(len(sent) == 2, "si nada cambió, no vuelve a mandar")
        await pg.evaluate("go('set')"); await pg.wait_for_timeout(200)
        check("Activados" in await pg.inner_text("#setBody"), "Ajustes muestra «Activados · N en los próximos 7 días»")
        await pg.evaluate("pushSheet()"); await pg.wait_for_timeout(500)
        t = await pg.inner_text("#sheetBody")
        check("Enviar uno de prueba" in t and "Desactivar" in t and "próximos" in t.lower(), "pantalla de avisos: prueba, desactivar y próximos")
        sz = await pg.evaluate("[...document.querySelectorAll('#sheetBody .seg button,#sheetBody .btn')].map(b=>b.getBoundingClientRect().height)")
        check(min(sz) >= 44, f"botones de al menos 44 px ({min(sz):.0f})")
        await pg.evaluate("closeSheet()")

        # ── Nube: marcas de cambio por día y hábito
        k = await pg.evaluate("todayK()")
        check(await pg.evaluate(f"(S.touch['logs:{k}']||0)>0 && (S.touch['logs:{k}']||0)<=Date.now()"), "marcar algo apunta la hora del cambio en ese día")
        await pg.evaluate("setNote('nota prueba');"); await pg.clock.run_for(600)
        check(await pg.evaluate(f"!!S.touch['notes:{k}']"), "la nota del día también")

        # ── Juntar dos estados
        r = await pg.evaluate("""(()=>{
          const base={habits:[{id:'a',name:'A'},{id:'b',name:'B'}],logs:{},notes:{},agenda:{},minDays:{},checkins:{},reviews:{},settings:{x:1},touch:{}};
          const L=JSON.parse(JSON.stringify(base)),R=JSON.parse(JSON.stringify(base));
          L.logs['2026-11-20']={a:{v:1}};L.touch['logs:2026-11-20']=100;           // solo en este
          R.logs['2026-11-21']={b:{v:1}};R.touch['logs:2026-11-21']=100;           // solo en la nube
          L.logs['2026-11-22']={a:{v:1}};L.touch['logs:2026-11-22']=300;           // los dos: gana el más reciente
          R.logs['2026-11-22']={a:{v:0}};R.touch['logs:2026-11-22']=200;
          L.notes['2026-11-23']='vieja';L.touch['notes:2026-11-23']=100;R.notes['2026-11-23']='nueva';R.touch['notes:2026-11-23']=500;
          R.habits.push({id:'c',name:'C'});R.touch['h:c']=50;                       // hábito nuevo en la nube
          L.habits=L.habits.filter(h=>h.id!=='b');L.touch['h:b']=400;               // borrado aquí
          L.logs['2026-11-01']={a:{v:1}};                                            // datos antiguos sin marca
          R.settings={x:2};
          const m=mergeStates(L,R,false);
          return [!!m.logs['2026-11-20'],!!m.logs['2026-11-21'],m.logs['2026-11-22'].a.v,m.notes['2026-11-23'],m.habits.map(h=>h.id).join(''),!!m.logs['2026-11-01'],m.settings.x,m.touch['logs:2026-11-22']];
        })()""")
        check(r[0] and r[1], "junta días distintos de cada dispositivo")
        check(r[2] == 1 and r[3] == "nueva", "mismo día en los dos: gana el cambio más reciente")
        check(r[4] == "ac", f"hábito nuevo de la nube entra y el borrado aquí se queda borrado ({r[4]})")
        check(r[5], "no pierde datos antiguos sin marca de cambio")
        check(r[6] == 2 and r[7] == 300, "ajustes del lado más reciente y marcas actualizadas")

        # ── cloudPull con cambios en los dos lados: junta sin preguntar y sube
        await pg.evaluate("""(async()=>{
          localStorage.setItem(CLOUD_KEY,JSON.stringify({token:'t',login:'u',gistId:'g',icsGist:'i',names2:true,lastSync:'2026-11-20T00:00:00.000Z',dirtyAt:Date.now(),lastPushAt:0}));
          const st=lightState();st.notes={...st.notes,'2026-11-18':'desde el ordenador'};st.touch={...st.touch,'notes:2026-11-18':Date.now()-1000};st.settings={...st.settings,push:{on:false,id:'otro'}};
          window.cloudRemote=async()=>({kind:'ironhabits-sync',savedAt:new Date(Date.now()-1000).toISOString(),device:'Ordenador',state:st});
          window._pushed=0;window.cloudPush=async()=>{window._pushed++;};
          await cloudPull();
        })()"""); await pg.wait_for_timeout(500)
        r = await pg.evaluate(f"[S.notes['2026-11-18'],S.notes['{k}'],!!(S.logs['{k}']&&S.logs['{k}']['{hid}']),window._pushed,S.settings.push.on,S.settings.push.id!=='otro']")
        check(r[0] == "desde el ordenador" and r[1] == "nota prueba" and r[2], "trae lo del otro dispositivo sin perder lo de este")
        check(r[3] >= 1, "y sube el resultado a la nube")
        check(r[4] is True and r[5], "los avisos son de cada móvil: la nube no los pisa")
        check("¿Seguro?" not in await pg.inner_text("body"), "ya no pregunta cuál quedarse")

        # Versión
        check(await pg.evaluate("APP_VERSION") == "1.21", "versión 1.21")
        check(not errs, f"sin errores de JS {errs[:2]}")
        await b.close()

asyncio.run(main())
print("FALLAN:" if fails else "TODO OK", fails if fails else "")
sys.exit(1 if fails else 0)
