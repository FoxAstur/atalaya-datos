"""
Comprueba que cada radar de tramo de las fuentes está en los datos publicados, en su sentido:
  - los del PDF de cinemómetros de la DGT (vía, PK de salida, sentido, longitud)
  - los de OpenStreetMap (relaciones enforcement=average_speed con device/from/to) de España
Uso: python comprobar_tramos.py [datos/radares.json]   (necesita red; pensado para GitHub Actions)
"""
import json, math, sys, urllib.parse, urllib.request
import recolector as r

datos = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "datos/radares.json"))["puntos"]
tramos = [p for p in datos if p["t"] == "RADAR_TRAMO" and "la2" in p]


def dist(a, b, c, d):
    return math.hypot((a - c) * 111_000, (b - d) * 111_000 * math.cos(math.radians(a)))


def rumbo(a, b, c, d):
    y = math.sin(math.radians(d - b)) * math.cos(math.radians(c))
    x = math.cos(math.radians(a)) * math.sin(math.radians(c)) - math.sin(math.radians(a)) * math.cos(math.radians(c)) * math.cos(math.radians(d - b))
    return (math.degrees(math.atan2(y, x)) + 360) % 360


# --- 1) PDF de la DGT
enl = r.enlaces_pdf_dgt()
filas = r.parsear_cinemometros(r.lineas_pdf(r.http(enl["cinemometros"], timeout=180)))
pdf = [f for f in filas if f["tipo"] == "Tramo"]
faltan_pdf = []
for f in pdf:
    via = r.via_normalizada(f["via"])
    sentidos = ["Creciente", "Decreciente"] if f["sentido"] == "Ambos" else [f["sentido"]]
    for s in sentidos:
        ok = False
        for t in tramos:
            if r.via_normalizada(t.get("c")) != via or t.get("s") != s:
                continue
            pks = [x for x in (t.get("pk"), t.get("pk2")) if x is not None]
            if any(abs(x - f["pk"]) < 0.6 for x in pks):
                ok = True
                break
        if not ok:
            faltan_pdf.append(f"{f['prov']} {via} PK {f['pk']} {s} ({f.get('longitud')} m)")
print(f"PDF DGT: {len(pdf)} tramos; faltan {len(faltan_pdf)} (vía+sentido+PK):")
for x in faltan_pdf:
    print("  FALTA PDF", x)

# --- 2) OpenStreetMap (España)
Q = ('[out:json][timeout:300];area["ISO3166-1"="ES"][admin_level=2]->.es;'
     'relation["type"="enforcement"]["enforcement"="average_speed"](area.es);out body;>;out skel qt;')
d = None
for u in r.OVERPASS + ["https://overpass.private.coffee/api/interpreter"]:
    try:
        req = urllib.request.Request(u, data=urllib.parse.urlencode({"data": Q}).encode(), headers={"User-Agent": r.UA})
        d = json.load(urllib.request.urlopen(req, timeout=360))
        break
    except Exception as e:  # noqa: BLE001
        print("overpass", u, e)
if d:
    nodos = {e["id"]: e for e in d["elements"] if e["type"] == "node"}
    rels = [e for e in d["elements"] if e["type"] == "relation"]
    faltan_osm = []
    for e in rels:
        def nodo(rol):
            for m in e["members"]:
                if m["type"] == "node" and m["role"] == rol and m["ref"] in nodos:
                    return nodos[m["ref"]]
            return None
        a, b = nodo("from"), nodo("to")
        if not a or not b:
            devs = [nodos[m["ref"]] for m in e["members"] if m["type"] == "node" and m["role"] == "device" and m["ref"] in nodos]
            if len(devs) == 2:
                a, b = devs   # sin from/to: sin sentido seguro
            else:
                continue
        ok = False
        for t in tramos:
            d1 = dist(t["la"], t["lo"], a["lat"], a["lon"]); d2 = dist(t["la2"], t["lo2"], b["lat"], b["lon"])
            if max(d1, d2) < 500:
                ok = True; break
            # al revés (sin from/to fiable): se da por bueno solo si la relación no tiene from/to
            if nodo("from") is None and max(dist(t["la"], t["lo"], b["lat"], b["lon"]), dist(t["la2"], t["lo2"], a["lat"], a["lon"])) < 500:
                ok = True; break
        if not ok:
            faltan_osm.append(f"r{e['id']} {e.get('tags', {}).get('maxspeed', '?')} de {a['lat']:.5f},{a['lon']:.5f} a {b['lat']:.5f},{b['lon']:.5f}")
    print(f"\nOSM: {len(rels)} tramos; faltan {len(faltan_osm)} (por extremos, en su sentido):")
    for x in faltan_osm:
        print("  FALTA OSM", x)
