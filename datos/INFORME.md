# Datos de Atalaya

Versión: 2026-10-30T20:21:40+00:00 · Total: **4822** puntos

## Fuentes

- **DGT feed**: ✅ 737 (1s)
- **DGT PDF radares**: ✅ 175 (6s)
- **DGT PDF cámaras**: ✅ 249 (1s)
- **Cataluña (SCT)**: ✅ 230 (15s)
- **Ayto. Madrid**: ✅ 23 (1s)
- **Ayto. València**: ✅ 11 (0s)
- **OpenStreetMap**: ⚠️ falló (Overpass: overpass.kumi.systems: HTTP Error 502: Bad Gateway); se mantienen 1573 de la vez anterior
- **Tramos radar móvil**: ✅ 1152 (1s)
- **Ayto. Madrid foto-rojo y ZBE**: ✅ 454 (3s)
- **Ayto. Málaga foto-rojo**: ✅ 7 (1s)
- **Ayto. Salamanca**: ✅ 24 (2s)
- **Ayto. Donostia**: ✅ 12 (1s)
- **Ayto. Santa Cruz de Tenerife foto-rojo**: ⚠️ falló (www.santacruzdetenerife.es: <urlopen error timed out>); se mantienen 0 de la vez anterior
- **Ayto. Pamplona cinemómetros**: ⚠️ falló (sig.pamplona.es: <urlopen error timed out>); se mantienen 0 de la vez anterior
- **Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados)**: ✅ 1654 (1s)
- **Sentido de los radares DGT (segunda opinión)**: 52 sentidos nuevos, 579 coinciden con los nuestros, 6 en desacuerdo (se avisa en los dos)
- **Sentido heredado de OSM**: copias de OSM con sentido frente a oficiales: 0/0 → no se usa
- **Sentido de los radares de OSM**: 0 radares de OSM con direction; frente a los oficiales: 0 igual, 0 al revés → no se usa
- **Zonas de bajas emisiones**: ✅ 57
- **Caminos de aproximación**: ✅ 3431 puntos con camino por su carretera, 262 de 322 tramos con recorrido real (82 sin vía cercana; 80s)
- **Sentido por el lado de la calle**: 304 puntos de calles de doble sentido y 61 de medianas siguen en ambos sentidos. Prueba de la regla (✓ = se usa): dgt carretera 12-25 m: 15/21; dgt ciudad 12-25 m: 1/3; dgt carretera 25-41 m: 5/7; dgt carretera 4-7 m: 33/45; dgt ciudad 4-7 m: 3/3; dgt carretera 7-12 m: 37/40 ✓; dgt ciudad 7-12 m: 1/2; dgt carretera todas: 90/113; dgt ciudad todas: 5/8; dgtpdf carretera 12-25 m: 8/18; dgtpdf ciudad 12-25 m: 8/10; dgtpdf carretera 25-41 m: 8/19; dgtpdf ciudad 25-41 m: 2/5; dgtpdf carretera 4-7 m: 7/10; dgtpdf ciudad 4-7 m: 1/3; dgtpdf carretera 7-12 m: 6/14; dgtpdf ciudad 7-12 m: 1/2; dgtpdf carretera todas: 29/61; dgtpdf ciudad todas: 12/20; osm carretera 12-25 m: 1/1; osm ciudad 12-25 m: 1/1; osm ciudad 25-41 m: 0/1; osm carretera 4-7 m: 85/111; osm ciudad 4-7 m: 73/114; osm carretera 7-12 m: 54/74; osm ciudad 7-12 m: 24/34; osm carretera todas: 140/186; osm ciudad todas: 98/150. Pistas combinadas: limite 2/3; cruce+lado 4/5; cruce 27/32; lado+limite 2/2
- **Copias de OSM de radares oficiales**: 1 quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: 0/1 → no se hereda
- **Radares viejos de OSM repetidos**: 0 quitados (de OSM sin sentido, con otro radar más fiable en la misma calle y sentido a menos de 300 m; 450 m si no tiene datos; 600 m si además es de 2015 o antes)
- **Radares seguidos (mismo sentido, < 300 m)**: 33 pares por revisar: dgt:GUID_CABINACINEMOMETRO_120602→dgt:GUID_CABINACINEMOMETRO_120603 14 m; osm:n8081941154→osm:n8432725875 99 m; madzbe:40.3986,-3.6695→madzbe:40.3977,-3.6701 105 m; osm:n5308701907→osm:n245940388 120 m; dgt:GUID_CABINACINEMOMETRO_120452→dgt:GUID_CABINACINEMOMETRO_120647 123 m; osm:r20130852→osm:n9920942778 128 m; madzbe:40.3926,-3.6774→madzbe:40.3932,-3.6767 132 m; osm:n13170535898b→osm:n13170535897 139 m; osm:n13170535897b→osm:n13170535898 139 m; osm:n8081941158→osm:n8158390898 143 m; osm:n8432725879→osm:n8081941158 144 m; osm:n9205627955→osm:n8119271102 144 m; madzbe:40.4142,-3.7208→madzbe:40.4156,-3.7208 156 m; madzbe:40.4127,-3.7211→madzbe:40.4142,-3.7208 163 m; madzbe:40.4266,-3.7133→madzbe:40.4280,-3.7141 181 m; osm:n8081941130→osm:n8119271103 186 m; madzbe:40.3631,-3.6845→madzbe:40.3614,-3.6838 188 m; madzbe:40.3614,-3.6838→madzbe:40.3631,-3.6845 189 m; osm:n4756348598→osm:n8432725880 193 m; madzbe:40.4130,-3.7137→madzbe:40.4118,-3.7137 198 m
- **Límites tomados de su vía**: 696 puestos, 5 quitados por no ser de su vía
- **Revisar**: nada sospechoso

## Por comunidad

| Comunidad | Fijos | Tramo | Semáforo | Stop/ceda | Otras cám. | Zonas móvil |
|---|---:|---:|---:|---:|---:|---:|
| Andalucía | 293 | 50 | 22 | 0 | 63 | 230 |
| Aragón | 97 | 6 | 0 | 0 | 17 | 102 |
| Canarias | 51 | 13 | 2 | 0 | 0 | 68 |
| Cantabria | 16 | 6 | 2 | 0 | 3 | 27 |
| Castilla y León | 215 | 58 | 34 | 0 | 31 | 265 |
| Castilla-La Mancha | 102 | 20 | 12 | 1 | 33 | 150 |
| Cataluña | 509 | 69 | 64 | 0 | 3 | 60 |
| Comunidad de Madrid | 154 | 28 | 66 | 1 | 304 | 59 |
| Comunidad Foral de Navarra | 37 | 2 | 1 | 0 | 2 | 35 |
| Comunitat Valenciana | 158 | 28 | 8 | 0 | 46 | 69 |
| Extremadura | 56 | 7 | 2 | 0 | 5 | 86 |
| Galicia | 127 | 33 | 7 | 0 | 31 | 128 |
| Illes Balears | 83 | 11 | 0 | 0 | 2 | 34 |
| La Rioja | 38 | 0 | 0 | 0 | 6 | 17 |
| Melilla | 6 | 0 | 0 | 0 | 0 | 0 |
| País Vasco | 211 | 2 | 9 | 0 | 0 | 0 |
| Principado de Asturias | 76 | 12 | 8 | 0 | 7 | 32 |
| Región de Murcia | 20 | 5 | 0 | 0 | 5 | 63 |
| Sin asignar | 0 | 0 | 1 | 0 | 0 | 0 |

Con sentido de circulación conocido (avisos solo en tu sentido): **2271**
Zonas de bajas emisiones: **57**

## Por fuente

- OSM: 1572
- DGT_TRAMOS_MOVIL: 1306
- DGT: 1117
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
OpenStreetMap: ERROR Overpass: overpass.kumi.systems: HTTP Error 502: Bad Gateway
Tramos radar móvil: 1152 puntos
Ayto. Madrid foto-rojo y ZBE: 454 puntos
Ayto. Málaga foto-rojo: 7 puntos
Ayto. Salamanca: 24 puntos
Ayto. Donostia: 12 puntos
Ayto. Santa Cruz de Tenerife foto-rojo: ERROR www.santacruzdetenerife.es: <urlopen error timed out>
Ayto. Pamplona cinemómetros: ERROR sig.pamplona.es: <urlopen error timed out>
Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados): 1654 puntos
feed comunitario tras quitar tramos ya situados: 483
fusión: 255 radares que estaban junto a otro del sentido contrario se mantienen (antes se perdían)
tramos: 5 puntos sueltos unidos a su tramo, 7 cámaras de entrada/salida absorbidas
correcciones: 0 quitados, 0 sentidos fijados
  límites: 879 sin límite, 0 por consultar
límites deducidos de OSM: 593
  regiones: 0 celdas nuevas que consultar
  CartoCiudad: 1998 hitos necesarios, 0 por consultar
rumbos por sentido: 1035
sentido hacia una ciudad: 70 puntos; ['VITORIA - GASTEIZ → 42.840,-2.722 (12 km)', 'IRUN → 43.327,-1.826 (33 km)', 'BILBAO → 43.254,-2.937 (28 km)', 'BILBAO → 43.254,-2.937 (30 km)', 'DONOSTIA / SAN SEBASTIÁN → 43.295,-1.988 (8 km)', 'IRUN → 43.327,-1.826 (21 km)', 'DONOSTIA / SAN SEBASTIÁN → 43.295,-1.988 (6 km)', 'VITORIA-GASTEIZ → 42.848,-2.679 (5 km)']
52 sentidos nuevos, 579 coinciden con los nuestros, 6 en desacuerdo (se avisa en los dos)
copias de OSM con sentido frente a oficiales: 0/0 → no se usa
0 radares de OSM con direction; frente a los oficiales: 0 igual, 0 al revés → no se usa
  ZBE: API CKAN no disponible (nap.dgt.es: HTTP Error 403: Forbidden); leo la página
  ZBE: 45 ficheros
ZBE: 57 zonas
  caminos: red cargada (937748 vías) en 60s
  caminos: regla del lado probada en 60s
  caminos: regla del cruce probada en 61s
  caminos: 0/3517 en 61s (dgt:GUID_CVM_161274)
  caminos: 500/3517 en 62s (dgt:GUID_CABINACINEMOMETRO_120574)
  caminos: 1000/3517 en 64s (sct:41.87303,1.71396)
  caminos: 1500/3517 en 69s (dgteq:A-391:5.1:D:cintur)
  caminos: 2000/3517 en 71s (osm:n10293906665)
  caminos: 2500/3517 en 74s (osm:n13718307112b)
  caminos: 3000/3517 en 77s (osm:n992002474)
  caminos: 3500/3517 en 80s (osm:n992006130)
1 quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: 0/1 → no se hereda
radares de OSM mapeados dos veces: 0 quitados []
gemelos de sentido contrario corregidos: 0 []
caminos: {'lado': 'dgt carretera 12-25 m: 15/21; dgt ciudad 12-25 m: 1/3; dgt carretera 25-41 m: 5/7; dgt carretera 4-7 m: 33/45; dgt ciudad 4-7 m: 3/3; dgt carretera 7-12 m: 37/40 ✓; dgt ciudad 7-12 m: 1/2; dgt carretera todas: 90/113; dgt ciudad todas: 5/8; dgtpdf carretera 12-25 m: 8/18; dgtpdf ciudad 12-25 m: 8/10; dgtpdf carretera 25-41 m: 8/19; dgtpdf ciudad 25-41 m: 2/5; dgtpdf carretera 4-7 m: 7/10; dgtpdf ciudad 4-7 m: 1/3; dgtpdf carretera 7-12 m: 6/14; dgtpdf ciudad 7-12 m: 1/2; dgtpdf carretera todas: 29/61; dgtpdf ciudad todas: 12/20; osm carretera 12-25 m: 1/1; osm ciudad 12-25 m: 1/1; osm ciudad 25-41 m: 0/1; osm carretera 4-7 m: 85/111; osm ciudad 4-7 m: 73/114; osm carretera 7-12 m: 54/74; osm ciudad 7-12 m: 24/34; osm carretera todas: 140/186; osm ciudad todas: 98/150', 'cruce': 'limite 2/3; cruce+lado 4/5; cruce 27/32; lado+limite 2/2', 'con_camino': 3431, 'sin_via': 82, 'tramos_con_recorrido': 262, 'tramos': 322, 'caminos_alternativos': 11, 'mediana_dos': 61, 'con_paralela': 1064, 'en_enlace': 31, 'sospechosos': [], 'dos_sentidos': 304, 'limites_via': 696, 'limites_quitados': 5, 'en_tunel': 58, 'calzada_corregida': 19, 'sin_calzada_de_su_sentido': 3, 'segundos': 80}
```
