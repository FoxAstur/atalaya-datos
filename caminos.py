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


LADO_MIN = 4.0   # m: a partir de aquí se sabe a qué lado de una calle de doble sentido está la cámara


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
        if abs(ld) >= LADO_MIN:
            return [1 if ld > 0 else -1]
    return [1, -1]


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


def anadir_caminos(puntos: list[dict], ruta_red: str) -> dict:
    t0 = time.time()
    objetivos = [p for p in puntos if p["t"] != "ZONA_MOVIL" or "tr" not in p]
    red = cargar_red(ruta_red, objetivos)
    stats = {"con_camino": 0, "sin_via": 0, "tramos_con_recorrido": 0, "tramos": 0,
             "lado_ok": 0, "lado_mal": 0, "caminos_alternativos": 0, "en_enlace": 0, "sospechosos": [], "dos_sentidos": 0, "limites_via": 0, "limites_quitados": 0}
    for p in objetivos:
        p.pop("ap", None)
        p.pop("rt", None)
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
            # comprobación de la regla del lado con los puntos de rumbo conocido (va al informe)
            if p.get("rb") is not None and w.sentido == 0 and p["t"] != "ZONA_MOVIL":
                ld = lado((p["la"], p["lo"]), w.pts[i], w.pts[i + 1])
                if abs(ld) >= LADO_MIN:
                    por_lado = 1 if ld > 0 else -1
                    stats["lado_ok" if [por_lado] == pasos else "lado_mal"] += 1
            if len(pasos) == 2:
                stats["dos_sentidos"] += 1
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
        # para revisar a mano: radares de autovía con límite de ciudad (como el "40" de la CV-35)
        if p["t"] == "RADAR_FIJO" and w.tipo in ("motorway", "trunk") and p.get("v") and p["v"] < 60:
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
