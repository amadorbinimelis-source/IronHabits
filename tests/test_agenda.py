"""Revisión automática de la agenda generada (plan.json)."""
import json, datetime, sys, os
P = json.load(open(os.path.join(os.path.dirname(__file__), "..", "plan.json"), encoding="utf-8"))
A = P["agenda"]; H = {h["id"]: h for h in P["habits"]}
def mins(s): h, m = map(int, s.split(":")); return h * 60 + m
errors = []; warns = []
days = sorted(A)
for k in days:
    ev = A[k]; d = datetime.date.fromisoformat(k)
    # 1. sin solapes y en orden
    for a, b in zip(ev, ev[1:]):
        if mins(b["start"]) < mins(a["end"]): errors.append(f"{k}: solape «{a['title']}» {a['start']}-{a['end']} con «{b['title']}» {b['start']}")
    # 2. sin huecos sin asignar (todo el día cubierto desde el despertar hasta dormir)
    for a, b in zip(ev, ev[1:]):
        if mins(b["start"]) - mins(a["end"]) > 20: warns.append(f"{k}: hueco de {mins(b['start'])-mins(a['end'])} min entre «{a['title']}» y «{b['title']}»")
    ids = [e["id"] for e in ev]
    # 3. comidas
    for need in ("desayuno", "comida", "cena", "dormir"):
        if need not in ids: errors.append(f"{k}: falta {need}")
    # 4. cada hábito con plan ese día tiene su bloque
    for hid, h in H.items():
        prog = h["plan"].get("program", {})
        due = k in prog or (hid == "estudio" and d.weekday() != 6)
        has = f"h:{hid}" in ids
        if due and not has: errors.append(f"{k}: falta el bloque de {h['name']}")
        if has and not due: errors.append(f"{k}: bloque de {h['name']} sin plan")
    # 5. ids únicos
    if len(ids) != len(set(ids)): errors.append(f"{k}: ids repetidos {ids}")
    # 6. llegar a clase a tiempo y boxeo a las 20:30
    for e in ev:
        if e["id"] == "clase":
            i = ids.index("clase"); prev = ev[i - 1]
            if prev["kind"] not in ("trayecto", "libre"): errors.append(f"{k}: antes de clase no hay trayecto/margen ({prev['title']})")
        if e["id"] == "h:boxeo" and "Clase" in e["title"] and e["start"] != "20:30": errors.append(f"{k}: boxeo fuera de hora")
# 7. sueño ≥ 7.5 h
for a, b in zip(days, days[1:]):
    bed = mins([e for e in A[a] if e["id"] == "dormir"][0]["start"])
    wake = mins(A[b][0]["start"]) + 24 * 60
    if (wake - bed) / 60 < 7.5: errors.append(f"{a}→{b}: solo {(wake-bed)/60:.1f} h de sueño")
print(f"Días revisados: {len(days)} ({days[0]} → {days[-1]})")
print(f"Errores: {len(errors)}"); [print("  ✗", e) for e in errors[:40]]
print(f"Avisos: {len(warns)}"); [print("  !", w) for w in warns[:20]]
sys.exit(1 if errors else 0)
