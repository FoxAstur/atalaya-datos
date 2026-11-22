#!/usr/bin/env python3
"""
Las líneas de los tramos de tráfico de Barcelona (Ajuntament, «transit-relacio-trams», CC BY 4.0), para que la app
pinte su estado en tiempo real (bcn.cat/transit/dades/dadestrams.dat, cada 5 min) sin bajar el CSV cada vez.
Salida: datos/trafico_bcn.json {"tramos": {"id": [lat, lon, lat, lon, …]}, "fecha": …}
"""
import csv
import datetime
import io
import json
import sys
import urllib.request

URL = ("https://opendata-ajuntament.barcelona.cat/data/dataset/1090983a-1c40-4609-8620-14ad49aae3ab/resource/"
       "1d6c814c-70ef-4147-aa16-a49ddb952f72/download/transit_relacio_trams.csv")


def main() -> int:
    req = urllib.request.Request(URL, headers={"User-Agent": "atalaya-datos/1.0 (github.com/FoxAstur/atalaya-datos)"})
    crudo = urllib.request.urlopen(req, timeout=120).read()
    texto = crudo.decode("utf-8-sig", errors="replace")
    filas = list(csv.reader(io.StringIO(texto)))
    cab = [c.strip().lower() for c in filas[0]]
    print("columnas:", cab)
    i_id = next(i for i, c in enumerate(cab) if c.startswith("tram"))
    i_co = next(i for i, c in enumerate(cab) if c.startswith("coord"))
    tramos = {}
    for f in filas[1:]:
        if len(f) <= max(i_id, i_co):
            continue
        nums = [float(x) for x in f[i_co].replace(";", ",").split(",") if x.strip()]
        if len(nums) < 4 or len(nums) % 2:
            continue
        # vienen como lon, lat; se guardan lat, lon con 5 decimales (~1 m)
        pts = []
        for k in range(0, len(nums), 2):
            lo, la = nums[k], nums[k + 1]
            if not (40.5 < la < 42.0 and 1.5 < lo < 2.8):
                break
            pts += [round(la, 5), round(lo, 5)]
        if len(pts) >= 4:
            tramos[f[i_id].strip()] = pts
    print("tramos:", len(tramos))
    if len(tramos) < 200:
        print("Muy pocos tramos")
        return 1
    json.dump({"fecha": datetime.date.today().isoformat(), "fuente": "Ajuntament de Barcelona (CC BY 4.0)", "tramos": tramos},
              open("datos/trafico_bcn.json", "w"), separators=(",", ":"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
