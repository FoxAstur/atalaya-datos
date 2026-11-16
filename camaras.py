#!/usr/bin/env python3
"""
Cámaras de tráfico de la DGT (Punto de Acceso Nacional, DATEX II v3.7): dónde está cada una, en qué carretera y PK,
y hacia dónde mira. La imagen la baja el móvil en directo de etraffic.dgt.es/camarasEtraffic/<id>.jpg.
Sale datos/camaras.json: [id, lat, lon, carretera, pk, destino, provincia].

Uso: python camaras.py   (lo lanza .github/workflows/camaras.yml una vez por semana)
"""
import json
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

URL = "https://nap.dgt.es/datex2/v3/dgt/DevicePublication/camaras_datex2_v37.xml"


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def leer(xml: bytes) -> list:
    out = []
    for dev in ET.fromstring(xml).iter():
        if local(dev.tag) != "device":
            continue
        v: dict = {}
        for e in dev.iter():
            t = local(e.tag)
            if e.text and e.text.strip() and t not in v:
                v[t] = e.text.strip()
        if v.get("typeOfDevice") != "camera":
            continue
        try:
            la, lo = float(v["latitude"]), float(v["longitude"])
        except (KeyError, ValueError):
            continue
        if not (27 < la < 44.5 and -19 < lo < 5):
            continue
        try:
            pk = round(float(v.get("kilometerPoint", "")), 1)
        except ValueError:
            pk = None
        url = v.get("deviceUrl", "")
        ident = dev.get("id") or ""
        # la imagen siempre es camarasEtraffic/<id>.jpg; si un día cambia, se guarda la URL entera
        imagen = "" if url.endswith(f"/camarasEtraffic/{ident}.jpg") else url
        destino = v.get("roadDestination", "").title().replace(" De ", " de ")
        out.append([ident, round(la, 5), round(lo, 5), v.get("roadName", ""), pk, destino, v.get("province", "").title(), imagen])
    return out


def main() -> int:
    if len(sys.argv) > 1:
        xml = open(sys.argv[1], "rb").read()
    else:
        ultimo = None
        for intento in range(4):
            try:
                req = urllib.request.Request(URL, headers={"User-Agent": "atalaya-datos (github.com/FoxAstur)"})
                with urllib.request.urlopen(req, timeout=180) as r:
                    xml = r.read()
                break
            except Exception as e:  # noqa: BLE001
                ultimo = e
                print(f"intento {intento + 1}: {e}", flush=True)
                time.sleep(30 * (intento + 1))
        else:
            print(f"::warning::DGT sin respuesta ({ultimo}); se mantienen las cámaras anteriores", flush=True)
            return 0
    camaras = leer(xml)
    if len(camaras) < 1000:
        print(f"solo {len(camaras)} cámaras: no se publica", flush=True)
        return 1
    camaras.sort(key=lambda c: (c[3], c[4] or 0))
    with open("datos/camaras.json", "w", encoding="utf-8") as f:
        json.dump({"generado": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "fuente": "DGT (Punto de Acceso Nacional)",
                   "imagen": "https://etraffic.dgt.es/camarasEtraffic/{id}.jpg",
                   "campos": ["id", "la", "lo", "carretera", "pk", "destino", "provincia", "imagen"],
                   "camaras": camaras}, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(camaras)} cámaras", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
