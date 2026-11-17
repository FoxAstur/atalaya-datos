#!/usr/bin/env python3
"""
Puntos de recarga para vehículos eléctricos de España (registro oficial del Ministerio para la Transición Ecológica,
publicado por la DGT en el Punto de Acceso Nacional, DATEX II v3), en un fichero pequeño para la app:
salida/recarga.json.gz.

Cada sitio: [id, lat, lon, operador (índice en "operadores"), nombre, municipio, dirección, horario ("" = 24 h),
pago con tarjeta (0/1), conectores [[tipo, kW, cuántos], ...]]
Tipos de conector: CCS, CHA (CHAdeMO), T2 (Tipo 2), T1, SCH (enchufe doméstico), CEE (industrial), T3.

Los cargadores de un mismo operador a menos de 40 m se juntan en un solo sitio (el registro da uno por poste).
Se publica como versión "recarga" (no en el historial de git).
"""
import gzip
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

URL = "https://nap.dgt.es/datex2/v3/miterd/EnergyInfrastructureTablePublication/electrolineras.xml"

# Marca comercial por palabras de la razón social (lo primero que coincida)
MARCAS = [
    ("Iberdrola | bp pulse", ["CHARGING TOGETHER"]),
    ("Iberdrola", ["IBERDROLA"]),
    ("Endesa X Way", ["ENDESA"]),
    ("Repsol", ["REPSOL"]),
    ("Zunder", ["ZUNDER", "EASYCHARG"]),
    ("Tesla", ["TESLA"]),
    ("Ionity", ["IONITY"]),
    ("Wenea", ["WENEA"]),
    ("EDP", ["EDP "]),
    ("TotalEnergies", ["TOTALENERGIES", "TOTAL ENERGIES"]),
    ("Acciona", ["ACCIONA"]),
    ("Galp", ["GALP"]),
    ("Moeve (Cepsa)", ["CEPSA", "MOEVE"]),
    ("Plenoil", ["PLENOIL"]),
    ("Fenie Energía", ["FENIE"]),
    ("Etecnic", ["ETECNIC"]),
    ("Eranovum", ["ERANOVUM"]),
    ("Atlante", ["ATLANTE"]),
    ("Allego", ["ALLEGO"]),
    ("Fastned", ["FASTNED", "THE F CHARGING"]),
    ("Electra", ["CHARG-ELECTRA", "ELECTRA SPAIN"]),
    ("Powerdot", ["POWERDOT", "POWER DOT"]),
    ("Shell Recharge", ["SHELL"]),
    ("Naturgy", ["NATURGY"]),
    ("Carrefour", ["CARREFOUR"]),
    ("Costco", ["COSTCO"]),
    ("Bonpreu", ["BONPREU"]),
    ("Qwello", ["QWELLO"]),
    ("Maksu", ["MAKSU"]),
    ("Emovili", ["EMOVILI"]),
    ("Prio", ["PRIO RECHARGE"]),
    ("InstaVolt", ["INSTAVOLT"]),
    ("Endolla Barcelona", ["BARCELONA DE SERVEIS MUNICIPALS"]),
    ("Aena", ["AENA"]),
]

TIPOS = {"iec62196T2COMBO": "CCS", "iec62196T1COMBO": "CCS", "chademo": "CHA", "iec62196T2": "T2", "iec62196T1": "T1",
         "iec62196T3A": "T3", "iec62196T3C": "T3"}

SOCIEDAD = re.compile(r"[,.]?\s+\b(S\.?\s?L\.?\s?U?\.?|S\.?\s?A\.?\s?U?\.?|S\.?R\.?L\.?|SLU|SAU|S\.M\.E\.?,?\s*S\.A\.?)\s*\.?$", re.I)


def marca(razon: str) -> str:
    r = " " + razon.upper().strip() + " "
    for nombre, claves in MARCAS:
        if any(c in r for c in claves):
            return nombre
    n = razon.strip()
    for _ in range(2):
        n = SOCIEDAD.sub("", n).strip(" ,.")
    n = re.sub(r"\s+", " ", n)
    # las razones sociales vienen casi todas en mayúsculas
    if n.isupper() or n.islower():
        n = " ".join(p.capitalize() for p in n.split(" "))
        n = re.sub(r"\b(De|Del|La|Las|Los|Y|D')\b", lambda m: m.group(1).lower(), n)
        n = n[:1].upper() + n[1:]
    return n or "Otro"


def tipo(t: str) -> str:
    if t in TIPOS:
        return TIPOS[t]
    if t.startswith("domestic"):
        return "SCH"
    if t.startswith("iec60309"):
        return "CEE"
    return "OTR"


def kw(texto) -> float:
    try:
        v = float(texto)
    except (TypeError, ValueError):
        return 0.0
    # viene en vatios; algún dato suelto está en kW (60.0) o es absurdo (1 MW en un Tipo 2)
    if v < 1000:
        v *= 1000
    v /= 1000
    return 0.0 if v > 500 else v


DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
ABREV = ["L", "M", "X", "J", "V", "S", "D"]


def horario(label: str) -> str:
    """«Lunes (09:00 - 21:30) Martes (...)» -> «L-V 09:00-21:30»; todos los días a todas horas -> ""."""
    h = {}
    for dia, a, b in re.findall(r"(\w+)\s*\((\d\d:\d\d)\s*-\s*(\d\d:\d\d)\)", label or ""):
        d = dia.replace("é", "e").replace("á", "a").capitalize()
        if d in DIAS:
            h.setdefault(DIAS.index(d), []).append(f"{a}-{b}")
    if not h:
        return ""
    todo = lambda fr: all(f.startswith("00:00") and f.endswith(("23:59", "24:00", "00:00")) for f in fr)  # noqa: E731
    if len(h) == 7 and all(todo(fr) for fr in h.values()):
        return ""
    partes, i = [], 0
    while i < 7:
        if i not in h:
            i += 1
            continue
        j = i
        while j + 1 < 7 and h.get(j + 1) == h[i]:
            j += 1
        dias = ABREV[i] if i == j else f"{ABREV[i]}-{ABREV[j]}"
        fr = "24 h" if todo(h[i]) else " y ".join(sorted(h[i]))
        partes.append(f"{dias} {fr}")
        i = j + 1
    return ", ".join(partes)


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def texto(e, nombre):
    for x in e.iter():
        if local(x.tag) == nombre and x.text and x.text.strip():
            return x.text.strip()
    return None


def bajar() -> bytes:
    ultimo = None
    for intento in range(4):
        try:
            req = urllib.request.Request(URL, headers={"User-Agent": "atalaya-datos (github.com/FoxAstur)", "Accept-Encoding": "gzip"})
            with urllib.request.urlopen(req, timeout=300) as r:
                b = r.read()
                return gzip.decompress(b) if r.headers.get("Content-Encoding") == "gzip" else b
        except Exception as e:  # noqa: BLE001
            ultimo = e
            print(f"intento {intento + 1}: {e}", flush=True)
            time.sleep(30 * (intento + 1))
    raise ConnectionError(f"DGT: {ultimo}")


def leer(xml: bytes):
    """Un sitio por poste del registro: dict con operador, posición y conectores {(tipo, kW): n}."""
    sitios = []
    for _, e in ET.iterparse(__import__("io").BytesIO(xml), events=("end",)):
        if local(e.tag) != "energyInfrastructureSite":
            continue
        la = lo = None
        nombre = razon = None
        lineas = {}
        etiqueta = None
        pago = set()
        con = {}
        for h in e:
            t = local(h.tag)
            if t == "name" and nombre is None:
                nombre = texto(h, "value")
            elif t == "operatingHours":
                etiqueta = texto(h, "label")
            elif t == "locationReference":
                try:
                    la, lo = float(texto(h, "latitude")), float(texto(h, "longitude"))
                except (TypeError, ValueError):
                    pass
                for v in h.iter():
                    if local(v.tag) == "value" and v.text and ":" in v.text:
                        k, _, val = v.text.partition(":")
                        lineas[k.strip()] = val.strip()
            elif t == "operator":
                razon = texto(h, "value")
            elif t == "energyInfrastructureStation":
                for x in h.iter():
                    lx = local(x.tag)
                    if lx == "authenticationAndIdentificationMethods" and x.text:
                        pago.add(x.text.strip())
                    elif lx == "connector":
                        k = (tipo(texto(x, "connectorType") or ""), round(kw(texto(x, "maxPowerAtSocket"))))
                        con[k] = con.get(k, 0) + 1
        ident = e.get("id")
        e.clear()
        if la is None or lo is None or not (27 < la < 44.5 and -19 < lo < 5) or not con:
            continue
        sitios.append({"id": ident, "la": la, "lo": lo, "op": marca(razon or ""), "nombre": (nombre or "").strip(),
                       "mun": lineas.get("Municipio", ""), "dir": lineas.get("Dirección", ""), "h": horario(etiqueta or ""),
                       "tarjeta": bool(pago & {"creditCard", "debitCard", "nfc"}), "con": con})
    return sitios


def distancia(a, b) -> float:
    x = math.radians(b["lo"] - a["lo"]) * math.cos(math.radians((a["la"] + b["la"]) / 2))
    y = math.radians(b["la"] - a["la"])
    return math.hypot(x, y) * 6_371_000


def juntar(sitios, radio=40.0):
    """Postes del mismo operador a menos de [radio] metros: un solo sitio."""
    celdas = {}
    grupos = []
    for s in sorted(sitios, key=lambda s: s["id"] or ""):
        cy, cx = int(s["la"] * 1000), int(s["lo"] * 1000)
        g = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for c in celdas.get((cy + dy, cx + dx), ()):
                    if c["op"] == s["op"] and distancia(c, s) <= radio:
                        g = c
                        break
                if g:
                    break
            if g:
                break
        if g is None:
            g = dict(s, con=dict(s["con"]))
            grupos.append(g)
            celdas.setdefault((cy, cx), []).append(g)
        else:
            for k, n in s["con"].items():
                g["con"][k] = g["con"].get(k, 0) + n
            g["tarjeta"] = g["tarjeta"] or s["tarjeta"]
            if not g["h"] or not s["h"]:
                g["h"] = ""          # con un poste abierto siempre, el sitio lo está
    return grupos


OVERPASS_SERVIDORES = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
                       "https://overpass.private.coffee/api/interpreter"]
CONSULTA_OSM = ('[out:json][timeout:240];area["ISO3166-1"="ES"][admin_level=2]->.a;'
                '(node["amenity"="charging_station"](area.a);way["amenity"="charging_station"](area.a););out center tags;')
ENCHUFES_OSM = {"type2_combo": "CCS", "chademo": "CHA", "type2": "T2", "type2_cable": "T2", "type1": "T1", "schuko": "SCH",
                "cee_blue": "CEE", "tesla_supercharger": "CCS", "type3c": "T3"}


def osm():
    """Cargadores de OpenStreetMap con enchufes conocidos (los que faltan en el registro oficial, como algunos de
    supermercados). Si Overpass no contesta, lista vacía: se publica solo el registro."""
    datos = None
    ultimo = None
    for intento, url in enumerate(OVERPASS_SERVIDORES * 2):
        try:
            req = urllib.request.Request(url, data=urllib.parse.urlencode({"data": CONSULTA_OSM}).encode(),
                                         headers={"User-Agent": "atalaya-datos (github.com/FoxAstur/atalaya-datos)"})
            with urllib.request.urlopen(req, timeout=300) as r:
                datos = json.load(r)
            break
        except Exception as e:  # noqa: BLE001
            ultimo = e
            print(f"Overpass {url}: {e}", flush=True)
            time.sleep(20 * (intento + 1))
    if datos is None:
        print(f"::warning::OpenStreetMap no ha contestado ({ultimo}): solo el registro oficial", flush=True)
        return []
    sitios = []
    for el in datos.get("elements", []):
        t = el.get("tags", {})
        la = el.get("lat") or el.get("center", {}).get("lat")
        lo = el.get("lon") or el.get("center", {}).get("lon")
        if la is None or lo is None or t.get("access") in ("private", "no", "customers_only"):
            continue
        con = {}
        for clave, tipo_ in ENCHUFES_OSM.items():
            v = t.get(f"socket:{clave}")
            if not v or v == "no":
                continue
            try:
                n = int(v)
            except ValueError:
                n = 1
            potencia = kw(t.get(f"socket:{clave}:output", "")) or {"CCS": 50, "CHA": 50}.get(tipo_, 0)
            if potencia <= 0:
                continue
            k = (tipo_, round(potencia))
            con[k] = con.get(k, 0) + max(1, n)
        if not con:
            continue
        op = t.get("operator") or t.get("brand") or t.get("network") or "Otros"
        calle = " ".join(x for x in (t.get("addr:street", ""), t.get("addr:housenumber", "")) if x)
        oh = t.get("opening_hours", "")
        sitios.append({"id": f"osm:{el['type'][0]}{el['id']}", "la": la, "lo": lo, "op": marca(op), "nombre": (t.get("name") or t.get("brand") or op).strip(),
                       "mun": t.get("addr:city", ""), "dir": calle, "h": "" if oh == "24/7" else (oh[:40] or "Horario sin datos"),
                       "tarjeta": t.get("payment:credit_cards") == "yes" or t.get("payment:debit_cards") == "yes", "con": con})
    return sitios


def nuevos_de_osm(oficiales, de_osm, radio=80.0):
    """Los de OpenStreetMap que no están ya en el registro (nada oficial a menos de [radio] metros)."""
    celdas = {}
    for s in oficiales:
        celdas.setdefault((int(s["la"] * 500), int(s["lo"] * 500)), []).append(s)
    fuera = []
    for s in de_osm:
        cy, cx = int(s["la"] * 500), int(s["lo"] * 500)
        if not any(distancia(c, s) <= radio for dy in (-1, 0, 1) for dx in (-1, 0, 1) for c in celdas.get((cy + dy, cx + dx), ())):
            fuera.append(s)
    return fuera


def nombre_comun(n: str) -> str:
    # «Centro Porsche Baleares CP2» -> «Centro Porsche Baleares»; códigos de poste al final fuera
    return re.sub(r"\s*[-_ ]\s*(CP|PR|P|N[ºo]?)?\s*\d{1,3}$", "", n).strip() or n


def main() -> int:
    if len(sys.argv) > 1:
        xml = open(sys.argv[1], "rb").read()
    else:
        try:
            xml = bajar()
        except ConnectionError as e:
            print(f"::warning::{e}. Se mantienen los puntos publicados la vez anterior.", flush=True)
            return 3
    postes = leer(xml)
    sitios = juntar(postes)
    if len(sitios) < 4000:
        print(f"solo {len(sitios)} sitios ({len(postes)} postes): no se publica", flush=True)
        return 1
    extra = nuevos_de_osm(sitios, osm()) if "--sin-osm" not in sys.argv else []
    print(f"{len(extra)} cargadores de OpenStreetMap que no están en el registro", flush=True)
    sitios += extra
    cuenta = {}
    for s in sitios:
        cuenta[s["op"]] = cuenta.get(s["op"], 0) + 1
    operadores = sorted(cuenta, key=lambda o: (-cuenta[o], o))
    indice = {o: i for i, o in enumerate(operadores)}
    orden = {"CCS": 0, "CHA": 1, "T2": 2}
    lista = []
    for s in sitios:
        con = sorted(([t, k, n] for (t, k), n in s["con"].items()), key=lambda c: (-c[1], orden.get(c[0], 9)))
        lista.append([s["id"], round(s["la"], 5), round(s["lo"], 5), indice[s["op"]], nombre_comun(s["nombre"])[:60], s["mun"],
                      s["dir"][:70], s["h"], 1 if s["tarjeta"] else 0, con])
    os.makedirs("salida", exist_ok=True)
    o = {"generado": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
         "fuente": "Ministerio para la Transición Ecológica / DGT (Punto de Acceso Nacional) y © OpenStreetMap (ODbL)",
         "campos": ["id", "la", "lo", "operador", "nombre", "municipio", "direccion", "horario", "tarjeta", "conectores"],
         "operadores": operadores, "sitios": lista}
    with gzip.open("salida/recarga.json.gz", "wt", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, separators=(",", ":"))
    rapidos = sum(1 for s in lista if s[9][0][1] >= 50)
    print(f"{len(lista)} sitios de {len(postes)} postes, {len(operadores)} operadores, {rapidos} con 50 kW o más, "
          f"{os.path.getsize('salida/recarga.json.gz') / 1e3:.0f} kB", flush=True)
    print("; ".join(f"{o} {cuenta[o]}" for o in operadores[:25]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
