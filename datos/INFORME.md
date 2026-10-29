# Datos de Atalaya

Versión: 2026-10-29T11:00:01+00:00 · Total: **4582** puntos

## Fuentes

- **DGT feed**: ✅ 737 (1s)
- **DGT PDF radares**: ✅ 175 (6s)
- **DGT PDF cámaras**: ✅ 249 (1s)
- **Cataluña (SCT)**: ✅ 230 (15s)
- **Ayto. Madrid**: ✅ 23 (1s)
- **Ayto. València**: ✅ 6 (0s)
- **OpenStreetMap**: ✅ 2605 (79s)
- **Tramos radar móvil**: ✅ 1152 (0s)
- **Ayto. Madrid foto-rojo y ZBE**: ✅ 454 (2s)
- **Ayto. Málaga foto-rojo**: ✅ 7 (1s)
- **Ayto. Salamanca**: ✅ 24 (2s)
- **Ayto. Donostia**: ✅ 12 (1s)
- **Ayto. Santa Cruz de Tenerife foto-rojo**: ⚠️ falló (www.santacruzdetenerife.es: <urlopen error timed out>); se mantienen 0 de la vez anterior
- **Ayto. Pamplona cinemómetros**: ⚠️ falló (sig.pamplona.es: <urlopen error timed out>); se mantienen 0 de la vez anterior
- **Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados)**: ✅ 1654 (0s)
- **Sentido de los radares DGT (segunda opinión)**: 51 sentidos nuevos, 573 coinciden con los nuestros, 5 en desacuerdo (se avisa en los dos)
- **Sentido heredado de OSM**: copias de OSM con sentido frente a oficiales: 528/603 → no se usa
- **Sentido de los radares de OSM**: 38 radares de OSM con direction; frente a los oficiales: 4 igual, 0 al revés → se usa en 38 puntos
- **Zonas de bajas emisiones**: ✅ 57
- **Caminos de aproximación**: ✅ 3242 puntos con camino por su carretera, 268 de 325 tramos con recorrido real (81 sin vía cercana; 68s)
- **Sentido por el lado de la calle**: 309 puntos de calles de doble sentido y 61 de medianas siguen en ambos sentidos. Prueba de la regla (✓ = se usa): carretera 4-7 m: 117/155; carretera 7-12 m: 88/113; carretera 12-25 m: 24/39; carretera 25-41 m: 13/26; ciudad 4-7 m: 57/90; ciudad 7-12 m: 20/28; ciudad 12-25 m: 10/15; ciudad 25-41 m: 2/5. Pistas combinadas: limite 22/29; cruce+lado 3/4; cruce 23/28; lado+limite 8/10
- **Copias de OSM de radares oficiales**: 46 quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: 26/29 → no se hereda
- **Radares viejos de OSM repetidos**: 2 quitados (de OSM sin sentido, con otro radar más fiable en la misma calle y sentido a menos de 300 m; 450 m si no tiene datos; 600 m si además es de 2015 o antes): osm:n1123913886, osm:r20130852
- **Radares seguidos (mismo sentido, < 300 m)**: 26 pares por revisar: osm:n8081941155→osm:n8432725880 85 m; osm:n8081941154→osm:n8432725875 99 m; madzbe:40.3986,-3.6695→madzbe:40.3977,-3.6701 105 m; osm:n5308701907→osm:n245940388 120 m; dgt:GUID_CABINACINEMOMETRO_120452→dgt:GUID_CABINACINEMOMETRO_120647 123 m; madzbe:40.3926,-3.6774→madzbe:40.3932,-3.6767 130 m; osm:n9205627955→osm:n8119271102 144 m; madzbe:40.4142,-3.7208→madzbe:40.4156,-3.7208 156 m; osm:n992007100→dgt:GUID_CABINACINEMOMETRO_120390 162 m; madzbe:40.4127,-3.7211→madzbe:40.4142,-3.7208 163 m; osm:n2334938884→osm:n14130746912 169 m; madzbe:40.4266,-3.7133→madzbe:40.4280,-3.7141 181 m; osm:n8081941130→osm:n8119271103 186 m; madzbe:40.3631,-3.6845→madzbe:40.3614,-3.6838 188 m; madzbe:40.3614,-3.6838→madzbe:40.3631,-3.6845 189 m; madzbe:40.4130,-3.7137→madzbe:40.4118,-3.7137 198 m; madzbe:40.4193,-3.6943→madzbe:40.4188,-3.6967 211 m; madzbe:40.4061,-3.7080→madzbe:40.4064,-3.7095 213 m; osm:n8432725880→osm:n8432725882 219 m; madzbe:40.3891,-3.6916→madzbe:40.3910,-3.6927 226 m
- **Límites tomados de su vía**: 121 puestos, 2 quitados por no ser de su vía
- **Revisar**: nada sospechoso

## Por comunidad

| Comunidad | Fijos | Tramo | Semáforo | Stop/ceda | Otras cám. | Zonas móvil |
|---|---:|---:|---:|---:|---:|---:|
| Andalucía | 278 | 48 | 19 | 0 | 61 | 230 |
| Aragón | 95 | 6 | 0 | 0 | 17 | 102 |
| Canarias | 46 | 12 | 2 | 0 | 0 | 68 |
| Cantabria | 15 | 6 | 2 | 0 | 3 | 27 |
| Castilla y León | 178 | 57 | 32 | 0 | 31 | 265 |
| Castilla-La Mancha | 104 | 20 | 9 | 1 | 33 | 150 |
| Cataluña | 478 | 69 | 59 | 0 | 3 | 60 |
| Comunidad de Madrid | 142 | 28 | 60 | 1 | 304 | 59 |
| Comunidad Foral de Navarra | 26 | 2 | 1 | 0 | 2 | 35 |
| Comunitat Valenciana | 146 | 28 | 6 | 0 | 43 | 69 |
| Extremadura | 50 | 7 | 2 | 0 | 5 | 86 |
| Galicia | 119 | 33 | 7 | 0 | 30 | 128 |
| Illes Balears | 67 | 11 | 0 | 0 | 2 | 34 |
| La Rioja | 29 | 0 | 0 | 0 | 6 | 17 |
| Melilla | 6 | 0 | 0 | 0 | 0 | 0 |
| País Vasco | 173 | 2 | 9 | 0 | 0 | 0 |
| Principado de Asturias | 68 | 12 | 8 | 0 | 7 | 32 |
| Región de Murcia | 20 | 5 | 0 | 0 | 5 | 63 |
| Sin asignar | 0 | 0 | 1 | 0 | 0 | 0 |

Con sentido de circulación conocido (avisos solo en tu sentido): **2017**
Zonas de bajas emisiones: **57**

## Por fuente

- OSM: 1354
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
OpenStreetMap: 2605 puntos
Tramos radar móvil: 1152 puntos
Ayto. Madrid foto-rojo y ZBE: 454 puntos
Ayto. Málaga foto-rojo: 7 puntos
Ayto. Salamanca: 24 puntos
Ayto. Donostia: 12 puntos
Ayto. Santa Cruz de Tenerife foto-rojo: ERROR www.santacruzdetenerife.es: <urlopen error timed out>
Ayto. Pamplona cinemómetros: ERROR sig.pamplona.es: <urlopen error timed out>
Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados): 1654 puntos
feed comunitario tras quitar tramos ya situados: 483
tramos: 2 puntos sueltos unidos a su tramo, 5 cámaras de entrada/salida absorbidas
correcciones: 1 quitados, 1 sentidos fijados
  límites: 194 sin límite, 0 por consultar
límites deducidos de OSM: 115
  regiones: 0 celdas nuevas que consultar
  CartoCiudad: 1993 hitos necesarios, 0 por consultar
rumbos por sentido: 1020
sentido hacia una ciudad: 72 puntos
51 sentidos nuevos, 573 coinciden con los nuestros, 5 en desacuerdo (se avisa en los dos)
copias de OSM con sentido frente a oficiales: 528/603 → no se usa
38 radares de OSM con direction; frente a los oficiales: 4 igual, 0 al revés → se usa en 38 puntos
  ZBE: API CKAN no disponible (nap.dgt.es: HTTP Error 403: Forbidden); leo la página
  ZBE: 45 ficheros
ZBE: 57 zonas
  caminos: red cargada (937773 vías) en 51s
  caminos: regla del lado probada en 52s
  caminos: regla del cruce probada en 52s
  caminos: 0/3325 en 52s (dgt:GUID_CVM_161274)
  caminos: 500/3325 en 53s (dgt:GUID_CABINACINEMOMETRO_120585)
  caminos: 1000/3325 en 55s (sct:41.64066,2.16653)
  caminos: 1500/3325 en 59s (dgteq:N-1:251.3:D:cintur)
  caminos: 2000/3325 en 61s (osm:n992001156)
  caminos: 2500/3325 en 64s (osm:n11026473818)
  caminos: 3000/3325 en 67s (osm:n100482065)
46 quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: 26/29 → no se hereda
radares de OSM mapeados dos veces: 1 quitados ['osm:n2238358575']
caminos: {'lado': 'carretera 4-7 m: 117/155; carretera 7-12 m: 88/113; carretera 12-25 m: 24/39; carretera 25-41 m: 13/26; ciudad 4-7 m: 57/90; ciudad 7-12 m: 20/28; ciudad 12-25 m: 10/15; ciudad 25-41 m: 2/5', 'cruce': 'limite 22/29; cruce+lado 3/4; cruce 23/28; lado+limite 8/10', 'con_camino': 3242, 'sin_via': 81, 'tramos_con_recorrido': 268, 'tramos': 325, 'caminos_alternativos': 9, 'mediana_dos': 61, 'con_paralela': 955, 'en_enlace': 34, 'sospechosos': [], 'dos_sentidos': 309, 'limites_via': 121, 'limites_quitados': 2, 'segundos': 68}
```
