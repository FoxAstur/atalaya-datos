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

import bisect
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
from datetime import date as _fecha, datetime, timezone

UA = "AtalayaRecolector/1.0 (+https://github.com/FoxAstur/atalaya-datos)"
SALIDA = "datos/radares.json"
INFORME = "datos/INFORME.md"
CACHE_GEO = "cache/geocodificacion.json"
CACHE_REV = "cache/regiones.json"
CACHE_VEL = "cache/limites.json"
CACHE_ACC = "cache/accidentes.json"

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


# Portugal continental, contorno aproximado (frontera con España y costa): para marcar sus puntos como
# "Portugal" y no buscarles provincia española
PORTUGAL = [(41.87, -8.88), (42.15, -8.19), (41.84, -7.89), (41.95, -7.20), (41.98, -6.55), (41.68, -6.19),
            (41.03, -6.93), (40.33, -6.85), (39.66, -7.53), (39.05, -7.00), (38.75, -7.25), (38.20, -6.93),
            (37.98, -7.25), (37.53, -7.50), (37.17, -7.40), (36.95, -7.90), (36.95, -9.00), (38.70, -9.55),
            (39.70, -9.15), (41.00, -8.75), (41.87, -8.95)]


def en_portugal(lat, lon) -> bool:
    d = False
    n = len(PORTUGAL)
    for k in range(n):
        (y1, x1), (y2, x2) = PORTUGAL[k], PORTUGAL[(k + 1) % n]
        if (y1 > lat) != (y2 > lat) and lon < (x2 - x1) * (lat - y1) / (y2 - y1) + x1:
            d = not d
    return d


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
        if a or b:
            return a or b
        return self._pk_lejos(via, pk, provincia)

    def _pk_lejos(self, via: str, pk: float, provincia: str | None):
        """
        Sin hitos en ⌊pk⌋ ni ⌊pk⌋+1 (CartoCiudad no tiene todos: en la V-30 faltan del 0 al 3), con los dos más
        cercanos que haya de esa vía (hasta 4 km a cada lado): se interpola entre ellos o, si los dos quedan del
        mismo lado, se prolonga la recta. Es aproximado (se marca como posición aproximada); después se lleva
        sobre la carretera.
        """
        k = int(math.floor(pk))
        cerca = []
        for d in range(1, 5):
            for km in (k - d, k + 1 + d):
                if km >= 0:
                    h = self._hito(via, km, provincia)
                    if h:
                        cerca.append((abs(km - pk), km, h))
            if len(cerca) >= 2:
                break
        if len(cerca) < 2:
            return None
        cerca.sort()
        (_, k1, h1), (_, k2, h2) = cerca[:2]
        if k1 == k2 or not 200 < distancia(h1[0], h1[1], h2[0], h2[1]) < 6000 * abs(k2 - k1):
            return None
        f = (pk - k1) / (k2 - k1)
        if f < -1.5 or f > 2.5:
            return None
        return [h1[0] + (h2[0] - h1[0]) * f, h1[1] + (h2[1] - h1[1]) * f]

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

    def lugar(self, texto: str, cerca: tuple):
        """
        Un pueblo o ciudad ("hacia IRUN"), el más cercano a `cerca` de los que se llaman así. El buscador de
        direcciones daba cualquier calle con ese nombre (Irun en Álava, Donostia en La Rioja, San Sebastián en
        Madrid), y con eso el sentido salía al revés.
        """
        mejor = None
        partes = [texto] + [x.strip() for x in re.split(r"\s+-\s+|/", texto) if x.strip() and x.strip() != texto]
        for nombre in partes:
            clave = f"lugar2|{normalizar(nombre)}"
            if clave not in self.cache:
                cands = []
                try:
                    cands = http_json(f"{CARTO_CAND}?{urllib.parse.urlencode({'q': nombre, 'limit': 20})}",
                                      timeout=40, intentos=2) or []
                except Exception:  # noqa: BLE001
                    pass
                obj = normalizar(nombre)
                opciones = []
                for c in (cands if isinstance(cands, list) else [])[:8]:
                    tipo = normalizar(str(c.get("type") or ""))
                    if not (tipo in ("municipio", "poblacion") or normalizar(str(c.get("address") or "")) == obj):
                        continue
                    la, lo = c.get("lat") or 0, c.get("lng") or 0
                    if not la or not lo:
                        # los municipios y poblaciones vienen sin coordenadas: se piden por su id
                        try:
                            r = http_json(f"{CARTO_FIND}?{urllib.parse.urlencode({'id': c.get('id'), 'type': c.get('type')})}",
                                          timeout=40, intentos=2)
                            la, lo = (r or {}).get("lat") or 0, (r or {}).get("lng") or 0
                        except Exception:  # noqa: BLE001
                            la = lo = 0
                    if la and lo and en_espana(float(la), float(lo)):
                        opciones.append([float(la), float(lo)])
                self.cache[clave] = opciones
                self.nuevas += 1
            for c in self.cache[clave] or []:
                d = distancia(c[0], c[1], *cerca)
                if mejor is None or d < mejor[0]:
                    mejor = (d, c)
            if mejor:
                break
        return mejor[1] if mejor and mejor[0] < 120_000 else None

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


# Cabinas del Ayuntamiento de València (seis cinemómetros que rotan entre diez cabinas; prensa del 24-25/05/2026,
# más las cuatro de los túneles de acceso de 2019). Posición en su calzada y sentido que vigila, sacados de
# OpenStreetMap (relaciones enforcement) y de los cruces que da el Ayuntamiento. Antes se geocodificaban las
# direcciones y salían en el centro de la avenida (a 300-500 m) o en otra provincia ("Hermanos Machado" →
# Badajoz).
VALENCIA = [  # el orden fija el id (vlc:0, vlc:1…): lo nuevo, al final
    {"n": "Avinguda dels Germans Machado (a la altura de Vicent Canet), entrada a València", "la": 39.501666, "lo": -0.390636, "rb": 141},
    {"n": "Avinguda d'Antonio Ferrandis (Camí del Pou d'Aparisi)", "la": 39.451319, "lo": -0.356371, "rb": 61},
    {"n": "Camí Nou de Picanya, 49", "la": 39.454433, "lo": -0.406758, "rb": 46},
    {"n": "Avinguda de Fernando Abril Martorell (Carrera de Malilla)", "la": 39.445464, "lo": -0.379314, "rb": 277},
    {"n": "Avinguda dels Tarongers, 8", "la": 39.478368, "lo": -0.340918, "rb": 110},
    {"n": "Avinguda del Maestro Rodrigo, 84 (entrada a València)", "la": 39.489685, "lo": -0.406672, "rb": 151},
    {"n": "Avinguda dels Germans Machado (a la altura de Sant Josep Artesà), salida hacia Burjassot", "la": 39.501241, "lo": -0.389968, "rb": 321},
    {"n": "Túnel de Corts Valencianes – Pius XII (entrada a València)", "la": 39.485197, "lo": -0.395783, "rb": 151, "tu": 1},
    {"n": "Avinguda del Cid, a la salida del túnel (entrada a València)", "la": 39.469624, "lo": -0.404758, "rb": 99},
    {"n": "Túnel de l'autopista del Saler – López Piñero (entrada a València)", "la": 39.453089, "lo": -0.351631, "rb": 323, "v": 70, "tu": 1},
    {"n": "Paso inferior de la Ronda Nord – Germans Machado (hacia el mar)", "la": 39.497581, "lo": -0.368867, "rb": 112, "tu": 1},
]


def fuente_valencia(geo: Geocodificador | None = None) -> list[dict]:
    salida = []
    for i, d in enumerate(VALENCIA):
        salida.append(punto(f"vlc:{i}", "RADAR_FIJO", "AYUNTAMIENTO", d["la"], d["lo"], c=re.split(r" \(|,", d["n"])[0],
                            n="Cabina del Ayuntamiento · " + d["n"], v=d.get("v", 50), rb=float(d["rb"]),
                            tu=d.get("tu"), mu="València", pr="Valencia", ca="Comunitat Valenciana"))
    return salida


CAMARAS_OPL = "red/camaras.opl"   # cámaras de OSM sacadas del extracto semanal de Geofabrik (recolectar.yml)


def opl_a_overpass(ruta: str) -> dict:
    """
    Las cámaras del extracto de Geofabrik (formato OPL de osmium) con la forma de la respuesta de Overpass
    ("out meta" para nodos, "out geom" para relaciones). Así, si Overpass falla, OSM no se queda en lo de la
    última vez: se perdían el sentido heredado de OSM y salían 120 radares más "en los dos sentidos".
    """
    def tags(t):
        out = {}
        for kv in t.split(",") if t else []:
            if "=" in kv:
                k, v = kv.split("=", 1)
                out[desopl(k)] = desopl(v)
        return out
    nodos, vias, rels = {}, {}, []
    for linea in open(ruta, encoding="utf-8"):
        partes = linea.rstrip("\n").split(" ")
        if not partes or not partes[0]:
            continue
        tipo, oid = partes[0][0], int(partes[0][1:])
        campos = {x[0]: x[1:] for x in partes[1:] if x}
        if tipo == "n" and campos.get("x"):
            nodos[oid] = {"type": "node", "id": oid, "lat": float(campos["y"]), "lon": float(campos["x"]),
                          "timestamp": campos.get("t", ""), "tags": tags(campos.get("T", ""))}
        elif tipo == "w":
            vias[oid] = [int(r[1:]) for r in campos.get("N", "").split(",") if r]
        elif tipo == "r":
            rels.append((oid, tags(campos.get("T", "")), campos.get("M", "")))
    elementos = [n for n in nodos.values() if n["tags"]]
    for oid, t, m in rels:
        miembros = []
        for x in m.split(",") if m else []:
            ref, _, rol = x.partition("@")
            k, r = ref[0], int(ref[1:])
            if k == "n" and r in nodos:
                miembros.append({"type": "node", "ref": r, "role": rol, "lat": nodos[r]["lat"], "lon": nodos[r]["lon"]})
            elif k == "w" and r in vias:
                g = [{"lat": nodos[n]["lat"], "lon": nodos[n]["lon"]} for n in vias[r] if n in nodos]
                if g:
                    miembros.append({"type": "way", "ref": r, "role": rol, "geometry": g})
        elementos.append({"type": "relation", "id": oid, "tags": t, "members": miembros})
    return {"elements": elementos}


def desopl(s: str) -> str:
    """OPL escapa los caracteres especiales como %xxxx% (código Unicode en hexadecimal)."""
    return re.sub(r"%([0-9a-fA-F]+)%", lambda m: chr(int(m.group(1), 16)), s)


def overpass(consulta: str) -> dict:
    ultimo = None
    for s in OVERPASS:
        try:
            return json.loads(http(s, data=urllib.parse.urlencode({"data": consulta}).encode(), timeout=300, intentos=2))
        except Exception as e:  # noqa: BLE001
            ultimo = e
    if os.path.exists(CAMARAS_OPL) and "enforcement" in consulta:
        log(f"  Overpass no responde ({ultimo}); uso las cámaras del extracto de Geofabrik")
        return opl_a_overpass(CAMARAS_OPL)
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
area["ISO3166-1"~"^(ES|PT)$"]["admin_level"="2"]->.es;
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
            # cámaras de semáforo importadas como "speed_camera" con una nota tipo "SEM PUNT València ... CRUCE ..."
            # o "Radar Semáforo": son de semáforo, no de velocidad
            texto = normalizar(" ".join(str(tags.get(k) or "") for k in ("note", "description", "name")))
            if tipo == "RADAR_FIJO" and not tags.get("enforcement") and \
                    re.search(r"(^|\s)sem(\s|$)|semaforo|foto ?-?rojo|red ?light", texto):
                tipo = "SEMAFORO"
            # "Control de stop", "foto-stop": cámara de stop (la de la rotonda del IMED de Burjassot salía de semáforo)
            elif tipo in ("RADAR_FIJO", "SEMAFORO") and not tags.get("enforcement") and \
                    re.search(r"(^|[\s-])stop(\s|$)|ceda el paso", texto):
                tipo = "STOP_CEDA"
            id_ = f"osm:n{e['id']}"
            # nodo viejo y sin datos (ni límite ni sentido): si hay otro radar más fiable en la misma calle y
            # sentido muy cerca, seguramente es una cabina que ya no está o un duplicado (se mira en caminos.py)
            anno = str(e.get("timestamp") or "")[:4]
            sin_datos = not tags.get("maxspeed") and not direccion_osm(tags)
            viejo = (2 if anno.isdigit() and int(anno) <= 2015 else 1) if sin_datos else None
            # notas importadas de bases de radares: "... CV-35 Km 7.6 Valencia-Heron City DIR Ademuz CL",
            # "sentido Zaragoza": el pueblo al que va el tráfico que vigila (se sitúa luego, como en Euskadi)
            hacia_txt = None
            nota = " ".join(str(tags.get(k) or "") for k in ("note", "description", "name", "direction:name"))
            m = re.search(r"\b(?:DIR|dir\.|Dir\.|sentido|Sentido|SENTIDO|sentit|Sentit|SENTIT|hacia|HACIA)\s+"
                          r"([A-Za-zÀ-ÿ'·][A-Za-zÀ-ÿ'·\- ]{1,30}?)(?=\s+(?:CL|CD|TRIP|en|EN|km|Km|KM|PK)\b|[,.;()]|$)", nota)
            if m and not direccion_osm(tags):
                hacia_txt = m.group(1).strip()
            por_id.setdefault(id_, punto(id_, tipo, "OSM", lat, lon, c=via_normalizada(tags.get("ref")) or None,
                                         v=limite(tags), n=nombre_camara_osm(tags), _viejo=viejo, _hacia_txt=hacia_txt,
                                         **direccion_osm(tags)))
        elif e["type"] == "relation":
            tipo = clasificar_osm(tags.get("enforcement"))
            if not tipo:
                continue
            desde = hasta = via = None
            desde_via = hasta_via = None   # extremos de "from"/"to" cuando son vías (cruces de semáforo)
            disp = []
            for m in e.get("members", []):
                g = m.get("geometry") if m.get("type") == "way" else None
                if m.get("type") == "node" and m.get("lat") is not None:
                    c = (m["lat"], m["lon"])
                elif g:
                    c = (g[0]["lat"], g[0]["lon"])
                else:
                    continue
                if not en_espana(*c):
                    continue
                rol = m.get("role")
                if rol == "from":
                    desde = c
                    if g:
                        desde_via = (c, (g[-1]["lat"], g[-1]["lon"]))
                elif rol == "to":
                    hasta = c
                    if g:
                        hasta_via = (c, (g[-1]["lat"], g[-1]["lon"]))
                elif rol == "via" and not g:
                    via = c
                elif rol == "device":
                    disp.append((f"osm:n{m.get('ref')}", c))
            # Sin aparato, el sitio es el cruce ("via") o el extremo de la vía "from" que da a "to"; antes se
            # tomaba el primer nodo de "from", que puede estar a cientos de metros (salían semáforos fantasma)
            if desde_via and tipo != "RADAR_TRAMO":
                ref_pt = via or (min(hasta_via, key=lambda q: min(distancia(*q, *x) for x in desde_via)) if hasta_via else hasta)
                if ref_pt:
                    cerca_ = min(desde_via, key=lambda x: distancia(*x, *ref_pt))
                    lejos_ = desde_via[1] if cerca_ is desde_via[0] else desde_via[0]
                    desde = lejos_          # de dónde viene el tráfico (para el rumbo)
                    if not disp and tipo != "RADAR_TRAMO":
                        disp = [(f"osm:r{e['id']}", via or cerca_)]
            elif via and not disp and tipo != "RADAR_TRAMO":
                disp = [(f"osm:r{e['id']}", via)]
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
                    # (con "from" pegado al aparato, a 10 m, ese rumbo sale de lado: entonces aparato → "to", o from → to)
                    if desde and distancia(*desde, *c) >= 30:
                        rb = round(rumbo_entre(desde[0], desde[1], c[0], c[1]), 1)
                    elif hasta and distancia(*c, *hasta) >= 30:
                        rb = round(rumbo_entre(c[0], c[1], hasta[0], hasta[1]), 1)
                    elif desde and hasta and distancia(*desde, *hasta) >= 20:
                        rb = round(rumbo_entre(desde[0], desde[1], hasta[0], hasta[1]), 1)
                    else:
                        rb = round(rumbo_entre(desde[0], desde[1], c[0], c[1]), 1) if desde and distancia(*desde, *c) > 5 else None
                    # el mismo aparato en otra relación con el sentido contrario: vigila los dos sentidos.
                    # Antes la segunda relación pisaba a la primera y se perdía un sentido (Germans Machado).
                    if prev.get("_rel") and prev.get("rb") is not None and rb is not None and \
                            abs((prev["rb"] - rb + 180) % 360 - 180) > 90:
                        i = i + "b"
                        prev = {k: v for k, v in prev.items() if k in ("c", "v", "n")}
                    por_id[i] = punto(i, "RADAR_FIJO" if tipo == "RADAR_TRAMO" else tipo, "OSM", c[0], c[1], _rel=1,
                                      c=ref or prev.get("c"), v=lim or prev.get("v"), n=prev.get("n") or nombre_camara_osm(tags), rb=rb,
                                      **({k: prev[k] for k in ("_dir", "_dirg") if k in prev} if rb is None else {}))
    for p in por_id.values():
        if en_portugal(p["la"], p["lo"]):
            p["pr"] = p["ca"] = "Portugal"
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
    d = http_json(URL_SANTACRUZ_FOTORROJO, timeout=15, intentos=1)  # casi nunca responde a GitHub: lo baja la app (fuentes_movil.json)
    return puntos_geojson(d, "SEMAFORO", "sctffr", nombre_fn=lambda p: "Foto-rojo " + str(
        p.get("nombre") or p.get("NOMBRE") or p.get("ubicacion") or "").strip(),
        mu="Santa Cruz de Tenerife", pr="Santa Cruz de Tenerife", ca="Canarias")


def fuente_pamplona() -> list[dict]:
    d = http_json(URL_PAMPLONA_CINEMO, timeout=15, intentos=1)  # ídem
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


URL_LISBOA = ("https://services.arcgis.com/1dSrzEWVQn5kHHyK/arcgis/rest/services/MOB_RadaresPaineis/FeatureServer/0/query"
              "?outFields=*&where=1%3D1&outSR=4326&f=geojson")


def fuente_lisboa() -> list[dict]:
    """Radares de la Câmara Municipal de Lisboa (dados.gov.pt, «Localização de radares»)."""
    salida = []
    for f in http_json(URL_LISBOA, timeout=90).get("features", []):
        g = f.get("geometry") or {}
        c = g.get("coordinates") or []
        pr = f.get("properties") or {}
        if g.get("type") != "Point" or len(c) < 2:
            continue
        if "radar" not in str(pr.get("REFNAME") or "radar").lower():
            continue
        lo, la = float(c[0]), float(c[1])
        salida.append(punto(f"lis:{la:.5f},{lo:.5f}", "RADAR_FIJO", "AYUNTAMIENTO", la, lo,
                            n="Radar da Câmara Municipal de Lisboa", mu="Lisboa", pr="Portugal", ca="Portugal",
                            at="Câmara Municipal de Lisboa (dados.gov.pt)"))
    return salida


URL_VILADECANS = ("https://geoportal.viladecans.cat/server/rest/services/EP520_Radars_PT/FeatureServer/0/query"
                  "?where=1%3D1&outFields=id,ubicacio,equip,estat&outSR=4326&f=geojson")


URL_ANSR = "https://radaresavista.pt/wp-content/themes/ansr-radares/dataTest.json"
# Sentido de la ANSR → rumbo aproximado del tráfico vigilado (caminos.py lo ajusta a la carretera)
CARDINAL_ANSR = {"norte-sul": 180.0, "sul-norte": 0.0, "este-oeste": 270.0, "oeste-este": 90.0}


def fuente_ansr() -> list[dict]:
    """
    Red SINCRO de Portugal: los radares oficiales de la ANSR (portal «Radares à vista»), con coordenadas,
    carretera, PK, límite y sentido (Norte-Sul, Este-Oeste… o Ambos).
    """
    datos = json.loads(http(URL_ANSR, timeout=90).decode("utf-8-sig", "replace"))
    salida = []
    for d in datos:
        nums = re.findall(r"-?\d+(?:\.\d+)?", str(d.get("Coordenada") or "").replace(",", " , "))
        if len(nums) < 2:
            continue
        la, lo = float(nums[0]), -abs(float(nums[1]))   # todo Portugal está al oeste de Greenwich
        if not (36.5 < la < 42.3 and -31.5 < lo < -6.0):
            continue
        tipo = "RADAR_TRAMO" if str(d.get("Tipo") or "").strip().upper() == "VM" else "RADAR_FIJO"
        via = str(d.get("Estrada") or "").strip()
        km = str(d.get("Km Inicial") or "").strip()
        sentido = str(d.get("Sentido") or "").strip()
        card = CARDINAL_ANSR.get(sentido.lower())
        vel = num(d.get("Velocidade"))
        salida.append(punto(f"ansr:{via}:{km}:{sentido[:1] or 'x'}", tipo, "AUTONOMICA", la, lo,
                            c=via or None, pk=num(km), v=int(vel) if vel else None,
                            s="Ambos" if sentido.lower() in ("ambos", "dois sentidos") else sentido or None,
                            n=("Radar de velocidad media" if tipo == "RADAR_TRAMO" else "Radar") + " SINCRO (ANSR)"
                              + (f" · {via} km {km.replace('.', ',')}" if via and km else ""),
                            _card=card, mu=str(d.get("Freguesia") or "").strip() or None, pr="Portugal", ca="Portugal",
                            at="ANSR — Radares à vista (radaresavista.pt)"))
    return salida


def fuente_viladecans() -> list[dict]:
    """Cabinas de radar y fotorrojos del Ajuntament de Viladecans (geoportal municipal, «Radars»)."""
    salida = []
    for f in http_json(URL_VILADECANS, timeout=90).get("features", []):
        g = f.get("geometry") or {}
        c = g.get("coordinates") or []
        pr = f.get("properties") or {}
        if g.get("type") != "Point" or len(c) < 2 or "producci" not in str(pr.get("estat") or "").lower():
            continue
        lo, la = float(c[0]), float(c[1])
        equip = str(pr.get("equip") or "").lower()
        rojo = "vermell" in equip or "roig" in equip
        donde = str(pr.get("ubicacio") or "").strip()
        salida.append(punto(f"vdc:{pr.get('id')}", "SEMAFORO" if rojo else "RADAR_FIJO", "AYUNTAMIENTO", la, lo,
                            c=re.split(r",| /", donde)[0] or None,
                            n=("Fotorrojo" if rojo else "Cabina de radar") + " del Ajuntament · " + donde,
                            mu="Viladecans", pr="Barcelona", ca="Cataluña",
                            at="Ajuntament de Viladecans (geoportal)"))
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
    # notas abiertas de OpenStreetMap en las que alguien avisa de un radar que aún no está en el mapa
    "osm_notes": "OSM",
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
        elif kind == "reported":
            tipo, nombre = "ZONA_MOVIL", "Posible radar: aviso de un usuario en OpenStreetMap, sin confirmar"
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


# --------------------------------------------------------- tramos de concentración de accidentes
URL_SEG_VIAL = "https://www.transportes.gob.es/carreteras/nuestra-red/seguridad-vial"
URLS_TCA = {  # por si la página cambia: los últimos publicados (2024)
    "TCA": "https://cdn.transportes.gob.es/portal-web-transportes/carreteras/nuestrared/Seguridad_vial/NOTA-TCA-2024-Para-Publicar-en-WEB%20%28105%29-Def.pdf",
    "TCAM": "https://cdn.transportes.gob.es/portal-web-transportes/carreteras/nuestrared/Seguridad_vial/tca-con-implicacion-de-motoristas.pdf",
}
RE_TCA = re.compile(r"\b((?:A|AP|N|AC|AG|AL|AS|AV|CA|CL|CM|CV|EX|GC|LO|MA|ML|MU|SE|TF|V|Z|B|M|C|H|GR|SA|TO|PA|LE|BU|SG|VA|ZA|SO|GU|CU|TE|HU|LR|NA|BI|GI|SS|PO|OU|LU|CO|JA|J|AB|CC|BA|IB|PM|E)-\d{1,4}[A-Z]?)\s+(\d{1,4}[.,]\d{1,3})\s+(\d{1,4}[.,]\d{1,3})")


def trazar_por_pk(geo: "Geocodificador", tramos: list[tuple]) -> dict:
    """(vía, PK inicial, PK final, provincia) → [(lat, lon), …] por los hitos de CartoCiudad (luego se lleva a la
    carretera con trazar_zonas). Solo si la longitud cuadra con la de los PK."""
    pet = set()
    for via, pki, pkf, prov in tramos:
        for k in range(int(math.floor(pki)), int(math.floor(pkf)) + 2):
            pet.add((via, k, prov))
    geo.precargar(pet)
    salida = {}
    for via, pki, pkf, prov in tramos:
        pts = []
        for pk in [pki] + [float(k) for k in range(int(math.floor(pki)) + 1, int(math.ceil(pkf)))] + [pkf]:
            c = geo.pk(via, pk, prov)
            if c and (not pts or distancia(pts[-1][0], pts[-1][1], c[0], c[1]) > 30):
                pts.append((round(c[0], 5), round(c[1], 5)))
        largo = sum(distancia(*pts[i], *pts[i + 1]) for i in range(len(pts) - 1)) if len(pts) >= 2 else 0
        if len(pts) >= 2 and 0.4 * (pkf - pki) * 1000 < largo < 2.5 * (pkf - pki) * 1000 + 300:
            salida[(via, pki, pkf, prov)] = pts
    return salida


# Accidentes con víctimas de la DGT (microdatos): vía + km de cada accidente. Los cinco últimos años.
URLS_ACCIDENTES = [
    "https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/24h/TABLA_ACCIDENTES_21.xlsx",
    "https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/24h/TABLA_ACCIDENTES_22.xlsx",
    "https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/24h/TABLA_ACCIDENTES_23.XLSX",
    "https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/publicaciones/Ficheros_microdatos_de_accidentalidad_con_victimas/TABLA_ACCIDENTES_24.XLSX",
    "https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/publicaciones/Ficheros_microdatos_de_accidentalidad_con_victimas/TABLA_ACCIDENTES_2025.XLSX",
]
UMBRAL_ACC_KM = 12   # accidentes con víctimas en 1 km en cinco años (≈ uno cada cinco meses)
COD_PROV = {v[0]: k for k, v in PROVINCIAS.items()}


def fuente_accidentes_dgt(geo: "Geocodificador") -> list[dict]:
    """
    Tramos con muchos accidentes en las carreteras autonómicas y de diputación, cuyas listas de TCA no son
    públicas (la Generalitat Valenciana solo publica cuántos hay). Con los microdatos de la DGT: todo kilómetro
    (ventana de 1 km que se desliza cada 100 m) con al menos UMBRAL_ACC_KM accidentes con víctimas en cinco años;
    los que se solapan se unen. No es la lista oficial (que pondera por el tráfico): en la red del Estado, con los
    mismos datos, este criterio cubre 103 de los 109 TCA oficiales, pero marca más tramos (vías con mucho tráfico).
    Por eso solo se usa donde no hay lista oficial. El cálculo se guarda y se repite cada 30 días.
    """
    import openpyxl
    cache = cargar_json(CACHE_ACC, {})
    hoy = _fecha.today()
    if cache.get("urls") != URLS_ACCIDENTES or not cache.get("fecha") or \
            (hoy - _fecha.fromisoformat(cache["fecha"])).days > 30:
        kms: dict = {}
        anyos = set()
        for url in URLS_ACCIDENTES:
            wb = openpyxl.load_workbook(io.BytesIO(http(url, timeout=300)), read_only=True)
            it = wb.worksheets[0].iter_rows(values_only=True)
            h = list(next(it))
            ix = {k: h.index(k) for k in ("ANYO", "COD_PROVINCIA", "CARRETERA", "KM", "TITULARIDAD_VIA")}
            for r in it:
                car, km, tit = r[ix["CARRETERA"]], r[ix["KM"]], r[ix["TITULARIDAD_VIA"]]
                if not car or km is None or str(tit) not in ("2", "3"):   # 2 autonómica, 3 diputación/cabildo
                    continue
                try:
                    km = float(km)
                except (TypeError, ValueError):
                    continue
                prov = COD_PROV.get(f"{int(r[ix['COD_PROVINCIA']]):02d}") if r[ix["COD_PROVINCIA"]] else None
                kms.setdefault(f"{via_normalizada(str(car))}|{prov or ''}", []).append(km)
                anyos.add(r[ix["ANYO"]])
            log(f"  accidentes: {url.rsplit('/', 1)[-1]} leído")
        tramos = []
        for clave, lista in kms.items():
            if len(lista) < UMBRAL_ACC_KM:
                continue
            lista.sort()
            cur = None
            a = math.floor(lista[0] * 10) / 10 - 1
            while a <= lista[-1]:
                n = bisect.bisect_left(lista, a + 1.0) - bisect.bisect_left(lista, a)
                if n >= UMBRAL_ACC_KM:
                    if cur and a <= cur[1]:
                        cur[1], cur[2] = round(a + 1.0, 1), max(cur[2], n)
                    else:
                        if cur:
                            tramos.append([clave] + cur)
                        cur = [round(max(a, 0), 1), round(a + 1.0, 1), n]
                a = round(a + 0.1, 1)
            if cur:
                tramos.append([clave] + cur)
        # accidentes de cada tramo (no el máximo de la ventana)
        for t in tramos:
            lista = kms[t[0]]
            t.append(bisect.bisect_left(lista, t[2]) - bisect.bisect_left(lista, t[1]))
        cache = {"urls": URLS_ACCIDENTES, "fecha": hoy.isoformat(), "anyos": sorted(anyos), "tramos": tramos}
        guardar_json(CACHE_ACC, cache)
    anyos = cache.get("anyos") or []
    periodo = f"{anyos[0]}-{anyos[-1]}" if anyos else "últimos cinco años"
    lista = [(t[0].split("|")[0], t[1], t[2], t[0].split("|")[1] or None, t[4]) for t in cache["tramos"]]
    trazados = trazar_por_pk(geo, [(v, a, b, pr) for v, a, b, pr, _ in lista])
    salida, sin = [], 0
    for via, a, b, prov, n in lista:
        pts = trazados.get((via, a, b, prov))
        if not pts:
            sin += 1
            continue
        salida.append(punto(
            f"acc:{via}:{a}-{b}", "TCA", "ACCIDENTES_DGT", pts[0][0], pts[0][1],
            tr=[x for q in pts for x in q], c=via, pk=a, pk2=b, s="Ambos", lm=round((b - a) * 1000), pr=prov,
            ca=PROVINCIAS[prov][1] if prov else None,
            n=f"Tramo con muchos accidentes: {n} con víctimas en {periodo} (microdatos DGT)",
            at="Calculado con los microdatos de accidentes con víctimas de la DGT"))
    log(f"  accidentes: {len(lista)} tramos, {len(salida)} situados, {sin} sin poder situar")
    return salida


def fuente_tca(geo: "Geocodificador") -> list[dict]:
    """
    Tramos de concentración de accidentes (TCA) del Ministerio de Transportes en la Red de Carreteras del
    Estado, y los de accidentes con motoristas (TCAM). Vienen como vía + PK inicial y final, sin sentido (se
    avisa en los dos). Se trazan con los hitos de CartoCiudad y después por la carretera (trazar_zonas).
    """
    urls = dict(URLS_TCA)
    try:
        html = http(URL_SEG_VIAL, timeout=60).decode("utf-8", "replace")
        for href in re.findall(r'href="([^"]+\.pdf)"', html, re.I):
            u = urllib.parse.urljoin(URL_SEG_VIAL, href)
            nombre = urllib.parse.unquote(href).lower()
            if "motorist" in nombre or "motocic" in nombre:
                urls["TCAM"] = u
            elif "tca" in nombre:
                urls["TCA"] = u
    except Exception as e:  # noqa: BLE001
        log(f"  TCA: página del Ministerio no disponible ({e}); se usan los PDF conocidos")
    filas = {}
    for clase, url in urls.items():
        try:
            lineas = lineas_pdf(http(url, timeout=120))
        except Exception as e:  # noqa: BLE001
            log(f"  TCA: {clase} no se pudo leer ({e})")
            continue
        n = 0
        for l in lineas:
            for via, a, b in RE_TCA.findall(l):
                pki, pkf = sorted((num_km(a), num_km(b)))
                if not 0 < pkf - pki <= 15:
                    continue
                clave = (via_normalizada(via), round(pki, 1), round(pkf, 1))
                filas.setdefault(clave, set()).add(clase)
                n += 1
        log(f"  TCA: {clase} {n} filas ({url.rsplit('/', 1)[-1]})")
    trazados = trazar_por_pk(geo, [(via, pki, pkf, None) for via, pki, pkf in filas])
    salida, sin = [], []
    for (via, pki, pkf), clases in sorted(filas.items()):
        pts = trazados.get((via, pki, pkf, None))
        if not pts:
            sin.append(f"{via} {pki}-{pkf}")
            continue
        motos = "TCAM" in clases
        salida.append(punto(
            f"tca:{via}:{pki}-{pkf}", "TCA", "MINISTERIO", pts[0][0], pts[0][1],
            tr=[x for q in pts for x in q], c=via, pk=pki, pk2=pkf, s="Ambos", lm=round((pkf - pki) * 1000),
            n=("Tramo de concentración de accidentes" + (" (también con motoristas)" if "TCA" in clases and motos
               else "") if "TCA" in clases else "Tramo de concentración de accidentes con motoristas"),
            at="Ministerio de Transportes y Movilidad Sostenible"))
    if sin:
        log(f"  TCA: {len(sin)} sin poder situar: {sin[:20]}")
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

    pendientes = sorted({clave(p) for p in puntos if not (p.get("mu") and p.get("pr")) and p.get("ca") != "Portugal"
                         and clave(p) not in cache})
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
        if p.get("ca") == "Portugal":
            continue
        r = cache.get(clave(p)) or {}
        propia = provincia_canonica(p.get("pr"))
        # Puntos situados por PK: si caen en otra provincia, el hito de CartoCiudad era de otra vía homónima
        if propia and r.get("pr") and r["pr"] != propia and p.get("src", "").startswith("DGT PDF"):
            p["_dudoso"] = True
            continue
        if not p.get("mu") and r.get("mu"):
            # CartoCiudad devuelve los apóstrofos como comillas dobles (L"Hospitalet, Sant Joan d"Alacant)
            p["mu"] = r["mu"].replace('"', "'")
        prov = propia or r.get("pr")
        if prov:
            p["pr"] = prov
            p["ca"] = PROVINCIAS[prov][1]

    # Lo que siga sin provincia (p. ej. en mitad de una autovía sin direcciones): la del vecino más cercano
    con = [p for p in puntos if p.get("pr") and p.get("ca") != "Portugal"]
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


def sentidos_opuestos(a: dict, b: dict) -> bool:
    """
    ¿Vigilan sentidos contrarios? Entonces son dos radares (uno por calzada, a la misma altura) y no se
    pueden juntar en uno: antes se juntaba todo lo que estaba a menos de 120 m y en autovías se perdía
    el radar de uno de los dos sentidos.
    """
    ra = a["rb"] if a.get("rb") is not None else a.get("_card")
    rb_ = b["rb"] if b.get("rb") is not None else b.get("_card")
    if ra is not None and rb_ is not None:   # rumbo o, si no hay, el "Norte-Sul" de la ANSR
        return abs((ra - rb_ + 180) % 360 - 180) > 90
    sa, sb = a.get("s"), b.get("s")
    if sa in ("Creciente", "Decreciente") and sb in ("Creciente", "Decreciente") and sa != sb:
        ca, cb = via_normalizada(a.get("c")), via_normalizada(b.get("c"))
        return not ca or not cb or ca == cb
    return False


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
            previo = rej.cerca(p["la"], p["lo"], radios.get(p["t"], 80),
                               lambda q: q["t"] == p["t"] and not sentidos_opuestos(p, q))
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
            if rej.cerca(p["la"], p["lo"], radios.get(p["t"], 80), lambda q: q["t"] == p["t"]) is not None:
                FUSION["opuestos"] += 1
            rej.add(p)
            salida.append(p)
    return salida


FUSION = {"opuestos": 0}


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
    puestos = ambos = 0
    for p in puntos:
        rbs = p.pop("_rbs_osm", None) or []
        r = unico(rbs)
        if usar and r is not None and p.get("rb") is None:
            p["rb"] = r
            puestos += 1
        elif usar and r is None and p.get("rb") is None and not p.get("s") and len(rbs) >= 2 and \
                any(abs((a - b + 180) % 360 - 180) >= 135 for a in rbs for b in rbs):
            # OSM tiene la cabina vigilando los dos sentidos (una relación por sentido): se avisa en los
            # dos sin decir "puede ser del otro sentido"
            p["s"] = "Ambos"
            ambos += 1
    return f"copias de OSM con sentido frente a oficiales: {ok}/{n} → " + \
        (f"se usa en {puestos} puntos y en {ambos} vigila los dos sentidos" if usar else "no se usa")


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
        # zonas de radar móvil: su trazado por carretera de la vez anterior (si empieza y acaba donde el de hoy)
        if q and p["t"] == "ZONA_MOVIL" and p.get("tr") and q.get("tr") and len(q["tr"]) > len(p["tr"]):
            a_, b_ = p["tr"], q["tr"]
            if max(abs(a_[0] - b_[0]), abs(a_[1] - b_[1]), abs(a_[-2] - b_[-2]), abs(a_[-1] - b_[-1])) < 1e-4:
                p["tr"] = b_
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


SENALES_OPL = "red/camaras.opl"   # los stops y semáforos van con las cámaras (misma pasada de osmium, recolectar.yml)


_SENALES: dict = {}


def cargar_senales(ruta: str = SENALES_OPL) -> tuple[dict, int]:
    """Stops y semáforos de OSM en una rejilla de ~100 m: {(cy, cx): [(la, lo, clase)]}. Se lee una vez."""
    if ruta in _SENALES:
        return _SENALES[ruta]
    rej: dict = {}
    n_sen = 0
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as f:
            for linea in f:
                if not linea.startswith("n"):
                    continue
                campos = linea.split()
                tags = next((c[1:] for c in campos if c.startswith("T")), "")
                x = next((c[1:] for c in campos if c.startswith("x")), "")
                y = next((c[1:] for c in campos if c.startswith("y")), "")
                if not x or not y:
                    continue
                clase = "stop" if "highway=stop" in tags else "semaforo" if "highway=traffic_signals" in tags else None
                if not clase:
                    continue
                la, lo = float(y), float(x)
                rej.setdefault((int(la // 0.001), int(lo // 0.001)), []).append((la, lo, clase))
                n_sen += 1
    _SENALES[ruta] = (rej, n_sen)
    return rej, n_sen


def semaforos_por_su_cruce(puntos: list[dict], ruta_red: str, zbe, ruta: str = SENALES_OPL) -> str:
    """
    Cámaras de semáforo, ya con sus caminos de aproximación. Una cámara de foto-rojo está unos metros ANTES de
    su semáforo, en el carril que vigila: si por uno de sus caminos el semáforo queda delante (a menos de 50 m)
    y por el contrario no hay ninguno cerca, ese es su sentido. Así se resuelven las de sentido dudoso de las
    calles de doble sentido (antes se avisaba en los dos) y se llevan a su línea de detención. Las que no tienen
    ningún semáforo delante por ninguno de sus caminos se cuentan aparte: su posición es sospechosa.
    """
    import caminos
    rej, _ = cargar_senales(ruta)
    if not rej:
        return "sin fichero de stops y semáforos"

    def delante(la, lo, rumbo_ap, maximo):
        mejor = None
        cy, cx = int(la // 0.001), int(lo // 0.001)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for sla, slo, clase in rej.get((cy + dy, cx + dx), ()):
                    if clase != "semaforo":
                        continue
                    d = distancia(la, lo, sla, slo)
                    if d > maximo:
                        continue
                    if d > 6 and abs((rumbo_entre(la, lo, sla, slo) - rumbo_ap + 180) % 360 - 180) > 35:
                        continue
                    if mejor is None or d < mejor[0]:
                        mejor = (d, sla, slo)
        return mejor

    # Comprobación con las de sentido conocido (de su fuente): ¿su semáforo queda delante (cámara antes de la
    # línea) o detrás (cámara pasado el cruce, mirando hacia atrás)? Si no es casi siempre delante, el método
    # no vale y no se deduce ningún sentido.
    a_favor = en_contra = 0
    for p in puntos:
        if p["t"] == "SEMAFORO" and p.get("rb") is not None:
            la0, lo0 = p.get("_la0", p["la"]), p.get("_lo0", p["lo"])
            dl, dt = delante(la0, lo0, p["rb"], 50), delante(la0, lo0, (p["rb"] + 180) % 360, 50)
            if dl and not dt:
                a_favor += 1
            elif dt and not dl:
                en_contra += 1
    fiable = a_favor >= 20 and a_favor / max(1, a_favor + en_contra) >= 0.85
    log(f"semáforos: con sentido conocido, su semáforo delante {a_favor}, detrás {en_contra} → "
        + ("se deducen sentidos" if fiable else "no se deducen sentidos"))

    resueltos, a_la_linea, sin_semaforo, rehacer, pasado_el_cruce = 0, 0, [], [], 0
    for p in puntos:
        if p["t"] != "SEMAFORO" or not p.get("ap"):
            continue
        la0, lo0 = p.get("_la0", p["la"]), p.get("_lo0", p["lo"])
        por_sentido = []   # (rumbo de llegada, semáforo delante o None, caminos de ese sentido)
        for ap in p["ap"]:
            h = caminos.llegada(ap)
            grupo = next((g for g in por_sentido if abs((g[0] - h + 180) % 360 - 180) <= 60), None)
            if grupo is None:
                por_sentido.append([h, delante(la0, lo0, h, 50), [ap]])
            else:
                grupo[2].append(ap)
        con = [g for g in por_sentido if g[1] is not None]
        if not con:
            # ¿cámara pasado el cruce, mirando atrás? (en las de sentido conocido pasa en 1 de cada 12): su
            # semáforo queda detrás, a pocos metros, por uno solo de sus sentidos
            detras = []
            for g in por_sentido:
                if p.get("rb") is not None and abs((g[0] - p["rb"] + 180) % 360 - 180) > 60:
                    continue
                sem = delante(la0, lo0, (g[0] + 180) % 360, 40)
                if sem is not None:
                    detras.append((g, sem))
            if len(detras) == 1:
                g, sem = detras[0]
                if p.get("rb") is None and fiable:
                    p["rb"] = round(g[0], 1)
                    p.pop("s2", None)
                    resueltos += 1
                if p.get("rb") is not None:
                    p["la"], p["lo"] = round(sem[1], 6), round(sem[2], 6)
                    p.pop("ap", None)
                    rehacer.append(p)
                    a_la_linea += 1
                    pasado_el_cruce += 1
                    continue
            sin_semaforo.append(p["id"])
            continue
        if fiable and p.get("rb") is None and len(con) == 1 and len(por_sentido) >= 2:
            h, sem, aps = con[0]
            # el contrario no puede tener un semáforo delante ni a 80 m: si no, es un cruce de dos semáforos seguidos
            otros = [g for g in por_sentido if g is not con[0]]
            if all(delante(la0, lo0, g[0], 80) is None for g in otros):
                p["rb"] = round(h, 1)
                p.pop("s2", None)
                resueltos += 1
        if p.get("rb") is not None:
            g = next((g for g in con if abs((g[0] - p["rb"] + 180) % 360 - 180) <= 60), None)
            if g is not None and g[1][0] >= 3 and (p["la"], p["lo"]) != (round(g[1][1], 6), round(g[1][2], 6)):
                p["la"], p["lo"] = round(g[1][1], 6), round(g[1][2], 6)
                p.pop("ap", None)
                rehacer.append(p)
                a_la_linea += 1
    if rehacer:
        caminos.anadir_caminos(rehacer, ruta_red, zbe, aviso=log)
    msg = (f"comprobación con las de sentido conocido: semáforo delante en {a_favor}, detrás en {en_contra}; "
           f"{resueltos} cámaras de semáforo con su sentido deducido por el semáforo que tienen delante; "
           f"{a_la_linea} llevadas a su línea ({pasado_el_cruce} estaban pasado el cruce); "
           f"{len(sin_semaforo)} sin ningún semáforo de OSM a 50 m (posición por revisar)")
    log(msg + (": " + ", ".join(sin_semaforo[:120]) if sin_semaforo else ""))
    return msg


def a_la_linea_de_detencion(puntos: list[dict], ruta: str = SENALES_OPL) -> str:
    """
    Una cámara de stop o de semáforo está en un poste unos metros antes (o al lado) de la línea donde hay que
    parar, y lo que importa al conducir es esa línea: con el punto en el poste, el aviso de llegada salía
    antes de tiempo (el foto-stop del IMED, 25 m antes del stop). Se lleva cada cámara al stop o al
    semáforo de OSM que tiene delante (en su sentido, a menos de 45 m); sin sentido conocido, al más
    cercano a menos de 25 m.
    """
    rej, n_sen = cargar_senales(ruta)
    if not rej:
        return "sin fichero de stops y semáforos"
    movidos = 0
    for p in puntos:
        if p["t"] not in ("SEMAFORO", "STOP_CEDA"):
            continue
        p["_la0"], p["_lo0"] = p["la"], p["lo"]   # dónde estaba (para deducir su sentido por su semáforo)
        if p.get("rb") is None and p["t"] == "SEMAFORO":
            # sin sentido, en un cruce el semáforo más cercano puede ser el de la otra calle: se decide después,
            # con los caminos de aproximación (semaforos_por_su_cruce)
            continue
        quiero = "stop" if p["t"] == "STOP_CEDA" else "semaforo"
        cy, cx = int(p["la"] // 0.001), int(p["lo"] // 0.001)
        rb = p.get("rb")
        mejor = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for la, lo, clase in rej.get((cy + dy, cx + dx), ()):
                    if clase != quiero:
                        continue
                    d = distancia(p["la"], p["lo"], la, lo)
                    if d < 3:
                        mejor = (0.0, la, lo)   # ya está en la línea
                        break
                    if rb is not None:
                        if d > 45 or abs((rumbo_entre(p["la"], p["lo"], la, lo) - rb + 180) % 360 - 180) > 50:
                            continue
                    elif d > 25:
                        continue
                    if mejor is None or d < mejor[0]:
                        mejor = (d, la, lo)
        if mejor and mejor[0] >= 3:
            p["la"], p["lo"] = round(mejor[1], 6), round(mejor[2], 6)
            movidos += 1
    return f"{movidos} cámaras de stop o semáforo llevadas a su línea de detención ({n_sen} stops y semáforos de OSM)"


def aplicar_verificados(puntos: list[dict], cambiados: list | None = None) -> str:
    """
    verificados.json: puntos comprobados sobre el terreno, que ninguna actualización puede perder ni estropear.
    Se buscan por su id y, si ese id ya no está o ahora es otro punto (algunas fuentes cambian los ids), por tipo
    y cercanía. Si falta, se repone; si se ha movido o ha cambiado de sentido, de tipo o de límite, se deja como
    está comprobado. Se marcan con "_verif" para comprobar después que tienen caminos de aproximación.
    """
    try:
        lista = cargar_json("verificados.json", {}).get("puntos", [])
    except Exception as e:  # noqa: BLE001
        return f"⚠️ verificados.json ilegible: {e}"
    por_id = {p["id"]: p for p in puntos}
    arreglos = []
    for r in lista:
        la, lo, t = float(r["la"]), float(r["lo"]), r["t"]
        p = por_id.get(r["id"])
        # "radio": hasta dónde puede estar el punto de la fuente (los situados por PK pueden estar a cientos de m)
        if p is not None and (p["t"] != t or distancia(p["la"], p["lo"], la, lo) > float(r.get("radio", 150))):
            p = None   # ese id ahora es otra cosa
        if p is None:
            cerca = [(distancia(q["la"], q["lo"], la, lo), q) for q in puntos if q["t"] == t]
            cerca = [x for x in cerca if x[0] < 80]
            p = min(cerca, key=lambda x: x[0])[1] if cerca else None
        if p is None:
            extra = {k: r[k] for k in ("c", "v", "n", "rb", "mu", "pr", "ca", "tu", "s", "la2", "lo2") if k in r}
            p = punto(r["id"], t, r.get("f", "AYUNTAMIENTO"), la, lo, src="Comprobado sobre el terreno", **extra)
            puntos.append(p)
            arreglos.append(f"{r['id']} repuesto")
            p["_verif"] = r["id"]
            continue
        cambios = []
        if distancia(p["la"], p["lo"], la, lo) > float(r.get("tol", 25)):
            p["la"], p["lo"] = la, lo
            # los situados a ojo sobre una fuente que solo da el PK se recolocan siempre: no es una avería
            if "radio" not in r:
                cambios.append("posición")
            elif cambiados is not None:
                cambiados.append(p)
        if r.get("s") == "Ambos":
            if p.get("s") != "Ambos" or "rb" in p:
                p["s"] = "Ambos"
                p.pop("rb", None)
                cambios.append("los dos sentidos")
        elif "rb" in r:
            if p.get("rb") is None:
                p["rb"] = float(r["rb"])   # la fuente no lo daba todavía: no es un arreglo
            elif abs((float(p["rb"]) - float(r["rb"]) + 180) % 360 - 180) > 20:
                p["rb"] = float(r["rb"])
                cambios.append("sentido")
        for k in ("v", "n", "la2", "lo2", "tu"):
            if k in r and p.get(k) != r[k]:
                p[k] = r[k]
                if not ("radio" in r and k in ("la2", "lo2")):
                    cambios.append(k)
                elif cambiados is not None and p not in cambiados:
                    cambiados.append(p)
        if cambios:
            arreglos.append(f"{r['id']} ({', '.join(cambios)})")
            if cambiados is not None:
                cambiados.append(p)
        p["_verif"] = r["id"]
        if r.get("px"):
            p["_verif_px"] = 1   # comprobado solo en parte (p. ej. un extremo de un tramo): sigue siendo aproximado
    msg = f"{len(lista)} comprobados sobre el terreno" + (f"; arreglados: {'; '.join(arreglos)}" if arreglos else ", todos en su sitio")
    log(f"verificados: {msg}")
    return msg if not arreglos else "⚠️ " + msg


def aplicar_correcciones(puntos: list[dict]) -> list[dict]:
    """correcciones.json: lo que se ha comprobado sobre el terreno (radares que no existen, sentidos)."""
    try:
        c = cargar_json("correcciones.json", {})
    except Exception:  # noqa: BLE001
        return puntos
    # Con posición (la/lo), se quita lo que haya de ese tipo a menos de 25 m, venga con el id que venga: los ids
    # de algunas fuentes cambian (vlc:0 fue una vez un radar de Badajoz) y por el id solo se podría quitar otro
    quitar = {q["id"] for q in c.get("quitar", []) if "la" not in q}
    quitar_pos = [(float(q["la"]), float(q["lo"]), q.get("t")) for q in c.get("quitar", []) if "la" in q and "lo" in q]
    sentidos = c.get("sentido", {})
    tipos = c.get("tipo", {})
    # cámaras que solo salen en la prensa o en avisos del ayuntamiento (foto-stop de un pueblo, etc.):
    # se añaden si no hay ya una del mismo tipo a menos de 60 m
    anadidos = 0
    for a in c.get("anadir", []):
        if any(q["t"] == a["t"] and distancia(q["la"], q["lo"], a["la"], a["lo"]) < 60 for q in puntos):
            continue
        puntos.append(punto(a["id"], a["t"], a.get("f", "AYUNTAMIENTO"), float(a["la"]), float(a["lo"]),
                            src=a.get("src", "Ayuntamiento / prensa (situada a mano)"),
                            **{k: v for k, v in a.items() if k in ("c", "v", "n", "rb", "mu", "pr", "ca", "tu", "at")}))
        anadidos += 1
    for p in puntos:
        if p["id"] in tipos:   # el tipo bien puesto (un foto-stop que OSM tiene como cámara de semáforo)
            p["t"] = tipos[p["id"]]["t"]
            if tipos[p["id"]].get("n"):
                p["n"] = tipos[p["id"]]["n"]
        if p["id"] in sentidos:
            c_ = sentidos[p["id"]]
            if c_.get("s") == "Ambos":   # vigila los dos sentidos: se avisa en ambos sin «puede ser del otro»
                p["s"] = "Ambos"
                p.pop("rb", None)
            else:
                p["rb"] = float(c_["rb"])
            if "la" in c_ and "lo" in c_:   # posición real, en su calzada
                p["la"], p["lo"] = float(c_["la"]), float(c_["lo"])
            if c_.get("n"):
                p["n"] = c_["n"]
    n = len(puntos)

    def sobra(p: dict) -> bool:
        if p["id"] in quitar:
            return True
        return p["t"] != "ZONA_MOVIL" and any((t is None or t == p["t"]) and distancia(p["la"], p["lo"], la, lo) < 25
                                              for la, lo, t in quitar_pos)
    puntos = [p for p in puntos if not sobra(p)]
    log(f"correcciones: {n - len(puntos)} quitados, {sum(1 for p in puntos if p['id'] in sentidos)} sentidos fijados, "
        f"{anadidos} añadidos, {sum(1 for p in puntos if p['id'] in tipos)} con el tipo corregido")
    return puntos


def _sobre_la_via(red, via: str, pk: float, prov: str | None, geo) -> tuple | None:
    """
    (lat, lon) del PK medido POR LA CARRETERA entre los hitos km⌊pk⌋ y km⌊pk⌋+1, o None. La recta entre dos
    hitos se separa de la vía en las curvas (y la distancia por la vía no es la de la recta): era el error de
    ~100 m de todo lo que se sitúa por PK.
    """
    import caminos
    k = int(math.floor(pk))
    a, b = geo._hito(via, k, prov), geo._hito(via, k + 1, prov)
    if not a or not b or not (300 < distancia(a[0], a[1], b[0], b[1]) < 2500):
        return None
    # hasta pasar pegado al hito b (con 200 m, el de las zonas, la ruta acababa antes de llegar a él)
    ruta = None
    for radio in (35.0, 70.0):
        ruta = caminos._ruta_entre(red, (a[0], a[1]), (b[0], b[1]), caminos.norm_ref(via), radio_objetivo=radio)
        if ruta:
            break
    if not ruta or len(ruta) < 2:
        return None
    # recorrido hasta donde más se acerca al hito b
    acum, mejor = 0.0, None
    for i in range(len(ruta) - 1):
        d, t = caminos.proyectar((b[0], b[1]), ruta[i], ruta[i + 1])
        seg = caminos.dist(ruta[i], ruta[i + 1])
        if mejor is None or d < mejor[0]:
            mejor = (d, acum + seg * t)
        acum += seg
    if mejor is None or mejor[0] > 80:
        return None
    total = mejor[1]
    # los hitos se sitúan a un lado de la vía: el inicio de la ruta es su proyección; el recorrido entre
    # hitos tiene que parecerse a 1 km (si no, la ruta no es la de esa carretera)
    if not 700 < total < 1500:
        return None
    objetivo = (pk - k) * total
    acum = 0.0
    for i in range(len(ruta) - 1):
        seg = caminos.dist(ruta[i], ruta[i + 1])
        if acum + seg >= objetivo:
            q = caminos.interpolar(ruta[i], ruta[i + 1], (objetivo - acum) / seg if seg else 0)
            return q[0], q[1]
        acum += seg
    return None


def pk_por_la_carretera(puntos: list[dict], ruta_red: str, geo) -> str:
    """
    Recoloca lo situado por PK (PDF de radares y de cámaras de la DGT) midiendo por la carretera. Antes, se
    comprueba el método con los radares del feed de la DGT, que traen PK y coordenadas exactas: se mide el
    error de la recta entre hitos y el de ir por la carretera, y solo se aplica si mejora.
    """
    import caminos
    import statistics
    por_pk = [p for p in puntos if (p["id"].startswith(("dgtpdf:", "dgteq:")) or p.get("_orient_pdf"))
              and p.get("c") and p.get("pk") is not None
              and not p.get("_pos_osm") and not p.get("_verif")]   # lo comprobado a ojo no se toca
    prueba = [p for p in puntos if p["id"].startswith("dgt:") and p["t"] == "RADAR_FIJO" and p.get("c")
              and p.get("pk") is not None and p.get("pr")][:400]
    semillas = por_pk + prueba
    if not semillas:
        return "nada que situar por PK"
    geo.precargar({(via_normalizada(p["c"]), int(math.floor(k)) + d, provincia_canonica(p.get("pr")))
                   for p in prueba for k in [float(p["pk"])] for d in (0, 1)})
    red = caminos.cargar_red(ruta_red, semillas)
    # 1) comprobación con el feed
    recta, carretera = [], []
    for p in prueba:
        via, prov, pk = via_normalizada(p["c"]), provincia_canonica(p.get("pr")), float(p["pk"])
        c1 = geo.pk(via, pk, prov)
        c2 = _sobre_la_via(red, via, pk, prov, geo)
        if c1 and c2:
            recta.append(distancia(p["la"], p["lo"], c1[0], c1[1]))
            carretera.append(distancia(p["la"], p["lo"], c2[0], c2[1]))
    if len(recta) < 30:
        return f"⚠️ sin bastantes radares del feed para comprobar ({len(recta)}): no se recoloca nada"

    def resumen(v):
        v = sorted(v)
        return f"mediana {statistics.median(v):.0f} m, p75 {v[int(len(v) * .75)]:.0f} m, p90 {v[int(len(v) * .9)]:.0f} m"
    mejora = statistics.median(carretera) < statistics.median(recta) and \
        sorted(carretera)[int(len(carretera) * .9)] <= sorted(recta)[int(len(recta) * .9)]
    texto = (f"comprobado con {len(recta)} radares del feed (PK y coordenadas): en recta {resumen(recta)}; "
             f"por la carretera {resumen(carretera)}")
    log(f"PK por la carretera: {texto}")
    if not mejora:
        return f"⚠️ {texto} → no mejora, no se recoloca"
    # 2) recolocar lo situado por PK
    movidos = 0
    for p in por_pk:
        via, prov = via_normalizada(p["c"]), provincia_canonica(p.get("pr"))
        c = _sobre_la_via(red, via, float(p["pk"]), prov, geo)
        if c and distancia(p["la"], p["lo"], c[0], c[1]) < 400:
            p["la"], p["lo"] = round(c[0], 6), round(c[1], 6)
            movidos += 1
        if p.get("_orient_pdf") and p.get("la2") is not None:
            # ¿Entrada o salida? La cámara del feed (la2) es real y está sobre su calzada: si allí se circula hacia el
            # otro extremo, la cámara es la ENTRADA y el tramo va al revés de lo supuesto. En la V-30 el PDF dice
            # creciente, pero la cámara del PK 8,77 está en la calzada que va hacia el puerto (decreciente, como dice
            # el feed). El otro extremo no cambia (PK ± largo en los dos casos): solo se giran los papeles.
            ref = caminos.norm_ref(via)
            hacia_otro = rumbo_entre(p["la2"], p["lo2"], p["la"], p["lo"])
            votos, rumbo_cam = [], None
            for d, t, wi, i in sorted(red.cercanos((p["la2"], p["lo2"]), 40.0)):
                w = red.vias[wi]
                if w.ref == ref and not w.tipo.endswith("_link") and w.sentido != 0:
                    fb = caminos.rumbo(w.pts[i], w.pts[i + 1])
                    if w.sentido == -1:
                        fb = (fb + 180) % 360
                    votos.append(abs((fb - hacia_otro + 180) % 360 - 180) < 90)
                    if rumbo_cam is None:
                        rumbo_cam = fb   # el de la calzada más cercana a la cámara
            if votos and all(votos):
                p["la"], p["lo"], p["la2"], p["lo2"] = p["la2"], p["lo2"], p["la"], p["lo"]
                if p.get("pk2") is not None:
                    p["pk"], p["pk2"] = p["pk2"], p["pk"]
                if p.get("s") in ("Creciente", "Decreciente"):
                    p["s"] = "Decreciente" if p["s"] == "Creciente" else "Creciente"
                p.pop("rb", None)
                p["_camara_entrada"] = True
                log(f"  tramo {p['id']}: la cámara del feed es la entrada (su calzada va hacia el otro extremo) → {p['s']}")
                p["rb"] = round(rumbo_cam, 1)
            # el extremo hecho por PK (la entrada, o la salida si se ha girado) sobre la calzada que va en el sentido
            # del tramo: el PK de la recta entre hitos puede caer en un enlace o en la otra calzada
            k_la, k_lo = ("la2", "lo2") if p.get("_camara_entrada") else ("la", "lo")
            rb_t = rumbo_entre(p["la"], p["lo"], p["la2"], p["lo2"])
            mejor = None
            for d, t, wi, i in red.cercanos((p[k_la], p[k_lo]), 350.0):
                w = red.vias[wi]
                if w.ref != ref or w.tipo.endswith("_link"):
                    continue
                fb = caminos.rumbo(w.pts[i], w.pts[i + 1])
                sentidos = [fb] if w.sentido == 1 else [(fb + 180) % 360] if w.sentido == -1 else [fb, (fb + 180) % 360]
                if not any(abs((x - rb_t + 180) % 360 - 180) < 70 for x in sentidos):
                    continue
                if mejor is None or d < mejor[0]:
                    mejor = (d, caminos.interpolar(w.pts[i], w.pts[i + 1], t))
            if mejor and mejor[0] > 15:
                p[k_la], p[k_lo] = round(mejor[1][0], 6), round(mejor[1][1], 6)
                movidos += 1
            continue
        if p.get("la2") is not None and p.get("pk2") is not None and not p.get("_orient_pdf"):
            c2 = _sobre_la_via(red, via, float(p["pk2"]), prov, geo)
            if c2 and distancia(p["la2"], p["lo2"], c2[0], c2[1]) < 400:
                p["la2"], p["lo2"] = round(c2[0], 6), round(c2[1], 6)
    return f"✅ {texto} → {movidos} de {len(por_pk)} situados por PK recolocados por la carretera"


PRIORIDAD_FUENTE = ("dgt:", "sct:", "ansr:", "mad:", "madfr:", "madzbe:", "vlc:", "dss:", "slmt:", "lis:", "vdc:",
                    "mlgfr:", "dgtpdf:", "dgteq:", "com:", "osm:")


def prioridad(p: dict) -> int:
    for i, pre in enumerate(PRIORIDAD_FUENTE):
        if p["id"].startswith(pre):
            return i
    return len(PRIORIDAD_FUENTE)


def pos_pk(p: dict, geo: "Geocodificador"):
    """Dónde cae su PK con los hitos de CartoCiudad (solo si los dos hitos son normales: 400-1700 m)."""
    if p.get("pk") is None or not p.get("c"):
        return None
    pk = float(p["pk"])
    k = int(math.floor(pk))
    a, b = geo._hito(p["c"], k, p.get("pr")), geo._hito(p["c"], k + 1, p.get("pr"))
    if not (a and b) or not 400 < distancia(a[0], a[1], b[0], b[1]) < 1700:
        return None
    f = pk - k
    return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f


def camaras_osm_opl(ruta: str) -> list:
    """Todas las cámaras de velocidad de OSM del extracto (también las quitadas por copia de un oficial)."""
    if not os.path.exists(ruta):
        return []
    out = []
    for e in opl_a_overpass(ruta)["elements"]:
        t = e.get("tags") or {}
        if e["type"] == "node" and (t.get("highway") == "speed_camera" or t.get("enforcement") == "maxspeed"
                                    or "speed_camera" in t):
            out.append((e["lat"], e["lon"], t))
        elif e["type"] == "relation" and t.get("enforcement") == "maxspeed":
            for m in e.get("members") or []:
                if m["type"] == "node" and m.get("role") in ("device", ""):
                    out.append((m["lat"], m["lon"], t))
    return out


def revision_final(todos: list[dict], ruta_red: str, geo: "Geocodificador") -> tuple[str, list]:
    """
    Última revisión, con testigos independientes (auditoría del 7-11-2026):
      1. Tercer testigo: un radar oficial a más de 150 m de su propio PK, con una cámara de OSM a menos de 100 m de
         ese PK → la coordenada era la mala (en el feed de la DGT pasa en ~1 de cada 6: A-40 km 299,5 a 446 m,
         A-4 km 40,4 a 409 m, N-432 km 111,6 a 347 m...). Se lleva a la cámara de OSM.
      2. Situados solo por su PK que han acabado sobre otra vía (una calle a 20 m y su carretera a 150 m) → a su
         carretera.
      3. Rumbo cruzado con su carretera (avisaría en la que la cruza) → el del sentido oficial, o en los dos.
      4. El mismo radar dos veces (misma clase, < 25 m, mismo sentido) → se queda el de la fuente más fiable.
    Devuelve el resumen y los puntos a los que hay que rehacer el camino.
    """
    import caminos
    FIJOS = ("RADAR_FIJO", "OTRA_CAMARA", "SEMAFORO", "STOP_CEDA")
    cambiados: dict = {}
    res = {"testigo": [], "su_via": [], "cruzado": [], "duplicados": []}

    # 1. tercer testigo
    cams = camaras_osm_opl(CAMARAS_OPL)
    rej = Rejilla()
    for la, lo, t in cams:
        rej.add({"la": la, "lo": lo, "t": "_osm", "tags": t})
    nuestros = Rejilla()
    for p in todos:
        if p["t"] in FIJOS:
            nuestros.add(p)
    for p in todos:
        if p["t"] != "RADAR_FIJO" or p.get("_verif") or not p["id"].startswith(("dgt:", "dgtpdf:F")):
            continue
        e = pos_pk(p, geo)
        if not e or distancia(e[0], e[1], p["la"], p["lo"]) <= 150:
            continue
        c = rej.cerca(e[0], e[1], 100)
        if c is None:
            continue
        # que la cámara no sea otro radar nuestro (uno distinto ya puesto ahí)
        otro = nuestros.cerca(c["la"], c["lo"], 40, lambda q: q is not p and q["t"] == "RADAR_FIJO")
        if otro is not None:
            continue
        d_osm = c["tags"].get("direction")
        if p.get("rb") is not None and d_osm and d_osm.replace(".", "").isdigit() and \
                abs((float(d_osm) - p["rb"] + 180) % 360 - 180) > 60 and \
                abs((float(d_osm) + 180 - p["rb"] + 180) % 360 - 180) > 60:
            continue
        m = distancia(c["la"], c["lo"], p["la"], p["lo"])
        if m > 700:
            continue
        log(f"  testigo: {p['id']} {p.get('c')} PK {p.get('pk')} a {distancia(e[0], e[1], p['la'], p['lo']):.0f} m de su PK; "
            f"la cámara de OSM, a {distancia(e[0], e[1], c['la'], c['lo']):.0f} m → se mueve {m:.0f} m")
        p["la"], p["lo"] = round(c["la"], 6), round(c["lo"], 6)
        p.pop("px", None)
        p["_pos_osm"] = True
        res["testigo"].append(p["id"])
        cambiados[p["id"]] = p

    # 2 y 3 necesitan la red
    if os.path.exists(ruta_red):
        fijos = [p for p in todos if p["t"] in FIJOS and not p.get("_verif")]
        red = caminos.cargar_red(ruta_red, fijos)

        def ref_de(c):
            if not c or not re.fullmatch(r"[A-Z]{1,5}-?\d{1,4}[A-Z]?(-\d+)?", c.strip().upper()):
                return None
            return caminos.norm_ref(c)

        for p in fijos:
            rc = ref_de(p.get("c"))
            pos = (p["la"], p["lo"])
            cerca = sorted(((d, wi, i, t) for d, t, wi, i in red.cercanos(pos, 400)), key=lambda x: x[0])
            if not cerca:
                continue
            propios = [x for x in cerca if rc and red.vias[x[1]].ref == rc]
            # 2. situado por PK sobre otra vía
            if (p.get("px") or p["id"].startswith(("dgtpdf:", "dgteq:"))) and propios and \
                    propios[0][0] > max(60.0, cerca[0][0] + 40) and not p.get("_pos_osm"):
                d, wi, i, t = propios[0]
                w = red.vias[wi]
                a, b = w.pts[i], w.pts[i + 1]
                nueva = caminos.interpolar(a, b, t)
                log(f"  su vía: {p['id']} {p.get('c')} PK {p.get('pk')}: estaba a {d:.0f} m de su carretera → a ella")
                p["la"], p["lo"] = round(nueva[0], 6), round(nueva[1], 6)
                res["su_via"].append(p["id"])
                cambiados[p["id"]] = p
                continue
            # 3. rumbo cruzado
            rb = p.get("rb")
            if rb is None:
                continue
            base = [x for x in (propios or cerca) if x[0] <= 30]
            if not base:
                continue
            ejes = [caminos.rumbo(red.vias[x[1]].pts[x[2]], red.vias[x[1]].pts[x[2] + 1]) for x in base]
            if any(min(caminos.dif(rb, r), caminos.dif(rb, (r + 180) % 360)) <= 50 for r in ejes):
                continue
            # para elegir entre las dos direcciones de su propia carretera basta un par de hitos (no hace falta la
            # comprobación estricta de rumbo_oficial, que es para llevarle la contraria a otro rumbo)
            ro = rumbo_oficial(p, geo)
            if ro is None and p.get("s") in ("Creciente", "Decreciente") and p.get("c") and p.get("pk") is not None:
                ro = geo.rumbo(p["c"], float(p["pk"]), p.get("pr"), p["s"])
            nuevo = None
            if ro is not None:
                mejor = min(((caminos.dif(ro, rr), rr) for r in ejes for rr in (r, (r + 180) % 360)), key=lambda x: x[0])
                if mejor[0] <= 75:
                    nuevo = round(mejor[1], 1)
            log(f"  rumbo cruzado: {p['id']} {p.get('c')} rumbo {rb} y su vía va a {[round(r) for r in ejes]} → {nuevo}")
            if nuevo is None:
                p.pop("rb", None)
            else:
                p["rb"] = nuevo
            res["cruzado"].append(p["id"])
            cambiados[p["id"]] = p

    # 4. el mismo radar dos veces
    fuera = set()
    rej2 = Rejilla()
    for p in todos:
        if p["t"] in FIJOS or p["t"] == "RADAR_TRAMO":
            rej2.add(p)

    def compatibles(p, q):
        if p.get("s") in ("Creciente", "Decreciente") and q.get("s") in ("Creciente", "Decreciente") and p["s"] != q["s"]:
            return False
        rp, rq = p.get("rb"), q.get("rb")
        return rp is None or rq is None or abs((rp - rq + 180) % 360 - 180) <= 45

    for p in todos:
        if p["id"] in fuera or not (p["t"] in FIJOS or p["t"] == "RADAR_TRAMO"):
            continue
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                kx, ky = rej2._k(p["la"], p["lo"])
                for q in rej2.d.get((kx + dx, ky + dy), []):
                    if q is p or q["id"] in fuera or p["id"] in fuera or q["t"] != p["t"] or not compatibles(p, q):
                        continue
                    if distancia(p["la"], p["lo"], q["la"], q["lo"]) > 25:
                        continue
                    if p["t"] == "RADAR_TRAMO":
                        if p.get("la2") is None or q.get("la2") is None or \
                                distancia(p["la2"], p["lo2"], q["la2"], q["lo2"]) > 60:
                            continue
                    if p.get("_verif") or q.get("_verif"):
                        continue
                    queda, va = (p, q) if prioridad(p) <= prioridad(q) else (q, p)
                    if queda.get("rb") is None and va.get("rb") is not None and queda.get("s") != "Ambos":
                        queda["rb"] = va["rb"]
                        cambiados[queda["id"]] = queda
                    fuera.add(va["id"])
                    res["duplicados"].append(f"{va['id']}→{queda['id']}")
    todos[:] = [p for p in todos if p["id"] not in fuera]
    for i in fuera:
        cambiados.pop(i, None)
    for p in cambiados.values():
        for k in ("ap", "rt", "pl"):
            p.pop(k, None)
    msg = (f"{len(res['testigo'])} movidos a su cámara de OSM (estaban a más de 150 m de su PK y OSM la tiene en él); "
           f"{len(res['su_via'])} llevados a su carretera; {len(res['cruzado'])} con el rumbo cruzado corregido; "
           f"{len(res['duplicados'])} duplicados quitados")
    log(f"revisión final: {msg}: {res}")
    return msg, list(cambiados.values())


def rumbo_oficial(p: dict, geo: "Geocodificador") -> float | None:
    """
    Rumbo de circulación que dice la fuente oficial (vía + PK + creciente/decreciente) con los hitos de CartoCiudad.
    Solo si es claro: dos pares de hitos seguidos (k→k+1 y el de al lado) de longitud normal que apuntan igual
    (en una curva cerrada la cuerda de 1 km no dice nada) y el PK cae cerca del punto (o del otro extremo del tramo).
    """
    s = p.get("s")
    if s not in ("Creciente", "Decreciente") or not p.get("c") or p.get("pk") is None or p["t"] in ("ZONA_MOVIL", "TCA"):
        return None
    pk = float(p["pk"])
    k = int(math.floor(pk))
    hs = {km: geo._hito(p["c"], km, p.get("pr")) for km in (k - 1, k, k + 1, k + 2) if km >= 0}

    def cuerda(a, b):
        ha, hb = hs.get(a), hs.get(b)
        if ha and hb and 450 < distancia(ha[0], ha[1], hb[0], hb[1]) < 1700:
            return rumbo_entre(ha[0], ha[1], hb[0], hb[1])
        return None
    c0 = cuerda(k, k + 1)
    otra = cuerda(k - 1, k) if pk - k < 0.5 else cuerda(k + 1, k + 2)
    otra = otra if otra is not None else (cuerda(k + 1, k + 2) if pk - k < 0.5 else cuerda(k - 1, k))
    if c0 is None or otra is None or abs((c0 - otra + 180) % 360 - 180) > 60:
        return None
    pos = geo.pk(p["c"], pk, p.get("pr"))
    extremos = [(p["la"], p["lo"])] + ([(p["la2"], p["lo2"])] if p.get("la2") is not None else [])
    if not pos or min(distancia(pos[0], pos[1], la, lo) for la, lo in extremos) > 2000:
        return None
    return round((c0 + 180) % 360 if s == "Decreciente" else c0, 1)


def imponer_sentido_oficial(puntos: list[dict], geo: "Geocodificador") -> tuple[str, list]:
    """
    Última palabra del sentido oficial. Varios pasos ponen o cambian rumbos (segunda opinión de radares-datos,
    herencia de OSM, gemelos, orientación de tramos...) y alguno puede dejarlo al revés de lo que dice la DGT: en la
    N-601 (Mansilla) y la CL-613/CL-615 (Palencia) los tramos «decrecientes» avisaban en el sentido creciente y
    los gemelos de la N-332 en Cullera estaban cambiados. Aquí, si el rumbo va contra el sentido oficial (más de
    120°) y los hitos lo dejan claro, manda el oficial; a los tramos se les orienta la entrada. Lo comprobado sobre
    el terreno no se toca. Devuelve el resumen y los puntos cambiados (hay que rehacer sus caminos).
    """
    cambiados, revisados = [], 0
    pet = set()
    for p in puntos:
        if p.get("s") in ("Creciente", "Decreciente") and p.get("c") and p.get("pk") is not None \
                and p["t"] not in ("ZONA_MOVIL", "TCA"):
            k = int(math.floor(float(p["pk"])))
            pet |= {(p["c"], km, p.get("pr")) for km in (k - 1, k, k + 1, k + 2) if km >= 0}
    geo.precargar(pet)
    for p in puntos:
        if p.get("_verif") or p.get("_camara_entrada"):
            continue
        ro = rumbo_oficial(p, geo)
        if ro is None:
            continue
        revisados += 1
        rb = p.get("rb")
        girar_tramo = p.get("la2") is not None and abs(
            (rumbo_entre(p["la"], p["lo"], p["la2"], p["lo2"]) - ro + 180) % 360 - 180) > 100 and \
            distancia(p["la"], p["lo"], p["la2"], p["lo2"]) > 250
        if (rb is not None and abs((rb - ro + 180) % 360 - 180) > 120) or girar_tramo:
            log(f"  sentido oficial: {p['id']} {p.get('c')} PK {p.get('pk')} {p.get('s')}: rumbo {rb} → {ro}"
                + (" (tramo girado)" if girar_tramo else ""))
            p["rb"] = ro
            if girar_tramo:
                p["la"], p["lo"], p["la2"], p["lo2"] = p["la2"], p["lo2"], p["la"], p["lo"]
                if p.get("pk2") is not None:
                    p["pk"], p["pk2"] = p["pk2"], p["pk"]
            for k in ("ap", "rt", "pl"):
                p.pop(k, None)
            cambiados.append(p)
    return (f"{revisados} con sentido oficial comprobable; {len(cambiados)} corregidos: "
            + ", ".join(p["id"] for p in cambiados[:30])), cambiados


def orientar_tramos_feed(puntos: list[dict], geo: "Geocodificador") -> str:
    """
    Los tramos del feed de la DGT traen dos puntos, pero no siempre la entrada primero: en muchos el primero es la
    cámara de SALIDA (en la V-30, "hacia Alicante", el primero era el PK 4,7, el final del tramo). Con el sentido
    oficial (creciente/decreciente) y los hitos se sabe hacia dónde se circula; si el tramo va al revés, se le da
    la vuelta. Si no, la app lo avisaba en la otra calzada y en el sentido contrario. Se comprueba antes contra
    los tramos de OSM y del PDF que coinciden: solo se aplica si en la gran mayoría el sentido oficial acierta.
    """
    # (los que se han hecho con el PDF ya están orientados por él)
    tramos = [p for p in puntos if p["id"].startswith("dgt:") and p["t"] == "RADAR_TRAMO" and p.get("la2") is not None
              and not p.get("_orient_pdf")]
    completar_rumbos(tramos, geo)
    # el rumbo que traiga (segunda opinión, OSM...) puede estar al revés: para decidir manda el oficial
    for p in tramos:
        ro = rumbo_oficial(p, geo)
        if ro is not None:
            p["rb"] = ro
    ref = [p for p in puntos if p["t"] == "RADAR_TRAMO" and p.get("la2") is not None
           and p["id"].startswith(("osm:", "dgtpdf:", "ansr:"))]

    def al_reves(p):
        return abs((rumbo_entre(p["la"], p["lo"], p["la2"], p["lo2"]) - p["rb"] + 180) % 360 - 180) > 120

    a_favor = en_contra = 0
    for p in tramos:
        if p.get("rb") is None:
            continue
        # con los dos PK: la entrada es el PK menor si es creciente y el mayor si es decreciente
        if p.get("pk2") is not None and p.get("pk") != p.get("pk2") and p.get("s") in ("Creciente", "Decreciente"):
            entra_la2 = (p["s"] == "Creciente") == (p["pk2"] < p["pk"])
            if al_reves(p) == entra_la2:
                a_favor += 1
            else:
                en_contra += 1
        for o in ref:
            igual = max(distancia(p["la"], p["lo"], o["la"], o["lo"]), distancia(p["la2"], p["lo2"], o["la2"], o["lo2"]))
            inverso = max(distancia(p["la"], p["lo"], o["la2"], o["lo2"]), distancia(p["la2"], p["lo2"], o["la"], o["lo"]))
            if min(igual, inverso) < 300:
                # el sentido oficial acierta si dice "al revés" justo cuando la otra fuente lo tiene al revés
                if al_reves(p) == (inverso < igual):
                    a_favor += 1
                else:
                    en_contra += 1
                break
    if a_favor < 8 or a_favor < 3 * en_contra:
        return f"⚠️ el sentido oficial no cuadra con OSM/PDF ({a_favor} a favor, {en_contra} en contra): no se toca"
    girados = []
    for p in tramos:
        if p.get("rb") is not None and al_reves(p):
            p["la"], p["lo"], p["la2"], p["lo2"] = p["la2"], p["lo2"], p["la"], p["lo"]
            if p.get("pk2") is not None:
                p["pk"], p["pk2"] = p["pk2"], p["pk"]
            for k in ("ap", "rt"):
                p.pop(k, None)
            girados.append(p["id"])
    log(f"tramos del feed girados: {girados}")
    return (f"{len(girados)} de {len(tramos)} tramos del feed de la DGT venían con la salida primero y se les ha dado "
            f"la vuelta (comprobado con OSM/PDF: {a_favor} a favor, {en_contra} en contra)")


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
    # El mismo tramo entero por dos fuentes (la DGT situada por PK, con ~100 m de error en cada extremo, y OSM,
    # trazada sobre la foto aérea): se queda el oficial con los extremos de OSM, que son más exactos
    osm_t = [t for t in tramos if t["f"] == "OSM"]
    duplicados = 0
    for t in tramos:
        if t["f"] == "OSM" or t["id"] in fuera:
            continue
        mejor = None
        for o in osm_t:
            if o["id"] in fuera:
                continue
            d = max(distancia(t["la"], t["lo"], o["la"], o["lo"]), distancia(t["la2"], t["lo2"], o["la2"], o["lo2"]))
            if d < 400 and (mejor is None or d < mejor[0]):
                mejor = (d, o)
        if mejor:
            o = mejor[1]
            if t["id"].startswith("dgtpdf:"):   # situado por PK: los extremos de OSM son mejores
                t["la"], t["lo"], t["la2"], t["lo2"] = o["la"], o["lo"], o["la2"], o["lo2"]
                t["_pos_osm"] = True
            for k in ("v",):
                if k not in t and k in o:
                    t[k] = o[k]
            fuera.add(o["id"]); duplicados += 1
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
    log(f"tramos: {duplicados} tramos repetidos (oficial y OSM) unidos, {sueltos} puntos sueltos unidos a su tramo, "
        f"{camaras} cámaras de entrada/salida absorbidas")
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


# Fuentes que cambian mucho de un día a otro por naturaleza (avisos semanales de radares móviles)
FUENTES_VARIABLES = {"Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados)"}


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

    def ejecutar(nombre, fn, si_falla: str | None = None):
        t0 = time.time()
        try:
            r = fn()
            if not r:
                raise RuntimeError("sin datos")
            # Respuesta a medias (Overpass cortado, un PDF que se lee mal…): si trae menos del 60 % de lo de la
            # vez anterior, se toma como fallo. Antes se publicaba y el móvil perdía esos radares hasta el día siguiente.
            prev_n = len(previos_por_fuente.get(nombre, []))
            if prev_n >= 30 and len(r) < 0.6 * prev_n and nombre not in FUENTES_VARIABLES:
                raise RuntimeError(f"solo {len(r)} de {prev_n}: respuesta incompleta")
            for p in r:
                p["src"] = nombre
            estado[nombre] = f"✅ {len(r)} ({time.time() - t0:.0f}s)"
            log(f"{nombre}: {len(r)} puntos")
            return r
        except Exception as e:  # noqa: BLE001
            prev = previos_por_fuente.get(nombre, [])
            if si_falla and not prev:
                # fuentes que desde GitHub no responden (bloquean IP de fuera de España) y ya baja la app
                estado[nombre] = f"ℹ️ {si_falla}"
                log(f"{nombre}: no responde ({e}); {si_falla}")
                return prev
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

        tomados: set = set()

        def en_feed(via, pk, sentido=None):
            """
            El feed trae vía y PK: se casa por ahí, sin depender de geocodificar. Una cámara del feed solo casa con
            una fila: en la V-31 el radar fijo del PK 6,125 (decreciente) se casaba con el tramo del 6,35
            (creciente) y se perdía el fijo. Por eso se casan primero los fijos y, a igual distancia, gana el sentido.
            """
            mejor, dmin = None, 0.35
            for q in indice.get(via, []):
                if q.get("pk") is None or q["id"] in tomados:
                    continue
                dd = abs(q["pk"] - pk)
                if sentido in ("Creciente", "Decreciente") and q.get("s") in ("Creciente", "Decreciente") \
                        and q["s"] != sentido:
                    dd += 0.2   # de otro sentido: solo si no hay nada mejor
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
        for f in sorted(filas, key=lambda f: f["tipo"] != "Fijo"):   # los fijos primero (ver en_feed)
            if f["tipo"] == "Movil":
                continue
            prov = provincia_canonica(f["prov"])
            via = via_normalizada(f["via"])
            q = en_feed(via, f["pk"], f["sentido"])
            c = None
            if q is None:
                c = geo.pk(via, f["pk"], prov)
                if not c:
                    sin_situar += 1
                    log(f"    sin situar: {f['tipo']} {via} PK {f['pk']} {f['sentido']} ({f['prov']})")
                    continue
                # respaldo espacial por si el feed escribe la vía de otra forma
                q = rej.cerca(c[0], c[1], 400, lambda q: via_normalizada(q.get("c")) == via and q["id"] not in tomados)
            if q is not None:
                casados += 1
                tomados.add(q["id"])
                if not q.get("s") or q.get("s") == "Ambos":
                    q["s"] = f["sentido"]
                q.setdefault("pr", prov)
                if f["tipo"] == "Tramo":
                    q["t"] = "RADAR_TRAMO"
                    if "la2" not in q and f["sentido"] in ("Creciente", "Decreciente") and q.get("s") != f["sentido"]:
                        # el feed da una sola cámara (la de salida) y a veces el sentido contrario al del PDF: en la
                        # V-30 el feed dice decreciente y el PDF y la prensa, creciente (del PK 4,65 al 8,85). Para el
                        # tramo manda el PDF.
                        log(f"    tramo {via} PK {f['pk']}: sentido del feed {q.get('s')} → {f['sentido']} (PDF)")
                        q["s"] = f["sentido"]
                        q.pop("rb", None)
                    if f.get("longitud"):
                        q.setdefault("lm", f["longitud"])
                        if "la2" not in q:
                            # El PK de los tramos del PDF es el de la cámara de SALIDA (comprobado con los 13 tramos
                            # nuevos de 2026, que la DGT anunció con PK de inicio y fin, y con los tramos de OSM): la
                            # cámara del feed que casa por ese PK es la de salida, y la entrada está «largo» antes.
                            # Antes se ponía la entrada aquí y el tramo quedaba corrido un tramo entero más allá.
                            largo = f["longitud"] / 1000
                            pk_ini = f["pk"] + largo if f["sentido"] == "Decreciente" else f["pk"] - largo
                            c1 = geo.pk(via, pk_ini, prov) if pk_ini >= 0 else None
                            if c1:
                                q["la2"], q["lo2"], q["pk2"] = q["la"], q["lo"], q.get("pk", f["pk"])
                                q["la"], q["lo"], q["pk"] = round(c1[0], 6), round(c1[1], 6), round(pk_ini, 3)
                                q["_orient_pdf"] = True   # entrada por su PK (y orientado por el PDF)
                continue
            base = dict(c=via, pk=f["pk"], s=f["sentido"], pr=prov, ca=PROVINCIAS[prov][1] if prov else None)
            if f["tipo"] == "Tramo" and f.get("longitud"):
                largo = f["longitud"] / 1000
                sentidos = ["Creciente", "Decreciente"] if f["sentido"] == "Ambos" else [f["sentido"]]
                for s in sentidos:
                    # el PK del PDF es la cámara de salida (ver arriba): la entrada está «largo» antes en su sentido
                    pk_ini = f["pk"] - largo if s != "Decreciente" else f["pk"] + largo
                    c1 = geo.pk(via, pk_ini, prov) if pk_ini >= 0 else None
                    if c1:
                        salida.append(punto(f"dgtpdf:T:{via}:{f['pk']}:{s[0]}", "RADAR_TRAMO", "DGT", c1[0], c1[1],
                                            la2=round(c[0], 6), lo2=round(c[1], 6), pk2=f["pk"],
                                            lm=f["longitud"], **{**base, "pk": round(pk_ini, 3), "s": s}))
                    else:
                        log(f"  tramo {via} PK {f['pk']} ({s}): no se pudo situar su entrada (PK {pk_ini:.3f})")
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
    lisboa = ejecutar("Câmara Municipal de Lisboa", fuente_lisboa)
    viladecans = ejecutar("Ajuntament de Viladecans", fuente_viladecans)
    ansr = ejecutar("Portugal: ANSR (red SINCRO)", fuente_ansr)
    desde_movil = "desde GitHub no responde; la app lo descarga en el móvil (fuentes_movil.json)"
    santacruz = ejecutar("Ayto. Santa Cruz de Tenerife foto-rojo", fuente_santacruz, desde_movil)
    pamplona = ejecutar("Ayto. Pamplona cinemómetros", fuente_pamplona, desde_movil)
    comunitario = ejecutar("Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados)", fuente_feed_comunitario)
    comunitario = solo_tramos_nuevos(comunitario, zonas)
    log(f"feed comunitario tras quitar tramos ya situados: {len(comunitario)}")

    todos = fusionar([feed, pdf_radares, sct, madrid, madrid2, valencia, malaga, salamanca, donostia, ansr, lisboa, viladecans, santacruz, pamplona,
                      camaras_dgt, comunitario, osm, zonas])
    log(f"fusión: {FUSION['opuestos']} radares que estaban junto a otro del sentido contrario se mantienen (antes se perdían)")
    todos = unir_tramos(todos)
    try:
        msg = a_la_linea_de_detencion(todos)
    except Exception as e:  # noqa: BLE001
        msg = f"falló ({e})"
    estado["Cámaras de stop y semáforo"] = msg
    log(msg)
    todos = aplicar_correcciones(todos)
    estado["Puntos comprobados"] = aplicar_verificados(todos)
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
    muestras = []
    for p in todos:
        txt = p.pop("_hacia_txt", None)
        if txt and p.get("rb") is None:
            c = geo.lugar(txt.title(), (p["la"], p["lo"]))
            # (a más de 1,2 km: si el radar ya está en el pueblo, "hacia" no dice nada)
            if c and 1200 < distancia(c[0], c[1], p["la"], p["lo"]):
                p["_hacia"] = c
                hacia += 1
                if hacia <= 8:
                    muestras.append(f"{txt} → {c[0]:.3f},{c[1]:.3f} ({distancia(c[0], c[1], p['la'], p['lo']) / 1000:.0f} km)")
    geo.guardar()
    log(f"sentido hacia una ciudad: {hacia} puntos; {muestras}")
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

    # con todos los sentidos ya puestos (hitos, segunda opinión, herencia de OSM): los tramos del feed que vienen
    # con la salida primero se giran, y ya en su sentido se unen con su copia de OSM
    try:
        estado["Sentido de los tramos de la DGT"] = orientar_tramos_feed(todos, geo)
        todos = unir_tramos(todos)
    except Exception as e:  # noqa: BLE001
        estado["Sentido de los tramos de la DGT"] = f"falló ({e})"

    zbe = ejecutar_zbe(anterior, estado)

    # Caminos de aproximación por la red viaria de OSM (la app solo avisa si vas por esa carretera)
    ruta_red = "red/vias.geojsonseq"
    if os.path.exists(ruta_red):
        try:
            import caminos
            try:
                estado["Situados por PK"] = pk_por_la_carretera(todos, ruta_red, geo)
            except Exception as e:  # noqa: BLE001
                estado["Situados por PK"] = f"⚠️ falló ({e})"
                log(f"PK por la carretera: ERROR {e}")
            st = caminos.anadir_caminos(todos, ruta_red, zbe, aviso=log)
            try:
                sz = caminos.trazar_zonas([p for p in todos if p["t"] == "ZONA_MOVIL" and p.get("tr")], ruta_red, aviso=log)
                estado["Zonas de radar móvil por carretera"] = (
                    f"{sz['zonas_trazadas']} de {sz['zonas_rectas']} que venían en línea recta siguen ya la carretera"
                    f" ({sz['zonas_sin_trazar']} sin poder trazar)")
                log(f"zonas: {sz}")
            except Exception as e:  # noqa: BLE001
                log(f"zonas: ERROR {e}")
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
            # Los del PDF de la DGT están situados por su PK (hitos de CartoCiudad, ~100 m de error); su copia de
            # OSM está puesta sobre la foto aérea: el radar se queda con la posición de OSM
            recolocados = 0
            for o, f, m in pares:
                if o["id"] in fuera and f["id"].startswith(("dgtpdf:", "dgteq:")):
                    f["_en_osm"] = True   # su copia de OSM confirma dónde está
                if o["id"] in fuera and f["id"].startswith(("dgtpdf:F", "dgteq:")) and m > 20 and not f.get("_verif"):
                    f["la"], f["lo"] = o["la"], o["lo"]
                    f.pop("ap", None)
                    if f not in reencajar:
                        reencajar.append(f)
                    recolocados += 1
            log(f"radares del PDF de la DGT recolocados en su copia de OSM: {recolocados}")
            todos[:] = [p for p in todos if p["id"] not in fuera]
            if reencajar:
                caminos.anadir_caminos(reencajar, ruta_red, zbe, aviso=log)   # su camino, ya en un solo sentido
            estado["Copias de OSM de radares oficiales"] = (
                f"{len(fuera)} quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: "
                f"{ok}/{n} → " + (f"heredado en {len(reencajar) - recolocados}" if heredar else "no se hereda")
                + f"; {recolocados} radares del PDF de la DGT llevados a la posición de su copia de OSM")
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
            # Gemelos: dos radares oficiales en el mismo sitio, uno "creciente" y otro "decreciente" (una cabina por
            # sentido, o una que vigila los dos), a los que el cálculo de rumbos ha dado el mismo sentido. Uno de los
            # dos está mal: se le da el contrario, y así queda uno en cada sentido como dice la fuente.
            gemelos = []
            # ...y si ninguno de los dos tiene sentido (misma cabina "creciente" y "decreciente", como en el túnel
            # de la M-111) cada uno avisaba en los mismos caminos: dos avisos en un sentido y ninguno en el otro.
            # Se le da a uno el sentido de su camino y al otro el contrario.
            for q, p in caminos.gemelos_sin_sentido(todos):
                q["rb"] = round(caminos.llegada(q["ap"][0]), 1)
                p["rb"] = round((q["rb"] + 180) % 360, 1)
                gemelos += [q, p]
            for m, q, p in seg:
                if m < 80 and q["t"] == p["t"] and q.get("s") in ("Creciente", "Decreciente") and \
                        p.get("s") in ("Creciente", "Decreciente") and q["s"] != p["s"] and q.get("rb") is not None \
                        and p["id"] not in {g["id"] for g in gemelos}:
                    p["rb"] = round((q["rb"] + 180) % 360, 1)
                    gemelos.append(p)
            if gemelos:
                caminos.anadir_caminos(gemelos, ruta_red, zbe, aviso=log)
                seg = caminos.seguidos(todos)
            log(f"gemelos de sentido contrario corregidos: {len(gemelos)} {[g['id'] for g in gemelos][:10]}")
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

    if os.path.exists(ruta_red):
        try:
            estado["Cámaras de semáforo"] = semaforos_por_su_cruce(todos, ruta_red, zbe)
        except Exception as e:  # noqa: BLE001
            estado["Cámaras de semáforo"] = f"⚠️ falló ({e})"
            log(f"semáforos: ERROR {e}")
    # Revisión final con testigos independientes y el sentido oficial (creciente/decreciente con los hitos) por
    # encima de lo que hayan dejado los demás pasos; después se rehacen los caminos de lo que haya cambiado
    rehacer: dict = {}
    try:
        msg, cambiados = imponer_sentido_oficial(todos, geo)
        estado["Sentido oficial (última comprobación)"] = msg
        rehacer.update({p["id"]: p for p in cambiados})
    except Exception as e:  # noqa: BLE001
        log(f"sentido oficial: ERROR {e}")
        estado["Sentido oficial (última comprobación)"] = f"⚠️ falló ({e})"
    try:
        msg, cambiados = revision_final(todos, ruta_red, geo)
        estado["Revisión final"] = msg
        rehacer.update({p["id"]: p for p in cambiados})
    except Exception as e:  # noqa: BLE001
        log(f"revisión final: ERROR {e}")
        estado["Revisión final"] = f"⚠️ falló ({e})"
    if rehacer and os.path.exists(ruta_red):
        try:
            import caminos
            for p in rehacer.values():
                for k in ("ap", "rt", "pl"):
                    p.pop(k, None)
            caminos.anadir_caminos(list(rehacer.values()), ruta_red, zbe, aviso=log)
        except Exception as e:  # noqa: BLE001
            log(f"caminos de los revisados: ERROR {e}")
    # Segunda pasada de los comprobados, ya con todos los pasos que ponen o cambian sentidos (segunda opinión de
    # la DGT, herencia de OSM, gemelos…): si alguno se los ha cambiado, se vuelven a poner y se recalcula su camino
    try:
        cambiados: list = []
        msg_final = aplicar_verificados(todos, cambiados)
        if cambiados:
            for p in cambiados:
                p.pop("ap", None)
            if os.path.exists(ruta_red):
                caminos.anadir_caminos(cambiados, ruta_red, zbe, aviso=log)
            estado["Puntos comprobados"] = msg_final.replace("⚠️ ", "⚠️ al final: ")
    except Exception as e:  # noqa: BLE001
        log(f"verificados (final): ERROR {e}")
    # Los puntos comprobados tienen que poder avisarse: con su camino de aproximación (salvo tramos, que llevan
    # su recorrido)
    sin_camino = [p["_verif"] for p in todos if p.get("_verif") and p["t"] != "RADAR_TRAMO" and not p.get("ap")]
    if sin_camino:
        estado["Puntos comprobados"] = f"⚠️ sin camino de aproximación (no avisarían): {', '.join(sin_camino)}"
        log(f"verificados SIN CAMINO: {sin_camino}")
    # Situados solo por su PK (sin coordenadas de la fuente ni copia de OSM que los confirme): la app lo dice
    # («a unos 300 metros», «muy cerca») en vez de dar por exacto un sitio con decenas de metros de error
    aprox = 0
    for p in todos:
        if (p["id"].startswith(("dgtpdf:", "dgteq:")) and not p.get("_pos_osm") and not p.get("_en_osm")
                and not (p.get("_verif") and not p.get("_verif_px"))):
            p["px"] = 1
            aprox += 1
    estado["Posición aproximada (solo PK)"] = f"{aprox} puntos"
    for p in todos:  # campos de trabajo que no van al fichero
        for k in ("_dir", "_dirg", "_osm_dirg", "_rbs_osm", "_viejo", "_hacia", "_hacia_txt", "_rel", "_card", "_verif", "_la0", "_lo0", "_pos_osm", "_en_osm", "_verif_px", "_orient_pdf", "_camara_entrada"):
            p.pop(k, None)
    todos.sort(key=lambda p: (p["t"], p["id"]))
    ahora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    # Freno de emergencia: si desaparece más del 15 % de los radares y cámaras de golpe, algo ha ido mal
    # (una fuente grande caída sin datos de la vez anterior, un fallo en la fusión…): no se publica.
    # Tramos de concentración de accidentes: van aparte (no son equipos: sin caminos, sin cruces con radares)
    tca = ejecutar("Ministerio: tramos de concentración de accidentes", lambda: fuente_tca(geo))
    tca_ac = ejecutar("Tramos con muchos accidentes (autonómicas y provinciales, microdatos DGT)", lambda: fuente_accidentes_dgt(geo))
    geo.guardar()
    tca = tca + tca_ac
    if tca and os.path.exists(ruta_red):
        try:
            st_tca = caminos.trazar_zonas(tca, ruta_red, aviso=log)
            estado["Ministerio: tramos de concentración de accidentes"] += (
                f"; trazados por la carretera {st_tca['zonas_trazadas']} de {st_tca['zonas_rectas']}")
        except Exception as e:  # noqa: BLE001
            log(f"TCA: trazado falló ({e})")
    todos = [p for p in todos if p["t"] != "TCA"] + tca
    fijos = sum(1 for p in todos if p["t"] not in ("ZONA_MOVIL", "TCA"))
    fijos_antes = sum(1 for p in anterior.get("puntos", []) if p["t"] not in ("ZONA_MOVIL", "TCA"))
    if fijos_antes >= 1000 and fijos < 0.85 * fijos_antes:
        estado["⛔ No publicado"] = f"solo {fijos} radares y cámaras frente a {fijos_antes} de la vez anterior"
        log(f"NO SE PUBLICA: {fijos} frente a {fijos_antes}")
        escribir_informe(todos, estado, anterior.get("version", ahora), zbe)
        return 1
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
    tipos = ["RADAR_FIJO", "RADAR_TRAMO", "SEMAFORO", "STOP_CEDA", "OTRA_CAMARA", "ZONA_MOVIL", "TCA"]
    nombres = {"RADAR_FIJO": "Fijos", "RADAR_TRAMO": "Tramo", "SEMAFORO": "Semáforo", "STOP_CEDA": "Stop/ceda",
               "OTRA_CAMARA": "Otras cám.", "ZONA_MOVIL": "Zonas móvil", "TCA": "Accidentes"}
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
