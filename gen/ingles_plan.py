"""Plan de inglés para el Cambridge B2 First (sábado 19 de junio de 2027) con meta 180 (nota A → certificado C1).

v14 (25 nov 2026), ajustado a su nivel real de noviembre: Reading & UoE 34/52 (~165), Listening 21/30 (~170, Part 2 floja: 2/10),
Writing 13/20 (~160, sin opinión ni conclusión). Cambios: controles 170/175/180; Listening Part 2 lunes y viernes en las
semanas 2–4; traducción inversa semanal de un texto modelo (martes → jueves) en las fases 1–2; plan de 5 min en cada writing.

Ritmo: L–V 75 min (Smart Review 10 + isla 10 + bloque B2 55), sábado 60 (10 + 50), domingo 40 (10 + 30).
Cada día lleva «blocks»: bloques con minutos, cómo hacerlo y UNA acción (abrir enlace exacto, copiar la línea para Claude…).
Cada herramienta hace solo lo suyo (no se repiten funciones en IronHabits):
  HyperLingua → vocabulario, repaso espaciado y colección «Errores» · 7ESL / libro / Cambridge → tests y su corrección
  British Council LearnEnglish → lecciones de gramática · Proyecto de Claude «Inglés B2» → corrección, speaking y explicaciones
  IronHabits → qué toca y cuándo, el botón exacto, cronómetro, material, notas y horas.
Todos los enlaces están comprobados (lista en LINKS; las pruebas los revisan en cada publicación)."""
import datetime

START = datetime.date(2026, 11, 23)                  # lunes de la semana 1
PREP = [datetime.date(2026, 11, d) for d in (19, 20, 21, 22)]
EXAM = datetime.date(2027, 6, 19)
UNI_EXAMS = {"2026-12-15", "2026-12-16", "2026-12-22", "2027-01-12", "2027-01-14"}
PHASES = [  # (nombre, primera semana, última semana, objetivo)
    ("Repaso de bachillerato", 1, 10, "Recuperar la base: gramática B1–B2, técnica de cada parte y primeros writings"),
    ("Nivel B2+ hacia C1", 11, 18, "Gramática avanzada, word formation y los 5 tipos de writing"),
    ("Examen por partes, cronometrado", 19, 26, "Tiempo real de examen y las partes flojas"),
    ("Simulacros", 27, 30, "Tres exámenes completos y semana final suave"),
]
CONTROLS = {"2027-01-23": ("Control 1", 170), "2027-03-27": ("Control 2", 175), "2027-05-15": ("Control 3", 180)}
GOAL = 180
LP2 = {2: (10, 9), 3: (8, 7), 4: (6, 1)}   # semana → tests de 7ESL cuya Listening Part 2 se hace el lunes y el viernes (el 1 = repetir el del test de nivel)

TOPICS = ["Travel and holidays", "Work and jobs", "Health and fitness", "Technology", "The environment",
          "Education and studying", "Sport", "Media and social networks", "Cities and housing", "Food and eating habits",
          "Relationships and personality", "Free time and culture", "Shopping and money", "Science and medicine"]

# ── Enlaces (comprobados) ──
def r7(n): return "https://7esl.com/exams/cambridge/fce/reading/" + ("" if n == 1 else f"?test={n}")
def l7(n): return "https://7esl.com/exams/cambridge/fce/listening/" + ("" if n == 1 else f"?test={n}")
def w7(n): return "https://7esl.com/exams/cambridge/fce/writing/" + ("" if n == 1 else f"?test={n}")
def la(code): return "https://learningapps.org/watch?v=" + code
BC = "https://learnenglish.britishcouncil.org/free-resources/grammar/"
CAMB = "https://www.cambridgeenglish.org/exams-and-tests/first/preparation/"
HANDBOOK = "https://www.cambridgeenglish.org/images/167791-b2-first-handbook.pdf"
CHECKLIST = "https://www.cambridgeenglish.org/Images/630454-checklist-to-improve-your-writing-b2-first-and-b2-first-for-schools.pdf"
WI = "https://writeandimprove.com/"
BBC6 = "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english"
SEVEN = "https://7esl.com/exams/cambridge/fce/"
BOOK = "libro «B2 First 6»"

K1 = [("Fabric Designer", "p972iy0za16"), ("The Art of Forgetting", "p6kbf0aoa16"), ("From Fiction to Reality", "ph7ozkfw516"),
      ("Where to Go Whale Watching", "pfg7evmjt16"), ("What Is a Coincidence?", "pcq5n9srk16"), ("Messages from the Stone Age", "ps8npkoec16"),
      ("Drumming Up Business", "pxws2y9fj16"), ("Multitasking Children", "pxhhk1es216"), ("Working for Navy", "pbo90xhyt16")]
K2 = [("London Marathon", "pnc72zktt16"), ("Learning an Instrument", "ps6qd27g316"), ("Dinosaurs Eating", "p15tszfoa16"),
      ("High Jumper", "p3wku4yot16"), ("Swimming with Seals", "poh2uph2v16"), ("Multimedia Education", "pgv4ea4g516"),
      ("Find the Gorilla", "pp91n8kmj16"), ("The Mini-Monet", "pd8dds6fc16"), ("Diet during Pregnancy", "pt01r7ora16")]

# Gramática: (título, ruta en LearnEnglish). Lunes = G1, viernes = G2. Semanas 1–10 repaso B1–B2; 11–18 B2+ y C1.
GRAMMAR = {
    1: (("Present perfect", "b1-b2/present-perfect"), ("Present perfect simple and continuous", "b1-b2/present-perfect-simple-continuous")),
    2: (("Past perfect", "b1-b2/past-perfect"), ("Past habits: used to, would and past simple", "b1-b2-grammar/past-habits-used-to-would-past-simple")),
    3: (("Future forms: will, be going to, present continuous", "b1-b2/future-forms-will-be-going-present-continuous"), ("Future continuous and future perfect", "b1-b2/future-continuous-future-perfect")),
    4: (("Conditionals: zero, first and second", "b1-b2/conditionals-zero-first-second"), ("Conditionals: third and mixed", "b1-b2/conditionals-third-mixed")),
    5: (("Wishes: wish and if only", "b1-b2/wishes-wish-if-only"), ("Passives", "b1-b2/passives")),
    6: (("Reported speech: statements", "b1-b2/reported-speech-statements"), ("Reported speech: questions", "b1-b2/reported-speech-questions")),
    7: (("Reported speech: reporting verbs", "b1-b2/reported-speech-reporting-verbs"), ("Relative clauses: defining", "b1-b2/relative-clauses-defining-relative-clauses")),
    8: (("Relative clauses: non-defining", "b1-b2/relative-clauses-non-defining-relative-clauses"), ("Modals: permission and obligation", "b1-b2/modals-permission-obligation")),
    9: (("Modals: deductions about the present", "b1-b2/modals-deductions-about-present"), ("Modals: deductions about the past", "b1-b2/modals-deductions-about-past")),
    10: (("Verbs + -ing or infinitive (change of meaning)", "b1-b2/verbs-followed-ing-or-infinitive-change-meaning"), ("Phrasal verbs", "b1-b2/phrasal-verbs")),
    11: (("Contrasting ideas: although, despite…", "b1-b2/contrasting-ideas-although-despite-others"), ("Intensifiers: so and such", "b1-b2/intensifiers-so-such")),
    12: (("Modifying comparatives", "b1-b2/modifying-comparatives"), ("Using enough", "b1-b2/using-enough")),
    13: (("Verbs and prepositions", "b1-b2/verbs-prepositions"), ("Stative verbs", "b1-b2/stative-verbs")),
    14: (("The future: degrees of certainty", "b1-b2/future-degrees-certainty"), ("Different uses of used to", "b1-b2-grammar/different-uses-of-used-to")),
    15: (("C1 · Inversion after negative adverbials", "c1/inversion-after-negative-adverbials"), ("C1 · Inversion and conditionals", "c1/inversion-conditionals")),
    16: (("C1 · Emphasis: cleft sentences, inversion, auxiliaries", "c1/emphasis-cleft-sentences-inversion-auxiliaries"), ("C1 · Participle clauses", "c1/participle-clauses")),
    17: (("C1 · Advanced passives review", "c1/advanced-passives-review"), ("C1 · Unreal time", "c1/unreal-time")),
    18: (("C1 · Patterns with reporting verbs", "c1/patterns-reporting-verbs"), ("C1 · Modals: probability", "c1/modals-probability")),
}
WRITE_TYPES = ["Essay", "Email / letter", "Article", "Essay", "Review", "Report"]

# ── Material (lo que hay que tener; la fecha en que se necesita la calcula build() a partir del primer uso) ──
CLAUDE_PROJECT = """Eres mi profesor y examinador de Cambridge B2 First (FCE). Mi lengua es el español. Me examino el sábado 19 de junio de 2027 y mi objetivo es 180 en la escala de Cambridge (nota A, certificado C1). Nivel de partida (noviembre 2026): Reading & Use of English 34/52, Listening 21/30 (Part 2 floja: escribo de más y fallo la ortografía), Writing 13/20 (no doy mi opinión ni cierro con conclusión; calcos del español). Mis puntos flojos: writing, vocabulario y Listening Part 2.

Reglas siempre:
- Explicaciones y correcciones en español; el inglés que me enseñes, natural y de nivel B2–C1.
- Corrige TODO error, también los pequeños, y señala los típicos de hispanohablantes.
- Sé exigente: puntúa como un examinador real, no me regales nota.
- Respuestas cortas y ordenadas.

Te escribiré una de estas órdenes (a veces con el tema de la semana):
WRITING TAREA · tipo · tema → dame una tarea realista de B2 First de ese tipo (140–190 palabras), sin modelo.
CORRIGE → (pego mi writing) puntúalo 0–5 en Content, Communicative Achievement, Organisation y Language con una frase de por qué; lista de errores (mi frase → corrección → por qué); versión mejorada manteniendo mis ideas; 5 expresiones B2+ que debería haber usado. Al final: «Frases para HyperLingua»: mis frases corregidas, una por línea, sin numerar.
REESCRIBIR → (pego mi versión reescrita) dime si he corregido bien los errores y la nota nueva.
SPEAKING P1 / P2 / P3 / P4 · tema → hazme esa parte del Speaking como examinador, una pregunta cada vez y espera mi respuesta. En P2 yo describo dos fotos de mi móvil o del libro: dame la pregunta típica. Al final, nota 0–5 (Grammar & Vocabulary, Discourse Management, Pronunciation, Interactive Communication) y mis 5 errores principales.
SPEAKING COMPLETO → las 4 partes seguidas, como el examen real, y nota final.
CONVERSACIÓN · tema → charla natural de 20 minutos; enséñame 10 collocations o phrasal verbs del tema y oblígame a usarlas; al final corrige mis errores.
MODELO · tipo · tema → escribe un texto modelo de nota máxima (B2 First, 170–190 palabras) de ese tipo y tema: opinión clara, un párrafo por idea (idea → por qué → ejemplo) y conclusión. Debajo, en 5 líneas, las estructuras y collocations que le dan la nota. Nada más.
COMPARA → (pego mi traducción inversa) compárala con el modelo original: lista de diferencias (mi frase → la del modelo → por qué suena mejor) y las 8 «Frases para HyperLingua» que más me conviene aprender.
WORD FORMATION · tema → 15 frases tipo Part 3 (palabra en mayúsculas para transformar), y después las soluciones con la regla.
TRANSFORMATIONS → 10 frases tipo Part 4 con la solución y la regla de cada una.
VOCAB SEMANA · tema → 40 frases de ejemplo en inglés con collocations, phrasal verbs y familias de palabras B2+ del tema. Formato: una frase por línea, sin numerar, sin traducción, listas para importar en HyperLingua.
EXPLICA → (pego un fallo de un test) explícame por qué es la respuesta correcta y la regla, en 5 líneas.
REPASO GRAMÁTICA → 12 frases para corregir con los errores de gramática que más he cometido en esta conversación del proyecto."""

KIT = [
    {"id": "book", "icon": "📕", "what": "Comprar", "name": "B2 First 6 · Practice Tests with Answers (versión digital oficial)",
     "why": "4 exámenes oficiales completos, con audio, respuestas y fotos del Speaking. Es tu material para el control 3 y los 3 simulacros.",
     "how": "Cómpralo en digital (Digital Pack de Cambridge) o en papel con audio. Si no está, vale «B2 First 5». No hagas sus tests antes de tiempo.",
     "url": "https://www.cambridge.org/gb/cambridgeenglish/official-exam-preparation-materials/exam/b2-first"},
    {"id": "hl", "icon": "🦜", "what": "Configurar", "name": "HyperLingua · inglés (UK) y 2 colecciones",
     "why": "Tu repaso diario. Todo el vocabulario y tus errores acaban aquí y se repasan solos en el Smart Review.",
     "how": "Añade inglés UK. Crea en My Collections «Vocabulario B2» y «Errores»."},
    {"id": "claude", "icon": "🤖", "what": "Configurar", "name": "Proyecto de Claude «Inglés B2»",
     "why": "Tu profesor: corrige writings, hace el Speaking por voz, te explica fallos y te prepara el vocabulario. Con el proyecto, cada orden de la app es una línea.",
     "how": "En Claude: Proyectos › Nuevo › «Inglés B2». Pega estas instrucciones (botón Copiar) y sube el PDF del handbook de Cambridge.",
     "copy": CLAUDE_PROJECT},
    {"id": "7esl", "icon": "📝", "what": "Crear cuenta", "name": "7ESL · cuenta gratis",
     "why": "10 exámenes B2 First gratis con corrección automática (Reading & Use of English, Listening, Writing con modelos).",
     "how": "El Test 1 va sin cuenta; del 2 al 10 necesitas la cuenta gratis.", "url": SEVEN},
    {"id": "camb", "icon": "🏛️", "what": "Descargar", "name": "Cambridge · 2 exámenes de muestra + respuestas + audio",
     "why": "El formato real oficial. Los usas en el control 2 y en la fase 3.",
     "how": "En la página oficial, descarga «Sample test 1» y «Sample test 2» (con sus respuestas y audio) y guárdalos en una carpeta.", "url": CAMB},
    {"id": "handbook", "icon": "📘", "what": "Descargar", "name": "Handbook oficial del B2 First (PDF)",
     "why": "Criterios de corrección y modelos de writing. Lo subes al proyecto de Claude.", "how": "Descárgalo y súbelo al proyecto «Inglés B2».", "url": HANDBOOK},
    {"id": "checklist", "icon": "✅", "what": "Descargar", "name": "Checklist oficial de Writing (PDF)",
     "why": "Lo revisas antes de entregar cada writing (1 minuto).", "how": "Descárgalo y guárdalo en Archivos.", "url": CHECKLIST},
    {"id": "wi", "icon": "🖊️", "what": "Crear cuenta", "name": "Write & Improve · cuenta gratis",
     "why": "Segunda opinión automática de tu nivel de writing (CEFR) en las semanas de control.", "how": "Crea la cuenta gratis.", "url": WI},
    {"id": "bbc", "icon": "🎧", "what": "Suscribirte", "name": "Podcast «6 Minute English» (BBC)",
     "why": "Listening extra de los sábados: 6 minutos con transcripción y vocabulario.", "how": "Suscríbete en la app Podcasts del iPhone.", "url": BBC6},
    {"id": "notes", "icon": "🗒️", "what": "Configurar", "name": "Nota «Writings» en el móvil",
     "why": "Donde escribes los writings con el cronómetro de IronHabits (luego los pegas en Claude).", "how": "Crea una nota «Writings» en Notas."},
    {"id": "partner", "icon": "🤝", "what": "Buscar", "name": "Compañero de Speaking (1 vez al mes)",
     "why": "El Speaking real es en pareja: practicar con una persona una vez al mes desde marzo.",
     "how": "Un compañero de clase que también se presente o un intercambio de idiomas (app Tandem)."},
    {"id": "exam", "icon": "🎯", "what": "Pagar", "name": "Matrícula del B2 First del 19 de junio",
     "why": "Sin matrícula no hay examen; el plazo suele cerrar a principios de mayo.",
     "how": "Elige centro en Barcelona (British Council, Exams Catalunya…). Unos 220 €. Revisa en el COE el día del Speaking."},
]

# ── Bloques ──
def A(kind, label, url=None, copy=None, kit=None):
    a = {"k": kind, "l": label}
    if url: a["u"] = url
    if copy: a["c"] = copy
    if kit: a["kit"] = kit
    return a
def B(icon, title, mins, how, act=None, kit=None):
    b = {"i": icon, "t": title, "m": mins, "d": how}
    if act: b["a"] = act
    if kit: b["kit"] = kit
    return b
def url(label, u, kit=None): return A("url", label, url=u, kit=kit)
def claude(line, kit="claude"): return A("claude", "Copiar y abrir Claude", copy=line, kit=kit)
def book(label): return A("book", label, kit="book")
def note(label, kit=None): return A("note", label, kit=kit)

ERR = "Lo que falles: «EXPLICA» en Claude si no lo entiendes, y la frase correcta a tu colección «Errores» de HyperLingua."

def week_of(d): return (d - START).days // 7 + 1

def grammar_block(w, which):
    g = GRAMMAR.get(w)
    if not g: return None
    t, path = g[which]
    return B("📘", f"Gramática · {t}", 20, ["Haz el test del principio, lee la explicación y el test final.", "Copia 3 frases de ejemplo a «Errores» si te costaron."],
             url("Abrir la lección", BC + path))

def uoe_block(w, mins):
    if w <= 9:
        t1, c1 = K1[w - 1]; t2, c2 = K2[w - 1]
        return [B("📝", f"Use of English · Part 1 «{t1}»", mins // 2, ["Lee el texto entero antes de elegir.", ERR], url("Abrir el ejercicio", la(c1))),
                B("📝", f"Use of English · Part 2 «{t2}»", mins - mins // 2, ["Una sola palabra por hueco.", ERR], url("Abrir el ejercicio", la(c2)))]
    tests = {10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 8, 16: 9}
    if w in tests:
        n = tests[w]
        return [B("📝", f"Use of English · 7ESL Test {n}, Parts 1–4", mins, ["Solo las preguntas 1–30.", "Sin cronómetro: entiende cada fallo.", ERR], url(f"Abrir Test {n}", r7(n), "7esl"))]
    return [B("🔧", "Key word transformations (Part 4)", mins, ["Haz las 10 frases y corrige con la solución.", ERR], claude("TRANSFORMATIONS"))]

def reading_block(w):
    seq = {1: (2, "5"), 2: (2, "6"), 3: (2, "7"), 4: (3, "5"), 5: (3, "6"), 6: (3, "7"), 7: (4, "5"), 8: (4, "6"), 9: (4, "7"), 10: (5, "5"),
           11: (5, "6 y 7"), 12: (7, "5–7"), 13: (8, "5–7"), 14: (9, "5–7"), 15: (2, "5–7"), 16: (3, "5–7"), 17: (4, "5–7"), 18: (5, "5–7")}
    n, p = seq[w]
    redo = " (lo repites: ya no te acordarás)" if w >= 15 else ""
    return [B("📖", f"Reading · 7ESL Test {n}, Part {p}{redo}", 40, ["Ve directo a esa parte. Sin diccionario.", "Al corregir, busca en el texto la frase que justifica cada respuesta.", ERR], url(f"Abrir Test {n}", r7(n), "7esl")),
            B("🔤", "Vocabulario del texto", 15, ["Las 8 expresiones que no conocías del texto, a «Vocabulario B2» de HyperLingua (copia la frase entera)."], note("HyperLingua › Vocabulario B2", "hl"))]

def listening_block(w):
    seq = {1: (2, "1"), 2: (2, "2"), 3: (2, "3"), 4: (2, "4"), 5: (3, "1"), 6: (3, "2"), 7: (3, "3"), 8: (3, "4"), 9: (4, "1 y 2"), 10: (4, "3 y 4"),
           11: (5, "1–4"), 12: (6, "1–4"), 13: (7, "1–4"), 14: (8, "1–4"), 15: (9, "1–4"), 16: (2, "1–4"), 17: (3, "1–4"), 18: (4, "1–4")}
    n, p = seq[w]
    return B("🎧", f"Listening · 7ESL Test {n}, Part {p}", 35, ["Cada audio dos veces, como en el examen.", "Corrige y vuelve a escuchar solo lo que fallaste.", ERR], url(f"Abrir Listening {n}", l7(n), "7esl"))

def writing_block(w, topic, mins_write):
    wtype = WRITE_TYPES[(w - 1) % len(WRITE_TYPES)]
    part = "Part 1" if wtype == "Essay" else "Part 2"
    return [B("✍️", f"Writing · {wtype} ({part})", 5, ["Pide la tarea y planifica 5 min antes de escribir:", "tu opinión en una frase · un párrafo por idea (idea → por qué → ejemplo) · conclusión con tu opinión."], claude(f"WRITING TAREA · {wtype} · {topic}")),
            B("✍️", f"Escríbelo · {mins_write} min", mins_write, ["En tu nota «Writings», sin traductor.", "140–190 palabras. Antes de acabar, pasa el checklist oficial."], note("Notas › Writings", "notes")),
            B("🔍", "Corrígelo con Claude", 55 - 5 - mins_write, ["Pega tu texto después de la orden.", "Las «Frases para HyperLingua» que te da, a tu colección «Errores»."], claude("CORRIGE"))]

def lp2_block(w, which):
    n = LP2[w][which]
    how = ["Lee las 10 frases antes de escuchar y piensa qué tipo de palabra falta.", "Escribe solo la palabra clave (1–3 palabras) y revisa la ortografía.", ERR]
    if n == 1: how.insert(0, "Es el de tu test de nivel (2/10): compara cuántas sacas ahora.")
    return B("🎧", f"Listening Part 2 · 7ESL Test {n}", 15, how, url(f"Abrir Listening {n}", l7(n), "7esl"))

def inverse_blocks(w, topic, step):
    wtype = WRITE_TYPES[(w - 1) % len(WRITE_TYPES)]
    if step == 1:
        return B("🔁", "Traducción inversa · 1/2 (modelo → español)", 10, ["Pide el modelo y tradúcelo al español en tu nota «Writings».", "No lo relees hasta el jueves."], claude(f"MODELO · {wtype} · {topic}"))
    return B("🔁", "Traducción inversa · 2/2 (español → inglés)", 10, ["Sin mirar el modelo, pasa tu traducción del martes al inglés.", "Pégala tras la orden: las diferencias son lo que aún piensas en español."], claude("COMPARA"))

def speaking_block(w, topic, mins):
    p = ["P1", "P2", "P3", "P4"][(w - 1) % 4]
    extra = ["Usa el modo voz de Claude."]
    if p == "P2": extra.append("Fotos: " + ("dos fotos de tu móvil relacionadas con el tema." if w < 11 else f"las del Speaking Part 2 del {BOOK}, Test {(w // 4) % 4 + 1}."))
    return B("🗣️", f"Speaking · {p}", mins, extra, claude(f"SPEAKING {p} · {topic}"), kit="book" if p == "P2" and w >= 11 else None)

def day_blocks(d, w, wd):
    """Bloques del inglés (después del Smart Review y la isla). Devuelve (tag, blocks, marca)."""
    k = d.isoformat(); topic = TOPICS[(w - 1) % len(TOPICS)]
    if k in UNI_EXAMS:
        return "Día de examen de la uni", [B("📚", "Hoy solo el Smart Review", 0, ["El resto, opcional."])], "light"
    if k in CONTROLS:
        name, goal = CONTROLS[k]
        src = {"Control 1": ("7ESL Test 6 · Reading & Use of English completo", r7(6), "7esl"),
               "Control 2": ("Cambridge · Sample test 1 · Reading & Use of English", CAMB, "camb"),
               "Control 3": (f"{BOOK}, Test 4 · Reading & Use of English", None, "book")}[name]
        a = url("Abrir el test", src[1], src[2]) if src[1] else book(f"{BOOK} · Test 4")
        return f"📍 {name} · meta {goal}", [B("📍", src[0], 75, ["Las 7 partes seguidas, con cronómetro (1 h 15).", "Al acabar, apunta tus aciertos en 📊 Notas: la app te dice si vas en meta."], a, kit=src[2]),
                                           B("✍️", "Segunda opinión del writing", 5, ["Pega tu último writing en Write & Improve y mira el nivel CEFR."], url("Abrir Write & Improve", WI, "wi"))], "control"
    if k in {(datetime.date.fromisoformat(c) + datetime.timedelta(days=1)).isoformat() for c in CONTROLS}:
        name = CONTROLS[(d - datetime.timedelta(days=1)).isoformat()][0]
        src = {"Control 1": ("7ESL Listening Test 5 completo", l7(5), "7esl"), "Control 2": ("Cambridge · Sample test 1 · Listening", CAMB, "camb"),
               "Control 3": (f"{BOOK}, Test 4 · Listening", None, "book")}[name]
        a = url("Abrir el test", src[1], src[2]) if src[1] else book(f"{BOOK} · Test 4 · audio")
        return f"📍 {name} · Listening", [B("📍", src[0], 40, ["Las 4 partes, cada audio dos veces.", "Apunta tus aciertos en 📊 Notas."], a, kit=src[2])], "control"
    if w <= 18:
        lp = w in LP2
        if wd == 0:
            if lp: return "Gramática + Use of English + Listening Part 2", [grammar_block(w, 0)] + uoe_block(w, 20) + [lp2_block(w, 0)], None
            return "Gramática + Use of English", [grammar_block(w, 0)] + uoe_block(w, 35), None
        if wd == 1:
            rb = reading_block(w); rb[0]["m"] = 30; rb[1]["m"] = 15
            return "Reading + traducción inversa", rb + [inverse_blocks(w, topic, 1)], None
        if wd == 2: return "Writing", writing_block(w, topic, 35 if w <= 10 else 40), None
        if wd == 3: return "Listening + word formation + traducción inversa", [listening_block(w), B("🔧", "Word formation (Part 3)", 10, ["8 frases del tema; corrige con las soluciones.", ERR], claude(f"WORD FORMATION · {topic}")), inverse_blocks(w, topic, 2)], None
        if wd == 4:
            if lp: return "Speaking + gramática + Listening Part 2", [speaking_block(w, topic, 20), grammar_block(w, 1), lp2_block(w, 1)], None
            return "Speaking + gramática", [speaking_block(w, topic, 35), grammar_block(w, 1)], None
    # Fase 3: examen por partes, cronometrado
    if 19 <= w <= 26:
        src = {19: ("7esl", 10), 20: ("camb", 2), 21: ("7esl", 6), 22: ("7esl", 7), 23: ("7esl", 8), 24: ("7esl", 9), 25: ("7esl", 2), 26: ("7esl", 3)}[w]
        lab, link, kit = (f"7ESL Test {src[1]}", r7(src[1]), "7esl") if src[0] == "7esl" else ("Cambridge · Sample test 2", CAMB, "camb")
        llab, llink = (f"7ESL Listening Test {src[1]}", l7(src[1])) if src[0] == "7esl" else ("Cambridge · Sample test 2 · Listening", CAMB)
        if wd == 0: return "Use of English cronometrado", [B("⏱️", f"{lab} · Parts 1–4", 30, ["25 min con cronómetro, como en el examen.", "Apunta tus aciertos en 📊 Notas."], url("Abrir el test", link, kit), kit=kit),
                                                           B("🔍", "Corrige y entiende cada fallo", 25, [ERR], claude("EXPLICA"))], None
        if wd == 1: return "Reading cronometrado", [B("⏱️", f"{lab} · Parts 5–7", 45, ["45 min con cronómetro.", "Apunta tus aciertos en 📊 Notas."], url("Abrir el test", link, kit), kit=kit),
                                                    B("🔍", "Corrige", 10, ["Busca en el texto la frase que justifica cada respuesta."])], None
        if wd == 2:
            wtype = WRITE_TYPES[(w - 1) % len(WRITE_TYPES)]
            return "Writing cronometrado", [B("✍️", f"Writing · {lab} (Part 1 o la Part 2 «{wtype}»)", 40, ["40 min exactos, en tu nota «Writings».", "Pasa el checklist oficial antes de acabar."], url("Abrir la tarea", w7(src[1]) if src[0] == "7esl" else CAMB, kit), kit=kit),
                                            B("🔍", "Corrígelo con Claude", 15, ["Pega tu texto.", "Compara con el modelo de 7ESL."], claude("CORRIGE"))], None
        if wd == 3: return "Listening cronometrado", [B("⏱️", f"{llab} · las 4 partes", 40, ["Unos 40 min, cada audio dos veces.", "Apunta tus aciertos en 📊 Notas."], url("Abrir el test", llink, kit), kit=kit),
                                                      B("🔍", "Vuelve a escuchar lo que fallaste", 15, [ERR])], None
        if wd == 4: return "Speaking completo + Part 4", [B("🗣️", "Speaking completo (P1–P4)", 35, ["Modo voz, como el examen real.", f"P2: fotos del {BOOK}."], claude("SPEAKING COMPLETO"), kit="book"),
                                                          B("🔧", "Key word transformations", 20, [ERR], claude("TRANSFORMATIONS"))], None
    # Fase 4: simulacros con el libro (tests 1–3) y semana final
    if 27 <= w <= 29:
        m = w - 26
        if wd == 0: return f"🧪 Simulacro {m} · Reading & Use of English", [B("🧪", f"{BOOK}, Test {m} · Reading & Use of English", 75, ["Las 7 partes seguidas: 1 h 15. Hoy sin isla.", "Corrige con las respuestas del libro y apunta en 📊 Notas."], book(f"{BOOK} · Test {m}"), kit="book")], "mock"
        if wd == 1: return f"🧪 Simulacro {m} · Writing", [B("🧪", f"{BOOK}, Test {m} · Writing (Part 1 + una Part 2)", 80, ["1 h 20 seguidas. Hoy sin isla."], book(f"{BOOK} · Test {m} · Writing"), kit="book"),
                                                           B("🔍", "Corrígelos con Claude", 0, ["Esta tarde o mañana, 10 min."], claude("CORRIGE"))], "mock"
        if wd == 2: return f"🧪 Simulacro {m} · Listening", [B("🧪", f"{BOOK}, Test {m} · Listening", 40, ["Las 4 partes con el audio del libro.", "Apunta en 📊 Notas."], book(f"{BOOK} · Test {m} · audio"), kit="book"),
                                                             B("🔍", "Vuelve a escuchar lo que fallaste", 15, [ERR])], "mock"
        if wd == 3: return f"🧪 Simulacro {m} · Speaking", [B("🧪", "Speaking completo, como el examen", 25, [f"Fotos del {BOOK}, Test {m}.", "Si puedes, con tu compañero de Speaking."], claude("SPEAKING COMPLETO"), kit="book"),
                                                            B("🔍", "Tus 5 errores del Speaking a «Errores»", 10, [])], "mock"
        if wd == 4: return "Corrección del simulacro", [B("🔁", "Repasa todos los fallos del simulacro", 35, ["Uno por uno: entiende la regla.", ERR], claude("EXPLICA")),
                                                        B("🔧", "Repaso de tu gramática floja", 20, [], claude("REPASO GRAMÁTICA"))], None
    if w == 30:
        L = {0: ("Repaso final · Use of English", [B("🔁", "Repasa tu colección «Errores» entera en HyperLingua", 30, ["Nada de tests largos."], note("HyperLingua › Errores", "hl"))]),
             1: ("Repaso final · Writing", [B("🔁", "Relee tus 5 mejores writings corregidos", 30, ["Y las frases que más usas."], note("Notas › Writings", "notes"))]),
             2: ("Speaking suave", [B("🗣️", "Speaking P1 y P2, 15 min", 15, [], claude("SPEAKING P1 · free topic"))]),
             3: ("Logística", [B("🎯", "Revisa tu COE: hora, centro y día del Speaking", 15, ["Prepara DNI, lápiz y goma."], kit="exam")]),
             4: ("Descanso", [B("😴", "Mañana es el examen: solo Smart Review", 10, ["Duerme bien. 💪"])])}
        tag, bl = L[wd]
        return tag, bl, "light"
    return "Libre", [], None

def weekend_blocks(d, w, wd):
    topic = TOPICS[(w - 1) % len(TOPICS)]
    if wd == 5:
        return "Conversación + vocabulario + podcast", [
            B("💬", f"Conversación · {topic}", 25, ["Modo voz. 20 min de charla.", "Las 10 expresiones que te enseñe, a «Vocabulario B2»."], claude(f"CONVERSACIÓN · {topic}")),
            B("🧠", "Vocabulario de la semana a HyperLingua", 10, ["Copia las 40 frases que te da y pégalas en «Vocabulario B2» (Import)."], claude(f"VOCAB SEMANA · {topic}")),
            B("🎧", "6 Minute English · último episodio", 15, ["Escúchalo una vez sin transcripción y otra con ella."], url("Abrir 6 Minute English", BBC6, "bbc"), kit="bbc")], None
    return "Reescribir + revisión", [
        B("✍️", "Reescribe tu writing de esta semana", 20, ["Con las correcciones de Claude delante, sin copiar la versión mejorada.", "Pega la versión nueva después de la orden."], claude("REESCRIBIR")),
        B("📊", "Revisión de la semana", 10, ["Apunta en 📊 Notas los tests de la semana.", "Mira en 📅 el plan de la semana que viene."])], None

def build():
    program = {}
    prep = {
        PREP[0]: ("Prepara el material", [B("🧰", "Abre 🧰 Material y consigue lo de esta semana", 30, ["Pide el libro, crea las cuentas y monta el proyecto de Claude (botón Copiar)."], A("kit", "Abrir Material"))], None),
        PREP[1]: ("Prepara el material", [B("🧰", "Termina el material de 🧰", 30, ["HyperLingua (inglés UK) con las colecciones «Vocabulario B2» y «Errores».", "Descarga los PDF de Cambridge."], A("kit", "Abrir Material"))], None),
        PREP[2]: ("🎯 Test de nivel · Reading & Use of English", [B("🎯", "7ESL Test 1 · Reading & Use of English completo", 75, ["Sin cronómetro pero sin ayuda: es tu punto de partida.", "Apunta los aciertos de cada parte en 📊 Notas."], url("Abrir Test 1", r7(1), "7esl"))], "control"),
        PREP[3]: ("🎯 Test de nivel · Listening y Writing", [B("🎯", "7ESL Listening Test 1 completo", 40, ["Apunta los aciertos en 📊 Notas."], url("Abrir Listening 1", l7(1), "7esl")),
                                                           B("✍️", "Writing de nivel", 20, ["Pide un essay, escríbelo y corrígelo: es tu nota de partida."], claude("WRITING TAREA · Essay · Education and studying"))], "control"),
    }
    for d, (tag, bl, mark) in prep.items():
        program[d.isoformat()] = {"tag": f"Semana 0 · {tag}", "blocks": bl, **({"mark": mark} if mark else {})}
    d = START
    while d <= EXAM:
        k = d.isoformat(); wd = d.weekday(); w = week_of(d)
        ph = next(i for i, p in enumerate(PHASES) if p[1] <= w <= p[2])
        if d == EXAM:
            program[k] = {"tag": "🎯 Examen B2 First", "mark": "exam", "blocks": [B("🎯", "Hoy es el B2 First", 0, ["Desayuna bien, llega con tiempo, lleva el DNI.", "Tú puedes. 💪"])]}
            break
        if wd >= 5 and k not in CONTROLS and (d - datetime.timedelta(days=1)).isoformat() not in CONTROLS and w <= 29:
            tag, bl, mark = weekend_blocks(d, w, wd)
        elif wd >= 5 and w == 30:
            tag, bl, mark = "Descanso", [B("😴", "Solo Smart Review", 10, [])], "light"
        else:
            tag, bl, mark = day_blocks(d, w, wd)
        e = {"tag": f"Semana {w} · {tag}", "blocks": bl, "phase": ph + 1}
        if mark: e["mark"] = mark
        program[k] = e
        d += datetime.timedelta(days=1)
    for k, msg in (("2027-04-12", "⚠️ Matricúlate esta semana en el B2 First del 19 de junio (🧰 Material › Matrícula)."),
                   ("2027-05-03", "⚠️ ¿Ya estás matriculado? Si no, hoy: los plazos cierran a principios de mayo.")):
        program[k]["notice"] = msg; program[k].setdefault("kitDue", []).append("exam")
    # minutos de cada día (Smart Review 10 + isla 10 + bloques) y texto de respaldo
    for k, e in program.items():
        bmin = sum(b["m"] for b in e["blocks"])
        light = e.get("mark") == "light"
        mock_long = e.get("mark") in ("mock", "control") and bmin >= 60
        wkend = datetime.date.fromisoformat(k).weekday() >= 5
        e["min"] = 10 + (0 if light or mock_long or wkend or e.get("mark") == "exam" else 10) + bmin  # isla solo L–V
        lines = [f"# {b['i']} {b['t']}" + (f" · {b['m']} min" if b['m'] else "") + "".join(f"\n- {x}" for x in b["d"]) +
                 (f"\n{b['a']['u']}" if b.get("a", {}).get("u") else "") + (f"\n«{b['a']['c']}»" if b.get("a", {}).get("k") == "claude" else "") for b in e["blocks"]]
        e["text"] = (e.get("notice", "") + "\n\n" if e.get("notice") else "") + "\n\n".join(lines)
    # material: primer día en que se usa cada cosa
    first = {}
    for k in sorted(program):
        for b in program[k]["blocks"]:
            for kid in {b.get("kit"), (b.get("a") or {}).get("kit")} - {None}:
                first.setdefault(kid, k)
        for kid in program[k].get("kitDue", []): first.setdefault(kid, k)
    for prep_kit in ("hl", "claude", "handbook", "checklist", "notes"): first.setdefault(prep_kit, PREP[0].isoformat())
    first.setdefault("partner", "2027-03-01")
    kit = [dict(x, need=first.get(x["id"], PREP[1].isoformat())) for x in KIT]
    return {
        "id": "en", "name": "Inglés", "emoji": "🇬🇧", "color": "#14B8A6",
        "desc": "75 min L–V, 60 el sábado y 40 el domingo · objetivo: 180 (nota A, certificado C1) en el B2 First del 19 de junio de 2027",
        "type": "checklist", "target": 1, "unit": "", "step": 1,
        "steps": [{"id": "en-sr", "text": "Smart Review · 10 min"},
                  {"id": "en-isla", "text": "Isla · 10 min"},
                  {"id": "en-b2", "text": "Bloque B2 del día"}],
        "moment": "manana", "start": "2026-11-19", "archived": False,
        "schedule": {"mode": "dates", "days": [1, 2, 3, 4, 5], "times": 3, "n": 2, "dates": sorted(program)},
        "plan": {"mode": "none", "weekly": {}, "cycle": ["", ""], "program": program},
        "kit": kit,
        "course": {"exam": EXAM.isoformat(), "examLabel": "Cambridge B2 First", "start": START.isoformat(),
                   "phases": [{"name": p[0], "from": (START + datetime.timedelta(weeks=p[1] - 1)).isoformat(), "to": min(EXAM, START + datetime.timedelta(weeks=p[2], days=-1)).isoformat(), "goal": p[3]} for p in PHASES],
                   "controls": [{"date": k, "name": v[0], "goal": v[1]} for k, v in CONTROLS.items()],
                   "targets": [160, GOAL, 190], "goal": GOAL},
    }

def audit(h):
    """Comprueba que el plan no se queda corto. Devuelve lista de fallos (vacía = OK)."""
    pr = h["plan"]["program"]; errs = []
    allb = [b for e in pr.values() for b in e["blocks"]]
    txt = lambda b: b["t"]
    mins = sum(e["min"] for e in pr.values())
    if mins / 60 < 220: errs.append(f"horas totales {mins/60:.0f} < 220")
    gr = {b["a"]["u"] for b in allb if b.get("a", {}).get("u", "").startswith(BC)}
    if len(gr) < 36: errs.append(f"solo {len(gr)} lecciones de gramática")
    for t in ["Essay", "Email / letter", "Article", "Review", "Report"]:
        n = sum(1 for b in allb if b["t"].startswith(f"Writing · {t}") or f"«{t}»" in b["t"])
        if n < (8 if t == "Essay" else 3): errs.append(f"pocos writings de {t}: {n}")
    for p in ["P1", "P2", "P3", "P4"]:
        n = sum(1 for b in allb if b["t"] == f"Speaking · {p}")
        if n < 4: errs.append(f"poco Speaking {p}: {n}")
    if sum(1 for e in pr.values() if e.get("mark") == "mock") < 12: errs.append("menos de 3 simulacros completos")
    if sum(1 for e in pr.values() if e.get("mark") == "control") < 8: errs.append("faltan controles")
    if sum(1 for b in allb if b["t"].startswith("Listening") or "Listening" in b["t"]) < 25: errs.append("poco listening")
    if sum(1 for b in allb if "Vocabulario de la semana" in b["t"]) < 24: errs.append("faltan semanas de vocabulario")
    for k, e in pr.items():
        for b in e["blocks"]:
            a = b.get("a")
            if a and a["k"] == "url" and not a.get("u", "").startswith("https://"): errs.append(f"enlace roto {k}")
    return errs
