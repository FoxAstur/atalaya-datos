# Datos de Atalaya

Versión: 2026-11-02T14:18:08+00:00 · Total: **5193** puntos

## Fuentes

- **DGT feed**: ✅ 737 (1s)
- **DGT PDF radares**: ✅ 175 (6s)
- **DGT PDF cámaras**: ✅ 249 (0s)
- **Cataluña (SCT)**: ✅ 230 (16s)
- **Ayto. Madrid**: ✅ 23 (1s)
- **Ayto. València**: ✅ 11 (0s)
- **OpenStreetMap**: ✅ 3217 (69s)
- **Tramos radar móvil**: ✅ 1152 (0s)
- **Ayto. Madrid foto-rojo y ZBE**: ✅ 454 (2s)
- **Ayto. Málaga foto-rojo**: ✅ 7 (1s)
- **Ayto. Salamanca**: ✅ 24 (2s)
- **Ayto. Donostia**: ✅ 12 (1s)
- **Câmara Municipal de Lisboa**: ✅ 18 (0s)
- **Ajuntament de Viladecans**: ✅ 24 (2s)
- **Portugal: ANSR (red SINCRO)**: ✅ 121 (1s)
- **Ayto. Santa Cruz de Tenerife foto-rojo**: ⚠️ falló (www.santacruzdetenerife.es: <urlopen error timed out>); se mantienen 0 de la vez anterior
- **Ayto. Pamplona cinemómetros**: ⚠️ falló (sig.pamplona.es: <urlopen error timed out>); se mantienen 0 de la vez anterior
- **Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados)**: ✅ 1675 (0s)
- **Cámaras de stop y semáforo**: sin fichero de stops y semáforos
- **Sentido de los radares DGT (segunda opinión)**: 52 sentidos nuevos, 585 coinciden con los nuestros, 6 en desacuerdo (se avisa en los dos)
- **Sentido heredado de OSM**: copias de OSM con sentido frente a oficiales: 559/582 → se usa en 319 puntos y en 42 vigila los dos sentidos
- **Sentido de los radares de OSM**: 61 radares de OSM con direction; frente a los oficiales: 3 igual, 1 al revés → no se usa
- **Zonas de bajas emisiones**: ✅ 57
- **Caminos de aproximación**: ⚠️ sin red viaria; 3723 puntos con los caminos de la vez anterior

## Por comunidad

| Comunidad | Fijos | Tramo | Semáforo | Stop/ceda | Otras cám. | Zonas móvil |
|---|---:|---:|---:|---:|---:|---:|
| Andalucía | 303 | 53 | 22 | 0 | 63 | 230 |
| Aragón | 99 | 6 | 0 | 0 | 17 | 102 |
| Canarias | 53 | 13 | 2 | 0 | 0 | 68 |
| Cantabria | 16 | 6 | 2 | 0 | 3 | 27 |
| Castilla y León | 217 | 58 | 34 | 0 | 31 | 301 |
| Castilla-La Mancha | 109 | 20 | 12 | 1 | 33 | 150 |
| Cataluña | 517 | 69 | 69 | 0 | 3 | 60 |
| Comunidad de Madrid | 161 | 28 | 66 | 1 | 305 | 59 |
| Comunidad Foral de Navarra | 38 | 2 | 1 | 0 | 2 | 35 |
| Comunitat Valenciana | 160 | 28 | 7 | 2 | 46 | 69 |
| Extremadura | 60 | 7 | 2 | 0 | 5 | 86 |
| Galicia | 129 | 33 | 7 | 0 | 31 | 128 |
| Illes Balears | 84 | 11 | 0 | 0 | 2 | 34 |
| La Rioja | 38 | 0 | 0 | 0 | 6 | 17 |
| Melilla | 6 | 0 | 0 | 0 | 0 | 0 |
| País Vasco | 215 | 2 | 9 | 0 | 0 | 0 |
| Portugal | 266 | 33 | 8 | 0 | 0 | 0 |
| Principado de Asturias | 77 | 12 | 8 | 0 | 7 | 32 |
| Región de Murcia | 20 | 5 | 0 | 0 | 5 | 28 |
| Sin asignar | 0 | 0 | 1 | 0 | 0 | 0 |

Con sentido de circulación conocido (avisos solo en tu sentido): **2758**
Zonas de bajas emisiones: **57**

## Por fuente

- OSM: 1786
- DGT_TRAMOS_MOVIL: 1306
- DGT: 1123
- AYUNTAMIENTO: 424
- SCT: 277
- AUTONOMICA: 208
- POLICIA_LOCAL: 36
- MULTAS: 33

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
Ayto. València: 11 puntos
OpenStreetMap: 3217 puntos
Tramos radar móvil: 1152 puntos
Ayto. Madrid foto-rojo y ZBE: 454 puntos
Ayto. Málaga foto-rojo: 7 puntos
Ayto. Salamanca: 24 puntos
Ayto. Donostia: 12 puntos
Câmara Municipal de Lisboa: 18 puntos
Ajuntament de Viladecans: 24 puntos
Portugal: ANSR (red SINCRO): 121 puntos
Ayto. Santa Cruz de Tenerife foto-rojo: ERROR www.santacruzdetenerife.es: <urlopen error timed out>
Ayto. Pamplona cinemómetros: ERROR sig.pamplona.es: <urlopen error timed out>
Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados): 1675 puntos
feed comunitario tras quitar tramos ya situados: 504
fusión: 263 radares que estaban junto a otro del sentido contrario se mantienen (antes se perdían)
tramos: 5 puntos sueltos unidos a su tramo, 13 cámaras de entrada/salida absorbidas
sin fichero de stops y semáforos
correcciones: 2 quitados, 15 sentidos fijados, 1 añadidos, 1 con el tipo corregido
  límites: 229 sin límite, 0 por consultar
límites deducidos de OSM: 141
  regiones: 1 celdas nuevas que consultar
  regiones: ejemplo de respuesta {"id": "10.46.G46_460780203326", "province": "València/Valencia", "provinceCode": "46", "comunidadAutonoma": "Comunitat Valenciana", "comunidadAutonomaCode": "10", "muni": "Burjassot", "muniCode": "46078", "type": "portal", "address": "ILUSTRACION", "postalCode": "46100", "poblacion": "Burjassot", "
  CartoCiudad: 2002 hitos necesarios, 0 por consultar
rumbos por sentido: 1041
sentido hacia una ciudad: 74 puntos; ['VITORIA - GASTEIZ → 42.840,-2.722 (12 km)', 'IRUN → 43.327,-1.826 (33 km)', 'BILBAO → 43.254,-2.937 (28 km)', 'BILBAO → 43.254,-2.937 (30 km)', 'DONOSTIA / SAN SEBASTIÁN → 43.295,-1.988 (8 km)', 'IRUN → 43.327,-1.826 (21 km)', 'DONOSTIA / SAN SEBASTIÁN → 43.295,-1.988 (6 km)', 'VITORIA-GASTEIZ → 42.848,-2.679 (5 km)']
52 sentidos nuevos, 585 coinciden con los nuestros, 6 en desacuerdo (se avisa en los dos)
copias de OSM con sentido frente a oficiales: 559/582 → se usa en 319 puntos y en 42 vigila los dos sentidos
61 radares de OSM con direction; frente a los oficiales: 3 igual, 1 al revés → no se usa
  ZBE: API CKAN no disponible (nap.dgt.es: HTTP Error 403: Forbidden); leo la página
  ZBE: 45 ficheros
ZBE: 57 zonas
```
