#!/usr/bin/env python3
"""
Red viaria compacta para la app (versión 3): saber por qué carretera vas y su límite de velocidad.

Lee red/vias.geojsonseq (OpenStreetMap vía Geofabrik, ver recolectar.yml) y escribe teselas de 0,25° en
datos/red/<fila>_<columna>.bin (binario comprimido con gzip) y datos/red/indice.json.

Formato de cada tesela (todo en enteros "varint" sin signo; los con signo, en zigzag):
  "ATR1"
  nº de textos, y cada texto: longitud + UTF-8           (referencias de carretera: "A-7", "CV-35"...)
  nº de vías, y cada vía:
    clase (0-13, ver CLASES) | 16 si sentido único | 32 si túnel | 64 si glorieta
    límite en el sentido del dibujo (km/h; 0 = sin dato)
    límite en el sentido contrario (km/h; 0 = sin dato)
    origen del límite: 0 sin dato, 1 señal (maxspeed numérico), 2 por tipo de zona (ES:urban, ES:rural...)
    referencia: 0 = ninguna, si no índice + 1 en la tabla de textos
    nº de puntos; el primero en 1e-5 grados relativo a la esquina SO de la tesela; los demás, diferencia con el
    anterior (zigzag)
Los vértices que comparten dos o más vías (cruces) no se quitan al simplificar: la app los usa para saber qué
vías se tocan.
"""
import gzip
import hashlib
import json
import math
import os
import sys
from collections import defaultdict

ENTRADA = "red/vias.geojsonseq"
SALIDA = "datos/red"
TAM = 0.25           # grados por tesela
TOL_M = 2.5          # simplificación (Douglas-Peucker), metros
CLASES = ["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary",
          "secondary_link", "tertiary", "tertiary_link", "unclassified", "residential", "living_street", "road"]

# Límites por tipo de zona (etiqueta maxspeed=XX:yyy o maxspeed:type / source:maxspeed)
ZONAS = {
    "ES:urban": 50, "ES:rural": 90, "ES:motorway": 120, "ES:trunk": 120, "ES:zone30": 30, "ES:zone20": 20,
    "ES:living_street": 20, "ES:zone10": 10,
    "PT:urban": 50, "PT:rural": 90, "PT:motorway": 120, "PT:trunk": 100,
}


def a_kmh(v):
    """'50' → (50, 1); 'ES:urban' → (50, 2); '30 mph' → km/h; 'none'/'walk'/basura → (0, 0)."""
    if not v:
        return 0, 0
    v = v.strip().split(";")[0].strip()
    if v in ZONAS:
        return ZONAS[v], 2
    try:
        if v.endswith("mph"):
            return round(float(v[:-3]) * 1.609), 1
        n = int(float(v))
        return (n, 1) if 5 <= n <= 150 else (0, 0)
    except ValueError:
        return 0, 0


def limites(p):
    base, org = a_kmh(p.get("maxspeed"))
    if not base:
        for k in ("maxspeed:type", "source:maxspeed", "zone:maxspeed"):
            base, org = a_kmh(p.get(k))
            if base:
                org = 2
                break
    fw, o1 = a_kmh(p.get("maxspeed:forward"))
    bw, o2 = a_kmh(p.get("maxspeed:backward"))
    adelante = fw or base
    atras = bw or base
    origen = 1 if (o1 == 1 or o2 == 1 or org == 1) else (2 if (adelante or atras) else 0)
    return adelante, atras, origen


def zz(n):
    return (n << 1) ^ (n >> 63)


def varint(n, out):
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return


def dp(pts, fijos, tol):
    """Douglas-Peucker en metros sobre (lat, lon) en 1e-5 grados; no quita los índices de [fijos]."""
    if len(pts) <= 2:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    for i in fijos:
        keep[i] = True
    ky = 1.1132
    kx = 1.1132 * math.cos(math.radians(pts[0][0] / 1e5))
    tramos = [i for i, k in enumerate(keep) if k]
    pila = list(zip(tramos, tramos[1:]))
    while pila:
        a, b = pila.pop()
        if b - a < 2:
            continue
        ay, ax = pts[a][0] * ky, pts[a][1] * kx
        by, bx = pts[b][0] * ky, pts[b][1] * kx
        dy, dx = by - ay, bx - ax
        l2 = dx * dx + dy * dy
        peor, ip = -1.0, -1
        for i in range(a + 1, b):
            py, px = pts[i][0] * ky, pts[i][1] * kx
            if l2 == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
                d = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
            if d > peor:
                peor, ip = d, i
        if peor > tol:
            keep[ip] = True
            pila.append((a, ip))
            pila.append((ip, b))
    return [p for p, k in zip(pts, keep) if k]


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else ENTRADA
    salida = sys.argv[2] if len(sys.argv) > 2 else SALIDA
    if not os.path.exists(ruta):
        print("sin red viaria; no se genera la red compacta")
        return
    # 1ª pasada: cuántas vías usan cada vértice (los cruces no se simplifican)
    usos = defaultdict(int)
    n = 0
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            g = json.loads(linea)
            cs = g["geometry"]["coordinates"]
            vistos = set()
            for x, y in cs:
                k = (round(y * 1e5), round(x * 1e5))
                if k not in vistos:
                    vistos.add(k)
                    usos[k] += 1
            n += 1
    cruces = {k for k, v in usos.items() if v >= 2}
    del usos
    print(f"{n} vías, {len(cruces)} cruces", flush=True)

    teselas = defaultdict(list)   # (fila, col) → [(flags, v1, v2, origen, ref, pts)]
    puntos_tot = 0
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            g = json.loads(linea)
            p = g["properties"]
            clase = p.get("highway")
            if clase not in CLASES:
                continue
            pts = []
            for x, y in g["geometry"]["coordinates"]:
                q = (round(y * 1e5), round(x * 1e5))
                if not pts or pts[-1] != q:
                    pts.append(q)
            if len(pts) < 2:
                continue
            ow = p.get("oneway")
            unico = ow in ("yes", "true", "1", "-1") or p.get("junction") in ("roundabout", "circular") or clase == "motorway"
            v1, v2, origen = limites(p)
            if ow == "-1":
                pts.reverse()
                v1, v2 = v2, v1
            fijos = [i for i, q in enumerate(pts) if q in cruces]
            pts = dp(pts, fijos, TOL_M)
            puntos_tot += len(pts)
            flags = CLASES.index(clase) | (16 if unico else 0) | (32 if p.get("tunnel") in ("yes", "building_passage", "avalanche_protector") else 0) \
                | (64 if p.get("junction") in ("roundabout", "circular") else 0)
            ref = (p.get("ref") or "").split(";")[0].strip()[:20]
            lat = [q[0] for q in pts]
            lon = [q[1] for q in pts]
            f0, f1 = math.floor(min(lat) / 1e5 / TAM), math.floor(max(lat) / 1e5 / TAM)
            c0, c1 = math.floor(min(lon) / 1e5 / TAM), math.floor(max(lon) / 1e5 / TAM)
            for fi in range(f0, f1 + 1):
                for co in range(c0, c1 + 1):
                    teselas[(fi, co)].append((flags, v1, v2, origen, ref, pts))
    os.makedirs(salida, exist_ok=True)
    for viejo in os.listdir(salida):
        if viejo.endswith(".bin"):
            os.remove(os.path.join(salida, viejo))
    indice = {}
    total = 0
    for (fi, co), vias in sorted(teselas.items()):
        out = bytearray(b"ATR1")
        refs = sorted({v[4] for v in vias if v[4]})
        pos = {r: i + 1 for i, r in enumerate(refs)}
        varint(len(refs), out)
        for r in refs:
            b = r.encode("utf-8")
            varint(len(b), out)
            out += b
        varint(len(vias), out)
        oy, ox = round(fi * TAM * 1e5), round(co * TAM * 1e5)
        for flags, v1, v2, origen, ref, pts in vias:
            varint(flags, out)
            varint(v1, out)
            varint(v2, out)
            varint(origen, out)
            varint(pos.get(ref, 0), out)
            varint(len(pts), out)
            py, px = oy, ox
            for y, x in pts:
                varint(zz(y - py), out)
                varint(zz(x - px), out)
                py, px = y, x
        nombre = f"{fi}_{co}.bin"
        datos = gzip.compress(bytes(out), 9, mtime=0)
        with open(os.path.join(salida, nombre), "wb") as g:
            g.write(datos)
        indice[f"{fi}_{co}"] = {"b": len(datos), "v": len(vias), "h": hashlib.sha1(datos).hexdigest()[:12]}
        total += len(datos)
    json.dump({"version": 1, "tam": TAM, "teselas": indice}, open(os.path.join(salida, "indice.json"), "w"),
              separators=(",", ":"), sort_keys=True)
    print(f"{len(indice)} teselas, {puntos_tot} puntos, {total / 1e6:.1f} MB", flush=True)


if __name__ == "__main__":
    main()
