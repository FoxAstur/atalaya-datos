#!/usr/bin/env python3
"""
Señales y peligros de la vía de España (OpenStreetMap), para pintarlos en el mapa de la app y avisar:
datos/senales.csv.gz, una línea por punto «tipo;lat;lon» (lat y lon en 1e-5 grados). Tipos:
  s  stop (highway=stop)                 c  ceda el paso (highway=give_way)
  f  semáforo (highway=traffic_signals; los de un mismo cruce, uno)
  b  paso a nivel con barreras (railway=level_crossing con crossing:barrier o crossing=barrier)
  n  paso a nivel sin barreras o sin saber (railway=level_crossing)
  r  resalto / paso elevado / cojín (traffic_calming=bump, hump, table, cushion)
  d  badén (traffic_calming=dip)
  a  paso de animales (hazard=animal_crossing o las señales P-23 y P-24)
Las versiones viejas de la app solo leen s, c y f y se saltan el resto.
Entrada: el OPL de osmium (colegios.yml). Datos © colaboradores de OpenStreetMap (ODbL).
"""
import gzip
import os
import sys

TIPOS = {"stop": "s", "give_way": "c", "traffic_signals": "f"}
RESALTOS = {"bump", "hump", "table", "cushion", "speed_bump", "speed_hump", "speed_table"}
# rejilla para juntar duplicados (en 1e-5 grados): semáforos de un cruce ~25 m; el resto ~5 m; animales ~200 m
REJILLA = {"f": (25, 30), "a": (200, 250), "r": (8, 10), "d": (8, 10), "b": (10, 12), "n": (10, 12)}


def etiquetas(partes: list[str]) -> dict:
    t = next((p[1:] for p in partes if p.startswith("T")), "")
    out = {}
    for kv in t.split(","):
        if "=" in kv:
            k, v = kv.split("=", 1)
            out[k] = v.replace("%20%", " ").replace("%3b%", ";")
    return out


def tipo_de(tg: dict) -> str | None:
    hw = tg.get("highway")
    if hw in TIPOS:
        return TIPOS[hw]
    if tg.get("railway") == "level_crossing":
        barrera = tg.get("crossing:barrier", "")
        if (barrera and barrera != "no") or tg.get("crossing") in ("barrier", "gates"):
            return "b"
        return "n"
    tc = tg.get("traffic_calming")
    if tc in RESALTOS:
        return "r"
    if tc == "dip":
        return "d"
    if tg.get("hazard") == "animal_crossing":
        return "a"
    ts = tg.get("traffic_sign", "").upper().replace("-", "").replace(" ", "")
    if any(c in ts for c in ("ES:P23", "ES:P24")):
        return "a"
    return None


def nodos_de_tranvia(ruta: str) -> set[str]:
    """Los nodos de las vías de tranvía y metro ligero (OPL de vías: «w… N n1,n2,…»)."""
    out = set()
    if not ruta or not os.path.exists(ruta):
        return out
    for linea in open(ruta, encoding="utf-8"):
        if not linea.startswith("w"):
            continue
        for p in linea.split(" "):
            if p.startswith("N"):
                out.update(x for x in p[1:].strip().split(",") if x)
    return out


def main() -> int:
    tranvia = nodos_de_tranvia(sys.argv[2] if len(sys.argv) > 2 else "")
    print("nodos de tranvía", len(tranvia))
    quitados = 0
    vistos = set()
    n = {k: 0 for k in "scfbnrda"}
    os.makedirs("datos", exist_ok=True)
    tmp = "datos/senales.csv.gz.tmp"
    with open(sys.argv[1], encoding="utf-8") as f, gzip.open(tmp, "wt", encoding="utf-8", compresslevel=9) as out:
        for linea in f:
            if not linea.startswith("n"):
                continue
            partes = linea.rstrip("\n").split(" ")
            x = next((p[1:] for p in partes if p.startswith("x")), "")
            y = next((p[1:] for p in partes if p.startswith("y")), "")
            if not x or not y:
                continue
            t = tipo_de(etiquetas(partes))
            if not t:
                continue
            if t in ("b", "n") and partes[0] in tranvia:
                quitados += 1
                continue
            la = round(float(y) * 1e5); lo = round(float(x) * 1e5)
            ra, ro = REJILLA.get(t, (4, 5))
            clave = (t, la // ra, lo // ro)
            if clave in vistos:
                continue
            vistos.add(clave)
            out.write(f"{t};{la};{lo}\n")
            n[t] += 1
    total = n["s"] + n["c"] + n["f"]
    print("stops", n["s"], "cedas", n["c"], "semáforos", n["f"], "| pasos a nivel con barreras", n["b"], "sin", n["n"],
          "(", quitados, "de tranvía quitados) | resaltos", n["r"], "badenes", n["d"], "| animales", n["a"])
    if total < 50_000:
        print("Muy pocas señales")
        os.remove(tmp)
        return 1
    os.replace(tmp, "datos/senales.csv.gz")
    return 0


if __name__ == "__main__":
    sys.exit(main())
