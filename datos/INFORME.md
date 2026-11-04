# Datos de Atalaya

Versión: 2026-11-04T11:14:58+00:00 · Total: **5200** puntos

## Fuentes

- **DGT feed**: ✅ 737 (1s)
- **DGT PDF radares**: ✅ 183 (8s)
- **DGT PDF cámaras**: ✅ 249 (1s)
- **Cataluña (SCT)**: ✅ 230 (14s)
- **Ayto. Madrid**: ✅ 23 (0s)
- **Ayto. València**: ✅ 11 (0s)
- **OpenStreetMap**: ✅ 3217 (73s)
- **Tramos radar móvil**: ✅ 1152 (0s)
- **Ayto. Madrid foto-rojo y ZBE**: ✅ 454 (2s)
- **Ayto. Málaga foto-rojo**: ✅ 7 (1s)
- **Ayto. Salamanca**: ✅ 24 (1s)
- **Ayto. Donostia**: ✅ 12 (0s)
- **Câmara Municipal de Lisboa**: ✅ 18 (0s)
- **Ajuntament de Viladecans**: ✅ 24 (1s)
- **Portugal: ANSR (red SINCRO)**: ✅ 121 (1s)
- **Ayto. Santa Cruz de Tenerife foto-rojo**: ℹ️ desde GitHub no responde; la app lo descarga en el móvil (fuentes_movil.json)
- **Ayto. Pamplona cinemómetros**: ℹ️ desde GitHub no responde; la app lo descarga en el móvil (fuentes_movil.json)
- **Euskadi, Navarra, Murcia, León, remolques SCT, multas (radares-anunciados)**: ✅ 1775 (0s)
- **Cámaras de stop y semáforo**: 100 cámaras de stop o semáforo llevadas a su línea de detención (140751 stops y semáforos de OSM)
- **Puntos comprobados**: ⚠️ 7 comprobados sobre el terreno; arreglados: osm:r9933664 (la2, lo2)
- **Sentido de los radares DGT (segunda opinión)**: 52 sentidos nuevos, 586 coinciden con los nuestros, 8 en desacuerdo (se avisa en los dos)
- **Sentido heredado de OSM**: copias de OSM con sentido frente a oficiales: 560/583 → se usa en 319 puntos y en 42 vigila los dos sentidos
- **Sentido de los radares de OSM**: 61 radares de OSM con direction; frente a los oficiales: 3 igual, 1 al revés → no se usa
- **Zonas de bajas emisiones**: ✅ 57
- **Zonas de radar móvil por carretera**: 1139 de 1301 que venían en línea recta siguen ya la carretera (162 sin poder trazar)
- **Caminos de aproximación**: ✅ 3866 puntos con camino por su carretera, 286 de 338 tramos con recorrido real (82 sin vía cercana; 115s)
- **Sentido por el lado de la calle**: 291 puntos de calles de doble sentido y 29 de medianas siguen en ambos sentidos. Prueba de la regla (✓ = se usa): dgt carretera 12-25 m: 15/21; dgt ciudad 12-25 m: 2/4; dgt carretera 25-41 m: 5/7; dgt carretera 4-7 m: 35/47; dgt ciudad 4-7 m: 3/3; dgt carretera 7-12 m: 38/41 ✓; dgt ciudad 7-12 m: 1/2; dgt carretera todas: 93/116; dgt ciudad todas: 6/9; dgtpdf carretera 12-25 m: 8/18; dgtpdf ciudad 12-25 m: 8/10; dgtpdf carretera 25-41 m: 8/19; dgtpdf ciudad 25-41 m: 2/5; dgtpdf carretera 4-7 m: 7/10; dgtpdf ciudad 4-7 m: 1/3; dgtpdf carretera 7-12 m: 6/14; dgtpdf ciudad 7-12 m: 1/2; dgtpdf carretera todas: 29/61; dgtpdf ciudad todas: 12/20; osm carretera 12-25 m: 2/2; osm ciudad 12-25 m: 2/2; osm ciudad 25-41 m: 0/1; osm carretera 4-7 m: 96/122; osm ciudad 4-7 m: 72/110; osm carretera 7-12 m: 58/78; osm ciudad 7-12 m: 22/31; osm carretera todas: 156/202; osm ciudad todas: 96/144; otros carretera 4-7 m: 4/5; otros carretera 7-12 m: 4/5; otros ciudad 7-12 m: 0/1; otros carretera todas: 8/10; otros ciudad todas: 0/1; sct carretera 4-7 m: 10/15; sct ciudad 4-7 m: 1/1; sct carretera 7-12 m: 3/4; sct carretera todas: 13/19; sct ciudad todas: 1/1. Pistas combinadas: limite 23/31; cruce+lado 1/2; cruce 33/41; lado+limite 10/12
- **Copias de OSM de radares oficiales**: 62 quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: 37/38 → heredado en 18; 7 radares del PDF de la DGT llevados a la posición de su copia de OSM
- **Radares viejos de OSM repetidos**: 4 quitados (de OSM sin sentido, con otro radar más fiable en la misma calle y sentido a menos de 300 m; 450 m si no tiene datos; 600 m si además es de 2015 o antes): osm:n1123913886, osm:n5744469677, osm:n7171815050, osm:n14169137330
- **Radares seguidos (mismo sentido, < 300 m)**: 70 pares por revisar: osm:n8281297753→osm:n3269210194 87 m; osm:n8081941155→osm:n8432725880 90 m; osm:n8081941154→osm:n8432725875 99 m; madzbe:40.3986,-3.6695→madzbe:40.3977,-3.6701 105 m; osm:n5308701907→osm:n245940388 120 m; ansr:IC17:7.4:N→ansr:IC17:6.7:N 121 m; dgt:GUID_CABINACINEMOMETRO_120452→dgt:GUID_CABINACINEMOMETRO_120647 123 m; osm:r20130852→osm:n9920942778 128 m; madzbe:40.3926,-3.6774→madzbe:40.3932,-3.6767 132 m; osm:n8432725876→osm:n8081941154 135 m; osm:n13170535898b→osm:n13170535897 139 m; osm:n13170535897b→osm:n13170535898 139 m; osm:n3269210194→osm:n8281297753 139 m; madzbe:40.4291,-3.7048→madzbe:40.4291,-3.7037 140 m; osm:n4388458815→osm:n682302418 141 m; osm:n13378565235→osm:n11223504291 142 m; osm:n8081941158→osm:n8158390898 143 m; osm:n8432725879→osm:n8081941158 144 m; osm:n9205627955→osm:n8119271102 144 m; madzbe:40.3998,-3.6687→madzbe:40.3986,-3.6695 154 m
- **Límites tomados de su vía**: 142 puestos, 4 quitados por no ser de su vía
- **Revisar**: nada sospechoso
- **Cámaras de semáforo**: comprobación con las de sentido conocido: semáforo delante en 99, detrás en 8; 8 cámaras de semáforo con su sentido deducido por el semáforo que tienen delante; 34 llevadas a su línea; 47 sin ningún semáforo de OSM delante (posición por revisar)

## Por comunidad

| Comunidad | Fijos | Tramo | Semáforo | Stop/ceda | Otras cám. | Zonas móvil |
|---|---:|---:|---:|---:|---:|---:|
| Andalucía | 293 | 48 | 22 | 0 | 63 | 231 |
| Aragón | 97 | 6 | 0 | 0 | 17 | 109 |
| Canarias | 51 | 14 | 2 | 0 | 0 | 68 |
| Cantabria | 16 | 5 | 2 | 0 | 3 | 27 |
| Castilla y León | 214 | 57 | 34 | 0 | 31 | 304 |
| Castilla-La Mancha | 103 | 20 | 12 | 1 | 33 | 154 |
| Cataluña | 502 | 69 | 69 | 0 | 3 | 66 |
| Comunidad de Madrid | 155 | 28 | 66 | 1 | 304 | 59 |
| Comunidad Foral de Navarra | 37 | 2 | 1 | 0 | 2 | 37 |
| Comunitat Valenciana | 157 | 22 | 8 | 2 | 46 | 80 |
| Extremadura | 56 | 6 | 2 | 0 | 5 | 86 |
| Galicia | 128 | 31 | 7 | 0 | 31 | 128 |
| Illes Balears | 83 | 9 | 0 | 0 | 2 | 38 |
| La Rioja | 38 | 0 | 0 | 0 | 6 | 17 |
| Melilla | 6 | 0 | 0 | 0 | 0 | 0 |
| País Vasco | 211 | 2 | 9 | 0 | 0 | 13 |
| Portugal | 258 | 33 | 8 | 0 | 0 | 0 |
| Principado de Asturias | 77 | 12 | 8 | 0 | 7 | 32 |
| Región de Murcia | 20 | 5 | 0 | 0 | 5 | 67 |
| Sin asignar | 0 | 0 | 1 | 0 | 0 | 0 |

Con sentido de circulación conocido (avisos solo en tu sentido): **2721**
Zonas de bajas emisiones: **57**

## Por fuente

- OSM: 1729
- DGT_TRAMOS_MOVIL: 1306
- DGT: 1134
- AYUNTAMIENTO: 423
- SCT: 277
- AUTONOMICA: 208
- POLICIA_LOCAL: 90
- MULTAS: 33

## Registro

```
  CartoCiudad: 672 hitos necesarios, 0 por consultar
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
  caminos: red cargada (1098703 vías) en 80s
  caminos: regla del lado probada en 81s
  caminos: regla del cruce probada en 81s
  caminos: 0/3960 en 81s (dgt:GUID_CVM_161274)
  caminos: 500/3960 en 83s (dgt:GUID_CABINACINEMOMETRO_120569)
  caminos: 1000/3960 en 85s (sct:41.32417,2.04486)
  caminos: 1500/3960 en 92s (dss:43.30828,-2.00974)
  caminos: 2000/3960 en 96s (com:euskadi-tunel-malmasin-can)
  caminos: 2500/3960 en 101s (osm:n2334938827)
  caminos: 3000/3960 en 107s (osm:n12599116369)
  caminos: 3500/3960 en 111s (osm:r14126600)
  zonas: red cargada (1153793 vías) para 1301 zonas en 92s
zonas: {'zonas_rectas': 1301, 'zonas_trazadas': 1139, 'zonas_sin_trazar': 162, 'segundos_zonas': 107}
radares del PDF de la DGT recolocados en su copia de OSM: 7
  caminos: red cargada (17971 vías) en 27s
  caminos: regla del lado probada en 27s
  caminos: regla del cruce probada en 27s
  caminos: 0/25 en 27s (sct:41.53823,0.45946)
62 quitadas (misma calle y sentido a menos de 450 m); sentido de la copia frente al oficial: 37/38 → heredado en 18; 7 radares del PDF de la DGT llevados a la posición de su copia de OSM
radares de OSM mapeados dos veces: 0 quitados []
  caminos: red cargada (1705 vías) en 26s
  caminos: regla del lado probada en 26s
  caminos: regla del cruce probada en 26s
  caminos: 0/3 en 26s (dgt:GUID_CABINACINEMOMETRO_120285)
gemelos de sentido contrario corregidos: 3 ['dgt:GUID_CABINACINEMOMETRO_120285', 'dgt:GUID_CABINACINEMOMETRO_120288', 'dgt:GUID_CABINACINEMOMETRO_120603']
caminos: {'lado': 'dgt carretera 12-25 m: 15/21; dgt ciudad 12-25 m: 2/4; dgt carretera 25-41 m: 5/7; dgt carretera 4-7 m: 35/47; dgt ciudad 4-7 m: 3/3; dgt carretera 7-12 m: 38/41 ✓; dgt ciudad 7-12 m: 1/2; dgt carretera todas: 93/116; dgt ciudad todas: 6/9; dgtpdf carretera 12-25 m: 8/18; dgtpdf ciudad 12-25 m: 8/10; dgtpdf carretera 25-41 m: 8/19; dgtpdf ciudad 25-41 m: 2/5; dgtpdf carretera 4-7 m: 7/10; dgtpdf ciudad 4-7 m: 1/3; dgtpdf carretera 7-12 m: 6/14; dgtpdf ciudad 7-12 m: 1/2; dgtpdf carretera todas: 29/61; dgtpdf ciudad todas: 12/20; osm carretera 12-25 m: 2/2; osm ciudad 12-25 m: 2/2; osm ciudad 25-41 m: 0/1; osm carretera 4-7 m: 96/122; osm ciudad 4-7 m: 72/110; osm carretera 7-12 m: 58/78; osm ciudad 7-12 m: 22/31; osm carretera todas: 156/202; osm ciudad todas: 96/144; otros carretera 4-7 m: 4/5; otros carretera 7-12 m: 4/5; otros ciudad 7-12 m: 0/1; otros carretera todas: 8/10; otros ciudad todas: 0/1; sct carretera 4-7 m: 10/15; sct ciudad 4-7 m: 1/1; sct carretera 7-12 m: 3/4; sct carretera todas: 13/19; sct ciudad todas: 1/1', 'cruce': 'limite 23/31; cruce+lado 1/2; cruce 33/41; lado+limite 10/12', 'rumbo_por_cardinal': 46, 'con_camino': 3866, 'sin_via': 82, 'tramos_con_recorrido': 286, 'tramos': 338, 'caminos_alternativos': 12, 'mediana_dos': 29, 'con_paralela': 1220, 'en_enlace': 42, 'sospechosos': [], 'dos_sentidos': 291, 'limites_via': 142, 'limites_quitados': 4, 'en_tunel': 69, 'ramas': 3096, 'calzada_corregida': 17, 'caminos_cortos': 9, 'sin_calzada_de_su_sentido': 3, 'segundos': 115}
semáforos: con sentido conocido, su semáforo delante 99, detrás 8 → se deducen sentidos
  caminos: red cargada (55918 vías) en 28s
  caminos: regla del lado probada en 28s
  caminos: regla del cruce probada en 28s
  caminos: 0/34 en 28s (madfr:40.43521,-3.67502)
comprobación con las de sentido conocido: semáforo delante en 99, detrás en 8; 8 cámaras de semáforo con su sentido deducido por el semáforo que tienen delante; 34 llevadas a su línea; 47 sin ningún semáforo de OSM delante (posición por revisar): madfr:40.45464,-3.69056, madfr:40.46227,-3.79330, madfr:40.38409,-3.75977, madfr:40.39694,-3.77433, madfr:40.41074,-3.65479, madfr:40.42034,-3.62522, madfr:40.44164,-3.62408, mlgfr:36.71300,-4.45466, vdc:1, dgteq:N-603:62.9:C:foto r, dgteq:N-6:63.2:C:foto r, osm:n992000541, osm:n992001267, osm:n992001584, osm:n992002942, osm:n992003252, osm:n992003267, osm:n2004518514, osm:n2004518665, osm:n2378266833, osm:n2378266933, osm:n2378267261, osm:n4029561801, osm:n4029562016, osm:n4087504678
verificados: 7 comprobados sobre el terreno, todos en su sitio
Sin cambios en los datos.
```
