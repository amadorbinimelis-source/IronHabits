"""Comprueba que todos los enlaces del plan (clases y material) responden. Se ejecuta en GitHub Actions (allí hay red).
Falla con 404/410 o si el dominio no existe. 401/403/429 y los tiempos de espera agotados (webs que no contestan a
robots, como British Council) solo avisan: esos enlaces se comprueban a mano al añadirlos."""
import json, re, sys, urllib.request, urllib.error, os, ssl
P = json.load(open(os.path.join(os.path.dirname(__file__), "..", "plan.json"), encoding="utf-8"))
urls = set()
for h in P["habits"]:
    for e in (h.get("plan", {}).get("program") or {}).values():
        if isinstance(e, dict):
            for b in e.get("blocks", []):
                u = (b.get("a") or {}).get("u")
                if u: urls.add(u)
    for x in h.get("kit", []):
        if x.get("url"): urls.add(x["url"])
bad, warn = [], []
ctx = ssl.create_default_context()
for u in sorted(urls):
    req = urllib.request.Request(u, method="GET", headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1"})
    try:
        with urllib.request.urlopen(req, timeout=12, context=ctx) as r: code = r.status
    except urllib.error.HTTPError as e: code = e.code
    except Exception as e: code = f"error: {e}"
    soft = isinstance(code, str) and ("timed out" in code or "timeout" in code.lower() or "reset" in code.lower())
    if code in (404, 410) or (isinstance(code, str) and not soft): bad.append((u, code))
    elif code not in (200, 301, 302): warn.append((u, code))
    print(code, u)
for u, c in warn: print("AVISO", c, u)
if bad:
    for u, c in bad: print("ROTO", c, u)
    sys.exit(1)
print(f"OK: {len(urls)} enlaces")
