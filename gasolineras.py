#!/usr/bin/env python3
"""
Precios oficiales de los carburantes de todas las gasolineras de España (Ministerio para la Transición Ecológica,
Geoportal de gasolineras), en un fichero pequeño para la app: salida/gasolineras.json.gz.

Cada gasolinera: [id, lat, lon, rótulo, municipio, dirección, horario, g95, g98, diésel, diésel premium, GLP]
(precios en €/l; null si no lo vende). Se publica como versión "gasolineras" (no en el historial de git).
"""
import gzip
import json
import os
import sys
import time
import urllib.request

URL = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
CAMPOS = ["Precio Gasolina 95 E5", "Precio Gasolina 98 E5", "Precio Gasoleo A", "Precio Gasoleo Premium",
          "Precio Gases licuados del petróleo"]


def num(s):
    s = (s or "").strip().replace(",", ".")
    try:
        v = float(s)
        return round(v, 3) if v > 0 else None
    except ValueError:
        return None


def coord(s):
    try:
        return float((s or "").strip().replace(",", "."))
    except ValueError:
        return None


def bajar():
    ultimo = None
    for intento in range(4):
        try:
            req = urllib.request.Request(URL, headers={"Accept": "application/json", "User-Agent": "atalaya-datos (github.com/FoxAstur)"})
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            ultimo = e
            time.sleep(20 * (intento + 1))
    raise RuntimeError(f"Ministerio: {ultimo}")


def main() -> int:
    d = bajar()
    lista = []
    for e in d.get("ListaEESSPrecio", []):
        la, lo = coord(e.get("Latitud")), coord(e.get("Longitud (WGS84)"))
        if la is None or lo is None:
            continue
        precios = [num(e.get(c)) for c in CAMPOS]
        if not any(precios):
            continue
        lista.append([e.get("IDEESS"), round(la, 5), round(lo, 5), (e.get("Rótulo") or "").strip().title(),
                      (e.get("Municipio") or "").strip().title(), (e.get("Dirección") or "").strip().title(),
                      (e.get("Horario") or "").strip()] + precios)
    if len(lista) < 5000:
        todas = d.get("ListaEESSPrecio", [])
        print(f"solo {len(lista)} de {len(todas)} gasolineras: no se publica", flush=True)
        if todas:
            print(json.dumps(todas[0], ensure_ascii=False)[:1500], flush=True)
            print(json.dumps({k: v for k, v in d.items() if k != "ListaEESSPrecio"}, ensure_ascii=False)[:500], flush=True)
        return 1
    os.makedirs("salida", exist_ok=True)
    o = {"fecha": d.get("Fecha"), "generado": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
         "campos": ["id", "la", "lo", "rotulo", "municipio", "direccion", "horario", "g95", "g98", "diesel", "diesel_plus", "glp"],
         "gasolineras": lista}
    with gzip.open("salida/gasolineras.json.gz", "wt", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(lista)} gasolineras ({d.get('Fecha')}), {os.path.getsize('salida/gasolineras.json.gz') / 1e3:.0f} kB", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
