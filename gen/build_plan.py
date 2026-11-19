"""Genera plan.json (paquete de plan para la app IronHabits)."""
import json, datetime, urllib.parse, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from frances_data import WEEKS
import ingles_plan, entreno_plan, fisio_plan, guias, agenda_plan

START = datetime.date(2026, 11, 23)          # lunes de la semana 1
PREP = [datetime.date(2026, 11, d) for d in (19, 20, 21, 22)]
EXAM_DAYS = {"2026-12-15", "2026-12-16", "2026-12-22", "2027-01-12", "2027-01-14"}

def yt(q): return "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(q)

def de(rol):
    for a,b in (("un ","d'un "),("une ","d'une "),("le ","du "),("les ","des ")):
        if rol.startswith(a): return b+rol[len(a):]
    return "de "+rol

def level(n):
    return "A1" if n <= 13 else "A2" if n <= 39 else "B1"

def serie(n):
    if n <= 13: return f"Extr@ en français · episodio {n} (con subtítulos en francés)", yt(f"Extr@ en français épisode {n}")
    if n <= 26: return f"Extr@ en français · episodio {n-13} otra vez, ahora sin subtítulos", yt(f"Extr@ en français épisode {n-13}")
    if n <= 43:
        e = n - 26  # 17 episodios: P1 1-5, P2 6-10, P3 11-17
        p, ep = (1, e) if e <= 5 else (2, e - 5) if e <= 10 else (3, e - 10)
        return f"Lupin (Netflix) · parte {p}, episodio {ep} · audio y subtítulos en francés", None
    if n <= 49: return f"Dix pour cent (Netflix) · T1, episodio {n-43} · audio y subtítulos en francés", None
    if n == 50: return "Película: Intouchables · audio y subtítulos en francés", None
    return "Libre: lo que te apetezca en francés (serie, película o YouTube)", None


def phrases_block(w):
    return "\n".join(f"- {fr} → {es}" for fr, es in w["ph"])

def day_text(n, w, wd):
    lv = level(n)
    if w.get("review"):
        return review_text(n, w, wd)
    if wd == 0:
        return ("Isla nueva", "# 🏝️ Empiezas una isla nueva en HyperLingua\n- Elige la siguiente isla (o repite la anterior si el domingo no te salió).\n- Lee todas las frases y entiende qué significan.\n- Primeras escuchas: ponla en bucle 2–3 veces repitiendo detrás.")
    if wd == 1:
        return ("Más isla", "# 🎧 Shadowing en bucle\n- Pon la isla en bucle y repite cada frase justo detrás del audio, imitando el ritmo.\n- Vale hacerlo en el trayecto.")
    if wd == 2:
        size = {"A1": "6–8 frases", "A2": "8–10 frases", "B1": "un texto de 120–160 palabras"}[lv]
        return ("Escritura", f"# ✍️ Escritura\n- Escribe {size} tuyas usando lo de la isla que estés haciendo.\n- Pégalas en Claude: «Corrige mon texte et explique mes erreurs en espagnol.»\n- Las correcciones útiles, añádelas a My Collections.")
    if wd == 3:
        part = "las 30 preguntas" if n % 2 else "las 30 frases"
        extra = "\n- Hoy además: pídeme un lote nuevo de frases de fisio de tu nivel para importarlas." if n in (13, 26, 39) else ""
        return ("Mi trabajo", f"# 🩺 Colección «Mi trabajo»\n- Esta semana tocan {part} de fisio.\n- Shadowing de todas y después traducir de memoria del español al francés.{extra}")
    if wd == 4:
        lvl = {"A1": "débutant (A1)", "A2": "A2", "B1": "B1"}[lv]
        return ("Hablar", f"# 🗣️ Role-play\nAbre Claude en modo voz (o escribe) y pega, cambiando el tema por el de tu isla:\n«Faisons une conversation sur le thème : [tema de mi isla]. Parle lentement, niveau {lvl}. Pose-moi des questions. À la fin, corrige mes erreurs en espagnol.»\n- 10 min de conversación.")
    if wd == 5:
        s_, link = serie(n)
        return ("Serie", f"# 📺 {s_}\n- Apunta 3 expresiones y añádelas a My Collections." + (f"\n{link}" if link else ""))
    if wd == 6:
        mins = {"A1": "1 minuto", "A2": "2 minutos", "B1": "3 minutos"}[lv]
        return ("Reto", f"# 🎙️ Reto del domingo\n- Grábate {mins} diciendo la isla de memoria.\n- Si te sale bien, el lunes pasas a la siguiente; si no, la repites una semana más.")

def review_text(n, w, wd):
    r = w["review"]
    if r == "A2":
        L = [("Repaso", "# Repaso de islas\n- Repite las 2–3 islas que más te costaron estos meses."),
             ("Más isla", "# Shadowing de las islas repasadas"),
             ("Escritura", "# ✍️ Cuenta tu semana (8–10 frases) y pégala en Claude para corregir."),
             ("Mi trabajo", "# 🩺 Colección «Mi trabajo» completa: de memoria\n- Hoy además: pídeme un lote nuevo de frases de fisio para importarlas."),
             ("Hablar", "# 🗣️ Conversación libre\nPega en Claude: «Discutons 10 minutes de ma vie (études, sport, Barcelone). Niveau A2. Corrige-moi à la fin en espagnol.»"),
             ("Serie", "# 📺 " + serie(n)[0] + ("\n" + serie(n)[1] if serie(n)[1] else "")),
             ("Balance", "# 🎉 Balance de 6 meses\n- Grábate 2 min presentándote y hablando de tu semana. Compáralo con la grabación del primer domingo.\n- Cuéntame qué te cuesta más para ajustar el plan.")]
        return L[wd]
    if r == "DELF A2":
        L = [("Examen A2 · oral", "# DELF A2 de prueba · comprensión oral\n(El bloque de hoy se alarga a ~30 min.) Busca un ejemplo oficial y haz la parte de comprensión oral.\n" + yt("DELF A2 compréhension orale exemple")),
             ("Examen A2 · lectura", "# DELF A2 de prueba · comprensión escrita\n(~30 min) Haz la parte de comprensión escrita de un ejemplo oficial."),
             ("Examen A2 · escritura", "# DELF A2 de prueba · producción escrita\n(~30 min) Haz las dos tareas y pégalas en Claude para que te las puntúe."),
             ("Mi trabajo", "# 🩺 Colección «Mi trabajo» de memoria\n- Pídeme un lote nuevo de frases de fisio de nivel B1."),
             ("Examen A2 · oral", "# DELF A2 de prueba · producción oral\nPega en Claude: «Fais-moi passer l'oral du DELF A2 (entretien dirigé, échange d'informations, dialogue simulé). Note-moi à la fin.»"),
             ("Serie", "# 📺 " + serie(n)[0]),
             ("Balance", "# Balance\n- Mira tus notas del examen de prueba y cuéntame qué reforzar en la fase B1.")]
        return L[wd]
    if r == "DELF B1 C":
        L = [("Examen B1 · oral", "# DELF B1 de prueba · comprensión oral\n(~30 min)\n" + yt("DELF B1 compréhension orale exemple")),
             ("Examen B1 · lectura", "# DELF B1 de prueba · comprensión escrita\n(~35 min)"),
             ("Corrección", "# Corrige las dos comprensiones y anota qué tipo de preguntas fallas."),
             ("Mi trabajo", "# 🩺 Colección «Mi trabajo» completa de memoria"),
             ("Hablar", "# 🗣️ Conversación libre de 15 min con Claude"),
             ("Serie", "# 📺 " + serie(n)[0]),
             ("Repaso", "# Repaso de lo que fallaste en el examen")]
        return L[wd]
    if r == "DELF B1 E":
        L = [("Examen B1 · escritura", "# DELF B1 de prueba · producción escrita\n(~45 min) Texto de opinión de 160 palabras. Pégalo en Claude: «Note ce texte selon la grille du DELF B1 et corrige-le.»"),
             ("Reescribir", "# Reescribe el texto con las correcciones"),
             ("Examen B1 · oral", "# DELF B1 de prueba · producción oral\nPega en Claude: «Fais-moi passer l'oral du DELF B1 (entretien, exercice en interaction, monologue suivi). Note-moi à la fin.»"),
             ("Mi trabajo", "# 🩺 Explica en 2 min tu trabajo de fisio sin mirar nada"),
             ("Hablar", "# 🗣️ Conversación libre de 15 min con Claude sobre tu año"),
             ("Serie", "# 📺 " + serie(n)[0]),
             ("Balance del año 🏁", "# 🏁 Balance del año\n- Grábate 3 min y compáralo con tu primera grabación.\n- Decidimos la fecha del DELF B1 y el plan siguiente.")]
        return L[wd]

def prep_text(d):
    i = PREP.index(d)
    return [
        ("Preparación", "# Prepara HyperLingua\n- Instala HyperLingua y elige francés.\n- Haz tu primer Smart Review y mira la lista de islas."),
        ("Preparación", "# Importa tu colección «Mi trabajo»\n- En My Collections, importa las 60 frases de fisio (preguntas y frases) que te pasé.\n- Busca la serie «Extr@ en français» en YouTube y guárdala.\n" + yt("Extr@ en français épisode 1")),
        ("Primer contacto", "# Primer contacto\n- Smart Review + 20 min con la primera isla."),
        ("Preparación", "# Mañana empieza la semana 1 🇫🇷\n- Smart Review y un repaso rápido de la primera isla."),
    ][i]

program = {}
for d in PREP:
    tag, txt = prep_text(d)
    program[d.isoformat()] = {"tag": f"Semana 0 · {tag}", "text": txt}

for i, w in enumerate(WEEKS):
    n = i + 1
    for wd in range(7):
        d = START + datetime.timedelta(days=7 * i + wd)
        k = d.isoformat()
        tag, txt = day_text(n, w, wd)
        if k in EXAM_DAYS:
            program[k] = {"tag": f"Semana {n} · Día de examen", "text": "# 📚 Día de examen\nHoy solo el Smart Review. Isla y bloque, opcionales (por ejemplo, la isla en bucle en el trayecto).\nPuedes marcarlos como hechos igualmente."}
            continue
        program[k] = {"tag": f"Semana {n} · {level(n)} · {tag}", "text": txt}

fr = {
    "id": "fr",
    "name": "Francés",
    "desc": "45 min cada mañana con HyperLingua · objetivo: B1 (DELF) hacia los 14–16 meses",
    "emoji": "🇫🇷",
    "color": "#3B82F6",
    "type": "checklist",
    "target": 1, "unit": "", "step": 1,
    "steps": [{"id": "fr-sr", "text": "Smart Review · 10 min"},
              {"id": "fr-isla", "text": "Isla de la semana · 20 min"},
              {"id": "fr-bloque", "text": "Bloque del día · 15 min"}],
    "moment": "manana",
    "start": "2026-11-19",
    "archived": False,
    "schedule": {"mode": "daily", "days": [1, 2, 3, 4, 5], "times": 3, "n": 2, "dates": []},
    "plan": {"mode": "none", "weekly": {}, "cycle": ["", ""], "program": program},
}

HABITS = entreno_plan.build() + [fr, ingles_plan.build()] + fisio_plan.build()
# Meta final de cada hábito: hasta dónde llega su plan y qué hay al final
GOALS = {
    "en": {"date": "2027-06-19", "label": "Examen Cambridge B2 First"},
    "fr": {"date": "2027-11-21", "label": "Objetivo B1 (DELF)"},
    "fuerza": {"date": "2027-06-18", "label": "Fin del plan actual de fuerza"},
    "boxeo": {"date": "2027-06-19", "label": "Fin del plan actual de boxeo"},
    "estudio": {"date": "2027-01-14", "label": "Último examen del cuatrimestre"},
    "dx": {"date": "2027-04-18", "label": "Fin de los 20 temas de dx diferencial"},
}
for h in HABITS:
    h["guide"] = guias.GUIDES.get(h["id"], "")
    h["minimal"] = guias.MINIMAL.get(h["id"], "")
    h["metrics"] = guias.METRICS.get(h["id"], [])
    h["goal"] = GOALS.get(h["id"])
pack = {"kind": "ironhabits-plan", "id": "amador", "version": 12, "generated": datetime.date.today().isoformat(), "habits": HABITS, "agenda": agenda_plan.build(HABITS), "agendaUntil": agenda_plan.END.isoformat(), "classesKnownUntil": entreno_plan.CLASSES_KNOWN_UNTIL.isoformat()}
out = os.path.join(os.path.dirname(__file__), "..", "plan.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(pack, f, ensure_ascii=False, separators=(",", ":"))
print("días:", len(program), "primero:", min(program), "último:", max(program), "tamaño KB:", os.path.getsize(out) // 1024)
