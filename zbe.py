#!/usr/bin/env python3
"""
Zonas de bajas emisiones (ZBE) de España, de OpenStreetMap (boundary=low_emission_zone), para que la app avise antes
de entrar según la etiqueta ambiental del coche: datos/zbe.json. Cada zona:
  {"n": nombre, "w": web o "", "a": [[lon, lat, lon, lat, ...], ...]}  (anillos exteriores, 5 decimales)
Las normas (horarios, moratorias, qué etiquetas entran) cambian por ciudad y no están bien en OSM, así que la app solo
dice que es una ZBE y deja claro que hay que mirar las normas del ayuntamiento.
Datos © colaboradores de OpenStreetMap (ODbL).
"""
import sys
import time

import recolector as R

CONSULTA = """
[out:json][timeout:280];
area["ISO3166-1"="ES"]["admin_level"="2"]->.p;
(
  relation["boundary"="low_emission_zone"](area.p);
  way["boundary"="low_emission_zone"](area.p);
);
out tags geom;
"""


def unir(trozos: list[list[tuple[float, float]]]) -> list[list[tuple[float, float]]]:
    """Une las vías de un multipolígono en anillos cerrados (por sus extremos)."""
    trozos = [t[:] for t in trozos if len(t) >= 2]
    anillos = []
    while trozos:
        a = trozos.pop(0)
        cambio = True
        while a[0] != a[-1] and cambio:
            cambio = False
            for i, t in enumerate(trozos):
                if t[0] == a[-1]:
                    a += t[1:]
                elif t[-1] == a[-1]:
                    a += t[-2::-1]
                elif t[-1] == a[0]:
                    a = t[:-1] + a
                elif t[0] == a[0]:
                    a = t[:0:-1] + a
                else:
                    continue
                trozos.pop(i)
                cambio = True
                break
        if len(a) >= 4:
            anillos.append(a)
    return anillos


def plano(anillo) -> list[float]:
    out = []
    for la, lo in anillo:
        out += [round(lo, 5), round(la, 5)]
    return out


def main() -> int:
    d = R.overpass(CONSULTA)
    zonas = []
    for e in d.get("elements", []):
        t = e.get("tags") or {}
        nombre = t.get("name") or t.get("name:es") or "Zona de bajas emisiones"
        if e["type"] == "way":
            g = [(p["lat"], p["lon"]) for p in e.get("geometry", [])]
            anillos = [g] if len(g) >= 4 and g[0] == g[-1] else []
        else:
            trozos = [[(p["lat"], p["lon"]) for p in m.get("geometry", [])]
                      for m in e.get("members", []) if m.get("type") == "way" and m.get("role", "outer") in ("outer", "")]
            anillos = unir(trozos)
        if not anillos:
            print("sin anillos:", nombre, flush=True)
            continue
        zonas.append({"n": nombre[:80], "w": (t.get("website") or t.get("url") or "")[:200], "a": [plano(a) for a in anillos]})
        print(nombre, len(anillos), sum(len(a) for a in anillos), flush=True)
    print("zonas:", len(zonas), flush=True)
    if len(zonas) < 3:
        return 1
    R.guardar_json("datos/zbe.json", {"generado": time.strftime("%Y-%m-%d"), "zonas": zonas}, compacto=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
