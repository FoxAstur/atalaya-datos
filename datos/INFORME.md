# Datos de Atalaya

Versión: 2026-10-26T23:02:56+00:00 · Total: **4070** puntos

## Fuentes

- **DGT feed**: ✅ 737 (1s)
- **DGT PDF radares**: ✅ 175 (4s)
- **DGT PDF cámaras**: ✅ 249 (2s)
- **Cataluña (SCT)**: ✅ 230 (15s)
- **Ayto. Madrid**: ✅ 23 (1s)
- **Ayto. València**: ✅ 6 (0s)
- **OpenStreetMap**: ✅ 2621 (63s)
- **Tramos radar móvil**: ✅ 1152 (1s)
- **Zonas de bajas emisiones**: ✅ 57

## Por comunidad

| Comunidad | Fijos | Tramo | Semáforo | Stop/ceda | Otras cám. | Zonas móvil |
|---|---:|---:|---:|---:|---:|---:|
| Andalucía | 279 | 49 | 19 | 0 | 68 | 211 |
| Aragón | 92 | 6 | 0 | 0 | 18 | 87 |
| Canarias | 48 | 12 | 2 | 0 | 0 | 57 |
| Cantabria | 15 | 6 | 2 | 0 | 6 | 27 |
| Castilla y León | 181 | 57 | 32 | 0 | 35 | 240 |
| Castilla-La Mancha | 111 | 20 | 9 | 1 | 34 | 140 |
| Cataluña | 490 | 69 | 59 | 0 | 4 | 0 |
| Comunidad de Madrid | 148 | 28 | 49 | 1 | 18 | 33 |
| Comunidad Foral de Navarra | 27 | 2 | 1 | 0 | 2 | 27 |
| Comunitat Valenciana | 150 | 29 | 6 | 0 | 44 | 63 |
| Extremadura | 54 | 7 | 2 | 0 | 5 | 55 |
| Galicia | 120 | 33 | 7 | 0 | 30 | 122 |
| Illes Balears | 67 | 11 | 0 | 0 | 2 | 26 |
| La Rioja | 29 | 0 | 0 | 0 | 7 | 15 |
| Melilla | 6 | 0 | 0 | 0 | 0 | 0 |
| País Vasco | 171 | 2 | 9 | 0 | 0 | 0 |
| Principado de Asturias | 69 | 12 | 8 | 0 | 7 | 23 |
| Región de Murcia | 20 | 5 | 0 | 0 | 5 | 26 |
| Sin asignar | 0 | 0 | 1 | 0 | 0 | 0 |

Con sentido de circulación conocido (avisos solo en tu sentido): **1025**
Zonas de bajas emisiones: **57**

## Por fuente

- OSM: 1565
- DGT_TRAMOS_MOVIL: 1152
- DGT: 1106
- SCT: 226
- AYUNTAMIENTO: 21

## Registro

```
DGT feed: 737 puntos
PDFs DGT: {'equipos': 'https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/conoce-el-estado-del-trafico/informacion-e-incidencias-de-trafico/EQUIPOS.pdf', 'cinemometros': 'https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/conoce-el-estado-del-trafico/informacion-e-incidencias-de-trafico/INFORME_CINEMOMETROS_WEB_OK_20260803_extra.pdf'}
  cinemómetros: 2158 filas (707 fijos, 126 tramos, 1325 móviles)
  CartoCiudad: 672 hitos necesarios, 0 por consultar
  cinemómetros: 642 ya estaban en el feed, 175 añadidos, 8 sin poder situar
DGT PDF radares: 175 puntos
  equipos: 260 filas; tipos: ['Cinturón', 'Foto Rojo', 'Línea Contínua', 'Video Stop']
  CartoCiudad: 496 hitos necesarios, 0 por consultar
  equipos: 249 situados, 11 sin poder situar
DGT PDF cámaras: 249 puntos
  SCT JSON: analisi.transparenciacatalunya.cat: HTTP Error 403: Forbidden; pruebo CSV y TXT
  SCT https://analisi.transparenciacatalunya.cat/api/views/re3y-fftf/rows.csv?accessType=DOWNLOAD: analisi.transparenciacatalunya.cat: HTTP Error 400: Bad Request
  SCT muestra: '(ETRS89)' | 'Via         PK          Velocitat   X           Y           ' | 'A-2         445,35      120         288075,4643 4601625,063 '
  SCT radars.txt: 230 radares
Cataluña (SCT): 230 puntos
  Madrid columnas: ['Nº RADAR', 'Ubicacion', 'Carretara o vial', 'UBICACIÓN Calle 30', 'PK', 'Sentido', 'Tipo', 'Carril', 'Longitud inicio tramo', 'Latitud inicio tramo', 'X (WGS84)', 'Y (WGS84)', 'Longitud', 'Latitud', 'Velocidad límite', 'Responsable']
Ayto. Madrid: 23 puntos
Ayto. València: 6 puntos
OpenStreetMap: 2621 puntos
Tramos radar móvil: 1152 puntos
  límites: 193 sin límite, 0 por consultar
límites deducidos de OSM: 115
  regiones: 98 celdas nuevas que consultar
  regiones: ejemplo de respuesta {"id": "09.43.G43_431550252375", "province": "Tarragona", "provinceCode": "43", "comunidadAutonoma": "Cataluña/Catalunya", "comunidadAutonomaCode": "09", "muni": "Tortosa", "muniCode": "43155", "type": "portal", "address": "S BERNABE", "postalCode": "43590", "poblacion": "Jesús", "geom": "POINT(0.51
  CartoCiudad: 2001 hitos necesarios, 0 por consultar
rumbos por sentido: 1025
  ZBE: API CKAN no disponible (nap.dgt.es: HTTP Error 403: Forbidden); leo la página
  ZBE: 45 ficheros
ZBE: 57 zonas
```
