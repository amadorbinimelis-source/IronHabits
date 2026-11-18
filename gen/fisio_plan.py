"""Estudio de exámenes (1 h al día, L–S) + diagnóstico diferencial (3 h/semana: jue, sáb, dom) con app propia."""
import datetime

START = datetime.date(2026, 11, 19)

EXAMS = [  # (fecha, asignatura, qué, hora)
    (datetime.date(2026, 12, 4), "CMUS", "presentación", "17:00"),
    (datetime.date(2026, 12, 11), "CMUS", "2.º parcial", "15:00"),
    (datetime.date(2026, 12, 15), "NEDM", "prueba de plab", "15:00"),
    (datetime.date(2026, 12, 16), "LESP", "prueba de plab", "15:00"),
    (datetime.date(2026, 12, 22), "LESP", "examen", "17:00"),
    (datetime.date(2027, 1, 12), "NEDM", "examen", "16:00"),
    (datetime.date(2027, 1, 14), "CMUS", "examen", "15:00"),
]
RECUS = "Recuperaciones (solo si hacen falta): NEDM 20 ene · LESP 26 ene · CMUS 27 ene."
STUDY_END = datetime.date(2027, 1, 14)

def estudio():
    prog = {}
    d = START
    while d <= STUDY_END:
        if d.weekday() != 6:
            nxt = [e for e in EXAMS if e[0] >= d]
            today = [e for e in nxt if e[0] == d]
            if today:
                e = today[0]
                prog[d.isoformat()] = {"tag": f"🎯 Hoy: {e[1]} · {e[2]} ({e[3]})",
                                       "text": f"# Hoy tienes {e[1]} · {e[2]} a las {e[3]}\n- Por la mañana, solo repaso ligero de lo esencial.\n- Llega con tiempo. 💪"}
            else:
                e = nxt[0]; n = (e[0] - d).days
                lines = [f"- {x[1]} · {x[2]}: {x[0].day}/{x[0].month} (en {(x[0]-d).days} día{'s' if (x[0]-d).days != 1 else ''})" for x in nxt[:3]]
                prog[d.isoformat()] = {"tag": f"⏳ {e[1]} · {e[2]} en {n} día{'s' if n != 1 else ''}",
                                       "text": "# Próximos exámenes\n" + "\n".join(lines) + "\n- Tú decides qué estudiar. Usa el cronómetro de la app."}
        d += datetime.timedelta(days=1)
    return {"id": "estudio", "name": "Estudio de exámenes", "emoji": "📚", "color": "#22C55E",
            "desc": "1 h al día de lunes a sábado. Qué estudiar lo decides tú; la app te enseña la cuenta atrás. " + RECUS,
            "type": "time", "target": 60, "unit": "", "step": 1, "steps": [],
            "moment": "manana", "start": START.isoformat(), "archived": False,
            "schedule": {"mode": "weekdays", "days": [1, 2, 3, 4, 5, 6], "times": 3, "n": 2, "dates": []},
            "plan": {"mode": "none", "weekly": {}, "cycle": ["", ""], "program": prog}}

TOPICS = [
    "Razonamiento clínico y cribado: cuándo derivar",
    "Banderas rojas generales (cáncer, infección, fractura, cauda equina)",
    "Revisión por sistemas y anamnesis de cribado",
    "Dolor referido visceral: mapas",
    "Lumbar I: cauda equina, fractura, cáncer, infección",
    "Lumbar II: aneurisma de aorta abdominal, origen renal y visceral; radiculopatía frente a dolor referido",
    "Cervical I: disfunción arterial cervical (marco IFOMPT) y mielopatía",
    "Cervical II: inestabilidad, radiculopatía y cefaleas",
    "Torácica, pelvis y sacroilíaca: origen cardíaco, pulmonar y visceral",
    "Cadera e ingle I: pubalgia, choque femoroacetabular, labrum",
    "Cadera e ingle II: fractura de estrés del cuello femoral, hernias, dolor referido visceral",
    "Rodilla I: regla de Ottawa, LCA y menisco",
    "Rodilla II: patelofemoral, tendinopatías, dolor referido de cadera, tumores",
    "Tobillo y pie I: regla de Ottawa, esguinces, sindesmosis",
    "Tobillo y pie II: Lisfranc, fracturas de estrés, tendón de Aquiles",
    "Pierna y vascular: TVP (criterios de Wells), síndrome compartimental, claudicación",
    "Hombro: dolor referido cardíaco y diafragmático, tumor de Pancoast, cervical frente a hombro",
    "Codo, muñeca y mano: escafoides, compresiones nerviosas",
    "Neurológico: signos de motoneurona superior, ictus, conmoción en el deporte",
    "Sistémico e integración: reumatológico, oncológico y casos mezclados",
]
PAUSE = {"2026-12-17", "2026-12-19", "2026-12-20", "2027-01-07", "2027-01-09", "2027-01-10", "2027-01-14"}

def app_task(i, topic):
    if i == 0: return "Diseñamos juntos la estructura de la app: regiones, campos de cada ficha, mapa del cuerpo. Pídeme el esqueleto."
    if i == 1: return "Añade la sección de banderas rojas generales, cada una con su acción (derivar urgente o no urgente)."
    if i == 2: return "Añade la plantilla de anamnesis de cribado y la revisión por sistemas."
    if i == 3: return "Añade los mapas de dolor referido visceral."
    return f"Monta en la app la ficha de «{topic}»: banderas rojas, diferenciales, tests (con Sn/Sp/LR y fuente) y reglas de predicción si las hay."

def dx():
    prog = {}
    week = datetime.date(2026, 11, 16)
    i = 0
    while i < len(TOPICS):
        days = [(week + datetime.timedelta(days=o)) for o in (3, 5, 6)]
        active = [d for d in days if d >= START and d.isoformat() not in PAUSE]
        if not active:
            week += datetime.timedelta(days=7); continue
        topic = TOPICS[i]; n = i + 1
        for d in active:
            wd = d.weekday()
            if wd == 3:
                prog[d.isoformat()] = {"tag": f"Semana {n}/20 · Teoría", "moment": "manana",
                    "text": f"# 📖 Teoría · {topic}\n- Lee el tema en Goodman & Heick o en Physiopedia (y en la guía del JOSPT, si hay).\n- Apunta: banderas rojas, diferenciales, tests con su sensibilidad/especificidad y la fuente.\n- Estas notas son la base de la ficha del sábado."}
            elif wd == 5:
                prog[d.isoformat()] = {"tag": f"Semana {n}/20 · App", "moment": "tarde",
                    "text": f"# 🛠️ App de diagnóstico diferencial\n- {app_task(i, topic)}\n- Pásame tus notas del jueves y montamos la ficha juntos.\n- Comprueba cada número en su fuente antes de guardarlo."}
            else:
                prog[d.isoformat()] = {"tag": f"Semana {n}/20 · Caso clínico", "moment": "tarde",
                    "text": f"# 🩺 Caso clínico · {topic}\nPega en Claude:\n«Haz de paciente que viene a mi consulta de fisio con un problema relacionado con: {topic}. No me digas el diagnóstico. Responde solo a lo que te pregunte, como un paciente real. Cuando escriba \"hipótesis\", evalúa mi razonamiento, si he buscado banderas rojas y si debería derivar, y dime el diagnóstico.»\n- Ten tu app abierta mientras razonas." + ("\n\n🏁 Has terminado las 20 semanas: decidimos juntos la siguiente fase." if n == 20 else "")}
        i += 1
        week += datetime.timedelta(days=7)
    return {"id": "dx", "name": "Diagnóstico diferencial", "emoji": "🩺", "color": "#EC4899",
            "desc": "3 h por semana (jueves, sábado y domingo): teoría, app propia y caso clínico. 20 semanas para recorrer todo el cuerpo.",
            "type": "time", "target": 60, "unit": "", "step": 1, "steps": [],
            "moment": "any", "start": START.isoformat(), "archived": False,
            "schedule": {"mode": "dates", "days": [], "times": 3, "n": 2, "dates": sorted(prog)},
            "plan": {"mode": "none", "weekly": {}, "cycle": ["", ""], "program": prog}}

def build():
    return [estudio(), dx()]
