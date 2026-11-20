"""Agenda diaria (tipo calendario) a partir del horario de Amador y del plan de hábitos.

Supuestos (ajustables desde la app):
- Sueño de 8 h: lun y jue a la cama a las 00:00 (vuelve del fútbol a las 22:50); mar, mié y vie a las 23:30 (boxeo hasta las 21:30);
  sáb y dom a las 23:00. Despertar = hora de acostarse de la noche anterior + 8 h.
- Trayecto casa ↔ Sant Pau/biblio/gimnasio: 30 min. Clase ↔ gimnasio: 40 min. Casa → clase: 40 min.
- Fútbol (fisio) lun y jue: sale 18:00, entreno 19–22, llega 22:50. La cena se deja hecha al mediodía.
- Partido el domingo por la mañana (hora aproximada). Tirada con Mimi el sábado a media mañana (aproximada).
- Clase de boxeo: 20:30–21:30.
"""
import datetime, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import entreno_plan

START = datetime.date(2026, 11, 19)
END = datetime.date(2027, 6, 20)

CLASS_INFO = {  # fecha: (asignatura, inicio, fin, descripción)
    "2026-11-20": ("CMUS", 15.0, 18.0, "CMUS · teoría"),
    "2026-11-24": ("NEDM", 16.0, 18.5, "NEDM · teoría"),
    "2026-11-25": ("LESP", 15.0, 19.0, "LESP · plab"),
    "2026-11-27": ("CMUS", 15.0, 19.0, "CMUS · teoría + plab G1"),
    "2026-12-01": ("NEDM", 16.0, 20.0, "NEDM · plab"),
    "2026-12-02": ("LESP", 16.0, 19.0, "LESP · plab"),
    "2026-12-04": ("CMUS", 15.0, 19.0, "CMUS · teoría + presentación"),
    "2026-12-09": ("LESP", 16.0, 19.0, "LESP · plab"),
    "2026-12-11": ("CMUS", 15.0, 17.0, "CMUS · 2.º parcial"),
    "2026-12-15": ("NEDM", 15.0, 20.0, "NEDM · prueba de plab"),
    "2026-12-16": ("LESP", 15.0, 20.0, "LESP · prueba de plab"),
    "2026-12-22": ("LESP", 17.0, 19.0, "LESP · examen"),
    "2027-01-12": ("NEDM", 16.0, 18.0, "NEDM · examen"),
    "2027-01-14": ("CMUS", 15.0, 17.0, "CMUS · examen"),
}
assert all(entreno_plan.CLASSES[k][1] == v[2] for k, v in CLASS_INFO.items()), "clases desincronizadas"

BED = {0: 24.0, 1: 23.5, 2: 23.5, 3: 24.0, 4: 23.5, 5: 23.0, 6: 23.0}   # hora de acostarse por día de la semana

def hm(h):
    h = round(h * 60) / 60
    return f"{int(h) % 24:02d}:{int(round((h % 1) * 60)):02d}" if h < 24 else f"{int(h):02d}:{int(round((h % 1) * 60)):02d}"

class Day:
    def __init__(self, d):
        self.d = d; self.ev = []
    def add(self, id_, title, s, e, kind, habit=None, detail=""):
        assert e > s, (self.d, title, s, e)
        self.ev.append({"id": id_, "title": title, "start": hm(s), "end": hm(e), "kind": kind,
                        **({"habit": habit} if habit else {}), **({"detail": detail} if detail else {})})
        return e

def wake_of(d):
    prev = d - datetime.timedelta(days=1)
    return BED[prev.weekday()] + 8 - 24

def build_day(d, has, train, en_h=0.75):
    """has: conjunto de hábitos con plan ese día; train: lista (habit, moment, tag, text) del entreno."""
    k = d.isoformat(); wd = d.weekday(); D = Day(d)
    wake = wake_of(d); bed = BED[wd]
    cls = CLASS_INFO.get(k)
    tr = {h: (m, tag) for h, m, tag, _ in train}
    reduced = "fuerza" in tr and "45 min" in tr["fuerza"][1]
    fdur = 0.75 if reduced else 1.17  # 45 min o ~70 min
    t = D.add("desayuno", "Despertar, asearte y desayunar", wake, wake + 0.5, "rutina")

    if wd == 6:  # domingo
        t = D.add("partido", "Partido (fisio) · trayectos incluidos", t, 11.5, "fijo", detail="Hora aproximada: si el partido es por la tarde, cámbiala aquí.")
        t = 12.0
        if "fr" in has: t = D.add("h:fr", "Francés", t, t + 0.75, "habito", "fr")
        if "en" in has: t = D.add("h:en", "Inglés", t, t + en_h, "habito", "en")
        t = D.add("comida", "Cocinar y comer", max(t, 13.5), max(t, 13.5) + 1, "comida")
        D.add("libre1", "Descanso", t, 17.0, "libre")
        t = 17.0
        if "dx" in has: t = D.add("h:dx", "Diagnóstico diferencial · caso clínico", t, t + 1, "habito", "dx")
        D.add("libre2", "Tiempo libre", t, 21.0, "libre")
        t = D.add("cena", "Cocinar y cenar", 21.0, 21.75, "comida")
        D.add("libre3", "Relax", t, bed, "libre")
        return D

    if wd == 5:  # sábado
        t = 8.0
        if "fr" in has: t = D.add("h:fr", "Francés", t, t + 0.75, "habito", "fr")
        if "en" in has: t = D.add("h:en", "Inglés", t, t + en_h, "habito", "en")
        t = D.add("tray1", "Trayecto al gimnasio", t, t + 0.5, "trayecto")
        if "boxeo" in tr: t = D.add("h:boxeo", "Boxeo por tu cuenta (gimnasio)", t, t + 1, "habito", "boxeo")
        t = D.add("mimi", "Tirada con Mimi", t + 0.25, t + 1.75, "fijo", detail="Hora aproximada: ajústala a su tirada.")
        t = D.add("comida", "Cocinar y comer", max(t + 0.25, 13.75), max(t + 0.25, 13.75) + 1, "comida")
        D.add("libre1", "Descanso", t, 16.0, "libre")
        t = 16.0
        if "estudio" in has: t = D.add("h:estudio", "Estudio de exámenes", t, t + 1, "habito", "estudio")
        if "dx" in has: t = D.add("h:dx", "Diagnóstico diferencial · app", t, t + 1, "habito", "dx")
        D.add("libre2", "Tiempo libre", t, 21.0, "libre")
        t = D.add("cena", "Cocinar y cenar", 21.0, 21.75, "comida")
        D.add("libre3", "Tiempo libre", t, bed, "libre")
        return D

    # ── lunes a viernes ──
    if "fr" in has: t = D.add("h:fr", "Francés", t, t + 0.75, "habito", "fr")
    if "en" in has: t = D.add("h:en", "Inglés", t, t + en_h, "habito", "en")
    t = D.add("tray1", "Ir a Sant Pau (dejar material) y a la biblio", t, t + 0.5, "trayecto")
    if "estudio" in has: t = D.add("h:estudio", "Estudio de exámenes (biblio)", t, t + 1, "habito", "estudio")
    if "dx" in has: t = D.add("h:dx", "Diagnóstico diferencial · teoría (biblio)", t, t + 1, "habito", "dx")
    am_f = "fuerza" in tr and tr["fuerza"][0] == "manana"
    am_b = "boxeo" in tr and tr["boxeo"][0] == "manana"
    if am_f:
        place = "parque de barras" if wd == 0 else "gimnasio"
        t = D.add("h:fuerza", f"Fuerza / calistenia ({place})", t, t + fdur, "habito", "fuerza")
    if am_b:
        t = D.add("h:boxeo", "Boxeo por tu cuenta (gimnasio)", t, t + 1, "habito", "boxeo")

    leave = cls[1] - 40 / 60 if cls else None
    home_lunch_end = max(t + 0.5, 13.0) + (1.25 if wd in (0, 3) else 1.0)
    tupper = cls is not None and home_lunch_end > leave
    if tupper:
        t = D.add("comida", "Comer táper (preparado la noche anterior)", t, t + 0.5, "comida")
        t = D.add("tray2", "Trayecto a clase", t, t + 40 / 60, "trayecto")
        if t < cls[1]: t = D.add("libre1", "Margen antes de clase", t, cls[1], "libre")
    else:
        t = D.add("tray2", "Vuelta a casa", t, t + 0.5, "trayecto")
        s = max(t, 13.0)
        if s > t: D.add("libre0", "Tiempo libre", t, s, "libre")
        title = "Cocinar, comer y dejar la cena hecha" if wd in (0, 3) else "Cocinar y comer"
        t = D.add("comida", title, s, home_lunch_end, "comida")

    if wd in (0, 3):  # fútbol
        D.add("libre1", "Tiempo libre", t, 17.5, "libre")
        D.add("merienda", "Merienda", 17.5, 18.0, "comida")
        D.add("tray3", "Trayecto al fútbol", 18.0, 19.0, "trayecto")
        D.add("futbol", "Fútbol · entreno (fisio)", 19.0, 22.0, "fijo")
        D.add("tray4", "Vuelta a casa", 22.0, 22 + 50 / 60, "trayecto")
        t = D.add("cena", "Cenar (cena ya hecha)", 22 + 50 / 60, 23 + 20 / 60, "comida")
        D.add("libre3", "Desconectar", t, bed, "libre")
        return D

    # martes, miércoles, viernes
    if cls:
        if not tupper:
            if leave > t: D.add("libre1", "Tiempo libre", t, leave, "libre")
            t = D.add("tray2b", "Trayecto a clase", leave, cls[1], "trayecto")
        t = D.add("clase", cls[3], cls[1], cls[2], "fijo")
    ev_f = "fuerza" in tr and tr["fuerza"][0] != "manana"
    ev_b = "boxeo" in tr and tr["boxeo"][0] != "manana"
    if ev_f:
        t = D.add("tray5", "Trayecto al gimnasio", t, t + 40 / 60, "trayecto")
        t = D.add("h:fuerza", "Fuerza / calistenia (gimnasio)" + (" · versión 45 min" if reduced else ""), t, t + fdur, "habito", "fuerza")
    if ev_b:
        if not ev_f:
            go = 20.5 - (40 / 60 if cls else 0.5)
            if go > t: D.add("libre2", "Tiempo libre", t, go, "libre")
            t = D.add("tray5", "Trayecto al gimnasio", max(t, go), 20.5, "trayecto")
        elif t < 20.5:
            t = D.add("merienda", "Merienda / margen", t, 20.5, "comida")
        t = D.add("h:boxeo", "Clase de boxeo", 20.5, 21.5, "habito", "boxeo")
        t = D.add("tray6", "Vuelta a casa", t, t + 0.5, "trayecto")
    else:
        if cls and not ev_f:
            t = D.add("tray6", "Vuelta a casa", t, t + 40 / 60, "trayecto")
        if t < 21.0: D.add("libre2", "Tiempo libre", t, 21.0, "libre")
        t = max(t, 21.0)
    t = D.add("cena", "Cocinar y cenar", t, t + 0.75, "comida")
    if bed > t: D.add("libre3", "Desconectar", t, bed, "libre")
    return D

def habits_with_plan(H, k):
    out = set()
    for h in H:
        hid = h["id"]
        if hid in ("fuerza", "boxeo"):
            continue
        prog = h["plan"].get("program", {})
        if k in prog:
            out.add(hid)
        elif hid == "estudio" and datetime.date.fromisoformat(k).weekday() != 6:
            out.add(hid)
    return out

def build(H):
    agenda = {}
    en = next((h for h in H if h["id"] == "en"), None)
    en_min = {k: e.get("min", 45) for k, e in (en["plan"]["program"] if en else {}).items()}
    d = START
    days = []
    while d <= END:
        k = d.isoformat()
        has = habits_with_plan(H, k)
        train = entreno_plan.plan_day(d)
        D = build_day(d, has, train, max(10, en_min.get(k, 45)) / 60)
        days.append(D)
        d += datetime.timedelta(days=1)
    # Preparar táper la noche anterior cuando el día siguiente come táper
    for i in range(len(days) - 1):
        nxt = days[i + 1]
        if any(e["id"] == "comida" and "táper" in e["title"] for e in nxt.ev):
            cur = days[i]
            for e in cur.ev:
                if e["id"] == "libre3":
                    s = e["start"]; h, m = map(int, s.split(":")); st = h + m / 60
                    e["start"] = hm(st + 0.25)
                    cur.ev.insert(cur.ev.index(e), {"id": "taper", "title": "Preparar el táper de mañana", "start": hm(st), "end": hm(st + 0.25), "kind": "comida"})
                    break
    for D in days:
        # rellenar huecos para que el día se lea entero
        fixed = []
        for a, b in zip(D.ev, D.ev[1:] + [None]):
            fixed.append(a)
            if b is None: continue
            ea = int(a["end"][:2]) * 60 + int(a["end"][3:]); sb = int(b["start"][:2]) * 60 + int(b["start"][3:])
            if sb - ea >= 10:
                title = ("Ir a buscar a Mimi" if b["id"] == "mimi" else
                         "Ducha y descanso" if a["id"] in ("partido", "mimi") or a["id"].startswith("h:boxeo") else "Tiempo libre")
                fixed.append({"id": f"hueco{len(fixed)}", "title": title, "start": a["end"], "end": b["start"], "kind": "libre"})
        D.ev = fixed
        # dormir: desde la hora de acostarse hasta la medianoche (el resto se ve en el día siguiente)
        bed = BED[D.d.weekday()]
        nxt_wake = wake_of(D.d + datetime.timedelta(days=1))
        D.add("dormir", f"Dormir (mañana te levantas a las {hm(nxt_wake)})", bed, max(bed + 0.5, 24.0), "sueno")
        agenda[D.d.isoformat()] = D.ev
    return agenda
