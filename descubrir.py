#!/usr/bin/env python3
"""
Explorador de fuentes: busca en los catálogos de datos abiertos de España cualquier conjunto de datos
de radares, cinemómetros, foto-rojo, cámaras de control o tramos de vigilancia, y deja un informe
(datos/DESCUBRIMIENTO.md) con cada conjunto, su publicador, sus ficheros y una muestra de su contenido.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = "AtalayaExplorador/1.0 (+https://github.com/FoxAstur/atalaya-datos)"

TERMINOS = [
    "radar", "radares", "cinemometro", "cinemómetro", "cinemometros", "cinemómetros", "foto rojo", "fotorrojo",
    "foto-rojo", "fotorojo", "semaforo rojo", "semáforo rojo", "control velocidad", "control de velocidad",
    "velocidad", "camaras control", "cámaras de control", "camaras trafico", "cámaras de tráfico", "sancion trafico",
    "radars", "cinemòmetre", "cinemòmetres", "radar tram", "radar de tramo", "radares tramo", "multas trafico",
    "denuncias trafico", "infracciones trafico", "control semaforico", "foto-roig", "fotoroig", "radar movil",
    "zona 30", "zinemometro", "abiadura",
]

# Palabras que delatan un falso positivo (radares meteorológicos, etc.)
EXCLUIR = re.compile(r"meteor|precipit|lluvia|aemet|marino|oleaje|hf radar|corriente|atmosf|tiempo real del mar|"
                     r"satelit|sentinel|altimet|batimet|eolic|aeropuert|aviaci|radón|radon\b", re.I)
INTERES = re.compile(r"radar|cinem|foto.?ro(j|i)|semaf|veloc|c[aá]mara|sanci|multa|denunc|infracc|tramo|zinemom|abiadura", re.I)


def get(url: str, timeout: int = 40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, */*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def get_json(url: str, timeout: int = 40):
    return json.loads(get(url, timeout).decode("utf-8", "replace"))


# ------------------------------------------------------------------ catálogos
CKAN = {
    "Barcelona (Ajuntament)": "https://opendata-ajuntament.barcelona.cat/data",
    "Málaga": "https://datosabiertos.malaga.eu",
    "Santa Cruz de Tenerife": "https://www.santacruzdetenerife.es/opendata",
    "Salamanca": "https://opendata.aytosalamanca.es/datosabiertos/catalogo",
    "Madrid (Ayuntamiento)": "https://datos.madrid.es",
    "València (Ajuntament)": "https://opendata.vlci.valencia.es",
    "Navarra": "https://datosabiertos.navarra.es",
    "Comunitat Valenciana": "https://dadesobertes.gva.es",
    "Andalucía": "https://www.juntadeandalucia.es/datosabiertos/portal",
    "Canarias": "https://datos.canarias.es/catalogos/general",
    "Región de Murcia": "https://datosabiertos.regiondemurcia.es/catalogo",
    "Diputació de Barcelona": "https://dadesobertes.diba.cat",
    "Alcobendas": "https://datos.alcobendas.org",
    "Gijón": "https://transparencia.gijon.es",
    "Cáceres": "https://opendata.caceres.es",
    "Bizkaia (Diputación)": "https://opendata.bizkaia.eus",
    "Gipuzkoa (Diputación)": "https://www.gipuzkoairekia.eus/es/datu-irekien-katalogoa",
    "Euskadi": "https://opendata.euskadi.eus",
    "Aragón": "https://opendata.aragon.es/ckan",
    "Castilla-La Mancha": "https://datosabiertos.castillalamancha.es",
    "Bilbao": "https://www.bilbao.eus/opendata",
    "Vitoria-Gasteiz": "https://www.vitoria-gasteiz.org/datosabiertos",
    "Sant Cugat": "https://opendata.santcugat.cat",
    "Terrassa": "https://opendata.terrassa.cat",
    "L'Hospitalet": "https://opendata.l-h.cat",
    "Rubí": "https://opendata.rubi.cat",
    "Cartagena": "https://datos.cartagena.es",
    "Logroño": "https://datos.logrono.es",
    "Badajoz": "https://datos.badajoz.es",
    "Lorca": "https://datosabiertos.lorca.es",
    "Bahía de Cádiz": "https://datos.bahiadecadiz.es",
    "Valladolid": "https://datosabiertos.valladolid.es",
    "Málaga provincia": "https://datosabiertos.malaga.es",
    "Rivas": "https://datos.rivasciudad.es",
}

OPENDATASOFT = {
    "València (opendatasoft)": "https://valencia.opendatasoft.com",
    "Castilla y León": "https://analisis.datosabiertos.jcyl.es",
    "Comunidad de Madrid": "https://datos.comunidad.madrid",
    "Sant Feliu": "https://santfeliu.opendatasoft.com",
    "Zaragoza (opendatasoft)": "https://zaragoza.opendatasoft.com",
    "Lleida": "https://lleida.opendatasoft.com",
    "L'Hospitalet (ods)": "https://lhospitalet.opendatasoft.com",
    "Gavà": "https://gava.opendatasoft.com",
}

SOCRATA = {
    "Catalunya (Generalitat)": "https://analisi.transparenciacatalunya.cat",
    "Illes Balears": "https://catalegdades.caib.cat",
}


def ckan(nombre: str, base: str) -> list[dict]:
    out = {}
    for t in TERMINOS:
        url = f"{base}/api/3/action/package_search?rows=100&q={urllib.parse.quote(t)}"
        try:
            d = get_json(url)
        except Exception:  # noqa: BLE001
            continue
        for p in d.get("result", {}).get("results", []):
            out[p.get("name") or p.get("id")] = {
                "catalogo": nombre,
                "titulo": p.get("title") or p.get("name"),
                "publica": (p.get("organization") or {}).get("title") or nombre,
                "web": f"{base}/dataset/{p.get('name')}",
                "licencia": p.get("license_title") or p.get("license_id"),
                "notas": (p.get("notes") or "")[:300],
                "ficheros": [{"url": r.get("url"), "formato": r.get("format"), "nombre": r.get("name")}
                             for r in p.get("resources", [])],
            }
    return list(out.values())


def opendatasoft(nombre: str, base: str) -> list[dict]:
    out = {}
    for t in TERMINOS:
        q = urllib.parse.quote(f'search("{t}")')
        url = f"{base}/api/explore/v2.1/catalog/datasets?limit=100&where={q}"
        try:
            d = get_json(url)
        except Exception:  # noqa: BLE001
            continue
        for r in d.get("results", []):
            ds = r.get("dataset_id")
            meta = (r.get("metas") or {}).get("default", {})
            out[ds] = {
                "catalogo": nombre, "titulo": meta.get("title") or ds, "publica": meta.get("publisher") or nombre,
                "web": f"{base}/explore/dataset/{ds}/", "licencia": meta.get("license"),
                "notas": re.sub("<[^>]+>", " ", meta.get("description") or "")[:300],
                "ficheros": [{"url": f"{base}/api/explore/v2.1/catalog/datasets/{ds}/exports/geojson", "formato": "GeoJSON"},
                             {"url": f"{base}/api/explore/v2.1/catalog/datasets/{ds}/exports/csv", "formato": "CSV"}],
            }
    return list(out.values())


def socrata(nombre: str, base: str) -> list[dict]:
    out = {}
    dominio = urllib.parse.urlparse(base).netloc
    for t in TERMINOS:
        url = f"https://api.us.socrata.com/api/catalog/v1?domains={dominio}&limit=100&q={urllib.parse.quote(t)}"
        try:
            d = get_json(url)
        except Exception:  # noqa: BLE001
            continue
        for r in d.get("results", []):
            res = r.get("resource", {})
            rid = res.get("id")
            out[rid] = {
                "catalogo": nombre, "titulo": res.get("name"), "publica": res.get("attribution") or nombre,
                "web": r.get("permalink") or f"{base}/d/{rid}",
                "licencia": (r.get("metadata") or {}).get("license"),
                "notas": (res.get("description") or "")[:300],
                "ficheros": [{"url": f"{base}/resource/{rid}.json?$limit=5000", "formato": "JSON"},
                             {"url": f"{base}/api/views/{rid}/rows.csv?accessType=DOWNLOAD", "formato": "CSV"}],
            }
    return list(out.values())


def datos_gob() -> list[dict]:
    """Catálogo nacional: agrega los catálogos de ayuntamientos, diputaciones y comunidades."""
    out = {}
    rutas = ["title", "keyword"]
    for t in TERMINOS:
        for ruta in rutas:
            pagina = 0
            while pagina < 5:
                url = (f"https://datos.gob.es/apidata/catalog/dataset/{ruta}/{urllib.parse.quote(t)}.json"
                       f"?_pageSize=50&_page={pagina}")
                try:
                    d = get_json(url, timeout=60)
                except Exception:  # noqa: BLE001
                    break
                items = d.get("result", {}).get("items", [])
                for it in items:
                    def txt(v):
                        if isinstance(v, list):
                            es = [x for x in v if isinstance(x, dict) and x.get("_lang") == "es"]
                            v = (es or v)[0] if v else ""
                        if isinstance(v, dict):
                            return v.get("_value", "")
                        return str(v or "")
                    dist = it.get("distribution") or []
                    if isinstance(dist, dict):
                        dist = [dist]
                    pub = it.get("publisher")
                    out[it.get("_about")] = {
                        "catalogo": "datos.gob.es",
                        "titulo": txt(it.get("title")),
                        "publica": pub if isinstance(pub, str) else txt(pub),
                        "web": it.get("_about"),
                        "licencia": txt(it.get("license")),
                        "notas": txt(it.get("description"))[:300],
                        "ficheros": [{"url": (x.get("accessURL") if isinstance(x, dict) else None),
                                      "formato": txt(x.get("format", {}).get("value") if isinstance(x, dict) and isinstance(x.get("format"), dict) else (x.get("format") if isinstance(x, dict) else ""))}
                                     for x in dist],
                    }
                if len(items) < 50:
                    break
                pagina += 1
    return list(out.values())


def relevante(d: dict) -> bool:
    texto = f"{d.get('titulo', '')} {d.get('notas', '')}"
    return bool(INTERES.search(d.get("titulo", ""))) and not EXCLUIR.search(texto)


def muestra(d: dict) -> str:
    """Primeros bytes del fichero más prometedor, para ver su estructura."""
    orden = ["geojson", "json", "csv", "xml", "kml", "wfs", ""]
    fich = sorted([f for f in d["ficheros"] if f.get("url")],
                  key=lambda f: next((i for i, o in enumerate(orden) if o in str(f.get("formato", "")).lower()
                                      or o in str(f.get("url", "")).lower()), 99))
    for f in fich[:2]:
        try:
            b = get(f["url"], timeout=40)[:700]
            t = b.decode("utf-8", "replace")
            return f"`{f['url']}`\n\n```\n{t[:600]}\n```"
        except Exception as e:  # noqa: BLE001
            continue
    return "(no se pudo descargar ninguna muestra)"


def main() -> int:
    tareas = [("datos.gob.es", datos_gob)]
    tareas += [(n, (lambda n=n, b=b: ckan(n, b))) for n, b in CKAN.items()]
    tareas += [(n, (lambda n=n, b=b: opendatasoft(n, b))) for n, b in OPENDATASOFT.items()]
    tareas += [(n, (lambda n=n, b=b: socrata(n, b))) for n, b in SOCRATA.items()]

    todos, estado = [], {}
    with ThreadPoolExecutor(10) as ex:
        futuros = {n: ex.submit(f) for n, f in tareas}
        for n, fu in futuros.items():
            try:
                r = fu.result(timeout=900)
                estado[n] = f"{len(r)} resultados"
                todos += r
            except Exception as e:  # noqa: BLE001
                estado[n] = f"error: {e}"

    vistos, utiles = set(), []
    for d in todos:
        clave = re.sub(r"\W+", "", (d.get("titulo") or "").lower()) + "|" + (d.get("publica") or "").lower()
        if clave in vistos or not relevante(d):
            continue
        vistos.add(clave)
        utiles.append(d)
    utiles.sort(key=lambda d: (d["publica"] or "", d["titulo"] or ""))

    with ThreadPoolExecutor(8) as ex:
        muestras = list(ex.map(muestra, utiles))

    l = ["# Descubrimiento de fuentes", "", f"Conjuntos relevantes: **{len(utiles)}**", "", "## Catálogos consultados", ""]
    l += [f"- {k}: {v}" for k, v in estado.items()]
    l += ["", "## Conjuntos encontrados", ""]
    for d, m in zip(utiles, muestras):
        l += [f"### {d['titulo']}", f"- Publica: {d['publica']} · Catálogo: {d['catalogo']}",
              f"- Web: {d['web']}", f"- Licencia: {d.get('licencia')}", f"- Notas: {d.get('notas', '').strip()[:250]}",
              "- Ficheros: " + "; ".join(f"{f.get('formato')}: {f.get('url')}" for f in d["ficheros"][:6]),
              "", m, ""]
    with open("datos/DESCUBRIMIENTO.md", "w", encoding="utf-8") as f:
        f.write("\n".join(l))
    with open("datos/descubrimiento.json", "w", encoding="utf-8") as f:
        json.dump(utiles, f, ensure_ascii=False, indent=1)
    print("\n".join(l[:40]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
