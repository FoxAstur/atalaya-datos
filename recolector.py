#!/usr/bin/env python3
"""
Recolector de Atalaya: junta todas las fuentes abiertas de radares y cámaras de control de España
en un único fichero (datos/radares.json) que la app descarga.

Fuentes (de más a menos fiable; ante duplicados manda la más oficial):
  1. DGT, feed DATEX II de radares (coordenadas oficiales).
  2. DGT, PDF "Puntos y tramos de control de velocidad": radares fijos y de tramo que falten en el feed
     (se sitúan por carretera + punto kilométrico con CartoCiudad del IGN) y longitud de cada tramo.
  3. DGT, PDF "Equipos automáticos de detección de infracciones": cámaras de cinturón/móvil,
     línea continua, foto-rojo y video-stop (situadas por PK con CartoCiudad).
  4. Servei Català de Trànsit (Cataluña), Ayuntamiento de Madrid, Ayuntamiento de València.
  5. OpenStreetMap: radares municipales, País Vasco, semáforos, stop/ceda, tramos.
  6. Tramos de vigilancia con radar móvil (PDF DGT geolocalizado por el proyecto radares-datos).

Cada fuente que falle conserva sus datos de la última ejecución correcta.
Se asigna comunidad, provincia y municipio con el geocodificador inverso de CartoCiudad (con caché),
y el límite de velocidad de la vía con OpenStreetMap cuando la fuente no lo trae.
"""
from __future__ import annotations

import csv
import gzip
import io
import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

UA = "AtalayaRecolector/1.0 (+https://github.com/FoxAstur/atalaya-datos)"
SALIDA = "datos/radares.json"
INFORME = "datos/INFORME.md"
CACHE_GEO = "cache/geocodificacion.json"
CACHE_REV = "cache/regiones.json"
CACHE_VEL = "cache/limites.json"

URL_DGT_FEED = "https://nap.dgt.es/datex2/dgt/PredefinedLocationsPublication/radares/content.xml"
URL_DGT_PAGINA = "https://www.dgt.es/conoce-el-estado-del-trafico/vigilancia-y-control/equipos-y-tramos-de-vigilancia/"
URL_SCT = "https://analisi.transparenciacatalunya.cat/resource/re3y-fftf.json?$limit=5000"
URL_MADRID = ("https://datos.madrid.es/dataset/300049-0-radares-fijos-moviles/resource/"
              "300049-1-radares-fijos-moviles-csv/download/300049-1-radares-fijos-moviles-csv.csv")
URL_ZONAS = "https://raw.githubusercontent.com/secretariacyas-crypto/radares-datos/main/mobile_zones.json"
OVERPASS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"]
CARTO_CAND = "https://www.cartociudad.es/geocoder/api/geocoder/candidates"
CARTO_FIND = "https://www.cartociudad.es/geocoder/api/geocoder/find"
CARTO_REV = "https://www.cartociudad.es/geocoder/api/geocoder/reverseGeocode"

LOG: list[str] = []
MUESTRA_REV: list[int] = []
INICIO = time.time()
# Cada ejecución consulta servicios externos como mucho este tiempo; lo que falte se completa
# en la siguiente (todo queda en caché), así nunca se pasa del límite de GitHub Actions.
PRESUPUESTO_GEO_S = 50 * 60
PRESUPUESTO_TOTAL_S = 85 * 60


def queda(segundos: float) -> bool:
    return time.time() - INICIO < segundos


def log(msg: str) -> None:
    print(msg, flush=True)
    LOG.append(msg)
    # registro en curso: si la ejecución se corta, se publica igualmente y se ve dónde se quedó
    try:
        os.makedirs("datos", exist_ok=True)
        with open("datos/REGISTRO.txt", "a", encoding="utf-8") as f:
            f.write(f"{time.time() - INICIO:7.0f}s  {msg}\n")
    except OSError:
        pass


# --------------------------------------------------------------------------------------- HTTP
def http(url: str, data: bytes | None = None, timeout: int = 120, intentos: int = 4,
         cabeceras: dict | None = None) -> bytes:
    ultimo = None
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **(cabeceras or {})})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                cuerpo = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    cuerpo = gzip.decompress(cuerpo)
                return cuerpo
        except Exception as e:  # noqa: BLE001
            ultimo = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"{urllib.parse.urlparse(url).netloc}: {ultimo}")


def http_json(url: str, **kw):
    return json.loads(http(url, **kw).decode("utf-8"))


# ------------------------------------------------------------------------------------- caché
def cargar_json(ruta: str, defecto):
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return defecto


def guardar_json(ruta: str, obj, compacto: bool = False) -> None:
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        if compacto:
            json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
        else:
            json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, ruta)


# ------------------------------------------------------------------------------------ geografía
def distancia(lat1, lon1, lat2, lon2) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def rumbo_entre(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def en_espana(lat, lon) -> bool:
    return (35.0 <= lat <= 44.5 and -10.0 <= lon <= 5.0) or (27.4 <= lat <= 29.6 and -18.5 <= lon <= -13.2)


def utm_a_latlon(x: float, y: float, huso: int):
    a, f, k0 = 6378137.0, 1 / 298.257222101, 0.9996
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)
    m = y / k0
    mu = m / (a * (1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256))
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    p1 = (mu + (3 * e1 / 2 - 27 * e1 ** 3 / 32) * math.sin(2 * mu)
          + (21 * e1 ** 2 / 16 - 55 * e1 ** 4 / 32) * math.sin(4 * mu)
          + (151 * e1 ** 3 / 96) * math.sin(6 * mu) + (1097 * e1 ** 4 / 512) * math.sin(8 * mu))
    n1 = a / math.sqrt(1 - e2 * math.sin(p1) ** 2)
    t1, c1 = math.tan(p1) ** 2, ep2 * math.cos(p1) ** 2
    r1 = a * (1 - e2) / (1 - e2 * math.sin(p1) ** 2) ** 1.5
    d = (x - 500000.0) / (n1 * k0)
    lat = p1 - (n1 * math.tan(p1) / r1) * (d * d / 2 - (5 + 3 * t1 + 10 * c1 - 4 * c1 ** 2 - 9 * ep2) * d ** 4 / 24
                                           + (61 + 90 * t1 + 298 * c1 + 45 * t1 ** 2 - 252 * ep2 - 3 * c1 ** 2) * d ** 6 / 720)
    lon0 = math.radians((huso - 1) * 6 - 180 + 3)
    lon = lon0 + (d - (1 + 2 * t1 + c1) * d ** 3 / 6
                  + (5 - 2 * c1 + 28 * t1 - 3 * c1 ** 2 + 8 * ep2 + 24 * t1 ** 2) * d ** 5 / 120) / math.cos(p1)
    return math.degrees(lat), math.degrees(lon)


# ------------------------------------------------------------------------------------ regiones
PROVINCIAS = {  # nombre canónico: (código INE, comunidad)
    "Álava": ("01", "País Vasco"), "Albacete": ("02", "Castilla-La Mancha"), "Alicante": ("03", "Comunitat Valenciana"),
    "Almería": ("04", "Andalucía"), "Ávila": ("05", "Castilla y León"), "Badajoz": ("06", "Extremadura"),
    "Illes Balears": ("07", "Illes Balears"), "Barcelona": ("08", "Cataluña"), "Burgos": ("09", "Castilla y León"),
    "Cáceres": ("10", "Extremadura"), "Cádiz": ("11", "Andalucía"), "Castellón": ("12", "Comunitat Valenciana"),
    "Ciudad Real": ("13", "Castilla-La Mancha"), "Córdoba": ("14", "Andalucía"), "A Coruña": ("15", "Galicia"),
    "Cuenca": ("16", "Castilla-La Mancha"), "Girona": ("17", "Cataluña"), "Granada": ("18", "Andalucía"),
    "Guadalajara": ("19", "Castilla-La Mancha"), "Gipuzkoa": ("20", "País Vasco"), "Huelva": ("21", "Andalucía"),
    "Huesca": ("22", "Aragón"), "Jaén": ("23", "Andalucía"), "León": ("24", "Castilla y León"), "Lleida": ("25", "Cataluña"),
    "La Rioja": ("26", "La Rioja"), "Lugo": ("27", "Galicia"), "Madrid": ("28", "Comunidad de Madrid"),
    "Málaga": ("29", "Andalucía"), "Murcia": ("30", "Región de Murcia"), "Navarra": ("31", "Comunidad Foral de Navarra"),
    "Ourense": ("32", "Galicia"), "Asturias": ("33", "Principado de Asturias"), "Palencia": ("34", "Castilla y León"),
    "Las Palmas": ("35", "Canarias"), "Pontevedra": ("36", "Galicia"), "Salamanca": ("37", "Castilla y León"),
    "Santa Cruz de Tenerife": ("38", "Canarias"), "Cantabria": ("39", "Cantabria"), "Segovia": ("40", "Castilla y León"),
    "Sevilla": ("41", "Andalucía"), "Soria": ("42", "Castilla y León"), "Tarragona": ("43", "Cataluña"),
    "Teruel": ("44", "Aragón"), "Toledo": ("45", "Castilla-La Mancha"), "Valencia": ("46", "Comunitat Valenciana"),
    "Valladolid": ("47", "Castilla y León"), "Bizkaia": ("48", "País Vasco"), "Zamora": ("49", "Castilla y León"),
    "Zaragoza": ("50", "Aragón"), "Ceuta": ("51", "Ceuta"), "Melilla": ("52", "Melilla"),
}


def normalizar(s: str) -> str:
    s = unicodedata.normalize("NFD", (s or "").strip().lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn").replace("�", "")


ALIAS = {normalizar(k): k for k in PROVINCIAS}
ALIAS.update({
    "alacant": "Alicante", "alicante/alacant": "Alicante", "castello": "Castellón", "castellon/castello": "Castellón",
    "castello de la plana": "Castellón", "valencia/valencia": "Valencia", "la coruna": "A Coruña", "coruna": "A Coruña",
    "coruna (a)": "A Coruña", "a coruna": "A Coruña", "orense": "Ourense", "gerona": "Girona", "lerida": "Lleida",
    "baleares": "Illes Balears", "islas baleares": "Illes Balears", "balears": "Illes Balears", "balears (illes)": "Illes Balears",
    "araba": "Álava", "araba/alava": "Álava", "alava": "Álava", "guipuzcoa": "Gipuzkoa", "vizcaya": "Bizkaia",
    "nafarroa": "Navarra", "rioja (la)": "La Rioja", "rioja": "La Rioja", "palmas (las)": "Las Palmas", "palmas": "Las Palmas",
    "tenerife": "Santa Cruz de Tenerife", "s.c. tenerife": "Santa Cruz de Tenerife", "sta. cruz de tenerife": "Santa Cruz de Tenerife",
    "murcia (region de)": "Murcia", "region de murcia": "Murcia", "madrid (comunidad de)": "Madrid",
    "asturias (principado de)": "Asturias", "principado de asturias": "Asturias", "navarra (comunidad foral de)": "Navarra",
})


def provincia_canonica(nombre: str | None) -> str | None:
    if not nombre:
        return None
    n = normalizar(nombre)
    if n in ALIAS:
        return ALIAS[n]
    for parte in re.split(r"[/(]", n):
        p = parte.strip(" )")
        if p in ALIAS:
            return ALIAS[p]
    # caracteres rotos del PDF ("C?ceres"): comparación con comodín
    patron = re.compile("^" + re.escape(n).replace("\\?", ".") + "$")
    for k, v in ALIAS.items():
        if patron.match(k):
            return v
    return None


def provincia_por_codigo(cod: str | None) -> str | None:
    if not cod:
        return None
    cod = str(cod).zfill(2)[:2]
    for k, (c, _) in PROVINCIAS.items():
        if c == cod:
            return k
    return None


# ---------------------------------------------------------------------------------- carreteras
ROMANOS = [("VIII", 8), ("VII", 7), ("III", 3), ("IV", 4), ("VI", 6), ("II", 2), ("IX", 9), ("V", 5), ("X", 10), ("I", 1)]


def via_normalizada(v: str | None) -> str:
    """'A7', 'a-7', 'A 7' → 'A-7'; 'N-VI' → 'N-6'; 'NVI' → 'N-6'."""
    if not v:
        return ""
    s = v.upper().replace(" ", "").replace("_", "-")
    m = re.match(r"^([A-Z]+)-?([0-9][0-9A-Z.]*)$", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    m = re.match(r"^N-?([IVX]+)([A-Z]?)$", s)
    if m:
        for rom, num in ROMANOS:
            if m.group(1) == rom:
                return f"N-{num}{m.group(2)}"
    return s


def variantes_via(v: str) -> list[str]:
    """Nombres con los que buscar una vía en CartoCiudad."""
    n = via_normalizada(v)
    out = [n]
    m = re.match(r"^N-(\d+)([A-Z]?)$", n)
    if m and int(m.group(1)) <= 10:  # nacionales radiales: CartoCiudad puede usar N-VI o N-6
        rom = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X"}[int(m.group(1))]
        out.append(f"N-{rom}{m.group(2)}")
    if v.upper() not in out:
        out.append(v.upper())
    return out


# -------------------------------------------------------------------------- CartoCiudad (PK)
class Geocodificador:
    """Sitúa (provincia, carretera, PK) con los hitos kilométricos de CartoCiudad, con caché persistente."""

    def __init__(self):
        self.cache: dict = cargar_json(CACHE_GEO, {})
        self.nuevas = 0
        self.agotado = False

    def precargar(self, peticiones: set) -> None:
        """Consulta en paralelo todos los hitos (vía, km, provincia) que aún no estén en caché."""
        pend = [p for p in peticiones if f"{p[0]}|{p[1]}|{p[2] or ''}" not in self.cache]
        log(f"  CartoCiudad: {len(peticiones)} hitos necesarios, {len(pend)} por consultar")
        with ThreadPoolExecutor(8) as ex:
            for i, _ in enumerate(ex.map(lambda p: self._hito(*p), pend)):
                if i and i % 300 == 0:
                    self.guardar()
                    log(f"    {i}/{len(pend)}")
        self.guardar()

    def _hito(self, via: str, km: int, provincia: str | None):
        clave = f"{via}|{km}|{provincia or ''}"
        if clave in self.cache:
            return self.cache[clave]
        if not queda(PRESUPUESTO_GEO_S):
            self.agotado = True
            return None
        cod = PROVINCIAS.get(provincia, (None, None))[0] if provincia else None
        res = None
        for nombre in variantes_via(via):
            params = {"q": f"{nombre} {km}", "limit": 15}
            try:
                cands = http_json(f"{CARTO_CAND}?{urllib.parse.urlencode(params)}", timeout=40, intentos=2)
            except Exception:  # noqa: BLE001
                cands = []
            objetivo = re.sub(r"[-\s]", "", nombre.upper())
            mejores = []
            for c in cands or []:
                m = re.match(r"^(\S+)\s+km\s+(\d+)", str(c.get("address", "")), re.I)
                if not m or int(m.group(2)) != km:
                    continue
                if re.sub(r"[-\s]", "", m.group(1).upper()) != objetivo:
                    continue
                if c.get("lat") is None or c.get("lng") is None:
                    continue
                mejores.append(c)
            if cod:
                en_prov = [c for c in mejores if str(c.get("provinceCode", "")).zfill(2) == cod]
                mejores = en_prov or mejores
            if mejores:
                c = mejores[0]
                res = [float(c["lat"]), float(c["lng"])]
                break
        self.cache[clave] = res
        self.nuevas += 1
        return res

    def pk(self, via: str, pk: float, provincia: str | None):
        """Coordenada interpolada entre los hitos km⌊pk⌋ y km⌊pk⌋+1."""
        k = int(math.floor(pk))
        a = self._hito(via, k, provincia)
        b = self._hito(via, k + 1, provincia)
        f = pk - k
        if a and b and distancia(a[0], a[1], b[0], b[1]) < 3000:
            return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f]
        if a and f < 0.5:
            return a
        if b and f >= 0.5:
            return b
        return a or b

    def rumbo(self, via: str, pk: float, provincia: str | None, sentido: str | None):
        """Rumbo (grados) de la circulación en ese PK y sentido; None si no se puede saber."""
        if sentido not in ("Creciente", "Decreciente"):
            return None
        k = int(math.floor(pk))
        for a_km, b_km in ((k, k + 1), (k - 1, k), (k + 1, k + 2)):
            if a_km < 0:
                continue
            a, b = self._hito(via, a_km, provincia), self._hito(via, b_km, provincia)
            if a and b and 50 < distancia(a[0], a[1], b[0], b[1]) < 3000:
                rb = rumbo_entre(a[0], a[1], b[0], b[1])
                return round((rb + 180) % 360 if sentido == "Decreciente" else rb, 1)
        return None

    def direccion(self, texto: str):
        clave = f"dir|{texto}"
        if clave in self.cache:
            return self.cache[clave]
        res = None
        try:
            r = http_json(f"{CARTO_FIND}?{urllib.parse.urlencode({'q': texto})}", timeout=40, intentos=2)
            if isinstance(r, dict) and r.get("lat") and r.get("lng"):
                res = [float(r["lat"]), float(r["lng"])]
        except Exception:  # noqa: BLE001
            pass
        self.cache[clave] = res
        self.nuevas += 1
        return res

    def guardar(self):
        guardar_json(CACHE_GEO, self.cache)


# ------------------------------------------------------------------------------- modelo común
def punto(id_, tipo, fuente, lat, lon, **kw) -> dict:
    p = {"id": id_, "t": tipo, "f": fuente, "la": round(lat, 6), "lo": round(lon, 6)}
    for k, v in kw.items():
        if v is not None and v != "":
            p[k] = v
    return p


# ------------------------------------------------------------------------------ 1. DGT (feed)
def fuente_dgt_feed() -> list[dict]:
    import xml.etree.ElementTree as ET
    raiz = ET.fromstring(http(URL_DGT_FEED, timeout=180))

    def local(tag):
        return tag.rsplit("}", 1)[-1]

    salida = []
    for el in raiz.iter():
        if local(el.tag) != "predefinedLocation" or "id" not in el.attrib:
            continue
        lats, lons, dists, campos = [], [], [], {}
        for h in el.iter():
            n = local(h.tag)
            t = (h.text or "").strip()
            if not t:
                continue
            if n == "latitude":
                lats.append(float(t))
            elif n == "longitude":
                lons.append(float(t))
            elif n == "referencePointDistance":
                dists.append(float(t))
            else:
                campos.setdefault(n.lower(), t)
        if not lats or not lons or not en_espana(lats[0], lons[0]):
            continue
        id_ = el.attrib["id"]
        nombre = campos.get("value")
        tramo = len(lats) >= 2 and distancia(lats[0], lons[0], lats[-1], lons[-1]) > 200
        pista_tramo = "TRAMO" in id_.upper() or (nombre and "tramo" in nombre.lower())
        sentido_raw = (campos.get("directionrelative") or campos.get("directionbound") or "").lower()
        sentido = ("Creciente" if any(x in sentido_raw for x in ("pos", "align", "crec"))
                   else "Decreciente" if any(x in sentido_raw for x in ("neg", "opp", "decre"))
                   else "Ambos" if "both" in sentido_raw else None)
        salida.append(punto(
            f"dgt:{id_}", "RADAR_TRAMO" if (tramo or pista_tramo) else "RADAR_FIJO", "DGT", lats[0], lons[0],
            la2=round(lats[-1], 6) if tramo else None, lo2=round(lons[-1], 6) if tramo else None,
            c=via_normalizada(campos.get("roadnumber")) or None,
            pk=round(dists[0] / 1000, 3) if dists else None,
            s=sentido, n=nombre,
        ))
    return salida


# --------------------------------------------------------------------------------- PDFs DGT
def enlaces_pdf_dgt() -> dict:
    html = http(URL_DGT_PAGINA, timeout=60).decode("utf-8", "replace")
    out = {}
    for href in re.findall(r'href="([^"]+\.pdf)"', html, re.I):
        url = urllib.parse.urljoin(URL_DGT_PAGINA, href)
        if "CINEMOMETROS" in href.upper():
            out.setdefault("cinemometros", url)
        elif "EQUIPOS" in href.upper():
            out.setdefault("equipos", url)
    return out


def lineas_pdf(datos: bytes) -> list[str]:
    import pdfplumber
    lineas = []
    with pdfplumber.open(io.BytesIO(datos)) as pdf:
        for pag in pdf.pages:
            lineas.extend((pag.extract_text() or "").splitlines())
    return [l.strip() for l in lineas if l.strip()]


RE_CINEMO = re.compile(
    r"^(?P<resto>.+?)\s+Radar\s+(?P<tipo>Fijo|M\S{0,2}vil|Tramo)\s+(?P<pk>[\d.,]+(?:\s*-\s*[\d.,]+)?)"
    r"\s+(?P<sentido>Creciente|Decreciente|Ambos)(?:\s+(?P<fecha>\d{2}/\d{2}/\d{4}))?", re.I)
RE_LONGITUD = re.compile(r"^\(?\s*([\d.,]+)\s*m\s*\)?$")


def num_km(s: str) -> float:
    return float(s.replace(",", "."))


def parsear_cinemometros(lineas: list[str]) -> list[dict]:
    filas = []
    for i, l in enumerate(lineas):
        m = RE_CINEMO.match(l)
        if not m:
            # longitud de tramo en la línea siguiente: "(5.638 m)"
            ml = RE_LONGITUD.match(l)
            if ml and filas and filas[-1]["tipo"] == "Tramo" and filas[-1].get("longitud") is None:
                filas[-1]["longitud"] = float(ml.group(1).replace(".", "").replace(",", "."))
            continue
        partes = m.group("resto").split()
        if len(partes) < 2:
            continue
        via = partes[-1]
        prov = " ".join(partes[:-1])
        tipo = m.group("tipo").capitalize()
        tipo = "Movil" if tipo.lower().startswith("m") else tipo
        pk_txt = m.group("pk")
        fila = {"prov": prov, "via": via, "tipo": tipo, "sentido": m.group("sentido").capitalize(),
                "fecha": m.group("fecha"), "longitud": None}
        if " - " in pk_txt or "-" in pk_txt.strip("-"):
            a, b = [num_km(x) for x in re.split(r"\s*-\s*", pk_txt) if x]
            fila["pk"], fila["pk2"] = min(a, b), max(a, b)
        else:
            fila["pk"] = num_km(pk_txt)
        # a veces la longitud viene en la misma línea, detrás
        ml = re.search(r"\(([\d.,]+)\s*m\)", l)
        if ml:
            fila["longitud"] = float(ml.group(1).replace(".", "").replace(",", "."))
        filas.append(fila)
    return filas


RE_EQUIPO = re.compile(r"^(?P<prov>.+?)\s+(?P<via>\S+)\s+(?P<pk>\d+(?:[.,]\d+)?)\s+(?P<sentido>C|D|A|Ambos)\s+(?P<equipo>.+)$")


def parsear_equipos(lineas: list[str]) -> list[dict]:
    filas = []
    for l in lineas:
        if l.upper().startswith(("PROVINCIA", "LISTADO", "PÁGINA", "PAGINA")):
            continue
        m = RE_EQUIPO.match(l)
        if not m:
            continue
        filas.append({"prov": m.group("prov"), "via": m.group("via"), "pk": num_km(m.group("pk")),
                      "sentido": {"C": "Creciente", "D": "Decreciente"}.get(m.group("sentido"), "Ambos"),
                      "equipo": m.group("equipo").strip()})
    return filas


def tipo_equipo(e: str) -> tuple[str, str]:
    n = normalizar(e)
    if "rojo" in n or "semaf" in n:
        return "SEMAFORO", "Cámara de semáforo en rojo"
    if "stop" in n or "ceda" in n:
        return "STOP_CEDA", "Cámara de stop"
    if "cintur" in n or "movil" in n:
        return "OTRA_CAMARA", "Cámara de cinturón y móvil"
    if "linea" in n or "continua" in n:
        return "OTRA_CAMARA", "Cámara de línea continua"
    return "OTRA_CAMARA", f"Cámara: {e}"


# ------------------------------------------------------------------------------- otras fuentes
URL_SCT_CSV = "https://analisi.transparenciacatalunya.cat/api/views/re3y-fftf/rows.csv?accessType=DOWNLOAD"
URL_SCT_TXT = "https://transit.gencat.cat/web/.content/documents/seguretat_viaria/radars.txt"


def sct_texto(texto: str) -> list[dict]:
    """Lector genérico del CSV/TXT de radares del SCT: detecta vía, UTM y velocidad por su forma."""
    salida = []
    lineas = [l for l in texto.splitlines() if l.strip()]
    if not lineas:
        return salida
    log("  SCT muestra: " + " | ".join(repr(l[:120]) for l in lineas[:3]))
    sep = max(["\t", ";", ","], key=lambda c: lineas[0].count(c))
    if lineas[0].count(sep) == 0:
        sep = None  # columnas separadas por espacios (como lee R con read.table)
    for l in lineas:
        trozos = l.split(sep) if sep else re.split(r"\s+", l.strip())
        campos = [c.strip().strip('"') for c in trozos]
        nums = []
        for c in campos:
            try:
                nums.append(float(c.replace(",", ".")))
            except ValueError:
                pass
        x = next((n for n in nums if 250000 <= n <= 550000), None)
        y = next((n for n in nums if 4450000 <= n <= 4760000), None)
        la = next((n for n in nums if 40.4 <= n <= 42.9), None)
        lo = next((n for n in nums if 0.1 <= n <= 3.4), None)
        if x and y:
            la, lo = utm_a_latlon(x, y, 31)
        if la is None or lo is None or not en_espana(la, lo):
            continue
        vel = next((int(n) for n in nums if n in (20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120)), None)
        via = next((c for c in campos if re.match(r"^[A-Z]{1,4}-?\d+[A-Z]?$", c.upper())), None)
        salida.append(punto(f"sct:{la:.5f},{lo:.5f}", "RADAR_FIJO", "SCT", la, lo,
                            c=via_normalizada(via) if via else None, v=vel, ca="Cataluña"))
    return salida


def fuente_sct() -> list[dict]:
    try:
        datos = http_json(URL_SCT, timeout=90, intentos=2)
    except Exception as e:  # noqa: BLE001
        log(f"  SCT JSON: {e}; pruebo CSV y TXT")
        for url in (URL_SCT_CSV, URL_SCT_TXT):
            try:
                b = http(url, timeout=90, intentos=2)
                try:
                    t = b.decode("utf-8")
                except UnicodeDecodeError:
                    t = b.decode("latin-1")
                r = sct_texto(t)
                log(f"  SCT {url.rsplit('/', 1)[-1][:30]}: {len(r)} radares")
                if r:
                    return r
            except Exception as e2:  # noqa: BLE001
                log(f"  SCT {url}: {e2}")
        raise
    salida = []
    for i, o in enumerate(datos):
        lat = lon = x = y = None
        via = vel = nombre = None
        for k, v in o.items():
            kl = k.lower()
            if isinstance(v, dict):
                try:
                    lat = float(v.get("latitude")); lon = float(v.get("longitude"))
                except Exception:  # noqa: BLE001
                    c = v.get("coordinates")
                    if c and len(c) >= 2:
                        lon, lat = float(c[0]), float(c[1])
                continue
            s = str(v).strip()
            try:
                num = float(s.replace(",", "."))
            except ValueError:
                num = None
            if "lat" in kl and num is not None:
                lat = num
            elif ("lon" in kl or "lng" in kl) and num is not None:
                lon = num
            elif num is not None and 250000 <= num <= 550000 and ("x" in kl or "utm" in kl):
                x = num
            elif num is not None and 4450000 <= num <= 4760000 and ("y" in kl or "utm" in kl):
                y = num
            elif ("veloc" in kl or "vmax" in kl or "limit" in kl) and num is not None:
                vel = int(num)
            elif kl == "via" or "carretera" in kl or "via" in kl:
                via = s
            elif nombre is None and ("nom" in kl or "denom" in kl or "municipi" in kl):
                nombre = s
        if (lat is None or lon is None) and x and y:
            lat, lon = utm_a_latlon(x, y, 31)
        if lat is None or lon is None or not en_espana(lat, lon):
            continue
        salida.append(punto(f"sct:{lat:.5f},{lon:.5f}", "RADAR_FIJO", "SCT", lat, lon,
                            c=via_normalizada(via) or via, v=vel if vel and 10 <= vel <= 150 else None,
                            n=nombre, ca="Cataluña"))
    return salida


def fuente_madrid() -> list[dict]:
    b = http(URL_MADRID, timeout=90)
    try:
        texto = b.decode("utf-8")
    except UnicodeDecodeError:
        texto = b.decode("latin-1")
    texto = texto.lstrip("﻿")
    primera = texto.splitlines()[0]
    sep = ";" if primera.count(";") >= primera.count(",") else ","
    filas = list(csv.reader(io.StringIO(texto), delimiter=sep))
    cab = [normalizar(c) for c in filas[0]]

    def col(*pistas):
        for i, c in enumerate(cab):
            if any(p in c for p in pistas):
                return i
        return -1

    i_lat, i_lon = col("latitud"), col("longitud")
    i_x, i_y = col("utm_x", "coordenada x", "coord_x", "x ("), col("utm_y", "coordenada y", "coord_y", "y (")
    i_tipo, i_via, i_pk = col("tipo"), col("ubicacion", "via", "calle", "carretera"), col("pk", "punto kilom")
    i_sent, i_vel = col("sentido"), col("velocidad", "limite")
    log(f"  Madrid columnas: {filas[0]}")

    def v(f, i):
        return f[i].strip() if 0 <= i < len(f) and f[i].strip() else None

    def n(f, i):
        try:
            return float(v(f, i).replace(",", "."))
        except Exception:  # noqa: BLE001
            return None

    salida = []
    for f in filas[1:]:
        lat, lon = n(f, i_lat), n(f, i_lon)
        if (lat is None or lon is None or not en_espana(lat, lon)) and n(f, i_x) and n(f, i_y):
            lat, lon = utm_a_latlon(n(f, i_x), n(f, i_y), 30)
        if lat is None or lon is None or not en_espana(lat, lon):
            continue
        t = normalizar(v(f, i_tipo) or "")
        tipo = ("RADAR_TRAMO" if "tramo" in t else "ZONA_MOVIL" if "movil" in t
                else "SEMAFORO" if "semaf" in t or "rojo" in t else "RADAR_FIJO")
        vel = n(f, i_vel)
        salida.append(punto(f"mad:{lat:.5f},{lon:.5f}", tipo, "AYUNTAMIENTO", lat, lon,
                            c=v(f, i_via), pk=n(f, i_pk), s=v(f, i_sent),
                            v=int(vel) if vel and 10 <= vel <= 150 else None,
                            n="Ayuntamiento de Madrid", mu="Madrid", pr="Madrid", ca="Comunidad de Madrid"))
    return salida


VALENCIA = [
    "Avenida de los Hermanos Machado, Valencia", "Avenida Antonio Ferrandis, Valencia",
    "Camí Nou de Picanya 49, Valencia", "Avenida Fernando Abril Martorell, Valencia",
    "Avenida de los Naranjos 8, Valencia", "Avenida del Maestro Rodrigo 84, Valencia",
]


def fuente_valencia(geo: Geocodificador) -> list[dict]:
    salida = []
    for i, d in enumerate(VALENCIA):
        c = geo.direccion(d)
        if c and en_espana(*c):
            salida.append(punto(f"vlc:{i}", "RADAR_FIJO", "AYUNTAMIENTO", c[0], c[1], c=d.split(",")[0],
                                n="Cabina de radar del Ayuntamiento (el cinemómetro rota entre cabinas)",
                                mu="València", pr="Valencia", ca="Comunitat Valenciana"))
    return salida


def overpass(consulta: str) -> dict:
    ultimo = None
    for s in OVERPASS:
        try:
            return json.loads(http(s, data=urllib.parse.urlencode({"data": consulta}).encode(), timeout=300, intentos=2))
        except Exception as e:  # noqa: BLE001
            ultimo = e
    raise RuntimeError(f"Overpass: {ultimo}")


def clasificar_osm(v: str | None) -> str | None:
    v = (v or "").lower().strip()
    if not v:
        return None
    if v in ("maxspeed", "speed", "speed_camera", "minspeed"):
        return "RADAR_FIJO"
    if v in ("average_speed", "section", "section_control"):
        return "RADAR_TRAMO"
    if v in ("traffic_signals", "red_light", "traffic_light"):
        return "SEMAFORO"
    if v in ("stop", "give_way", "yield", "priority"):
        return "STOP_CEDA"
    if v in NOMBRES_CAMARA_OSM:
        return "OTRA_CAMARA"
    # peajes, aparcamiento, ruido, pesos, alturas, control de acceso a un recinto…: no son multas de conducción
    return None


# Cámaras de OSM que sí multan al conducir, con el nombre que entiende la app (cinturón, línea, ZBE…)
NOMBRES_CAMARA_OSM = {
    "access": "Cámara de acceso a zona restringida o ZBE (lee matrículas)",
    "seatbelt": "Cámara de cinturón y móvil", "seat_belt": "Cámara de cinturón y móvil",
    "mobile_phone": "Cámara de cinturón y móvil", "phone": "Cámara de cinturón y móvil",
    "handheld": "Cámara de cinturón y móvil",
    "overtaking": "Cámara de línea continua", "continuous_line": "Cámara de línea continua",
    "lane": "Cámara de carril reservado", "bus_lane": "Cámara de carril bus",
    "mindistance": "Cámara de distancia de seguridad", "min_distance": "Cámara de distancia de seguridad",
    "traffic": "Cámara de control de tráfico",
}


def nombre_camara_osm(tags: dict) -> str | None:
    if tags.get("name"):
        return tags.get("name")
    return NOMBRES_CAMARA_OSM.get(str(tags.get("enforcement") or "").lower().strip())


def limite(tags: dict | None):
    s = (tags or {}).get("maxspeed", "").strip()
    return int(s) if s.isdigit() and 10 <= int(s) <= 150 else None


CARDINALES = {"n": 0, "nne": 22.5, "ne": 45, "ene": 67.5, "e": 90, "ese": 112.5, "se": 135, "sse": 157.5,
              "s": 180, "ssw": 202.5, "sw": 225, "wsw": 247.5, "w": 270, "wnw": 292.5, "nw": 315, "nnw": 337.5}


def direccion_osm(tags: dict) -> dict:
    """Sentido que vigila un nodo de OSM: forward/backward (respecto a su vía, se resuelve en caminos.py)
    o grados/cardinal (se calibra contra los radares oficiales antes de usarlo)."""
    for k in ("direction", "camera:direction", "traffic_signals:direction"):
        v = str(tags.get(k) or "").strip().lower()
        if not v:
            continue
        if v in ("forward", "backward"):
            return {"_dir": v}
        if v in CARDINALES:
            return {"_dirg": CARDINALES[v]}
        try:
            g = float(v)
            if 0 <= g <= 360:
                return {"_dirg": g % 360}
        except ValueError:
            pass
    return {}


def fuente_osm() -> list[dict]:
    q = """
[out:json][timeout:280];
area["ISO3166-1"="ES"]["admin_level"="2"]->.es;
(
  node["highway"="speed_camera"](area.es);
  node["enforcement"](area.es);
  node["speed_camera"](area.es);
);
out meta;
rel["type"="enforcement"](area.es);
out geom;
"""
    d = overpass(q)
    por_id: dict[str, dict] = {}
    for e in d.get("elements", []):
        tags = e.get("tags") or {}
        if e["type"] == "node":
            lat, lon = e.get("lat"), e.get("lon")
            if lat is None or not en_espana(lat, lon):
                continue
            tipo = (clasificar_osm(tags.get("enforcement"))
                    or clasificar_osm(tags.get("speed_camera") if tags.get("speed_camera") not in ("yes", None) else None)
                    or ("RADAR_FIJO" if tags.get("highway") == "speed_camera" or tags.get("speed_camera") == "yes" else None))
            if not tipo:
                continue
            id_ = f"osm:n{e['id']}"
            # nodo viejo y sin datos (ni límite ni sentido): si hay otro radar más fiable en la misma calle y
            # sentido muy cerca, seguramente es una cabina que ya no está o un duplicado (se mira en caminos.py)
            anno = str(e.get("timestamp") or "")[:4]
            sin_datos = not tags.get("maxspeed") and not direccion_osm(tags)
            viejo = (2 if anno.isdigit() and int(anno) <= 2015 else 1) if sin_datos else None
            por_id.setdefault(id_, punto(id_, tipo, "OSM", lat, lon, c=via_normalizada(tags.get("ref")) or None,
                                         v=limite(tags), n=nombre_camara_osm(tags), _viejo=viejo,
                                         **direccion_osm(tags)))
        elif e["type"] == "relation":
            tipo = clasificar_osm(tags.get("enforcement"))
            if not tipo:
                continue
            desde = hasta = None
            disp = []
            for m in e.get("members", []):
                if m.get("type") == "node" and m.get("lat") is not None:
                    c = (m["lat"], m["lon"])
                elif m.get("type") == "way" and m.get("geometry"):
                    c = (m["geometry"][0]["lat"], m["geometry"][0]["lon"])
                else:
                    continue
                if not en_espana(*c):
                    continue
                rol = m.get("role")
                if rol == "from":
                    desde = c
                elif rol == "to":
                    hasta = c
                elif rol == "device":
                    disp.append((f"osm:n{m.get('ref')}", c))
            lim, ref = limite(tags), via_normalizada(tags.get("ref")) or None
            if tipo == "RADAR_TRAMO" and desde and hasta:
                id_ = f"osm:r{e['id']}"
                por_id[id_] = punto(id_, "RADAR_TRAMO", "OSM", desde[0], desde[1], la2=round(hasta[0], 6),
                                    lo2=round(hasta[1], 6), c=ref, v=lim, n=tags.get("name"))
                for i, _ in disp:
                    por_id.pop(i, None)
            else:
                lista = disp or ([(f"osm:r{e['id']}", desde)] if desde else [])
                for i, c in lista:
                    prev = por_id.get(i, {})
                    # la relación dice de dónde viene el tráfico: rumbo desde "from" hasta el aparato
                    rb = round(rumbo_entre(desde[0], desde[1], c[0], c[1]), 1) if desde and distancia(*desde, *c) > 5 else None
                    por_id[i] = punto(i, "RADAR_FIJO" if tipo == "RADAR_TRAMO" else tipo, "OSM", c[0], c[1],
                                      c=ref or prev.get("c"), v=lim or prev.get("v"), n=prev.get("n"), rb=rb,
                                      **({k: prev[k] for k in ("_dir", "_dirg") if k in prev} if rb is None else {}))
    return list(por_id.values())


URL_ZBE_CKAN = "https://nap.dgt.es/api/3/action/package_show?id=zonas-de-bajas-emisiones"
URL_ZBE_DATASET = "https://nap.dgt.es/dataset/zonas-de-bajas-emisiones"


def urls_zbe() -> list[str]:
    urls = []
    try:
        d = http_json(URL_ZBE_CKAN, timeout=60)
        urls = [r["url"] for r in d["result"]["resources"] if str(r.get("url", "")).lower().endswith(".xml")]
    except Exception as e:  # noqa: BLE001
        log(f"  ZBE: API CKAN no disponible ({e}); leo la página")
    if not urls:
        html = http(URL_ZBE_DATASET, timeout=60).decode("utf-8", "replace")
        for rid in sorted(set(re.findall(r"/resource/([0-9a-f-]{36})", html))):
            try:
                h = http(f"{URL_ZBE_DATASET}/resource/{rid}", timeout=60, intentos=2).decode("utf-8", "replace")
                m = re.search(r'(https://nap\.dgt\.es/datex2/v3/dgt/zbe/[^"\'<>\s]+\.xml)', h)
                if m:
                    urls.append(m.group(1))
            except Exception:  # noqa: BLE001
                pass
    return sorted(set(urls))


def simplificar(anillo: list[tuple], tolerancia_m: float = 8.0) -> list[tuple]:
    """Quita puntos repetidos y casi alineados para que el fichero pese poco."""
    limpio = []
    for p in anillo:
        if not limpio or distancia(limpio[-1][0], limpio[-1][1], p[0], p[1]) > tolerancia_m:
            limpio.append(p)
    return limpio


def fuente_zbe() -> list[dict]:
    import xml.etree.ElementTree as ET

    def local(t):
        return t.rsplit("}", 1)[-1]

    urls = urls_zbe()
    log(f"  ZBE: {len(urls)} ficheros")
    zonas = []
    for url in urls:
        try:
            raiz = ET.fromstring(http(url, timeout=90, intentos=2))
        except Exception as e:  # noqa: BLE001
            log(f"  ZBE: {url.rsplit('/', 1)[-1]} falló ({e})")
            continue
        for z in raiz.iter():
            if local(z.tag) != "controlledZone":
                continue
            nombre = desc = web = estado = None
            anillos, etiquetas = [], set()
            for h in z.iter():
                n = local(h.tag)
                if n == "name" and nombre is None:
                    nombre = next((v.text for v in h.iter() if local(v.tag) == "value" and v.text), None)
                elif n == "controlledZoneDescription" and desc is None:
                    desc = next((v.text for v in h.iter() if local(v.tag) == "value" and v.text), None)
                elif n == "urlForFurtherInformation":
                    web = (h.text or "").strip() or None
                elif n == "status":
                    estado = (h.text or "").strip()
                elif n == "openlrPolygonCorners":
                    pts = []
                    for c in h:
                        if local(c.tag) != "openlrCoordinates":
                            continue
                        la = lo = None
                        for v in c:
                            if local(v.tag) == "latitude":
                                la = float(v.text)
                            elif local(v.tag) == "longitude":
                                lo = float(v.text)
                        if la is not None and lo is not None and en_espana(la, lo):
                            pts.append((la, lo))
                    pts = simplificar(pts)
                    if len(pts) >= 3:
                        anillos.append([round(x, 5) for p in pts for x in p])
                elif "emission" in n.lower() or "badge" in n.lower() or "label" in n.lower():
                    if h.text and h.text.strip():
                        etiquetas.add(h.text.strip())
            if not anillos or estado == "inactive":
                continue
            zonas.append({"id": z.attrib.get("id", nombre or url), "n": nombre, "d": desc, "u": web,
                          "e": sorted(etiquetas) or None, "p": anillos})
    return [{k: v for k, v in z.items() if v} for z in zonas]


# ------------------------------------------------------------------- más fuentes municipales
def csv_filas(b: bytes):
    try:
        t = b.decode("utf-8")
    except UnicodeDecodeError:
        t = b.decode("latin-1")
    t = t.lstrip("﻿")
    primera = t.splitlines()[0] if t else ""
    sep = ";" if primera.count(";") >= primera.count(",") else ","
    filas = list(csv.reader(io.StringIO(t), delimiter=sep))
    cab = [normalizar(c) for c in filas[0]] if filas else []
    return cab, filas[1:]


def num(v):
    try:
        return float(str(v).strip().replace(",", "."))
    except Exception:  # noqa: BLE001
        return None


def coordenadas_fila(cab, f, huso=30):
    def col(*pistas):
        for i, c in enumerate(cab):
            if any(c == p or c.startswith(p) for p in pistas):
                return i
        return -1
    la, lo = col("latitud", "lat"), col("longitud", "lon", "lng")
    x, y = col("utm_x", "gis_x", "x"), col("utm_y", "gis_y", "y")
    lat = num(f[la]) if 0 <= la < len(f) else None
    lon = num(f[lo]) if 0 <= lo < len(f) else None
    if lat is not None and lon is not None and en_espana(lat, lon):
        return lat, lon
    if 0 <= x < len(f) and 0 <= y < len(f) and num(f[x]) and num(f[y]):
        lat, lon = utm_a_latlon(num(f[x]), num(f[y]), huso)
        if en_espana(lat, lon):
            return lat, lon
    return None


URL_MADRID_FOTORROJO = ("https://datos.madrid.es/dataset/205193-0-semaforos-foto-rojo/resource/"
                        "205193-1-semaforos-foto-rojo-csv/download/205193-1-semaforos-foto-rojo-csv.csv")
URL_MADRID_ZBE_CAM = ("https://datos.madrid.es/dataset/300654-0-circulacion-camaras-trafico/resource/"
                      "300654-1-circulacion-camaras-trafico-csv/download/300654-1-circulacion-camaras-trafico-csv.csv")
URL_MADRID_ZBEDEP = ("https://datos.madrid.es/dataset/300229-0-trafico-madrid-central/resource/"
                     "300229-2-trafico-madrid-central-csv/download/300229-2-trafico-madrid-central-csv.csv")
URL_MALAGA_FOTORROJO = "https://datosabiertos.malaga.eu/recursos/transporte/trafico/da_transporteFotoRojo-4326.geojson"
URL_SALAMANCA_FIJOS = ("https://ide.aytosalamanca.es/geoserver/ide_salamanca_tic/ows?service=WFS&version=1.0.0&request=GetFeature"
                       "&typeName=ide_salamanca_tic%3ARadares_Fijos&outputFormat=application%2Fjson&srsName=EPSG%3A4326")
URL_SALAMANCA_TRAMO = ("https://ide.aytosalamanca.es/geoserver/ide_salamanca_movilidad/ows?service=WFS&version=1.0.0&request=GetFeature"
                       "&typeName=ide_salamanca_movilidad%3ARADAR_TRAMO&outputFormat=application%2Fjson&srsName=EPSG%3A4326")
URL_DONOSTIA = ("https://www.donostia.eus/geozerbitzuak/rest/services/ext/GARRAIOA/MapServer/41/query"
                "?where=1%3D1&outFields=*&outSR=4326&f=geojson")
URL_SANTACRUZ_FOTORROJO = ("https://www.santacruzdetenerife.es/opendata/dataset/3e0ec029-2efe-42e6-bbd2-5edc7fde283b/resource/"
                           "c72047bc-3e4b-409a-8997-d1f1a1f11772/download/foto_rojo.geojson")
URL_PAMPLONA_CINEMO = ("https://sig.pamplona.es/ogc/wfs?service=WFS&version=1.1.0&request=GetFeature&typeName=SEGU_Pto_Cinemometro"
                       "&outputFormat=application/json&srsName=EPSG:4326")
URL_SENTIDOS_DGT = "https://raw.githubusercontent.com/secretariacyas-crypto/radares-datos/main/radar_directions.json"
URL_FEED_COMUNITARIO = "https://geiserx.github.io/radares-anunciados-ha/feed.geojson"


def puntos_geojson(d, tipo, prefijo, nombre_fn=None, lim_fn=None, **extra):
    salida = []
    for i, f in enumerate(d.get("features", [])):
        g = f.get("geometry") or {}
        props = f.get("properties") or {}
        coords = g.get("coordinates")
        if g.get("type") == "MultiPoint" and coords:
            coords = coords[0]
        if g.get("type") not in ("Point", "MultiPoint") or not coords:
            continue
        lo, la = float(coords[0]), float(coords[1])
        if not en_espana(la, lo):
            continue
        lim = lim_fn(props) if lim_fn else None
        salida.append(punto(f"{prefijo}:{la:.5f},{lo:.5f}", tipo, "AYUNTAMIENTO", la, lo,
                            n=nombre_fn(props) if nombre_fn else None,
                            v=int(lim) if lim and 10 <= lim <= 150 else None, **extra))
    return salida


def fuente_madrid_extra() -> list[dict]:
    salida = []
    cab, filas = csv_filas(http(URL_MADRID_FOTORROJO, timeout=90))
    i_nom = cab.index("nombre") if "nombre" in cab else -1
    i_act = cab.index("activo") if "activo" in cab else -1
    for f in filas:
        if 0 <= i_act < len(f) and f[i_act].strip() == "0":
            continue
        c = coordenadas_fila(cab, f)
        if c:
            salida.append(punto(f"madfr:{c[0]:.5f},{c[1]:.5f}", "SEMAFORO", "AYUNTAMIENTO", c[0], c[1],
                                n=("Foto-rojo " + f[i_nom].strip().title()) if 0 <= i_nom < len(f) else "Foto-rojo",
                                mu="Madrid", pr="Madrid", ca="Comunidad de Madrid"))
    vistos = set()
    for url, etiqueta in ((URL_MADRID_ZBE_CAM, "Cámara de acceso a la ZBE (lee matrículas)"),
                          (URL_MADRID_ZBEDEP, "Cámara de acceso a la ZBE Distrito Centro (lee matrículas)")):
        try:
            cab, filas = csv_filas(http(url, timeout=90))
        except Exception as e:  # noqa: BLE001
            log(f"  Madrid ZBE: {e}")
            continue
        for f in filas:
            c = coordenadas_fila(cab, f)
            if not c:
                continue
            clave = f"{c[0]:.4f},{c[1]:.4f}"
            if clave in vistos:  # varias cámaras en el mismo poste
                continue
            vistos.add(clave)
            salida.append(punto(f"madzbe:{clave}", "OTRA_CAMARA", "AYUNTAMIENTO", c[0], c[1], n=etiqueta,
                                mu="Madrid", pr="Madrid", ca="Comunidad de Madrid"))
    return salida


def fuente_malaga() -> list[dict]:
    d = http_json(URL_MALAGA_FOTORROJO, timeout=90)
    return puntos_geojson(d, "SEMAFORO", "mlgfr",
                          nombre_fn=lambda p: p.get("NOMBRE") or "Foto-rojo",
                          mu="Málaga", pr="Málaga", ca="Andalucía")


def fuente_santacruz() -> list[dict]:
    d = http_json(URL_SANTACRUZ_FOTORROJO, timeout=45, intentos=1)  # casi nunca responde a GitHub: lo baja la app (fuentes_movil.json)
    return puntos_geojson(d, "SEMAFORO", "sctffr", nombre_fn=lambda p: "Foto-rojo " + str(
        p.get("nombre") or p.get("NOMBRE") or p.get("ubicacion") or "").strip(),
        mu="Santa Cruz de Tenerife", pr="Santa Cruz de Tenerife", ca="Canarias")


def fuente_pamplona() -> list[dict]:
    d = http_json(URL_PAMPLONA_CINEMO, timeout=45, intentos=1)  # ídem
    return puntos_geojson(d, "RADAR_FIJO", "pnacin", nombre_fn=lambda p: "Cinemómetro municipal",
                          mu="Pamplona", pr="Navarra", ca="Comunidad Foral de Navarra")


def fuente_salamanca() -> list[dict]:
    salida = puntos_geojson(http_json(URL_SALAMANCA_FIJOS, timeout=90), "RADAR_FIJO", "slm",
                            nombre_fn=lambda p: p.get("Ubicación") or p.get("Ubicacion"),
                            lim_fn=lambda p: num(p.get("vmax") or p.get("VMAX")),
                            mu="Salamanca", pr="Salamanca", ca="Castilla y León")
    for i, f in enumerate(http_json(URL_SALAMANCA_TRAMO, timeout=90).get("features", [])):
        g = f.get("geometry") or {}
        c = g.get("coordinates") or []
        if g.get("type") == "MultiLineString" and c:
            c = c[0]
        if g.get("type") not in ("LineString", "MultiLineString") or len(c) < 2:
            continue
        (lo1, la1), (lo2, la2) = c[0][:2], c[-1][:2]
        lim = num((f.get("properties") or {}).get("VMAX"))
        salida.append(punto(f"slmt:{i}", "RADAR_TRAMO", "AYUNTAMIENTO", la1, lo1, la2=round(la2, 6), lo2=round(lo2, 6),
                            v=int(lim) if lim else None, n="Radar de tramo municipal",
                            mu="Salamanca", pr="Salamanca", ca="Castilla y León"))
    return salida


def fuente_donostia() -> list[dict]:
    d = http_json(URL_DONOSTIA, timeout=90)
    return puntos_geojson(d, "RADAR_FIJO", "dss",
                          nombre_fn=lambda p: next((str(v) for k, v in p.items() if "kale" in k.lower() or "calle" in k.lower()
                                                    or "izena" in k.lower() or "nombre" in k.lower()), "Radar municipal"),
                          lim_fn=lambda p: next((num(v) for k, v in p.items() if "abiad" in k.lower() or "veloc" in k.lower()
                                                 or "vmax" in k.lower()), None),
                          mu="Donostia / San Sebastián", pr="Gipuzkoa", ca="País Vasco")


# --------------------------------------------------------- feed comunitario (radares-anunciados)
# Proyecto abierto que publica (ODbL) fuentes que solo responden desde IP española o que se leen de
# avisos de la Policía Local. Solo se toman las que no recogemos ya por nuestra cuenta.
FUENTES_FEED = {
    "euskadi": "AUTONOMICA", "navarra": "AUTONOMICA", "murcia": "POLICIA_LOCAL", "leon": "POLICIA_LOCAL",
    "madrid_multas": "MULTAS", "barcelona_multas": "MULTAS", "sct_remolc": "SCT", "dgt_invive": "DGT_TRAMOS_MOVIL",
    "donostia_movil": "POLICIA_LOCAL",
}


def fuente_feed_comunitario() -> list[dict]:
    d = http_json(URL_FEED_COMUNITARIO, timeout=180)
    salida = []
    for f in d.get("features", []):
        p = f.get("properties") or {}
        src = p.get("source")
        if src not in FUENTES_FEED:
            continue
        g = f.get("geometry") or {}
        kind = p.get("kind")
        fuente = FUENTES_FEED[src]
        prov = provincia_por_codigo(p.get("province"))
        base = dict(c=via_normalizada(p.get("road_ref") or p.get("road")) or None,
                    pk=p.get("km") if p.get("km") is not None else p.get("km_from"),
                    pk2=p.get("km_to"), v=p.get("maxspeed") if isinstance(p.get("maxspeed"), int) else None,
                    pr=prov, ca=PROVINCIAS[prov][1] if prov else None,
                    at=(((p.get("attribution") or "")[:240] + " · ") if p.get("attribution") else "") + "vía radares-anunciados (ODbL)",
                    vd=p.get("valid_from"), vh=p.get("valid_to"))
        dtxt = str(p.get("direction") or "").strip()
        if src == "euskadi" and dtxt and not dtxt.replace(".", "").isdigit() and dtxt.lower() not in ("both", "ambos"):
            base["_hacia_txt"] = dtxt
        kd = p.get("km_direction")
        if kd in ("positive", "negative") and base.get("c") and base.get("pk") is not None:
            base["s"] = "Creciente" if kd == "positive" else "Decreciente"
        if p.get("bearing") is not None and p.get("direction_semantics") == "travel" \
                and p.get("direction_confidence") not in ("low", None):
            base["rb"] = float(p["bearing"])
        id_ = f"com:{f.get('id')}"
        if g.get("type") == "LineString" and len(g.get("coordinates") or []) >= 2:
            c = g["coordinates"]
            if kind == "stretch":
                tr = [round(x, 5) for lo, la in (pt[:2] for pt in c) for x in (la, lo)]
                salida.append(punto(id_, "ZONA_MOVIL", fuente, c[0][1], c[0][0], tr=tr, n=p.get("name"), **base))
            else:
                salida.append(punto(id_, "RADAR_TRAMO", fuente, c[0][1], c[0][0], la2=round(c[-1][1], 6),
                                    lo2=round(c[-1][0], 6), n=p.get("name"), **base))
            continue
        if g.get("type") != "Point":
            continue
        lo, la = g["coordinates"][:2]
        if not en_espana(la, lo):
            continue
        if kind in ("fixed", "section_start"):
            tipo, nombre = "RADAR_FIJO", p.get("name")
        elif kind == "trailer":
            tipo, nombre = "ZONA_MOVIL", "Punto de radar en remolque (se mueve entre estos puntos)"
        elif kind == "mobile_announced":
            tipo, nombre = "ZONA_MOVIL", (p.get("name") or "Radar móvil anunciado").replace("Radar anunciado", "Radar móvil anunciado")
        elif kind == "mobile_recurring":
            tipo, nombre = "ZONA_MOVIL", (p.get("name") or "").replace("Radar móvil frecuente", "Punto habitual de radar móvil") or "Punto habitual de radar móvil"
        else:
            continue
        salida.append(punto(id_, tipo, fuente, la, lo, n=nombre, **base))
    return salida


def solo_tramos_nuevos(invive: list[dict], zonas: list[dict]) -> list[dict]:
    """De los tramos INVIVE (oficiales, en línea recta) solo los que radares-datos no ha podido situar."""
    por_via: dict[str, list] = {}
    for z in zonas:
        por_via.setdefault(via_normalizada(z.get("c")), []).append(z)
    salida = []
    for t in invive:
        if t["t"] != "ZONA_MOVIL" or "tr" not in t:
            salida.append(t)
            continue
        a, b = sorted([t.get("pk") or 0, t.get("pk2") or 0])
        solapa = any(max(a, min(z.get("pk") or 0, z.get("pk2") or 0)) <= min(b, max(z.get("pk") or 0, z.get("pk2") or 0)) + 0.5
                     for z in por_via.get(via_normalizada(t.get("c")), []))
        if not solapa:
            salida.append(t)
    return salida


def fuente_zonas() -> list[dict]:
    d = http_json(URL_ZONAS, timeout=180)
    salida = []
    for i, z in enumerate(d.get("zones", [])):
        path = z.get("path") or []
        if len(path) < 4:
            continue
        path = [round(float(x), 5) for x in path[: len(path) - len(path) % 2]]
        prov = provincia_canonica(z.get("province"))
        salida.append(punto(f"movil:{z.get('id', i)}:{i}", "ZONA_MOVIL", "DGT_TRAMOS_MOVIL", path[0], path[1],
                            tr=path, c=z.get("road"), pk=z.get("pkStart"), pk2=z.get("pkEnd"),
                            n="Trazado aproximado" if z.get("approx") else None,
                            pr=prov, ca=PROVINCIAS[prov][1] if prov else None))
    return salida


# ------------------------------------------------------------------------- límites de velocidad
def completar_limites(puntos: list[dict]) -> int:
    """Límite de la vía más cercana (OSM maxspeed) para radares y tramos que no lo traen. Con caché."""
    cache = cargar_json(CACHE_VEL, {})
    faltan = [p for p in puntos if p["t"] in ("RADAR_FIJO", "RADAR_TRAMO") and "v" not in p]
    pendientes = [p for p in faltan if f"{p['la']:.4f},{p['lo']:.4f}" not in cache]
    log(f"  límites: {len(faltan)} sin límite, {len(pendientes)} por consultar")
    for i in range(0, len(pendientes), 40):
        if not queda(PRESUPUESTO_TOTAL_S - 20 * 60):
            log("  límites: sin tiempo, se sigue en la próxima ejecución")
            break
        lote = pendientes[i:i + 40]
        partes = "".join(f'way(around:30,{p["la"]},{p["lo"]})["highway"]["maxspeed"];' for p in lote)
        try:
            d = overpass(f"[out:json][timeout:120];({partes});out tags geom;")
        except Exception as e:  # noqa: BLE001
            log(f"  límites: lote fallido ({e})")
            continue
        vias = [(limite(w.get("tags")), w.get("geometry") or []) for w in d.get("elements", []) if limite(w.get("tags"))]
        for p in lote:
            mejor, dmin = None, 40.0
            for lim, geom in vias:
                for g in geom:
                    dd = distancia(p["la"], p["lo"], g["lat"], g["lon"])
                    if dd < dmin:
                        mejor, dmin = lim, dd
            cache[f"{p['la']:.4f},{p['lo']:.4f}"] = mejor
        time.sleep(1.5)
    guardar_json(CACHE_VEL, cache)
    n = 0
    for p in faltan:
        lim = cache.get(f"{p['la']:.4f},{p['lo']:.4f}")
        if lim:
            p["v"] = lim
            p["vo"] = 1  # límite deducido de la vía, no del radar
            n += 1
    return n


# ------------------------------------------------------------------------- regiones (inverso)
def completar_regiones(puntos: list[dict]) -> None:
    cache = cargar_json(CACHE_REV, {})

    def clave(p):
        return f"{p['la']:.3f},{p['lo']:.3f}"

    pendientes = sorted({clave(p) for p in puntos if not (p.get("mu") and p.get("pr")) and clave(p) not in cache})
    log(f"  regiones: {len(pendientes)} celdas nuevas que consultar")

    def consulta(k):
        if not queda(PRESUPUESTO_TOTAL_S - 10 * 60):
            return k, "SIN_TIEMPO"
        la, lo = k.split(",")
        try:
            r = http_json(f"{CARTO_REV}?{urllib.parse.urlencode({'lon': lo, 'lat': la})}", timeout=30, intentos=2)
        except Exception:  # noqa: BLE001
            return k, None
        if not isinstance(r, dict):
            return k, None
        if not MUESTRA_REV:
            MUESTRA_REV.append(1)
            log(f"  regiones: ejemplo de respuesta {json.dumps(r, ensure_ascii=False)[:300]}")
        prov = provincia_canonica(r.get("province")) or provincia_por_codigo(r.get("provinceCode"))
        return k, {"mu": r.get("muni"), "pr": prov}

    with ThreadPoolExecutor(6) as ex:
        sin_tiempo = 0
        for k, v in ex.map(consulta, pendientes):
            if v == "SIN_TIEMPO":
                sin_tiempo += 1
                continue
            cache[k] = v
        if sin_tiempo:
            log(f"  regiones: {sin_tiempo} celdas quedan para la próxima ejecución")
    guardar_json(CACHE_REV, cache)

    for p in puntos:
        r = cache.get(clave(p)) or {}
        propia = provincia_canonica(p.get("pr"))
        # Puntos situados por PK: si caen en otra provincia, el hito de CartoCiudad era de otra vía homónima
        if propia and r.get("pr") and r["pr"] != propia and p.get("src", "").startswith("DGT PDF"):
            p["_dudoso"] = True
            continue
        if not p.get("mu") and r.get("mu"):
            p["mu"] = r["mu"]
        prov = propia or r.get("pr")
        if prov:
            p["pr"] = prov
            p["ca"] = PROVINCIAS[prov][1]

    # Lo que siga sin provincia (p. ej. en mitad de una autovía sin direcciones): la del vecino más cercano
    con = [p for p in puntos if p.get("pr")]
    rej = Rejilla(0.1)
    for p in con:
        rej.add(p)
    for p in puntos:
        if p.get("pr") or p.get("_dudoso"):
            continue
        v = rej.cerca(p["la"], p["lo"], 25000)
        if v is not None:
            p["pr"], p["ca"] = v["pr"], v.get("ca")


# --------------------------------------------------------------------------------- rumbos
def completar_rumbos(puntos: list[dict], geo: "Geocodificador") -> int:
    """Rumbo de circulación de cada punto con vía + PK + sentido: la app avisa solo en ese sentido."""
    candidatos = [p for p in puntos if p.get("c") and p.get("pk") is not None and p.get("s") in ("Creciente", "Decreciente")
                  and p["t"] != "ZONA_MOVIL" and "rb" not in p]
    pet = set()
    for p in candidatos:
        k = int(math.floor(p["pk"]))
        pet |= {(p["c"], k, p.get("pr")), (p["c"], k + 1, p.get("pr"))}
    geo.precargar(pet)
    n = 0
    for p in candidatos:
        rb = geo.rumbo(p["c"], p["pk"], p.get("pr"), p["s"])
        if rb is not None:
            # comprobación: el hito interpolado debe estar cerca del punto real (si no, PK/vía dudosos)
            c = geo.pk(p["c"], p["pk"], p.get("pr"))
            if c and distancia(c[0], c[1], p["la"], p["lo"]) < 1500:
                p["rb"] = rb
                n += 1
    geo.guardar()
    return n


# ------------------------------------------------------------------------------- deduplicado
class Rejilla:
    def __init__(self, celda=0.01):
        self.celda, self.d = celda, {}

    def _k(self, la, lo):
        return int(la // self.celda), int(lo // self.celda)

    def add(self, p):
        self.d.setdefault(self._k(p["la"], p["lo"]), []).append(p)

    def cerca(self, la, lo, radio, filtro=lambda p: True):
        kx, ky = self._k(la, lo)
        mejor, dmin = None, radio
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for p in self.d.get((kx + dx, ky + dy), []):
                    if not filtro(p):
                        continue
                    dd = distancia(la, lo, p["la"], p["lo"])
                    if dd < dmin:
                        mejor, dmin = p, dd
        return mejor


def fusionar(capas: list[list[dict]]) -> list[dict]:
    """Une capas por orden de prioridad: un punto de una capa posterior que coincide con uno anterior se descarta."""
    radios = {"RADAR_FIJO": 120, "RADAR_TRAMO": 300, "SEMAFORO": 60, "STOP_CEDA": 60, "OTRA_CAMARA": 80, "ZONA_MOVIL": 50}
    rej = Rejilla()
    salida = []
    for capa in capas:
        for p in capa:
            if p["t"] == "ZONA_MOVIL" and "tr" in p:
                salida.append(p)
                continue
            previo = rej.cerca(p["la"], p["lo"], radios.get(p["t"], 80), lambda q: q["t"] == p["t"])
            if previo is not None:
                for k in ("v", "c", "la2", "lo2"):
                    if k not in previo and k in p:
                        previo[k] = p[k]
                if "_dirg" in p:
                    previo.setdefault("_osm_dirg", p["_dirg"])
                # el mismo radar mapeado en OSM con su sentido (relación from → radar): se guarda como pista
                if p.get("f") == "OSM" and p.get("rb") is not None and \
                        distancia(p["la"], p["lo"], previo["la"], previo["lo"]) <= 60:
                    previo.setdefault("_rbs_osm", []).append(p["rb"])
                continue
            rej.add(p)
            salida.append(p)
    return salida


def segunda_opinion_sentidos(puntos: list[dict]) -> str:
    """
    radares-datos (ODbL) calcula por su cuenta el rumbo de cada radar de la DGT. Si nosotros no lo tenemos,
    se toma el suyo; si los dos no coinciden, se quita (mejor avisar en los dos sentidos que callar ante uno real).
    """
    d = http_json(URL_SENTIDOS_DGT, timeout=60)
    rad = d.get("radars") or {}
    puestos = coinciden = quitados = 0
    for p in puntos:
        if p.get("f") != "DGT" or not p["id"].startswith("dgt:GUID_"):
            continue
        suyo = rad.get(p["id"][len("dgt:GUID_"):])
        if not suyo or suyo[0] is None:
            continue
        rb = float(suyo[0])
        if p.get("rb") is None:
            p["rb"] = rb
            p.setdefault("at", "Sentido: radares-datos (ODbL)")
            puestos += 1
        elif abs((p["rb"] - rb + 180) % 360 - 180) <= 60:
            coinciden += 1
        else:
            p.pop("rb", None)
            quitados += 1
    return f"{puestos} sentidos nuevos, {coinciden} coinciden con los nuestros, {quitados} en desacuerdo (se avisa en los dos)"


def heredar_sentido_osm(puntos: list[dict]) -> str:
    """
    Si un radar oficial sin sentido tiene en OpenStreetMap su copia con sentido (a menos de 60 m), se usa el
    de OSM. Antes se comprueba con los oficiales que sí tienen sentido: solo si coinciden ≥ 90 % (y ≥ 15 casos).
    Si OSM da dos sentidos distintos para el mismo sitio (una cabina por sentido), no se decide.
    """
    def unico(rbs):
        if not rbs:
            return None
        if any(abs((r - rbs[0] + 180) % 360 - 180) > 45 for r in rbs):
            return None
        return rbs[0]
    ok = n = 0
    for p in puntos:
        r = unico(p.get("_rbs_osm") or [])
        if r is not None and p.get("rb") is not None:
            n += 1
            ok += abs((r - p["rb"] + 180) % 360 - 180) <= 60
    usar = n >= 15 and ok / n >= 0.9
    puestos = 0
    for p in puntos:
        r = unico(p.pop("_rbs_osm", None) or [])
        if usar and r is not None and p.get("rb") is None:
            p["rb"] = r
            puestos += 1
    return f"copias de OSM con sentido frente a oficiales: {ok}/{n} → " + (f"se usa en {puestos} puntos" if usar else "no se usa")


def calibrar_direcciones(puntos: list[dict]) -> str:
    """
    En OSM, direction=<grados> unas veces es hacia dónde va el tráfico vigilado y otras hacia dónde mira la
    cámara (al revés). Se mide contra los radares oficiales que tienen rumbo y también un duplicado de OSM,
    y solo se usa si la gran mayoría coincide (o la gran mayoría es justo al revés).
    """
    igual = contrario = 0
    for p in puntos:
        g = p.pop("_osm_dirg", None)
        if g is None or p.get("rb") is None:
            continue
        dd = abs((g - p["rb"] + 180) % 360 - 180)
        if dd <= 45:
            igual += 1
        elif dd >= 135:
            contrario += 1
    total = igual + contrario
    giro = None
    # pocos casos: se exige que coincidan todos (o casi)
    if total >= 4 and igual / total >= 0.9:
        giro = 0
    elif total >= 4 and contrario / total >= 0.9:
        giro = 180
    n = 0
    con_dir = sum(1 for p in puntos if "_dirg" in p)
    for p in puntos:
        g = p.pop("_dirg", None)
        if g is not None and giro is not None and p.get("rb") is None:
            p["rb"] = round((g + giro) % 360, 1)
            n += 1
    return (f"{con_dir} radares de OSM con direction; frente a los oficiales: {igual} igual, {contrario} al revés → "
            + ("no se usa" if giro is None else f"se usa{' girado 180°' if giro else ''} en {n} puntos"))


def reutilizar_caminos(puntos: list[dict], anterior: dict) -> int:
    """Sin red viaria, cada punto conserva su camino, recorrido y sentido de la vez anterior (si sigue igual)."""
    previos = {p["id"]: p for p in anterior.get("puntos", [])}
    n = 0
    for p in puntos:
        q = previos.get(p["id"])
        if not q or abs(q["la"] - p["la"]) > 1e-5 or abs(q["lo"] - p["lo"]) > 1e-5:
            continue
        for k in ("ap", "rt", "s2", "pl"):
            if k in q and k not in p:
                p[k] = q[k]
        if "rb" in q and "rb" not in p:
            p["rb"] = q["rb"]
        if "ap" in p:
            n += 1
    return n


def aplicar_correcciones(puntos: list[dict]) -> list[dict]:
    """correcciones.json: lo que se ha comprobado sobre el terreno (radares que no existen, sentidos)."""
    try:
        c = cargar_json("correcciones.json", {})
    except Exception:  # noqa: BLE001
        return puntos
    quitar = {q["id"] for q in c.get("quitar", [])}
    sentidos = c.get("sentido", {})
    for p in puntos:
        if p["id"] in sentidos:
            p["rb"] = float(sentidos[p["id"]]["rb"])
    n = len(puntos)
    puntos = [p for p in puntos if p["id"] not in quitar]
    log(f"correcciones: {n - len(puntos)} quitados, {sum(1 for p in puntos if p['id'] in sentidos)} sentidos fijados")
    return puntos


def unir_tramos(puntos: list[dict]) -> list[dict]:
    """
    Un mismo radar de tramo puede llegar por varias fuentes de forma distinta: OSM con entrada y salida,
    y la DGT con un solo punto (a veces la cámara de salida) o con su cámara de entrada como "radar fijo".
    Sin unirlos, la app avisaba de un "radar" en la entrada y otra vez del tramo al pasarlo.
    """
    tramos = [p for p in puntos if p["t"] == "RADAR_TRAMO" and "la2" in p]
    rej = Rejilla()
    for t in tramos:
        rej.add({"t": "_ext", "la": t["la"], "lo": t["lo"], "_t": t})
        rej.add({"t": "_ext", "la": t["la2"], "lo": t["lo2"], "_t": t})

    def sentido_ok(p, t):
        rb = p.get("rb")
        return rb is None or abs((rumbo_entre(t["la"], t["lo"], t["la2"], t["lo2"]) - rb + 180) % 360 - 180) <= 70

    fuera, sueltos, camaras = set(), 0, 0
    for p in puntos:
        if p["t"] == "RADAR_TRAMO" and "la2" not in p:
            e = rej.cerca(p["la"], p["lo"], 300, lambda q: sentido_ok(p, q["_t"]))
            if e is not None:
                t = e["_t"]
                for k in ("c", "v"):  # el PK y el sentido son los de su punto, no los de la entrada
                    if k in p and k not in t:
                        t[k] = p[k]
                fuera.add(p["id"]); sueltos += 1
        elif p["t"] == "RADAR_FIJO" and "v" not in p:
            # cámara de entrada o salida del tramo dada de alta como radar fijo (sin límite propio)
            e = rej.cerca(p["la"], p["lo"], 150, lambda q: sentido_ok(p, q["_t"]))
            if e is not None:
                fuera.add(p["id"]); camaras += 1
    log(f"tramos: {sueltos} puntos sueltos unidos a su tramo, {camaras} cámaras de entrada/salida absorbidas")
    return [p for p in puntos if p["id"] not in fuera]


# ------------------------------------------------------------------------------------- main
def ejecutar_zbe(anterior: dict, estado: dict) -> list:
    try:
        z = fuente_zbe()
        if not z:
            raise RuntimeError("sin zonas")
        estado["Zonas de bajas emisiones"] = f"✅ {len(z)}"
        log(f"ZBE: {len(z)} zonas")
        return z
    except Exception as e:  # noqa: BLE001
        prev = anterior.get("zbe", [])
        estado["Zonas de bajas emisiones"] = f"⚠️ falló ({e}); se mantienen {len(prev)}"
        log(f"ZBE: ERROR {e}")
        return prev


def main() -> int:
    try:
        os.remove("datos/REGISTRO.txt")
    except OSError:
        pass
    anterior = cargar_json(SALIDA, {"puntos": []})
    previos_por_fuente: dict[str, list] = {}
    for p in anterior.get("puntos", []):
        previos_por_fuente.setdefault(p.get("src", p["f"]), []).append(p)

    estado: dict[str, str] = {}
    geo = Geocodificador()

    def ejecutar(nombre, fn):
        t0 = time.time()
        try:
            r = fn()
            if not r:
                raise RuntimeError("sin datos")
            for p in r:
                p["src"] = nombre
            estado[nombre] = f"✅ {len(r)} ({time.time() - t0:.0f}s)"
            log(f"{nombre}: {len(r)} puntos")
            return r
        except Exception as e:  # noqa: BLE001
            prev = previos_por_fuente.get(nombre, [])
            estado[nombre] = f"⚠️ falló ({e}); se mantienen {len(prev)} de la vez anterior"
            log(f"{nombre}: ERROR {e}")
            return prev

    feed = ejecutar("DGT feed", fuente_dgt_feed)

    pdfs = {}
    try:
        pdfs = enlaces_pdf_dgt()
        log(f"PDFs DGT: {pdfs}")
    except Exception as e:  # noqa: BLE001
        log(f"PDFs DGT: no se pudo leer la página ({e})")

    # --- PDF de cinemómetros: fijos y tramos que no estén en el feed
    def de_cinemometros():
        filas = parsear_cinemometros(lineas_pdf(http(pdfs["cinemometros"], timeout=180)))
        log(f"  cinemómetros: {len(filas)} filas "
            f"({sum(f['tipo'] == 'Fijo' for f in filas)} fijos, {sum(f['tipo'] == 'Tramo' for f in filas)} tramos, "
            f"{sum(f['tipo'] == 'Movil' for f in filas)} móviles)")
        rej = Rejilla(0.05)
        indice: dict[str, list] = {}
        for p in feed:
            rej.add(p)
            indice.setdefault(via_normalizada(p.get("c")), []).append(p)

        def en_feed(via, pk):
            """El feed trae vía y PK: se casa por ahí, sin depender de geocodificar."""
            mejor, dmin = None, 0.35
            for q in indice.get(via, []):
                if q.get("pk") is None:
                    continue
                dd = abs(q["pk"] - pk)
                if dd < dmin:
                    mejor, dmin = q, dd
            return mejor

        pet = set()
        casados = 0
        for f in filas:
            if f["tipo"] == "Movil":
                continue
            prov, via = provincia_canonica(f["prov"]), via_normalizada(f["via"])
            q = en_feed(via, f["pk"])
            pks = [] if q is not None else [f["pk"]]
            if f.get("longitud") and (q is None or "la2" not in q):
                pks += [f["pk"] + f["longitud"] / 1000, f["pk"] - f["longitud"] / 1000]
            for pk in pks:
                if pk >= 0:
                    pet |= {(via, int(math.floor(pk)), prov), (via, int(math.floor(pk)) + 1, prov)}
        geo.precargar(pet)
        salida, sin_situar = [], 0
        for f in filas:
            if f["tipo"] == "Movil":
                continue
            prov = provincia_canonica(f["prov"])
            via = via_normalizada(f["via"])
            q = en_feed(via, f["pk"])
            c = None
            if q is None:
                c = geo.pk(via, f["pk"], prov)
                if not c:
                    sin_situar += 1
                    continue
                # respaldo espacial por si el feed escribe la vía de otra forma
                q = rej.cerca(c[0], c[1], 400, lambda q: via_normalizada(q.get("c")) == via)
            if q is not None:
                casados += 1
                if not q.get("s") or q.get("s") == "Ambos":
                    q["s"] = f["sentido"]
                q.setdefault("pr", prov)
                if f["tipo"] == "Tramo":
                    q["t"] = "RADAR_TRAMO"
                    if f.get("longitud"):
                        q.setdefault("lm", f["longitud"])
                        if "la2" not in q:
                            # el feed solo trae la cámara de entrada: calculamos el final por PK
                            largo = f["longitud"] / 1000
                            pk_fin = f["pk"] - largo if f["sentido"] == "Decreciente" else f["pk"] + largo
                            c2 = geo.pk(via, pk_fin, prov) if pk_fin >= 0 else None
                            if c2:
                                q["la2"], q["lo2"], q["pk2"] = round(c2[0], 6), round(c2[1], 6), round(pk_fin, 3)
                continue
            base = dict(c=via, pk=f["pk"], s=f["sentido"], pr=prov, ca=PROVINCIAS[prov][1] if prov else None)
            if f["tipo"] == "Tramo" and f.get("longitud"):
                largo = f["longitud"] / 1000
                sentidos = ["Creciente", "Decreciente"] if f["sentido"] == "Ambos" else [f["sentido"]]
                for s in sentidos:
                    pk_fin = f["pk"] + largo if s != "Decreciente" else f["pk"] - largo
                    c2 = geo.pk(via, pk_fin, prov) if pk_fin >= 0 else None
                    ini, fin = (c, c2)
                    if c2:
                        salida.append(punto(f"dgtpdf:T:{via}:{f['pk']}:{s[0]}", "RADAR_TRAMO", "DGT", ini[0], ini[1],
                                            la2=round(fin[0], 6), lo2=round(fin[1], 6), pk2=round(pk_fin, 3),
                                            lm=f["longitud"], **{**base, "s": s}))
            else:
                salida.append(punto(f"dgtpdf:F:{via}:{f['pk']}:{f['sentido'][0]}",
                                    "RADAR_TRAMO" if f["tipo"] == "Tramo" else "RADAR_FIJO", "DGT", c[0], c[1], **base))
        log(f"  cinemómetros: {casados} ya estaban en el feed, {len(salida)} añadidos, {sin_situar} sin poder situar")
        return salida

    pdf_radares = ejecutar("DGT PDF radares", de_cinemometros) if "cinemometros" in pdfs else previos_por_fuente.get("DGT PDF radares", [])

    def de_equipos():
        filas = parsear_equipos(lineas_pdf(http(pdfs["equipos"], timeout=180)))
        log(f"  equipos: {len(filas)} filas; tipos: {sorted({f['equipo'] for f in filas})}")
        pet = set()
        for f in filas:
            prov, via = provincia_canonica(f["prov"]), via_normalizada(f["via"])
            k = int(math.floor(f["pk"]))
            pet |= {(via, k, prov), (via, k + 1, prov)}
        geo.precargar(pet)
        salida, sin_situar = [], 0
        for f in filas:
            prov = provincia_canonica(f["prov"])
            via = via_normalizada(f["via"])
            c = geo.pk(via, f["pk"], prov)
            if not c:
                sin_situar += 1
                continue
            tipo, nombre = tipo_equipo(f["equipo"])
            salida.append(punto(f"dgteq:{via}:{f['pk']}:{f['sentido'][0]}:{normalizar(f['equipo'])[:6]}", tipo, "DGT",
                                c[0], c[1], c=via, pk=f["pk"], s=f["sentido"], n=nombre,
                                pr=prov, ca=PROVINCIAS[prov][1] if prov else None))
        log(f"  equipos: {len(salida)} situados, {sin_situar} sin poder situar")
        return salida

    camaras_dgt = ejecutar("DGT PDF cámaras", de_equipos) if "equipos" in pdfs else previos_por_fuente.get("DGT PDF cámaras", [])
    geo.guardar()

    sct = ejecutar("Cataluña (SCT)", fuente_sct)
    madrid = ejecutar("Ayto. Madrid", fuente_madrid)
    valencia = ejecutar("Ayto. València", lambda: fuente_valencia(geo))
    geo.guardar()
    osm = ejecutar("OpenStreetMap", fuente_osm)
    zonas = ejecutar("Tramos radar móvil", fuente_zonas)
    madrid2 = ejecutar("Ayto. Madrid foto-rojo y ZBE", fuente_madrid_extra)
    malaga = ejecutar("Ayto. Málaga foto-rojo", fuente_malaga)
    salamanca = ejecutar("Ayto. Salamanca", fuente_salamanca)
    donostia = ejecutar("Ayto. Donostia", fuente_donostia)
    santacruz = ejecutar("Ayto. Santa Cruz de Tenerife foto-rojo", fuente_santacruz)
    pamplona = ejecutar("Ayto. Pamplona cinemómetros", fuente_pamplona)
    comunitario = ejecutar("Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados)", fuente_feed_comunitario)
    comunitario = solo_tramos_nuevos(comunitario, zonas)
    log(f"feed comunitario tras quitar tramos ya situados: {len(comunitario)}")

    todos = fusionar([feed, pdf_radares, sct, madrid, madrid2, valencia, malaga, salamanca, donostia, santacruz, pamplona,
                      camaras_dgt, comunitario, osm, zonas])
    todos = unir_tramos(todos)
    todos = aplicar_correcciones(todos)
    # radares móviles anunciados ya caducados fuera
    hoy = datetime.now(timezone.utc).date().isoformat()
    todos = [p for p in todos if not p.get("vh") or p["vh"] >= hoy]

    try:
        n = completar_limites(todos)
        log(f"límites deducidos de OSM: {n}")
    except Exception as e:  # noqa: BLE001
        log(f"límites: ERROR {e}")
    try:
        completar_regiones(todos)
    except Exception as e:  # noqa: BLE001
        log(f"regiones: ERROR {e}")
    dudosos = [p for p in todos if p.pop("_dudoso", False)]
    if dudosos:
        log(f"descartados {len(dudosos)} puntos situados por PK en otra provincia: "
            + ", ".join(f"{p.get('c')} PK {p.get('pk')} ({p.get('pr')})" for p in dudosos[:15]))
        ids = {p["id"] for p in dudosos}
        todos = [p for p in todos if p["id"] not in ids]
    try:
        n = completar_rumbos(todos, geo)
        log(f"rumbos por sentido: {n}")
    except Exception as e:  # noqa: BLE001
        log(f"rumbos: ERROR {e}")
    # "hacia Vitoria", "hacia Logroño": la ciudad a la que va el tráfico que vigila el radar
    hacia = 0
    for p in todos:
        txt = p.pop("_hacia_txt", None)
        if txt and p.get("rb") is None:
            c = geo.direccion(txt.title() + ", España")
            if c and distancia(c[0], c[1], p["la"], p["lo"]) > 3000:
                p["_hacia"] = c
                hacia += 1
    geo.guardar()
    log(f"sentido hacia una ciudad: {hacia} puntos")
    try:
        r = segunda_opinion_sentidos(todos)
        estado["Sentido de los radares DGT (segunda opinión)"] = r
        log(r)
    except Exception as e:  # noqa: BLE001
        log(f"segunda opinión de sentidos: ERROR {e}")
    try:
        r = heredar_sentido_osm(todos)
        estado["Sentido heredado de OSM"] = r
        log(r)
    except Exception as e:  # noqa: BLE001
        log(f"sentido heredado de OSM: ERROR {e}")
    try:
        r = calibrar_direcciones(todos)
        estado["Sentido de los radares de OSM"] = r
        log(r)
    except Exception as e:  # noqa: BLE001
        log(f"direcciones OSM: ERROR {e}")

    zbe = ejecutar_zbe(anterior, estado)

    # Caminos de aproximación por la red viaria de OSM (la app solo avisa si vas por esa carretera)
    ruta_red = "red/vias.geojsonseq"
    if os.path.exists(ruta_red):
        try:
            import caminos
            st = caminos.anadir_caminos(todos, ruta_red, zbe, aviso=log)
            estado["Caminos de aproximación"] = (f"✅ {st['con_camino']} puntos con camino por su carretera, "
                                                 f"{st['tramos_con_recorrido']} de {st['tramos']} tramos con recorrido real "
                                                 f"({st['sin_via']} sin vía cercana; {st['segundos']}s)")
            estado["Sentido por el lado de la calle"] = (
                f"{st['dos_sentidos']} puntos de calles de doble sentido y {st['mediana_dos']} de medianas siguen en ambos sentidos. "
                f"Prueba de la regla (✓ = se usa): {st['lado']}. Pistas combinadas: {st['cruce']}")
            # copias de OSM de radares oficiales (misma calle y sentido, < 450 m): fuera la copia; si el
            # oficial no tiene sentido y la copia sí, se hereda (si la prueba con los que tienen ambos sale bien)
            pares = caminos.copias_osm(todos)
            ok = n = 0
            for o, f, m in pares:
                if o.get("rb") is not None and f.get("rb") is not None:
                    n += 1
                    ok += abs((o["rb"] - f["rb"] + 180) % 360 - 180) <= 60
            heredar = n >= 15 and ok / n >= 0.9
            reencajar = []
            for o, f, m in pares:
                if heredar and f.get("rb") is None and o.get("rb") is not None:
                    f["rb"] = o["rb"]
                    reencajar.append(f)
            # si los dos tienen sentido y no coincide, no son el mismo radar (uno por sentido en una carretera
            # de doble sentido): se quedan los dos
            fuera = {o["id"] for o, f, m in pares
                     if not (o.get("rb") is not None and f.get("rb") is not None
                             and abs((o["rb"] - f["rb"] + 180) % 360 - 180) > 60)}
            todos[:] = [p for p in todos if p["id"] not in fuera]
            if reencajar:
                caminos.anadir_caminos(reencajar, ruta_red, zbe, aviso=log)   # su camino, ya en un solo sentido
            estado["Copias de OSM de radares oficiales"] = (
                f"{len(fuera)} quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: "
                f"{ok}/{n} → " + (f"heredado en {len(reencajar)}" if heredar else "no se hereda"))
            log(estado["Copias de OSM de radares oficiales"])
            quitados = caminos.quitar_viejos_repetidos(todos)
            if quitados:
                ids = {p["id"] for p in quitados}
                todos[:] = [p for p in todos if p["id"] not in ids]
            estado["Radares viejos de OSM repetidos"] = (
                f"{len(quitados)} quitados (de OSM sin sentido, con otro radar más fiable en la misma calle y sentido a menos de 300 m; 450 m si no tiene datos; 600 m si además es de 2015 o antes)"
                + (": " + ", ".join(p["id"] for p in quitados[:15]) if quitados else ""))
            # dos radares de OSM sin sentido, en la misma calzada (de sentido único), mismo límite y a menos de
            # 200 m: el mismo radar mapeado dos veces. Se deja el primero (el aviso llega antes).
            dobles = {p["id"] for m, q, p in caminos.seguidos(todos, 200.0)
                      if q["f"] == p["f"] == "OSM" and q["t"] == p["t"] == "RADAR_FIJO"
                      and q.get("rb") is None and p.get("rb") is None and len(q["ap"]) == len(p["ap"]) == 1
                      and q.get("v") == p.get("v")}
            todos[:] = [p for p in todos if p["id"] not in dobles]
            log(f"radares de OSM mapeados dos veces: {len(dobles)} quitados {sorted(dobles)[:10]}")
            seg = caminos.seguidos(todos)
            estado["Radares seguidos (mismo sentido, < 300 m)"] = (
                f"{len(seg)} pares por revisar" + (": " + "; ".join(
                    f"{q['id']}→{p['id']} {m} m" for m, q, p in sorted(seg, key=lambda x: x[0])[:20]) if seg else ""))
            estado["Límites tomados de su vía"] = f"{st['limites_via']} puestos, {st['limites_quitados']} quitados por no ser de su vía"
            sos = st.get("sospechosos", [])
            estado["Revisar"] = (f"{len(sos)} radares de autovía con límite deducido < 60: " + "; ".join(sos[:12])) if sos else "nada sospechoso"
            log(f"caminos: {st}")
        except Exception as e:  # noqa: BLE001
            estado["Caminos de aproximación"] = f"⚠️ falló ({e}); se mantienen los de la vez anterior"
            log(f"caminos: ERROR {e}")
            n = reutilizar_caminos(todos, anterior)
            log(f"caminos: {n} puntos con los caminos de la vez anterior")
    else:
        n = reutilizar_caminos(todos, anterior)
        estado["Caminos de aproximación"] = f"⚠️ sin red viaria; {n} puntos con los caminos de la vez anterior"

    for p in todos:  # campos de trabajo que no van al fichero
        for k in ("_dir", "_dirg", "_osm_dirg", "_rbs_osm", "_viejo", "_hacia", "_hacia_txt"):
            p.pop(k, None)
    todos.sort(key=lambda p: (p["t"], p["id"]))
    ahora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    # Solo se reescribe si cambia el contenido (así el móvil no descarga si no hay novedades)
    huella = json.dumps(todos, ensure_ascii=False, sort_keys=True)
    huella += json.dumps(zbe, ensure_ascii=False, sort_keys=True)
    if huella == (json.dumps(anterior.get("puntos", []), ensure_ascii=False, sort_keys=True)
                  + json.dumps(anterior.get("zbe", []), ensure_ascii=False, sort_keys=True)):
        log("Sin cambios en los datos.")
        version = anterior.get("version", ahora)
    else:
        version = ahora
    guardar_json(SALIDA, {"version": version, "comprobado": ahora, "fuentes": estado, "puntos": todos, "zbe": zbe}, compacto=True)
    escribir_informe(todos, estado, version, zbe)
    return 0


def escribir_informe(puntos: list[dict], estado: dict, version: str, zbe: list | None = None) -> None:
    from collections import Counter
    tipos = ["RADAR_FIJO", "RADAR_TRAMO", "SEMAFORO", "STOP_CEDA", "OTRA_CAMARA", "ZONA_MOVIL"]
    nombres = {"RADAR_FIJO": "Fijos", "RADAR_TRAMO": "Tramo", "SEMAFORO": "Semáforo", "STOP_CEDA": "Stop/ceda",
               "OTRA_CAMARA": "Otras cám.", "ZONA_MOVIL": "Zonas móvil"}
    por_ccaa = Counter((p.get("ca") or "Sin asignar", p["t"]) for p in puntos)
    ccaas = sorted({p.get("ca") or "Sin asignar" for p in puntos}, key=lambda x: (x == "Sin asignar", normalizar(x)))
    l = [f"# Datos de Atalaya\n\nVersión: {version} · Total: **{len(puntos)}** puntos\n", "## Fuentes\n"]
    l += [f"- **{k}**: {v}" for k, v in estado.items()]
    l += ["\n## Por comunidad\n", "| Comunidad | " + " | ".join(nombres[t] for t in tipos) + " |",
          "|---|" + "---:|" * len(tipos)]
    for c in ccaas:
        l.append(f"| {c} | " + " | ".join(str(por_ccaa.get((c, t), 0)) for t in tipos) + " |")
    l += [f"\nCon sentido de circulación conocido (avisos solo en tu sentido): **{sum('rb' in p for p in puntos)}**",
          f"Zonas de bajas emisiones: **{len(zbe or [])}**"]
    por_fuente = Counter(p["f"] for p in puntos)
    l += ["\n## Por fuente\n"] + [f"- {k}: {v}" for k, v in por_fuente.most_common()]
    l += ["\n## Registro\n", "```", *LOG[-80:], "```"]
    os.makedirs(os.path.dirname(INFORME), exist_ok=True)
    with open(INFORME, "w", encoding="utf-8") as f:
        f.write("\n".join(l) + "\n")


if __name__ == "__main__":
    sys.exit(main())
