#!/usr/bin/env python3
"""
Las autopistas de peaje de España con su precio, para saber lo que cuesta una ruta sin depender de nadie:
datos/peajes.json = las tarifas (peajes_tarifas.json, a mano cada año) + el trazado de cada una (las vías con
toll=yes de OpenStreetMap, simplificadas), asignado por referencia y caja:
  {"version": 1, "fuente": …, "tarifas": [...], "vias": [[i, [lat, lon, lat, lon, …]], …]}
con i el índice de la tarifa. Entrada: el GeoJSON por líneas de osmium (colegios.yml): las vías con toll=yes y, aparte, las autopistas (para las
tarifas «todas»).
Datos © colaboradores de OpenStreetMap (ODbL).
"""
import json
import math
import sys

CLASES = {"motorway", "trunk", "primary", "secondary", "tertiary"}


def simplificar(pts: list[tuple[float, float]], tol_m: float = 12.0) -> list[tuple[float, float]]:
    """Douglas-Peucker en metros (aprox. plana local)."""
    if len(pts) < 3:
        return pts
    la0 = pts[0][0]
    kx = 111_320 * math.cos(math.radians(la0))
    ky = 110_540
    xy = [((lo - pts[0][1]) * kx, (la - la0) * ky) for la, lo in pts]
    guardar = [False] * len(pts)
    guardar[0] = guardar[-1] = True
    pila = [(0, len(pts) - 1)]
    while pila:
        a, b = pila.pop()
        ax, ay = xy[a]
        bx, by = xy[b]
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy
        peor, k = -1.0, -1
        for i in range(a + 1, b):
            px, py = xy[i]
            if l2 == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
                d = math.hypot(px - ax - t * dx, py - ay - t * dy)
            if d > peor:
                peor, k = d, i
        if peor > tol_m:
            guardar[k] = True
            pila.append((a, k))
            pila.append((k, b))
    return [p for p, g in zip(pts, guardar) if g]


def dentro(caja, la, lo) -> bool:
    return caja[0] <= lo <= caja[2] and caja[1] <= la <= caja[3]


def main() -> int:
    tarifas = json.load(open("peajes_tarifas.json", encoding="utf-8"))
    lista = tarifas["tarifas"]
    vias = []
    sin = 0
    sueltas: dict[str, float] = {}
    def lineas():
        for ruta in sys.argv[1:]:
            yield from open(ruta, encoding="utf-8")
    for linea in lineas():
        linea = linea.strip().lstrip("\x1e")
        if not linea:
            continue
        f = json.loads(linea)
        p = f.get("properties") or {}
        if p.get("highway") not in CLASES:
            continue
        g = f.get("geometry") or {}
        if g.get("type") != "LineString":
            continue
        pts = [(c[1], c[0]) for c in g["coordinates"]]
        if len(pts) < 2:
            continue
        refs = {r.strip().replace(" ", "-") for r in (p.get("ref") or "").split(";") if r.strip()}
        mla, mlo = pts[len(pts) // 2]
        peaje = p.get("toll") == "yes"
        idx = next((i for i, t in enumerate(lista)
                    if (peaje or t.get("todas")) and dentro(t["caja"], mla, mlo)
                    and (t["ref"] is None or refs & set(t.get("refs") or [t["ref"]]))), None)
        if idx is None and not peaje:
            continue
        if idx is None:
            sin += 1
            largo = sum(math.hypot((pts[k + 1][0] - pts[k][0]) * 110.54, (pts[k + 1][1] - pts[k][1]) * 111.32 * math.cos(math.radians(pts[k][0])))
                        for k in range(len(pts) - 1))
            clave = (",".join(sorted(refs)) or p.get("name") or "?") + f" @{mla:.2f},{mlo:.2f}"[:12]
            sueltas[clave] = sueltas.get(clave, 0.0) + largo
            continue
        s = simplificar(pts)
        plano = []
        for la, lo in s:
            plano += [round(la, 5), round(lo, 5)]
        vias.append([idx, plano])
    out = {"version": 1, "fuente": tarifas.get("fuente"), "atribucion": "© colaboradores de OpenStreetMap",
           "tarifas": lista, "vias": vias}
    with open("datos/peajes.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
    usadas = {v[0] for v in vias}
    print("vías de peaje sin tarifa (las más largas; gratis ya o sin precio conocido):")
    for k, v in sorted(sueltas.items(), key=lambda x: -x[1])[:25]:
        print(f"  {k}: {v:.1f} km")
    print(f"vías de peaje: {len(vias)} (sin tarifa: {sin}); tarifas con trazado: {len(usadas)}/{len(lista)}")
    for i, t in enumerate(lista):
        if i not in usadas:
            print("  sin trazado:", t["id"])
    return 0 if len(usadas) >= len(lista) * 0.7 else 1


if __name__ == "__main__":
    sys.exit(main())
