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
faltan_pdf, etiqueta = [], []
for f in pdf:
    via = r.via_normalizada(f["via"])
    sentidos = ["Creciente", "Decreciente"] if f["sentido"] == "Ambos" else [f["sentido"]]
    largo = (f.get("longitud") or 0) / 1000
    for s in sentidos:
        # el PK del PDF es la salida; la entrada está «largo» antes en su sentido
        ini = f["pk"] + largo if s == "Decreciente" else f["pk"] - largo
        def casa(t):
            pk, pk2 = t.get("pk"), t.get("pk2")
            return (pk is not None and abs(pk - ini) < 0.6) or (pk2 is not None and abs(pk2 - f["pk"]) < 0.6) \
                or (pk is not None and pk2 is None and abs(pk - f["pk"]) < 0.6)
        mismos = [t for t in tramos if r.via_normalizada(t.get("c")) == via and casa(t)]
        if any(t.get("s") == s for t in mismos):
            continue
        if mismos:
            etiqueta.append(f"{f['prov']} {via} PK {f['pk']} {s}: está como {mismos[0].get('s')} ({mismos[0]['id']})")
        else:
            faltan_pdf.append(f"{f['prov']} {via} PK {f['pk']} {s} ({f.get('longitud')} m)")
print(f"PDF DGT: {len(pdf)} tramos; faltan {len(faltan_pdf)} (vía+sentido+PK):")
for x in faltan_pdf:
    print("  FALTA PDF", x)
print(f"con otra etiqueta de sentido ({len(etiqueta)}; puede ser el otro sentido o solo la etiqueta):")
for x in etiqueta:
    print("  ETIQUETA", x)

# --- 2) OpenStreetMap (España)
# por trozos (la consulta de toda España de golpe no la aguanta el servidor)
trozos = [(la, lo, la + 2.5, lo + 3.0) for la in (35.9, 38.4, 40.9) for lo in (-9.5, -6.5, -3.5, -0.5, 2.5)] + \
         [(27.5, -18.5, 29.5, -13.3), (43.3, -9.5, 44.0, -1.0)]
import time
elementos, fallidos = {}, []
fin = time.time() + 20 * 60   # Overpass a veces no contesta: como mucho 20 min y se informa de lo que haya
for b in trozos:
    if time.time() > fin:
        fallidos.append(b)
        continue
    Q = ('[out:json][timeout:180];relation["type"="enforcement"]["enforcement"="average_speed"]'
         f'({b[0]},{b[1]},{b[2]},{b[3]});out body;>;out skel qt;')
    hecho = False
    for intento in range(3):
        for u in r.OVERPASS + ["https://overpass.private.coffee/api/interpreter"]:
            if time.time() > fin:
                break
            try:
                req = urllib.request.Request(u, data=urllib.parse.urlencode({"data": Q}).encode(), headers={"User-Agent": r.UA})
                for e in json.load(urllib.request.urlopen(req, timeout=120))["elements"]:
                    elementos[(e["type"], e["id"])] = e
                hecho = True
                break
            except Exception as ex:  # noqa: BLE001
                print("overpass", u, b, ex)
        if hecho or time.time() > fin:
            break
        time.sleep(30)
    if not hecho:
        fallidos.append(b)
d = {"elements": list(elementos.values())} if elementos else None
if fallidos:
    print("trozos sin respuesta:", fallidos)
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
        froms = [nodos[m["ref"]] for m in e["members"] if m["type"] == "node" and m["role"] == "from" and m["ref"] in nodos]
        if b and len(froms) > 1:   # varias entradas: el tramo empieza en la más lejana de la salida (como el recolector)
            a = max(froms, key=lambda n: dist(n["lat"], n["lon"], b["lat"], b["lon"]))
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
