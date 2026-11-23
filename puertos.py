#!/usr/bin/env python3
"""
Puertos de montaña de España en carretera (OpenStreetMap: nodos mountain_pass=yes que forman parte de una vía para
coches), para avisar de nieve y cadenas al cruzarlos: datos/puertos.json, «puertos»: [[lat, lon, nombre, altitud], …]
(nombre y altitud pueden ser null). Entrada: el GeoJSON por líneas de osmium (colegios.yml).
Datos © colaboradores de OpenStreetMap (ODbL).
"""
import json
import math
import re
import sys


def altitud(v) -> int | None:
    if not v:
        return None
    m = re.match(r"\s*(-?\d+(?:[.,]\d+)?)", str(v))
    if not m:
        return None
    a = float(m.group(1).replace(",", "."))
    if "ft" in str(v):
        a *= 0.3048
    return int(round(a)) if -50 < a < 4000 else None


def main() -> int:
    puertos = []
    for linea in open(sys.argv[1], encoding="utf-8"):
        linea = linea.strip().lstrip("\x1e")
        if not linea:
            continue
        f = json.loads(linea)
        g = f.get("geometry") or {}
        if g.get("type") != "Point":
            continue
        p = f.get("properties") or {}
        if p.get("mountain_pass") != "yes":
            continue
        lon, lat = g["coordinates"]
        nombre = (p.get("name:es") or p.get("name") or "").strip() or None
        # los túneles marcados como puerto (el del Cadí…) no son un puerto que se cruce por arriba
        if nombre and nombre.lower().startswith(("túnel", "tunel", "túnels", "tunnel")):
            continue
        ele = altitud(p.get("ele"))
        # un collado sin nombre ni altura en una calle no ayuda a nadie
        if nombre is None and (ele is None or ele < 500):
            continue
        puertos.append([round(lat, 5), round(lon, 5), nombre, ele])
    # el mismo puerto marcado dos veces (una por calzada): uno
    puertos.sort(key=lambda x: (x[2] or "", x[0], x[1]))
    out = []
    for p in puertos:
        if out and out[-1][2] == p[2] and p[2] is not None:
            q = out[-1]
            d = math.hypot((p[0] - q[0]) * 111_000, (p[1] - q[1]) * 111_000 * math.cos(math.radians(p[0])))
            if d < 1500:
                if q[3] is None:
                    q[3] = p[3]
                continue
        out.append(p)
    out.sort(key=lambda x: (x[0], x[1]))
    with open("datos/puertos.json", "w", encoding="utf-8") as fh:
        json.dump({"version": 1, "atribucion": "© colaboradores de OpenStreetMap", "puertos": out}, fh, ensure_ascii=False, separators=(",", ":"))
    print(f"puertos: {len(out)} (con nombre: {sum(1 for p in out if p[2])}, con altitud: {sum(1 for p in out if p[3])})")
    return 0 if len(out) > 100 else 1


if __name__ == "__main__":
    sys.exit(main())
