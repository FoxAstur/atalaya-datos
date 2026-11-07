# Datos de Atalaya

Versión: 2026-11-07T17:54:40+00:00 · Total: **5272** puntos

## Fuentes

- **DGT feed**: ✅ 737 (1s)
- **DGT PDF radares**: ✅ 184 (7s)
- **DGT PDF cámaras**: ✅ 252 (1s)
- **Cataluña (SCT)**: ✅ 230 (14s)
- **Ayto. Madrid**: ✅ 23 (0s)
- **Ayto. València**: ✅ 11 (0s)
- **OpenStreetMap**: ✅ 3217 (57s)
- **Tramos radar móvil**: ✅ 1152 (0s)
- **Ayto. Madrid foto-rojo y ZBE**: ✅ 454 (1s)
- **Ayto. Málaga foto-rojo**: ✅ 7 (7s)
- **Ayto. Salamanca**: ✅ 24 (1s)
- **Ayto. Donostia**: ✅ 12 (1s)
- **Câmara Municipal de Lisboa**: ✅ 18 (0s)
- **Ajuntament de Viladecans**: ✅ 24 (1s)
- **Portugal: ANSR (red SINCRO)**: ✅ 121 (1s)
- **Ayto. Santa Cruz de Tenerife foto-rojo**: ℹ️ desde GitHub no responde; la app lo descarga en el móvil (fuentes_movil.json)
- **Ayto. Pamplona cinemómetros**: ℹ️ desde GitHub no responde; la app lo descarga en el móvil (fuentes_movil.json)
- **Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados)**: ✅ 1798 (0s)
- **Cámaras de stop y semáforo**: 100 cámaras de stop o semáforo llevadas a su línea de detención (140751 stops y semáforos de OSM)
- **Puntos comprobados**: ⚠️ 96 comprobados sobre el terreno; arreglados: osm:r9933664 (la2, lo2)
- **Sentido de los tramos de la DGT**: 15 de 69 tramos del feed de la DGT venían con la salida primero y se les ha dado la vuelta (comprobado con OSM/PDF: 19 a favor, 2 en contra)
- **Sentido de los radares DGT (segunda opinión)**: 52 sentidos nuevos, 586 coinciden con los nuestros, 8 en desacuerdo (se avisa en los dos)
- **Sentido heredado de OSM**: copias de OSM con sentido frente a oficiales: 562/585 → se usa en 317 puntos y en 42 vigila los dos sentidos
- **Sentido de los radares de OSM**: 61 radares de OSM con direction; frente a los oficiales: 3 igual, 1 al revés → no se usa
- **Zonas de bajas emisiones**: ✅ 57
- **Situados por PK**: ✅ comprobado con 357 radares del feed (PK y coordenadas): en recta mediana 46 m, p75 93 m, p90 256 m; por la carretera mediana 34 m, p75 76 m, p90 247 m → 280 de 348 situados por PK recolocados por la carretera
- **Zonas de radar móvil por carretera**: 1139 de 1301 que venían en línea recta siguen ya la carretera (162 sin poder trazar)
- **Caminos de aproximación**: ✅ 3890 puntos con camino por su carretera, 318 de 357 tramos con recorrido real (27 sin vía cercana; 99s)
- **Sentido por el lado de la calle**: 277 puntos de calles de doble sentido y 29 de medianas siguen en ambos sentidos. Prueba de la regla (✓ = se usa): dgt carretera 12-25 m: 15/21; dgt ciudad 12-25 m: 2/4; dgt carretera 25-41 m: 5/7; dgt carretera 4-7 m: 35/47; dgt ciudad 4-7 m: 3/3; dgt carretera 7-12 m: 38/41 ✓; dgt ciudad 7-12 m: 1/2; dgt carretera todas: 93/116; dgt ciudad todas: 6/9; dgtpdf carretera 12-25 m: 1/2; dgtpdf ciudad 12-25 m: 3/5; dgtpdf carretera 25-41 m: 1/2; dgtpdf carretera 4-7 m: 1/1; dgtpdf carretera 7-12 m: 0/1; dgtpdf ciudad 7-12 m: 1/1; dgtpdf carretera todas: 3/6; dgtpdf ciudad todas: 4/6; osm carretera 12-25 m: 2/2; osm ciudad 12-25 m: 2/2; osm ciudad 25-41 m: 0/1; osm carretera 4-7 m: 96/122; osm ciudad 4-7 m: 72/110; osm carretera 7-12 m: 58/78; osm ciudad 7-12 m: 22/31; osm carretera todas: 156/202; osm ciudad todas: 96/144; otros carretera 4-7 m: 4/5; otros carretera 7-12 m: 4/5; otros ciudad 7-12 m: 0/1; otros carretera todas: 8/10; otros ciudad todas: 0/1; sct carretera 4-7 m: 10/15; sct ciudad 4-7 m: 1/1; sct carretera 7-12 m: 3/4; sct carretera todas: 13/19; sct ciudad todas: 1/1. Pistas combinadas: limite 23/32; cruce+lado 1/2; cruce 33/42; lado+limite 8/9
- **Copias de OSM de radares oficiales**: 67 quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: 42/43 → heredado en 18; 9 radares del PDF de la DGT llevados a la posición de su copia de OSM
- **Radares viejos de OSM repetidos**: 4 quitados (de OSM sin sentido, con otro radar más fiable en la misma calle y sentido a menos de 300 m; 450 m si no tiene datos; 600 m si además es de 2015 o antes): osm:n1123913886, osm:n5744469677, osm:n7171815050, osm:n14169137330
- **Radares seguidos (mismo sentido, < 300 m)**: 70 pares por revisar: osm:n8281297753→osm:n3269210194 87 m; osm:n8081941155→osm:n8432725880 90 m; osm:n8081941154→osm:n8432725875 99 m; madzbe:40.3986,-3.6695→madzbe:40.3977,-3.6701 105 m; osm:n5308701907→osm:n245940388 120 m; ansr:IC17:7.4:N→ansr:IC17:6.7:N 121 m; dgt:GUID_CABINACINEMOMETRO_120452→dgt:GUID_CABINACINEMOMETRO_120647 123 m; osm:r20130852→osm:n9920942778 128 m; madzbe:40.3926,-3.6774→madzbe:40.3932,-3.6767 132 m; osm:n8432725876→osm:n8081941154 135 m; osm:n13170535898b→osm:n13170535897 139 m; osm:n13170535897b→osm:n13170535898 139 m; osm:n3269210194→osm:n8281297753 139 m; madzbe:40.4291,-3.7048→madzbe:40.4291,-3.7037 140 m; osm:n4388458815→osm:n682302418 141 m; osm:n13378565235→osm:n11223504291 142 m; osm:n8081941158→osm:n8158390898 143 m; osm:n8432725879→osm:n8081941158 144 m; osm:n9205627955→osm:n8119271102 144 m; madzbe:40.3998,-3.6687→madzbe:40.3986,-3.6695 154 m
- **Límites tomados de su vía**: 149 puestos, 5 quitados por no ser de su vía
- **Revisar**: nada sospechoso
- **Cámaras de semáforo**: comprobación con las de sentido conocido: semáforo delante en 99, detrás en 8; 10 cámaras de semáforo con su sentido deducido por el semáforo que tienen delante; 41 llevadas a su línea (7 estaban pasado el cruce); 40 sin ningún semáforo de OSM a 50 m (posición por revisar)
- **Posición aproximada (solo PK)**: 342 puntos
- **Ministerio: tramos de concentración de accidentes**: ✅ 109 (23s); trazados por la carretera 101 de 103

## Por comunidad

| Comunidad | Fijos | Tramo | Semáforo | Stop/ceda | Otras cám. | Zonas móvil | Accidentes |
|---|---:|---:|---:|---:|---:|---:|---:|
| Andalucía | 292 | 48 | 22 | 0 | 65 | 231 | 0 |
| Aragón | 97 | 6 | 0 | 0 | 17 | 109 | 0 |
| Canarias | 51 | 14 | 2 | 0 | 0 | 68 | 0 |
| Cantabria | 16 | 4 | 2 | 0 | 3 | 27 | 0 |
| Castilla y León | 214 | 57 | 34 | 0 | 32 | 285 | 0 |
| Castilla-La Mancha | 102 | 20 | 12 | 1 | 33 | 152 | 0 |
| Cataluña | 502 | 69 | 69 | 0 | 3 | 66 | 0 |
| Comunidad de Madrid | 154 | 28 | 66 | 1 | 304 | 59 | 0 |
| Comunidad Foral de Navarra | 37 | 2 | 1 | 0 | 2 | 37 | 0 |
| Comunitat Valenciana | 156 | 22 | 8 | 2 | 46 | 80 | 0 |
| Extremadura | 56 | 6 | 2 | 0 | 5 | 86 | 0 |
| Galicia | 127 | 30 | 7 | 0 | 31 | 128 | 0 |
| Illes Balears | 83 | 9 | 0 | 0 | 2 | 38 | 0 |
| La Rioja | 38 | 0 | 0 | 0 | 6 | 17 | 0 |
| Melilla | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| País Vasco | 211 | 2 | 9 | 0 | 0 | 0 | 0 |
| Portugal | 258 | 33 | 8 | 0 | 0 | 0 | 0 |
| Principado de Asturias | 77 | 13 | 8 | 0 | 7 | 32 | 0 |
| Región de Murcia | 20 | 5 | 0 | 0 | 5 | 67 | 0 |
| Sin asignar | 0 | 0 | 1 | 0 | 0 | 0 | 109 |

Con sentido de circulación conocido (avisos solo en tu sentido): **2721**
Zonas de bajas emisiones: **57**

## Por fuente

- OSM: 1720
- DGT_TRAMOS_MOVIL: 1306
- DGT: 1138
- AYUNTAMIENTO: 423
- SCT: 277
- AUTONOMICA: 208
- MINISTERIO: 109
- POLICIA_LOCAL: 58
- MULTAS: 33

## Registro

```
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
Ayto. Santa Cruz de Tenerife foto-rojo: no responde (www.santacruzdetenerife.es: <urlopen error timed out>); desde GitHub no responde; la app lo descarga en el móvil (fuentes_movil.json)
Ayto. Pamplona cinemómetros: no responde (sig.pamplona.es: <urlopen error timed out>); desde GitHub no responde; la app lo descarga en el móvil (fuentes_movil.json)
Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados): 1798 puntos
feed comunitario tras quitar tramos ya situados: 627
fusión: 264 radares que estaban junto a otro del sentido contrario se mantienen (antes se perdían)
tramos: 2 tramos repetidos (oficial y OSM) unidos, 4 puntos sueltos unidos a su tramo, 13 cámaras de entrada/salida absorbidas
100 cámaras de stop o semáforo llevadas a su línea de detención (140751 stops y semáforos de OSM)
correcciones: 2 quitados, 37 sentidos fijados, 1 añadidos, 1 con el tipo corregido
verificados: 96 comprobados sobre el terreno; arreglados: osm:r9933664 (la2, lo2)
  límites: 212 sin límite, 0 por consultar
límites deducidos de OSM: 130
  regiones: 0 celdas nuevas que consultar
  CartoCiudad: 1901 hitos necesarios, 0 por consultar
rumbos por sentido: 970
  CartoCiudad: 66 hitos necesarios, 0 por consultar
tramos del feed girados: ['dgt:GUID_CVM_161436', 'dgt:GUID_CVM_162916', 'dgt:GUID_CVM_163339', 'dgt:GUID_CVM_163340', 'dgt:GUID_CVM_164230', 'dgt:GUID_CVM_164237', 'dgt:GUID_CVM_164265', 'dgt:GUID_CVM_165289', 'dgt:GUID_CVM_166399', 'dgt:GUID_CVM_166402', 'dgt:GUID_CABINACINEMOMETRO_120380', 'dgt:GUID_CABINACINEMOMETRO_120569', 'dgt:GUID_CABINACINEMOMETRO_162917', 'dgt:GUID_CABINACINEMOMETRO_174089', 'dgt:GUID_CABINACINEMOMETRO_175021']
tramos: 2 tramos repetidos (oficial y OSM) unidos, 0 puntos sueltos unidos a su tramo, 0 cámaras de entrada/salida absorbidas
sentido hacia una ciudad: 74 puntos; ['VITORIA - GASTEIZ → 42.840,-2.722 (12 km)', 'IRUN → 43.327,-1.826 (33 km)', 'BILBAO → 43.254,-2.937 (28 km)', 'BILBAO → 43.254,-2.937 (30 km)', 'DONOSTIA / SAN SEBASTIÁN → 43.295,-1.988 (8 km)', 'IRUN → 43.327,-1.826 (21 km)', 'DONOSTIA / SAN SEBASTIÁN → 43.295,-1.988 (6 km)', 'VITORIA-GASTEIZ → 42.848,-2.679 (5 km)']
52 sentidos nuevos, 586 coinciden con los nuestros, 8 en desacuerdo (se avisa en los dos)
copias de OSM con sentido frente a oficiales: 562/585 → se usa en 317 puntos y en 42 vigila los dos sentidos
61 radares de OSM con direction; frente a los oficiales: 3 igual, 1 al revés → no se usa
  ZBE: API CKAN no disponible (nap.dgt.es: HTTP Error 403: Forbidden); leo la página
  ZBE: 45 ficheros
ZBE: 57 zonas
  CartoCiudad: 745 hitos necesarios, 0 por consultar
PK por la carretera: comprobado con 357 radares del feed (PK y coordenadas): en recta mediana 46 m, p75 93 m, p90 256 m; por la carretera mediana 34 m, p75 76 m, p90 247 m
  caminos: red cargada (1097677 vías) en 71s
  caminos: regla del lado probada en 71s
  caminos: regla del cruce probada en 72s
  caminos: 0/3928 en 72s (dgt:GUID_CVM_161274)
  caminos: 500/3928 en 74s (dgt:GUID_CABINACINEMOMETRO_120569)
  caminos: 1000/3928 en 75s (sct:41.31141,2.03136)
  caminos: 1500/3928 en 81s (dss:43.29166,-1.97345)
  caminos: 2000/3928 en 84s (com:euskadi-zorroza)
  caminos: 2500/3928 en 88s (osm:n2334938901)
  caminos: 3000/3928 en 92s (osm:n13043403920)
  caminos: 3500/3928 en 96s (osm:r16150125)
  zonas: red cargada (1153793 vías) para 1301 zonas en 81s
zonas: {'zonas_rectas': 1301, 'zonas_trazadas': 1139, 'zonas_sin_trazar': 162, 'segundos_zonas': 94}
radares del PDF de la DGT recolocados en su copia de OSM: 9
  caminos: red cargada (19732 vías) en 24s
  caminos: regla del lado probada en 24s
  caminos: regla del cruce probada en 24s
  caminos: 0/27 en 24s (sct:41.53823,0.45946)
67 quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: 42/43 → heredado en 18; 9 radares del PDF de la DGT llevados a la posición de su copia de OSM
radares de OSM mapeados dos veces: 0 quitados []
  caminos: red cargada (5749 vías) en 24s
  caminos: regla del lado probada en 24s
  caminos: regla del cruce probada en 24s
  caminos: 0/5 en 24s (dgt:GUID_CABINACINEMOMETRO_120285)
gemelos de sentido contrario corregidos: 5 ['dgt:GUID_CABINACINEMOMETRO_120285', 'dgt:GUID_CABINACINEMOMETRO_120288', 'dgteq:SE-30:23.2:C:cintur', 'dgteq:SE-30:23.2:D:cintur', 'dgt:GUID_CABINACINEMOMETRO_120603']
caminos: {'lado': 'dgt carretera 12-25 m: 15/21; dgt ciudad 12-25 m: 2/4; dgt carretera 25-41 m: 5/7; dgt carretera 4-7 m: 35/47; dgt ciudad 4-7 m: 3/3; dgt carretera 7-12 m: 38/41 ✓; dgt ciudad 7-12 m: 1/2; dgt carretera todas: 93/116; dgt ciudad todas: 6/9; dgtpdf carretera 12-25 m: 1/2; dgtpdf ciudad 12-25 m: 3/5; dgtpdf carretera 25-41 m: 1/2; dgtpdf carretera 4-7 m: 1/1; dgtpdf carretera 7-12 m: 0/1; dgtpdf ciudad 7-12 m: 1/1; dgtpdf carretera todas: 3/6; dgtpdf ciudad todas: 4/6; osm carretera 12-25 m: 2/2; osm ciudad 12-25 m: 2/2; osm ciudad 25-41 m: 0/1; osm carretera 4-7 m: 96/122; osm ciudad 4-7 m: 72/110; osm carretera 7-12 m: 58/78; osm ciudad 7-12 m: 22/31; osm carretera todas: 156/202; osm ciudad todas: 96/144; otros carretera 4-7 m: 4/5; otros carretera 7-12 m: 4/5; otros ciudad 7-12 m: 0/1; otros carretera todas: 8/10; otros ciudad todas: 0/1; sct carretera 4-7 m: 10/15; sct ciudad 4-7 m: 1/1; sct carretera 7-12 m: 3/4; sct carretera todas: 13/19; sct ciudad todas: 1/1', 'cruce': 'limite 23/32; cruce+lado 1/2; cruce 33/42; lado+limite 8/9', 'rumbo_por_cardinal': 46, 'con_camino': 3890, 'sin_via': 27, 'tramos_con_recorrido': 318, 'tramos': 357, 'caminos_alternativos': 11, 'mediana_dos': 29, 'con_paralela': 1210, 'en_enlace': 41, 'sospechosos': [], 'dos_sentidos': 277, 'limites_via': 149, 'limites_quitados': 5, 'en_tunel': 69, 'ramas': 3106, 'calzada_corregida': 8, 'caminos_cortos': 8, 'segundos': 99}
semáforos: con sentido conocido, su semáforo delante 99, detrás 8 → se deducen sentidos
  caminos: red cargada (66302 vías) en 26s
  caminos: regla del lado probada en 26s
  caminos: regla del cruce probada en 26s
  caminos: 0/41 en 26s (madfr:40.43521,-3.67502)
comprobación con las de sentido conocido: semáforo delante en 99, detrás en 8; 10 cámaras de semáforo con su sentido deducido por el semáforo que tienen delante; 41 llevadas a su línea (7 estaban pasado el cruce); 40 sin ningún semáforo de OSM a 50 m (posición por revisar): madfr:40.45464,-3.69056, madfr:40.46227,-3.79330, madfr:40.38409,-3.75977, madfr:40.39694,-3.77433, madfr:40.41074,-3.65479, madfr:40.42034,-3.62522, madfr:40.44164,-3.62408, mlgfr:36.71300,-4.45466, dgteq:N-603:62.9:C:foto r, osm:n992000541, osm:n992001267, osm:n992002942, osm:n992003252, osm:n992003267, osm:n2004518514, osm:n2004518665, osm:n2378266833, osm:n2378266933, osm:n2378267261, osm:n4029561801, osm:n4029562016, osm:n4087504678, osm:n4258221018, osm:n9757953611, osm:n12736058897, osm:n12736232082, osm:n12993247575, osm:n12993247583, osm:n12993898230, osm:n14169267684, osm:n3015095098, osm:n3015103519, osm:n1416249515, osm:n4349063327, osm:r19801864, osm:n7821371292, osm:r19964592, osm:r19964593, osm:n11692022938, osm:n5326355963
verificados: 96 comprobados sobre el terreno, todos en su sitio
  TCA: página del Ministerio no disponible (www.transportes.gob.es: HTTP Error 403: Forbidden); se usan los PDF conocidos
  TCA: TCA 130 filas (NOTA-TCA-2024-Para-Publicar-en-WEB%20%28105%29-Def.pdf)
  TCA: TCAM 21 filas (tca-con-implicacion-de-motoristas.pdf)
  CartoCiudad: 295 hitos necesarios, 0 por consultar
  TCA: 11 sin poder situar: ['B-24 9.6-10.7', 'B-40 1.4-2.1', 'GR-30 9.1-10.1', 'GR-30 10.1-10.6', 'N-240 19.0-19.5', 'N-332 216.3-217.3', 'N-340 1144.7-1145.2', 'N-340 1154.3-1154.8', 'N-340 1159.8-1160.3', 'N-349 2.7-3.2', 'N-351 5.9-6.5']
Ministerio: tramos de concentración de accidentes: 109 puntos
  zonas: red cargada (148895 vías) para 103 zonas en 30s
```
