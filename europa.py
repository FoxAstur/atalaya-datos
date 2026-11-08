#!/usr/bin/env python3
"""
Radares y cámaras de otros países de Europa (OpenStreetMap), para viajar fuera de España y Portugal.

Escribe datos/europa.json con el mismo formato de puntos que radares.json. Los identificadores llevan el país
("eu:FR:n123"): la app lo usa para aplicar la ley de cada país (en Francia solo zonas de control, sin decir dónde
está el radar). Alemania y Suiza no se incluyen: allí no se permite usar avisadores mientras conduces.

Datos © colaboradores de OpenStreetMap (ODbL).
"""
import json
import sys
import time

import recolector as R

PAISES = ["FR", "IT", "BE", "NL", "LU", "AT", "AD", "MC"]
SALIDA = "datos/europa.json"


def consulta(pais: str) -> str:
    return f"""
[out:json][timeout:280];
area["ISO3166-1"="{pais}"]["admin_level"="2"]->.p;
(
  node["highway"="speed_camera"](area.p);
  node["enforcement"](area.p);
  node["speed_camera"](area.p);
);
out body;
rel["type"="enforcement"](area.p);
out geom;
"""


def puntos_de(pais: str) -> list[dict]:
    d = R.overpass(consulta(pais))
    salida = {}
    for e in d.get("elements", []):
        tags = e.get("tags") or {}
        if e["type"] == "node":
            tipo = (R.clasificar_osm(tags.get("enforcement"))
                    or R.clasificar_osm(tags.get("speed_camera") if tags.get("speed_camera") not in ("yes", None) else None)
                    or ("RADAR_FIJO" if tags.get("highway") == "speed_camera" or tags.get("speed_camera") == "yes" else None))
            if not tipo or e.get("lat") is None:
                continue
            ex = {}
            dg = R.direccion_osm(tags).get("_dirg")
            if dg is not None:
                ex["rb"] = round(float(dg), 1)
            else:
                ex["s2"] = 1
            i = f"eu:{pais}:n{e['id']}"
            salida[i] = R.punto(i, tipo, "OSM", e["lat"], e["lon"], v=R.limite(tags), c=(tags.get("ref") or None),
                                n=R.nombre_camara_osm(tags), src="OpenStreetMap", **ex)
        elif e["type"] == "relation":
            tipo = R.clasificar_osm(tags.get("enforcement"))
            if tipo != "RADAR_TRAMO":
                continue
            desde = hasta = None
            for m in e.get("members", []):
                c = None
                if m.get("type") == "node" and m.get("lat") is not None:
                    c = (m["lat"], m["lon"])
                elif m.get("geometry"):
                    c = (m["geometry"][0]["lat"], m["geometry"][0]["lon"])
                if c and m.get("role") == "from":
                    desde = c
                elif c and m.get("role") == "to":
                    hasta = c
            if desde and hasta:
                i = f"eu:{pais}:r{e['id']}"
                salida[i] = R.punto(i, "RADAR_TRAMO", "OSM", desde[0], desde[1], la2=round(hasta[0], 6),
                                    lo2=round(hasta[1], 6), v=R.limite(tags), n=tags.get("name"), src="OpenStreetMap")
    return list(salida.values())


def main() -> int:
    todos, estado = [], {}
    try:
        previo = {p["id"].split(":")[1]: [] for p in json.load(open(SALIDA, encoding="utf-8"))["puntos"]}
        for p in json.load(open(SALIDA, encoding="utf-8"))["puntos"]:
            previo[p["id"].split(":")[1]].append(p)
    except (OSError, ValueError, KeyError):
        previo = {}
    for pais in PAISES:
        try:
            ps = puntos_de(pais)
            if len(ps) < 0.5 * len(previo.get(pais, [])):
                raise RuntimeError(f"solo {len(ps)} (antes {len(previo[pais])})")
            estado[pais] = f"ok · {len(ps)}"
        except Exception as e:  # noqa: BLE001
            ps = previo.get(pais, [])
            estado[pais] = f"error ({e}); se mantienen {len(ps)}"
        print(pais, estado[pais], flush=True)
        todos += ps
        time.sleep(5)
    if not todos:
        return 1
    R.guardar_json(SALIDA, {"version": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()), "fuentes": estado,
                            "puntos": todos}, compacto=True)
    print(f"{len(todos)} puntos", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
