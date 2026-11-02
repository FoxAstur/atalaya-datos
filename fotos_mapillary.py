#!/usr/bin/env python3
"""
Fotos de calle de Mapillary (licencia CC BY-SA) alrededor de un punto, para comprobar a ojo dónde está una
cabina o hacia dónde mira. Uso: python fotos_mapillary.py LAT LON [RADIO_M] [MAX]. Deja las fotos en
fotos/ con nombre fecha_lat_lon_rumbo.jpg y un indice.json. Necesita MAPILLARY_TOKEN.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://graph.mapillary.com/images"
TAM = os.environ.get("TAM", "1024")          # 1024, 2048 u original
DESDE = int(os.environ.get("DESDE", "0"))    # año mínimo de las fotos
URL = "thumb_original_url" if TAM == "original" else f"thumb_{TAM}_url"
CAMPOS = "id,captured_at,compass_angle,computed_compass_angle,computed_geometry,geometry,sequence," + URL


def pedir(url: str, binario: bool = False):
    for intento in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                datos = r.read()
                return datos if binario else json.loads(datos.decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            if intento == 2:
                print(f"  fallo {url[:80]}: {e}", flush=True)
            time.sleep(2 + 3 * intento)
    return None


def main() -> int:
    token = os.environ["MAPILLARY_TOKEN"]
    la, lo = float(sys.argv[1]), float(sys.argv[2])
    radio = float(sys.argv[3]) if len(sys.argv) > 3 else 150.0
    maximo = int(sys.argv[4]) if len(sys.argv) > 4 else 80
    dla = radio / 111320.0
    dlo = radio / (111320.0 * math.cos(math.radians(la)))
    q = urllib.parse.urlencode({
        "access_token": token, "fields": CAMPOS, "limit": 2000,
        "bbox": f"{lo - dlo:.6f},{la - dla:.6f},{lo + dlo:.6f},{la + dla:.6f}",
    })
    r = pedir(f"{API}?{q}") or {}
    fotos = r.get("data", [])
    print(f"{len(fotos)} fotos en {radio:.0f} m", flush=True)
    # Las más recientes primero, sin repetir casi el mismo sitio y rumbo
    fotos.sort(key=lambda f: -(f.get("captured_at") or 0))
    elegidas, vistos = [], set()
    for f in fotos:
        g = (f.get("computed_geometry") or f.get("geometry") or {}).get("coordinates")
        if not g or not f.get(URL):
            continue
        if DESDE and time.gmtime((f.get("captured_at") or 0) / 1000).tm_year < DESDE:
            continue
        rumbo = f.get("computed_compass_angle", f.get("compass_angle")) or 0
        clave = (round(g[1] * 4000), round(g[0] * 4000), int(rumbo // 45))   # ~25 m y 45°
        if clave in vistos:
            continue
        vistos.add(clave)
        elegidas.append((f, g, rumbo))
        if len(elegidas) >= maximo:
            break
    os.makedirs("fotos", exist_ok=True)
    indice = []
    for f, g, rumbo in elegidas:
        fecha = time.strftime("%Y-%m-%d", time.gmtime((f.get("captured_at") or 0) / 1000))
        nombre = f"{fecha}_{g[1]:.6f}_{g[0]:.6f}_{int(rumbo):03d}.jpg"
        datos = pedir(f[URL], binario=True)
        if not datos:
            continue
        with open(os.path.join("fotos", nombre), "wb") as fh:
            fh.write(datos)
        indice.append({"archivo": nombre, "id": f["id"], "la": g[1], "lo": g[0], "rumbo": rumbo, "fecha": fecha,
                       "secuencia": f.get("sequence")})
    with open("fotos/indice.json", "w") as fh:
        json.dump(indice, fh, indent=1)
    print(f"{len(indice)} fotos guardadas", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
