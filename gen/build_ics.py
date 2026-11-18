"""Genera ironhabits.ics: calendario de suscripción (iPhone / Google Calendar) con hábitos y compromisos fijos.
Cada evento lleva un aviso 5 min antes y, si es un hábito, lo que toca ese día. Se regenera en cada publicación."""
import json, datetime, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
pack = json.loads((ROOT / "plan.json").read_text(encoding="utf-8"))
H = {h["id"]: h for h in pack["habits"]}

def esc(t):
    return str(t or "").replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")

def fold(line):  # RFC 5545: líneas de máx. 75 octetos
    b = line.encode("utf-8"); out = []
    while len(b) > 74:
        cut = 74
        while (b[cut] & 0xC0) == 0x80: cut -= 1
        out.append(b[:cut].decode()); b = b[cut:]
    out.append(b.decode()); return "\r\n ".join(out)

def dt(day, hm):
    h, m = map(int, hm.split(":")); d = datetime.date.fromisoformat(day)
    if h >= 24: h -= 24; d += datetime.timedelta(days=1)
    return f"{d:%Y%m%d}T{h:02d}{m:02d}00"

def plan_text(hid, day):
    e = (H[hid].get("plan") or {}).get("program", {}).get(day)
    if not e: return ""
    txt = e if isinstance(e, str) else (e.get("tag", "") + "\n" + e.get("text", ""))
    return re.sub(r"\n{2,}", "\n", txt)[:900]

stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//IronHabits//ES", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
     "X-WR-CALNAME:IronHabits", "X-WR-TIMEZONE:Europe/Madrid", "REFRESH-INTERVAL;VALUE=DURATION:PT6H", "X-PUBLISHED-TTL:PT6H",
     "BEGIN:VTIMEZONE", "TZID:Europe/Madrid",
     "BEGIN:DAYLIGHT", "TZOFFSETFROM:+0100", "TZOFFSETTO:+0200", "TZNAME:CEST", "DTSTART:19700329T020000", "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU", "END:DAYLIGHT",
     "BEGIN:STANDARD", "TZOFFSETFROM:+0200", "TZOFFSETTO:+0100", "TZNAME:CET", "DTSTART:19701025T030000", "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU", "END:STANDARD",
     "END:VTIMEZONE"]
n = 0
for day in sorted(pack["agenda"]):
    for e in pack["agenda"][day]:
        if e["kind"] not in ("habito", "fijo"): continue
        hid = e.get("habit"); emoji = H[hid]["emoji"] + " " if hid in H else ""
        desc = plan_text(hid, day) if hid else e.get("detail", "")
        L += ["BEGIN:VEVENT", f"UID:{day}-{e['id'].replace(':', '-')}@ironhabits", f"DTSTAMP:{stamp}",
              f"DTSTART;TZID=Europe/Madrid:{dt(day, e['start'])}", f"DTEND;TZID=Europe/Madrid:{dt(day, e['end'])}",
              f"SUMMARY:{esc(emoji + e['title'])}", f"DESCRIPTION:{esc(desc)}",
              "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{esc(e['title'])}", "TRIGGER:-PT5M", "END:VALARM", "END:VEVENT"]
        n += 1
L.append("END:VCALENDAR")
(ROOT / "ironhabits.ics").write_text("\r\n".join(fold(x) for x in L) + "\r\n", encoding="utf-8")
print(f"ironhabits.ics: {n} eventos, {(ROOT / 'ironhabits.ics').stat().st_size // 1024} KB")
