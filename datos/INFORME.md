# Datos de Atalaya

Versión: 2026-11-04T11:50:22+00:00 · Total: **5195** puntos

## Fuentes

- **DGT feed**: ✅ 737 (1s)
- **DGT PDF radares**: ✅ 183 (7s)
- **DGT PDF cámaras**: ✅ 249 (1s)
- **Cataluña (SCT)**: ✅ 230 (15s)
- **Ayto. Madrid**: ✅ 23 (0s)
- **Ayto. València**: ✅ 11 (0s)
- **OpenStreetMap**: ✅ 3217 (79s)
- **Tramos radar móvil**: ✅ 1152 (0s)
- **Ayto. Madrid foto-rojo y ZBE**: ✅ 454 (1s)
- **Ayto. Málaga foto-rojo**: ✅ 7 (5s)
- **Ayto. Salamanca**: ✅ 24 (2s)
- **Ayto. Donostia**: ✅ 12 (1s)
- **Câmara Municipal de Lisboa**: ✅ 18 (0s)
- **Ajuntament de Viladecans**: ✅ 24 (2s)
- **Portugal: ANSR (red SINCRO)**: ✅ 121 (1s)
- **Ayto. Santa Cruz de Tenerife foto-rojo**: ℹ️ desde GitHub no responde; la app lo descarga en el móvil (fuentes_movil.json)
- **Ayto. Pamplona cinemómetros**: ℹ️ desde GitHub no responde; la app lo descarga en el móvil (fuentes_movil.json)
- **Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados)**: ✅ 1775 (1s)
- **Cámaras de stop y semáforo**: 100 cámaras de stop o semáforo llevadas a su línea de detención (140751 stops y semáforos de OSM)
- **Puntos comprobados**: ⚠️ 7 comprobados sobre el terreno; arreglados: osm:r9933664 (la2, lo2)
- **Sentido de los radares DGT (segunda opinión)**: 52 sentidos nuevos, 586 coinciden con los nuestros, 8 en desacuerdo (se avisa en los dos)
- **Sentido heredado de OSM**: copias de OSM con sentido frente a oficiales: 560/583 → se usa en 319 puntos y en 42 vigila los dos sentidos
- **Sentido de los radares de OSM**: 61 radares de OSM con direction; frente a los oficiales: 3 igual, 1 al revés → no se usa
- **Zonas de bajas emisiones**: ✅ 57
- **Situados por PK**: ✅ comprobado con 357 radares del feed (PK y coordenadas): en recta mediana 46 m, p75 93 m, p90 256 m; por la carretera mediana 34 m, p75 76 m, p90 247 m → 355 de 424 situados por PK recolocados por la carretera
- **Zonas de radar móvil por carretera**: 1139 de 1301 que venían en línea recta siguen ya la carretera (162 sin poder trazar)
- **Caminos de aproximación**: ✅ 3920 puntos con camino por su carretera, 318 de 356 tramos con recorrido real (29 sin vía cercana; 111s)
- **Sentido por el lado de la calle**: 291 puntos de calles de doble sentido y 29 de medianas siguen en ambos sentidos. Prueba de la regla (✓ = se usa): dgt carretera 12-25 m: 15/21; dgt ciudad 12-25 m: 2/4; dgt carretera 25-41 m: 5/7; dgt carretera 4-7 m: 35/47; dgt ciudad 4-7 m: 3/3; dgt carretera 7-12 m: 38/41 ✓; dgt ciudad 7-12 m: 1/2; dgt carretera todas: 93/116; dgt ciudad todas: 6/9; dgtpdf carretera 12-25 m: 1/2; dgtpdf ciudad 12-25 m: 3/5; dgtpdf carretera 25-41 m: 1/2; dgtpdf carretera 4-7 m: 1/1; dgtpdf carretera 7-12 m: 0/1; dgtpdf ciudad 7-12 m: 1/1; dgtpdf carretera todas: 3/6; dgtpdf ciudad todas: 4/6; osm carretera 12-25 m: 2/2; osm ciudad 12-25 m: 2/2; osm ciudad 25-41 m: 0/1; osm carretera 4-7 m: 96/122; osm ciudad 4-7 m: 72/110; osm carretera 7-12 m: 58/78; osm ciudad 7-12 m: 22/31; osm carretera todas: 156/202; osm ciudad todas: 96/144; otros carretera 4-7 m: 4/5; otros carretera 7-12 m: 4/5; otros ciudad 7-12 m: 0/1; otros carretera todas: 8/10; otros ciudad todas: 0/1; sct carretera 4-7 m: 10/15; sct ciudad 4-7 m: 1/1; sct carretera 7-12 m: 3/4; sct carretera todas: 13/19; sct ciudad todas: 1/1. Pistas combinadas: limite 23/32; cruce+lado 1/2; cruce 33/41; lado+limite 8/9
- **Copias de OSM de radares oficiales**: 67 quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: 42/43 → heredado en 18; 9 radares del PDF de la DGT llevados a la posición de su copia de OSM
- **Radares viejos de OSM repetidos**: 4 quitados (de OSM sin sentido, con otro radar más fiable en la misma calle y sentido a menos de 300 m; 450 m si no tiene datos; 600 m si además es de 2015 o antes): osm:n1123913886, osm:n5744469677, osm:n7171815050, osm:n14169137330
- **Radares seguidos (mismo sentido, < 300 m)**: 70 pares por revisar: osm:n8281297753→osm:n3269210194 87 m; osm:n8081941155→osm:n8432725880 90 m; osm:n8081941154→osm:n8432725875 99 m; madzbe:40.3986,-3.6695→madzbe:40.3977,-3.6701 105 m; osm:n5308701907→osm:n245940388 120 m; ansr:IC17:7.4:N→ansr:IC17:6.7:N 121 m; dgt:GUID_CABINACINEMOMETRO_120452→dgt:GUID_CABINACINEMOMETRO_120647 123 m; osm:r20130852→osm:n9920942778 128 m; madzbe:40.3926,-3.6774→madzbe:40.3932,-3.6767 132 m; osm:n8432725876→osm:n8081941154 135 m; osm:n13170535898b→osm:n13170535897 139 m; osm:n13170535897b→osm:n13170535898 139 m; osm:n3269210194→osm:n8281297753 139 m; madzbe:40.4291,-3.7048→madzbe:40.4291,-3.7037 140 m; osm:n4388458815→osm:n682302418 141 m; osm:n13378565235→osm:n11223504291 142 m; osm:n8081941158→osm:n8158390898 143 m; osm:n8432725879→osm:n8081941158 144 m; osm:n9205627955→osm:n8119271102 144 m; madzbe:40.3998,-3.6687→madzbe:40.3986,-3.6695 154 m
- **Límites tomados de su vía**: 148 puestos, 5 quitados por no ser de su vía
- **Revisar**: nada sospechoso
- **Cámaras de semáforo**: comprobación con las de sentido conocido: semáforo delante en 99, detrás en 8; 10 cámaras de semáforo con su sentido deducido por el semáforo que tienen delante; 41 llevadas a su línea (7 estaban pasado el cruce); 40 sin ningún semáforo de OSM a 50 m (posición por revisar)
- **Posición aproximada (solo PK)**: 411 puntos

## Por comunidad

| Comunidad | Fijos | Tramo | Semáforo | Stop/ceda | Otras cám. | Zonas móvil |
|---|---:|---:|---:|---:|---:|---:|
| Andalucía | 292 | 48 | 22 | 0 | 63 | 231 |
| Aragón | 97 | 6 | 0 | 0 | 17 | 109 |
| Canarias | 51 | 14 | 2 | 0 | 0 | 68 |
| Cantabria | 16 | 5 | 2 | 0 | 3 | 27 |
| Castilla y León | 214 | 57 | 34 | 0 | 31 | 304 |
| Castilla-La Mancha | 102 | 20 | 12 | 1 | 33 | 154 |
| Cataluña | 502 | 69 | 69 | 0 | 3 | 66 |
| Comunidad de Madrid | 154 | 28 | 66 | 1 | 304 | 59 |
| Comunidad Foral de Navarra | 37 | 2 | 1 | 0 | 2 | 37 |
| Comunitat Valenciana | 156 | 22 | 8 | 2 | 46 | 80 |
| Extremadura | 56 | 6 | 2 | 0 | 5 | 86 |
| Galicia | 127 | 31 | 7 | 0 | 31 | 128 |
| Illes Balears | 83 | 9 | 0 | 0 | 2 | 38 |
| La Rioja | 38 | 0 | 0 | 0 | 6 | 17 |
| Melilla | 6 | 0 | 0 | 0 | 0 | 0 |
| País Vasco | 211 | 2 | 9 | 0 | 0 | 13 |
| Portugal | 258 | 33 | 8 | 0 | 0 | 0 |
| Principado de Asturias | 77 | 12 | 8 | 0 | 7 | 32 |
| Región de Murcia | 20 | 5 | 0 | 0 | 5 | 67 |
| Sin asignar | 0 | 0 | 1 | 0 | 0 | 0 |

Con sentido de circulación conocido (avisos solo en tu sentido): **2718**
Zonas de bajas emisiones: **57**

## Por fuente

- OSM: 1724
- DGT_TRAMOS_MOVIL: 1306
- DGT: 1134
- AYUNTAMIENTO: 423
- SCT: 277
- AUTONOMICA: 208
- POLICIA_LOCAL: 90
- MULTAS: 33

## Registro

```
  tramo LZ-67 PK 16.22 (Decreciente): no se pudo situar su entrada (PK 21.724)
  cinemómetros: 641 ya estaban en el feed, 183 añadidos, 8 sin poder situar
DGT PDF radares: 183 puntos
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
Ayto. Santa Cruz de Tenerife foto-rojo: no responde (www.santacruzdetenerife.es: <urlopen error timed out>); desde GitHub no responde; la app lo descarga en el móvil (fuentes_movil.json)
Ayto. Pamplona cinemómetros: no responde (sig.pamplona.es: <urlopen error timed out>); desde GitHub no responde; la app lo descarga en el móvil (fuentes_movil.json)
Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados): 1775 puntos
feed comunitario tras quitar tramos ya situados: 604
fusión: 263 radares que estaban junto a otro del sentido contrario se mantienen (antes se perdían)
tramos: 2 tramos repetidos (oficial y OSM) unidos, 4 puntos sueltos unidos a su tramo, 13 cámaras de entrada/salida absorbidas
100 cámaras de stop o semáforo llevadas a su línea de detención (140751 stops y semáforos de OSM)
correcciones: 2 quitados, 37 sentidos fijados, 1 añadidos, 1 con el tipo corregido
verificados: 7 comprobados sobre el terreno; arreglados: osm:r9933664 (la2, lo2)
  límites: 211 sin límite, 0 por consultar
límites deducidos de OSM: 129
  regiones: 0 celdas nuevas que consultar
  CartoCiudad: 2016 hitos necesarios, 0 por consultar
rumbos por sentido: 1049
sentido hacia una ciudad: 74 puntos; ['VITORIA - GASTEIZ → 42.840,-2.722 (12 km)', 'IRUN → 43.327,-1.826 (33 km)', 'BILBAO → 43.254,-2.937 (28 km)', 'BILBAO → 43.254,-2.937 (30 km)', 'DONOSTIA / SAN SEBASTIÁN → 43.295,-1.988 (8 km)', 'IRUN → 43.327,-1.826 (21 km)', 'DONOSTIA / SAN SEBASTIÁN → 43.295,-1.988 (6 km)', 'VITORIA-GASTEIZ → 42.848,-2.679 (5 km)']
52 sentidos nuevos, 586 coinciden con los nuestros, 8 en desacuerdo (se avisa en los dos)
copias de OSM con sentido frente a oficiales: 560/583 → se usa en 319 puntos y en 42 vigila los dos sentidos
61 radares de OSM con direction; frente a los oficiales: 3 igual, 1 al revés → no se usa
  ZBE: API CKAN no disponible (nap.dgt.es: HTTP Error 403: Forbidden); leo la página
  ZBE: 45 ficheros
ZBE: 57 zonas
  CartoCiudad: 745 hitos necesarios, 0 por consultar
PK por la carretera: comprobado con 357 radares del feed (PK y coordenadas): en recta mediana 46 m, p75 93 m, p90 256 m; por la carretera mediana 34 m, p75 76 m, p90 247 m
  caminos: red cargada (1098179 vías) en 76s
  caminos: regla del lado probada en 77s
  caminos: regla del cruce probada en 78s
  caminos: 0/3960 en 78s (dgt:GUID_CVM_161274)
  caminos: 500/3960 en 80s (dgt:GUID_CABINACINEMOMETRO_120569)
  caminos: 1000/3960 en 82s (sct:41.32417,2.04486)
  caminos: 1500/3960 en 89s (dss:43.30828,-2.00974)
  caminos: 2000/3960 en 92s (com:euskadi-tunel-malmasin-can)
  caminos: 2500/3960 en 98s (osm:n2334938827)
  caminos: 3000/3960 en 103s (osm:n12599116369)
  caminos: 3500/3960 en 107s (osm:r14126600)
  zonas: red cargada (1153793 vías) para 1301 zonas en 89s
zonas: {'zonas_rectas': 1301, 'zonas_trazadas': 1139, 'zonas_sin_trazar': 162, 'segundos_zonas': 104}
radares del PDF de la DGT recolocados en su copia de OSM: 9
  caminos: red cargada (19732 vías) en 26s
  caminos: regla del lado probada en 26s
  caminos: regla del cruce probada en 26s
  caminos: 0/27 en 26s (sct:41.53823,0.45946)
67 quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: 42/43 → heredado en 18; 9 radares del PDF de la DGT llevados a la posición de su copia de OSM
radares de OSM mapeados dos veces: 0 quitados []
  caminos: red cargada (1705 vías) en 25s
  caminos: regla del lado probada en 25s
  caminos: regla del cruce probada en 25s
  caminos: 0/3 en 25s (dgt:GUID_CABINACINEMOMETRO_120285)
gemelos de sentido contrario corregidos: 3 ['dgt:GUID_CABINACINEMOMETRO_120285', 'dgt:GUID_CABINACINEMOMETRO_120288', 'dgt:GUID_CABINACINEMOMETRO_120603']
caminos: {'lado': 'dgt carretera 12-25 m: 15/21; dgt ciudad 12-25 m: 2/4; dgt carretera 25-41 m: 5/7; dgt carretera 4-7 m: 35/47; dgt ciudad 4-7 m: 3/3; dgt carretera 7-12 m: 38/41 ✓; dgt ciudad 7-12 m: 1/2; dgt carretera todas: 93/116; dgt ciudad todas: 6/9; dgtpdf carretera 12-25 m: 1/2; dgtpdf ciudad 12-25 m: 3/5; dgtpdf carretera 25-41 m: 1/2; dgtpdf carretera 4-7 m: 1/1; dgtpdf carretera 7-12 m: 0/1; dgtpdf ciudad 7-12 m: 1/1; dgtpdf carretera todas: 3/6; dgtpdf ciudad todas: 4/6; osm carretera 12-25 m: 2/2; osm ciudad 12-25 m: 2/2; osm ciudad 25-41 m: 0/1; osm carretera 4-7 m: 96/122; osm ciudad 4-7 m: 72/110; osm carretera 7-12 m: 58/78; osm ciudad 7-12 m: 22/31; osm carretera todas: 156/202; osm ciudad todas: 96/144; otros carretera 4-7 m: 4/5; otros carretera 7-12 m: 4/5; otros ciudad 7-12 m: 0/1; otros carretera todas: 8/10; otros ciudad todas: 0/1; sct carretera 4-7 m: 10/15; sct ciudad 4-7 m: 1/1; sct carretera 7-12 m: 3/4; sct carretera todas: 13/19; sct ciudad todas: 1/1', 'cruce': 'limite 23/32; cruce+lado 1/2; cruce 33/41; lado+limite 8/9', 'rumbo_por_cardinal': 46, 'con_camino': 3920, 'sin_via': 29, 'tramos_con_recorrido': 318, 'tramos': 356, 'caminos_alternativos': 13, 'mediana_dos': 29, 'con_paralela': 1228, 'en_enlace': 41, 'sospechosos': [], 'dos_sentidos': 291, 'limites_via': 148, 'limites_quitados': 5, 'en_tunel': 69, 'ramas': 3097, 'calzada_corregida': 6, 'caminos_cortos': 8, 'sin_calzada_de_su_sentido': 1, 'segundos': 111}
semáforos: con sentido conocido, su semáforo delante 99, detrás 8 → se deducen sentidos
  caminos: red cargada (66302 vías) en 27s
  caminos: regla del lado probada en 27s
  caminos: regla del cruce probada en 27s
  caminos: 0/41 en 27s (madfr:40.43521,-3.67502)
comprobación con las de sentido conocido: semáforo delante en 99, detrás en 8; 10 cámaras de semáforo con su sentido deducido por el semáforo que tienen delante; 41 llevadas a su línea (7 estaban pasado el cruce); 40 sin ningún semáforo de OSM a 50 m (posición por revisar): madfr:40.45464,-3.69056, madfr:40.46227,-3.79330, madfr:40.38409,-3.75977, madfr:40.39694,-3.77433, madfr:40.41074,-3.65479, madfr:40.42034,-3.62522, madfr:40.44164,-3.62408, mlgfr:36.71300,-4.45466, dgteq:N-603:62.9:C:foto r, osm:n992000541, osm:n992001267, osm:n992002942, osm:n992003252, osm:n992003267, osm:n2004518514, osm:n2004518665, osm:n2378266833, osm:n2378266933, osm:n2378267261, osm:n4029561801, osm:n4029562016, osm:n4087504678, osm:n4258221018, osm:n9757953611, osm:n12736058897, osm:n12736232082, osm:n12993247575, osm:n12993247583, osm:n12993898230, osm:n14169267684, osm:n3015095098, osm:n3015103519, osm:n1416249515, osm:n4349063327, osm:r19801864, osm:n7821371292, osm:r19964592, osm:r19964593, osm:n11692022938, osm:n5326355963
verificados: 7 comprobados sobre el terreno, todos en su sitio
```
