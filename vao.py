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
  way["highway"]["hov"~"^(designated|lane)$"](area.p);
  way["highway"]["name"~"VAO",i](area.p);
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


def unir(carriles: list[dict]) -> list[dict]:
    """OSM corta las vías en cada puente o cambio de carriles: se juntan las seguidas del mismo nombre y sentido."""
    def ini(c):
        return (c["a"][0], c["a"][1])

    def fin(c):
        return (c["a"][-2], c["a"][-1])

    pend = carriles[:]
    out = []
    while pend:
        c = pend.pop(0)
        cambio = True
        while cambio:
            cambio = False
            for i, o in enumerate(pend):
                if o["n"] != c["n"] or o["r"] != c["r"]:
                    continue
                if ini(o) == fin(c):
                    c = dict(c, a=c["a"] + o["a"][2:])
                elif fin(o) == ini(c):
                    c = dict(c, a=o["a"] + c["a"][2:])
                else:
                    continue
                c["m"] = max(c["m"], o["m"])
                c["c"] = c["c"] or o["c"]
                pend.pop(i)
                cambio = True
                break
        out.append(c)
    return out


def largo(c) -> float:
    a = c["a"]
    return sum(R.distancia(a[i], a[i + 1], a[i + 2], a[i + 3]) for i in range(0, len(a) - 2, 2))


def main() -> int:
    d = None
    for intento in range(3):
        try:
            d = R.overpass(CONSULTA)
            break
        except Exception as e:  # noqa: BLE001
            print("Overpass:", e, flush=True)
            time.sleep(60)
    if d is None:
        return 1
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
        if t.get("hov") in ("designated", "lane") or "vao" in (t.get("name") or "").lower() or "designated" in t.get("hov:lanes", "") or "designated" in t.get("hov:lanes:forward", ""):
            sentidos.append(1)
            if reversible or t.get("oneway") not in ("yes", "1", "-1") and "hov:lanes" not in t:
                sentidos.append(-1)
        if t.get("oneway") == "-1":
            sentidos = [-s for s in sentidos]
        for s in sorted(set(sentidos)):
            carriles.append({"n": nombre[:40], "m": minimo, "r": reversible, "c": cond, "a": plano(g if s > 0 else g[::-1])})
    print("vías:", len(d.get("elements", [])), "trozos:", len(carriles), flush=True)
    carriles = [c for c in unir(carriles) if largo(c) >= 200]
    print("carriles (juntos, de 200 m o más):", len(carriles), flush=True)
    for c in carriles:
        print(c["n"], c["m"], c["r"], c["c"], round(largo(c)), c["a"][:2], flush=True)
    if len(carriles) < 3:
        return 1
    R.guardar_json("datos/vao.json", {"generado": time.strftime("%Y-%m-%d"), "carriles": carriles}, compacto=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
