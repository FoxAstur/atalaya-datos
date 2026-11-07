#!/usr/bin/env python3
"""
Auditoría de los datos publicados (datos/radares.json), independiente de cómo se calculó cada punto.

Comprueba cada radar o cámara contra:
  - la red viaria de OSM (red/vias.geojsonseq): ¿está sobre una carretera?, ¿sobre la suya (ref)?, ¿su rumbo va a
    favor de alguna calzada?, ¿el camino de aproximación acaba en él y en su rumbo?
  - los hitos kilométricos de CartoCiudad: ¿cae cerca de su PK?, ¿"Creciente" mira de verdad hacia el km siguiente?
  - los demás puntos: ¿duplicados?
  - las cámaras de OSM (red/camaras.opl): ¿hay radares en OSM sin ningún punto nuestro cerca?

Salida: auditoria/INFORME.md y auditoria/hallazgos.json (lista de hallazgos con id, tipo, detalle y coordenadas).
"""
import json
import math
import os
import re
import sys
import time
from collections import Counter, defaultdict

import caminos

# referencias completas ("A-7;E-15" → "A7;E15") para comparar con cualquiera de ellas
caminos.norm_ref = lambda r: ";".join(x.strip().upper().replace(" ", "").replace("-", "") for x in (r or "").split(";") if x.strip())

import recolector  # noqa: E402

recolector.PRESUPUESTO_GEO_S = 75 * 60

RED = "red/vias.geojsonseq"
OPL = "red/camaras.opl"
FIJOS = {"RADAR_FIJO", "RADAR_TRAMO", "OTRA_CAMARA", "SEMAFORO", "STOP_CEDA"}
INICIO = time.time()

dist = caminos.dist
rumbo = caminos.rumbo
dif = caminos.dif


def log(m):
    print(f"{time.time() - INICIO:7.0f}s  {m}", flush=True)


def refs(r: str) -> set:
    return {x for x in (r or "").split(";") if x}


def ref_carretera(c: str | None) -> str | None:
    """Solo referencias de carretera (A-7, CV-35, N-340A, M-30...), no nombres de calle."""
    if not c:
        return None
    c = c.strip().upper()
    if not re.fullmatch(r"[A-Z]{1,5}-?\d{1,4}[A-Z]?(-\d+)?", c):
        return None
    return c.replace("-", "").replace(" ", "")


def cerca(red, p, radio):
    """[(d, via, idx, t)] ordenado por distancia."""
    return sorted(((d, wi, i, t) for d, t, wi, i in red.cercanos(p, radio)), key=lambda x: x[0])


def rumbo_seg(red, wi, i):
    w = red.vias[wi]
    return rumbo(w.pts[i], w.pts[i + 1])


def a_favor(red, wi, i, rb, tol=50.0) -> bool:
    """¿Se puede circular por ese tramo de vía con rumbo rb?"""
    w = red.vias[wi]
    r = rumbo_seg(red, wi, i)
    if w.sentido == 1:
        return dif(rb, r) <= tol
    if w.sentido == -1:
        return dif(rb, (r + 180) % 360) <= tol
    return dif(rb, r) <= tol or dif(rb, (r + 180) % 360) <= tol


def hallazgo(lista, p, tipo, detalle, grave=2, **extra):
    h = {"id": p["id"], "tipo": tipo, "grave": grave, "t": p["t"], "src": p.get("src"), "c": p.get("c"),
         "pk": p.get("pk"), "s": p.get("s"), "rb": p.get("rb"), "la": p["la"], "lo": p["lo"],
         "px": p.get("px"), "detalle": detalle}
    h.update(extra)
    lista.append(h)


def main():
    datos = json.load(open("datos/radares.json", encoding="utf-8"))
    puntos = datos["puntos"]
    fijos = [p for p in puntos if p["t"] in FIJOS]
    log(f"{len(puntos)} puntos, {len(fijos)} radares y cámaras")
    verif = {v["id"] for v in json.load(open("verificados.json", encoding="utf-8"))["puntos"]}

    extremos = [{"la": p["la"], "lo": p["lo"]} for p in fijos] + \
        [{"la": p["la2"], "lo": p["lo2"]} for p in fijos if p.get("la2") is not None]
    red = caminos.cargar_red(RED, extremos)
    log(f"red: {len(red.vias)} vías")

    H: list[dict] = []
    stats = Counter()

    # ------------------------------------------------------------------ 1-4, 8: contra la red
    for p in fijos:
        pos = (p["la"], p["lo"])
        cs = cerca(red, pos, 600)
        if not cs:
            hallazgo(H, p, "fuera_de_via", "ninguna carretera a menos de 600 m", 1)
            continue
        d0 = cs[0][0]
        stats["con_via"] += 1
        rc = ref_carretera(p.get("c"))
        propios = [x for x in cs if rc and rc in refs(red.vias[x[1]].ref)]
        if d0 > 40 and not (propios and propios[0][0] <= 40):
            hallazgo(H, p, "fuera_de_via", f"a {d0:.0f} m de la carretera más cercana", 2 if d0 < 100 else 1, d=round(d0))
        if rc:
            stats["con_ref"] += 1
            if not propios:
                # ¿existe esa carretera por aquí? (si OSM no tiene la ref, no se puede decir nada)
                hallazgo(H, p, "sin_su_carretera", f"no hay ninguna vía {p['c']} a menos de 600 m (la más cercana: "
                         f"{red.vias[cs[0][1]].ref or red.vias[cs[0][1]].nombre or red.vias[cs[0][1]].tipo} a {d0:.0f} m)", 3)
            elif propios[0][0] > max(60.0, d0 + 40):
                otra = red.vias[cs[0][1]]
                hallazgo(H, p, "otra_via", f"su {p['c']} está a {propios[0][0]:.0f} m; está sobre "
                         f"{otra.ref or otra.nombre or otra.tipo} ({otra.tipo}) a {d0:.0f} m", 1 if propios[0][0] > 120 else 2,
                         d_suya=round(propios[0][0]))
        rb = p.get("rb")
        if rb is not None:
            stats["con_rumbo"] += 1
            # calzadas a favor del rumbo a menos de 60 m (la cabina puede estar en la mediana o en la otra calzada)
            cand = propios if propios else cs
            alineadas = [x for x in cand if x[0] <= 60 and
                         min(dif(rb, rumbo_seg(red, x[1], x[2])), dif(rb, (rumbo_seg(red, x[1], x[2]) + 180) % 360)) <= 50]
            favor = [x for x in alineadas if a_favor(red, x[1], x[2], rb)]
            if alineadas and not favor:
                w = red.vias[alineadas[0][1]]
                hallazgo(H, p, "contra_direccion", f"rumbo {rb:.0f}° contra el único sentido de {w.ref or w.nombre or w.tipo} "
                         f"(a {alineadas[0][0]:.0f} m) y ninguna calzada a favor a menos de 60 m", 1)
            elif not alineadas and cand[0][0] <= 30:
                # ninguna vía en ese eje: rumbo cruzado (o el punto está en un cruce)
                ejes = sorted({round(rumbo_seg(red, x[1], x[2]) % 180) for x in cand if x[0] <= 30})
                hallazgo(H, p, "rumbo_cruzado", f"rumbo {rb:.0f}° y las vías a menos de 30 m van a {ejes}° (o su opuesto)", 2)
            # camino de aproximación
            ap = p.get("ap")
            if ap:
                try:
                    caps = json.loads(ap) if isinstance(ap, str) else ap
                except ValueError:
                    caps = []
                malos = 0
                for a in caps:
                    if len(a) < 4:
                        continue
                    fin = (a[-2], a[-1])
                    prev = (a[-4], a[-3])
                    dfin = dist(fin, pos)
                    rfin = rumbo(prev, fin) if dist(prev, fin) > 3 else None
                    if dfin > 60 or (rfin is not None and dif(rfin, rb) > 75):
                        malos += 1
                if caps and malos == len([a for a in caps if len(a) >= 4]) and malos:
                    hallazgo(H, p, "camino_incoherente", f"{malos} camino(s) de aproximación que no acaban en el punto o "
                             f"llegan con otro rumbo", 2)
        # tramos
        if p["t"] == "RADAR_TRAMO" and p.get("la2") is not None:
            stats["tramos"] += 1
            recta = dist(pos, (p["la2"], p["lo2"]))
            lm = p.get("lm")
            if recta < 250:
                hallazgo(H, p, "tramo_raro", f"entrada y salida a {recta:.0f} m", 1)
            elif lm and (lm < recta * 0.97 or lm > recta * 2.2):
                hallazgo(H, p, "tramo_raro", f"longitud {lm:.0f} m con los extremos a {recta:.0f} m en recta", 2)
            if recta > 30_000:
                hallazgo(H, p, "tramo_raro", f"extremos a {recta / 1000:.1f} km", 1)
            if rb is not None and recta > 300 and dif(rb, rumbo(pos, (p["la2"], p["lo2"]))) > 100:
                hallazgo(H, p, "tramo_al_reves", f"rumbo {rb:.0f}° y la salida queda hacia "
                         f"{rumbo(pos, (p['la2'], p['lo2'])):.0f}°", 1)
            cs2 = cerca(red, (p["la2"], p["lo2"]), 300)
            if not cs2 or cs2[0][0] > 40:
                hallazgo(H, p, "salida_fuera_de_via", f"salida a {cs2[0][0]:.0f} m de la carretera" if cs2 else
                         "salida sin carretera a menos de 300 m", 2)
            elif rc and not any(rc in refs(red.vias[x[1]].ref) for x in cs2 if x[0] <= 80):
                hallazgo(H, p, "salida_otra_via", f"la salida no está sobre la {p['c']}", 2)
    log(f"red: {len(H)} hallazgos")

    # ------------------------------------------------------------------ 5: PK y sentido con los hitos
    geo = recolector.Geocodificador()
    con_pk = [p for p in fijos if p.get("pk") is not None and ref_carretera(p.get("c")) and p.get("pr") in recolector.PROVINCIAS]
    pet = set()
    for p in con_pk:
        k = int(math.floor(float(p["pk"])))
        pet.add((p["c"], k, p["pr"]))
        pet.add((p["c"], k + 1, p["pr"]))
    geo.precargar(pet)
    n_pk = n_sent = 0
    for p in con_pk:
        pk = float(p["pk"])
        k = int(math.floor(pk))
        a = geo.cache.get(f"{p['c']}|{k}|{p['pr']}")
        b = geo.cache.get(f"{p['c']}|{k + 1}|{p['pr']}")
        if not (a and b):
            continue
        lab = dist(a, b)
        if not (500 <= lab <= 1600):
            continue      # hitos dudosos (o carretera muy revirada)
        n_pk += 1
        f = pk - k
        en_pk = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        d = dist(en_pk, (p["la"], p["lo"]))
        if d > 1000 and not p.get("px"):
            hallazgo(H, p, "pk_lejos", f"a {d / 1000:.1f} km de donde cae su PK {pk} en {p['c']}",
                     1 if d > 3000 else 2, d=round(d), en_pk=[round(en_pk[0], 5), round(en_pk[1], 5)])
        s = (p.get("s") or "").lower()
        rb = p.get("rb")
        if rb is None or d > 1500 or s not in ("creciente", "decreciente"):
            continue
        n_sent += 1
        hacia = rumbo(a, b) if s == "creciente" else rumbo(b, a)
        df = dif(rb, hacia)
        if df > 120:
            hallazgo(H, p, "sentido_al_reves", f"«{p['s']}» va hacia {hacia:.0f}° (del km {k if s == 'creciente' else k + 1} "
                     f"al {k + 1 if s == 'creciente' else k}) y el rumbo es {rb:.0f}°", 1, verificado=p["id"] in verif)
        elif df > 70:
            hallazgo(H, p, "sentido_dudoso", f"«{p['s']}» va hacia {hacia:.0f}° y el rumbo es {rb:.0f}°", 3)
    stats["comprobados_pk"] = n_pk
    stats["comprobados_sentido_pk"] = n_sent
    log(f"hitos: {n_pk} con PK comprobado, {n_sent} con sentido comprobado")

    # ------------------------------------------------------------------ 6: duplicados
    rej = defaultdict(list)
    for p in fijos:
        rej[(round(p["la"] / 0.002), round(p["lo"] / 0.002))].append(p)
    vistos = set()
    for p in fijos:
        cy, cx = round(p["la"] / 0.002), round(p["lo"] / 0.002)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for q in rej.get((cy + dy, cx + dx), ()):
                    if q["id"] <= p["id"] or (p["id"], q["id"]) in vistos:
                        continue
                    grupo = lambda t: "RADAR" if t in ("RADAR_FIJO", "RADAR_TRAMO") else t
                    if grupo(p["t"]) != grupo(q["t"]):
                        continue
                    d = dist((p["la"], p["lo"]), (q["la"], q["lo"]))
                    if d > 50:
                        continue
                    rp, rq = p.get("rb"), q.get("rb")
                    if rp is not None and rq is not None and dif(rp, rq) > 45:
                        continue
                    vistos.add((p["id"], q["id"]))
                    hallazgo(H, p, "duplicado", f"a {d:.0f} m de {q['id']} ({q.get('src')}, rumbo {rq})", 2, otro=q["id"])

    # ------------------------------------------------------------------ 9: cobertura frente a OSM
    nuestros = defaultdict(list)
    for p in fijos:
        for la, lo in [(p["la"], p["lo"])] + ([(p["la2"], p["lo2"])] if p.get("la2") is not None else []):
            nuestros[(round(la / 0.01), round(lo / 0.01))].append((la, lo))

    def hay_nuestro(la, lo, radio):
        cy, cx = round(la / 0.01), round(lo / 0.01)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for q in nuestros.get((cy + dy, cx + dx), ()):
                    if dist((la, lo), q) <= radio:
                        return True
        return False

    faltan = []
    if os.path.exists(OPL):
        ov = recolector.opl_a_overpass(OPL)
        n_osm = 0
        for e in ov["elements"]:
            if e["type"] != "node":
                continue
            t = e["tags"]
            es = t.get("highway") == "speed_camera" or "speed_camera" in t or t.get("enforcement") in ("maxspeed", "traffic_signals", "average_speed")
            if not es:
                continue
            n_osm += 1
            if not hay_nuestro(e["lat"], e["lon"], 150):
                faltan.append({"id": f"osm:n{e['id']}", "la": e["lat"], "lo": e["lon"], "fecha": e.get("timestamp", "")[:10],
                               "tags": {k: v for k, v in t.items() if k in ("highway", "enforcement", "speed_camera", "maxspeed",
                                                                           "direction", "ref", "name", "description", "note")}})
        for e in ov["elements"]:
            if e["type"] != "relation" or e["tags"].get("enforcement") not in ("maxspeed", "average_speed", "traffic_signals"):
                continue
            n_osm += 1
            dev = [m for m in e["members"] if m["type"] == "node" and m["role"] in ("device", "from", "")]
            if dev and not any(hay_nuestro(m["lat"], m["lon"], 150) for m in dev):
                m = dev[0]
                faltan.append({"id": f"osm:r{e['id']}", "la": m["lat"], "lo": m["lon"], "fecha": "",
                               "tags": {k: v for k, v in e["tags"].items() if k in ("enforcement", "maxspeed", "name", "description")}})
        stats["osm_camaras"] = n_osm
    stats["osm_sin_nuestro"] = len(faltan)
    log(f"OSM: {stats['osm_camaras']} cámaras, {len(faltan)} sin punto nuestro a 150 m")

    # ------------------------------------------------------------------ informe
    os.makedirs("auditoria", exist_ok=True)
    json.dump({"stats": stats, "hallazgos": H, "osm_faltan": faltan}, open("auditoria/hallazgos.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=0)
    por = Counter(h["tipo"] for h in H)
    L = [f"# Auditoría {datos.get('version')}", "", "## Resumen", ""]
    L += [f"- {k}: {v}" for k, v in sorted(stats.items())]
    L += ["", "| Tipo | Hallazgos | Graves |", "|---|---:|---:|"]
    for k, v in por.most_common():
        L.append(f"| {k} | {v} | {sum(1 for h in H if h['tipo'] == k and h['grave'] == 1)} |")
    for k, _ in por.most_common():
        L += ["", f"## {k}", ""]
        for h in sorted((h for h in H if h["tipo"] == k), key=lambda h: (h["grave"], h["src"] or "")):
            L.append(f"- [{h['grave']}] `{h['id']}` ({h['src']}; {h['c']} PK {h['pk']} {h['s'] or ''}) "
                     f"{h['la']:.5f},{h['lo']:.5f}: {h['detalle']}")
    L += ["", "## Cámaras de OSM sin punto nuestro a 150 m", ""]
    for f in faltan:
        L.append(f"- `{f['id']}` {f['la']:.5f},{f['lo']:.5f} {f['fecha']} {f['tags']}")
    open("auditoria/INFORME.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    log(f"hecho: {len(H)} hallazgos {dict(por)}")


if __name__ == "__main__":
    main()
