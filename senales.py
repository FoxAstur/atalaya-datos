#!/usr/bin/env python3
"""
Stops, cedas el paso y semáforos de España (OpenStreetMap, highway=stop / give_way / traffic_signals), para pintarlos
en el mapa de la app: datos/senales.csv.gz, una línea por señal «tipo;lat;lon» (tipo s = stop, c = ceda el paso,
f = semáforo; lat y lon en 1e-5 grados). Los semáforos de un mismo cruce (uno por cada calle) se juntan en uno.
Entrada: el OPL de osmium (colegios.yml). Datos © colaboradores de OpenStreetMap (ODbL).
"""
import gzip
import os
import sys

TIPOS = {"stop": "s", "give_way": "c", "traffic_signals": "f"}


def main() -> int:
    vistos = set()
    n = {"s": 0, "c": 0, "f": 0}
    os.makedirs("datos", exist_ok=True)
    tmp = "datos/senales.csv.gz.tmp"
    with open(sys.argv[1], encoding="utf-8") as f, gzip.open(tmp, "wt", encoding="utf-8", compresslevel=9) as out:
        for linea in f:
            if not linea.startswith("n"):
                continue
            partes = linea.rstrip("\n").split(" ")
            tags = next((p[1:] for p in partes if p.startswith("T")), "")
            x = next((p[1:] for p in partes if p.startswith("x")), "")
            y = next((p[1:] for p in partes if p.startswith("y")), "")
            if not x or not y:
                continue
            hw = None
            for kv in tags.split(","):
                if kv.startswith("highway="):
                    hw = kv[8:]
            t = TIPOS.get(hw)
            if not t:
                continue
            la = round(float(y) * 1e5); lo = round(float(x) * 1e5)
            # el mismo tipo a menos de ~25 m (semáforos de un cruce): uno
            clave = (t, la // 25 if t == "f" else la // 4, lo // 30 if t == "f" else lo // 5)
            if clave in vistos:
                continue
            vistos.add(clave)
            out.write(f"{t};{la};{lo}\n")
            n[t] += 1
    total = sum(n.values())
    print("stops", n["s"], "cedas", n["c"], "semáforos", n["f"], "total", total)
    if total < 50_000:
        print("Muy pocas señales")
        os.remove(tmp)
        return 1
    os.replace(tmp, "datos/senales.csv.gz")
    return 0


if __name__ == "__main__":
    sys.exit(main())
