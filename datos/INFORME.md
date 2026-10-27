# Datos de Atalaya

Versión: 2026-10-27T11:10:28+00:00 · Total: **4641** puntos

## Fuentes

- **DGT feed**: ✅ 737 (0s)
- **DGT PDF radares**: ✅ 175 (6s)
- **DGT PDF cámaras**: ✅ 249 (0s)
- **Cataluña (SCT)**: ✅ 230 (17s)
- **Ayto. Madrid**: ✅ 23 (1s)
- **Ayto. València**: ✅ 6 (0s)
- **OpenStreetMap**: ✅ 2621 (70s)
- **Tramos radar móvil**: ✅ 1152 (0s)
- **Ayto. Madrid foto-rojo y ZBE**: ✅ 454 (2s)
- **Ayto. Málaga foto-rojo**: ✅ 7 (1s)
- **Ayto. Salamanca**: ✅ 24 (1s)
- **Ayto. Donostia**: ✅ 12 (1s)
- **Ayto. Santa Cruz de Tenerife foto-rojo**: ⚠️ falló (www.santacruzdetenerife.es: <urlopen error timed out>); se mantienen 0 de la vez anterior
- **Ayto. Pamplona cinemómetros**: ⚠️ falló (sig.pamplona.es: <urlopen error timed out>); se mantienen 0 de la vez anterior
- **Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados)**: ✅ 1637 (0s)
- **Sentido de los radares de OSM**: 37 radares de OSM con direction; frente a los oficiales: 4 igual, 0 al revés → no se usa
- **Zonas de bajas emisiones**: ✅ 57
- **Caminos de aproximación**: ✅ 3252 puntos con camino por su carretera, 268 de 325 tramos con recorrido real (81 sin vía cercana; 54s)
- **Sentido por el lado de la calle**: 336 puntos siguen en ambos sentidos. Prueba de la regla (✓ = se usa): carretera 4-7 m: 115/153; carretera 7-12 m: 87/111; carretera 12-25 m: 23/38; carretera 25-41 m: 12/25; ciudad 4-7 m: 54/88; ciudad 7-12 m: 20/28; ciudad 12-25 m: 12/17; ciudad 25-41 m: 2/5
- **Límites tomados de su vía**: 114 puestos, 2 quitados por no ser de su vía
- **Revisar**: nada sospechoso

## Por comunidad

| Comunidad | Fijos | Tramo | Semáforo | Stop/ceda | Otras cám. | Zonas móvil |
|---|---:|---:|---:|---:|---:|---:|
| Andalucía | 279 | 48 | 19 | 0 | 68 | 230 |
| Aragón | 92 | 6 | 0 | 0 | 18 | 102 |
| Canarias | 48 | 12 | 2 | 0 | 0 | 68 |
| Cantabria | 15 | 6 | 2 | 0 | 6 | 27 |
| Castilla y León | 181 | 57 | 32 | 0 | 35 | 265 |
| Castilla-La Mancha | 109 | 20 | 9 | 1 | 34 | 150 |
| Cataluña | 490 | 69 | 59 | 0 | 4 | 60 |
| Comunidad de Madrid | 147 | 28 | 60 | 1 | 307 | 59 |
| Comunidad Foral de Navarra | 27 | 2 | 1 | 0 | 2 | 35 |
| Comunitat Valenciana | 149 | 28 | 6 | 0 | 44 | 69 |
| Extremadura | 54 | 7 | 2 | 0 | 5 | 86 |
| Galicia | 120 | 33 | 7 | 0 | 30 | 128 |
| Illes Balears | 67 | 11 | 0 | 0 | 2 | 34 |
| La Rioja | 29 | 0 | 0 | 0 | 7 | 17 |
| Melilla | 6 | 0 | 0 | 0 | 0 | 0 |
| País Vasco | 176 | 2 | 9 | 0 | 0 | 0 |
| Principado de Asturias | 68 | 12 | 8 | 0 | 7 | 32 |
| Región de Murcia | 20 | 5 | 0 | 0 | 5 | 63 |
| Sin asignar | 0 | 0 | 1 | 0 | 0 | 0 |

Con sentido de circulación conocido (avisos solo en tu sentido): **1984**
Zonas de bajas emisiones: **57**

## Por fuente

- OSM: 1413
- DGT_TRAMOS_MOVIL: 1306
- DGT: 1100
- AYUNTAMIENTO: 386
- SCT: 277
- AUTONOMICA: 91
- POLICIA_LOCAL: 35
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
Ayto. València: 6 puntos
OpenStreetMap: 2621 puntos
Tramos radar móvil: 1152 puntos
Ayto. Madrid foto-rojo y ZBE: 454 puntos
Ayto. Málaga foto-rojo: 7 puntos
Ayto. Salamanca: 24 puntos
Ayto. Donostia: 12 puntos
Ayto. Santa Cruz de Tenerife foto-rojo: ERROR www.santacruzdetenerife.es: <urlopen error timed out>
Ayto. Pamplona cinemómetros: ERROR sig.pamplona.es: <urlopen error timed out>
Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados): 1637 puntos
feed comunitario tras quitar tramos ya situados: 466
tramos: 2 puntos sueltos unidos a su tramo, 5 cámaras de entrada/salida absorbidas
  límites: 186 sin límite, 0 por consultar
límites deducidos de OSM: 108
  regiones: 0 celdas nuevas que consultar
  CartoCiudad: 1993 hitos necesarios, 0 por consultar
rumbos por sentido: 1020
37 radares de OSM con direction; frente a los oficiales: 4 igual, 0 al revés → no se usa
  ZBE: API CKAN no disponible (nap.dgt.es: HTTP Error 403: Forbidden); leo la página
  ZBE: 45 ficheros
ZBE: 57 zonas
caminos: {'lado': 'carretera 4-7 m: 115/153; carretera 7-12 m: 87/111; carretera 12-25 m: 23/38; carretera 25-41 m: 12/25; ciudad 4-7 m: 54/88; ciudad 7-12 m: 20/28; ciudad 12-25 m: 12/17; ciudad 25-41 m: 2/5', 'con_camino': 3252, 'sin_via': 81, 'tramos_con_recorrido': 268, 'tramos': 325, 'caminos_alternativos': 8, 'en_enlace': 36, 'sospechosos': [], 'dos_sentidos': 336, 'limites_via': 114, 'limites_quitados': 2, 'segundos': 54}
```
