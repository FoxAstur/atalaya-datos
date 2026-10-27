# Datos de Atalaya

Versión: 2026-10-27T16:49:44+00:00 · Total: **4586** puntos

## Fuentes

- **DGT feed**: ✅ 737 (1s)
- **DGT PDF radares**: ✅ 175 (8s)
- **DGT PDF cámaras**: ✅ 249 (1s)
- **Cataluña (SCT)**: ✅ 230 (16s)
- **Ayto. Madrid**: ✅ 23 (1s)
- **Ayto. València**: ✅ 6 (0s)
- **OpenStreetMap**: ⚠️ falló (Overpass: overpass.kumi.systems: HTTP Error 502: Bad Gateway); se mantienen 1410 de la vez anterior
- **Tramos radar móvil**: ✅ 1152 (0s)
- **Ayto. Madrid foto-rojo y ZBE**: ✅ 454 (2s)
- **Ayto. Málaga foto-rojo**: ✅ 7 (1s)
- **Ayto. Salamanca**: ✅ 24 (2s)
- **Ayto. Donostia**: ✅ 12 (1s)
- **Ayto. Santa Cruz de Tenerife foto-rojo**: ⚠️ falló (www.santacruzdetenerife.es: <urlopen error timed out>); se mantienen 0 de la vez anterior
- **Ayto. Pamplona cinemómetros**: ⚠️ falló (sig.pamplona.es: <urlopen error timed out>); se mantienen 0 de la vez anterior
- **Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados)**: ✅ 1637 (0s)
- **Sentido de los radares DGT (segunda opinión)**: 51 sentidos nuevos, 569 coinciden con los nuestros, 5 en desacuerdo (se avisa en los dos)
- **Sentido heredado de OSM**: copias de OSM con sentido frente a oficiales: 0/0 → no se usa
- **Sentido de los radares de OSM**: 0 radares de OSM con direction; frente a los oficiales: 0 igual, 0 al revés → no se usa
- **Zonas de bajas emisiones**: ✅ 57
- **Caminos de aproximación**: ✅ 3245 puntos con camino por su carretera, 258 de 317 tramos con recorrido real (81 sin vía cercana; 86s)
- **Sentido por el lado de la calle**: 309 puntos de calles de doble sentido y 61 de medianas siguen en ambos sentidos. Prueba de la regla (✓ = se usa): carretera 4-7 m: 117/155; carretera 7-12 m: 88/113; carretera 12-25 m: 24/39; carretera 25-41 m: 13/26; ciudad 4-7 m: 57/91; ciudad 7-12 m: 20/28; ciudad 12-25 m: 11/16; ciudad 25-41 m: 2/5. Pistas combinadas: limite 2/4; cruce+lado 3/4; cruce 23/28; lado+limite 2/2
- **Copias de OSM de radares oficiales**: 46 quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: 26/29 → no se hereda
- **Radares viejos de OSM repetidos**: 2 quitados (de OSM sin sentido, con otro radar más fiable en la misma calle y sentido a menos de 300 m; 450 m si no tiene datos; 600 m si además es de 2015 o antes): osm:n1123913886, osm:r20130852
- **Radares seguidos (mismo sentido, < 300 m)**: 26 pares por revisar: osm:n8081941155→osm:n8432725880 85 m; osm:n8081941154→osm:n8432725875 99 m; madzbe:40.3986,-3.6695→madzbe:40.3977,-3.6701 105 m; osm:n5308701907→osm:n245940388 120 m; dgt:GUID_CABINACINEMOMETRO_120452→dgt:GUID_CABINACINEMOMETRO_120647 123 m; madzbe:40.3926,-3.6774→madzbe:40.3932,-3.6767 130 m; osm:n9205627955→osm:n8119271102 144 m; madzbe:40.4142,-3.7208→madzbe:40.4156,-3.7208 156 m; osm:n992007100→dgt:GUID_CABINACINEMOMETRO_120390 162 m; madzbe:40.4127,-3.7211→madzbe:40.4142,-3.7208 163 m; madzbe:40.4266,-3.7133→madzbe:40.4280,-3.7141 181 m; osm:n8081941130→osm:n8119271103 186 m; osm:n4258215850→osm:n2238358575 186 m; madzbe:40.3631,-3.6845→madzbe:40.3614,-3.6838 188 m; madzbe:40.3614,-3.6838→madzbe:40.3631,-3.6845 189 m; madzbe:40.4130,-3.7137→madzbe:40.4118,-3.7137 198 m; madzbe:40.4193,-3.6943→madzbe:40.4188,-3.6967 211 m; madzbe:40.4061,-3.7080→madzbe:40.4064,-3.7095 213 m; osm:n8432725880→osm:n8432725882 219 m; madzbe:40.3891,-3.6916→madzbe:40.3910,-3.6927 226 m
- **Límites tomados de su vía**: 688 puestos, 4 quitados por no ser de su vía
- **Revisar**: nada sospechoso

## Por comunidad

| Comunidad | Fijos | Tramo | Semáforo | Stop/ceda | Otras cám. | Zonas móvil |
|---|---:|---:|---:|---:|---:|---:|
| Andalucía | 270 | 47 | 19 | 0 | 68 | 230 |
| Aragón | 90 | 6 | 0 | 0 | 18 | 102 |
| Canarias | 46 | 12 | 2 | 0 | 0 | 68 |
| Cantabria | 15 | 6 | 2 | 0 | 6 | 27 |
| Castilla y León | 178 | 57 | 32 | 0 | 35 | 265 |
| Castilla-La Mancha | 103 | 20 | 9 | 1 | 34 | 150 |
| Cataluña | 478 | 69 | 59 | 0 | 4 | 60 |
| Comunidad de Madrid | 142 | 28 | 60 | 1 | 305 | 59 |
| Comunidad Foral de Navarra | 26 | 2 | 1 | 0 | 2 | 35 |
| Comunitat Valenciana | 146 | 28 | 6 | 0 | 44 | 69 |
| Extremadura | 50 | 7 | 2 | 0 | 5 | 86 |
| Galicia | 119 | 33 | 7 | 0 | 30 | 128 |
| Illes Balears | 67 | 11 | 0 | 0 | 2 | 34 |
| La Rioja | 29 | 0 | 0 | 0 | 7 | 17 |
| Melilla | 6 | 0 | 0 | 0 | 0 | 0 |
| País Vasco | 173 | 2 | 9 | 0 | 0 | 0 |
| Principado de Asturias | 67 | 12 | 8 | 0 | 7 | 32 |
| Región de Murcia | 20 | 5 | 0 | 0 | 5 | 63 |
| Sin asignar | 0 | 0 | 1 | 0 | 0 | 0 |

Con sentido de circulación conocido (avisos solo en tu sentido): **2020**
Zonas de bajas emisiones: **57**

## Por fuente

- OSM: 1362
- DGT_TRAMOS_MOVIL: 1306
- DGT: 1096
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
OpenStreetMap: ERROR Overpass: overpass.kumi.systems: HTTP Error 502: Bad Gateway
Tramos radar móvil: 1152 puntos
Ayto. Madrid foto-rojo y ZBE: 454 puntos
Ayto. Málaga foto-rojo: 7 puntos
Ayto. Salamanca: 24 puntos
Ayto. Donostia: 12 puntos
Ayto. Santa Cruz de Tenerife foto-rojo: ERROR www.santacruzdetenerife.es: <urlopen error timed out>
Ayto. Pamplona cinemómetros: ERROR sig.pamplona.es: <urlopen error timed out>
Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados): 1637 puntos
feed comunitario tras quitar tramos ya situados: 466
tramos: 3 puntos sueltos unidos a su tramo, 7 cámaras de entrada/salida absorbidas
correcciones: 0 quitados, 0 sentidos fijados
  límites: 869 sin límite, 120 por consultar
  límites: lote fallido (Overpass: overpass.kumi.systems: HTTP Error 502: Bad Gateway)
límites deducidos de OSM: 549
  regiones: 0 celdas nuevas que consultar
  CartoCiudad: 1989 hitos necesarios, 0 por consultar
rumbos por sentido: 1016
sentido hacia una ciudad: 72 puntos
51 sentidos nuevos, 569 coinciden con los nuestros, 5 en desacuerdo (se avisa en los dos)
copias de OSM con sentido frente a oficiales: 0/0 → no se usa
0 radares de OSM con direction; frente a los oficiales: 0 igual, 0 al revés → no se usa
  ZBE: API CKAN no disponible (nap.dgt.es: HTTP Error 403: Forbidden); leo la página
  ZBE: 45 ficheros
ZBE: 57 zonas
  caminos: red cargada (939532 vías) en 64s
  caminos: regla del lado probada en 64s
  caminos: regla del cruce probada en 65s
  caminos: 0/3328 en 65s (dgt:GUID_CVM_161274)
  caminos: 500/3328 en 66s (dgt:GUID_CABINACINEMOMETRO_120587)
  caminos: 1000/3328 en 68s (sct:41.73961,2.81575)
  caminos: 1500/3328 en 74s (dgteq:A-2004:0.0:D:cintur)
  caminos: 2000/3328 en 77s (osm:n10978420379)
  caminos: 2500/3328 en 80s (osm:n2173326716)
  caminos: 3000/3328 en 83s (osm:r17052286)
46 quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: 26/29 → no se hereda
caminos: {'lado': 'carretera 4-7 m: 117/155; carretera 7-12 m: 88/113; carretera 12-25 m: 24/39; carretera 25-41 m: 13/26; ciudad 4-7 m: 57/91; ciudad 7-12 m: 20/28; ciudad 12-25 m: 11/16; ciudad 25-41 m: 2/5', 'cruce': 'limite 2/4; cruce+lado 3/4; cruce 23/28; lado+limite 2/2', 'con_camino': 3245, 'sin_via': 81, 'tramos_con_recorrido': 258, 'tramos': 317, 'caminos_alternativos': 9, 'mediana_dos': 61, 'con_paralela': 956, 'en_enlace': 37, 'sospechosos': [], 'dos_sentidos': 309, 'limites_via': 688, 'limites_quitados': 4, 'segundos': 86}
```
