"""Zonas de aparcamiento regulado (de pago) de las ciudades que lo publican, para que la app sepa si has aparcado o vas
a aparcar en zona azul / ORA / SER y te diga su horario.

- València: cada plaza ORA con su color (geoportal OPENDATA, capa 205; CC BY 4.0).
- Madrid: los parquímetros del SER (sigma.madrid.es): cerca de uno, estás en zona SER (azul o verde).

Barcelona no deja bajar sus datos desde servidores (403): la app los bajaría en el móvil más adelante.

Salida: salida/aparcar.json.gz → {"generado", "ciudades": {"VLC": {"nombre", "horario", "radio", "tipos", "p": [[la, lo, tipo]…]}}}
"""
import gzip, json, math, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"


def pedir(url, intentos=4):
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"  reintento {i + 1}: {e}", file=sys.stderr)
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"no responde: {url}")


def arcgis(base, campos="*", tam=1000):
    """Todas las entidades de una capa ArcGIS (por páginas), en GeoJSON y coordenadas GPS."""
    out, off = [], 0
    while True:
        q = urllib.parse.urlencode({"where": "1=1", "outFields": campos, "outSR": 4326, "f": "geojson",
                                    "resultOffset": off, "resultRecordCount": tam, "returnGeometry": "true"})
        d = pedir(f"{base}/query?{q}")
        fs = d.get("features") or []
        out += fs
        print(f"  {base.split('/')[-3]}: {len(out)}", file=sys.stderr)
        if len(fs) < tam and not d.get("exceededTransferLimit") and not (d.get("properties") or {}).get("exceededTransferLimit"):
            break
        if not fs:
            break
        off += len(fs)
    return out


def centro(geom):
    """Un punto de la geometría (el medio de sus coordenadas)."""
    t = geom.get("type")
    c = geom.get("coordinates")
    if t == "Point":
        return c[1], c[0]
    pts = c if t == "LineString" else [p for parte in c for p in parte] if t in ("MultiLineString", "Polygon") else []
    if not pts:
        return None
    return sum(p[1] for p in pts) / len(pts), sum(p[0] for p in pts) / len(pts)


def valencia():
    fs = arcgis("https://geoportal.valencia.es/server/rest/services/OPENDATA/Trafico/MapServer/205", "color", 2000)
    tipos = ["Azul", "Naranja", "Verde"]   # «Blanco»: sin regular (no se guarda)
    p = []
    for f in fs:
        col = (f.get("properties") or {}).get("color")
        if col not in tipos or not f.get("geometry"):
            continue
        c = centro(f["geometry"])
        if c:
            p.append([round(c[0], 5), round(c[1], 5), tipos.index(col)])
    # plazas vecinas del mismo color casi en el mismo sitio: una basta (cada 8 m)
    vistos, unicos = set(), []
    for la, lo, t in p:
        k = (round(la / 0.00007), round(lo / 0.00009), t)
        if k in vistos:
            continue
        vistos.add(k)
        unicos.append([la, lo, t])
    return {"nombre": "València", "sistema": "ORA", "radio": 30, "tipos": tipos,
            "horario": "De pago de lunes a viernes de 9 a 14 y de 17 a 20, y los sábados de 9 a 14 (mira el parquímetro)",
            "p": unicos}


def madrid():
    base = "https://sigma.madrid.es/hosted/rest/services/GEOPORTAL/PARQU%C3%8DMETROS_DEL_SERVICIO_DE_ESTACIONAMIENTO_REGULADO/MapServer/0"
    info = pedir(base + "?f=json")
    print("  campos Madrid:", [c.get("name") for c in info.get("fields", [])], file=sys.stderr)
    fs = arcgis(base, "*", 1000)
    p = []
    for f in fs:
        pr = f.get("properties") or {}
        # (la capa guarda también los retirados: si lo dice, fuera)
        txt = " ".join(str(v) for v in pr.values()).lower()
        if "baja" in txt or "retirad" in txt or "histor" in txt:
            continue
        c = centro(f.get("geometry") or {})
        if c:
            p.append([round(c[0], 5), round(c[1], 5), 0])
    return {"nombre": "Madrid", "sistema": "SER", "radio": 120, "tipos": ["SER (azul o verde)"],
            "horario": "De pago de lunes a viernes de 9 a 21 y los sábados de 9 a 15; en agosto, de 9 a 15 (mira el parquímetro)",
            "p": p}


def main():
    ciudades = {}
    for cod, f in (("VLC", valencia), ("MAD", madrid)):
        try:
            c = f()
            if len(c["p"]) < 100:
                raise RuntimeError(f"muy pocas plazas: {len(c['p'])}")
            ciudades[cod] = c
            print(f"{cod}: {len(c['p'])} puntos", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print(f"::warning::{cod}: {e}", file=sys.stderr)
    if not ciudades:
        sys.exit(3)
    os.makedirs("salida", exist_ok=True)
    doc = {"generado": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M"), "ciudades": ciudades}
    with gzip.open("salida/aparcar.json.gz", "wt", encoding="utf-8") as g:
        json.dump(doc, g, ensure_ascii=False, separators=(",", ":"))
    print("tamaño:", os.path.getsize("salida/aparcar.json.gz"), file=sys.stderr)


if __name__ == "__main__":
    main()
