#!/usr/bin/env python3
"""
Áreas de descanso y de servicio (OpenStreetMap: highway=rest_area / services) de España, Portugal y los países de
los viajes, para la barra de ruta de la app: datos/areas.json. Cada una: [lat, lon, tipo (D descanso, S servicio), nombre].
Datos © colaboradores de OpenStreetMap (ODbL).
"""
import json
import sys
import time

import recolector as R

PAISES = ["ES", "PT", "FR", "IT", "AD", "BE", "NL", "LU", "AT", "DE", "CH"]


def main() -> int:
    todas = []
    for p in PAISES:
        q = f"""
[out:json][timeout:280];
area["ISO3166-1"="{p}"]["admin_level"="2"]->.p;
nwr["highway"~"^(rest_area|services)$"](area.p);
out center tags;
"""
        try:
            d = R.overpass(q)
        except Exception as e:  # noqa: BLE001
            print(p, "error", e, flush=True)
            continue
        n = 0
        for e in d.get("elements", []):
            la = e.get("lat") or (e.get("center") or {}).get("lat")
            lo = e.get("lon") or (e.get("center") or {}).get("lon")
            if la is None:
                continue
            t = e.get("tags") or {}
            todas.append([round(la, 5), round(lo, 5), "S" if t.get("highway") == "services" else "D", (t.get("name") or "")[:60]])
            n += 1
        print(p, n, flush=True)
        time.sleep(5)
    if len(todas) < 2000:
        return 1
    R.guardar_json("datos/areas.json", {"generado": time.strftime("%Y-%m-%d"), "areas": todas}, compacto=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
