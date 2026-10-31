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
    __slots__ = ("pts", "clase", "ref", "nombre", "sentido", "tipo", "vmax", "vmax_ad", "vmax_at", "tunel")

    def __init__(self, pts, tags):
        self.pts = pts
        self.tipo = tags.get("highway", "")
        self.clase = CLASE.get(self.tipo, 6)
        self.ref = norm_ref(tags.get("ref"))
        self.nombre = (tags.get("name") or "").strip().lower()
        self.vmax = velocidad(tags.get("maxspeed"))
        self.vmax_ad = velocidad(tags.get("maxspeed:forward")) or self.vmax
        self.vmax_at = velocidad(tags.get("maxspeed:backward")) or self.vmax
        self.tunel = str(tags.get("tunnel", "")).lower() in ("yes", "1", "true")
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
        # el camino vuelve sobre sí mismo (vuelta a una manzana, rotonda, cambio de sentido): se corta ahí.
        # Con un lazo, la posición casa con dos tramos del camino y la distancia que se dice sale mal.
        if hacia_atras and len(pts) > 3 and largo - resto > 120:
            hecho, k = 0.0, len(pts) - 1
            while k > 0 and hecho < 120:
                hecho += dist(pts[k], pts[k - 1])
                k -= 1
            if any(dist(nodo, q) < 20 for q in pts[:k]):
                break
        # ...o vuelve a pasar por el mismo sitio (dos vueltas a una rotonda)
        if hacia_atras and len(pts) > 2 and any(dist(nodo, q) < 3 for q in pts[:-1]):
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


RAMAS_CIUDAD_M = 250.0       # hasta dónde (hacia atrás) se miran los cruces por los que también se llega
RAMAS_CARRETERA_M = 400.0
MAX_RAMAS = 6


def ramas(red: Red, camino: list, largo: float, interurbana: bool, solo_enlace: bool = False) -> list:
    """
    Otros caminos por los que se llega al punto: las calles que desembocan en el camino principal en los
    últimos 250 m (400 m en carretera). caminar() sigue una sola carretera hacia atrás, y una cabina justo
    después de un cruce solo avisaba a quien llegaba por la calle elegida (Germans Machado: se avisaba
    viniendo por la CV-30 y no viniendo de Burjassot). Cada rama es el trozo de la calle que desemboca
    más el camino principal desde el cruce hasta el punto. Devuelve caminos en el orden del tráfico.
    """
    if solo_enlace or len(camino) < 2:
        return []
    tope = RAMAS_CARRETERA_M if interurbana else RAMAS_CIUDAD_M
    salida, vistas = [], set()
    acum = 0.0
    for j in range(1, len(camino)):
        acum += dist(camino[j - 1], camino[j])
        if acum > tope or len(salida) >= MAX_RAMAS:
            break
        nodo = camino[j]
        clave = Red.clave(nodo)
        if clave not in red.nodos:
            continue   # punto interpolado, no un nodo de la red
        # rumbo con el que el tráfico sale del cruce hacia el punto
        sale = rumbo(nodo, camino[j - 1])
        for wk, k in red.nodos[clave]:
            w = red.vias[wk]
            for paso in (1, -1):
                otro = k - paso
                if not (0 <= otro < len(w.pts)) or not se_puede(w, paso):
                    continue
                desde = w.pts[otro]
                # es el propio camino (por donde ya se viene) o vuelve por donde se va
                if j + 1 < len(camino) and dist(desde, camino[j + 1]) < 1.0:
                    continue
                if dist(desde, camino[j - 1]) < 1.0:
                    continue
                llega = rumbo(desde, nodo)
                if dif(llega, sale) > 150:
                    continue   # cambio de sentido
                # Solo si quien viene por esa calle sigue, lo más recto que puede, hacia el punto (incorporación,
                # rampa, rotonda, calle que acaba en "T"). Una calle que cruza recta no: avisaría a todo el que cruza.
                giros = []
                for wm, m in red.nodos[clave]:
                    o = red.vias[wm]
                    for p2 in (1, -1):
                        sig = m + p2
                        if 0 <= sig < len(o.pts) and se_puede(o, p2) and dist(o.pts[sig], desde) >= 1.0:
                            giros.append(dif(llega, rumbo(nodo, o.pts[sig])))
                if giros and dif(llega, sale) > min(giros) + 15:
                    continue
                if (wk, otro) in vistas:
                    continue
                vistas.add((wk, otro))
                i0, t0 = (k - 1, 1.0) if paso == 1 else (k, 0.0)
                atras = caminar(red, wk, i0, t0, paso, max(60.0, largo - acum), True)
                if len(atras) < 2 or longitud(atras) < 40:
                    continue
                salida.append(list(reversed(atras)) + list(reversed(camino[:j])))
                if len(salida) >= MAX_RAMAS:
                    break
            if len(salida) >= MAX_RAMAS:
                break
    return salida


def llegada(a) -> float:
    """Rumbo con el que un camino plano (lat,lon,…) llega a su punto (últimos ~40 m)."""
    n = len(a) // 2
    fin = (a[-2], a[-1])
    k = n - 2
    while k > 0 and dist((a[2 * k], a[2 * k + 1]), fin) < 40:
        k -= 1
    return rumbo((a[2 * k], a[2 * k + 1]), fin)


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


def grupo_fuente(p: dict) -> str:
    """
    Quién pone la posición del punto. La regla del lado solo dice algo si la posición es la de la cabina:
    en OSM la pone a mano quien la ha visto; la DGT y otras fuentes dan a menudo un punto de la carretera
    (el eje, el PK). Por eso se prueba por separado para cada una.
    """
    pre = p["id"].split(":")[0]
    return {"osm": "osm", "sct": "sct", "dgt": "dgt", "dgtpdf": "dgtpdf", "dgteq": "dgtpdf"}.get(pre, "otros")


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
        # "hacia Vitoria": el sentido en el que, siguiendo la carretera 3 km, te acercas a esa ciudad
        if p.get("_hacia"):
            h = hacia_ciudad(red, wi, i, tuple(p["_hacia"]))
            if h:
                return [h]
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
        f = franja_lado(w, ld)
        if f is not None and ((grupo_fuente(p),) + f in LADO_FIABLE or (grupo_fuente(p), "todas", f[1]) in LADO_FIABLE):
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


def hacia_ciudad(red: Red, wi: int, i: int, ciudad):
    finales = {}
    for paso in (1, -1):
        if se_puede(red.vias[wi], paso):
            camino = caminar(red, wi, i, 0.5, paso, 3000.0, False)
            if len(camino) >= 2 and longitud(camino) > 1000:
                finales[paso] = dist(camino[-1], ciudad)
    if len(finales) == 2:
        a, b = finales[1], finales[-1]
        if abs(a - b) > 800:
            return 1 if a < b else -1
    return None


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
    por fuente (quién pone la posición), por franjas de distancia al eje y por tipo de vía. Solo se usa donde
    hay 20 casos o más y un 90 % de aciertos; en el resto, ante la duda, se avisa en los dos sentidos (mejor
    un aviso de más que uno de menos). Antes se probaba todo junto y los puntos de la DGT (que suelen estar en
    el eje de la carretera) hundían la regla también para OSM.
    """
    LADO_FIABLE.clear()
    cuenta: dict = {}
    for p in puntos:
        if p.get("rb") is None or p["t"] in ("ZONA_MOVIL", "RADAR_TRAMO") or p.get("_rb_por_lado"):
            continue
        e = encajar(red, p)
        if e is None:
            continue
        wi, i, _ = e
        w = red.vias[wi]
        if w.sentido != 0:
            continue
        ld = lado((p["la"], p["lo"]), w.pts[i], w.pts[i + 1])
        f = franja_lado(w, ld)
        if f is None:
            continue
        fb = rumbo(w.pts[i], w.pts[i + 1])
        real = 1 if dif(p["rb"], fb) <= 90 else -1
        acierto = real == (1 if ld > 0 else -1)
        g = grupo_fuente(p)
        for k in ((g,) + f, (g, "todas", f[1])):
            ok, n = cuenta.get(k, (0, 0))
            cuenta[k] = (ok + acierto, n + 1)
    partes = []
    for k in sorted(cuenta, key=lambda k: (k[0], str(k[1]), k[2])):
        ok, n = cuenta[k]
        fiable = n >= 20 and ok / n >= 0.9
        if fiable:
            LADO_FIABLE.add(k)
        franja = "todas" if k[1] == "todas" else f"{k[1][0]}-{k[1][1]} m"
        partes.append(f"{k[0]} {'ciudad' if k[2] else 'carretera'} {franja}: {ok}/{n}{' ✓' if fiable else ''}")
    return "; ".join(partes) or "sin casos"


def via_paralela(red: Red, ap: list) -> float | None:
    """
    Metros a la vía más cercana que va pegada y en el mismo sentido que los últimos 400 m del camino
    (vía de servicio, calzada lateral). La app pide entonces ir más pegado al camino para avisar.
    """
    pts = [(ap[k], ap[k + 1]) for k in range(0, len(ap) - 1, 2)]
    if len(pts) < 2:
        return None
    # últimos 400 m, muestreados cada ~25 m
    muestras = []
    acum = 0.0
    for k in range(len(pts) - 1, 0, -1):
        a, b = pts[k - 1], pts[k]
        seg = dist(a, b)
        n = max(1, int(seg // 25))
        for j in range(n):
            muestras.append((interpolar(b, a, j / n), rumbo(a, b)))
        acum += seg
        if acum >= 400:
            break
    mejor = None
    for q, rb in muestras:
        cand = list(red.cercanos(q, 45.0))
        if not cand:
            continue
        # la propia carretera es la más cercana (el camino está simplificado: puede quedar a unos metros)
        d0, _, propia, _ = min(cand)
        wp = red.vias[propia]
        for d, t, wj, j in cand:
            if wj == propia or d < d0 + 5.0 or d - d0 > 35.0:
                continue
            o = red.vias[wj]
            # otro trozo o carril de la misma carretera no cuenta como vía paralela
            if (wp.nombre and o.nombre == wp.nombre) or (wp.ref and o.ref == wp.ref):
                continue
            d = d - d0
            o = red.vias[wj]
            fb = rumbo(o.pts[j], o.pts[j + 1])
            sentidos_o = [fb] if o.sentido == 1 else [(fb + 180) % 360] if o.sentido == -1 else [fb, (fb + 180) % 360]
            if any(dif(rb, x) <= 25 for x in sentidos_o) and (mejor is None or d < mejor):
                mejor = d
    return round(mejor, 1) if mejor is not None else None


def rumbos_llegada(p: dict) -> list:
    """Rumbo con el que se llega a un punto por cada uno de sus caminos (último tramo)."""
    out = []
    for ap in p.get("ap") or []:
        if len(ap) >= 4:
            out.append(rumbo((ap[-4], ap[-3]), (ap[-2], ap[-1])))
    return out


def en_camino_m(q, ap, max_m=600.0, margen=10.0, rumbos_q=None):
    """
    Metros por carretera desde q hasta el final del camino ap (el radar), si q está en él y (con rumbos_q)
    circulando en el mismo sentido que el camino en ese punto; si no, None. El sentido evita confundir la
    calzada de enfrente, que en una avenida o autovía va a 10-25 m.
    """
    pts = [(ap[k], ap[k + 1]) for k in range(0, len(ap) - 1, 2)]
    acum = 0.0
    for k in range(len(pts) - 1, 0, -1):
        a, b = pts[k - 1], pts[k]
        d, t = proyectar(q, a, b)
        if d <= margen and (not rumbos_q or any(dif(rumbo(a, b), r) <= 45 for r in rumbos_q)):
            m = acum + (1 - t) * dist(a, b)
            return m if m <= max_m else None
        acum += dist(a, b)
        if acum > max_m:
            break
    return None


def copias_osm(puntos: list[dict], max_m=450.0):
    """
    Pares (copia de OSM, radar oficial): mismo tipo, misma calle y sentido, a menos de max_m por carretera.
    La DGT, el SCT, Euskadi o un ayuntamiento sitúan su radar a veces a 100-400 m de donde lo pone OSM; al
    juntar fuentes con 120 m de margen salían dos radares seguidos donde hay uno.
    """
    oficiales = [p for p in puntos if p["f"] not in ("OSM", "PROPIO") and p.get("ap") and p["t"] != "ZONA_MOVIL"]
    rej: dict = {}
    for f in oficiales:
        rej.setdefault((int(f["la"] // 0.01), int(f["lo"] // 0.01)), []).append(f)
    pares = []
    for o in puntos:
        if o["f"] != "OSM" or not o.get("ap") or o["t"] in ("ZONA_MOVIL", "RADAR_TRAMO"):
            continue
        cy, cx = int(o["la"] // 0.01), int(o["lo"] // 0.01)
        mejor = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for f in rej.get((cy + dy, cx + dx), ()):
                    if f["t"] != o["t"] or dist((o["la"], o["lo"]), (f["la"], f["lo"])) > max_m + 50:
                        continue
                    ro, rf = rumbos_llegada(o), rumbos_llegada(f)
                    ms = [m for m in ([en_camino_m((o["la"], o["lo"]), ap, max_m, rumbos_q=ro) for ap in f["ap"]] +
                                      [en_camino_m((f["la"], f["lo"]), ap, max_m, rumbos_q=rf) for ap in o["ap"]]) if m is not None]
                    if ms and (mejor is None or min(ms) < mejor[0]):
                        mejor = (min(ms), f)
        if mejor:
            pares.append((o, mejor[1], mejor[0]))
    return pares


def seguidos(puntos: list[dict], max_m=300.0) -> list:
    """Pares de radares fijos (o cámaras) del mismo tipo, en la misma calle y sentido, a menos de max_m."""
    ps = [p for p in puntos if p.get("ap") and p["t"] in ("RADAR_FIJO", "OTRA_CAMARA")]
    rej: dict = {}
    for p in ps:
        rej.setdefault((int(p["la"] // 0.01), int(p["lo"] // 0.01)), []).append(p)
    out = []
    for p in ps:
        cy, cx = int(p["la"] // 0.01), int(p["lo"] // 0.01)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for q in rej.get((cy + dy, cx + dx), ()):
                    if q is p or q["t"] != p["t"] or dist((p["la"], p["lo"]), (q["la"], q["lo"])) > max_m + 30:
                        continue
                    rq = rumbos_llegada(q)
                    ms = [m for m in (en_camino_m((q["la"], q["lo"]), ap, max_m, rumbos_q=rq) for ap in p["ap"]) if m]
                    if ms and min(ms) > 5:
                        out.append((round(min(ms)), q, p))
    return out


def quitar_viejos_repetidos(puntos: list[dict]) -> list[dict]:
    """
    Un radar de OSM sin sentido conocido que está en la misma calle y sentido que otro más fiable (oficial,
    o de OSM con sentido) y muy cerca, sobra: es una cabina antigua, un duplicado mal situado o el punto
    "desde" de una relación sin aparato. Cerca es 300 m; 450 m si no tiene ningún dato propio; 600 m si
    además es de 2015 o antes. Así no se cantan "dos radares seguidos" donde hay uno.
    """
    candidatos = [p for p in puntos if p["f"] == "OSM" and p["t"] == "RADAR_FIJO" and p.get("ap")
                  and p.get("rb") is None]
    if not candidatos:
        return []
    ids_cand = {p["id"] for p in candidatos}
    fiables = [p for p in puntos if p["t"] == "RADAR_FIJO" and p.get("ap") and p["id"] not in ids_cand
               and (p["f"] != "OSM" or p.get("rb") is not None)]
    rej: dict = {}
    for o in fiables:
        rej.setdefault((int(o["la"] // 0.01), int(o["lo"] // 0.01)), []).append(o)
    fuera = []
    for v in candidatos:
        lim = {2: 600.0, 1: 450.0}.get(v.get("_viejo"), 300.0)
        rv = rumbos_llegada(v)
        cy, cx = int(v["la"] // 0.01), int(v["lo"] // 0.01)
        hallado = False
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for o in rej.get((cy + dy, cx + dx), ()):
                    if hallado or dist((v["la"], v["lo"]), (o["la"], o["lo"])) > lim + 50:
                        continue
                    ro = rumbos_llegada(o)
                    if any(en_camino_m((o["la"], o["lo"]), ap, lim, rumbos_q=ro) is not None for ap in v["ap"]) or \
                            any(en_camino_m((v["la"], v["lo"]), ap, lim, rumbos_q=rv) is not None for ap in o["ap"]):
                        hallado = True
        if hallado:
            fuera.append(v)
    return fuera


def rumbo_por_cardinal(red: Red, puntos: list[dict]) -> int:
    """
    Fuentes que dan el sentido como "Norte-Sul", "Este-Oeste" (ANSR, Portugal): el rumbo exacto es el de la
    carretera en ese punto, en el sentido de circulación que más se parece (a menos de 75°). Si la carretera
    va de través (un "Norte-Sul" en una vía este-oeste) no se adivina: se queda en los dos sentidos.
    """
    n = 0
    for p in puntos:
        card = p.pop("_card", None)
        if card is None or (p.get("rb") is not None and dif(p["rb"], card) <= 100):
            continue
        pos = (p["la"], p["lo"])
        ref = norm_ref(p.get("c"))
        mejor = None
        for d, t, wi, i in red.cercanos(pos):
            w = red.vias[wi]
            if w.tipo.endswith("_link"):
                continue
            fb = rumbo(w.pts[i], w.pts[i + 1])
            for paso in (1, -1):
                if not se_puede(w, paso):
                    continue
                r = fb if paso == 1 else (fb + 180) % 360
                dd = dif(r, card)
                if dd > 75:
                    continue
                s = d + dd / 3 + ((-15 if w.ref == ref else 25) if ref and w.ref else 0)
                if mejor is None or s < mejor[0]:
                    mejor = (s, r)
        if mejor:
            p["rb"] = round(mejor[1], 1)
            n += 1
    return n


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
    n_card = rumbo_por_cardinal(red, objetivos)
    lado_txt = calibrar_lado(red, objetivos)
    aviso(f"  caminos: regla del lado probada en {time.time() - t0:.0f}s")
    cruce_txt = calibrar_cruce(red, objetivos)
    aviso(f"  caminos: regla del cruce probada en {time.time() - t0:.0f}s")
    stats = {"lado": lado_txt, "cruce": cruce_txt, "rumbo_por_cardinal": n_card,
             "con_camino": 0, "sin_via": 0, "tramos_con_recorrido": 0, "tramos": 0,
             "caminos_alternativos": 0, "mediana_dos": 0, "con_paralela": 0, "en_enlace": 0, "sospechosos": [], "dos_sentidos": 0, "limites_via": 0, "limites_quitados": 0}
    for n_p, p in enumerate(objetivos):
        if n_p % 500 == 0:
            aviso(f"  caminos: {n_p}/{len(objetivos)} en {time.time() - t0:.0f}s ({p['id']})")
        p.pop("ap", None)
        p.pop("rt", None)
        p.pop("s2", None)
        p.pop("pl", None)
        e = encajar(red, p)
        if e is None:
            stats["sin_via"] += 1
            continue
        wi, i, t = e
        w = red.vias[wi]
        if w.tunel and p["t"] != "ZONA_MOVIL":
            p["tu"] = 1   # en un túnel: se dice ("Radar en túnel") y el GPS ahí dentro va peor
            stats["en_tunel"] = stats.get("en_tunel", 0) + 1
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
                # se avisa en los dos sentidos porque no se sabe cuál vigila; si la fuente dice que vigila los
                # dos ("Ambos"), no hay duda y no se dice "puede ser del otro sentido"
                if p["t"] != "ZONA_MOVIL" and p.get("s") != "Ambos":
                    p["s2"] = 1
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
                if p["t"] != "ZONA_MOVIL":
                    for rama in ramas(red, camino, largo, w.tipo in INTERURBANA, enlace):
                        aps.append(plano(simplificar(rama)))
                        stats["ramas"] = stats.get("ramas", 0) + 1
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
        # Con sentido conocido, el camino tiene que llegar en ese sentido. Si llega al revés, el punto se ha
        # encajado en la calzada de enfrente (autovía, avenida con mediana): se busca la suya a menos de 60 m.
        rb = p.get("rb")
        if rb is not None and aps and p["t"] != "ZONA_MOVIL" and p["t"] != "RADAR_TRAMO":
            buenos = [a for a in aps if dif(llegada(a), rb) <= 90]
            if not buenos:
                for d0, tj, wj, j in sorted(red.cercanos((p["la"], p["lo"]), 60.0)):
                    o = red.vias[wj]
                    fb = rumbo(o.pts[j], o.pts[j + 1])
                    paso = 1 if dif(rb, fb) <= 60 else -1 if dif(rb, (fb + 180) % 360) <= 60 else 0
                    if paso == 0 or not se_puede(o, paso):
                        continue
                    camino = caminar(red, wj, j, tj, paso, largo, True, solo_enlace=o.tipo.endswith("_link"))
                    if len(camino) >= 2 and longitud(camino) > 60:
                        buenos = [plano(simplificar(list(reversed(camino))))]
                        break
                stats["calzada_corregida" if buenos else "sin_calzada_de_su_sentido"] = \
                    stats.get("calzada_corregida" if buenos else "sin_calzada_de_su_sentido", 0) + 1
            if buenos:
                aps = buenos
            else:
                p["s2"] = 1   # su vía y su sentido no casan: se avisa por donde está, diciendo que puede no ser
        if aps:
            p["ap"] = aps
            stats["con_camino"] += 1
            pl = min((x for x in (via_paralela(red, a) for a in aps) if x is not None), default=None)
            # por debajo de 8 m suelen ser carriles de giro o el trazado simplificado de la misma calle
            if pl is not None and pl >= 8:
                p["pl"] = pl
                stats["con_paralela"] += 1
    for p in puntos:
        p.pop("_dir", None); p.pop("_dirg", None); p.pop("_card", None)
    stats["segundos"] = round(time.time() - t0)
    return stats


if __name__ == "__main__":
    # uso: caminos.py red.geojsonseq datos/radares.json
    datos = json.load(open(sys.argv[2], encoding="utf-8"))
    print(anadir_caminos(datos["puntos"], sys.argv[1]))
