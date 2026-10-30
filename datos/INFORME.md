# Datos de Atalaya

Versión: 2026-10-30T17:31:34+00:00 · Total: **4824** puntos

## Fuentes

- **DGT feed**: ✅ 737 (1s)
- **DGT PDF radares**: ✅ 175 (5s)
- **DGT PDF cámaras**: ✅ 249 (0s)
- **Cataluña (SCT)**: ✅ 230 (15s)
- **Ayto. Madrid**: ✅ 23 (1s)
- **Ayto. València**: ✅ 11 (0s)
- **OpenStreetMap**: ✅ 2859 (69s)
- **Tramos radar móvil**: ✅ 1152 (0s)
- **Ayto. Madrid foto-rojo y ZBE**: ✅ 454 (2s)
- **Ayto. Málaga foto-rojo**: ✅ 7 (1s)
- **Ayto. Salamanca**: ✅ 24 (2s)
- **Ayto. Donostia**: ✅ 12 (1s)
- **Ayto. Santa Cruz de Tenerife foto-rojo**: ⚠️ falló (www.santacruzdetenerife.es: <urlopen error timed out>); se mantienen 0 de la vez anterior
- **Ayto. Pamplona cinemómetros**: ⚠️ falló (sig.pamplona.es: <urlopen error timed out>); se mantienen 0 de la vez anterior
- **Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados)**: ✅ 1654 (0s)
- **Sentido de los radares DGT (segunda opinión)**: 52 sentidos nuevos, 585 coinciden con los nuestros, 6 en desacuerdo (se avisa en los dos)
- **Sentido heredado de OSM**: copias de OSM con sentido frente a oficiales: 539/574 → se usa en 270 puntos
- **Sentido de los radares de OSM**: 38 radares de OSM con direction; frente a los oficiales: 5 igual, 0 al revés → se usa en 37 puntos
- **Zonas de bajas emisiones**: ✅ 57
- **Caminos de aproximación**: ✅ 3484 puntos con camino por su carretera, 272 de 330 tramos con recorrido real (82 sin vía cercana; 62s)
- **Sentido por el lado de la calle**: 220 puntos de calles de doble sentido y 23 de medianas siguen en ambos sentidos. Prueba de la regla (✓ = se usa): carretera 4-7 m: 150/198; carretera 7-12 m: 106/140; carretera 12-25 m: 24/40; carretera 25-41 m: 13/26; ciudad 4-7 m: 74/118; ciudad 7-12 m: 25/39; ciudad 12-25 m: 10/15; ciudad 25-41 m: 2/6. Pistas combinadas: limite 22/30; cruce+lado 3/5; cruce 24/30; lado+limite 9/11
- **Copias de OSM de radares oficiales**: 47 quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: 28/32 → no se hereda
- **Radares viejos de OSM repetidos**: 2 quitados (de OSM sin sentido, con otro radar más fiable en la misma calle y sentido a menos de 300 m; 450 m si no tiene datos; 600 m si además es de 2015 o antes): osm:n1123913886, osm:r20130852
- **Radares seguidos (mismo sentido, < 300 m)**: 36 pares por revisar: dgt:GUID_CABINACINEMOMETRO_120602→dgt:GUID_CABINACINEMOMETRO_120603 14 m; osm:n8081941155→osm:n8432725880 85 m; osm:n8081941154→osm:n8432725875 99 m; madzbe:40.3986,-3.6695→madzbe:40.3977,-3.6701 105 m; osm:n4756348598→osm:n8081941155 109 m; osm:n5308701907→osm:n245940388 120 m; dgt:GUID_CABINACINEMOMETRO_120452→dgt:GUID_CABINACINEMOMETRO_120647 123 m; madzbe:40.3926,-3.6774→madzbe:40.3932,-3.6767 130 m; osm:n571649668b→osm:n571649668 135 m; osm:n13170535898b→osm:n13170535897 139 m; osm:n13170535897b→osm:n13170535898 139 m; osm:n9205627955→osm:n8119271102 144 m; madzbe:40.4142,-3.7208→madzbe:40.4156,-3.7208 156 m; osm:n992007100→dgt:GUID_CABINACINEMOMETRO_120390 162 m; madzbe:40.4127,-3.7211→madzbe:40.4142,-3.7208 163 m; osm:n2334938884→osm:n14130746912 169 m; madzbe:40.4266,-3.7133→madzbe:40.4280,-3.7141 181 m; osm:n8081941130→osm:n8119271103 186 m; madzbe:40.3631,-3.6845→madzbe:40.3614,-3.6838 188 m; madzbe:40.3614,-3.6838→madzbe:40.3631,-3.6845 189 m
- **Límites tomados de su vía**: 119 puestos, 2 quitados por no ser de su vía
- **Revisar**: nada sospechoso

## Por comunidad

| Comunidad | Fijos | Tramo | Semáforo | Stop/ceda | Otras cám. | Zonas móvil |
|---|---:|---:|---:|---:|---:|---:|
| Andalucía | 295 | 51 | 22 | 0 | 63 | 230 |
| Aragón | 97 | 6 | 0 | 0 | 17 | 102 |
| Canarias | 51 | 13 | 2 | 0 | 0 | 68 |
| Cantabria | 16 | 6 | 2 | 0 | 3 | 27 |
| Castilla y León | 215 | 58 | 34 | 0 | 31 | 265 |
| Castilla-La Mancha | 102 | 20 | 12 | 1 | 33 | 150 |
| Cataluña | 510 | 69 | 64 | 0 | 3 | 60 |
| Comunidad de Madrid | 154 | 28 | 66 | 1 | 304 | 59 |
| Comunidad Foral de Navarra | 37 | 2 | 1 | 0 | 2 | 35 |
| Comunitat Valenciana | 159 | 28 | 8 | 0 | 47 | 69 |
| Extremadura | 56 | 7 | 2 | 0 | 5 | 86 |
| Galicia | 127 | 33 | 7 | 0 | 31 | 128 |
| Illes Balears | 83 | 11 | 0 | 0 | 2 | 34 |
| La Rioja | 38 | 0 | 0 | 0 | 6 | 17 |
| Melilla | 6 | 0 | 0 | 0 | 0 | 0 |
| País Vasco | 206 | 2 | 9 | 0 | 0 | 0 |
| Principado de Asturias | 77 | 12 | 8 | 0 | 7 | 32 |
| Región de Murcia | 20 | 5 | 0 | 0 | 5 | 63 |
| Sin asignar | 0 | 0 | 1 | 0 | 0 | 0 |

Con sentido de circulación conocido (avisos solo en tu sentido): **2533**
Zonas de bajas emisiones: **57**

## Por fuente

- OSM: 1568
- DGT_TRAMOS_MOVIL: 1306
- DGT: 1123
- AYUNTAMIENTO: 391
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
Ayto. València: 11 puntos
OpenStreetMap: 2859 puntos
Tramos radar móvil: 1152 puntos
Ayto. Madrid foto-rojo y ZBE: 454 puntos
Ayto. Málaga foto-rojo: 7 puntos
Ayto. Salamanca: 24 puntos
Ayto. Donostia: 12 puntos
Ayto. Santa Cruz de Tenerife foto-rojo: ERROR www.santacruzdetenerife.es: <urlopen error timed out>
Ayto. Pamplona cinemómetros: ERROR sig.pamplona.es: <urlopen error timed out>
Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados): 1654 puntos
feed comunitario tras quitar tramos ya situados: 483
fusión: 250 radares que estaban junto a otro del sentido contrario se mantienen (antes se perdían)
tramos: 2 puntos sueltos unidos a su tramo, 5 cámaras de entrada/salida absorbidas
correcciones: 2 quitados, 0 sentidos fijados
  límites: 189 sin límite, 5 por consultar
límites deducidos de OSM: 114
  regiones: 22 celdas nuevas que consultar
  regiones: ejemplo de respuesta {"id": "01.41.MUN_410910499394", "province": "Sevilla", "provinceCode": "41", "comunidadAutonoma": "Andalucía", "comunidadAutonomaCode": "01", "muni": "Sevilla", "muniCode": "41091", "type": "portal", "address": "PARQUEFLORES VI FASE", "postalCode": "41015", "poblacion": "Sevilla", "geom": "POINT(-5
  CartoCiudad: 2002 hitos necesarios, 0 por consultar
rumbos por sentido: 1041
sentido hacia una ciudad: 53 puntos
52 sentidos nuevos, 585 coinciden con los nuestros, 6 en desacuerdo (se avisa en los dos)
copias de OSM con sentido frente a oficiales: 539/574 → se usa en 270 puntos
38 radares de OSM con direction; frente a los oficiales: 5 igual, 0 al revés → se usa en 37 puntos
  ZBE: API CKAN no disponible (nap.dgt.es: HTTP Error 403: Forbidden); leo la página
  ZBE: 45 ficheros
ZBE: 57 zonas
  caminos: red cargada (937995 vías) en 49s
  caminos: regla del lado probada en 50s
  caminos: regla del cruce probada en 50s
  caminos: 0/3568 en 50s (dgt:GUID_CVM_161274)
  caminos: 500/3568 en 51s (dgt:GUID_CABINACINEMOMETRO_120570)
  caminos: 1000/3568 en 52s (sct:41.54123,1.88726)
  caminos: 1500/3568 en 55s (dgteq:A-7:525.9:C:cintur)
  caminos: 2000/3568 en 56s (osm:n986339533)
  caminos: 2500/3568 en 59s (osm:n10101245045)
  caminos: 3000/3568 en 61s (osm:n13745832649)
  caminos: 3500/3568 en 62s (osm:n13734486002b)
47 quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: 28/32 → no se hereda
radares de OSM mapeados dos veces: 1 quitados ['osm:n2238358575']
caminos: {'lado': 'carretera 4-7 m: 150/198; carretera 7-12 m: 106/140; carretera 12-25 m: 24/40; carretera 25-41 m: 13/26; ciudad 4-7 m: 74/118; ciudad 7-12 m: 25/39; ciudad 12-25 m: 10/15; ciudad 25-41 m: 2/6', 'cruce': 'limite 22/30; cruce+lado 3/5; cruce 24/30; lado+limite 9/11', 'con_camino': 3484, 'sin_via': 82, 'tramos_con_recorrido': 272, 'tramos': 330, 'caminos_alternativos': 13, 'mediana_dos': 23, 'con_paralela': 1046, 'en_enlace': 38, 'sospechosos': [], 'dos_sentidos': 220, 'limites_via': 119, 'limites_quitados': 2, 'en_tunel': 58, 'segundos': 62}
```
