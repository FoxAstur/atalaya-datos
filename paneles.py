"""
Paneles de mensaje variable de la DGT: dónde está cada uno y hacia dónde mira.

El feed de localizaciones (DATEX II v3.7, Punto de Acceso Nacional) da de cada panel la carretera, el PK, las
coordenadas y el sentido como «positivo/negativo» (PK creciente/decreciente), que en la carretera no dice nada: la
app necesita el RUMBO de quien lo lee, para enseñar solo los paneles de tu calzada. Se saca igual que el de los
radares, con los hitos kilométricos de CartoCiudad (misma caché). Sale datos/paneles.json; el mensaje de cada panel
lo baja el móvil en tiempo real y lo cruza por el identificador.

Uso: python paneles.py   (lo lanza .github/workflows/paneles.yml una vez por semana)
"""
import json
import re
import sys
import time
import xml.etree.ElementTree as ET

import recolector as r

URL = "https://nap.dgt.es/datex2/v3/dgt/DevicePublication/vms_datex2_v37.xml"


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def leer(xml: bytes) -> list[dict]:
    out = []
    for dev in ET.fromstring(xml).iter():
        if local(dev.tag) != "device":
            continue
        v: dict = {}
        for e in dev.iter():
            t = local(e.tag)
            if e.text and e.text.strip() and t not in v:
                v[t] = e.text.strip()
        try:
            la, lo = float(v["latitude"]), float(v["longitude"])
        except (KeyError, ValueError):
            continue
        if not (27 < la < 44.5 and -19 < lo < 5):
            continue
        sentido = {"positive": "Creciente", "negative": "Decreciente"}.get(v.get("tpegDirectionRoad", ""))
        pk = None
        try:
            pk = float(v["kilometerPoint"])
        except (KeyError, ValueError):
            pass
        out.append({"id": dev.get("id"), "t": "PANEL", "la": la, "lo": lo, "c": v.get("roadName"), "pk": pk, "s": sentido,
                    "pr": r.provincia_canonica(v.get("province")), "destino": v.get("roadDestination")})
    return out


def main() -> int:
    r.log = lambda m: print(m, flush=True)          # sin tocar el registro del recolector
    try:
        xml = r.http(URL, timeout=120, intentos=4)
    except Exception as e:  # noqa: BLE001
        print(f"::warning::No se han podido bajar los paneles ({e}); se mantienen los de la vez anterior")
        return 0
    paneles = leer(xml)
    if len(paneles) < 1000:
        print(f"::warning::Solo {len(paneles)} paneles; se mantienen los de la vez anterior")
        return 0
    geo = r.Geocodificador()
    pet = set()
    for p in paneles:
        if p["s"] and p["c"] and p["pk"] is not None:
            k = int(p["pk"])
            pet |= {(p["c"], km, p["pr"]) for km in (k - 1, k, k + 1, k + 2) if km >= 0}
    geo.precargar(pet)
    con = 0
    filas = []
    for p in paneles:
        rb = r.rumbo_oficial(p, geo) if p["s"] and p["c"] and p["pk"] is not None else None
        con += rb is not None
        via = re.sub(r"\s+", "", p["c"] or "") or None
        filas.append([p["id"], round(p["la"], 5), round(p["lo"], 5), via, rb, p["pk"], (p["destino"] or "").title() or None])
    geo.guardar()
    filas.sort(key=lambda f: f[0])
    r.guardar_json("datos/paneles.json", {"version": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                           "campos": ["id", "la", "lo", "via", "rumbo", "pk", "destino"], "paneles": filas},
                   compacto=True)
    print(f"{len(filas)} paneles, {con} con rumbo ({100 * con // len(filas)} %)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
