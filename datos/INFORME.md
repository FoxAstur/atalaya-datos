# Datos de Atalaya

Versión: 2026-10-26T22:45:24+00:00 · Total: **4007** puntos

## Fuentes

- **DGT feed**: ✅ 737 (1s)
- **DGT PDF radares**: ✅ 230 (137s)
- **DGT PDF cámaras**: ✅ 249 (150s)
- **Cataluña (SCT)**: ⚠️ falló (analisi.transparenciacatalunya.cat: HTTP Error 403: Forbidden); se mantienen 0 de la vez anterior
- **Ayto. Madrid**: ✅ 23 (0s)
- **Ayto. València**: ✅ 6 (5s)
- **OpenStreetMap**: ✅ 2563 (129s)
- **Tramos radar móvil**: ✅ 1152 (0s)
- **Zonas de bajas emisiones**: ✅ 57

## Por comunidad

| Comunidad | Fijos | Tramo | Semáforo | Stop/ceda | Otras cám. | Zonas móvil |
|---|---:|---:|---:|---:|---:|---:|
| Andalucía | 271 | 49 | 18 | 0 | 65 | 211 |
| Aragón | 92 | 6 | 0 | 0 | 17 | 87 |
| Canarias | 45 | 11 | 2 | 0 | 0 | 57 |
| Cantabria | 15 | 6 | 2 | 0 | 3 | 27 |
| Castilla y León | 182 | 54 | 31 | 0 | 34 | 238 |
| Castilla-La Mancha | 110 | 18 | 8 | 1 | 34 | 140 |
| Cataluña | 422 | 62 | 59 | 0 | 4 | 0 |
| Comunidad de Madrid | 146 | 26 | 49 | 1 | 17 | 33 |
| Comunidad Foral de Navarra | 25 | 2 | 1 | 0 | 2 | 27 |
| Comunitat Valenciana | 159 | 28 | 5 | 0 | 44 | 63 |
| Extremadura | 54 | 7 | 2 | 0 | 5 | 55 |
| Galicia | 119 | 31 | 8 | 0 | 30 | 121 |
| Illes Balears | 70 | 7 | 0 | 0 | 2 | 26 |
| La Rioja | 29 | 0 | 0 | 0 | 7 | 15 |
| Melilla | 5 | 0 | 0 | 0 | 0 | 0 |
| País Vasco | 164 | 2 | 9 | 0 | 0 | 0 |
| Principado de Asturias | 69 | 10 | 5 | 0 | 7 | 23 |
| Región de Murcia | 20 | 5 | 0 | 0 | 5 | 26 |
| Sin asignar | 42 | 11 | 2 | 0 | 2 | 3 |

Con sentido de circulación conocido (avisos solo en tu sentido): **1081**
Zonas de bajas emisiones: **57**

## Por fuente

- OSM: 1672
- DGT: 1162
- DGT_TRAMOS_MOVIL: 1152
- AYUNTAMIENTO: 21

## Registro

```
DGT feed: 737 puntos
PDFs DGT: {'equipos': 'https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/conoce-el-estado-del-trafico/informacion-e-incidencias-de-trafico/EQUIPOS.pdf', 'cinemometros': 'https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/conoce-el-estado-del-trafico/informacion-e-incidencias-de-trafico/INFORME_CINEMOMETROS_WEB_OK_20260803_extra.pdf'}
  cinemómetros: 2158 filas (707 fijos, 126 tramos, 1325 móviles)
  CartoCiudad: 1827 hitos necesarios, 1827 por consultar
    300/1827
    600/1827
    900/1827
    1200/1827
    1500/1827
    1800/1827
  cinemómetros: 230 añadidos al feed, 23 sin poder situar
DGT PDF radares: 230 puntos
  equipos: 260 filas; tipos: ['Cinturón', 'Foto Rojo', 'Línea Contínua', 'Video Stop']
  CartoCiudad: 496 hitos necesarios, 403 por consultar
    300/403
  equipos: 249 situados, 11 sin poder situar
DGT PDF cámaras: 249 puntos
Cataluña (SCT): ERROR analisi.transparenciacatalunya.cat: HTTP Error 403: Forbidden
  Madrid columnas: ['Nº RADAR', 'Ubicacion', 'Carretara o vial', 'UBICACIÓN Calle 30', 'PK', 'Sentido', 'Tipo', 'Carril', 'Longitud inicio tramo', 'Latitud inicio tramo', 'X (WGS84)', 'Y (WGS84)', 'Longitud', 'Latitud', 'Velocidad límite', 'Responsable']
Ayto. Madrid: 23 puntos
Ayto. València: 6 puntos
OpenStreetMap: 2563 puntos
Tramos radar móvil: 1152 puntos
  límites: 232 sin límite, 232 por consultar
  límites: lote fallido (Overpass: overpass.kumi.systems: HTTP Error 504: Gateway Timeout)
límites deducidos de OSM: 118
  regiones: 3938 celdas nuevas que consultar
  regiones: ejemplo de respuesta {"id": "350260056173", "province": "Las Palmas", "provinceCode": "35", "comunidadAutonoma": "Canarias", "comunidadAutonomaCode": "05", "muni": "Telde", "muniCode": "35026", "type": "portal", "address": "GC-1", "postalCode": "35219", "poblacion": null, "geom": "POINT(-15.387262715 27.9515646830001)",
  CartoCiudad: 2022 hitos necesarios, 227 por consultar
rumbos por sentido: 1081
  ZBE: API CKAN no disponible (nap.dgt.es: HTTP Error 403: Forbidden); leo la página
  ZBE: 45 ficheros
ZBE: 57 zonas
```
