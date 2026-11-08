#!/usr/bin/env python3
"""Vías de la red en bruto (red/vias.geojsonseq) cerca de unos puntos, sin filtros: para ver qué hay de verdad."""
import json
import math
import sys

PUNTOS = {
    "Somport AP4": (42.75790, -0.52598), "Somport AP2": (42.78251, -0.54176), "GR-30 16.2": (37.12174, -3.75781),
    "CV-10 55.9": (40.26040, -0.07783), "C-31 Garraf": (41.21220, 1.75249), "A-42 55.7": (39.98639, -3.86466),
    "N-234 119.7": (40.33313, -1.11474), "H-30 8.5": (37.28582, -6.94108),
}


def dist_seg(p, a, b):
    kx = 111320 * math.cos(math.radians(p[0]))
    ax, ay = (a[1] - p[1]) * kx, (a[0] - p[0]) * 111320
    bx, by = (b[1] - p[1]) * kx, (b[0] - p[0]) * 111320
    dx, dy = bx - ax, by - ay
    t = 0 if dx == dy == 0 else max(0, min(1, -(ax * dx + ay * dy) / (dx * dx + dy * dy)))
    return math.hypot(ax + t * dx, ay + t * dy)


res = {k: [] for k in PUNTOS}
for linea in open(sys.argv[1] if len(sys.argv) > 1 else "red/vias.geojsonseq", encoding="utf-8"):
    linea = linea.strip().lstrip("\x1e")
    if not linea:
        continue
    ft = json.loads(linea)
    c = ft["geometry"]["coordinates"]
    las = [x[1] for x in c]; los = [x[0] for x in c]
    for k, p in PUNTOS.items():
        if min(las) - 0.02 > p[0] or max(las) + 0.02 < p[0] or min(los) - 0.03 > p[1] or max(los) + 0.03 < p[1]:
            continue
        d = min(dist_seg(p, (a[1], a[0]), (b[1], b[0])) for a, b in zip(c, c[1:]))
        if d < 1500:
            res[k].append((round(d), len(c), ft.get("properties")))
for k, v in res.items():
    print(f"== {k} {PUNTOS[k]}")
    for x in sorted(v, key=lambda x: x[0])[:8]:
        print("  ", x)
