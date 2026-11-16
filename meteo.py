#!/usr/bin/env python3
"""
Avisos meteorológicos de AEMET (Meteoalerta) para la app, sacados de Meteoalarm (EUMETNET, licencia equivalente a
CC BY 4.0): lluvia, viento, nieve, niebla, tormentas, temperaturas… de nivel amarillo, naranja o rojo.

- salida/avisos.json.gz (versión «meteo», cada 30 minutos): los avisos vigentes o de las próximas 48 h.
  [zona, nivel (2 amarillo, 3 naranja, 4 rojo), tipo, titular, descripción, inicio, fin]  (fechas en ms UTC)
- datos/zonas_meteo.json (una vez al mes): el contorno de cada zona de aviso (Meteoalarm / GeoSphere Austria),
  {codigo: [nombre, [[lon, lat, lon, lat, …], …]]} con los anillos exteriores simplificados.

Uso: python meteo.py [--zonas]
"""
import gzip
import json
import os
import sys
import time
import urllib.request
from datetime import datetime

AVISOS = "https://feeds.meteoalarm.org/api/v1/warnings/feeds-spain"
ZONAS = ("https://gis.geosphere.at/maps/rest/services/Hosted/MeteoAlarm_Gap_Analysis_2026_WFL1/FeatureServer/3/query"
         "?where=code%20like%20%27ES%25%27&outFields=code,name,type&maxAllowableOffset=0.004&geometryPrecision=4&outSR=4326&f=geojson")

# awareness_type de Meteoalarm -> tipo de la app (los costeros no afectan a la carretera)
TIPOS = {1: "viento", 2: "nieve", 3: "tormentas", 4: "niebla", 5: "calor", 6: "frio", 8: "incendios", 9: "aludes",
         10: "lluvia", 12: "inundaciones", 13: "lluvia"}


def bajar(url: str, timeout=120) -> bytes:
    ultimo = None
    for intento in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "atalaya-datos (github.com/FoxAstur)", "Accept-Encoding": "gzip"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                b = r.read()
                return gzip.decompress(b) if r.headers.get("Content-Encoding") == "gzip" else b
        except Exception as e:  # noqa: BLE001
            ultimo = e
            print(f"intento {intento + 1}: {e}", flush=True)
            time.sleep(20 * (intento + 1))
    raise ConnectionError(str(ultimo))


def zonas() -> int:
    d = json.loads(bajar(ZONAS, 300))
    out = {}
    for f in d.get("features", []):
        p, g = f["properties"], f["geometry"]
        if p.get("type") != "EMMA_ID" or not g:
            continue
        polis = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        anillos = []
        for poli in polis:
            ext = poli[0]
            if len(ext) < 4:
                continue
            anillos.append([round(v, 4) for x, y in ext for v in (x, y)])
        if anillos:
            out[p["code"]] = [p.get("name", ""), anillos]
    if len(out) < 200:
        print(f"solo {len(out)} zonas: no se guardan", flush=True)
        return 1
    with open("datos/zonas_meteo.json", "w", encoding="utf-8") as f:
        json.dump({"fuente": "Meteoalarm (EUMETNET) / GeoSphere Austria", "zonas": out}, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(out)} zonas, {os.path.getsize('datos/zonas_meteo.json') / 1e3:.0f} kB", flush=True)
    return 0


def ms(texto: str) -> int:
    return int(datetime.fromisoformat(texto.replace("Z", "+00:00")).timestamp() * 1000)


def leer(d: dict, ahora_ms: int) -> list:
    """Los avisos en castellano, de nivel amarillo o más, vigentes o que empiezan en menos de 48 h."""
    vistos = {}
    for w in d.get("warnings", []):
        a = w.get("alert", {})
        if a.get("status") != "Actual" or a.get("msgType") == "Cancel":
            continue
        for i in a.get("info", []):
            if i.get("language") != "es-ES":
                continue
            par = {p["valueName"]: p["value"] for p in i.get("parameter", [])}
            try:
                nivel = int(par.get("awareness_level", "0").split(";")[0])
                tipo = TIPOS.get(int(par.get("awareness_type", "0").split(";")[0]))
            except ValueError:
                continue
            if nivel < 2 or tipo is None:
                continue
            try:
                ini, fin = ms(i.get("onset") or i["effective"]), ms(i["expires"])
            except (KeyError, ValueError):
                continue
            if fin <= ahora_ms or ini > ahora_ms + 48 * 3_600_000:
                continue
            desc = " ".join((i.get("description") or "").split())
            for ar in i.get("area", []):
                for g in ar.get("geocode", []):
                    if g.get("valueName") != "EMMA_ID":
                        continue
                    fila = [g["value"], nivel, tipo, i.get("event", ""), desc[:240], ini, fin]
                    # un aviso actualizado sustituye al anterior de la misma zona, tipo y hora
                    vistos[(g["value"], tipo, ini)] = fila
    return sorted(vistos.values(), key=lambda f: (f[0], f[5]))


def main() -> int:
    if "--zonas" in sys.argv:
        return zonas()
    try:
        d = json.loads(bajar(AVISOS))
    except ConnectionError as e:
        print(f"::warning::Meteoalarm sin respuesta ({e}); se mantienen los avisos anteriores", flush=True)
        return 3
    avisos = leer(d, int(time.time() * 1000))
    os.makedirs("salida", exist_ok=True)
    with gzip.open("salida/avisos.json.gz", "wt", encoding="utf-8") as f:
        json.dump({"generado": int(time.time() * 1000), "fuente": "AEMET vía Meteoalarm (EUMETNET)",
                   "campos": ["zona", "nivel", "tipo", "titular", "descripcion", "inicio", "fin"], "avisos": avisos},
                  f, ensure_ascii=False, separators=(",", ":"))
    n = {k: sum(1 for a in avisos if a[1] == k) for k in (2, 3, 4)}
    print(f"{len(avisos)} avisos (amarillos {n[2]}, naranjas {n[3]}, rojos {n[4]})", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
