#!/usr/bin/env python3
"""
Pasa las decisiones tomadas a ojo sobre las hojas de posición a verificados.json.

decisiones.json: {"<n>": "ok" | "h<idx>[+m]" | "x" | "no"}
  ok      → la cabina/pórtico está donde lo tenemos (±40 m): se da por comprobado
  h7      → está justo delante de la foto 7 (a unos 20 m); h7+40 = a 40 m de esa foto
  f1+40   → hoja de zoom: a unos 40 m delante de la foto 1 (0 = la de arriba)
  x       → no se puede saber con las fotos (se queda como aproximado)
  no      → con fotos completas no se ve nada: se apunta para revisarlo, sin tocarlo
"""
import json
import math
import re
import sys

sys.path.insert(0, ".")
from posiciones_mapillary import dist, pares  # noqa: E402

objetivos = json.load(open("depurar/objetivos_posicion.json", encoding="utf-8"))
indices, zoom = {}, {}
for ruta in sys.argv[2:]:
    for r in json.load(open(ruta, encoding="utf-8")):
        (zoom if "fotos" in r else indices)[r["n"]] = r
dec = json.load(open(sys.argv[1], encoding="utf-8"))
ver = json.load(open("verificados.json", encoding="utf-8"))
P = {p["id"]: p for p in json.load(open("datos/radares.json", encoding="utf-8"))["puntos"]}


def en_linea(o, s):
    """Punto a s metros del punto estimado sobre la línea de la hoja."""
    pts = pares(o["linea"])
    obj = o["s0"] + s
    acum = 0.0
    for i in range(len(pts) - 1):
        d = dist(*pts[i], *pts[i + 1])
        if acum + d >= obj:
            t = (obj - acum) / d if d else 0
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t)
        acum += d
    return pts[-1]


por_id: dict = {}
resumen = {"ok": 0, "movido": 0, "x": 0, "no": 0}
movs = []
for n_txt, d in dec.items():
    n = int(n_txt)
    o = objetivos[n]
    if d in ("x", "no"):
        resumen[d] += 1
        continue
    if d == "ok":
        la, lo = o["la"], o["lo"]
        resumen["ok"] += 1
    elif d.startswith("f"):
        m = re.fullmatch(r"f(\d+)\+(\d+)", d)
        f = zoom[n]["fotos"][int(m.group(1))]
        la, lo = en_linea(o, f["s"] + int(m.group(2)))
        movs.append((o["clave"], round(dist(la, lo, o["la"], o["lo"]))))
        resumen["movido"] += 1
    else:
        m = re.fullmatch(r"h(\d+)(?:\+(\d+))?", d)
        idx, extra = int(m.group(1)), int(m.group(2) or 20)
        h = indices[n]["huecos"][idx]
        la, lo = en_linea(o, h["s"] + extra)
        movs.append((o["clave"], round(dist(la, lo, o["la"], o["lo"]))))
        resumen["movido"] += 1
    por_id.setdefault(o["id"], {})[o["ext"]] = (round(la, 6), round(lo, 6), d)

nuevos = 0
existentes = {v["id"] for v in ver["puntos"]}
for pid, exts in por_id.items():
    if pid in existentes:
        continue
    p = P[pid]
    e = {"id": pid, "t": p["t"], "f": p.get("f", "DGT")}
    ini = exts.get("ini")
    e["la"], e["lo"] = (ini[0], ini[1]) if ini else (p["la"], p["lo"])
    if p["t"] == "RADAR_TRAMO" and p.get("la2") is not None:
        fin = exts.get("fin")
        e["la2"], e["lo2"] = (fin[0], fin[1]) if fin else (p["la2"], p["lo2"])
        if not (ini and fin):
            e["px"] = 1   # un extremo sin comprobar: sigue siendo aproximado
    if p.get("rb") is not None:
        e["rb"] = p["rb"]
    e["tol"] = 30
    e["radio"] = 600
    e["motivo"] = "Situado con fotos de Mapillary (CC BY-SA) a lo largo de la vía: " + ", ".join(
        f"{k} {v[2]}" for k, v in sorted(exts.items()))
    ver["puntos"].append(e)
    nuevos += 1
json.dump(ver, open("verificados.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(resumen, "nuevos verificados:", nuevos)
movs.sort(key=lambda x: -x[1])
print("movidos (m):", movs[:40])
