#!/usr/bin/env python3
"""
Hojas de fotos de Mapillary (CC BY-SA 4.0) para decidir a ojo el sentido de los radares dudosos (s2=1).

Para cada punto dudoso busca fotos recientes tomadas de 12 a 90 m antes del punto, mirando hacia él, y las
separa en los dos sentidos de la vía. Con dos fotos por sentido se ve en qué margen está la cabina: en
España va a la derecha del carril que vigila. Deja una hoja por punto en hojas/ y hojas/indice.json.
Necesita MAPILLARY_TOKEN. Uso: python sentidos_mapillary.py [DESDE_AÑO]
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

from PIL import Image, ImageDraw

API = "https://graph.mapillary.com/images"
CAMPOS = "id,captured_at,compass_angle,computed_compass_angle,computed_geometry,geometry,thumb_2048_url"


def pedir(url: str, binario: bool = False):
    for intento in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                d = r.read()
                return d if binario else json.loads(d.decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            if intento == 2:
                print(f"  fallo: {e}", flush=True)
            time.sleep(2 + 3 * intento)
    return None


def dist(la1, lo1, la2, lo2):
    x = (lo2 - lo1) * math.cos(math.radians((la1 + la2) / 2)) * 111320
    y = (la2 - la1) * 111320
    return math.hypot(x, y)


def rumbo(la1, lo1, la2, lo2):
    x = (lo2 - lo1) * math.cos(math.radians((la1 + la2) / 2))
    y = la2 - la1
    return math.degrees(math.atan2(x, y)) % 360


def dif(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def main() -> int:
    token = os.environ["MAPILLARY_TOKEN"]
    desde = int(sys.argv[1]) if len(sys.argv) > 1 else 2019
    datos = json.load(open("datos/radares.json"))
    puntos = datos["puntos"] if isinstance(datos, dict) else datos
    dudosos = [p for p in puntos if p.get("s2")]
    print(f"{len(dudosos)} dudosos", flush=True)
    os.makedirs("hojas", exist_ok=True)
    indice = []
    for n, p in enumerate(dudosos):
        la, lo = p["la"], p["lo"]
        r = 110.0
        dla, dlo = r / 111320.0, r / (111320.0 * math.cos(math.radians(la)))
        q = urllib.parse.urlencode({"access_token": token, "fields": CAMPOS, "limit": 2000,
                                    "bbox": f"{lo - dlo:.6f},{la - dla:.6f},{lo + dlo:.6f},{la + dla:.6f}"})
        fotos = (pedir(f"{API}?{q}") or {}).get("data", [])
        cand = []
        for f in fotos:
            g = (f.get("computed_geometry") or f.get("geometry") or {}).get("coordinates")
            if not g or not f.get("thumb_2048_url"):
                continue
            ano = time.gmtime((f.get("captured_at") or 0) / 1000).tm_year
            if ano < desde:
                continue
            h = f.get("computed_compass_angle", f.get("compass_angle"))
            if h is None:
                continue
            d = dist(g[1], g[0], la, lo)
            if not 12 <= d <= 90 or dif(h, rumbo(g[1], g[0], la, lo)) > 22:
                continue
            cand.append({"f": f, "la": g[1], "lo": g[0], "h": h, "d": d, "ano": ano,
                         "fecha": time.strftime("%Y-%m-%d", time.gmtime(f["captured_at"] / 1000))})
        # dos sentidos: el de rb (o el de la primera foto) y el contrario
        base = p.get("rb")
        if base is None and cand:
            base = cand[0]["h"]
        grupos = {"A": [], "B": []}
        for c in cand:
            if dif(c["h"], base) <= 60:
                grupos["A"].append(c)
            elif dif(c["h"], (base + 180) % 360) <= 60:
                grupos["B"].append(c)
        filas, meta = [], {}
        for k in ("A", "B"):
            g = sorted(grupos[k], key=lambda c: (-c["ano"], abs(c["d"] - 40)))
            elegidas, usadas = [], set()
            for c in g:   # una por distancia aproximada, para no repetir la misma foto
                clave = round(c["d"] / 20)
                if clave in usadas:
                    continue
                usadas.add(clave)
                elegidas.append(c)
                if len(elegidas) == 2:
                    break
            imgs = []
            for c in elegidas:
                b = pedir(c["f"]["thumb_2048_url"], binario=True)
                if not b:
                    continue
                im = Image.open(io.BytesIO(b)).convert("RGB")
                w, h = im.size
                im = im.crop((0, int(h * 0.1), w, int(h * 0.68)))
                im = im.resize((900, int(900 * im.height / im.width)))
                dr = ImageDraw.Draw(im)
                txt = f"{k} rumbo {c['h']:.0f}  a {c['d']:.0f} m  {c['fecha']}  id {c['f']['id']}"
                dr.rectangle([0, 0, 9 * len(txt) + 10, 22], fill=(0, 0, 0))
                dr.text((5, 5), txt, fill=(255, 255, 0))
                imgs.append(im)
            if imgs:
                filas.append(imgs)
                meta[k] = [{"id": c["f"]["id"], "rumbo": round(c["h"]), "d": round(c["d"]), "fecha": c["fecha"]}
                           for c in elegidas]
        reg = {"n": n, "id": p["id"], "t": p["t"], "la": la, "lo": lo, "rb": p.get("rb"), "c": p.get("c"),
               "nombre": p.get("n"), "fotos": meta, "total_cerca": len(cand)}
        if filas:
            alto = max(i.height for f in filas for i in f)
            hoja = Image.new("RGB", (1800, alto * len(filas) + 30), "white")
            dr = ImageDraw.Draw(hoja)
            dr.text((5, 8), f"{p['id']}  rb={p.get('rb')}  {(p.get('n') or p.get('c') or '')[:150]}", fill=(0, 0, 0))
            for i, fila in enumerate(filas):
                for j, im in enumerate(fila):
                    hoja.paste(im, (j * 900, 30 + i * alto))
            nombre = f"{n:03d}_{p['id'].replace(':', '_').replace(',', '_')}.jpg"
            hoja.save(os.path.join("hojas", nombre), quality=82)
            reg["hoja"] = nombre
        indice.append(reg)
        print(f"{n:3d} {p['id']}: {len(cand)} fotos cerca, sentidos {list(meta)}", flush=True)
    json.dump(indice, open("hojas/indice.json", "w"), ensure_ascii=False, indent=1)
    print(f"con fotos: {sum(1 for r in indice if r.get('hoja'))} · en los dos sentidos: "
          f"{sum(1 for r in indice if len(r['fotos']) == 2)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
