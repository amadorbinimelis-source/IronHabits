"""Plan de entreno: fuerza/calistenia + boxeo, colocado según el calendario de clases.
Reglas (acordadas con Amador):
- Trayecto clase → gimnasio: 40 min. Gimnasio L–V 7–22, sábado 7–12, domingo cerrado.
- Lunes: tirón por la mañana (parque de barras), fútbol por la tarde. Jueves: sin entreno (fútbol).
- Martes pierna + boxeo · Miércoles empuje + boxeo · Viernes mixto + boxeo. Siempre fuerza antes que boxeo.
- Clase hasta las 20:00 → fuerza y boxeo por la mañana.
- LESP hasta las 19:00 → fuerza reducida (45 min) + boxeo 20:30.
- CMUS hasta las 19:00 → fuerza por la mañana + boxeo 20:30.
- Clase que acaba ≤ 18:30 → fuerza al llegar (fin + 40 min) + boxeo 20:30.
- Sin clase → fuerza por la mañana + boxeo 20:30.
- Sábado: boxeo por tu cuenta (gimnasio por la mañana). Domingo: descanso (partido como fisio).
- Días de examen: se entrena normal.
"""
import datetime

START = datetime.date(2026, 11, 19)
END = datetime.date(2027, 6, 20)
CLASSES_KNOWN_UNTIL = datetime.date(2027, 1, 31)  # después: sin clases conocidas → regla «sin clase»

# fecha: (asignatura, hora de fin)
CLASSES = {
    "2026-11-20": ("CMUS", 18.0), "2026-11-24": ("NEDM", 18.5), "2026-11-25": ("LESP", 19.0),
    "2026-11-27": ("CMUS", 19.0), "2026-12-01": ("NEDM", 20.0), "2026-12-02": ("LESP", 19.0),
    "2026-12-04": ("CMUS", 19.0), "2026-12-09": ("LESP", 19.0), "2026-12-11": ("CMUS", 17.0),
    "2026-12-15": ("NEDM", 20.0), "2026-12-16": ("LESP", 20.0), "2026-12-22": ("LESP", 19.0),
    "2027-01-12": ("NEDM", 18.0), "2027-01-14": ("CMUS", 17.0),
}

def hhmm(h):
    return f"{int(h)}:{int(round((h % 1) * 60)):02d}"

CORE = ["Core (10 min) · bloque 1: dead bug 3×10 · Pallof press 3×10 por lado · hollow hold 3×30 s",
        "Core (10 min) · bloque 2: rueda abdominal 3×8 · L-sit 3× máx · rotación con landmine 3×8 por lado"]
EMPUJE_EXTRA = ["fondos", "press militar", "flexión con goma"]

def empuje(w, reduced):
    core = CORE[w % 2]
    if reduced:
        return ("Empuje · versión 45 min",
                "- Calentamiento de muñecas y hombro (5 min)\n- 3×2 subidas a pino desde rana (excéntrica con goma)\n- 3×45–50 s montadas de pino + aguante\n- 3× RIR 2 flexiones en pica\n- Core 5 min: 2 series de " + core.split(': ', 1)[1])
    return ("Empuje",
            f"- Calentamiento de muñecas y hombro (8 min)\n- 3×2 subidas a pino desde rana (excéntrica con goma)\n- 3×45–50 s montadas de pino + aguante\n- 3× RIR 2 flexiones en pica\n- 3× RIR 1 {EMPUJE_EXTRA[w % 3]}\n- {core}")

def tiron():
    return ("Tirón · parque de barras",
            "- Calentamiento de hombro y escápulas (8 min)\n- 3×2 muscle-ups\n- 3×3–4 muscle-ups con goma\n- 3× RIR 2 dominadas pronas\n- 3× RIR 1 dominadas supinas")

def mixto(reduced):
    if reduced:
        return ("Mixto · versión 45 min", "- Calentamiento (5 min)\n- 3×2 muscle-ups\n- 3× aguante de pino en pared casi al máximo\n- Si te sobra tiempo: 2×4 remontadas en pared")
    return ("Mixto",
            "- Calentamiento (8 min)\n- 3×2 muscle-ups\n- 3× RIR 1 dominadas\n- 3×4 remontadas en pared y bajar\n- 3× aguante de pino en pared casi al máximo")

def pierna(w, reduced):
    core = CORE[w % 2]
    if w % 2 == 0:
        name = "Pierna A"
        full = ("- Calentamiento + movilidad de cadera y tobillo (10 min)\n- 4× (isométrico máximo de media sentadilla 5 s → 3 saltos verticales)\n"
                "- 3×5 búlgara pesada\n- 3×6 saltos laterales tipo skater\n- 3×5 nórdicos\n- 3×12 gemelo\n- " + core)
        red = "- Calentamiento (5 min)\n- 4× (isométrico máximo 5 s → 3 saltos verticales)\n- 3×5 búlgara pesada\n- 3×6 saltos laterales tipo skater"
    else:
        name = "Pierna B"
        full = ("- Calentamiento + movilidad de cadera y tobillo (10 min)\n- 4× (3 pesos muertos pesados → 3 saltos verticales)\n"
                "- 3×6 hip thrust\n- 3×5 saltos horizontales\n- 3×6 saltos en zancada alterna\n- 3×20 s Copenhagen por lado\n- " + core)
        red = "- Calentamiento (5 min)\n- 4× (3 pesos muertos pesados → 3 saltos verticales)\n- 3×6 hip thrust\n- 3×5 saltos horizontales"
    return (name + (" · versión 45 min" if reduced else ""), red if reduced else full)

FOCOS = ["jab-cross", "ganchos", "al cuerpo", "defensa + contra", "volumen", "potencia"]

def boxeo_propio(w):
    focos = [FOCOS[(w + i) % 6] for i in range(6)]
    return ("Boxeo por tu cuenta",
            "- Comba 3×3 min\n- Sombra 3×3 min\n- Saco: 6 asaltos de 3 min (1 min de descanso)\n" +
            "\n".join(f"  · Asalto {i+1}: {f}" for i, f in enumerate(focos)) + "\n- Cuello y core: 5 min")

def boxeo_clase():
    return ("Clase de boxeo 20:30", "- Clase del profe de tarde.\n- Lleva vendas, guantes y agua.")

def plan_day(d):
    """Devuelve una lista de (habit_id, moment, tag, text)."""
    k = d.isoformat(); wd = d.weekday(); w = (d - datetime.date(2026, 11, 16)).days // 7
    cls = CLASSES.get(k)
    out = []
    if wd == 0:
        n, t = tiron(); out.append(("fuerza", "manana", f"🌅 Mañana · {n}", t))
        return out
    if wd == 3 or wd == 6:
        return out
    if wd == 5:
        n, t = boxeo_propio(w); out.append(("boxeo", "manana", f"🌅 Mañana (gimnasio 7–12) · {n}", t))
        return out
    # martes, miércoles, viernes
    if wd == 1: strength = lambda r: pierna(w, r)
    elif wd == 2: strength = lambda r: empuje(w, r)
    else: strength = lambda r: mixto(r)
    if cls is None:
        n, t = strength(False); out.append(("fuerza", "manana", f"🌅 Mañana · {n}", t))
        n, t = boxeo_clase(); out.append(("boxeo", "noche", f"🌙 {n}", t))
        return out
    subj, end = cls
    arrive = end + 40 / 60
    if end >= 20:
        n, t = strength(False); out.append(("fuerza", "manana", f"🌅 Mañana · {n}", t + f"\n(Hoy tienes {subj} hasta las {hhmm(end)}: todo por la mañana.)"))
        n, t = boxeo_propio(w); out.append(("boxeo", "manana", f"🌅 Mañana · {n} (o clase de mañana)", t))
        return out
    if end >= 19:
        if subj == "LESP":
            n, t = strength(True); out.append(("fuerza", "noche", f"🌙 {hhmm(arrive)} · {n}", t + f"\n(Sales de {subj} a las {hhmm(end)}: versión corta antes del boxeo.)"))
        else:
            n, t = strength(False); out.append(("fuerza", "manana", f"🌅 Mañana · {n}", t + f"\n(Hoy tienes {subj} hasta las {hhmm(end)}.)"))
        n, t = boxeo_clase(); out.append(("boxeo", "noche", f"🌙 {n}", t))
        return out
    n, t = strength(False); out.append(("fuerza", "tarde" if arrive < 19 else "noche", f"{'🌤️' if arrive < 19 else '🌙'} {hhmm(arrive)} · {n}", t + f"\n(Sales de {subj} a las {hhmm(end)}; llegas al gimnasio sobre las {hhmm(arrive)}.)"))
    n, t = boxeo_clase(); out.append(("boxeo", "noche", f"🌙 {n}", t))
    return out

def build():
    prog = {"fuerza": {}, "boxeo": {}}
    d = START
    while d <= END:
        for hid, mom, tag, txt in plan_day(d):
            entry = {"tag": tag, "text": txt, "moment": mom}
            if hid == "fuerza" and "45 min" in tag:   # si se anula la clase, pasa a la sesión completa
                wd = d.weekday(); w = (d - datetime.date(2026, 11, 16)).days // 7
                n, t = (pierna(w, False) if wd == 1 else empuje(w, False) if wd == 2 else mixto(False))
                entry["alt"] = {"tag": f"🌅 Sin clase · {n} completa", "text": t + "\n(Has anulado la clase: hoy toca la sesión completa.)", "moment": "manana"}
            prog[hid][d.isoformat()] = entry
        d += datetime.timedelta(days=1)
    def habit(hid, name, emoji, color, desc):
        p = prog[hid]
        return {"id": hid, "name": name, "emoji": emoji, "color": color, "desc": desc,
                "type": "check", "target": 1, "unit": "", "step": 1, "steps": [],
                "moment": "any", "start": START.isoformat(), "archived": False,
                "schedule": {"mode": "dates", "days": [1, 2, 3, 4, 5], "times": 3, "n": 2, "dates": sorted(p)},
                "plan": {"mode": "none", "weekly": {}, "cycle": ["", ""], "program": p}}
    return [habit("fuerza", "Fuerza / calistenia", "💪", "#A855F7", "Rutina de tu hermano (empuje, tirón, mixto) + pierna con contraste. Siempre antes del boxeo."),
            habit("boxeo", "Boxeo", "🥊", "#EF4444", "4 sesiones por semana: clase de las 20:30 o por tu cuenta.")]
