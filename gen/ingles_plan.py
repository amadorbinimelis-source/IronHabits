"""Plan de inglés: HyperLingua + preparación del Cambridge B2 First (examen: sábado 19 de junio de 2027)."""
import datetime, urllib.parse

def g(q): return "https://www.google.com/search?q=" + urllib.parse.quote_plus(q)
def yt(q): return "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(q)

START = datetime.date(2026, 11, 23)
PREP = [datetime.date(2026, 11, d) for d in (19, 20, 21, 22)]
EXAM = datetime.date(2027, 6, 19)
MOCK_START = datetime.date(2027, 5, 24)      # fase 3
PARTS_START = datetime.date(2027, 3, 1)      # fase 2
UNI_EXAMS = {"2026-12-15", "2026-12-16", "2026-12-22", "2027-01-12", "2027-01-14"}

TOPICS = ["Travel and holidays", "Work and jobs", "Health and fitness", "Technology",
          "The environment", "Education and studying", "Sport", "Media and social networks",
          "Cities and housing", "Food and eating habits", "Relationships and personality", "Free time and culture",
          "Shopping and money", "Science and medicine"]

UOE = [("Part 1 · Multiple-choice cloze", "8 huecos con 4 opciones: vocabulario, collocations y phrasal verbs."),
       ("Part 2 · Open cloze", "8 huecos sin opciones: palabras gramaticales (preposiciones, artículos, conectores)."),
       ("Part 3 · Word formation", "8 huecos: formar la palabra correcta a partir de una raíz (prefijos y sufijos)."),
       ("Part 4 · Key word transformations", "6 frases: reescribir con una palabra dada, entre 2 y 5 palabras.")]
READ = [("Part 5 · Multiple choice", "Texto largo con 6 preguntas de opción múltiple (opinión, actitud, detalle)."),
        ("Part 6 · Gapped text", "Texto con 6 frases quitadas: colocar cada una en su sitio (cohesión y referencias)."),
        ("Part 7 · Multiple matching", "10 preguntas que emparejar con varios textos cortos (buscar información rápido).")]
LIST = [("Part 1 · Extractos cortos", "8 audios cortos con una pregunta de 3 opciones cada uno."),
        ("Part 2 · Sentence completion", "Un monólogo; completas 10 frases con palabras que oyes."),
        ("Part 3 · Multiple matching", "5 hablantes sobre un tema; emparejas cada uno con una opción."),
        ("Part 4 · Multiple choice", "Una entrevista larga con 7 preguntas de 3 opciones.")]
SPEAK = [("Part 1 · Interview", "Preguntas personales (2 min): estudios, trabajo, aficiones, planes.",
          "Act as a Cambridge B2 First examiner. Do Speaking Part 1 with me: ask me 6 personal questions one by one. After my answers, correct my mistakes in Spanish and suggest more natural B2 expressions."),
         ("Part 2 · Long turn", "Comparar dos fotos durante 1 minuto y responder una pregunta.",
          "Act as a Cambridge B2 First examiner. Do Speaking Part 2: I will compare two photos from my exam book for 1 minute (I'll tell you briefly what they show). Give me a typical Part 2 question for them, let me speak, then ask the follow-up question to the other candidate (me). Give me feedback in Spanish and a model answer."),
         ("Part 3 · Collaborative task", "Conversación de 2 min sobre 5 opciones para tomar una decisión.",
          "Act as my partner in Cambridge B2 First Speaking Part 3. Give me the central question and 5 prompts, then discuss them with me for 2 minutes and help us reach a decision. Afterwards, correct me in Spanish."),
         ("Part 4 · Discussion", "Preguntas de opinión más abiertas relacionadas con la Part 3.",
          "Act as a Cambridge B2 First examiner. Do Speaking Part 4: ask me 4 opinion questions on a general topic. Push me to justify my answers. Then correct me in Spanish and give me useful phrases to give opinions.")]
WRITE = [("Part 1 · Essay", "Essay de 140–190 palabras: das tu opinión sobre un tema con dos ideas dadas y una tuya."),
         ("Part 2 · Email / letter", "Email o carta de 140–190 palabras (formal o informal)."),
         ("Part 1 · Essay", "Essay de 140–190 palabras: das tu opinión sobre un tema con dos ideas dadas y una tuya."),
         ("Part 2 · Article", "Artículo de 140–190 palabras para una revista o web: enganchar al lector."),
         ("Part 1 · Essay", "Essay de 140–190 palabras: das tu opinión sobre un tema con dos ideas dadas y una tuya."),
         ("Part 2 · Review", "Review de 140–190 palabras de un sitio, película, libro, app…"),
         ("Part 1 · Essay", "Essay de 140–190 palabras: das tu opinión sobre un tema con dos ideas dadas y una tuya."),
         ("Part 2 · Report", "Report de 140–190 palabras con apartados y recomendaciones.")]

ART = {"Essay": "an essay", "Email / letter": "an email or letter", "Article": "an article", "Review": "a review", "Report": "a report"}
WRITE_PROMPT = "«Act as a Cambridge B2 First examiner. Give me {task} task about «{topic}». After I write it, mark it with the official B2 First criteria (Content, Communicative Achievement, Organisation, Language), correct my mistakes in Spanish and show me an improved version.»"

WARM = ["describe your own experience with it",
        "compare how it was ten years ago and how it is now",
        "give your opinion: is it getting better or worse? Why?",
        "tell a short story related to it",
        "what would you change about it, and why?"]

def warm(topic, wd):
    q = WARM[wd % len(WARM)]
    return f"🎙️ Calentamiento (5 min): habla 1 minuto en voz alta sin parar, sobre «{topic}»: {q}{"" if q.endswith("?") else "."} Grábate y escúchate.\n\n"

def phase(d):
    if d >= MOCK_START: return 3
    if d >= PARTS_START: return 2
    return 1

def week_index(d):
    return (d - START).days // 7  # 0-based

# ── Recursos exactos ──
def r7(n):  return "https://7esl.com/exams/cambridge/fce/reading/" + ("" if n == 1 else f"?test={n}")
def l7(n):  return "https://7esl.com/exams/cambridge/fce/listening/" + ("" if n == 1 else f"?test={n}")
CAMB = "https://www.cambridgeenglish.org/exams-and-tests/first/preparation/"
WI = "https://writeandimprove.com/"
K1 = [("Fabric Designer", "p972iy0za16"), ("The Art of Forgetting", "p6kbf0aoa16"), ("From Fiction to Reality", "ph7ozkfw516"),
      ("Where to Go Whale Watching", "pfg7evmjt16"), ("What Is a Coincidence?", "pcq5n9srk16"), ("Messages from the Stone Age", "ps8npkoec16"),
      ("Drumming Up Business", "pxws2y9fj16"), ("Multitasking Children", "pxhhk1es216"), ("Working for Navy", "pbo90xhyt16")]
K2 = [("London Marathon", "pnc72zktt16"), ("Learning an Instrument", "ps6qd27g316"), ("Dinosaurs Eating", "p15tszfoa16"),
      ("High Jumper", "p3wku4yot16"), ("Swimming with Seals", "poh2uph2v16"), ("Multimedia Education", "pgv4ea4g516"),
      ("Find the Gorilla", "pp91n8kmj16"), ("The Mini-Monet", "pd8dds6fc16"), ("Diet during Pregnancy", "pt01r7ora16"), ("Postman", "p1geugfzt16")]
def la(code): return "https://learningapps.org/watch?v=" + code
RQ = {1: "1–8", 2: "9–16", 3: "17–24", 4: "25–30", 5: "31–36", 6: "37–42", 7: "43–52"}
RN = {1: "Multiple-choice cloze", 2: "Open cloze", 3: "Word formation", 4: "Key word transformations", 5: "Multiple choice", 6: "Gapped text", 7: "Multiple matching"}
LQ = {1: "1–8", 2: "9–18", 3: "19–23", 4: "24–30"}
LN = {1: "Extractos cortos", 2: "Sentence completion", 3: "Multiple matching", 4: "Multiple choice (entrevista)"}
BOOK = "libro «Cambridge B2 First 4 · Authentic Practice Tests»"

def errores():
    return "\n- Apunta cada fallo en tu nota «Errores inglés»: la frase, la respuesta correcta y por qué."

def text_phase1(d, wd):
    w = week_index(d); n = w + 1; topic = TOPICS[w % len(TOPICS)]
    if wd == 0:
        if n <= 9:
            t1, c1 = K1[n - 1]; t2, c2 = K2[n - 1]
            return ("Use of English", warm(topic, wd) + f"# 📝 Use of English · Parts 1 y 2\n- Part 1 (multiple-choice cloze) · KSE Academy, ejercicio {n} «{t1}»:\n{la(c1)}\n- Part 2 (open cloze) · KSE Academy, ejercicio {n} «{t2}»:\n{la(c2)}\n- Sin prisa: lee el texto entero antes de responder. La app te corrige al final." + errores())
        t = n - 9
        return ("Use of English", warm(topic, wd) + f"# 📝 Use of English · 7ESL Test {t}, Parts 1–4 (preguntas 1–30)\n{r7(t)}\n- Haz solo las Parts 1 a 4. Las Parts 5–7 de este test las harás los martes.\n- Sin cronómetro todavía: céntrate en entender cada fallo." + errores())
    if wd == 1:
        seq = [(t, p) for t in range(1, 6) for p in (5, 6, 7)]
        t, p = seq[w]
        return ("Reading", warm(topic, wd) + f"# 📖 Reading · 7ESL Test {t}, Part {p} ({RN[p]}, preguntas {RQ[p]})\n{r7(t)}\n- Ve directo a la Part {p}. Léela sin diccionario y responde.\n- Después corrige y busca en el texto la frase que justifica cada respuesta.\n- 5 palabras nuevas a My Collections de HyperLingua." + errores())
    if wd == 2:
        name, desc = WRITE[w % len(WRITE)]
        return ("Writing", warm(topic, wd) + f"# ✍️ Writing · {name}\n{desc}\n1) Pega en Claude:\n" + WRITE_PROMPT.format(task=ART[name.split(' · ')[1]], topic=topic) + f"\n2) Escríbelo en 25 min, sin traductor.\n3) Pégalo también en Write & Improve para ver tu nivel CEFR:\n{WI}\n4) Pasa las correcciones a tu nota «Errores inglés».")
    if wd == 3:
        seq = [(t, p) for t in range(1, 5) for p in (1, 2, 3, 4)]
        t, p = seq[w]
        return ("Listening", warm(topic, wd) + f"# 🎧 Listening · 7ESL Test {t}, Part {p} ({LN[p]}, preguntas {LQ[p]})\n{l7(t)}\n- Escucha dos veces, como en el examen.\n- Corrige y vuelve a escuchar lo que fallaste.\n- 3 expresiones nuevas a My Collections." + errores())
    if wd == 4:
        name, desc, prompt = SPEAK[w % 4]
        extra = f"\n- Fotos: usa las del Speaking Part 2 del {BOOK}, Test {(w // 4) % 4 + 1}. Describe y compara en voz alta 1 minuto con el cronómetro y luego díselo a Claude." if "Part 2" in name else ""
        return ("Speaking", f"# 🗣️ Speaking · {name}\n{desc}\nAbre Claude en modo voz y pega:\n«{prompt}»\n- Tema de la semana: {topic}." + extra)
    if wd == 5:
        return ("Speaking + vocabulario", f"# 🗣️ Conversación de 20 min · {topic}\nAbre Claude en modo voz y pega:\n«Let's have a 20-minute conversation about «{topic}». During the conversation, teach me 10 useful B2 collocations and phrasal verbs on this topic and make me use them. At the end, correct my mistakes in Spanish and list the 10 expressions.»\n- Importa las 10 expresiones en My Collections.\n- Esta noche: Dexter en VO 📺")
    if wd == 6:
        return ("Speaking + repaso", "# 🗣️ Cuéntame tu semana (5 min)\nAbre Claude en modo voz y pega:\n«Ask me about my week in English, like a friend. Keep it natural for 5 minutes, then correct my mistakes in Spanish.»\n\n# 🔁 Repaso de errores (15 min)\n- Abre tu nota «Errores inglés» y tápate las respuestas de esta semana: intenta acertarlas.\n- Las que vuelvas a fallar, márcalas con ⭐.")

def p2_source(w):
    """Fuente de cada semana de la fase 2 (w = índice de semana, 14..25)."""
    k = w - 14
    if k <= 4:  return ("7esl", k + 6)          # 7ESL tests 6–10
    if k == 5:  return ("book", 4)               # libro Test 4
    if k == 6:  return ("camb", 1)               # Sample paper 1
    if k == 7:  return ("camb", 2)               # Sample paper 2
    return ("redo", k - 7)                        # rehacer 7ESL tests 1–4

def src_label(src):
    kind, n = src
    if kind == "7esl": return f"7ESL Test {n}", r7(n)
    if kind == "book": return f"{BOOK}, Test {n}", None
    if kind == "camb": return f"Cambridge · Sample paper {n} (gratis, en la página oficial)", CAMB
    return f"7ESL Test {n} (lo rehaces: ya no te acordarás)", r7(n)

def text_phase2(d, wd):
    w = week_index(d); topic = TOPICS[w % len(TOPICS)]
    src = p2_source(w); lab, url = src_label(src)
    link = f"\n{url}" if url else ""
    if wd == 0:
        return ("Use of English", warm(topic, wd) + f"# 📝 {lab} · Reading & Use of English, Parts 1–4 (preguntas 1–30)\n- Con cronómetro: 25 min.{link}\n- Corrige y apunta cada fallo por tipo (vocabulario, gramática, formación de palabras)." + errores())
    if wd == 1:
        return ("Reading", warm(topic, wd) + f"# 📖 {lab} · Parts 5–7 (preguntas 31–52)\n- Con cronómetro: 45 min (hoy el bloque se alarga).{link}\n- Corrige buscando en el texto la frase que justifica cada respuesta." + errores())
    if wd == 2:
        if src[0] in ("book", "camb"):
            task = f"# ✍️ Writing · Part 1 (essay) del {lab}\n- 40 min, como en el examen.{link}"
        else:
            name = WRITE[w % len(WRITE)][0]
            task = f"# ✍️ Writing · {name} · 40 min\nPega en Claude:\n" + WRITE_PROMPT.format(task=ART[name.split(' · ')[1]], topic=topic)
        return ("Writing", warm(topic, wd) + task + f"\n- Al acabar: pégalo en Write & Improve ({WI}) y en Claude para que lo puntúe con los criterios oficiales.\n- Pasa las correcciones a «Errores inglés».")
    if wd == 3:
        kind, n = src
        if kind == "7esl": lt, lurl = f"7ESL Listening Test {n - 1}", l7(n - 1)
        elif kind == "book": lt, lurl = f"{BOOK}, Test 4 · Listening", None
        elif kind == "camb": lt, lurl = ("Cambridge · Digital Listening Sample Test" if n == 1 else "7ESL Listening Test 4 (completo)"), (CAMB if n == 1 else l7(4))
        else: lt, lurl = f"7ESL Listening Test {n} (lo rehaces completo)", l7(n)
        return ("Listening", warm(topic, wd) + f"# 🎧 {lt} · las 4 partes (preguntas 1–30)\n- Unos 40 min, cada audio dos veces." + (f"\n{lurl}" if lurl else "") + "\n- Corrige y vuelve a escuchar los fallos." + errores())
    if wd == 4:
        name, desc, prompt = SPEAK[w % 4]
        extra = f"\n- Fotos: Speaking Part 2 del {BOOK}, Test {(w // 4) % 4 + 1}." if "Part 2" in name else ""
        return ("Speaking", f"# 🗣️ Speaking · {name}\nAbre Claude en modo voz y pega:\n«{prompt}»\n- Después, pídele que te haga también la parte siguiente." + extra)
    if wd in (5, 6):
        return text_phase1(d, wd)

def text_phase3(d, wd):
    if d >= datetime.date(2027, 6, 14):
        L = {14: ("Repaso final", "# Repaso final · Use of English\n- Repasa tu lista de errores típicos. Nada de tests largos."),
             15: ("Repaso final", "# Repaso final · Writing\n- Relee tus mejores writings corregidos y las estructuras útiles."),
             16: ("Repaso final", "# Speaking suave\n- 10 min de Part 1 y Part 2 con Claude."),
             17: ("Repaso final", "# Logística\n- Revisa la hora y el centro del examen, el DNI y la confirmación (COE).\n- Repaso ligero de vocabulario."),
             18: ("Descanso", "# Mañana es el examen 💪\n- Solo Smart Review. Duerme bien.")}
        return L.get(d.day, ("Repaso", "# Repaso ligero"))
    mock = (d - MOCK_START).days // 7 + 1
    L = [("Simulacro · Reading & UoE", f"# 🧪 Simulacro {mock} · {BOOK}, Test {mock} · Reading & Use of English\n- Las 7 partes seguidas, cronometrado: 1 h 15 (hoy el bloque se alarga).\n- Corrige con las respuestas del final del libro."),
         ("Simulacro · Writing", f"# 🧪 Simulacro {mock} · {BOOK}, Test {mock} · Writing\n- Part 1 (essay) + una tarea de Part 2, en 1 h 20.\n- Pégalos en Claude para que los puntúe con los criterios oficiales."),
         ("Simulacro · Listening", f"# 🧪 Simulacro {mock} · {BOOK}, Test {mock} · Listening\n- Las 4 partes con el audio del libro, unos 40 min."),
         ("Simulacro · Speaking", f"# 🧪 Simulacro · Speaking completo con Claude\n- Ten delante las fotos del Speaking del {BOOK}, Test {mock}.\nPega en Claude:\n«Act as a Cambridge B2 First examiner and give me a full Speaking test (Parts 1 to 4) as realistically as possible. For Part 2 I will describe the two photos from my book. Then give me a band score for each criterion and feedback in Spanish.»"),
         ("Corrección", "# Corrige el simulacro\n- Apunta tus errores típicos en una lista. Es lo que repasarás la última semana."),
         ("Vocabulario", "# Vocabulario: tus fallos\n- Repasa en My Collections todo lo que has ido apuntando."),
         ("Descanso", "# Descanso del bloque B2\n- Solo Smart Review e isla.")]
    return L[wd]

def build():
    program = {}
    prep = [
        ("Prepara el kit", "# 🧰 Prepara tu kit de inglés\n- Abre la guía del hábito (botón ⋯ de Inglés › Progreso, guía y plan completo › 📘 Guía) y consigue todo lo que pone.\n- Hoy: añade inglés (UK) en HyperLingua y crea tu cuenta gratis en 7ESL.\n- Pide el libro «Cambridge B2 First 4 · Authentic Practice Tests» (con respuestas y audio)."),
        ("Prepara el kit", f"# 🧰 Guarda tus enlaces\n- Página oficial de preparación de Cambridge (sample papers 1 y 2):\n{CAMB}\n- Write & Improve:\n{WI}\n- Crea en el móvil una nota llamada «Errores inglés»."),
        ("Nivel de partida", f"# 🎯 ¿De dónde partes?\n- Haz el Reading & Use of English del 7ESL Test 1 sin cronómetro, para ver tu nivel real:\n{r7(1)}\n- Apunta tu nota: la compararemos en marzo."),
        ("Primer día", "# Mañana empezamos 🇬🇧\n- Smart Review y primera isla en inglés.\n- Mira cómo será la semana 1 en la app."),
    ]
    for i, d in enumerate(PREP):
        program[d.isoformat()] = {"tag": f"Semana 0 · {prep[i][0]}", "text": prep[i][1]}
    d = START
    while d <= EXAM:
        k = d.isoformat(); wd = d.weekday()
        n = week_index(d) + 1
        if d == EXAM:
            program[k] = {"tag": "🎯 Día del examen B2 First", "text": "# 🎯 Hoy es el B2 First\n- Desayuna bien, llega con tiempo y lleva el DNI.\n- Tú puedes. 💪"}
        elif k in UNI_EXAMS:
            program[k] = {"tag": f"Semana {n} · Día de examen de la uni", "text": "# 📚 Día de examen\nHoy solo el Smart Review. El resto, opcional."}
        else:
            ph = phase(d)
            tag, txt = (text_phase1 if ph == 1 else text_phase2 if ph == 2 else text_phase3)(d, wd)
            lab = {1: "Base", 2: "Examen por partes", 3: "Simulacros"}[ph]
            program[k] = {"tag": f"Semana {n} · {lab} · {tag}", "text": txt}
        d += datetime.timedelta(days=1)
    # recordatorio de matrícula (se añade al texto de ese día)
    for k, msg in (("2027-04-12", "⚠️ Matricúlate esta semana en el B2 First del sábado 19 de junio (British Council, Exams Catalunya u otro centro de Barcelona). Antes, comprueba que no coincide con la defensa del TFG."),
                   ("2027-05-03", "⚠️ ¿Ya estás matriculado en el B2 First? Si no, hazlo hoy: los plazos cierran unas semanas antes.")):
        program[k]["text"] = msg + "\n\n" + program[k]["text"]
    return {
        "id": "en", "name": "Inglés", "emoji": "🇬🇧", "color": "#14B8A6",
        "desc": "45 min cada mañana después del francés · objetivo: Cambridge B2 First el 19 de junio de 2027",
        "type": "checklist", "target": 1, "unit": "", "step": 1,
        "steps": [{"id": "en-sr", "text": "Smart Review · 10 min"},
                  {"id": "en-isla", "text": "Isla · 10 min"},
                  {"id": "en-b2", "text": "Bloque B2 · 25 min"}],
        "moment": "manana", "start": "2026-11-19", "archived": False,
        "schedule": {"mode": "dates", "days": [1, 2, 3, 4, 5], "times": 3, "n": 2, "dates": sorted(program)},
        "plan": {"mode": "none", "weekly": {}, "cycle": ["", ""], "program": program},
    }
