#!/usr/bin/env python3
"""
Hojas de posición (Mapillary, CC BY-SA 4.0) para situar a ojo los puntos de posición dudosa.

Para cada objetivo (depurar/objetivos_posicion.json: una línea por donde se circula hacia el punto, con el
punto estimado en s = 0) busca fotos tomadas sobre esa línea, mirando en el sentido de la marcha, y elige una
cada 40 m desde 400 m antes hasta 240 m después. En la hoja, la foto en la que la cabina o el pórtico aparece
justo a punto de pasar dice dónde está de verdad (la posición de esa foto + unos metros).

  python posiciones_mapillary.py preparar   → depurar/objetivos_posicion.json (desde datos/radares.json)
  python posiciones_mapillary.py hojas      → hojas_pos/*.jpg + hojas_pos/indice.json (necesita MAPILLARY_TOKEN)
"""
from __future__ import annotations

import io
import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

API = "https://graph.mapillary.com/images"
CAMPOS = "id,captured_at,computed_compass_angle,compass_angle,computed_geometry,geometry,thumb_1024_url,thumb_2048_url,camera_type"
OBJETIVOS = "depurar/objetivos_posicion.json"
ATRAS, DELANTE, PASO = 400.0, 240.0, 40.0


def dist(la1, lo1, la2, lo2):
    x = (lo2 - lo1) * math.cos(math.radians((la1 + la2) / 2)) * 111320
    y = (la2 - la1) * 111320
    return math.hypot(x, y)


def rumbo(la1, lo1, la2, lo2):
    x = (lo2 - lo1) * math.cos(math.radians((la1 + la2) / 2))
    return math.degrees(math.atan2(x, la2 - la1)) % 360


def dif(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def avanzar(la, lo, rb, m):
    return (la + m * math.cos(math.radians(rb)) / 111320,
            lo + m * math.sin(math.radians(rb)) / (111320 * math.cos(math.radians(la))))


def pares(flat):
    return [(flat[i], flat[i + 1]) for i in range(0, len(flat) - 1, 2)]


def recortar_atras(pts, m):
    """Los últimos m metros de una polilínea."""
    out, acum = [pts[-1]], 0.0
    for i in range(len(pts) - 1, 0, -1):
        d = dist(*pts[i - 1], *pts[i])
        out.append(pts[i - 1])
        acum += d
        if acum >= m:
            break
    return out[::-1]


def recortar_delante(pts, m):
    out, acum = [pts[0]], 0.0
    for i in range(1, len(pts)):
        acum += dist(*pts[i - 1], *pts[i])
        out.append(pts[i])
        if acum >= m:
            break
    return out


def linea_de(atras, delante):
    """atras termina en el punto, delante empieza en él; devuelve (línea, longitud hasta el punto)."""
    if len(delante) < 2:
        a, b = atras[-2], atras[-1]
        rb = rumbo(*a, *b)
        delante = [atras[-1], avanzar(*atras[-1], rb, DELANTE)]
    linea = atras + delante[1:]
    s0 = sum(dist(*atras[i], *atras[i + 1]) for i in range(len(atras) - 1))
    return linea, s0


def preparar(ruta="datos/radares.json", extra_ids=()):
    P = json.load(open(ruta, encoding="utf-8"))["puntos"]
    objetivos = []
    for p in P:
        if not (p.get("px") or p["id"] in extra_ids):
            continue
        extremos = [("ini", p["la"], p["lo"])]
        if p["t"] == "RADAR_TRAMO" and p.get("la2") is not None:
            extremos.append(("fin", p["la2"], p["lo2"]))
        for ext, la, lo in extremos:
            rt = pares(p["rt"]) if p.get("rt") else None
            if ext == "ini":
                if p.get("ap"):
                    atras = recortar_atras(pares(max(p["ap"], key=len)), ATRAS + 60)
                elif p.get("rb") is not None:
                    atras = [avanzar(la, lo, (p["rb"] + 180) % 360, ATRAS + 60), (la, lo)]
                else:
                    continue
                atras[-1] = (la, lo)
                delante = recortar_delante(rt, DELANTE) if rt else []
            else:
                if rt:
                    atras = recortar_atras(rt, ATRAS + 60)
                else:
                    atras = [(p["la"], p["lo"])]
                    rb0 = rumbo(p["la"], p["lo"], la, lo)
                    atras = [avanzar(la, lo, (rb0 + 180) % 360, ATRAS + 60)]
                atras.append((la, lo))
                delante = []
            if len(atras) < 2:
                continue
            linea, s0 = linea_de(atras, delante)
            objetivos.append({
                "clave": f"{p['id']}|{ext}", "id": p["id"], "ext": ext, "t": p["t"], "la": la, "lo": lo,
                "rb": p.get("rb"), "c": p.get("c"), "pk": p.get("pk2") if ext == "fin" else p.get("pk"),
                "mu": p.get("mu"), "v": p.get("v"), "nombre": p.get("n"),
                "linea": [round(x, 6) for q in linea for x in q], "s0": round(s0, 1),
            })
    orden = {"RADAR_FIJO": 0, "RADAR_TRAMO": 1, "SEMAFORO": 2, "STOP_CEDA": 3, "OTRA_CAMARA": 4}
    objetivos.sort(key=lambda o: (orden.get(o["t"], 9), o["id"], o["ext"]))
    os.makedirs("depurar", exist_ok=True)
    json.dump(objetivos, open(OBJETIVOS, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(objetivos)} objetivos")


def pedir(url, binario=False):
    for intento in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                d = r.read()
                return d if binario else json.loads(d.decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            if intento == 2:
                print(f"  fallo: {str(e)[:120]}", flush=True)
            time.sleep(2 + 3 * intento)
    return None


def proyectar(la, lo, linea):
    """(s a lo largo de la línea, distancia lateral, rumbo del segmento)."""
    mejor, acum = None, 0.0
    for i in range(len(linea) - 1):
        a, b = linea[i], linea[i + 1]
        kx = math.cos(math.radians(a[0])) * 111320
        ax, ay, bx, by = a[1] * kx, a[0] * 111320, b[1] * kx, b[0] * 111320
        px, py = lo * kx, la * 111320
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
        d = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
        L = math.sqrt(L2)
        if mejor is None or d < mejor[1]:
            mejor = (acum + t * L, d, rumbo(*a, *b))
        acum += L
    return mejor


def fotos_de(token, o, todas=False):
    linea = pares(o["linea"])
    # consultas pequeñas a lo largo de la línea (una grande se queda en el límite de 2000 en ciudad)
    trozos, acum, ult = [linea[0]], 0.0, linea[0]
    for q in linea[1:]:
        acum += dist(*ult, *q)
        ult = q
        if acum >= 120:
            trozos.append(q)
            acum = 0.0
    trozos.append(linea[-1])
    vistas, fotos = set(), []
    for i in range(len(trozos) - 1):
        a, b = trozos[i], trozos[i + 1]
        m = 30 / 111320
        la0, la1 = min(a[0], b[0]) - m, max(a[0], b[0]) + m
        mlo = m / math.cos(math.radians(a[0]))
        lo0, lo1 = min(a[1], b[1]) - mlo, max(a[1], b[1]) + mlo
        q = urllib.parse.urlencode({"access_token": token, "fields": CAMPOS, "limit": 2000,
                                    "bbox": f"{lo0:.6f},{la0:.6f},{lo1:.6f},{la1:.6f}"})
        for f in (pedir(f"{API}?{q}") or {}).get("data", []):
            if f["id"] not in vistas:
                vistas.add(f["id"])
                fotos.append(f)
    cand = []
    for f in fotos:
        g = (f.get("computed_geometry") or f.get("geometry") or {}).get("coordinates")
        h = f.get("computed_compass_angle", f.get("compass_angle"))
        if not g or h is None or not f.get("thumb_1024_url"):
            continue
        s, d, rs = proyectar(g[1], g[0], linea)
        s -= o["s0"]
        if d > 18 or not -ATRAS - 20 <= s <= DELANTE or dif(h, rs) > 30:
            continue
        esf = f.get("camera_type") not in (None, "perspective", "fisheye")
        cand.append({"id": f["id"], "url": f["thumb_1024_url"], "url2": f.get("thumb_2048_url"), "la": g[1], "lo": g[0], "s": s, "d": d,
                     "h": h, "esf": esf, "ms": f.get("captured_at") or 0})
    if todas:
        return cand, len(cand)
    # una por tramo de 40 m: la más reciente que no sea 360º (mejor si va centrada en el carril)
    elegidas = []
    k = -ATRAS
    while k < DELANTE:
        en = [c for c in cand if k <= c["s"] < k + PASO]
        if en:
            en.sort(key=lambda c: (c["esf"], -(c["ms"] // (180 * 86400_000)), c["d"]))
            elegidas.append(en[0])
        else:
            elegidas.append(None)
        k += PASO
    return elegidas, len(cand)


def zoom():
    """Validación / detalle: 3 fotos a 2048 px de los 110-20 m antes del punto, en una franja ancha."""
    from PIL import Image, ImageDraw
    token = os.environ["MAPILLARY_TOKEN"]
    objetivos = json.load(open(OBJETIVOS, encoding="utf-8"))
    desde, hasta = int(os.environ.get("DESDE", "0")), int(os.environ.get("HASTA", "100000"))
    os.makedirs("hojas_pos", exist_ok=True)
    indice = []
    for n, o in enumerate(objetivos):
        ns = set(map(int, os.environ.get("NS", "").split()))
        if n < desde or n >= hasta or (ns and n not in ns):
            continue
        elegidas, total = fotos_de(token, o, todas=True)
        # todas las candidatas, no solo una por hueco: se reconsulta con huecos de 30 m entre -110 y -20
        todas = [c for c in elegidas if not c["esf"] and c.get("url2")]
        offs = [float(x) for x in os.environ.get("OFFS", "-125,-70,-15").split(",")]
        cand, usadas = [], set()
        for off in offs:   # la foto más reciente a ±25 m de cada distancia pedida
            cerca = [c for c in todas if abs(c["s"] - off) <= 25 and c["id"] not in usadas]
            if cerca:
                c = max(cerca, key=lambda c: (c["ms"] // (90 * 86400_000), -abs(c["s"] - off)))
                usadas.add(c["id"])
                cand.append(c)
        ims = []
        for c in cand:
            b = pedir(c["url2"], binario=True)
            if not b:
                continue
            im = Image.open(io.BytesIO(b)).convert("RGB")
            w, h = im.size
            im = im.crop((0, int(h * 0.22), w, int(h * 0.72))).resize((1600, int(1600 * h * 0.5 / w)))
            d = ImageDraw.Draw(im)
            et = f"#{n} s={int(round(c['s'])):+d} m {time.strftime('%Y-%m', time.gmtime(c['ms'] / 1000))} {o['id']}"
            d.rectangle([0, 0, 10 + 7 * len(et), 18], fill=(0, 0, 0))
            d.text((4, 4), et, fill=(255, 255, 0))
            ims.append(im)
        reg = {"n": n, "clave": o["clave"], "fotos": [{"id": c["id"], "s": round(c["s"]), "la": round(c["la"], 6), "lo": round(c["lo"], 6)} for c in cand]}
        if ims:
            hoja = Image.new("RGB", (1600, sum(i.height for i in ims)), "white")
            y = 0
            for i in ims:
                hoja.paste(i, (0, y))
                y += i.height
            hoja.save(os.path.join("hojas_pos", f"z{n:03d}.jpg"), quality=78)
            reg["hoja"] = f"z{n:03d}.jpg"
        indice.append(reg)
    json.dump(indice, open("hojas_pos/indice_zoom.json", "w", encoding="utf-8"), ensure_ascii=False)


def hojas():
    from PIL import Image, ImageDraw
    token = os.environ["MAPILLARY_TOKEN"]
    objetivos = json.load(open(OBJETIVOS, encoding="utf-8"))
    solo = set(filter(None, os.environ.get("SOLO", "").split()))
    desde, hasta = int(os.environ.get("DESDE", "0")), int(os.environ.get("HASTA", "100000"))
    os.makedirs("hojas_pos", exist_ok=True)
    indice = []
    W, H = 400, 300
    t0 = time.time()

    def preparar_foto(c):
        if c is None:
            return None
        b = pedir(c["url"], binario=True)
        if not b:
            return None
        im = Image.open(io.BytesIO(b)).convert("RGB")
        w, h = im.size
        if c["esf"]:   # 360º: el trozo que mira hacia delante
            im = im.crop((int(w * 0.375), int(h * 0.3), int(w * 0.625), int(h * 0.6)))
            return im.resize((W, H))
        # la foto entera (hay móviles que apuntan al cielo y otros al capó): encajada sin deformar
        lienzo = Image.new("RGB", (W, H), (30, 30, 30))
        im.thumbnail((W, H))
        lienzo.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
        return lienzo

    for n, o in enumerate(objetivos):
        if n < desde or n >= hasta or (solo and o["id"] not in solo):
            continue
        elegidas, total = fotos_de(token, o)
        with ThreadPoolExecutor(8) as ex:
            ims = list(ex.map(preparar_foto, elegidas))
        reg = {k: o[k] for k in ("clave", "id", "ext", "t", "la", "lo", "rb", "c", "pk", "mu", "v", "nombre")}
        reg["n"], reg["fotos_linea"] = n, total
        reg["huecos"] = [None if c is None else {"id": c["id"], "s": round(c["s"]), "la": round(c["la"], 6),
                                                 "lo": round(c["lo"], 6), "h": round(c["h"]),
                                                 "fecha": time.strftime("%Y-%m", time.gmtime(c["ms"] / 1000))}
                         for c in elegidas]
        if any(ims):
            cols = 4
            filas = math.ceil(len(ims) / cols)
            hoja = Image.new("RGB", (W * cols, 34 + H * filas), "white")
            dr = ImageDraw.Draw(hoja)
            tit = (f"#{n} {o['id']} [{o['ext']}] {o['t']} {o.get('c') or ''} pk {o.get('pk')} "
                   f"{o.get('mu') or ''} v{o.get('v') or ''}  {(o.get('nombre') or '')[:60]}")
            dr.text((6, 10), tit, fill=(0, 0, 0))
            for i, (im, c) in enumerate(zip(ims, elegidas)):
                x, y = (i % cols) * W, 34 + (i // cols) * H
                k = -ATRAS + i * PASO
                if im is not None:
                    hoja.paste(im, (x, y))
                else:
                    dr.rectangle([x, y, x + W - 1, y + H - 1], fill=(60, 60, 60))
                cero = k <= 0 < k + PASO
                et = f"{i:02d} s={int(round(c['s'] if c else k)):+d} m" + (f" {time.strftime('%Y-%m', time.gmtime(c['ms'] / 1000))}" if c else " (sin foto)")
                dr.rectangle([x, y, x + 9 + 7 * len(et), y + 18], fill=(200, 0, 0) if cero else (0, 0, 0))
                dr.text((x + 4, y + 4), et, fill=(255, 255, 0))
                if cero:
                    dr.rectangle([x, y, x + W - 1, y + H - 1], outline=(255, 0, 0), width=4)
            nombre = f"{n:03d}.jpg"
            hoja.save(os.path.join("hojas_pos", nombre), quality=72)
            reg["hoja"] = nombre
        indice.append(reg)
        if n % 10 == 0:
            print(f"{n} {o['clave']}: {total} fotos en la línea, {sum(1 for c in elegidas if c)} huecos con foto "
                  f"({time.time() - t0:.0f}s)", flush=True)
    json.dump(indice, open("hojas_pos/indice.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"hojas: {sum(1 for r in indice if r.get('hoja'))} de {len(indice)}", flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["preparar"]:
        extra = open(sys.argv[2], encoding="utf-8").read().splitlines() if len(sys.argv) > 2 else []
        preparar(extra_ids=tuple(x.strip() for x in extra if x.strip()))
    elif sys.argv[1:2] == ["zoom"]:
        zoom()
    else:
        hojas()
