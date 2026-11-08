#!/usr/bin/env python3
"""
¿Alguna fuente lleva tiempo fallando, o la auditoría ha visto algo grave? Lo apunta en cache/salud.json y deja en
salud.md el texto del aviso (vacío si todo va bien). recolectar.yml abre, actualiza o cierra con él un issue en
GitHub, que llega por correo y a la app de GitHub.
"""
import json
import re
import sys
from datetime import datetime, timezone

UMBRAL_H = 36   # una caída de una tarde no avisa; de día y medio, sí
ahora = datetime.now(timezone.utc)
d = json.load(open("datos/radares.json", encoding="utf-8"))
salud = {}
try:
    salud = json.load(open("cache/salud.json", encoding="utf-8"))
except (OSError, ValueError):
    pass

fallan = {}
for nombre, estado in (d.get("fuentes") or {}).items():
    e = str(estado)
    if "falló" in e or "⛔" in e or ("⚠️" in e and "se mantienen" in e):
        fallan[nombre] = e[:200]
for nombre in list(salud):
    if nombre not in fallan:
        del salud[nombre]          # se ha recuperado
for nombre, e in fallan.items():
    salud.setdefault(nombre, {"desde": ahora.isoformat(timespec="minutes")})
    salud[nombre]["ultimo"] = e
json.dump(salud, open("cache/salud.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

lineas = []
for nombre, s in sorted(salud.items()):
    h = (ahora - datetime.fromisoformat(s["desde"])).total_seconds() / 3600
    if h >= UMBRAL_H:
        lineas.append(f"- **{nombre}**: falla desde hace {h / 24:.1f} días. Último estado: {s['ultimo']}")
inf = open("datos/INFORME.md", encoding="utf-8").read()
m = re.search(r"## Auditoría automática\s+(⚠️[^\n]*)", inf)
if m:
    lineas.append(f"- **Auditoría**: {m.group(1)[:400]}")
texto = ""
if lineas:
    texto = ("Atalaya ha detectado problemas en la recolección de datos:\n\n" + "\n".join(lineas) +
             f"\n\nDatos de {d.get('version')}. Informe completo: datos/INFORME.md y datos/AUDITORIA.md.\n"
             "Este aviso se cierra solo cuando todo vuelve a ir bien.")
open("salud.md", "w", encoding="utf-8").write(texto)
print(texto or "todo bien")
sys.exit(0)
