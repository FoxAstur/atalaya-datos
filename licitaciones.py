#!/usr/bin/env python3
"""
Vigía de licitaciones: contratos públicos de radares, foto-rojo, foto-stop y cámaras de tráfico en España
(Diario Oficial de la UE, TED). Los pliegos suelen decir dónde va cada equipo: así se sabe de cámaras
nuevas antes de que nadie las meta en el mapa. Deja datos/LICITACIONES.md, con las nuevas marcadas.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from datetime import date, timedelta

API = "https://api.ted.europa.eu/v3/notices/search"
TERMINOS = ["cinemómetro", "cinemómetros", "cinemometro", "foto-rojo", "fotorrojo", "foto rojo", "foto-stop",
            "fotostop", "radar de velocidad", "radares de velocidad", "control de velocidad", "semáforo en rojo",
            "control de accesos ZBE", "lectura de matrículas", "radar de tramo", "control de stop"]
CAMPOS = ["publication-number", "notice-title", "buyer-name", "buyer-city", "publication-date", "notice-type",
          "place-of-performance", "links"]
CACHE = "cache/licitaciones.json"
SALIDA = "datos/LICITACIONES.md"


def buscar(termino: str, desde: str) -> list[dict]:
    q = f'FT~"{termino}" AND buyer-country=ESP AND publication-date>={desde}'
    cuerpo = json.dumps({"query": q, "fields": CAMPOS, "limit": 100, "page": 1, "scope": "ALL",
                         "paginationMode": "PAGE_NUMBER"}).encode()
    req = urllib.request.Request(API, data=cuerpo, method="POST",
                                 headers={"Content-Type": "application/json", "Accept": "application/json",
                                          "User-Agent": "AtalayaLicitaciones/1.0 (+https://github.com/FoxAstur/atalaya-datos)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8")).get("notices", [])


def texto(v) -> str:
    """Los campos de TED vienen como {"spa": [...], "eng": [...]} o listas: se coge el español si hay."""
    if isinstance(v, dict):
        for k in ("spa", "SPA", "es", "cat", "eng", "ENG"):
            if k in v:
                return texto(v[k])
        return texto(next(iter(v.values()), ""))
    if isinstance(v, list):
        return " · ".join(dict.fromkeys(texto(x) for x in v if x))
    return str(v or "").strip()


def main() -> int:
    desde = (date.today() - timedelta(days=730)).strftime("%Y%m%d")
    conocidas = {}
    if os.path.exists(CACHE):
        conocidas = json.load(open(CACHE, encoding="utf-8"))
    todas, errores = {}, []
    for t in TERMINOS:
        try:
            for n in buscar(t, desde):
                num = n.get("publication-number")
                if num and num not in todas:
                    todas[num] = n | {"_termino": t}
        except Exception as e:  # noqa: BLE001
            errores.append(f"{t}: {e}")
        time.sleep(1)
    hoy = date.today().isoformat()
    filas = []
    for num, n in todas.items():
        vista = conocidas.get(num) or hoy
        conocidas[num] = vista
        enlace = f"https://ted.europa.eu/es/notice/-/detail/{num}"
        filas.append((texto(n.get("publication-date"))[:10], num, texto(n.get("buyer-name")), texto(n.get("buyer-city")),
                      texto(n.get("notice-title")).replace("|", "/")[:200], n["_termino"], enlace, vista == hoy))
    filas.sort(reverse=True)
    os.makedirs("datos", exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(f"# Licitaciones de radares y cámaras de tráfico (TED, España)\n\nRevisado: {hoy} · desde {desde} · "
                f"{len(filas)} anuncios, {sum(1 for x in filas if x[7])} nuevos desde la última vez\n\n")
        if errores:
            f.write("Errores: " + "; ".join(errores) + "\n\n")
        f.write("| Fecha | Comprador | Lugar | Objeto | Encontrado por | |\n|---|---|---|---|---|---|\n")
        for fe, num, comp, ciudad, titulo, ter, enlace, nueva in filas:
            f.write(f"| {fe} | {comp} | {ciudad} | {('**NUEVA** ' if nueva else '') + titulo} | {ter} | [{num}]({enlace}) |\n")
    os.makedirs("cache", exist_ok=True)
    json.dump(conocidas, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
    print(f"{len(filas)} anuncios; errores: {errores}")
    return 0 if not errores or filas else 1


if __name__ == "__main__":
    sys.exit(main())
