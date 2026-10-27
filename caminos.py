#!/usr/bin/env python3
"""
Caminos de aproximación: para cada radar o cámara, el trozo de su carretera por el que se llega a él
(en su sentido de circulación), y para cada radar de tramo su recorrido real de inicio a fin.

Con esto la app solo avisa cuando vas por esa carretera y en esa dirección: nada de radares de la vía
paralela, del carril contrario, de un puente o de una calle que cruza.

Entrada: red viaria de OpenStreetMap exportada con osmium a GeoJSON por líneas (una vía por línea).
Las vías se unen por sus nodos compartidos (mismas coordenadas en el cruce).
"""
from __future__ import annotations

import json
import math
import sys
import time

# Clase de vía: cuanto más bajo, más importante. Sirve para seguir "la carretera principal" en los cruces.
CLASE = {
    "motorway": 1, "trunk": 1, "primary": 2, "secondary": 2, "motorway_link": 3, "trunk_link": 3,
    "primary_link": 3, "secondary_link": 3, "tertiary": 3, "tertiary_link": 4, "unclassified": 4,
    "residential": 4, "road": 4, "living_street": 5,
}
INTERURBANA = {"motorway", "trunk", "primary", "secondary", "motorway_link", "trunk_link", "primary_link", "secondary_link"}

CELDA_INTERES = 0.02    # ~2 km: se cargan solo las vías cerca de algún punto
CELDA_SEG = 0.002       # ~200 m: rejilla para encontrar el tramo de vía más cercano
RADIO_ENCAJE = 40.0     # m: distancia máxima del punto a su vía


# --------------------------------------------------------------------------- geometría
def dist(a, b):
    la1, lo1 = a
    la2, lo2 = b
    kx = 111320.0 * math.cos(math.radians((la1 + la2) / 2))
    return math.hypot((lo2 - lo1) * kx, (la2 - la1) * 110540.0)


def rumbo(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dl = math.radians(b[1] - a[1])
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def dif(a, b):
    d = abs(a - b) % 360
    return 360 - d if d > 180 else d


def proyectar(p, a, b):
    """Distancia de p al segmento ab y fracción t (0..1) del punto más cercano."""
    kx = 111320.0 * math.cos(math.radians(p[0]))
    ax, ay = (a[1] - p[1]) * kx, (a[0] - p[0]) * 110540.0
    bx, by = (b[1] - p[1]) * kx, (b[0] - p[0]) * 110540.0
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    t = 0.0 if l2 == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / l2))
    return math.hypot(ax + t * dx, ay + t * dy), t


def lado(p, a, b):
    """Distancia con signo de p a la recta a→b: positiva a la derecha del sentido a→b."""
    ky = 111320.0
    kx = 111320.0 * math.cos(math.radians(a[0]))
    bx, by = (b[1] - a[1]) * kx, (b[0] - a[0]) * ky
    px, py = (p[1] - a[1]) * kx, (p[0] - a[0]) * ky
    n = math.hypot(bx, by)
    return (bx * py - by * px) / n * -1 if n else 0.0


def interpolar(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def simplificar(pts, tol=4.0):
    """Douglas-Peucker en metros."""
    if len(pts) <= 2:
        return pts
    marca = [False] * len(pts)
    marca[0] = marca[-1] = True
    pila = [(0, len(pts) - 1)]
    while pila:
        i, j = pila.pop()
        dmax, k = 0.0, -1
        for m in range(i + 1, j):
            d, _ = proyectar(pts[m], pts[i], pts[j])
            if d > dmax:
                dmax, k = d, m
        if k >= 0 and dmax > tol:
            marca[k] = True
            pila += [(i, k), (k, j)]
    return [p for p, ok in zip(pts, marca) if ok]


def plano(pts):
    return [round(x, 5) for p in pts for x in p]


LIMITES_ES = {"es:urban": 50, "es:rural": 90, "es:motorway": 120, "es:trunk": 100, "es:living_street": 20,
              "es:zone30": 30, "es:zone20": 20, "es:school": 30, "es:bicycle_road": 30}


def velocidad(v):
    """maxspeed de OSM → km/h (o None)."""
    v = (v or "").strip().lower()
    if not v:
        return None
    if v in LIMITES_ES:
        return LIMITES_ES[v]
    n = v.split()[0].split(";")[0]
    if n.isdigit() and 10 <= int(n) <= 150:
        return int(n) if "mph" not in v else None
    return None


def norm_ref(r):
    return (r or "").upper().replace(" ", "").replace("-", "").split(";")[0]


# --------------------------------------------------------------------------- red viaria
class Via:
    __slots__ = ("pts", "clase", "ref", "nombre", "sentido", "tipo", "vmax", "vmax_ad", "vmax_at")

    def __init__(self, pts, tags):
        self.pts = pts
        self.tipo = tags.get("highway", "")
        self.clase = CLASE.get(self.tipo, 6)
        self.ref = norm_ref(tags.get("ref"))
        self.nombre = (tags.get("name") or "").strip().lower()
        self.vmax = velocidad(tags.get("maxspeed"))
        self.vmax_ad = velocidad(tags.get("maxspeed:forward")) or self.vmax
        self.vmax_at = velocidad(tags.get("maxspeed:backward")) or self.vmax
        ow = str(tags.get("oneway", "")).lower()
        if ow in ("yes", "1", "true"):
            self.sentido = 1
        elif ow == "-1":
            self.sentido = -1
        elif ow == "no":
            self.sentido = 0
        elif tags.get("junction") in ("roundabout", "circular") or self.tipo in ("motorway",):
            self.sentido = 1
        else:
            self.sentido = 0


class Red:
    def __init__(self):
        self.vias: list[Via] = []
        self.nodos: dict[tuple, list] = {}      # coord → [(vía, índice)]
        self.segs: dict[tuple, list] = {}       # celda → [(vía, índice)]
        self.con_limites = False                 # ¿trae la red los maxspeed? (exportaciones antiguas no)

    @staticmethod
    def clave(p):
        return (round(p[0], 6), round(p[1], 6))

    def anadir(self, pts, tags):
        if len(pts) < 2:
            return
        wi = len(self.vias)
        self.vias.append(Via(pts, tags))
        for i, p in enumerate(pts):
            self.nodos.setdefault(self.clave(p), []).append((wi, i))
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            # todas las celdas que toca el segmento (los de autovía pueden medir cientos de metros)
            y0, y1 = sorted((int(a[0] // CELDA_SEG), int(b[0] // CELDA_SEG)))
            x0, x1 = sorted((int(a[1] // CELDA_SEG), int(b[1] // CELDA_SEG)))
            if (y1 - y0 + 1) * (x1 - x0 + 1) > 400:
                y1, x1 = min(y1, y0 + 19), min(x1, x0 + 19)
            for cy in range(y0, y1 + 1):
                for cx in range(x0, x1 + 1):
                    self.segs.setdefault((cy, cx), []).append((wi, i))

    def cercanos(self, p, radio=RADIO_ENCAJE):
        cy, cx = int(p[0] // CELDA_SEG), int(p[1] // CELDA_SEG)
        vistos = set()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for s in self.segs.get((cy + dy, cx + dx), ()):
                    if s in vistos:
                        continue
                    vistos.add(s)
                    w = self.vias[s[0]]
                    d, t = proyectar(p, w.pts[s[1]], w.pts[s[1] + 1])
                    if d <= radio:
                        yield d, t, s[0], s[1]


def cargar_red(ruta: str, puntos: list[dict]) -> Red:
    interes = set()
    for p in puntos:
        cy, cx = int(p["la"] // CELDA_INTERES), int(p["lo"] // CELDA_INTERES)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                interes.add((cy + dy, cx + dx))
    red = Red()
    n = 0
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip().lstrip("\x1e")
            if not linea:
                continue
            n += 1
            try:
                ft = json.loads(linea)
            except ValueError:
                continue
            g = ft.get("geometry") or {}
            if g.get("type") != "LineString":
                continue
            c = g.get("coordinates") or []
            if not any((int(la // CELDA_INTERES), int(lo // CELDA_INTERES)) in interes for lo, la in c[::3] + c[-1:]):
                continue
            tags = ft.get("properties") or {}
            if tags.get("highway") not in CLASE:
                continue
            red.anadir([(la, lo) for lo, la in c], tags)
            if "maxspeed" in tags:
                red.con_limites = True
    print(f"  red viaria: {n} vías leídas, {len(red.vias)} cerca de algún punto", flush=True)
    return red


# --------------------------------------------------------------------------- recorridos
def se_puede(w: Via, paso: int) -> bool:
    """¿Se circula por la vía avanzando en su índice (+1) o al revés (-1)?"""
    return w.sentido == 0 or w.sentido == paso


def elegir(red: Red, nodo, via_actual: int, idx_actual: int, ref, nombre, clase, es_link, rumbo_ref, hacia_atras):
    """
    En un cruce, la continuación que sigue "la misma carretera": misma referencia, mismo nombre,
    misma importancia y el menor giro. Devuelve (vía, índice del cruce en esa vía, paso de tráfico) o None.

    Hacia delante: rumbo_ref es el rumbo con el que llegamos al cruce; se mira el rumbo de salida.
    Hacia atrás: rumbo_ref es el rumbo con el que el tráfico sale del cruce hacia el radar; se mira
    el rumbo con el que el tráfico entra en el cruce por cada vía.
    """
    mejor, puntuacion = None, 1e9
    for wj, k in red.nodos.get(nodo, ()):
        if wj == via_actual and k == idx_actual:
            continue
        w = red.vias[wj]
        for paso in (1, -1):
            otro = k - paso if hacia_atras else k + paso
            if not (0 <= otro < len(w.pts)) or not se_puede(w, paso):
                continue
            rb = rumbo(w.pts[otro], w.pts[k]) if hacia_atras else rumbo(w.pts[k], w.pts[otro])
            giro = dif(rb, rumbo_ref)
            if giro > 100:
                continue
            p = giro
            if ref and w.ref == ref:
                p -= 200
            elif ref and w.ref and w.ref != ref:
                p += 120
            if nombre and w.nombre == nombre:
                p -= 80
            p += 25 * abs(w.clase - clase)
            if w.tipo.endswith("_link") and not es_link:
                p += 60
            if p < puntuacion:
                mejor, puntuacion = (wj, k, paso), p
    return mejor


def caminar(red: Red, wi: int, i: int, t: float, paso: int, largo: float, hacia_atras: bool,
            objetivo=None, radio_objetivo=45.0, solo_enlace=False):
    """
    Recorre la red desde (vía wi, segmento i, fracción t) por la circulación que va en sentido `paso`.
    hacia_atras=True: contra el tráfico, para saber por dónde se llega. Devuelve los puntos recorridos;
    con objetivo, devuelve (puntos, llegado) y para al pasar a menos de radio_objetivo de él.
    """
    w = red.vias[wi]
    pts = [interpolar(w.pts[i], w.pts[i + 1], t)]
    resto = largo
    step = -paso if hacia_atras else paso          # avance del índice sobre la vía actual
    idx = i if step < 0 else i + 1
    via, ref, nombre, clase = wi, w.ref, w.nombre, w.clase
    vistos = {(wi, idx)}
    llegado = False
    while resto > 0:
        nodo = w.pts[idx]
        if objetivo is not None:
            dd, tt = proyectar(objetivo, pts[-1], nodo)
            if dd <= radio_objetivo:
                pts.append(interpolar(pts[-1], nodo, tt))
                llegado = True
                break
        d = dist(pts[-1], nodo)
        if d >= resto:
            pts.append(interpolar(pts[-1], nodo, resto / d if d else 0))
            break
        pts.append(nodo)
        resto -= d
        if 0 <= idx + step < len(w.pts):
            idx += step
            continue
        # fin de la vía: continuar por la misma carretera
        rb_ref = rumbo(pts[-1], pts[-2]) if hacia_atras else rumbo(pts[-2], pts[-1])
        e = elegir(red, Red.clave(nodo), via, idx, ref, nombre, clase, w.tipo.endswith("_link"), rb_ref, hacia_atras)
        if e is None:
            break
        wj, k, p2 = e
        if hacia_atras and solo_enlace and not red.vias[wj].tipo.endswith("_link"):
            # el punto está en una rampa: antes de la bifurcación no se sabe si vas a tomarla
            break
        w = red.vias[wj]
        step = -p2 if hacia_atras else p2
        idx = k + step
        if (wj, idx) in vistos:
            break
        vistos.add((wj, idx))
        via = wj
        ref = w.ref or ref
        nombre = w.nombre or nombre
        clase = w.clase
    return (pts, llegado) if objetivo is not None else pts


def longitud(pts):
    return sum(dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


# --------------------------------------------------------------------------- encaje
def encajar(red: Red, p: dict):
    """La vía del punto: la más cercana, prefiriendo la que tiene su misma referencia y su sentido."""
    pos = (p["la"], p["lo"])
    ref = norm_ref(p.get("c"))
    rb = p.get("rb")
    mejor, puntuacion = None, 1e9
    for d, t, wi, i in red.cercanos(pos):
        w = red.vias[wi]
        s = d
        if ref and w.ref:
            s += -15 if w.ref == ref else 25
        s += 4 * (w.clase - 1) if p["t"] in ("RADAR_FIJO", "RADAR_TRAMO") else 0
        if w.tipo.endswith("_link"):
            s += 10
        if rb is None and w.sentido != 0 and p["t"] != "ZONA_MOVIL":
            # calzada de un solo sentido: la cámara está a su derecha (o encima), no a su izquierda;
            # si queda a la izquierda, seguramente es de la calzada de enfrente
            ld = lado(pos, w.pts[i], w.pts[i + 1]) * w.sentido
            if ld < -3:
                s += 15
        if p.get("_dir") and d < 1.5:
            s -= 20   # nodo de OSM puesto sobre su vía: esa es
        if rb is not None:
            fb = rumbo(w.pts[i], w.pts[i + 1])
            opciones = [fb] if w.sentido == 1 else [(fb + 180) % 360] if w.sentido == -1 else [fb, (fb + 180) % 360]
            dmin = min(dif(rb, o) for o in opciones)
            # la calzada que circula en el sentido del radar manda (autovías: dos calzadas a pocos metros)
            s += dmin / 3 if dmin <= 60 else 150
        if s < puntuacion:
            mejor, puntuacion = (wi, i, t), s
    return mejor


LADO_MIN = 4.0   # m: por debajo, el punto está en el eje de la calle y no dice nada
# Franjas de distancia al eje (m) y tipos de vía en las que la regla "la cámara vigila el carril que tiene
# al lado" se pone a prueba con los radares de sentido conocido. Solo se usa donde acierta (ver calibrar_lado).
FRANJAS = ((4, 7), (7, 12), (12, 25), (25, 41))
URBANAS = {"residential", "living_street", "tertiary", "tertiary_link", "unclassified", "road"}
LADO_FIABLE: set = set()   # (franja, urbana) que han pasado la prueba en esta ejecución


def franja_lado(w: Via, ld: float):
    a = abs(ld)
    for f in FRANJAS:
        if f[0] <= a < f[1]:
            return (f, w.tipo in URBANAS)
    return None


def sentidos(red: Red, wi: int, i: int, rb, p: dict | None = None):
    """
    Sentidos de circulación (paso +1/-1 sobre la vía) que vigila el punto. En una vía de doble sentido sin
    rumbo conocido: el direction=forward/backward de OSM, y si no, el lado de la calle (en España se
    circula por la derecha y la cámara vigila el carril que tiene al lado). Solo si está en el eje, ambos.
    """
    w = red.vias[wi]
    if w.sentido != 0:
        return [w.sentido]
    if rb is not None:
        fb = rumbo(w.pts[i], w.pts[i + 1])
        return [1] if dif(rb, fb) <= 90 else [-1]
    if p is not None and p["t"] != "ZONA_MOVIL":
        pos = (p["la"], p["lo"])
        ld = lado(pos, w.pts[i], w.pts[i + 1])
        if p.get("_dir") in ("forward", "backward") and abs(ld) < 2:
            return [1 if p["_dir"] == "forward" else -1]
        # cámara de acceso a una ZBE: vigila a quien entra
        if p["t"] == "OTRA_CAMARA" and "zbe" in (p.get("n") or "").lower():
            hacia = hacia_dentro_zbe(w, i, pos)
            if hacia:
                return [hacia]
        # Pistas débiles (lado de la calle, cruce de delante, límite por sentido): solo las que, solas o
        # juntas, han acertado ≥ 90 % con los radares de sentido conocido en esta misma ejecución
        votos = senales(red, wi, i, p)
        for regla in ORDEN_REGLAS:
            if regla in REGLAS_FIABLES:
                v = aplicar_regla(regla, votos)
                if v:
                    return [v]
        if franja_lado(w, ld) in LADO_FIABLE:
            return [1 if ld > 0 else -1]
    return [1, -1]


ORDEN_REGLAS = ("limite", "cruce+lado", "cruce", "lado+limite")
REGLAS_FIABLES: set = set()


def senales(red: Red, wi: int, i: int, p: dict) -> dict:
    """Cada pista que apunta a un sentido (+1/-1 sobre la vía)."""
    w = red.vias[wi]
    pos = (p["la"], p["lo"])
    v = {}
    ld = lado(pos, w.pts[i], w.pts[i + 1])
    if abs(ld) >= LADO_MIN:
        v["lado"] = 1 if ld > 0 else -1
    if p["t"] == "SEMAFORO":
        h = hacia_cruce(red, wi, i, pos)
        if h:
            v["cruce"] = h
    # el límite propio del radar coincide con el de un solo sentido de la vía
    lim = p.get("v") if p.get("vo") != 1 else None
    if lim and w.vmax_ad != w.vmax_at:
        if lim == w.vmax_ad:
            v["limite"] = 1
        elif lim == w.vmax_at:
            v["limite"] = -1
    return v


def aplicar_regla(regla: str, votos: dict):
    partes = regla.split("+")
    vals = {votos.get(k) for k in partes}
    if None in vals or len(vals) != 1:
        return None
    return vals.pop()


# ---------------------------------------------------------------- sentido por el entorno
ZONAS_ZBE: list = []      # polígonos de las ZBE: [(caja, [anillo plano lat,lon,…])]


def dentro(pt, anillo) -> bool:
    la, lo = pt
    n = len(anillo) // 2
    d = False
    j = n - 1
    for k in range(n):
        yi, xi, yj, xj = anillo[2 * k], anillo[2 * k + 1], anillo[2 * j], anillo[2 * j + 1]
        if (yi > la) != (yj > la) and lo < (xj - xi) * (la - yi) / (yj - yi) + xi:
            d = not d
        j = k
    return d


def en_zbe(pt) -> bool:
    for (a, b, c, d), anillos in ZONAS_ZBE:
        if a <= pt[0] <= b and c <= pt[1] <= d and any(dentro(pt, r) for r in anillos):
            return True
    return False


def desplazar(pt, rb, m):
    return (pt[0] + m * math.cos(math.radians(rb)) / 110540.0,
            pt[1] + m * math.sin(math.radians(rb)) / (111320.0 * math.cos(math.radians(pt[0]))))


def hacia_dentro_zbe(w: Via, i: int, pos):
    """+1/-1 si solo uno de los dos sentidos de la vía entra en una ZBE en este punto."""
    if not ZONAS_ZBE:
        return None
    fb = rumbo(w.pts[i], w.pts[i + 1])
    entran = []
    for paso, rb in ((1, fb), (-1, (fb + 180) % 360)):
        if en_zbe(desplazar(pos, rb, 40)) and not en_zbe(desplazar(pos, rb, -40)):
            entran.append(paso)
    return entran[0] if len(entran) == 1 else None


def grado(red: Red, nodo) -> int:
    """Nº de tramos de calle que salen de un nodo (3 o más = cruce)."""
    g = 0
    for wj, k in red.nodos.get(nodo, ()):
        n = len(red.vias[wj].pts)
        g += (k > 0) + (k < n - 1)
    return g


def dist_cruce(red: Red, wi: int, i: int, pos, paso: int, maximo=120.0):
    """Metros por la calle hasta el siguiente cruce en el sentido paso (o None si no hay en `maximo`)."""
    w = red.vias[wi]
    idx = i + 1 if paso == 1 else i
    previo = pos
    total = 0.0
    vistos = set()
    pasos = 0
    while total <= maximo:
        pasos += 1
        if pasos > 400:   # red rara (nodos repetidos, bucles): mejor no decidir
            return None
        nodo = w.pts[idx]
        total += dist(previo, nodo)
        previo = nodo
        if total > maximo:
            return None
        clave = Red.clave(nodo)
        g = grado(red, clave)
        if g >= 3:
            return total
        siguiente = idx + paso
        if 0 <= siguiente < len(w.pts):
            idx = siguiente
            continue
        # fin de la vía en un nodo de paso (grado 2): se sigue por la otra
        otra = [(wj, k) for wj, k in red.nodos.get(clave, ()) if wj != wi]
        if len(otra) != 1 or (otra[0][0], otra[0][1]) in vistos:
            return None
        wi, k = otra[0]
        vistos.add((wi, k))
        w = red.vias[wi]
        paso = 1 if k == 0 else -1
        idx = k + paso
        if not (0 <= idx < len(w.pts)):
            return None
    return None


def hacia_cruce(red: Red, wi: int, i: int, pos):
    """El sentido que va hacia el cruce que la cámara tiene justo delante (y no detrás)."""
    a = dist_cruce(red, wi, i, pos, 1)
    b = dist_cruce(red, wi, i, pos, -1)
    if a is not None and a <= 35 and (b is None or b >= a + 30):
        return 1
    if b is not None and b <= 35 and (a is None or a >= b + 30):
        return -1
    return None


def calibrar_cruce(red: Red, puntos: list[dict]) -> str:
    """
    Prueba cada regla (y combinación de pistas) con los puntos de sentido conocido en calles de doble sentido.
    Se usa con ≥ 20 casos y ≥ 90 % de aciertos.
    """
    REGLAS_FIABLES.clear()
    cuenta = {r: [0, 0] for r in ORDEN_REGLAS}
    for p in puntos:
        if p.get("rb") is None or p["t"] in ("ZONA_MOVIL", "RADAR_TRAMO"):
            continue
        e = encajar(red, p)
        if e is None:
            continue
        wi, i, _ = e
        w = red.vias[wi]
        if w.sentido != 0:
            continue
        real = 1 if dif(p["rb"], rumbo(w.pts[i], w.pts[i + 1])) <= 90 else -1
        votos = senales(red, wi, i, p)
        for r in ORDEN_REGLAS:
            v = aplicar_regla(r, votos)
            if v:
                cuenta[r][0] += v == real
                cuenta[r][1] += 1
    partes = []
    for r in ORDEN_REGLAS:
        ok, n = cuenta[r]
        if n >= 20 and ok / n >= 0.9:
            REGLAS_FIABLES.add(r)
        partes.append(f"{r} {ok}/{n}" + (" ✓" if r in REGLAS_FIABLES else ""))
    return "; ".join(partes)


def mejor_aproximacion(red: Red, candidatas, rb, largo):
    """El camino de llegada más largo entre varias vías candidatas, circulando con rumbo rb."""
    mejor = None
    for (cw, ci, ct) in candidatas:
        w = red.vias[cw]
        fb = rumbo(w.pts[ci], w.pts[ci + 1])
        for paso in (1, -1):
            if not se_puede(w, paso) or dif(rb, fb if paso == 1 else (fb + 180) % 360) > 60:
                continue
            camino = caminar(red, cw, ci, ct, paso, largo, True, solo_enlace=w.tipo.endswith("_link"))
            if len(camino) >= 2 and longitud(camino) > 20 and (mejor is None or longitud(camino) > longitud(mejor)):
                mejor = camino
    return plano(simplificar(list(reversed(mejor)))) if mejor else None


def limite_de_via(red: Red, wi: int, i: int, pasos, p: dict):
    """Límite de la vía en la que está el punto (y en su sentido); si no lo tiene, el de la misma carretera al lado."""
    w = red.vias[wi]
    paso = pasos[0] if len(pasos) == 1 else 0
    lim = w.vmax_ad if paso == 1 else w.vmax_at if paso == -1 else w.vmax
    if lim is None:
        for d, t, wj, j in sorted(red.cercanos((p["la"], p["lo"]))):
            o = red.vias[wj]
            if o.vmax and ((w.ref and o.ref == w.ref) or (w.nombre and o.nombre == w.nombre)) and o.tipo == w.tipo:
                return o.vmax
    return lim


def calibrar_lado(red: Red, puntos: list[dict]) -> str:
    """
    ¿Acierta la regla del lado? Se mira con los puntos que sí traen rumbo (y por tanto sentido conocido),
    por franjas de distancia al eje y por tipo de vía. Solo se usa en las franjas con 25 casos o más y un
    90 % de aciertos; en el resto, ante la duda, se avisa en los dos sentidos (mejor un aviso de más que uno de menos).
    """
    LADO_FIABLE.clear()
    cuenta: dict = {}
    for p in puntos:
        if p.get("rb") is None or p["t"] in ("ZONA_MOVIL", "RADAR_TRAMO"):
            continue
        e = encajar(red, p)
        if e is None:
            continue
        wi, i, _ = e
        w = red.vias[wi]
        if w.sentido != 0:
            continue
        ld = lado((p["la"], p["lo"]), w.pts[i], w.pts[i + 1])
        k = franja_lado(w, ld)
        if k is None:
            continue
        fb = rumbo(w.pts[i], w.pts[i + 1])
        real = 1 if dif(p["rb"], fb) <= 90 else -1
        ok, n = cuenta.get(k, (0, 0))
        cuenta[k] = (ok + (real == (1 if ld > 0 else -1)), n + 1)
    partes = []
    for k in sorted(cuenta, key=lambda k: (k[1], k[0])):
        ok, n = cuenta[k]
        fiable = n >= 25 and ok / n >= 0.9
        if fiable:
            LADO_FIABLE.add(k)
        partes.append(f"{'ciudad' if k[1] else 'carretera'} {k[0][0]}-{k[0][1]} m: {ok}/{n}{' ✓' if fiable else ''}")
    return "; ".join(partes) or "sin casos"


def anadir_caminos(puntos: list[dict], ruta_red: str, zbe: list | None = None, aviso=print) -> dict:
    t0 = time.time()
    ZONAS_ZBE.clear()
    for z in zbe or []:
        anillos = [r for r in z.get("p", []) if len(r) >= 6]
        if anillos:
            las = [v for r in anillos for v in r[0::2]]
            los = [v for r in anillos for v in r[1::2]]
            ZONAS_ZBE.append(((min(las), max(las), min(los), max(los)), anillos))
    objetivos = [p for p in puntos if p["t"] != "ZONA_MOVIL" or "tr" not in p]
    red = cargar_red(ruta_red, objetivos)
    aviso(f"  caminos: red cargada ({len(red.vias)} vías) en {time.time() - t0:.0f}s")
    lado_txt = calibrar_lado(red, objetivos)
    aviso(f"  caminos: regla del lado probada en {time.time() - t0:.0f}s")
    cruce_txt = calibrar_cruce(red, objetivos)
    aviso(f"  caminos: regla del cruce probada en {time.time() - t0:.0f}s")
    stats = {"lado": lado_txt, "cruce": cruce_txt,
             "con_camino": 0, "sin_via": 0, "tramos_con_recorrido": 0, "tramos": 0,
             "caminos_alternativos": 0, "mediana_dos": 0, "en_enlace": 0, "sospechosos": [], "dos_sentidos": 0, "limites_via": 0, "limites_quitados": 0}
    for n_p, p in enumerate(objetivos):
        if n_p % 500 == 0:
            aviso(f"  caminos: {n_p}/{len(objetivos)} en {time.time() - t0:.0f}s ({p['id']})")
        p.pop("ap", None)
        p.pop("rt", None)
        p.pop("s2", None)
        e = encajar(red, p)
        if e is None:
            stats["sin_via"] += 1
            continue
        wi, i, t = e
        w = red.vias[wi]
        largo = 1700.0 if w.tipo in INTERURBANA else 800.0
        if p["t"] == "RADAR_TRAMO" and "la2" in p:
            stats["tramos"] += 1
            fin = (p["la2"], p["lo2"])
            directo = dist((p["la"], p["lo"]), fin)
            mejor = None
            # se prueban la vía encajada y las cercanas (en autovías, la otra calzada o un enlace),
            # en los dos sentidos permitidos: gana el recorrido más corto que llega al final
            candidatas = [(wi, i, t)]
            vistas = {wi}
            for d, t2, wj, j in sorted(red.cercanos((p["la"], p["lo"]))):
                if d <= 40 and wj not in vistas and len(candidatas) < 6:
                    vistas.add(wj)
                    candidatas.append((wj, j, t2))
            for (cw, ci, ct) in candidatas:
                for paso in sentidos(red, cw, ci, None):
                    ruta, ok = caminar(red, cw, ci, ct, paso, directo * 2.2 + 3000, False,
                                       objetivo=fin, radio_objetivo=60.0)
                    if ok and (mejor is None or longitud(ruta) < longitud(mejor[1])):
                        mejor = (paso, ruta, (cw, ci, ct))
            if mejor:
                paso, ruta, cand = mejor
                p["rt"] = plano(simplificar(ruta))
                p["lm"] = round(longitud(ruta))
                stats["tramos_con_recorrido"] += 1
                # sentido de circulación del recorrido, para elegir el sentido de cada vía candidata
                k = 1
                while k < len(ruta) - 1 and dist(ruta[0], ruta[k]) < 40:
                    k += 1
                rb_ruta = rumbo(ruta[0], ruta[k])
                if (p.get("vo") == 1 or "v" not in p) and red.con_limites:
                    cw, ci, _ = cand
                    fb = rumbo(red.vias[cw].pts[ci], red.vias[cw].pts[ci + 1])
                    lim = limite_de_via(red, cw, ci, [1 if dif(rb_ruta, fb) <= 90 else -1], p)
                    if lim:
                        p["v"], p["vo"] = lim, 1
                        stats["limites_via"] += 1
                camino = mejor_aproximacion(red, [(wi, i, t), cand], rb_ruta, largo)
                if camino:
                    p["ap"] = [camino]
                    stats["con_camino"] += 1
                continue
            else:
                # sin recorrido: al menos el sentido que va hacia el final
                fb = rumbo(w.pts[i], w.pts[i + 1])
                pasos = [1 if dif(rumbo((p["la"], p["lo"]), fin), fb) <= 90 else -1]
                pasos = [s for s in pasos if se_puede(w, s)] or sentidos(red, wi, i, None)
        else:
            pasos = sentidos(red, wi, i, p.get("rb"), p)
            if len(pasos) == 2:
                stats["dos_sentidos"] += 1
                if p["t"] != "ZONA_MOVIL":
                    p["s2"] = 1   # se avisa en los dos sentidos porque no se sabe cuál vigila
        # el límite deducido (no el del propio radar) se toma de la vía en la que está, no de la más cercana
        if p["t"] == "RADAR_FIJO" and (p.get("vo") == 1 or "v" not in p) and red.con_limites:
            lim = limite_de_via(red, wi, i, pasos, p)
            if lim:
                p["v"], p["vo"] = lim, 1
                stats["limites_via"] += 1
            elif p.get("vo") == 1:
                p.pop("v", None); p.pop("vo", None)
                stats["limites_quitados"] += 1
        aps = []
        enlace = w.tipo.endswith("_link")
        for paso in pasos:
            camino = caminar(red, wi, i, t, paso, largo, True, solo_enlace=enlace)
            if len(camino) >= 2 and longitud(camino) > (20 if enlace else 60):
                aps.append(plano(simplificar(list(reversed(camino)))))
        # En la mediana entre dos calzadas de sentido único y sin saber a cuál mira: las dos (y el usuario
        # puede silenciar desde la app el sentido que no es). Elegir una al azar dejaría sin aviso la otra la mitad de las veces.
        if p.get("rb") is None and not p.get("_dir") and w.sentido != 0 and not enlace and p["t"] != "ZONA_MOVIL" and aps:
            pos = (p["la"], p["lo"])
            d_w = proyectar(pos, w.pts[i], w.pts[i + 1])[0]
            if lado(pos, w.pts[i], w.pts[i + 1]) * w.sentido < -2:
                trafico_w = rumbo(w.pts[i], w.pts[i + 1]) if w.sentido == 1 else rumbo(w.pts[i + 1], w.pts[i])
                for d_o, t_o, wj, j in sorted(red.cercanos(pos)):
                    o = red.vias[wj]
                    if wj == wi or o.sentido == 0 or o.tipo.endswith("_link") or d_o - d_w > 6:
                        continue
                    trafico_o = rumbo(o.pts[j], o.pts[j + 1]) if o.sentido == 1 else rumbo(o.pts[j + 1], o.pts[j])
                    if dif(trafico_w, trafico_o) > 120 and lado(pos, o.pts[j], o.pts[j + 1]) * o.sentido < -2:
                        camino = caminar(red, wj, j, t_o, o.sentido, largo, True)
                        if len(camino) >= 2 and longitud(camino) > 60:
                            aps.append(plano(simplificar(list(reversed(camino)))))
                            stats["mediana_dos"] += 1
                            p["s2"] = 1
                        break
        # para revisar a mano: radares de autovía con límite de ciudad (como el "40" de la CV-35)
        if p["t"] == "RADAR_FIJO" and w.tipo == "motorway" and p.get("vo") == 1 and p.get("v") and p["v"] < 60:
            stats["sospechosos"].append(f'{p["id"]} {p.get("c") or ""} {p.get("mu") or ""} límite {p["v"]}')
        if w.tipo.endswith("_link"):
            stats["en_enlace"] += 1
        if not aps:
            # sin camino por la vía elegida (calle cortada, fin de vía…): la más cercana, en sus sentidos
            for d0, tj, wj, j in sorted(red.cercanos((p["la"], p["lo"])))[:4]:
                o = red.vias[wj]
                for paso in ([o.sentido] if o.sentido else sentidos(red, wj, j, p.get("rb"), p)):
                    camino = caminar(red, wj, j, tj, paso, largo, True, solo_enlace=o.tipo.endswith("_link"))
                    if len(camino) >= 2 and longitud(camino) > 60:
                        aps.append(plano(simplificar(list(reversed(camino)))))
                if aps:
                    stats["caminos_alternativos"] += 1
                    break
        if aps:
            p["ap"] = aps
            stats["con_camino"] += 1
    for p in puntos:
        p.pop("_dir", None); p.pop("_dirg", None)
    stats["segundos"] = round(time.time() - t0)
    return stats


if __name__ == "__main__":
    # uso: caminos.py red.geojsonseq datos/radares.json
    datos = json.load(open(sys.argv[2], encoding="utf-8"))
    print(anadir_caminos(datos["puntos"], sys.argv[1]))
