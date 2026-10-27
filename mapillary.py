#!/usr/bin/env python3
"""
Mapillary: lo que ven las cámaras de la calle alrededor de cada radar (señales y objetos detectados en
fotos, con la dirección hacia la que miran). Sirve para deducir el sentido que vigila un radar cuando
ninguna fuente lo dice.

Modo exploración (python mapillary.py explorar): toma una muestra de radares de sentido conocido y de
sentido dudoso, consulta qué detecta Mapillary a su alrededor y lo guarda en depurar/mapillary.json para
estudiar qué pistas sirven. Necesita la variable de entorno MAPILLARY_TOKEN.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
import urllib.parse
import urllib.request

API = "https://graph.mapillary.com/map_features"
CAMPOS = "id,object_value,object_type,aligned_direction,geometry,first_seen_at,last_seen_at"


def consultar(token: str, la: float, lo: float, radio_m: float = 80.0) -> list[dict]:
    dla = radio_m / 111320.0
    dlo = radio_m / (111320.0 * max(0.2, abs(__import__("math").cos(__import__("math").radians(la)))))
    q = urllib.parse.urlencode({
        "access_token": token, "fields": CAMPOS, "limit": 200,
        "bbox": f"{lo - dlo:.6f},{la - dla:.6f},{lo + dlo:.6f},{la + dla:.6f}",
    })
    for intento in range(3):
        try:
            with urllib.request.urlopen(f"{API}?{q}", timeout=40) as r:
                return json.loads(r.read().decode("utf-8")).get("data", [])
        except Exception as e:  # noqa: BLE001
            if intento == 2:
                print(f"  mapillary {la:.5f},{lo:.5f}: {e}", flush=True)
            time.sleep(2 + 3 * intento)
    return []


def explorar(ruta_datos: str, salida: str, n: int = 120) -> None:
    token = os.environ.get("MAPILLARY_TOKEN", "").strip()
    if not token:
        sys.exit("Falta MAPILLARY_TOKEN")
    d = json.load(open(ruta_datos, encoding="utf-8"))
    pts = [p for p in d["puntos"] if p["t"] in ("RADAR_FIJO", "SEMAFORO", "OTRA_CAMARA")]
    random.seed(7)
    conocidos = [p for p in pts if p.get("rb") is not None]
    dudosos = [p for p in pts if p.get("s2")]
    muestra = random.sample(conocidos, min(n, len(conocidos))) + random.sample(dudosos, min(n, len(dudosos)))
    res = []
    t0 = time.time()
    for k, p in enumerate(muestra):
        feats = consultar(token, p["la"], p["lo"])
        res.append({"id": p["id"], "t": p["t"], "f": p["f"], "la": p["la"], "lo": p["lo"], "rb": p.get("rb"),
                    "s2": p.get("s2"), "c": p.get("c"), "mu": p.get("mu"), "ap": p.get("ap"), "mly": feats})
        if k % 20 == 0:
            print(f"  {k}/{len(muestra)} en {time.time() - t0:.0f}s", flush=True)
        time.sleep(0.2)
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False)
    tipos: dict = {}
    for r in res:
        for f in r["mly"]:
            tipos[f.get("object_value")] = tipos.get(f.get("object_value"), 0) + 1
    print("clases más vistas:", sorted(tipos.items(), key=lambda x: -x[1])[:60], flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "explorar":
        explorar("datos/radares.json", "depurar/mapillary.json")
