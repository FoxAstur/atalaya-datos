#!/usr/bin/env python3
"""
Carriles BUS-VAO de España (OpenStreetMap: hov=designated en toda la calzada o en algún carril, hov:lanes), para que
la app avise al acercarte: datos/vao.json. Cada uno:
  {"n": carretera o nombre, "m": ocupantes mínimos (0 si no consta), "r": 1 si es reversible / cambia con la hora,
   "c": condiciones tal cual (hov:conditional, oneway:conditional), "a": [lat, lon, lat, lon, ...] en el sentido del carril}
Datos © colaboradores de OpenStreetMap (ODbL).
"""
import sys
import time

import recolector as R

CONSULTA = """
[out:json][timeout:280];
area["ISO3166-1"="ES"]["admin_level"="2"]->.p;
(
  way["highway"]["hov"="designated"](area.p);
  way["highway"]["hov:lanes"~"designated"](area.p);
  way["highway"]["hov:lanes:forward"~"designated"](area.p);
  way["highway"]["hov:lanes:backward"~"designated"](area.p);
);
out tags geom;
"""


def plano(g) -> list[float]:
    out = []
    for p in g:
        out += [round(p["lat"], 5), round(p["lon"], 5)]
    return out


def main() -> int:
    d = R.overpass(CONSULTA)
    carriles = []
    for e in d.get("elements", []):
        t = e.get("tags") or {}
        g = e.get("geometry") or []
        if len(g) < 2 or t.get("access") == "no" and t.get("bus") == "designated" and "hov" not in t:
            continue
        nombre = t.get("ref") or t.get("name") or ""
        try:
            minimo = int(str(t.get("hov:minimum", "0")).split(";")[0])
        except ValueError:
            minimo = 0
        cond = "; ".join(v for k, v in t.items() if k in ("hov:conditional", "oneway:conditional", "hov:lanes:conditional"))[:200]
        reversible = 1 if t.get("oneway") in ("reversible", "alternating") or "oneway:conditional" in t else 0
        sentidos = []
        if "hov:lanes:backward" in t and "designated" in t["hov:lanes:backward"]:
            sentidos.append(-1)
        if t.get("hov") == "designated" or "designated" in t.get("hov:lanes", "") or "designated" in t.get("hov:lanes:forward", ""):
            sentidos.append(1)
            if reversible or t.get("oneway") not in ("yes", "1", "-1") and t.get("hov") == "designated" and "hov:lanes" not in t:
                sentidos.append(-1)
        if t.get("oneway") == "-1":
            sentidos = [-s for s in sentidos]
        for s in sorted(set(sentidos)):
            carriles.append({"n": nombre[:40], "m": minimo, "r": reversible, "c": cond, "a": plano(g if s > 0 else g[::-1])})
    print("vías:", len(d.get("elements", [])), "carriles:", len(carriles), flush=True)
    for c in carriles[:40]:
        print(c["n"], c["m"], c["r"], c["c"], len(c["a"]) // 2, c["a"][:2], flush=True)
    if len(carriles) < 3:
        return 1
    R.guardar_json("datos/vao.json", {"generado": time.strftime("%Y-%m-%d"), "carriles": carriles}, compacto=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
