#!/usr/bin/env python3
"""
Colegios y escuelas infantiles de España (OpenStreetMap: amenity=school / kindergarten), para el aviso de zona escolar
de la app en horario de clase: datos/colegios.json. Cada uno: [lat, lon, radio en m, nombre].
El radio sale del recinto (mitad de la diagonal de su caja, entre 40 y 250 m); si es un punto, 60 m.
Datos © colaboradores de OpenStreetMap (ODbL).
"""
import json
import math
import sys
import time

import recolector as R

# por provincias: por comunidades Overpass cortaba la respuesta (salían 236 en la Comunitat Valenciana)
REGIONES = ["ES-A", "ES-AB", "ES-AL", "ES-AV", "ES-B", "ES-BA", "ES-BI", "ES-BU", "ES-C", "ES-CA", "ES-CC", "ES-CO", "ES-CR",
            "ES-CS", "ES-CU", "ES-GC", "ES-GI", "ES-GR", "ES-GU", "ES-H", "ES-HU", "ES-J", "ES-L", "ES-LE", "ES-LO", "ES-LU",
            "ES-M", "ES-MA", "ES-MU", "ES-NA", "ES-O", "ES-OR", "ES-P", "ES-PM", "ES-PO", "ES-S", "ES-SA", "ES-SE", "ES-SG",
            "ES-SO", "ES-SS", "ES-T", "ES-TE", "ES-TF", "ES-TO", "ES-V", "ES-VA", "ES-VI", "ES-Z", "ES-ZA", "ES-CE", "ES-ML"]
NO_ESCUELA = ("autoescuela", "escuela de idiomas", "academia", "universidad", "conservatorio", "escuela de música",
              "escuela de musica", "escuela oficial de idiomas", "escuela de adultos")


def radio(e) -> float:
    b = e.get("bounds")
    if not b:
        return 60.0
    la = (b["minlat"] + b["maxlat"]) / 2
    dy = (b["maxlat"] - b["minlat"]) * 110540
    dx = (b["maxlon"] - b["minlon"]) * 111320 * math.cos(math.radians(la))
    return max(40.0, min(250.0, math.hypot(dx, dy) / 2))


def main() -> int:
    todos = []
    vistos = set()
    for reg in REGIONES:
        q = f"""
[out:json][timeout:600][maxsize:536870912];
area["ISO3166-2"="{reg}"]->.r;
nwr["amenity"~"^(school|kindergarten)$"](area.r);
out center bb tags;
"""
        try:
            d = R.overpass(q)
        except Exception as e:  # noqa: BLE001
            print(reg, "error", e, flush=True)
            continue
        if d.get("remark"):
            print(reg, "aviso de Overpass:", d["remark"][:200], flush=True)
        n = 0
        for e in d.get("elements", []):
            la = e.get("lat") or (e.get("center") or {}).get("lat")
            lo = e.get("lon") or (e.get("center") or {}).get("lon")
            if la is None:
                continue
            t = e.get("tags") or {}
            nombre = (t.get("name") or "").strip()
            if any(x in nombre.lower() for x in NO_ESCUELA):
                continue
            # el mismo colegio como punto y como recinto: uno
            clave = (round(la, 3), round(lo, 3), nombre[:20])
            if clave in vistos:
                continue
            vistos.add(clave)
            todos.append([round(la, 5), round(lo, 5), int(radio(e)), nombre[:60]])
            n += 1
        print(reg, n, flush=True)
        time.sleep(3)
    if len(todos) < 8000:
        print("Muy pocos colegios:", len(todos))
        return 1
    R.guardar_json("datos/colegios.json", {"generado": time.strftime("%Y-%m-%d"), "colegios": todos}, compacto=True)
    print("Total", len(todos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
